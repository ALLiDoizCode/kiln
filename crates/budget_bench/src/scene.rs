//! Procedural content for a measured scene: where the assets stand, their meshes and their
//! textures. Everything is a pure function of its arguments, so a rerun draws the same scene.

use bevy::{
    asset::RenderAssetUsages,
    image::{ImageAddressMode, ImageFilterMode, ImageSampler, ImageSamplerDescriptor},
    math::{Vec2, Vec3},
    mesh::{Indices, Mesh, PrimitiveTopology},
    prelude::Image,
    render::render_resource::{Extent3d, TextureDescriptor, TextureDimension, TextureFormat, TextureUsages},
};

use crate::case::TexFormat;

/// Eye height of the 1.8 m player.
pub const EYE_HEIGHT: f32 = 1.7;
/// Vertical field of view, in degrees.
pub const FOV_DEGREES: f32 = 72.0;
/// The camera looks this far below the horizon, in degrees.
pub const PITCH_DOWN_DEGREES: f32 = 8.0;
/// Distance from the camera to the surface of the nearest asset: the pit game's closest view.
pub const NEAREST: f32 = 0.5;
/// Largest dimension of every asset, in metres.
pub const ASSET_SIZE: f32 = 1.0;
/// Assets behind the nearest one stand on a jittered grid with this spacing, in metres.
pub const SPACING: f32 = 2.0;
/// Distances in metres beyond which an asset drops to a quarter, a sixteenth and a sixty-fourth
/// of its triangles when levels of detail are on.
pub const LOD_DISTANCES: [f32; 3] = [10.0, 20.0, 40.0];

