//! Loads a `.glb`, sets its morph weights (or seeks an animation clip) and writes PNG frames,
//! with no window. A throwaway probe for `learn/research/fur-animation-trial.md`.
//!
//! morph_probe <model.glb> --out <folder> [--frames "0;0.5;1"] [--clip N --times "0,0.5,1"]
//!             [--views three_quarter,side] [--distance 3.4]
//!
//! `--frames`: one picture per `;`-separated entry; an entry is a comma list of weights given
//! to morph targets 0, 1, ... of every node that has morph weights (targets not named get 0).
//! `--clip N --times`: instead, play animation N of the file, paused, and seek to each time.
//! The model is shown as the file places it (no scaling), on the viewer's ground and light.

use std::{
    path::PathBuf,
    sync::{Arc, Mutex},
    time::Duration,
};

use asset_view::scene::{self, Model};
use bevy::{
    animation::{AnimationPlayer, graph::{AnimationGraph, AnimationGraphHandle, AnimationNodeIndex}},
    app::ScheduleRunnerPlugin,
    camera::RenderTarget,
    gltf::Gltf,
    mesh::{morph::{MeshMorphWeights, MorphWeights}, skinning::SkinnedMesh},
    prelude::*,
    render::{
        RenderPlugin,
        render_resource::TextureFormat,
        renderer::RenderAdapterInfo,
        view::screenshot::{Screenshot, ScreenshotCaptured},
    },
    window::ExitCondition,
    winit::WinitPlugin,
    world_serialization::WorldAsset,
};

const SIZE: (u32, u32) = (1280, 960);
const SETTLE: u32 = 8;

#[derive(Resource)]
struct Job {
    file_name: String,
    out: PathBuf,
    frames: Vec<Vec<f32>>,
    clip: Option<usize>,
    times: Vec<f32>,
    views: Vec<String>,
    distance: f32,
}

#[derive(Resource)]
struct Loading(Handle<WorldAsset>, Handle<Gltf>);
#[derive(Resource)]
struct Target(Handle<Image>);
#[derive(Resource, Clone, Default)]
struct Taken(Arc<Mutex<Option<Image>>>);
#[derive(Resource)]
struct Playing(AnimationNodeIndex);

#[derive(Resource, Default)]
enum Step {
    #[default]
    Loading,
    Loaded(u32),
    Settling { frame: usize, view: usize, waited: u32 },
    Taking { frame: usize, view: usize },
    Finished,
}

fn main() -> AppExit {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let (mut glb, mut out, mut frames, mut clip, mut times) = (None, None, vec![vec![0.0]], None, vec![]);
    let (mut views, mut distance) = (vec!["three_quarter".to_string(), "side".to_string()], 3.4f32);
    let mut rest = args.iter();
    while let Some(arg) = rest.next() {
        match arg.as_str() {
            "--out" => out = rest.next().map(PathBuf::from),
            "--frames" => {
                frames = rest.next().unwrap().split(';').map(|f| f.split(',').map(|w| w.trim().parse().unwrap()).collect()).collect()
            }
            "--clip" => clip = Some(rest.next().unwrap().parse().unwrap()),
            "--times" => times = rest.next().unwrap().split(',').map(|t| t.trim().parse().unwrap()).collect(),
            "--views" => views = rest.next().unwrap().split(',').map(str::to_string).collect(),
            "--distance" => distance = rest.next().unwrap().parse().unwrap(),
            _ => glb = Some(std::fs::canonicalize(arg).expect("the model file cannot be opened")),
        }
    }
    let (glb, out) = (glb.expect("no model file"), out.expect("--out was not given"));
    std::fs::create_dir_all(&out).unwrap();

    let mut app = App::new();
    app.add_plugins(
        scene::plugins(&glb, false)
            .set(WindowPlugin { primary_window: None, exit_condition: ExitCondition::DontExit, ..default() })
            .disable::<WinitPlugin>()
            .set(RenderPlugin { synchronous_pipeline_compilation: true, ..default() }),
    )
    .add_plugins(ScheduleRunnerPlugin::run_loop(Duration::ZERO));
    scene::light_the_world(&mut app);
    app.insert_resource(Job {
        file_name: glb.file_name().unwrap().to_string_lossy().into_owned(),
        out,
        frames,
        clip,
        times,
        views,
        distance,
    })
    .init_resource::<Step>()
    .init_resource::<Taken>()
    .add_systems(Startup, setup)
    .add_systems(Update, step)
    .run()
}

fn setup(
    mut commands: Commands,
    job: Res<Job>,
    asset_server: Res<AssetServer>,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    mut images: ResMut<Assets<Image>>,
) {
    let scene = scene::spawn_scene(&mut commands, &asset_server, &mut meshes, &mut materials, &job.file_name);
    let gltf: Handle<Gltf> = asset_server.load(job.file_name.clone());
    commands.insert_resource(Loading(scene, gltf));
    let target = images.add(Image::new_target_texture(SIZE.0, SIZE.1, TextureFormat::Rgba8UnormSrgb, None));
    commands.spawn((Camera3d::default(), RenderTarget::Image(target.clone().into())));
    commands.insert_resource(Target(target));
}

fn eye(view: &str, distance: f32) -> Vec3 {
    let direction = match view {
        "side" => Vec3::new(1.0, 0.12, 0.0),
        "front" => Vec3::new(0.0, 0.12, 1.0),
        "back" => Vec3::new(0.0, 0.12, -1.0),
        "top" => Vec3::new(0.0, 1.0, 0.02),
        "back_quarter" => Vec3::new(-0.7, 0.5, -0.8),
        _ => Vec3::new(0.7, 0.5, 0.8),
    };
    Vec3::new(0.0, 0.5, 0.0) + direction.normalize() * distance
}

