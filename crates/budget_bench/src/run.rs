//! Draws scenes one after another in one window, times each one's frames and writes each result
//! as one line of JSON.

use std::{collections::BTreeMap, fs::OpenOptions, io::Write, path::PathBuf, time::Instant};

use bevy::{
    camera::primitives::Aabb,
    diagnostic::DiagnosticsStore,
    light::{CascadeShadowConfigBuilder, DirectionalLightShadowMap},
    log::{Level, LogPlugin},
    prelude::*,
    render::{diagnostic::RenderDiagnosticsPlugin, renderer::RenderAdapterInfo},
    window::{MonitorSelection, PresentMode, PrimaryWindow, WindowMode, WindowResolution},
    winit::WinitSettings,
};
use serde_json::{Value, json};

use crate::{
    case::Case,
    scene::{self, Map},
};

/// Width and height the window asks for, in physical pixels.
pub const RESOLUTION: (u32, u32) = (1920, 1080);
/// Between scenes nothing is drawn for this long and this many frames, so the last scene is
/// gone from the renderer before the next is built.
const SETTLE_SECONDS: f64 = 0.3;
const SETTLE_FRAMES: u32 = 30;
/// The first frames of a scene are thrown away whatever the time, so slow scenes warm up too.
const WARM_UP_FRAMES: u32 = 40;
/// Frames are never recorded for longer than this.
const SAMPLE_MAX_SECONDS: f64 = 20.0;
/// Bytes of one vertex: position 12, normal 12, UV 8, tangent 16. An index is 4 bytes.
const VERTEX_BYTES: u64 = 48;

/// How long a scene is drawn before and while its frames are recorded.
struct Timing {
    /// Frames before this many seconds have passed are thrown away.
    warm_up: f64,
    /// Frames are then recorded for this many seconds, ...
    sample: f64,
    /// ... or until this many are recorded if that takes longer.
    min_frames: usize,
}

impl Timing {
    const FULL: Self = Self { warm_up: 1.2, sample: 2.0, min_frames: 200 };
    /// For the memory pass, where only the video memory reading matters.
    const QUICK: Self = Self { warm_up: 1.0, sample: 2.0, min_frames: 20 };
}
/// Shadow settings, as Bevy's defaults, written out so the result records them.
pub const SHADOW_MAP_SIZE: usize = 2048;
pub const SHADOW_DISTANCE: f32 = 150.0;

/// One window draws every scene in turn. Each scene goes through these steps.
enum Phase {
    /// Nothing is drawn, until the last scene's memory is released.
    Settle { since: Instant, frames: u32 },
    /// The scene is drawn and its frames thrown away.
    WarmUp { since: Instant, frames: u32 },
    /// The scene's frames are recorded.
    Sample { since: Instant },
}

#[derive(Resource)]
struct Bench {
    cases: Vec<Case>,
    /// Index into `cases` of the scene being measured, or about to be.
    current: usize,
    phase: Phase,
    result_path: PathBuf,
    frame_ms: Vec<f64>,
    /// Sum and number of readings of each render diagnostic while sampling.
    render: BTreeMap<String, (f64, u32)>,
    scene: SceneFacts,
    timing: Timing,
}

/// What was actually built, as opposed to what was asked for.
#[derive(Default)]
struct SceneFacts {
    triangles: u64,
    vertices: u64,
    meshes: u32,
    materials: u32,
    textures: u32,
    texture_bytes: u64,
    /// Bytes of the different meshes: each is stored once however often it is drawn.
    mesh_bytes: u64,
    farthest_m: f32,
    build_seconds: f64,
}

/// Everything that belongs to one scene and is removed before the next.
#[derive(Component)]
struct InScene;

/// Draws each of `cases` in one window and appends one line of JSON per scene to `result_path`.
pub fn run(cases: Vec<Case>, result_path: PathBuf, windowed: bool, quick: bool) -> AppExit {
    let mut window = Window {
        title: "budget_bench".to_string(),
        resolution: WindowResolution::new(RESOLUTION.0, RESOLUTION.1).with_scale_factor_override(1.0),
        // No waiting for the monitor: a frame takes as long as it takes to make.
        present_mode: PresentMode::AutoNoVsync,
        ..default()
    };
    if !windowed {
        // A tiling compositor would resize an ordinary window; full screen on a 1920x1080
        // monitor is the resolution being measured.
        window.mode = WindowMode::BorderlessFullscreen(MonitorSelection::Primary);
    }
    App::new()
        .add_plugins(
            DefaultPlugins
                .set(WindowPlugin { primary_window: Some(window), ..default() })
                .set(LogPlugin { level: Level::WARN, ..default() }),
        )
        .add_plugins(RenderDiagnosticsPlugin)
        // Keep drawing at full speed when the window does not have keyboard focus.
        .insert_resource(WinitSettings::continuous())
        .insert_resource(ClearColor(Color::linear_rgb(0.35, 0.45, 0.6)))
        .insert_resource(GlobalAmbientLight { brightness: 600.0, ..default() })
        .insert_resource(DirectionalLightShadowMap { size: SHADOW_MAP_SIZE })
        .insert_resource(Bench {
            cases,
            current: 0,
            phase: Phase::Settle { since: Instant::now(), frames: 0 },
            result_path,
            frame_ms: Vec::new(),
            render: BTreeMap::new(),
            scene: SceneFacts::default(),
            timing: if quick { Timing::QUICK } else { Timing::FULL },
        })
        .add_systems(Update, step)
        .run()
}

