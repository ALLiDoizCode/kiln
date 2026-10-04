//! Headless Bevy load test (gate L4).
//!
//! Loads one GLB through the real `bevy_gltf` loader with no window and no
//! renderer, then compares what Bevy sees against the asset's manifest.
//! Exit code is the only signal: 0 pass, 1 check failed, 2 usage or I/O error.
//!
//! Usage: asset_smoke <asset.glb> <manifest.json> [--report <out.json>]

use std::{
    collections::BTreeSet,
    path::{Path, PathBuf},
    process::ExitCode,
    time::{Duration, Instant},
};

use bevy::{
    app::TaskPoolPlugin,
    asset::{AssetPlugin, RecursiveDependencyLoadState, UnapprovedPathMode},
    gltf::{Gltf, GltfMaterial, GltfMesh, GltfNode, GltfPlugin},
    image::{CompressedImageFormatSupport, CompressedImageFormats},
    log::LogPlugin,
    mesh::{Mesh, MeshPlugin, PrimitiveTopology, VertexAttributeValues},
    prelude::*,
    world_serialization::WorldSerializationPlugin,
};
use serde::{Deserialize, Serialize};

const LOAD_TIMEOUT: Duration = Duration::from_secs(60);

/// Written by `tools/export.py` from the Blender scene. Bounds are in glTF
/// space (+Y up, metres), over every mesh in the file with node transforms
/// applied.
#[derive(Deserialize)]
struct Manifest {
    nodes: Vec<String>,
    mesh_count: usize,
    material_count: usize,
    triangles: usize,
    bounds: Bounds,
    bounds_tolerance: f32,
    /// glTF attribute semantics every primitive must carry, e.g. "NORMAL".
    attributes: Vec<String>,
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

    let manifest: Manifest = match std::fs::read_to_string(manifest_path)
        .map_err(|e| e.to_string())
        .and_then(|text| serde_json::from_str(&text).map_err(|e| e.to_string()))
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
        Ok(app) => measure(&app, &manifest, &mut report),
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

fn measure(app: &App, manifest: &Manifest, report: &mut Report) {
    let world = app.world();
    let gltf = world
        .resource::<Assets<Gltf>>()
        .get(&world.resource::<Loading>().0)
        .expect("loaded Gltf is in Assets");
    let nodes = world.resource::<Assets<GltfNode>>();
    let gltf_meshes = world.resource::<Assets<GltfMesh>>();
    let meshes = world.resource::<Assets<Mesh>>();
    let mut fail = |message: String| report.failures.push(message);

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
    if gltf.materials.len() != manifest.material_count {
        fail(format!(
            "material_count {} != manifest {}",
            gltf.materials.len(),
            manifest.material_count
        ));
    }
    let materials = world.resource::<Assets<GltfMaterial>>();
    for handle in &gltf.materials {
        if materials.get(handle).is_none() {
            fail("a material handle did not resolve".into());
        }
    }

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
            triangles += mesh.indices().map_or(mesh.count_vertices(), |i| i.len()) / 3;

            let present: BTreeSet<&str> = mesh.attributes().map(|(a, _)| gltf_semantic(a.name)).collect();
            for wanted in &manifest.attributes {
                if !present.contains(wanted.as_str()) {
                    fail(format!("{label}: attribute {wanted} missing; has {present:?}"));
                }
            }
            match mesh.attribute(Mesh::ATTRIBUTE_POSITION) {
                Some(VertexAttributeValues::Float32x3(positions)) => {
                    for p in positions {
                        let p = world_from_node.transform_point3(Vec3::from(*p));
                        min = min.min(p);
                        max = max.max(p);
                    }
                }
                _ => fail(format!("{label}: no float3 positions")),
            }
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
