//! Headless Bevy load test (gate L4).
//!
//! Loads one GLB through the real `bevy_gltf` loader with no window and no
//! renderer, then compares what Bevy sees against the asset's manifest.
//! Images are loaded too (PNG only), so a painted texture is measured as
//! Bevy decoded it; see `painted.rs`.
//! Exit code is the only signal: 0 pass, 1 check failed, 2 usage or I/O error.
//!
//! Usage: asset_smoke <asset.glb> <manifest.json> [--report <out.json>]

use std::{
    collections::{BTreeMap, BTreeSet},
    path::{Path, PathBuf},
    process::ExitCode,
    time::{Duration, Instant},
};

use bevy::{
    app::TaskPoolPlugin,
    asset::{AssetPlugin, RecursiveDependencyLoadState, UnapprovedPathMode},
    gltf::{Gltf, GltfMaterial, GltfMesh, GltfNode, GltfPlugin},
    image::{CompressedImageFormatSupport, CompressedImageFormats, Image, ImagePlugin},
    log::LogPlugin,
    mesh::{Mesh, MeshPlugin, PrimitiveTopology, VertexAttributeValues},
    prelude::*,
    world_serialization::WorldSerializationPlugin,
};
use serde::{Deserialize, Serialize};

mod foliage;
mod grain;
mod painted;
mod pieces;

const LOAD_TIMEOUT: Duration = Duration::from_secs(60);
/// Per channel, in linear RGB. 8-bit sRGB steps are larger than this.
const COLOUR_TOLERANCE: f32 = 0.005;
/// Cosine of 1 degree: normals closer than this light the same.
const SAME_NORMAL_COS: f32 = 0.99985;

/// Written by `tools/export.py` from the Blender scene. Bounds are in glTF
/// space (+Y up, metres), over every mesh in the file with node transforms
/// applied.
#[derive(Deserialize)]
struct Manifest {
    nodes: Vec<String>,
    mesh_count: usize,
    /// Material name to base colour, as linear RGB.
    materials: BTreeMap<String, [f32; 3]>,
    /// A closed surface: its triangles must enclose a positive volume.
    watertight: bool,
    triangles: usize,
    bounds: Bounds,
    bounds_tolerance: f32,
    /// glTF attribute semantics every primitive must carry, e.g. "NORMAL".
    attributes: Vec<String>,
    /// Every edge above the ground is lit round: no position off the floor of
    /// the bounds carries two different normals.
    #[serde(default)]
    soft_edges: bool,
    /// Painted shading: the materials take their colour from one texture, and
    /// the texture does what this says. Absent: every material is one flat colour.
    #[serde(default)]
    painted: Option<painted::Painted>,
    /// Materials whose faces are separate open pieces (leaf pieces). They enclose
    /// nothing, so `watertight` is asked of every other material's triangles.
    #[serde(default)]
    open_materials: Vec<String>,
    /// Several closed pieces that pass into each other (ADR 13): facing outward is asked of
    /// each piece, and surface buried inside another piece is not measured as painted surface.
    #[serde(default)]
    overlap: bool,
    /// Foliage: one material's triangles are leaf pieces coloured from a palette
    /// in the painted texture, and are measured as such instead of as painted surface.
    #[serde(default)]
    foliage: Option<foliage::Foliage>,
}

/// The manifest's `painted` block again, for the keys `grain.rs` reads from it.
#[derive(Deserialize)]
struct GrainManifest {
    #[serde(default)]
    painted: Option<grain::Wanted>,
}

#[derive(Deserialize, Serialize, Clone, Copy)]
struct Bounds {
    min: [f32; 3],
    max: [f32; 3],
}

#[derive(Serialize, Default)]
struct Report {
    asset: String,
    passed: bool,
    failures: Vec<String>,
    nodes: Vec<String>,
    mesh_count: usize,
    material_count: usize,
    triangles: usize,
    bounds: Option<Bounds>,
    #[serde(skip_serializing_if = "Option::is_none")]
    painted: Option<painted::Measured>,
    #[serde(skip_serializing_if = "Option::is_none")]
    foliage: Option<foliage::Measured>,
    #[serde(skip_serializing_if = "Option::is_none")]
    grain: Option<grain::Measured>,
}

fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let (positional, report_path) = match parse_args(&args) {
        Ok(parsed) => parsed,
        Err(message) => {
            eprintln!("{message}\nusage: asset_smoke <asset.glb> <manifest.json> [--report <out.json>]");
            return ExitCode::from(2);
        }
    };
    let (glb, manifest_path) = (&positional[0], &positional[1]);

    let manifest: (Manifest, GrainManifest) = match std::fs::read_to_string(manifest_path)
        .map_err(|e| e.to_string())
        .and_then(|text| Ok((serde_json::from_str(&text).map_err(|e| e.to_string())?, serde_json::from_str(&text).map_err(|e| e.to_string())?)))
    {
        Ok(manifest) => manifest,
        Err(e) => {
            eprintln!("cannot read manifest {}: {e}", manifest_path.display());
            return ExitCode::from(2);
        }
    };

    let mut report = Report {
        asset: glb.display().to_string(),
        ..default()
    };
    match load(glb) {
        Ok(app) => measure(&app, &manifest.0, manifest.1.painted.as_ref(), &mut report),
        Err(e) => report.failures.push(e),
    }
    report.passed = report.failures.is_empty();

    let json = serde_json::to_string_pretty(&report).expect("report serialises");
    if let Some(path) = report_path {
        if let Err(e) = std::fs::write(&path, &json) {
            eprintln!("cannot write report {}: {e}", path.display());
            return ExitCode::from(2);
        }
    }
    println!("{json}");
    if report.passed {
        ExitCode::SUCCESS
    } else {
        ExitCode::from(1)
    }
}

fn parse_args(args: &[String]) -> Result<(Vec<PathBuf>, Option<PathBuf>), String> {
    let mut positional = Vec::new();
    let mut report = None;
    let mut iter = args.iter();
    while let Some(arg) = iter.next() {
        if arg == "--report" {
            report = Some(PathBuf::from(iter.next().ok_or("--report needs a path")?));
        } else {
            positional.push(PathBuf::from(arg));
        }
    }
    if positional.len() != 2 {
        return Err(format!("expected 2 arguments, got {}", positional.len()));
    }
    Ok((positional, report))
}

#[derive(Resource)]
struct Loading(Handle<Gltf>);

/// Runs the app until the GLB and all its dependencies have loaded or failed.
fn load(glb: &Path) -> Result<App, String> {
    let glb = glb
        .canonicalize()
        .map_err(|e| format!("cannot find {}: {e}", glb.display()))?;
    let dir = glb.parent().expect("file has a parent directory");
    let file = glb.file_name().expect("file has a name");

    let mut app = App::new();
    // The plugin set bevy_gltf's own tests use: no window, no renderer.
    app.add_plugins((
        LogPlugin::default(),
        TaskPoolPlugin::default(),
        AssetPlugin {
            file_path: dir.to_string_lossy().into_owned(),
            unapproved_path_mode: UnapprovedPathMode::Deny,
            ..default()
        },
        WorldSerializationPlugin,
        MeshPlugin,
        // The image asset type; the PNG decoder comes from the `png` cargo feature.
        ImagePlugin::default(),
        GltfPlugin::default(),
    ));
    // Normally set by the renderer; without it the loader warns on every file.
    app.insert_resource(CompressedImageFormatSupport(CompressedImageFormats::NONE));
    app.finish();
    app.cleanup();
    app.update();

    let server = app.world().resource::<AssetServer>().clone();
    let handle: Handle<Gltf> = server.load(file.to_string_lossy().into_owned());
    let id = handle.id();
    app.insert_resource(Loading(handle));

    let started = Instant::now();
    loop {
        app.update();
        match server.recursive_dependency_load_state(id) {
            RecursiveDependencyLoadState::Loaded => return Ok(app),
            RecursiveDependencyLoadState::Failed(e) => return Err(format!("load failed: {e}")),
            _ if started.elapsed() > LOAD_TIMEOUT => {
                return Err(format!("load timed out after {LOAD_TIMEOUT:?}"));
            }
            _ => std::thread::sleep(Duration::from_millis(1)),
        }
    }
}