fn build_scene(
    case: &Case,
    commands: &mut Commands,
    meshes: &mut Assets<Mesh>,
    images: &mut Assets<Image>,
    materials: &mut Assets<StandardMaterial>,
) -> SceneFacts {
    let began = Instant::now();
    let aspect = RESOLUTION.0 as f32 / RESOLUTION.1 as f32;
    let eye = Vec3::new(0.0, scene::EYE_HEIGHT, 0.0);

    commands.spawn((
        InScene,
        Camera3d::default(),
        Projection::Perspective(PerspectiveProjection { fov: scene::FOV_DEGREES.to_radians(), ..default() }),
        Transform::from_translation(eye).with_rotation(Quat::from_rotation_x(-scene::PITCH_DOWN_DEGREES.to_radians())),
        match case.msaa {
            1 => Msaa::Off,
            4 => Msaa::Sample4,
            other => panic!("msaa must be 1 or 4, not {other}"),
        },
    ));
    commands.spawn((
        InScene,
        DirectionalLight { illuminance: 8000.0, shadow_maps_enabled: case.shadows, ..default() },
        CascadeShadowConfigBuilder {
            num_cascades: case.cascades as usize,
            maximum_distance: SHADOW_DISTANCE,
            ..default()
        }
        .build(),
        Transform::default().looking_to(Vec3::new(0.4, -1.0, -0.6), Vec3::Y),
    ));
    commands.spawn((
        InScene,
        Mesh3d(meshes.add(Plane3d::default().mesh().size(600.0, 600.0))),
        MeshMaterial3d(materials.add(StandardMaterial {
            base_color: Color::linear_rgb(0.2, 0.22, 0.18),
            perceptual_roughness: 1.0,
            ..default()
        })),
    ));

    let placed = scene::layout(case.count, aspect);
    let unique = case.unique_assets() as usize;

    // One material with its own three textures for each different asset.
    let maps = [Map::BaseColour, Map::Normal, Map::MetallicRoughness];
    let made = scene::in_parallel(unique * 3, |i| scene::texture(case.tex, maps[i % 3], case.mips, case.format, i as u64 + 1));
    let mut handles = made.into_iter().map(|image| images.add(image));
    let asset_materials: Vec<Handle<StandardMaterial>> = (0..unique)
        .map(|_| {
            materials.add(StandardMaterial {
                base_color_texture: handles.next(),
                normal_map_texture: handles.next(),
                metallic_roughness_texture: handles.next(),
                metallic: 1.0,
                perceptual_roughness: 1.0,
                ..default()
            })
        })
        .collect();

    // One mesh for each different asset, and one more for each level of detail of it in use.
    let level_of = |at: Vec3| if case.lod { scene::lod_level(at.distance(eye)) } else { 0 };
    let mut wanted: Vec<(usize, u32)> = placed.iter().enumerate().map(|(i, (at, _))| (i % unique, level_of(*at))).collect();
    wanted.sort_unstable();
    wanted.dedup();
    let made = scene::in_parallel(wanted.len(), |i| {
        let (asset, level) = wanted[i];
        scene::rock_mesh(case.tris >> (2 * level), asset as u64 * 8 + level as u64)
    });
    let asset_meshes: BTreeMap<(usize, u32), (Handle<Mesh>, u32, u32)> =
        wanted.iter().copied().zip(made).map(|(key, (mesh, triangles, vertices))| (key, (meshes.add(mesh), triangles, vertices))).collect();

    let mut facts = SceneFacts {
        meshes: asset_meshes.len() as u32,
        materials: unique as u32,
        textures: unique as u32 * 3,
        texture_bytes: unique as u64 * 3 * scene::texture_bytes(case.tex, case.mips, case.format),
        mesh_bytes: asset_meshes.values().map(|(_, triangles, vertices)| *vertices as u64 * VERTEX_BYTES + *triangles as u64 * 12).sum(),
        ..default()
    };
    for (i, (at, turn)) in placed.iter().enumerate() {
        let (mesh, triangles, vertices) = &asset_meshes[&(i % unique, level_of(*at))];
        facts.triangles += *triangles as u64;
        facts.vertices += *vertices as u64;
        facts.farthest_m = facts.farthest_m.max(at.distance(eye));
        commands.spawn((
            InScene,
            Mesh3d(mesh.clone()),
            MeshMaterial3d(asset_materials[i % unique].clone()),
            Transform::from_translation(*at).with_rotation(Quat::from_rotation_y(*turn)),
            // Given here because the mesh data leaves the main world once it is on the GPU.
            Aabb::from_min_max(Vec3::splat(-scene::ASSET_SIZE / 2.0), Vec3::splat(scene::ASSET_SIZE / 2.0)),
        ));
    }
    facts.build_seconds = began.elapsed().as_secs_f64();
    facts
}