#[expect(clippy::too_many_arguments, clippy::type_complexity)]
fn step(
    mut commands: Commands,
    job: Res<Job>,
    loading: Res<Loading>,
    target: Res<Target>,
    taken: Res<Taken>,
    playing: Option<Res<Playing>>,
    adapter: Res<RenderAdapterInfo>,
    asset_server: Res<AssetServer>,
    (gltfs, mesh_assets, mut graphs): (Res<Assets<Gltf>>, Res<Assets<Mesh>>, ResMut<Assets<AnimationGraph>>),
    mut step: ResMut<Step>,
    mut exit: MessageWriter<AppExit>,
    model: Single<Entity, With<Model>>,
    (children, mesh_entities): (Query<&Children>, Query<(&Mesh3d, &GlobalTransform)>),
    (mut morphs, mesh_morphs, skinned): (Query<&mut MorphWeights>, Query<&MeshMorphWeights>, Query<&SkinnedMesh>),
    mut players: Query<(Entity, &mut AnimationPlayer)>,
    mut camera: Single<&mut Transform, With<Camera3d>>,
) {
    let count = if job.clip.is_some() { job.times.len() } else { job.frames.len() };
    match *step {
        Step::Loading | Step::Loaded(_) => {
            if !asset_server.is_loaded_with_dependencies(&loading.0) || !asset_server.is_loaded_with_dependencies(&loading.1) {
                return;
            }
            let found = scene::vertex_box(*model, &children, &mesh_entities, &mesh_assets);
            let waited = if let Step::Loaded(n) = *step { n } else { 0 };
            if found.is_none() || waited < 3 {
                if waited > 600 {
                    eprintln!("morph_probe: the model holds no mesh");
                    *step = Step::Finished;
                    exit.write(AppExit::error());
                    return;
                }
                *step = Step::Loaded(waited + 1);
                return;
            }
            let gltf = gltfs.get(&loading.1).unwrap();
            let (min, max, meshes) = found.unwrap();
            let targets: Vec<usize> = morphs.iter().map(|m| m.weights().len()).collect();
            eprintln!(
                "{}",
                serde_json::json!({
                    "file": job.file_name, "bevy": "0.19.1", "graphics_card": adapter.name, "backend": adapter.backend.to_string(),
                    "mesh_entities": meshes, "box_min": [min.x, min.y, min.z], "box_max": [max.x, max.y, max.z],
                    "nodes_with_morph_weights": targets.len(), "targets_per_node": targets,
                    "mesh_entities_with_morph_weights": mesh_morphs.iter().count(),
                    "skinned_mesh_entities": skinned.iter().count(),
                    "joints_per_skin": skinned.iter().map(|s| s.joints.len()).collect::<Vec<_>>(),
                    "animation_clips": gltf.animations.len(),
                    "clip_names": gltf.named_animations.keys().collect::<Vec<_>>(),
                    "animation_players": players.iter().count(),
                })
            );
            if let Some(clip) = job.clip {
                let Some(handle) = gltf.animations.get(clip) else {
                    eprintln!("morph_probe: the file has no animation {clip}");
                    *step = Step::Finished;
                    exit.write(AppExit::error());
                    return;
                };
                let (graph, index) = AnimationGraph::from_clip(handle.clone());
                let graph = graphs.add(graph);
                for (entity, mut player) in &mut players {
                    commands.entity(entity).insert(AnimationGraphHandle(graph.clone()));
                    player.play(index).pause();
                }
                commands.insert_resource(Playing(index));
            }
            *step = Step::Settling { frame: 0, view: 0, waited: 0 };
        }
        Step::Settling { frame, view, waited } => {
            if waited == 0 {
                **camera = Transform::from_translation(eye(&job.views[view], job.distance)).looking_at(Vec3::new(0.0, 0.5, 0.0), Vec3::Y);
            }
            // Set every frame while settling: a clip would otherwise write its own weights back.
            if let Some(playing) = &playing {
                for (_, mut player) in &mut players {
                    if let Some(active) = player.animation_mut(playing.0) {
                        active.seek_to(job.times[frame]);
                    }
                }
            }
            // With a clip, the first entry of --frames still sets the morph weights, so a file
            // with a skin and morph targets can be shown bent and spiked at once.
            let weights = &job.frames[if playing.is_some() { 0 } else { frame }];
            {
                for mut morph in &mut morphs {
                    for (i, weight) in morph.weights_mut().iter_mut().enumerate() {
                        *weight = weights.get(i).copied().unwrap_or(0.0);
                    }
                }
            }
            if waited < SETTLE {
                *step = Step::Settling { frame, view, waited: waited + 1 };
                return;
            }
            let taken = taken.clone();
            commands.spawn(Screenshot::image(target.0.clone())).observe(move |captured: On<ScreenshotCaptured>| {
                *taken.0.lock().unwrap() = Some(captured.image.clone());
            });
            *step = Step::Taking { frame, view };
        }
        Step::Taking { frame, view } => {
            let Some(image) = taken.0.lock().unwrap().take() else { return };
            let path = job.out.join(format!("{}_{:02}.png", job.views[view], frame));
            image.try_into_dynamic().unwrap().to_rgb8().save_with_format(&path, image::ImageFormat::Png).unwrap();
            println!("{}", path.display());
            *step = if view + 1 < job.views.len() {
                Step::Settling { frame, view: view + 1, waited: 0 }
            } else if frame + 1 < count {
                Step::Settling { frame: frame + 1, view: 0, waited: 0 }
            } else {
                exit.write(AppExit::Success);
                Step::Finished
            };
        }
        Step::Finished => {}
    }
}
