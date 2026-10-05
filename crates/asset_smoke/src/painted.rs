//! Painted shading checks (gate L4): what the texture Bevy loaded does, measured on
//! the loaded triangles, UVs and texels, against the manifest.
//!
//! `tools/paint.py` computes the colour at a point as
//! `material colour * tint(height) * (1 - side shade) * (1 + blotch) * (1 - crevice shadow) * (1 + edge light)`,
//! with growth changing hue. Here every sampled texel's luminance is divided
//! by `luminance(material colour * tint(height)) * (1 - side shade)`, which
//! the geometry alone gives. That leaves a number that is 1 on an open face
//! (give or take its blotches, which average out), above 1 on an exposed edge
//! and below 1 in a crevice. Which of those a texel is comes from the
//! geometry alone, never from the texture. The foot, the strip where a side
//! meets the ground, is near 1 too: the paint gives the edge an asset stands
//! on no light. It is measured only for the gradient from base to top.
//!
//! Growth is measured by hue: a texel divided by the tint, at the material's
//! lightness, lies somewhere on the line from the material colour to the
//! growth colour, and how far along is how much growth it shows.
//!
//! Where the spec gives `growth_darker`, patches of growth above the reach of
//! the growth at the base are that much darker than the surface round them.
//! The darkening is a multiply, so it does not move the hue, and the growth a
//! texel shows is still read from its hue. Above that reach, the luminance a
//! texel is held to is then lowered by `growth_darker` times the growth it
//! shows. So the colour, gradient, blotch, edge and side-shade checks still
//! compare each texel with what the formula gives for it, moss and all, and
//! `painted.growth_darker` alone asks whether the moss is as dark as specified.

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
    /// Absent when the spec asks no crevice shadow: the shape has no inside corner, and the load test holds it to that.
    #[serde(default)]
    crevice_shadow: Option<f32>,
    #[serde(default)]
    crevice_width_m: Option<f32>,
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
    /// Variation the spec asks for; absent or zero means none, and nothing is asked of it.
    #[serde(default)]
    growth: Option<[f32; 3]>,
    #[serde(default)]
    growth_height_m: f32,
    #[serde(default)]
    growth_up: f32,
    #[serde(default)]
    growth_edges: f32,
    /// How much darker than the surface round them the patches of growth are; absent or zero, growth only changes hue.
    #[serde(default)]
    growth_darker: f32,
    /// How large a patch of growth is, metres; absent or zero, nothing is asked of their size.
    #[serde(default)]
    growth_patch_m: f32,
    #[serde(default)]
    blotch: f32,
    #[serde(default)]
    side_shade: f32,
    /// The rules `tools/paint.py` paints by and these checks measure by, from `conventions.toml`.
    #[serde(default = "side_normal")]
    side_shade_normal_z: [f32; 2],
    #[serde(default = "half_band")]
    side_shade_half_band: f32,
    #[serde(default = "up_normal")]
    growth_up_normal_z: [f32; 2],
    #[serde(default = "cover")]
    growth_cover: [f32; 2],
    #[serde(default = "patch_edges")]
    growth_patch_edges: f32,
    #[serde(default = "spread")]
    blotch_spread: [f32; 2],
    #[serde(default = "grain")]
    max_blotch_grain: f32,
    #[serde(default = "level_gap")]
    max_level_gap: u8,
}

// Used only by manifests written before these rules existed (the tests' tampered ones).
fn side_normal() -> [f32; 2] { [0.3, 0.7] }
fn half_band() -> f32 { 0.35 }
fn up_normal() -> [f32; 2] { [0.82, 0.94] }
fn cover() -> [f32; 2] { [0.5, 1.5] }
fn patch_edges() -> f32 { 0.9 }
fn spread() -> [f32; 2] { [1.0, 2.5] }
fn grain() -> f32 { 0.2 }
fn level_gap() -> u8 { 3 }

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
    /// Samples left out because they lie inside another piece (overlapping pieces only).
    buried_samples: usize,
    open_samples: usize,
    edge_samples: usize,
    crevice_samples: usize,
    /// Samples on the strip where a side meets the ground: measured with the open faces for the gradient alone.
    foot_samples: usize,
    /// Mean of texel luminance over (material colour times tint) luminance, per zone.
    open_ratio: f32,
    edge_ratio: f32,
    crevice_ratio: f32,
    /// Luminance of the lowest quarter of the open and foot samples, by height, over the highest quarter.
    gradient: f32,
    gradient_expected: f32,
    /// Largest run of 8-bit levels of the green channel that no open face uses and that two
    /// neighbouring samples of one open face lie either side of: a step in the texture.
    level_gap: u8,
    /// Share of growth, 0 to 1, by hue: low on the asset, on upright open faces high up, on level
    /// open faces high up, and along upper edges.
    growth_base: f32,
    growth_bare_sides: f32,
    growth_up: f32,
    growth_edges: f32,
    /// How much darker open faces are where they show growth than where they show none, above the reach of the growth at the base.
    growth_darker: f32,
    /// Level open faces above that reach: how often growth starts or stops along the surface, per `growth_patch_m` metres.
    growth_patch_edges: f32,
    /// Open faces: the 10th to 90th percentile spread of tone, and the mean step between neighbouring samples over it.
    blotch_spread: f32,
    blotch_grain: f32,
    /// How much darker upright open faces near mid height are than the tint alone makes them, and the shade asked of them.
    side_shade: f32,
    side_shade_expected: f32,
}