#[allow(clippy::too_many_arguments)]
fn step(
    mut commands: Commands,
    mut bench: ResMut<Bench>,
    time: Res<Time<Real>>,
    diagnostics: Res<DiagnosticsStore>,
    window: Single<&Window, With<PrimaryWindow>>,
    adapter: Res<RenderAdapterInfo>,
    in_scene: Query<Entity, With<InScene>>,
    mut meshes: ResMut<Assets<Mesh>>,
    mut images: ResMut<Assets<Image>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    mut exit: MessageWriter<AppExit>,
) {
    let bench = &mut *bench;
    let since = match &mut bench.phase {
        Phase::Settle { since, frames } => {
            *frames += 1;
            if *frames > SETTLE_FRAMES && since.elapsed().as_secs_f64() > SETTLE_SECONDS {
                if bench.current == bench.cases.len() {
                    exit.write(AppExit::Success);
                    return;
                }
                bench.scene = build_scene(&bench.cases[bench.current], &mut commands, &mut meshes, &mut images, &mut materials);
                bench.phase = Phase::WarmUp { since: Instant::now(), frames: 0 };
            }
            return;
        }
        Phase::WarmUp { since, frames } => {
            *frames += 1;
            if *frames > WARM_UP_FRAMES && since.elapsed().as_secs_f64() > bench.timing.warm_up {
                bench.frame_ms.clear();
                bench.render.clear();
                bench.phase = Phase::Sample { since: Instant::now() };
            }
            return;
        }
        Phase::Sample { since } => *since,
    };
    bench.frame_ms.push(time.delta_secs_f64() * 1000.0);
    // Render diagnostics arrive a few frames late and cost a little to read, so read some.
    if bench.frame_ms.len().is_multiple_of(8) {
        for diagnostic in diagnostics.iter() {
            let path = diagnostic.path().as_str();
            if let (true, Some(value)) = (path.starts_with("render/"), diagnostic.value()) {
                let entry = bench.render.entry(path.to_string()).or_default();
                entry.0 += value;
                entry.1 += 1;
            }
        }
    }
    let sampled = since.elapsed().as_secs_f64();
    let enough = sampled >= bench.timing.sample && bench.frame_ms.len() >= bench.timing.min_frames;
    if !enough && sampled < SAMPLE_MAX_SECONDS {
        return;
    }

    // Read while the scene is still loaded and drawing.
    let (vram_mib, gpu_percent) = crate::nvidia_now();
    let frames = &bench.frame_ms;
    let half = frames.len() / 2;
    let (first, second) = (stats(&frames[..half]), stats(&frames[half..]));
    let all = stats(frames);
    let render: BTreeMap<&str, f64> = bench.render.iter().map(|(path, (sum, n))| (path.as_str(), sum / *n as f64)).collect();
    // Time the GPU spent inside the render passes Bevy times: the top-level spans only, so
    // nothing counts twice. Bevy 0.19.1 does not time its shadow passes, so this is less than
    // the GPU's whole frame when shadows are on.
    let gpu_pass_ms: f64 =
        render.iter().filter(|(path, _)| path.ends_with("/elapsed_gpu") && path.split('/').count() == 3).map(|(_, ms)| ms).sum();
    let opaque = |field: &str| render.get(format!("render/main_opaque_pass_3d/{field}").as_str()).copied();
    let case = &bench.cases[bench.current];
    let result = json!({
        "name": case.name,
        "case": case.to_arg(),
        "count": case.count, "tris_per_asset": case.tris, "texture_size": case.tex,
        "unique_assets": case.unique_assets(), "shadows": case.shadows, "mips": case.mips,
        "format": format!("{:?}", case.format).to_lowercase(), "msaa": case.msaa, "lod": case.lod,
        "cascades": case.cascades,
        "triangles_total": bench.scene.triangles, "vertices_total": bench.scene.vertices,
        "meshes": bench.scene.meshes, "materials": bench.scene.materials, "textures": bench.scene.textures,
        "texture_mib_computed": bench.scene.texture_bytes as f64 / 1048576.0,
        "mesh_mib_computed": bench.scene.mesh_bytes as f64 / 1048576.0,
        "farthest_asset_m": bench.scene.farthest_m,
        "window_width": window.physical_width(), "window_height": window.physical_height(),
        "frames": frames.len(), "sample_seconds": sampled, "build_seconds": bench.scene.build_seconds,
        "frame_ms_median": all.median, "frame_ms_mean": all.mean, "frame_ms_p95": all.p95,
        "frame_ms_p99": all.p99, "frame_ms_min": all.min, "frame_ms_max": all.max,
        // How far the second half of the sample was from the first: a sample that is still
        // settling shows up here.
        "drift_percent": (second.median / first.median - 1.0) * 100.0,
        "gpu_pass_ms": gpu_pass_ms,
        "opaque_pass_gpu_ms": opaque("elapsed_gpu"),
        "opaque_triangles_drawn": opaque("clipper_primitives_out"),
        "opaque_fragments": opaque("fragment_shader_invocations"),
        "gpu_utilisation_percent": gpu_percent,
        "vram_used_mib": vram_mib, "vram_process_mib": crate::nvidia_process_mib(std::process::id()),
        "adapter": adapter.name, "backend": format!("{:?}", adapter.backend),
        "driver": format!("{} {}", adapter.driver, adapter.driver_info),
        "render_diagnostics": render,
    });
    let mut file = OpenOptions::new().create(true).append(true).open(&bench.result_path).expect("cannot open the result file");
    writeln!(file, "{result}").expect("cannot write the result");
    println!(
        "  {:>2}/{} {:<24} median {:>8.3} ms  p99 {:>8.3} ms  GPU {:>3.0}% busy",
        bench.current + 1,
        bench.cases.len(),
        case.name,
        all.median,
        all.p99,
        gpu_percent.unwrap_or(f64::NAN),
    );

    // Remove the scene. Its meshes, materials and textures go with the last handle to them.
    for entity in &in_scene {
        commands.entity(entity).despawn();
    }
    bench.current += 1;
    bench.phase = Phase::Settle { since: Instant::now(), frames: 0 };
}

