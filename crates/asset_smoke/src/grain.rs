//! Grain and close-range texels (gate L4, ADR 12): what the bark Bevy loaded shows a player
//! who stands against it, measured on the loaded triangles, UVs and texels.
//!
//! `tools/paint.py` paints grain as tone that runs in streaks along a limb, and gives the
//! surface below `close_height_m` at least `close_texels_per_m`. Here both are measured on the
//! upright triangles below that height, where "along" is up the face: the tone step half a
//! grain width across the grain, and the same step along it. A hand-sized patch must show
//! both a step across and a step across well above the step along, and most patches must:
//! grain on average, with bare patches, is not bark at arm's length.

use std::collections::HashMap;

use bevy::{image::Image, prelude::*};
use serde::{Deserialize, Serialize};

use crate::painted::Triangle;

/// The parts of the manifest's `painted` block this module reads; `painted.rs` reads the rest.
#[derive(Deserialize)]
pub struct Wanted {
    texture_px: u32,
    hidden_underside: bool,
    #[serde(default)]
    grain: f32,
    #[serde(default)]
    grain_width_m: f32,
    #[serde(default)]
    close_height_m: Option<f32>,
    #[serde(default)]
    close_texels_per_m: f32,
    /// From `conventions.toml`: the side of a patch, the least step across the grain over
    /// `grain`, the least ratio of that step to the step along, and the share of patches.
    #[serde(default)]
    grain_patch_m: f32,
    #[serde(default)]
    min_grain_step: f32,
    #[serde(default)]
    min_grain_along: f32,
    #[serde(default)]
    min_grain_patches: f32,
    /// A limb that lies (a fallen log): the direction its grain runs, in glTF space. Absent, the
    /// grain runs up, as on a standing trunk. See `lying`.
    #[serde(default)]
    grain_along: Option<[f32; 3]>,
}

/// A triangle of a lying limb is measured when it runs along the limb: its normal within this of
/// square to `grain_along` (the cosine between them). An end, broken or sawn, faces along it.
const ALONG_LIMB: f32 = 0.5;

/// Where grain is measured, and which way "along" is there, on a limb that lies (`grain_along`):
/// on every triangle that runs along the limb, at any height and facing any way (a log is seen
/// from above, and the wall of a hollow from inside), along the limb's direction laid into the
/// triangle's plane. None: the triangle is an end, or a stub standing square to the limb.
fn lying(axis: Vec3, n: Vec3) -> Option<Vec3> {
    (n.dot(axis).abs() <= ALONG_LIMB).then(|| (axis - n * n.dot(axis)).normalize())
}

#[derive(Serialize, Default)]
pub struct Measured {
    /// Texels per metre of the sparsest visible triangle below `close_height_m`.
    close_texels_per_m: f32,
    /// Mean tone step half a grain width across the grain and along it, over the tone.
    step_across: f32,
    step_along: f32,
    patches: usize,
    /// Share of patches with enough step across, and with that step enough above the step along.
    patches_with_grain: f32,
    patches_with_streaks: f32,
}

const LUMA: Vec3 = Vec3::new(0.2126, 0.7152, 0.0722);
/// A patch with fewer samples than this is not judged.
const MIN_PATCH_SAMPLES: usize = 24;
/// Faces steeper than this (the upward part of the normal) are upright.
const UPRIGHT: f32 = 0.5;
/// Grain is measured from this far above the floor, clear of the roots' fins.
const ABOVE_ROOTS_M: f32 = 0.5;