const LUMA: Vec3 = Vec3::new(0.2126, 0.7152, 0.0722);
/// A zone with fewer samples than this is not measured.
const MIN_SAMPLES: usize = 50;
/// Aim for about this many samples over the whole texture.
const SAMPLE_GRID: u32 = 384;
/// Faces closer in tilt than this are one surface.
const SAME_SURFACE_DEG: f32 = 4.0;
/// The foot is the surface within this many edge widths of the ground. The paint fades the edge light in over two
/// edge widths from the ground (tools/paint.py), so the foot has at most an eighth of it.
const FOOT_EDGE_WIDTHS: f32 = 0.25;
/// Two samples next to each other in the texture are neighbours on the surface when no further apart than this many sample steps.
const NEIGHBOUR_STEPS: f32 = 3.0;
/// A point of a surface is buried when the space this far in front of it is inside another piece (as `[overlap] in_front_m` in conventions.toml).
const BURIED_IN_FRONT_M: f32 = 0.0001;

struct Sample {
    /// Texel position, to find neighbours, and the point of the surface it paints.
    at: (u32, u32),
    point: Vec3,
    /// Metres above the floor, and the upward part of the face's normal.
    above: f32,
    up: f32,
    /// How much of the side shade the paint gives this point, 0 to 1.
    shade: f32,
    /// Growth shown, 0 to 1, by hue.
    growth: f32,
    /// Beside an exposed edge, as the edge zone is, whether or not a join is near: where growth along edges is looked for on a shape with no edge clear of its joins.
    rim: bool,
    green: u8,
    height: f32,
    /// Texel luminance over the luminance the formula gives an open face here.
    ratio: f32,
    /// The same, before any darkening by growth is allowed for.
    bare_ratio: f32,
    /// Metres along the surface between this sample and the next one in the texture.
    step_m: f32,
    luminance: f32,
    expected: f32,
    zone: Zone,
}

#[derive(PartialEq)]
enum Zone {
    Open,
    Edge,
    Crevice,
    /// The strip where a side meets the ground it stands on: no edge light to speak of, and no shadow.
    Foot,
    Other,
}