struct Stats {
    median: f64,
    mean: f64,
    p95: f64,
    p99: f64,
    min: f64,
    max: f64,
}

fn stats(values: &[f64]) -> Stats {
    let mut sorted = values.to_vec();
    sorted.sort_by(f64::total_cmp);
    let at = |q: f64| sorted[((sorted.len() - 1) as f64 * q).round() as usize];
    Stats {
        median: at(0.5),
        mean: sorted.iter().sum::<f64>() / sorted.len() as f64,
        p95: at(0.95),
        p99: at(0.99),
        min: sorted[0],
        max: sorted[sorted.len() - 1],
    }
}

/// The measurement settings every result shares, for the record of a run.
pub fn settings() -> Value {
    json!({
        "resolution": format!("{}x{}", RESOLUTION.0, RESOLUTION.1),
        "present_mode": "AutoNoVsync",
        "settle_between_scenes": format!("{SETTLE_SECONDS} s and {SETTLE_FRAMES} frames with nothing drawn"),
        "warm_up": format!("{} s and {WARM_UP_FRAMES} frames, discarded", Timing::FULL.warm_up),
        "sample": format!("{} s and at least {} frames, at most {SAMPLE_MAX_SECONDS} s", Timing::FULL.sample, Timing::FULL.min_frames),
        "shadow_map_size": SHADOW_MAP_SIZE, "shadow_distance_m": SHADOW_DISTANCE,
        "eye_height_m": scene::EYE_HEIGHT, "fov_vertical_degrees": scene::FOV_DEGREES,
        "pitch_down_degrees": scene::PITCH_DOWN_DEGREES, "nearest_surface_m": scene::NEAREST,
        "asset_size_m": scene::ASSET_SIZE, "asset_spacing_m": scene::SPACING,
        "lod_distances_m": scene::LOD_DISTANCES,
        "texture_filtering": "trilinear, no anisotropic filtering",
        "depth_prepass": false,
    })
}