fn measure(app: &App, manifest: &Manifest, grain: Option<&grain::Wanted>, report: &mut Report) {
    let world = app.world();
    let gltf = world
        .resource::<Assets<Gltf>>()
        .get(&world.resource::<Loading>().0)
        .expect("loaded Gltf is in Assets");
    let nodes = world.resource::<Assets<GltfNode>>();
    let gltf_meshes = world.resource::<Assets<GltfMesh>>();
    let meshes = world.resource::<Assets<Mesh>>();
    let images = world.resource::<Assets<Image>>();
    let mut failures = Vec::new();
    let mut fail = |message: String| failures.push(message);

    let node_names: BTreeSet<String> = gltf.named_nodes.keys().map(|k| k.to_string()).collect();
    for name in &manifest.nodes {
        if !node_names.contains(name) {
            fail(format!("node '{name}' missing; file has {node_names:?}"));
        }
    }
    if gltf.nodes.len() != gltf.named_nodes.len() {
        fail(format!(
            "{} of {} nodes are unnamed or share a name",
            gltf.nodes.len() - gltf.named_nodes.len(),
            gltf.nodes.len()
        ));
    }
    if gltf.meshes.len() != manifest.mesh_count {
        fail(format!("mesh_count {} != manifest {}", gltf.meshes.len(), manifest.mesh_count));
    }
    let materials = world.resource::<Assets<GltfMaterial>>();
    let found: BTreeSet<&str> = gltf.named_materials.keys().map(|k| &**k).collect();
    let wanted: BTreeSet<&str> = manifest.materials.keys().map(String::as_str).collect();
    if found != wanted || gltf.materials.len() != wanted.len() {
        fail(format!("materials {found:?} != manifest {wanted:?}"));
    }
    for (name, want) in &manifest.materials {
        let Some(material) = gltf.named_materials.get(name.as_str()).and_then(|h| materials.get(h)) else {
            continue;
        };
        // Painted: the manifest's colour is what the texture was painted from; painted.rs measures it.
        if manifest.painted.is_some() {
            continue;
        }
        let got = material.base_color.to_linear();
        let got = [got.red, got.green, got.blue];
        if got.iter().zip(want).any(|(a, b)| (a - b).abs() > COLOUR_TOLERANCE) {
            fail(format!("{name}: base colour {got:?} != manifest {want:?} (linear)"));
        }
        if material.base_color_texture.is_some() {
            fail(format!("flat.no_texture: {name}: has a base colour texture; the manifest expects a flat colour"));
        }
    }
    // Painted: the texture alone gives the colour, so the factor it is multiplied by must be white.
    let mut textures: Vec<Handle<Image>> = Vec::new();
    if manifest.painted.is_some() {
        for name in manifest.materials.keys() {
            let Some(material) = gltf.named_materials.get(name.as_str()).and_then(|h| materials.get(h)) else {
                continue;
            };
            let factor = material.base_color.to_linear();
            if [factor.red, factor.green, factor.blue].iter().any(|c| (c - 1.0).abs() > COLOUR_TOLERANCE) {
                fail(format!("painted.factor: {name}: base colour factor {factor:?} is not white, so it would tint the painted texture"));
            }
            match &material.base_color_texture {
                Some(texture) if !textures.contains(texture) => textures.push(texture.clone()),
                Some(_) => {}
                None => {}
            }
        }
        if textures.len() != 1 {
            fail(format!("painted.present: {} base colour textures; a painted asset has exactly one", textures.len()));
        }
    }
    let name_of = |handle: &Option<Handle<GltfMaterial>>| {
        let handle = handle.as_ref()?;
        Some(gltf.named_materials.iter().find(|(_, h)| h.id() == handle.id())?.0.to_string())
    };
    let mut painted_triangles: Vec<painted::Triangle> = Vec::new();
    let mut leaf_triangles: Vec<painted::Triangle> = Vec::new();
    let leaf_material = manifest.foliage.as_ref().map(|foliage| foliage.material.as_str());

    // Walk from scene roots so bounds are in scene space, not mesh-local space.
    let children: BTreeSet<_> = gltf
        .nodes
        .iter()
        .filter_map(|h| nodes.get(h))
        .flat_map(|n| n.children.iter().map(Handle::id))
        .collect();
    let mut stack: Vec<(Handle<GltfNode>, Mat4)> = gltf
        .nodes
        .iter()
        .filter(|h| !children.contains(&h.id()))
        .map(|h| (h.clone(), Mat4::IDENTITY))
        .collect();

    let mut triangles = 0;
    let mut volume = 0.0;
    // Every triangle that must be part of a closed surface, to find the pieces among them.
    let mut closed: Vec<[Vec3; 3]> = Vec::new();
    let mut against_winding = 0;
    // (position, normal) of every vertex, to find positions lit as a hard edge.
    let mut lit: Vec<(Vec3, Vec3)> = Vec::new();
    let (mut min, mut max) = (Vec3::MAX, Vec3::MIN);
    while let Some((handle, parent)) = stack.pop() {
        let Some(node) = nodes.get(&handle) else {
            fail("a node handle did not resolve".into());
            continue;
        };
        let world_from_node = parent * node.transform.to_matrix();
        stack.extend(node.children.iter().map(|c| (c.clone(), world_from_node)));

        let Some(gltf_mesh) = node.mesh.as_ref().and_then(|h| gltf_meshes.get(h)) else {
            continue;
        };
        for primitive in &gltf_mesh.primitives {
            let label = format!("{}/primitive{}", gltf_mesh.name, primitive.index);
            let Some(mesh) = meshes.get(&primitive.mesh) else {
                fail(format!("{label}: mesh data not retained"));
                continue;
            };
            if mesh.primitive_topology() != PrimitiveTopology::TriangleList {
                fail(format!("{label}: topology is {:?}", mesh.primitive_topology()));
                continue;
            }
            let present: BTreeSet<&str> = mesh.attributes().map(|(a, _)| gltf_semantic(a.name)).collect();
            for wanted in &manifest.attributes {
                if !present.contains(wanted.as_str()) {
                    fail(format!("{label}: attribute {wanted} missing; has {present:?}"));
                }
            }
            let Some(VertexAttributeValues::Float32x3(positions)) = mesh.attribute(Mesh::ATTRIBUTE_POSITION) else {
                fail(format!("{label}: no float3 positions"));
                continue;
            };
            let positions: Vec<Vec3> = positions
                .iter()
                .map(|p| world_from_node.transform_point3(Vec3::from(*p)))
                .collect();
            for p in &positions {
                min = min.min(*p);
                max = max.max(*p);
            }
            let normal_matrix = Mat3::from_mat4(world_from_node).inverse().transpose();
            let normals: Option<Vec<Vec3>> = match mesh.attribute(Mesh::ATTRIBUTE_NORMAL) {
                Some(VertexAttributeValues::Float32x3(n)) => {
                    Some(n.iter().map(|n| normal_matrix * Vec3::from(*n)).collect())
                }
                _ => None,
            };
            if let Some(normals) = &normals {
                lit.extend(positions.iter().zip(normals).map(|(p, n)| (*p, n.normalize_or_zero())));
            }
            let indices: Vec<usize> = match mesh.indices() {
                Some(indices) => indices.iter().collect(),
                None => (0..positions.len()).collect(),
            };
            let uvs: Option<Vec<Vec2>> = match mesh.attribute(Mesh::ATTRIBUTE_UV_0) {
                Some(VertexAttributeValues::Float32x2(uvs)) => Some(uvs.iter().map(|uv| Vec2::from(*uv)).collect()),
                _ => None,
            };
            let material = name_of(&primitive.material);
            let colour = material.as_ref().and_then(|name| manifest.materials.get(name).copied());
            let is_leaf = material.is_some() && material.as_deref() == leaf_material;
            let is_open = material.as_ref().is_some_and(|name| manifest.open_materials.contains(name));
            for triangle in indices.chunks_exact(3) {
                let [a, b, c] = [triangle[0], triangle[1], triangle[2]].map(|i| positions[i]);
                let loaded = painted::Triangle {
                    positions: [a, b, c],
                    uvs: uvs.as_ref().map(|uvs| [triangle[0], triangle[1], triangle[2]].map(|i| uvs[i])),
                    colour,
                };
                if is_leaf {
                    leaf_triangles.push(loaded);
                } else {
                    painted_triangles.push(loaded);
                }
                if !is_open {
                    volume += a.dot(b.cross(c)) / 6.0;
                    closed.push([a, b, c]);
                }
                // The side a triangle's winding makes its front must be the
                // side its vertex normals point to, or it lights wrongly.
                let front = (b - a).cross(c - a);
                if let Some(normals) = &normals
                    && triangle.iter().any(|&i| normals[i].dot(front) <= 0.0)
                {
                    against_winding += 1;
                }
            }
            triangles += indices.len() / 3;
        }
    }

    if against_winding > 0 {
        fail(format!("{against_winding} triangles have vertex normals facing against their winding"));
    }
    if manifest.soft_edges {
        // Two vertices at one place with different normals are a hard edge.
        // The edge where the asset meets the ground is allowed to be one.
        let tolerance = manifest.bounds_tolerance;
        let floor = manifest.bounds.min[1] + tolerance;
        let above: Vec<&(Vec3, Vec3)> = lit.iter().filter(|(p, _)| p.y > floor).collect();
        let hard = above
            .iter()
            .enumerate()
            .filter(|(i, (p, n))| {
                above[..*i].iter().any(|(q, m)| p.abs_diff_eq(*q, tolerance) && n.dot(*m) < SAME_NORMAL_COS)
            })
            .count();
        if lit.is_empty() || hard > 0 {
            fail(format!(
                "soft_edges: {hard} of {} vertices above the ground share a position with a differently lit vertex",
                above.len()
            ));
        }
    }
    if manifest.watertight && volume <= 0.0 {
        fail(format!("signed volume {volume} is not positive: faces are inside out or the mesh is open"));
    }
    if manifest.watertight && manifest.overlap {
        // One small piece inside out leaves the volume of the whole positive.
        let (piece, count) = pieces::split(&closed);
        let inside_out: Vec<f32> = pieces::volumes(&closed, &piece, count).into_iter().filter(|v| *v <= 0.0).collect();
        if !inside_out.is_empty() {
            fail(format!(
                "pieces.outward: {} of {count} pieces are inside out or open: signed volumes {inside_out:?}",
                inside_out.len()
            ));
        }
    }

    if triangles != manifest.triangles {
        fail(format!("triangles {triangles} != manifest {}", manifest.triangles));
    }
    if triangles > 0 {
        let tolerance = manifest.bounds_tolerance;
        let (want_min, want_max) = (Vec3::from(manifest.bounds.min), Vec3::from(manifest.bounds.max));
        if !min.abs_diff_eq(want_min, tolerance) || !max.abs_diff_eq(want_max, tolerance) {
            fail(format!(
                "bounds {min}..{max} != manifest {want_min}..{want_max} (tolerance {tolerance})"
            ));
        }
        report.bounds = Some(Bounds { min: min.into(), max: max.into() });
    }

    if let Some(want) = &manifest.painted
        && let [texture] = textures.as_slice()
    {
        match images.get(texture) {
            Some(image) => {
                report.painted = Some(painted::check(
                    want,
                    &painted_triangles,
                    manifest.overlap,
                    manifest.foliage.is_some(),
                    image,
                    manifest.bounds.min[1],
                    manifest.bounds.max[1],
                    manifest.bounds_tolerance,
                    &mut fail,
                ));
            }
            None => fail("painted.present: the base colour texture did not load".into()),
        }
    }

    // Grain and close-range texels (ADR 12), on the same painted triangles and texture.
    if let Some(want) = grain
        && let [texture] = textures.as_slice()
        && let Some(image) = images.get(texture)
    {
        report.grain = grain::check(want, &painted_triangles, image, manifest.bounds.min[1], manifest.bounds_tolerance, &mut fail);
    }

    if let Some(want) = &manifest.foliage {
        let material = gltf.named_materials.get(want.material.as_str()).and_then(|h| materials.get(h));
        match (material, textures.as_slice().first().and_then(|texture| images.get(texture))) {
            (Some(material), Some(image)) => {
                let two_sided = material.double_sided && material.cull_mode.is_none();
                report.foliage = Some(foliage::check(want, manifest.materials.get(&want.material), &leaf_triangles, image, two_sided, &mut fail));
            }
            _ => fail(format!("foliage.present: no material '{}' with a texture to take leaf colours from", want.material)),
        }
    }

    report.failures.extend(failures);
    report.nodes = node_names.into_iter().collect();
    report.mesh_count = gltf.meshes.len();
    report.material_count = gltf.materials.len();
    report.triangles = triangles;
}

/// Bevy's attribute names mapped back to the glTF semantics the manifest uses.
fn gltf_semantic(bevy_name: &str) -> &str {
    match bevy_name {
        "Vertex_Position" => "POSITION",
        "Vertex_Normal" => "NORMAL",
        "Vertex_Tangent" => "TANGENT",
        "Vertex_Uv" => "TEXCOORD_0",
        "Vertex_Uv_1" => "TEXCOORD_1",
        "Vertex_Color" => "COLOR_0",
        "Vertex_JointIndex" => "JOINTS_0",
        "Vertex_JointWeight" => "WEIGHTS_0",
        other => other,
    }
}
