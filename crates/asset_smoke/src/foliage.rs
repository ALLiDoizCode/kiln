//! Foliage checks (gate L4): what the leaf pieces Bevy loaded look like, measured on
//! the loaded triangles, UVs and texels, against the manifest (ADR 11).
//!
//! `tools/paint.py` gives every leaf piece one colour from a palette: the leaf
//! material's colour times a tint that runs from `under_tint` at the bottom of
//! the piece's pad to `top_tint` at its top, in `shades` steps, each in `tones`
//! tones from `variation` darker to `variation` lighter. Here pieces and pads
//! are found again from the loaded triangles alone, the way `tools/foliage.py`
//! finds them: a piece is triangles joined by shared corners, and a pad is
//! pieces with no clear air between them on a grid of `pad_gap_m`.

use std::collections::{BTreeSet, HashMap};

use bevy::{image::Image, prelude::*};
use serde::{Deserialize, Serialize};

use crate::painted::Triangle;

/// From the asset's spec (`foliage`) and `conventions.toml`, written by `tools/export.py`.
#[derive(Deserialize)]
pub struct Foliage {
    pub material: String,
    pad_gap_m: f32,
    min_pad_pieces: usize,
    /// Linear RGB multipliers at the bottom and the top of a pad.
    under_tint: [f32; 3],
    top_tint: [f32; 3],
    shades: usize,
    tones: usize,
    variation: f32,
    /// How far a piece's colour may be from the nearest palette colour, per channel, linear.
    max_palette_error: f32,
    /// The share of pieces whose nearest piece must be another colour.
    min_neighbours_differ: f32,
    /// The share of the tints' difference the measured pads must show.
    min_effect_share: f32,
}

#[derive(Serialize, Default)]
pub struct Measured {
    pieces: usize,
    /// Pieces in each pad of at least `min_pad_pieces`, largest first.
    pads: Vec<usize>,
    /// Pieces whose corners do not all show one colour.
    shaded_pieces: usize,
    colours: usize,
    off_palette: usize,
    neighbours_differ: f32,
    /// Luminance of the highest quarter of each pad's pieces over its lowest quarter: the least of the pads, and what the tints give.
    lighter_above: f32,
    lighter_above_expected: f32,
    /// Blue as a share of the colour, in the lowest and the highest quarter of the pads' pieces.
    blue_below: f32,
    blue_above: f32,
}

const LUMA: Vec3 = Vec3::new(0.2126, 0.7152, 0.0722);

struct Piece {
    middle: Vec3,
    colour: Vec3,
    pad: usize,
}