pub fn check(want: &Wanted, triangles: &[Triangle], image: &Image, floor: f32, tolerance: f32, fail: &mut impl FnMut(String)) -> Option<Measured> {
    let ceiling = floor + want.close_height_m?;
    let mut measured = Measured::default();
    let px = want.texture_px as f32;
    let normal = |t: &Triangle| (t.positions[1] - t.positions[0]).cross(t.positions[2] - t.positions[0]);
    let close: Vec<&Triangle> = triangles
        .iter()
        .filter(|t| t.uvs.is_some() && t.positions.iter().all(|p| p.y <= ceiling + tolerance))
        .filter(|t| !(want.hidden_underside && normal(t).normalize_or_zero().y < -0.999 && t.positions.iter().all(|p| p.y <= floor + tolerance)))
        .collect();
    measured.close_texels_per_m = close
        .iter()
        .filter(|t| normal(t).length() > 1e-9)
        .map(|t| {
            let uv = t.uvs.unwrap();
            ((uv[1] - uv[0]).perp_dot(uv[2] - uv[0]).abs() / 2.0 * px * px / (normal(t).length() / 2.0)).sqrt()
        })
        .fold(f32::MAX, f32::min);
    if close.is_empty() || measured.close_texels_per_m < want.close_texels_per_m {
        fail(format!(
            "uv.close_density: the sparsest of the {} visible triangles below {} m has {:.0} texels per metre; the manifest wants at least {} where a player stands against the asset",
            close.len(),
            ceiling - floor,
            measured.close_texels_per_m,
            want.close_texels_per_m
        ));
    }
    if want.grain <= 0.0 && want.min_grain_step <= 0.0 {
        return Some(measured);
    }

    let tone = |uv: Vec2| {
        let x = (uv.x * px).floor().clamp(0.0, px - 1.0) as u32;
        let y = (uv.y * px).floor().clamp(0.0, px - 1.0) as u32;
        image.get_color_at(x, y).ok().map(|colour| {
            let linear = colour.to_linear();
            Vec3::new(linear.red, linear.green, linear.blue).dot(LUMA)
        })
    };
    let reach = want.grain_width_m / 2.0;
    // patch -> (samples, sum of steps across, sum of steps along)
    let mut patches: HashMap<(i32, i32, i32), (usize, f32, f32)> = HashMap::new();
    for t in &close {
        let n = normal(t).normalize_or_zero();
        let along = match want.grain_along {
            Some(axis) => match lying(Vec3::from(axis).normalize_or_zero(), n) {
                Some(along) => along,
                None => continue,
            },
            None => {
                if n.y.abs() > UPRIGHT || t.positions.iter().any(|p| p.y < floor + ABOVE_ROOTS_M) {
                    continue;
                }
                (Vec3::Y - n * n.y).normalize()
            }
        };
        let across = n.cross(along);
        let [a, b, c] = t.positions;
        let uv = t.uvs.unwrap();
        let (e1, e2) = (b - a, c - a);
        // Where a point of the triangle's plane lies, as shares of its two edges from `a`.
        let (d11, d12, d22) = (e1.dot(e1), e1.dot(e2), e2.dot(e2));
        let det = d11 * d22 - d12 * d12;
        let shares = |p: Vec3| {
            let (x, y) = ((p - a).dot(e1), (p - a).dot(e2));
            Vec2::new((d22 * x - d12 * y) / det, (d11 * y - d12 * x) / det)
        };
        let inside = |s: Vec2| s.x >= 0.0 && s.y >= 0.0 && s.x + s.y <= 1.0;
        let at = |s: Vec2| uv[0] + (uv[1] - uv[0]) * s.x + (uv[2] - uv[0]) * s.y;
        let steps = ((e1.length().max(e2.length()) / reach).ceil() as usize).clamp(1, 400);
        for i in 0..=steps {
            for j in 0..=(steps - i) {
                let here = Vec2::new(i as f32 / steps as f32, j as f32 / steps as f32);
                let p = a + e1 * here.x + e2 * here.y;
                let (over, up) = (shares(p + across * reach), shares(p + along * reach));
                if !inside(over) || !inside(up) {
                    continue;
                }
                let (Some(t0), Some(t1), Some(t2)) = (tone(at(here)), tone(at(over)), tone(at(up))) else { continue };
                let patch = (p / want.grain_patch_m.max(1e-3)).floor();
                let entry = patches.entry((patch.x as i32, patch.y as i32, patch.z as i32)).or_default();
                *entry = (entry.0 + 1, entry.1 + (t1 - t0).abs() / ((t1 + t0) / 2.0).max(1e-6), entry.2 + (t2 - t0).abs() / ((t2 + t0) / 2.0).max(1e-6));
            }
        }
    }
    let judged: Vec<(f32, f32)> = patches.values().filter(|(n, _, _)| *n >= MIN_PATCH_SAMPLES).map(|(n, across, along)| (across / *n as f32, along / *n as f32)).collect();
    measured.patches = judged.len();
    let count = judged.len().max(1) as f32;
    measured.step_across = judged.iter().map(|(across, _)| across).sum::<f32>() / count;
    measured.step_along = judged.iter().map(|(_, along)| along).sum::<f32>() / count;
    let least = want.min_grain_step * want.grain;
    measured.patches_with_grain = judged.iter().filter(|(across, _)| *across >= least).count() as f32 / count;
    measured.patches_with_streaks = judged.iter().filter(|(across, along)| *across >= want.min_grain_along * along).count() as f32 / count;
    if judged.is_empty() || measured.patches_with_grain < want.min_grain_patches {
        fail(format!(
            "painted.grain: {:.2} of the {} patches of upright surface ({} m across, below {} m) show a tone step of at least {least:.3} half a grain width across the grain (mean step {:.3}); grain {} wants {} of them to",
            measured.patches_with_grain,
            judged.len(),
            want.grain_patch_m,
            ceiling - floor,
            measured.step_across,
            want.grain,
            want.min_grain_patches
        ));
    }
    if judged.is_empty() || measured.patches_with_streaks < want.min_grain_patches {
        fail(format!(
            "painted.grain_along: in {:.2} of the {} patches the tone step across the grain is at least {} times the step along it (means {:.3} across, {:.3} along); conventions want that of {} of them: streaks along the limb, not speckle or hoops",
            measured.patches_with_streaks,
            judged.len(),
            want.min_grain_along,
            measured.step_across,
            measured.step_along,
            want.min_grain_patches
        ));
    }
    Some(measured)
}