fn mix(mut x: u64) -> u64 {
    x = x.wrapping_add(0x9E37_79B9_7F4A_7C15);
    x = (x ^ (x >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    x = (x ^ (x >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    x ^ (x >> 31)
}

/// A number in 0..1 from a seed.
fn unit(seed: u64) -> f32 {
    (mix(seed) >> 40) as f32 / (1u64 << 24) as f32
}

/// Where each asset's centre is, nearest first, with a turn about the vertical axis.
///
/// The first asset floats 0.5 m from the camera, right of centre. The rest stand on the ground
/// in the wedge the camera sees, on a jittered grid, so more assets reach further away.
pub fn layout(count: u32, aspect: f32) -> Vec<(Vec3, f32)> {
    let mut placed = Vec::new();
    if count == 0 {
        return placed;
    }
    let eye = Vec3::new(0.0, EYE_HEIGHT, 0.0);
    let (yaw, pitch) = (30f32.to_radians(), 20f32.to_radians());
    let direction = Vec3::new(yaw.sin() * pitch.cos(), -pitch.sin(), -yaw.cos() * pitch.cos());
    placed.push((eye + direction * (NEAREST + ASSET_SIZE / 2.0), 0.0));

    let half_width = ((FOV_DEGREES / 2.0).to_radians().tan() * aspect).atan() - 3f32.to_radians();
    let wanted = count as usize - 1;
    // The wedge's area grows with the square of its radius; search far enough for `wanted`.
    let radius = (wanted as f32 * SPACING * SPACING / half_width).sqrt() * 1.3 + 4.0 * SPACING;
    let cells = (radius / SPACING).ceil() as i32;
    let mut candidates = Vec::new();
    for ix in -cells..=cells {
        for iz in 1..=cells {
            let seed = ((ix + 100_000) as u64) << 32 | iz as u64;
            let x = (ix as f32 + (unit(seed) - 0.5) * 0.5) * SPACING;
            let z = (iz as f32 + (unit(seed ^ 0xABCD) - 0.5) * 0.5) * SPACING;
            let distance = Vec2::new(x, z).length();
            if distance >= 2.0 && (x / z).atan().abs() < half_width {
                candidates.push((distance, Vec3::new(x, ASSET_SIZE * 0.45, -z), unit(seed ^ 0x55) * std::f32::consts::TAU));
            }
        }
    }
    candidates.sort_by(|a, b| a.0.total_cmp(&b.0));
    assert!(candidates.len() >= wanted, "layout search radius too small");
    placed.extend(candidates.into_iter().take(wanted).map(|(_, at, turn)| (at, turn)));
    placed
}

/// The level of detail an asset at `distance` metres uses: 0 is full detail.
pub fn lod_level(distance: f32) -> u32 {
    LOD_DISTANCES.iter().filter(|&&limit| distance >= limit).count() as u32
}

/// Columns and rows of a sphere grid with as near to `triangles` triangles as a grid allows.
/// The count is exact whenever `triangles / 2` has a divisor near its square root.
fn grid_for(triangles: u32) -> (u32, u32) {
    let half = (triangles / 2).max(6);
    let ideal = (triangles as f64).sqrt();
    // Prefer an exact divisor within a factor of two of the ideal column count.
    let mut best: Option<u32> = None;
    let (low, high) = ((ideal / 2.0).max(3.0) as u32, (ideal * 2.0) as u32);
    for columns in low..=high {
        if half.is_multiple_of(columns) && half / columns >= 2 {
            let better = best.is_none_or(|b| (columns as f64 - ideal).abs() < (b as f64 - ideal).abs());
            if better {
                best = Some(columns);
            }
        }
    }
    let columns = best.unwrap_or((ideal.round() as u32).max(3));
    let bands = (half as f64 / columns as f64).round().max(2.0) as u32;
    (columns, bands + 1)
}

/// A rock-like closed shape of about `triangles` triangles with UVs, normals and tangents:
/// a sphere grid pushed in and out by a few waves, 1 m across. Returns the mesh and its
/// exact triangle and vertex counts.
pub fn rock_mesh(triangles: u32, seed: u64) -> (Mesh, u32, u32) {
    let (columns, rows) = grid_for(triangles);
    // Three waves across the surface, different for each seed.
    let waves: [(Vec3, f32); 3] = std::array::from_fn(|i| {
        let s = seed.wrapping_mul(31).wrapping_add(i as u64 * 7);
        let axis = Vec3::new(unit(s) - 0.5, unit(s + 1) - 0.5, unit(s + 2) - 0.5).normalize_or(Vec3::X);
        (axis * (2.0 + 2.0 * i as f32), unit(s + 3) * std::f32::consts::TAU)
    });
    let surface = |direction: Vec3| {
        let bump: f32 = waves.iter().map(|(axis, phase)| (direction.dot(*axis) + phase).sin()).sum();
        direction * (ASSET_SIZE / 2.0) * (1.0 + 0.05 * bump) / 1.15
    };

    let vertex_count = ((columns + 1) * (rows + 1)) as usize;
    let mut positions = Vec::with_capacity(vertex_count);
    let mut normals = Vec::with_capacity(vertex_count);
    let mut tangents = Vec::with_capacity(vertex_count);
    let mut uvs = Vec::with_capacity(vertex_count);
    for row in 0..=rows {
        let v = row as f32 / rows as f32;
        let (sin_phi, cos_phi) = (v * std::f32::consts::PI).sin_cos();
        for column in 0..=columns {
            let u = column as f32 / columns as f32;
            let (sin_theta, cos_theta) = (u * std::f32::consts::TAU).sin_cos();
            let direction = Vec3::new(sin_phi * cos_theta, cos_phi, sin_phi * sin_theta);
            let east = Vec3::new(-sin_theta, 0.0, cos_theta);
            let south = east.cross(direction).normalize();
            let here = surface(direction);
            let step = 1e-3;
            let to_east = surface((direction + east * step).normalize()) - here;
            let to_south = surface((direction + south * step).normalize()) - here;
            let normal = to_east.cross(to_south).normalize();
            let normal = if normal.dot(direction) < 0.0 { -normal } else { normal };
            let tangent = (east - normal * east.dot(normal)).normalize();
            positions.push(here.to_array());
            normals.push(normal.to_array());
            tangents.push([tangent.x, tangent.y, tangent.z, 1.0]);
            uvs.push([u * 2.0, v]);
        }
    }

    let mut indices: Vec<u32> = Vec::with_capacity((2 * columns * (rows - 1) * 3) as usize);
    for row in 0..rows {
        for column in 0..columns {
            let a = row * (columns + 1) + column;
            let b = a + columns + 1;
            // Counter-clockwise seen from outside. The top and bottom rows are fans of single
            // triangles, because all their upper (or lower) vertices are the one pole.
            if row != 0 {
                indices.extend([a, a + 1, b]);
            }
            if row != rows - 1 {
                indices.extend([a + 1, b + 1, b]);
            }
        }
    }
    // Fix the winding once, from one triangle, in case the grid's handedness is the other way.
    let corner = |i: usize| Vec3::from(positions[indices[i] as usize]);
    let middle = indices.len() / 6 * 3;
    let face = (corner(middle + 1) - corner(middle)).cross(corner(middle + 2) - corner(middle));
    if face.dot(corner(middle)) < 0.0 {
        for triangle in indices.as_chunks_mut::<3>().0 {
            triangle.swap(1, 2);
        }
    }

    let triangle_count = (indices.len() / 3) as u32;
    let mesh = Mesh::new(PrimitiveTopology::TriangleList, RenderAssetUsages::RENDER_WORLD)
        .with_inserted_attribute(Mesh::ATTRIBUTE_POSITION, positions)
        .with_inserted_attribute(Mesh::ATTRIBUTE_NORMAL, normals)
        .with_inserted_attribute(Mesh::ATTRIBUTE_TANGENT, tangents)
        .with_inserted_attribute(Mesh::ATTRIBUTE_UV_0, uvs)
        .with_inserted_indices(Indices::U32(indices));
    (mesh, triangle_count, vertex_count as u32)
}

/// Which of an asset's three textures an image is.
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum Map {
    BaseColour,
    Normal,
    MetallicRoughness,
}

/// Bytes of one texture on the GPU: every mip level, summed.
pub fn texture_bytes(size: u32, mips: bool, format: TexFormat) -> u64 {
    let levels = if mips { size.ilog2() + 1 } else { 1 };
    (0..levels)
        .map(|level| {
            let side = (size >> level).max(1) as u64;
            match format {
                TexFormat::Rgba8 => side * side * 4,
                TexFormat::Bc7 => side.div_ceil(4) * side.div_ceil(4) * 16,
            }
        })
        .sum()
}

/// One square texture of noise, `size` pixels a side, with or without its mip chain.
pub fn texture(size: u32, map: Map, mips: bool, format: TexFormat, seed: u64) -> Image {
    assert!(size.is_power_of_two() && size >= 4, "texture size must be a power of two, 4 or more");
    let levels = if mips { size.ilog2() + 1 } else { 1 };
    let mut data = Vec::with_capacity(texture_bytes(size, mips, format) as usize);
    match format {
        TexFormat::Rgba8 => {
            data.extend(noise_pixels(size, map, seed));
            let (mut start, mut side) = (0usize, size as usize);
            for _ in 1..levels {
                let next = halve(&data[start..start + side * side * 4], side);
                start = data.len();
                side /= 2;
                data.extend(next);
            }
        }
        TexFormat::Bc7 => {
            let mut state = mix(seed ^ map as u64);
            let bytes = texture_bytes(size, mips, format) as usize;
            while data.len() < bytes {
                state = mix(state);
                data.extend(state.to_le_bytes());
            }
        }
    }
    let srgb = map == Map::BaseColour;
    Image {
        data: Some(data),
        texture_descriptor: TextureDescriptor {
            label: None,
            size: Extent3d { width: size, height: size, depth_or_array_layers: 1 },
            mip_level_count: levels,
            sample_count: 1,
            dimension: TextureDimension::D2,
            format: match (format, srgb) {
                (TexFormat::Rgba8, true) => TextureFormat::Rgba8UnormSrgb,
                (TexFormat::Rgba8, false) => TextureFormat::Rgba8Unorm,
                (TexFormat::Bc7, true) => TextureFormat::Bc7RgbaUnormSrgb,
                (TexFormat::Bc7, false) => TextureFormat::Bc7RgbaUnorm,
            },
            usage: TextureUsages::TEXTURE_BINDING | TextureUsages::COPY_DST,
            view_formats: &[],
        },
        // Trilinear filtering, repeating, no anisotropic filtering: what Bevy's glTF loader
        // gives a texture whose file asks for linear filtering with mipmaps.
        sampler: ImageSampler::Descriptor(ImageSamplerDescriptor {
            address_mode_u: ImageAddressMode::Repeat,
            address_mode_v: ImageAddressMode::Repeat,
            mag_filter: ImageFilterMode::Linear,
            min_filter: ImageFilterMode::Linear,
            mipmap_filter: ImageFilterMode::Linear,
            ..Default::default()
        }),
        asset_usage: RenderAssetUsages::RENDER_WORLD,
        ..Default::default()
    }
}

/// RGBA pixels: smooth noise at two scales plus per-pixel noise, so no part of the image is flat.
fn noise_pixels(size: u32, map: Map, seed: u64) -> Vec<u8> {
    let smooth = |x: u32, y: u32, cell: u32, salt: u64| {
        let cells = (size / cell).max(1);
        let corner = |cx: u32, cy: u32| unit(seed ^ salt ^ ((cx % cells) as u64) << 20 ^ ((cy % cells) as u64) << 40);
        let (cx, cy) = (x / cell, y / cell);
        let (fx, fy) = ((x % cell) as f32 / cell as f32, (y % cell) as f32 / cell as f32);
        let (fx, fy) = (fx * fx * (3.0 - 2.0 * fx), fy * fy * (3.0 - 2.0 * fy));
        let top = corner(cx, cy) * (1.0 - fx) + corner(cx + 1, cy) * fx;
        let bottom = corner(cx, cy + 1) * (1.0 - fx) + corner(cx + 1, cy + 1) * fx;
        top * (1.0 - fy) + bottom * fy
    };
    let (coarse, fine) = ((size / 8).max(1), (size / 64).max(1));
    let tint = [0.5 + 0.5 * unit(seed ^ 1), 0.5 + 0.5 * unit(seed ^ 2), 0.5 + 0.5 * unit(seed ^ 3)];
    let byte = |value: f32| (value.clamp(0.0, 1.0) * 255.0) as u8;
    let mut pixels = Vec::with_capacity((size * size * 4) as usize);
    for y in 0..size {
        for x in 0..size {
            let grain = mix(seed ^ (x as u64) << 32 ^ y as u64);
            let (g0, g1) = ((grain & 0xFF) as f32 / 255.0, (grain >> 8 & 0xFF) as f32 / 255.0);
            let (a, b) = (smooth(x, y, coarse, 11), smooth(x, y, fine, 22));
            let pixel = match map {
                Map::BaseColour => {
                    let shade = 0.25 + 0.45 * a + 0.2 * b + 0.1 * g0;
                    [byte(shade * tint[0]), byte(shade * tint[1]), byte(shade * tint[2]), 255]
                }
                Map::Normal => {
                    // A direction leaning a little off straight out, as a normal map stores it.
                    let (dx, dy) = ((b - 0.5) * 0.6 + (g0 - 0.5) * 0.2, (a - 0.5) * 0.6 + (g1 - 0.5) * 0.2);
                    let n = Vec3::new(dx, dy, 1.0).normalize();
                    [byte(n.x * 0.5 + 0.5), byte(n.y * 0.5 + 0.5), byte(n.z * 0.5 + 0.5), 255]
                }
                // glTF packing: roughness in green, metallic in blue.
                Map::MetallicRoughness => [0, byte(0.35 + 0.5 * b + 0.1 * g0), if a > 0.7 { 255 } else { 0 }, 255],
            };
            pixels.extend(pixel);
        }
    }
    pixels
}

/// The next mip level: each pixel is the mean of a 2 by 2 block.
fn halve(pixels: &[u8], side: usize) -> Vec<u8> {
    let half = side / 2;
    let mut out = Vec::with_capacity(half * half * 4);
    for y in 0..half {
        for x in 0..half {
            for channel in 0..4 {
                let at = |dx: usize, dy: usize| pixels[((y * 2 + dy) * side + x * 2 + dx) * 4 + channel] as u32;
                out.push(((at(0, 0) + at(1, 0) + at(0, 1) + at(1, 1) + 2) / 4) as u8);
            }
        }
    }
    out
}

/// Runs `make(0..count)` across all cores and returns the results in order.
pub fn in_parallel<T: Send>(count: usize, make: impl Fn(usize) -> T + Sync) -> Vec<T> {
    let next = std::sync::atomic::AtomicUsize::new(0);
    let threads = std::thread::available_parallelism().map_or(4, |n| n.get()).min(count.max(1));
    let mut slots: Vec<Option<T>> = (0..count).map(|_| None).collect();
    let made: Vec<Vec<(usize, T)>> = std::thread::scope(|scope| {
        let workers: Vec<_> = (0..threads)
            .map(|_| {
                scope.spawn(|| {
                    let mut mine = Vec::new();
                    loop {
                        let index = next.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
                        if index >= count {
                            return mine;
                        }
                        mine.push((index, make(index)));
                    }
                })
            })
            .collect();
        workers.into_iter().map(|worker| worker.join().unwrap()).collect()
    });
    for (index, value) in made.into_iter().flatten() {
        slots[index] = Some(value);
    }
    slots.into_iter().map(Option::unwrap).collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn meshes_have_the_triangle_count_asked_for() {
        for triangles in [1_000, 2_000, 5_000, 10_000, 20_000, 50_000, 100_000, 200_000, 500_000, 1_000_000, 2_500, 12_500] {
            let (mesh, made, vertices) = rock_mesh(triangles, 7);
            assert_eq!(made, triangles, "asked for {triangles}");
            assert_eq!(mesh.indices().unwrap().len() as u32, made * 3);
            assert_eq!(mesh.count_vertices() as u32, vertices);
        }
    }

    #[test]
    fn mesh_faces_point_outwards_and_fit_the_asset_size() {
        let (mesh, _, _) = rock_mesh(2_000, 3);
        let positions = mesh.attribute(Mesh::ATTRIBUTE_POSITION).unwrap().as_float3().unwrap();
        let indices: Vec<usize> = mesh.indices().unwrap().iter().collect();
        for triangle in indices.chunks_exact(3) {
            let [a, b, c] = [0, 1, 2].map(|i| Vec3::from(positions[triangle[i]]));
            assert!((b - a).cross(c - a).dot(a + b + c) >= 0.0, "a triangle faces inwards");
        }
        let widest = positions.iter().map(|p| Vec3::from(*p).length()).fold(0.0, f32::max);
        assert!(widest <= ASSET_SIZE / 2.0 && widest > ASSET_SIZE * 0.4, "radius {widest}");
    }

    #[test]
    fn layout_puts_the_nearest_surface_at_half_a_metre_and_places_every_asset() {
        let eye = Vec3::new(0.0, EYE_HEIGHT, 0.0);
        for count in [0, 1, 10, 300, 3000] {
            let placed = layout(count, 16.0 / 9.0);
            assert_eq!(placed.len(), count as usize);
            if let Some((nearest, _)) = placed.first() {
                assert!((nearest.distance(eye) - ASSET_SIZE / 2.0 - NEAREST).abs() < 1e-4);
            }
        }
    }

    #[test]
    fn texture_bytes_match_the_image_data() {
        // A 1024 RGBA8 texture is 4 MiB, and a third more with its mip chain.
        assert_eq!(texture_bytes(1024, false, TexFormat::Rgba8), 4 << 20);
        assert_eq!(texture_bytes(1024, true, TexFormat::Rgba8), 5_592_404);
        // Block compression stores 16 bytes per 4 by 4 block: a quarter of RGBA8.
        assert_eq!(texture_bytes(1024, false, TexFormat::Bc7), 1 << 20);
        for (mips, format) in [(true, TexFormat::Rgba8), (false, TexFormat::Rgba8), (true, TexFormat::Bc7)] {
            let image = texture(64, Map::Normal, mips, format, 1);
            assert_eq!(image.data.unwrap().len() as u64, texture_bytes(64, mips, format));
        }
    }

    #[test]
    fn levels_of_detail_step_at_the_stated_distances() {
        assert_eq!([5.0, 10.0, 25.0, 40.0, 90.0].map(lod_level), [0, 1, 2, 3, 3]);
    }
}