pub fn check(
    want: &Foliage,
    material_colour: Option<&[f32; 3]>,
    triangles: &[Triangle],
    image: &Image,
    two_sided: bool,
    fail: &mut impl FnMut(String),
) -> Measured {
    let mut measured = Measured::default();
    if !two_sided {
        fail(format!(
            "foliage.two_sided: material '{}' is not double-sided; a leaf piece would vanish seen from behind",
            want.material
        ));
    }
    let Some(material_colour) = material_colour else {
        fail(format!("foliage.pieces: the manifest gives no colour for '{}'", want.material));
        return measured;
    };
    if triangles.is_empty() || triangles.iter().any(|t| t.uvs.is_none()) {
        fail(format!("foliage.pieces: {} triangles of '{}', all needing TEXCOORD_0", triangles.len(), want.material));
        return measured;
    }

    // Pieces: triangles joined by shared corners.
    let key = |p: Vec3| ((p.x * 1e4).round() as i64, (p.y * 1e4).round() as i64, (p.z * 1e4).round() as i64);
    let mut parent: Vec<usize> = (0..triangles.len()).collect();
    fn find(parent: &mut [usize], mut i: usize) -> usize {
        while parent[i] != i {
            parent[i] = parent[parent[i]];
            i = parent[i];
        }
        i
    }
    let mut corner_owner: HashMap<(i64, i64, i64), usize> = HashMap::new();
    for (index, triangle) in triangles.iter().enumerate() {
        for corner in triangle.positions {
            let other = *corner_owner.entry(key(corner)).or_insert(index);
            let (a, b) = (find(&mut parent, index), find(&mut parent, other));
            parent[a] = b;
        }
    }
    let mut piece_of_root: HashMap<usize, usize> = HashMap::new();
    let piece_of: Vec<usize> = (0..triangles.len())
        .map(|index| {
            let root = find(&mut parent, index);
            let next = piece_of_root.len();
            *piece_of_root.entry(root).or_insert(next)
        })
        .collect();
    let count = piece_of_root.len();
    measured.pieces = count;

    // Each piece's colour, read at every corner's UV; a piece whose corners disagree is shaded.
    let (width, height) = (image.width() as f32, image.height() as f32);
    let texel = |uv: Vec2| {
        let x = (uv.x * width).floor().clamp(0.0, width - 1.0) as u32;
        let y = (uv.y * height).floor().clamp(0.0, height - 1.0) as u32;
        image.get_color_at(x, y).ok().map(|colour| {
            let linear = colour.to_linear();
            Vec3::new(linear.red, linear.green, linear.blue)
        })
    };
    let mut sums = vec![(Vec3::ZERO, Vec3::ZERO, 0usize); count];
    let mut first: Vec<Option<Vec3>> = vec![None; count];
    let mut shaded = vec![false; count];
    for (triangle, &piece) in triangles.iter().zip(&piece_of) {
        for (position, uv) in triangle.positions.iter().zip(triangle.uvs.unwrap()) {
            let Some(colour) = texel(uv) else {
                fail("foliage.pieces: the texture has no readable texels".into());
                return measured;
            };
            match first[piece] {
                None => first[piece] = Some(colour),
                Some(seen) if (seen - colour).abs().max_element() > 1e-4 => shaded[piece] = true,
                Some(_) => {}
            }
            let entry = &mut sums[piece];
            *entry = (entry.0 + *position, entry.1 + colour, entry.2 + 1);
        }
    }
    measured.shaded_pieces = shaded.iter().filter(|&&s| s).count();
    if measured.shaded_pieces > 0 {
        fail(format!(
            "foliage.flat_colour: {} of {count} leaf pieces show more than one colour across their corners; each piece is one flat colour",
            measured.shaded_pieces
        ));
    }

    // Pads: pieces with no clear air between them, on a grid of pad_gap_m.
    let cell = want.pad_gap_m;
    let longest = triangles
        .iter()
        .flat_map(|t| [t.positions[0].distance(t.positions[1]), t.positions[1].distance(t.positions[2]), t.positions[2].distance(t.positions[0])])
        .fold(0.0, f32::max);
    let steps = ((longest / (cell / 2.0)).ceil() as usize).max(1);
    let mut cube_owner: HashMap<(i32, i32, i32), usize> = HashMap::new();
    let mut pad_parent: Vec<usize> = (0..count).collect();
    for (triangle, &piece) in triangles.iter().zip(&piece_of) {
        let [a, b, c] = triangle.positions;
        for i in 0..=steps {
            for j in 0..=(steps - i) {
                let p = a + (b - a) * (i as f32 / steps as f32) + (c - a) * (j as f32 / steps as f32);
                let cube = ((p.x / cell).floor() as i32, (p.y / cell).floor() as i32, (p.z / cell).floor() as i32);
                let other = *cube_owner.entry(cube).or_insert(piece);
                let (x, y) = (find(&mut pad_parent, piece), find(&mut pad_parent, other));
                pad_parent[x] = y;
            }
        }
    }
    let cubes: Vec<((i32, i32, i32), usize)> = cube_owner.iter().map(|(cube, piece)| (*cube, *piece)).collect();
    for ((x, y, z), piece) in cubes {
        for dx in -1..=1 {
            for dy in -1..=1 {
                for dz in -1..=1 {
                    if let Some(&other) = cube_owner.get(&(x + dx, y + dy, z + dz)) {
                        let (a, b) = (find(&mut pad_parent, piece), find(&mut pad_parent, other));
                        pad_parent[a] = b;
                    }
                }
            }
        }
    }
    let pieces: Vec<Piece> = (0..count)
        .map(|piece| Piece {
            middle: sums[piece].0 / sums[piece].2 as f32,
            colour: sums[piece].1 / sums[piece].2 as f32,
            pad: find(&mut pad_parent, piece),
        })
        .collect();
    let mut pads: HashMap<usize, Vec<&Piece>> = HashMap::new();
    for piece in &pieces {
        pads.entry(piece.pad).or_default().push(piece);
    }
    let mut pads: Vec<Vec<&Piece>> = pads.into_values().filter(|pad| pad.len() >= want.min_pad_pieces).collect();
    pads.sort_by_key(|pad| std::cmp::Reverse(pad.len()));
    measured.pads = pads.iter().map(Vec::len).collect();
    if pads.is_empty() {
        fail(format!(
            "foliage.pieces: {count} leaf pieces form no pad of at least {} pieces",
            want.min_pad_pieces
        ));
        return measured;
    }

    // The palette the spec gives, and how far each piece's colour is from it.
    let material = Vec3::from(*material_colour);
    let (under, top) = (Vec3::from(want.under_tint), Vec3::from(want.top_tint));
    let palette: Vec<Vec3> = (0..want.shades)
        .flat_map(|shade| {
            let tint = under.lerp(top, shade as f32 / (want.shades - 1) as f32);
            (0..want.tones).map(move |tone| {
                let lift = 1.0 + want.variation * (2.0 * tone as f32 / (want.tones - 1) as f32 - 1.0);
                (material * tint * lift).min(Vec3::ONE)
            })
        })
        .collect();
    measured.off_palette = pieces
        .iter()
        .filter(|piece| palette.iter().all(|colour| (*colour - piece.colour).abs().max_element() > want.max_palette_error))
        .count();
    if measured.off_palette > 0 {
        fail(format!(
            "foliage.palette: {} of {count} leaf pieces are further than {} (linear, per channel) from every colour the spec's leaf colour, tints, shades and tones give",
            measured.off_palette, want.max_palette_error
        ));
    }
    let distinct: BTreeSet<(u32, u32, u32)> = pieces
        .iter()
        .map(|piece| ((piece.colour.x * 1000.0) as u32, (piece.colour.y * 1000.0) as u32, (piece.colour.z * 1000.0) as u32))
        .collect();
    measured.colours = distinct.len();

    // Neighbours differ: the nearest other piece is another colour.
    let differ = pieces
        .iter()
        .enumerate()
        .filter(|(index, piece)| {
            pieces
                .iter()
                .enumerate()
                .filter(|(other, _)| other != index)
                .min_by(|(_, a), (_, b)| a.middle.distance_squared(piece.middle).total_cmp(&b.middle.distance_squared(piece.middle)))
                .is_some_and(|(_, nearest)| (nearest.colour - piece.colour).abs().max_element() > 1e-3)
        })
        .count();
    measured.neighbours_differ = differ as f32 / count as f32;
    if measured.neighbours_differ < want.min_neighbours_differ {
        fail(format!(
            "foliage.colour_varies: {:.2} of the leaf pieces have a nearest neighbour of another colour ({} colours in all); conventions want at least {}",
            measured.neighbours_differ, measured.colours, want.min_neighbours_differ
        ));
    }

    // Lighter and yellower above, darker and bluer below, in every pad: its highest quarter of pieces against its lowest.
    let full = (material * top).dot(LUMA) / (material * under).dot(LUMA);
    measured.lighter_above_expected = full;
    let floor = 1.0 + want.min_effect_share * (full - 1.0);
    let blue = |colour: Vec3| colour.z / (colour.x + colour.y + colour.z).max(1e-6);
    let (mut least, mut below, mut above) = (f32::MAX, Vec3::ZERO, Vec3::ZERO);
    for pad in &mut pads {
        pad.sort_by(|a, b| a.middle.y.total_cmp(&b.middle.y));
        let quarter = (pad.len() / 4).max(1);
        let mean = |part: &[&Piece]| part.iter().map(|piece| piece.colour).sum::<Vec3>() / part.len() as f32;
        let (low, high) = (mean(&pad[..quarter]), mean(&pad[pad.len() - quarter..]));
        least = least.min(high.dot(LUMA) / low.dot(LUMA).max(1e-6));
        below += low;
        above += high;
    }
    measured.lighter_above = least;
    (measured.blue_below, measured.blue_above) = (blue(below), blue(above));
    if least < floor {
        fail(format!(
            "foliage.lighter_above: in the pad where it is least, the highest quarter of the pieces is {least:.2} times as light as the lowest quarter; the tints give {full:.2} from bottom to top, and conventions want at least {floor:.2}"
        ));
    }
    // Asked only when the spec's underside tint is itself bluer than its top tint.
    let tint_blue = |tint: Vec3| blue(material * tint);
    if tint_blue(under) > tint_blue(top) + 1e-4 {
        let wanted = want.min_effect_share * (tint_blue(under) - tint_blue(top));
        if measured.blue_below - measured.blue_above < wanted {
            fail(format!(
                "foliage.bluer_below: blue is {:.3} of the colour in the pads' lowest quarters and {:.3} in their highest; the tints give {:.3} and {:.3}, and conventions want the difference to be at least {wanted:.3}",
                measured.blue_below,
                measured.blue_above,
                tint_blue(under),
                tint_blue(top)
            ));
        }
    }
    measured
}