pub fn check(
    want: &Painted,
    triangles: &[Triangle],
    overlap: bool,
    foliage: bool,
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
    // With no crevice shadow asked, an inside corner is looked for as near as an exposed edge is.
    let crevice_width_m = want.crevice_width_m.unwrap_or(want.edge_width_m);
    // Overlapping pieces (ADR 13): which piece each face is of. Surface inside another piece is
    // never seen, and what the paint did there is not measured.
    let corners: Vec<[Vec3; 3]> = faces.iter().map(|(t, _, _)| t.positions).collect();
    let (piece_of, piece_count) = if overlap { crate::pieces::split(&corners) } else { (vec![0; corners.len()], 1) };
    let mut samples = Vec::new();
    let (mut darkest, mut brightest) = (u8::MAX, u8::MIN);
    // Above this, growth is patches only: clear of the ragged top of the growth at the base, which wanders by half its height either way.
    let above_base = want.growth_height_m * 1.6;
    for (index, (t, n, _)) in faces.iter().enumerate() {
        let Some(colour) = t.colour else { continue };
        let uv = t.uvs.unwrap();
        let texels = (uv[1] - uv[0]).perp_dot(uv[2] - uv[0]).abs() / 2.0 * px * px;
        let step_m = stride as f32 / (texels / (normal(t).length() / 2.0)).sqrt().max(1e-6);
        texels_in(t, stride, &mut |x, y, w| {
            // A format with no readable texels leaves no samples, and fails painted.open_faces.
            let Ok(texel) = image.get_color_at(x, y) else { return };
            let srgb = texel.to_srgba();
            let peak = (srgb.red.max(srgb.green).max(srgb.blue) * 255.0).round() as u8;
            darkest = darkest.min(peak);
            brightest = brightest.max(peak);
            let linear = texel.to_linear();
            let p = t.positions[0] * w.x + t.positions[1] * w.y + t.positions[2] * w.z;
            if piece_count > 1 && crate::pieces::buried(p + *n * BURIED_IN_FRONT_M, piece_of[index], &corners, &piece_of, piece_count) {
                measured.buried_samples += 1;
                return;
            }
            let height = ((p.y - floor) / (top - floor)).clamp(0.0, 1.0);
            let tint = base_tint.lerp(top_tint, height);
            // Upright faces are painted darker near mid height (tools/paint.py, side_shade).
            let [side, not_side] = want.side_shade_normal_z;
            let upright = ((not_side - n.y.abs()) / (not_side - side)).clamp(0.0, 1.0);
            let shade = upright * (1.0 - (height - 0.5).abs() / want.side_shade_half_band).clamp(0.0, 1.0);
            let undarkened = (Vec3::from(colour) * tint).dot(LUMA) * (1.0 - want.side_shade * shade);
            let rgb = Vec3::new(linear.red, linear.green, linear.blue);
            let luminance = rgb.dot(LUMA);
            // Growth: the tint taken out and the lightness set to the material's, the texel lies on
            // the line from the material colour to the growth colour.
            let growth = want.growth.map_or(0.0, |growth| {
                let material = Vec3::from(colour);
                let growth = Vec3::from(growth) * (material.dot(LUMA) / Vec3::from(growth).dot(LUMA));
                let untinted = rgb / tint;
                let seen = untinted * (material.dot(LUMA) / untinted.dot(LUMA).max(1e-6));
                ((seen - material).dot(growth - material) / (growth - material).length_squared()).clamp(0.0, 1.0)
            });

            // Patches of growth are darker than the surface they grow on (tools/paint.py, growth_darker).
            let darkened = if want.growth.is_some() && p.y - floor > above_base { want.growth_darker * growth } else { 0.0 };
            let expected = undarkened * (1.0 - darkened);

            // Nearest face that turns away (an exposed edge) or rises in front (a crevice).
            let (mut convex, mut concave) = (f32::MAX, f32::MAX);
            let (mut any_convex, mut any_concave) = (f32::MAX, f32::MAX);
            for (other_index, (other, m, centre)) in faces.iter().enumerate() {
                let cos = n.dot(*m);
                if cos > same_cos {
                    continue;
                }
                let distance = distance_to_triangle(p, &other.positions);
                // A face of another piece near a point that is not buried is that piece coming out
                // of this one or standing against it: a join, whichever side its middle lies. Only
                // a point's own piece can turn away from it and make an exposed edge there.
                let rises = (*centre - p).dot(*n) > 0.0 || piece_of[other_index] != piece_of[index];
                let (near, any) = if rises { (&mut concave, &mut any_concave) } else { (&mut convex, &mut any_convex) };
                *any = any.min(distance);
                if cos <= feature_cos {
                    *near = near.min(distance);
                }
            }
            // The edge an asset stands on is not exposed, and is not painted as one.
            let on_ground = want.hidden_underside && p.y - floor < want.edge_width_m * 2.0;
            let zone = if on_ground {
                if p.y - floor < want.edge_width_m * FOOT_EDGE_WIDTHS && any_concave > crevice_width_m * 1.25 { Zone::Foot } else { Zone::Other }
            } else if concave <= crevice_width_m * 0.25 {
                Zone::Crevice
            } else if convex <= want.edge_width_m * 0.5 && any_concave > crevice_width_m {
                Zone::Edge
            } else if any_convex > want.edge_width_m * 2.0 && any_concave > crevice_width_m * 1.25 {
                Zone::Open
            } else {
                Zone::Other
            };
            samples.push(Sample {
                at: (x, y),
                point: p,
                above: p.y - floor,
                up: n.y,
                shade,
                growth,
                rim: convex <= want.edge_width_m * 0.5,
                green: (srgb.green * 255.0).round() as u8,
                height,
                ratio: luminance / expected,
                bare_ratio: luminance / undarkened,
                step_m,
                luminance,
                expected,
                zone,
            });
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
    measured.foot_samples = samples.iter().filter(|s| s.zone == Zone::Foot).count();
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

    // Lowest and highest quarter, by height, of the surface whose tone the formula gives: the open
    // faces and the foot. On a low stone the open faces are its cap, a few blotches across and
    // almost one height: its low and high quarters differ by their blotches, by more than the
    // tolerance either way, and by nothing the tints do (twelve seeds of pebble_1 read 0.21 over
    // to 0.11 under what the tints give, and the same stone painted with no gradient 0.20 over).
    // The gradient of such a stone is between its foot and its cap, so the foot is measured too.
    let mut by_height: Vec<&Sample> = samples.iter().filter(|s| s.zone == Zone::Open || s.zone == Zone::Foot).collect();
    by_height.sort_by(|a, b| a.height.total_cmp(&b.height));
    let quarter = by_height.len() / 4;
    let total = |part: &[&Sample], value: fn(&Sample) -> f32| part.iter().map(|s| value(s)).sum::<f32>();
    let (low, high) = (&by_height[..quarter], &by_height[by_height.len() - quarter..]);
    measured.gradient = total(low, |s| s.luminance) / total(high, |s| s.luminance);
    measured.gradient_expected = total(low, |s| s.expected) / total(high, |s| s.expected);
    if (measured.gradient - measured.gradient_expected).abs() > want.colour_tolerance {
        fail(format!(
            "painted.gradient: the lowest quarter of the open faces and the foot is {:.3} times as light as the highest; the tints give {:.3} +/- {}",
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
    // The crevice shadow is asked of a shape that has inside corners, and of no other: asked of a
    // convex stone it would pass unmeasured, and left out of a spec it must not leave a corner unshaded.
    match want.crevice_shadow {
        Some(shadow) if crevice_count >= MIN_SAMPLES => {
            let crevice_ceiling = 1.0 - want.min_effect_share * shadow;
            if crevice / open > crevice_ceiling {
                fail(format!(
                    "painted.crevices_darker: inside corners are {:.3} times as light as open faces ({crevice_count} samples); crevice_shadow {shadow} wants at most {crevice_ceiling:.3}",
                    crevice / open
                ));
            }
        }
        // Not yet asked of foliage: the stems of a bush or a tuft meet in corners too small for a sample, and their shadow is not measured.
        Some(shadow) if !foliage => fail(format!(
            "painted.crevices_darker: only {crevice_count} samples lie in inside corners; nothing to measure crevice_shadow {shadow} on. A shape with no inside corner leaves crevice_shadow and crevice_width_m out of its spec"
        )),
        None if crevice_count >= MIN_SAMPLES => fail(format!(
            "painted.crevices_darker: {crevice_count} samples lie in inside corners, and the spec asks no crevice shadow of them (crevice_shadow, crevice_width_m)"
        )),
        _ => {}
    }

    // Banding: a smooth gradient uses every 8-bit level it passes through, so where two
    // neighbouring samples of one face lie either side of levels that no open face uses, the
    // texture steps over them, and the eye sees the step as a band. Levels unused only because
    // no open face lies at the height that would have them (a cap and a neck with air between,
    // stones piled on each other) are not passed through by any pair, and are no step.
    let open_at: std::collections::HashMap<(u32, u32), &Sample> = samples.iter().filter(|s| s.zone == Zone::Open).map(|s| (s.at, s)).collect();
    let mut greens: Vec<u8> = open_at.values().map(|s| s.green).collect();
    greens.sort_unstable();
    let inner = &greens[greens.len() / 50..greens.len() - greens.len() / 50];
    let mut used = [false; 256];
    for &level in inner {
        used[level as usize] = true;
    }
    let mut stepped_over = [false; 256];
    for (&(x, y), sample) in &open_at {
        for next in [(x + stride, y), (x, y + stride)] {
            let Some(other) = open_at.get(&next) else { continue };
            // Neighbours in the texture that are not neighbours on the surface lie on two islands of the layout.
            if sample.point.distance(other.point) > NEIGHBOUR_STEPS * sample.step_m.max(other.step_m) {
                continue;
            }
            for level in sample.green.min(other.green) as usize + 1..sample.green.max(other.green) as usize {
                stepped_over[level] = true;
            }
        }
    }
    let mut run = 0;
    for level in inner[0]..=inner[inner.len() - 1] {
        run = if stepped_over[level as usize] && !used[level as usize] { run + 1 } else { 0 };
        measured.level_gap = measured.level_gap.max(run);
    }
    if measured.level_gap > want.max_level_gap {
        fail(format!(
            "painted.banding: open faces span 8-bit levels {}..{} of the green channel, and neighbouring texels step over a run of {} that none of them uses; conventions allow {}",
            inner[0],
            inner[inner.len() - 1],
            measured.level_gap,
            want.max_level_gap
        ));
    }

    // Variation, each kind measured where the geometry says it should be and nowhere else.
    let average = |pick: &dyn Fn(&Sample) -> bool, value: &dyn Fn(&Sample) -> f32| {
        let values: Vec<f32> = samples.iter().filter(|s| pick(s)).map(value).collect();
        (values.len(), values.iter().sum::<f32>() / values.len().max(1) as f32)
    };
    let upright = |s: &Sample| s.up.abs() <= want.side_shade_normal_z[0];
    let level = |s: &Sample| s.up >= want.growth_up_normal_z[1];
    if want.growth.is_some() {
        // Clear of the ragged top of the growth, which wanders by half its height either way.
        let (low, high) = (want.growth_height_m * 0.4, above_base);
        // Each amount is measured where the rock has it: on open faces, clear of edges and joins. A shape may have no
        // such face of the kind asked (a slab or a pebble has no upright one above its wash, a standing stone no level
        // one, a stack none at all up there). It is then measured on the surface the shape does have, named in the
        // message, and fails only if it has none of that either: nothing passes unmeasured.
        let settles = |s: &Sample| s.up >= want.growth_up_normal_z[0];
        let seen = |s: &Sample| s.zone != Zone::Crevice && s.above > high;
        let (base_count, base) = average(&|s| s.zone != Zone::Crevice && s.above < low, &|s| s.growth);
        let (mut bare_count, mut bare) = average(&|s| s.zone == Zone::Open && upright(s) && s.above > high, &|s| s.growth);
        let (mut bare_on, mut bare_most) = ("upright open faces", 0.15);
        if bare_count < MIN_SAMPLES {
            // No upright open face: the open faces growth does not settle on, upright or leaning.
            (bare_count, bare) = average(&|s| s.zone == Zone::Open && !settles(s) && s.above > high, &|s| s.growth);
            bare_on = "open faces that are not near level";
        }
        if bare_count < MIN_SAMPLES {
            // No open face it does not settle on: every such face is within reach of an edge or a join, where growth
            // along edges is asked. It may show what that puts there, by the measure growth on level faces is held to, and no more.
            (bare_count, bare) = average(&|s| seen(s) && !settles(s), &|s| s.growth);
            bare_on = "faces that are not near level, none of them clear of an edge or a join";
            bare_most = (want.growth_cover[1] * want.growth_edges).max(bare_most);
        }
        (measured.growth_base, measured.growth_bare_sides) = (base, bare);
        if base_count < MIN_SAMPLES || bare_count < MIN_SAMPLES || base < 0.7 || bare > bare_most {
            fail(format!(
                "painted.growth_height: growth shows on {base:.2} of the surface below {low:.2} m ({base_count} samples; wanted at least 0.7) and on {bare:.2} of {bare_on} above {high:.2} m ({bare_count} samples; wanted at most {bare_most:.2}); growth_height_m is {}",
                want.growth_height_m
            ));
        }
        if want.growth_up > 0.0 {
            let (mut count, mut cover) = average(&|s| s.zone == Zone::Open && level(s) && s.above > high, &|s| s.growth);
            let [least, mut most] = want.growth_cover.map(|share| share * want.growth_up);
            let mut on = "level open faces";
            if count < MIN_SAMPLES {
                // No level face clear of an edge or a join: the level faces there are. Growth along edges lies on them
                // too, so they may show the two together; bare of both, or carpeted, they fail as the open ones do.
                (count, cover) = average(&|s| seen(s) && level(s), &|s| s.growth);
                on = "level faces, none of them clear of an edge or a join";
                most = want.growth_cover[1] * (want.growth_up + want.growth_edges - want.growth_up * want.growth_edges);
            }
            measured.growth_up = cover;
            if count < MIN_SAMPLES || cover < least || cover > most {
                fail(format!(
                    "painted.growth_up: growth covers {cover:.2} of {on} above {high:.2} m ({count} samples); growth_up {} wants {least:.2} to {most:.2}: patches, neither bare nor a carpet. A shape with no face near level above its wash leaves growth_up out of its spec",
                    want.growth_up
                ));
            }
        }
        if want.growth_edges > 0.0 {
            let (mut count, mut cover) = average(&|s| s.zone == Zone::Edge && upright(s) && s.height > 0.8, &|s| s.growth);
            let mut on = "the exposed edges of upright faces";
            if count < MIN_SAMPLES {
                // No upright edge clear of a join in the top fifth: the exposed edges there are, of any face growth does not settle on of itself.
                (count, cover) = average(&|s| s.rim && s.zone != Zone::Crevice && !settles(s) && s.height > 0.8, &|s| s.growth);
                on = "the exposed edges of faces that are not near level";
            }
            measured.growth_edges = cover;
            let least = want.min_effect_share * want.growth_edges;
            if count < MIN_SAMPLES || cover < least {
                fail(format!(
                    "painted.growth_edges: growth covers {cover:.2} of {on} in the top fifth ({count} samples); growth_edges {} wants at least {least:.2}. A shape whose top fifth is all near level, where the growth on level faces lies, leaves growth_edges out of its spec",
                    want.growth_edges
                ));
            }
        }
        if want.growth_darker > 0.0 {
            // Open faces above the base's growth: where they show growth against where they show none.
            // The tint and the side shade are already divided out, and blotches average out.
            let (mut grown_count, grown) = average(&|s| s.zone == Zone::Open && s.above > high && s.growth >= 0.8, &|s| s.bare_ratio);
            let (mut bare_count, bare) = average(&|s| s.zone == Zone::Open && s.above > high && s.growth <= 0.2, &|s| s.bare_ratio);
            let mut on = "open faces";
            measured.growth_darker = 1.0 - grown / bare.max(1e-6);
            if grown_count < MIN_SAMPLES || bare_count < MIN_SAMPLES {
                // Too little open face with growth on it, or without. Off open faces the edge light and the shadow at a
                // join change the tone as well, so a sample that shows growth is held against its own neighbour in the
                // texture that shows none: the two are a few centimetres apart and get the same of both. A patch's edge is
                // soft, so the pair shows growth g and h, not 1 and 0, and is darker by growth_darker times each: the tones
                // t and u are as (1 - d g) to (1 - d h), which gives d = (u - t) / (g u - h t), summed over the pairs.
                let near: std::collections::HashMap<(u32, u32), (f32, f32)> = samples.iter().filter(|s| seen(s)).map(|s| (s.at, (s.growth, s.bare_ratio))).collect();
                let (mut pairs, mut step, mut scale) = (0usize, 0.0f32, 0.0f32);
                for (&(x, y), &(growth, tone)) in &near {
                    for next in [(x + stride, y), (x, y + stride)] {
                        let Some(&(other, other_tone)) = near.get(&next) else { continue };
                        if growth.max(other) >= 0.8 && growth.min(other) <= 0.2 {
                            let ((g, t), (h, u)) = if growth > other { ((growth, tone), (other, other_tone)) } else { ((other, other_tone), (growth, tone)) };
                            pairs += 1;
                            step += u - t;
                            scale += g * u - h * t;
                        }
                    }
                }
                (grown_count, bare_count) = (pairs, pairs);
                on = "neighbouring samples, on any face";
                measured.growth_darker = step / scale.max(1e-6);
            }
            if grown_count < MIN_SAMPLES || bare_count < MIN_SAMPLES || (measured.growth_darker - want.growth_darker).abs() > want.colour_tolerance {
                fail(format!(
                    "painted.growth_darker: {on} above {high:.2} m are {:.3} darker where they show growth ({grown_count} samples) than where they show none ({bare_count} samples); growth_darker {} wants that within {}",
                    measured.growth_darker, want.growth_darker, want.colour_tolerance
                ));
            }
        }
        if want.growth_patch_m > 0.0 {
            // How often growth starts or stops between neighbouring samples of level open faces, per patch length:
            // small, broken patches have a lot of outline for their area, and broad ones little.
            let outline = |pick: &dyn Fn(&Sample) -> bool| {
                let grown: std::collections::HashMap<(u32, u32), (bool, f32)> = samples.iter().filter(|s| pick(s)).map(|s| (s.at, (s.growth >= 0.5, s.step_m))).collect();
                let (mut edges, mut metres) = (0usize, 0.0f32);
                for (&(x, y), &(here, step)) in &grown {
                    if let Some(&(next, _)) = grown.get(&(x + stride, y)) {
                        edges += usize::from(here != next);
                        metres += step;
                    }
                }
                (edges, metres)
            };
            let (mut edges, mut metres) = outline(&|s| s.zone == Zone::Open && level(s) && s.above > high);
            let mut on = "level open faces";
            if metres < 1.0 {
                // Under a metre of level open face: every surface the patches are asked on in full, the level faces
                // there are and the exposed edges of the top fifth.
                (edges, metres) = outline(&|s| seen(s) && (level(s) || (s.rim && s.height > 0.8)));
                on = "level faces and the exposed edges of the top fifth";
            }
            measured.growth_patch_edges = edges as f32 / metres.max(1e-6) * want.growth_patch_m;
            if metres < 1.0 || measured.growth_patch_edges < want.growth_patch_edges {
                fail(format!(
                    "painted.growth_patches: on {on} above {high:.2} m growth starts or stops {:.2} times per {} m ({edges} times in {metres:.1} m sampled); conventions want at least {} for patches of growth_patch_m {}: small and broken, not broad",
                    measured.growth_patch_edges, want.growth_patch_m, want.growth_patch_edges, want.growth_patch_m
                ));
            }
        }
    }
    if want.blotch > 0.0 {
        // Open faces whose tone the formula gives. Between the foot of the growth at the base and the height it is
        // clear of, a patch of growth is darker by an amount that depends on how far the base's growth reaches at
        // that spot, which only the paint knows: a sample showing growth there is not held to be a blotch.
        let band = (want.growth_height_m * 0.4, above_base);
        let plain = |s: &Sample| s.zone == Zone::Open && !(want.growth_darker > 0.0 && s.growth > 0.2 && s.above > band.0 && s.above <= band.1);
        let mut tones: Vec<f32> = samples.iter().filter(|s| plain(s)).map(|s| s.ratio).collect();
        tones.sort_by(f32::total_cmp);
        measured.blotch_spread = tones[tones.len() * 9 / 10] - tones[tones.len() / 10];
        let [least, most] = want.blotch_spread.map(|share| share * want.blotch);
        if measured.blotch_spread < least || measured.blotch_spread > most {
            fail(format!(
                "painted.blotches: the tone of open faces spreads {:.3} from its 10th to its 90th percentile; blotch {} wants {least:.3} to {most:.3}",
                measured.blotch_spread, want.blotch
            ));
        }
        // Neighbouring samples, a stride apart along a row of the texture.
        let open: std::collections::HashMap<(u32, u32), f32> =
            samples.iter().filter(|s| plain(s)).map(|s| (s.at, s.ratio)).collect();
        let steps: Vec<f32> = open.iter().filter_map(|(&(x, y), ratio)| open.get(&(x + stride, y)).map(|next| (next - ratio).abs())).collect();
        measured.blotch_grain = steps.iter().sum::<f32>() / steps.len().max(1) as f32 / measured.blotch_spread.max(1e-6);
        if measured.blotch_grain > want.max_blotch_grain {
            fail(format!(
                "painted.blotches_broad: neighbouring samples of open faces differ by {:.2} of the tone spread on average; conventions allow {}: blotches are broad patches, not grain",
                measured.blotch_grain, want.max_blotch_grain
            ));
        }
    }
    if want.side_shade > 0.0 {
        // What the tint alone would give, against what is there, where at least half the shade is due.
        let side = |s: &Sample| s.zone == Zone::Open && s.shade >= 0.5;
        let (count, due) = average(&side, &|s| s.shade);
        let (_, tone) = average(&side, &|s| s.ratio * (1.0 - want.side_shade * s.shade));
        (measured.side_shade, measured.side_shade_expected) = (1.0 - tone, want.side_shade * due);
        let least = want.min_effect_share * want.side_shade * due;
        if count < MIN_SAMPLES || 1.0 - tone < least {
            fail(format!(
                "painted.side_shade: upright open faces near mid height are {:.3} darker than the tint alone makes them ({count} samples); side_shade {} wants at least {least:.3}",
                1.0 - tone,
                want.side_shade
            ));
        }
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
