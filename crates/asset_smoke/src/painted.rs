//! Painted shading checks (gate L4): what the texture Bevy loaded does, measured on
//! the loaded triangles, UVs and texels, against the manifest.
//!
//! `tools/paint.py` computes the colour at a point as
//! `material colour * tint(height) * (1 - crevice shadow) * (1 + edge light)`,
//! with growth changing hue but not lightness. Here every sampled texel's
//! luminance is divided by `luminance(material colour * tint(height))`, which
//! leaves a number that is 1 on an open face, above 1 on an exposed edge and
//! below 1 in a crevice. Which of those a texel is comes from the geometry
//! alone, never from the texture.

use bevy::{image::Image, prelude::*};
use serde::{Deserialize, Serialize};

/// From the asset's spec (`painted_shading`) and `conventions.toml`, written by `tools/export.py`.
#[derive(Deserialize)]
pub struct Painted {
    texture_px: u32,
    /// Linear RGB multipliers at the floor and the top of the bounds.
    base_tint: [f32; 3],
    top_tint: [f32; 3],
    edge_light: f32,
    edge_width_m: f32,
    crevice_shadow: f32,
    crevice_width_m: f32,
    /// Faces lying on the floor of the bounds and facing down are never seen, and are not measured.
    hidden_underside: bool,
    min_texels_per_m: f32,
    min_uv_coverage: f32,
    max_uv_overlap: f32,
    /// Lowest and highest 8-bit sRGB value a texel's brightest channel may have.
    texel_range: [u8; 2],
    /// Two faces at least this far apart in tilt form an edge or a crevice.
    feature_deg: f32,
    /// How far an open face's colour may be from material colour times tint, as a share.
    colour_tolerance: f32,
    /// The share of `edge_light` and `crevice_shadow` the measured zones must show on average.
    min_effect_share: f32,
}

/// One triangle as Bevy loaded it, in scene space.
pub struct Triangle {
    pub positions: [Vec3; 3],
    pub uvs: Option<[Vec2; 3]>,
    /// Linear base colour the manifest gives this triangle's material.
    pub colour: Option<[f32; 3]>,
}

#[derive(Serialize, Default)]
pub struct Measured {
    texture_px: [u32; 2],
    uv_coverage: f32,
    uv_overlap: f32,
    min_texels_per_m: f32,
    texel_range: [u8; 2],
    open_samples: usize,
    edge_samples: usize,
    crevice_samples: usize,
    /// Mean of texel luminance over (material colour times tint) luminance, per zone.
    open_ratio: f32,
    edge_ratio: f32,
    crevice_ratio: f32,
    /// Luminance of the lowest quarter of open samples over the highest quarter.
    gradient: f32,
    gradient_expected: f32,
}

const LUMA: Vec3 = Vec3::new(0.2126, 0.7152, 0.0722);
/// A zone with fewer samples than this is not measured.
const MIN_SAMPLES: usize = 50;
/// Aim for about this many samples over the whole texture.
const SAMPLE_GRID: u32 = 384;
/// Faces closer in tilt than this are one surface.
const SAME_SURFACE_DEG: f32 = 4.0;

struct Sample {
    height: f32,
    /// Texel luminance over the luminance the formula gives an open face here.
    ratio: f32,
    luminance: f32,
    expected: f32,
    zone: Zone,
}

#[derive(PartialEq)]
enum Zone {
    Open,
    Edge,
    Crevice,
    Other,
}

pub fn check(
    want: &Painted,
    triangles: &[Triangle],
    image: &Image,
    floor: f32,
    top: f32,
    tolerance: f32,
    fail: &mut impl FnMut(String),
) -> Measured {
    let mut measured = Measured {
        texture_px: [image.width(), image.height()],
        ..default()
    };
    if image.width() != want.texture_px || image.height() != want.texture_px {
        fail(format!(
            "painted.texture_size: {}x{} px != manifest {} px square",
            image.width(),
            image.height(),
            want.texture_px
        ));
        return measured;
    }
    let px = want.texture_px as f32;
    let size = want.texture_px as usize;

    let normal = |t: &Triangle| (t.positions[1] - t.positions[0]).cross(t.positions[2] - t.positions[0]);
    let hidden = |t: &Triangle| {
        want.hidden_underside
            && normal(t).normalize_or_zero().y < -0.999
            && t.positions.iter().all(|p| p.y <= floor + tolerance)
    };

    if triangles.iter().any(|t| t.uvs.is_none()) {
        fail("uv.present: a primitive has no TEXCOORD_0".into());
        return measured;
    }
    let outside = triangles
        .iter()
        .flat_map(|t| t.uvs.unwrap())
        .filter(|uv| uv.min_element() < -1e-4 || uv.max_element() > 1.0 + 1e-4)
        .count();
    if outside > 0 {
        fail(format!("uv.in_unit_square: {outside} corners lie outside 0..1"));
        return measured;
    }

    // Every texel centre inside a triangle's UVs, with its barycentric weights.
    let texels_in = |t: &Triangle, stride: u32, visit: &mut dyn FnMut(u32, u32, Vec3)| {
        let uv = t.uvs.unwrap().map(|uv| uv * px);
        let area = (uv[1] - uv[0]).perp_dot(uv[2] - uv[0]);
        if area.abs() < 1e-9 {
            return;
        }
        let lo = uv[0].min(uv[1]).min(uv[2]).floor().max(Vec2::ZERO);
        let hi = uv[0].max(uv[1]).max(uv[2]).ceil().min(Vec2::splat(px - 1.0));
        let first = |v: f32| (v as u32).div_ceil(stride) * stride;
        let mut y = first(lo.y);
        while y as f32 <= hi.y {
            let mut x = first(lo.x);
            while x as f32 <= hi.x {
                let p = Vec2::new(x as f32 + 0.5, y as f32 + 0.5);
                let w0 = (uv[1] - p).perp_dot(uv[2] - p) / area;
                let w1 = (uv[2] - p).perp_dot(uv[0] - p) / area;
                let weights = Vec3::new(w0, w1, 1.0 - w0 - w1);
                // Strictly inside, so a texel on an edge two triangles share is counted for neither.
                if weights.min_element() > 1e-4 {
                    visit(x, y, weights);
                }
                x += stride;
            }
            y += stride;
        }
    };

    // UV layout: coverage, overlap, texel density.
    let mut cover = vec![0u8; size * size];
    for t in triangles {
        texels_in(t, 1, &mut |x, y, _| {
            let cell = &mut cover[y as usize * size + x as usize];
            *cell = cell.saturating_add(1);
        });
    }
    let covered = cover.iter().filter(|&&c| c > 0).count();
    let overlapped = cover.iter().filter(|&&c| c > 1).count();
    measured.uv_coverage = covered as f32 / (size * size) as f32;
    measured.uv_overlap = overlapped as f32 / covered.max(1) as f32;
    if measured.uv_overlap > want.max_uv_overlap {
        fail(format!(
            "uv.no_overlap: {overlapped} of {covered} used texels ({:.4}) are claimed by more than one triangle; conventions allow {}",
            measured.uv_overlap, want.max_uv_overlap
        ));
    }
    if measured.uv_coverage < want.min_uv_coverage {
        fail(format!(
            "uv.coverage: triangles use {:.3} of the texture; conventions want at least {}",
            measured.uv_coverage, want.min_uv_coverage
        ));
    }
    let visible: Vec<&Triangle> = triangles.iter().filter(|t| !hidden(t)).collect();
    measured.min_texels_per_m = visible
        .iter()
        .map(|t| {
            let uv = t.uvs.unwrap();
            let texels = (uv[1] - uv[0]).perp_dot(uv[2] - uv[0]).abs() / 2.0 * px * px;
            (texels / (normal(t).length() / 2.0)).sqrt()
        })
        .fold(f32::MAX, f32::min);
    if measured.min_texels_per_m < want.min_texels_per_m {
        fail(format!(
            "uv.texel_density: the sparsest visible triangle has {:.0} texels per metre; conventions want at least {}",
            measured.min_texels_per_m, want.min_texels_per_m
        ));
    }

    // Sample the texture over the visible surface.
    let stride = (want.texture_px / SAMPLE_GRID).max(1);
    let feature_cos = want.feature_deg.to_radians().cos();
    let same_cos = SAME_SURFACE_DEG.to_radians().cos();
    let faces: Vec<(&Triangle, Vec3, Vec3)> = visible
        .iter()
        .map(|t| (*t, normal(t).normalize_or_zero(), (t.positions[0] + t.positions[1] + t.positions[2]) / 3.0))
        .collect();
    let (base_tint, top_tint) = (Vec3::from(want.base_tint), Vec3::from(want.top_tint));
    let mut samples = Vec::new();
    let (mut darkest, mut brightest) = (u8::MAX, u8::MIN);
    for (t, n, _) in &faces {
        let Some(colour) = t.colour else { continue };
        texels_in(t, stride, &mut |x, y, w| {
            // A format with no readable texels leaves no samples, and fails painted.open_faces.
            let Ok(texel) = image.get_color_at(x, y) else { return };
            let srgb = texel.to_srgba();
            let peak = (srgb.red.max(srgb.green).max(srgb.blue) * 255.0).round() as u8;
            darkest = darkest.min(peak);
            brightest = brightest.max(peak);
            let linear = texel.to_linear();
            let p = t.positions[0] * w.x + t.positions[1] * w.y + t.positions[2] * w.z;
            let height = ((p.y - floor) / (top - floor)).clamp(0.0, 1.0);
            let expected = (Vec3::from(colour) * base_tint.lerp(top_tint, height)).dot(LUMA);
            let luminance = Vec3::new(linear.red, linear.green, linear.blue).dot(LUMA);

            // Nearest face that turns away (an exposed edge) or rises in front (a crevice).
            let (mut convex, mut concave) = (f32::MAX, f32::MAX);
            let (mut any_convex, mut any_concave) = (f32::MAX, f32::MAX);
            for (other, m, centre) in &faces {
                let cos = n.dot(*m);
                if cos > same_cos {
                    continue;
                }
                let distance = distance_to_triangle(p, &other.positions);
                let rises = (*centre - p).dot(*n) > 0.0;
                let (near, any) = if rises { (&mut concave, &mut any_concave) } else { (&mut convex, &mut any_convex) };
                *any = any.min(distance);
                if cos <= feature_cos {
                    *near = near.min(distance);
                }
            }
            // The edge an asset stands on is not exposed, and is not painted as one.
            let on_ground = want.hidden_underside && p.y - floor < want.edge_width_m * 2.0;
            let zone = if on_ground {
                Zone::Other
            } else if concave <= want.crevice_width_m * 0.25 {
                Zone::Crevice
            } else if convex <= want.edge_width_m * 0.5 && any_concave > want.crevice_width_m {
                Zone::Edge
            } else if any_convex > want.edge_width_m * 2.0 && any_concave > want.crevice_width_m * 1.25 {
                Zone::Open
            } else {
                Zone::Other
            };
            samples.push(Sample { height, ratio: luminance / expected, luminance, expected, zone });
        });
    }
    measured.texel_range = [darkest, brightest];
    if !samples.is_empty() && (darkest < want.texel_range[0] || brightest > want.texel_range[1]) {
        fail(format!(
            "painted.range: texels' brightest channel spans {darkest}..{brightest} (8-bit sRGB); conventions want {}..{}",
            want.texel_range[0], want.texel_range[1]
        ));
    }

    let mean = |zone: Zone| {
        let ratios: Vec<f32> = samples.iter().filter(|s| s.zone == zone).map(|s| s.ratio).collect();
        (ratios.len(), ratios.iter().sum::<f32>() / ratios.len().max(1) as f32)
    };
    let (open_count, open) = mean(Zone::Open);
    let (edge_count, edge) = mean(Zone::Edge);
    let (crevice_count, crevice) = mean(Zone::Crevice);
    (measured.open_samples, measured.edge_samples, measured.crevice_samples) = (open_count, edge_count, crevice_count);
    (measured.open_ratio, measured.edge_ratio, measured.crevice_ratio) = (open, edge, crevice);
    if open_count < MIN_SAMPLES {
        fail(format!("painted.open_faces: only {open_count} samples lie on open faces; nothing to measure the colour on"));
        return measured;
    }

    if (open - 1.0).abs() > want.colour_tolerance {
        fail(format!(
            "painted.colour: open faces are {open:.3} times the material colour times the tint at their height; conventions allow 1 +/- {}",
            want.colour_tolerance
        ));
    }

    // Lowest and highest quarter of the open samples, by height.
    let mut by_height: Vec<&Sample> = samples.iter().filter(|s| s.zone == Zone::Open).collect();
    by_height.sort_by(|a, b| a.height.total_cmp(&b.height));
    let quarter = by_height.len() / 4;
    let total = |part: &[&Sample], value: fn(&Sample) -> f32| part.iter().map(|s| value(s)).sum::<f32>();
    let (low, high) = (&by_height[..quarter], &by_height[by_height.len() - quarter..]);
    measured.gradient = total(low, |s| s.luminance) / total(high, |s| s.luminance);
    measured.gradient_expected = total(low, |s| s.expected) / total(high, |s| s.expected);
    if (measured.gradient - measured.gradient_expected).abs() > want.colour_tolerance {
        fail(format!(
            "painted.gradient: the lowest quarter of the open faces is {:.3} times as light as the highest; the tints give {:.3} +/- {}",
            measured.gradient, measured.gradient_expected, want.colour_tolerance
        ));
    }

    let edge_floor = 1.0 + want.min_effect_share * want.edge_light;
    if edge_count >= MIN_SAMPLES && edge / open < edge_floor {
        fail(format!(
            "painted.edges_lighter: exposed edges are {:.3} times as light as open faces ({edge_count} samples); edge_light {} wants at least {edge_floor:.3}",
            edge / open,
            want.edge_light
        ));
    }
    let crevice_ceiling = 1.0 - want.min_effect_share * want.crevice_shadow;
    if crevice_count >= MIN_SAMPLES && crevice / open > crevice_ceiling {
        fail(format!(
            "painted.crevices_darker: inside corners are {:.3} times as light as open faces ({crevice_count} samples); crevice_shadow {} wants at most {crevice_ceiling:.3}",
            crevice / open,
            want.crevice_shadow
        ));
    }
    measured
}

/// Distance from a point to a triangle (Ericson, Real-Time Collision Detection, 5.1.5).
fn distance_to_triangle(p: Vec3, [a, b, c]: &[Vec3; 3]) -> f32 {
    let (ab, ac, ap) = (*b - *a, *c - *a, p - *a);
    let (d1, d2) = (ab.dot(ap), ac.dot(ap));
    if d1 <= 0.0 && d2 <= 0.0 {
        return ap.length();
    }
    let bp = p - *b;
    let (d3, d4) = (ab.dot(bp), ac.dot(bp));
    if d3 >= 0.0 && d4 <= d3 {
        return bp.length();
    }
    let vc = d1 * d4 - d3 * d2;
    if vc <= 0.0 && d1 >= 0.0 && d3 <= 0.0 {
        return (p - (*a + ab * (d1 / (d1 - d3)))).length();
    }
    let cp = p - *c;
    let (d5, d6) = (ab.dot(cp), ac.dot(cp));
    if d6 >= 0.0 && d5 <= d6 {
        return cp.length();
    }
    let vb = d5 * d2 - d1 * d6;
    if vb <= 0.0 && d2 >= 0.0 && d6 <= 0.0 {
        return (p - (*a + ac * (d2 / (d2 - d6)))).length();
    }
    let va = d3 * d6 - d5 * d4;
    if va <= 0.0 && (d4 - d3) >= 0.0 && (d5 - d6) >= 0.0 {
        return (p - (*b + (*c - *b) * ((d4 - d3) / ((d4 - d3) + (d5 - d6))))).length();
    }
    let denominator = 1.0 / (va + vb + vc);
    (p - (*a + ab * (vb * denominator) + ac * (vc * denominator))).length()
}
