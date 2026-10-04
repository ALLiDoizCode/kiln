//! Shows one asset under Bevy's renderer, beside a player-height figure.
//!
//! With `--screenshot` it renders one fixed view to a PNG with no window and
//! exits (the review gate uses this). Without it, it opens a window with a
//! slow turntable and reloads the asset whenever the GLB changes on disk.
//!
//! `--close` frames the asset alone from about first-person distance, with no figure.
//! `--back` takes the screenshot from the opposite side, the asset's back left.
//!
//! Usage: asset_view <asset.glb> <manifest.json> [--screenshot <out.png>] [--close] [--back]

use std::{
    path::{Path, PathBuf},
    time::Duration,
};

use bevy::{
    app::ScheduleRunnerPlugin,
    asset::{RecursiveDependencyLoadState, UnapprovedPathMode},
    camera::RenderTarget,
    prelude::*,
    render::{
        render_resource::{TextureFormat, TextureUsages},
        view::screenshot::{Screenshot, save_to_disk},
    },
    window::ExitCondition,
    winit::WinitPlugin,
    world_serialization::WorldAsset,
};
use serde::Deserialize;

const SIZE: u32 = 1024;
const PLAYER_HEIGHT: f32 = 1.8;
/// Frames to let shadows and shaders settle before capturing.
const SETTLE_FRAMES: u32 = 30;
const TIMEOUT_FRAMES: u32 = 3600;

#[derive(Deserialize)]
struct Manifest {
    bounds: Bounds,
}

#[derive(Deserialize)]
struct Bounds {
    min: [f32; 3],
    max: [f32; 3],
}

#[derive(Resource)]
struct View {
    scene: Handle<WorldAsset>,
    /// What the camera frames: the asset and the figure together.
    centre: Vec3,
    radius: f32,
    screenshot: Option<PathBuf>,
    /// Where the screenshot's camera stands, as a turn about the vertical from the front right.
    orbit: f32,
    target: Option<Handle<Image>>,
    settled: u32,
    frames: u32,
    requested: bool,
}

fn main() -> AppExit {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut positional = Vec::new();
    let mut screenshot = None;
    let mut close = false;
    let mut back = false;
    let mut iter = args.iter();
    while let Some(arg) = iter.next() {
        if arg == "--screenshot" {
            screenshot = iter.next().map(PathBuf::from);
        } else if arg == "--close" {
            close = true;
        } else if arg == "--back" {
            back = true;
        } else {
            positional.push(PathBuf::from(arg));
        }
    }
    if positional.len() != 2 {
        eprintln!(
            "usage: asset_view <asset.glb> <manifest.json> [--screenshot <out.png>] [--close] [--back]"
        );
        return AppExit::error();
    }
    let glb = positional[0].canonicalize().expect("asset file exists");
    let manifest: Manifest = serde_json::from_str(
        &std::fs::read_to_string(&positional[1]).expect("manifest is readable"),
    )
    .expect("manifest is valid JSON");

    let headless = screenshot.is_some();
    let assets = AssetPlugin {
        file_path: glb.parent().unwrap().to_string_lossy().into_owned(),
        unapproved_path_mode: UnapprovedPathMode::Deny,
        watch_for_changes_override: Some(!headless),
        ..default()
    };

    let mut app = App::new();
    if headless {
        app.add_plugins(
            DefaultPlugins
                .set(assets)
                .set(WindowPlugin {
                    primary_window: None,
                    exit_condition: ExitCondition::DontExit,
                    ..default()
                })
                .disable::<WinitPlugin>(),
        )
        .add_plugins(ScheduleRunnerPlugin::run_loop(Duration::from_secs_f64(
            1.0 / 60.0,
        )));
    } else {
        app.add_plugins(DefaultPlugins.set(assets).set(WindowPlugin {
            primary_window: Some(Window {
                title: format!("asset_view: {}", glb.file_name().unwrap().to_string_lossy()),
                ..default()
            }),
            ..default()
        }));
    }

    let (min, max) = (
        Vec3::from(manifest.bounds.min),
        Vec3::from(manifest.bounds.max),
    );
    // The figure stands on the ground to the asset's left, as in the Blender
    // scale view, and level with its front so the asset does not hide it.
    let figure = Vec3::new(min.x - 0.5, 0.0, max.z);
    let (framed_min, framed_max) = if close {
        (min, max)
    } else {
        (
            min.min(Vec3::new(figure.x - 0.2, 0.0, min.z)),
            max.max(Vec3::new(max.x, PLAYER_HEIGHT, figure.z + 0.2)),
        )
    };

    app.insert_resource(ClearColor(Color::linear_rgb(0.18, 0.19, 0.21)))
        .insert_resource(View {
            scene: Handle::default(),
            centre: (framed_min + framed_max) / 2.0,
            // Close up, the asset overfills the frame a little, as it would at arm's length.
            radius: (framed_max - framed_min).length() / 2.0 * if close { 0.8 } else { 1.0 },
            screenshot,
            orbit: if back { std::f32::consts::PI } else { 0.0 },
            target: None,
            settled: 0,
            frames: 0,
            requested: false,
        })
        .insert_resource(FigureAt(figure))
        .insert_resource(ShowFigure(!close))
        .insert_resource(AssetFile(
            glb.file_name().unwrap().to_string_lossy().into_owned(),
        ))
        .add_systems(Startup, setup);
    if headless {
        app.add_systems(Update, capture);
    } else {
        app.add_systems(Update, turntable);
    }
    app.run()
}

#[derive(Resource)]
struct FigureAt(Vec3);

#[derive(Resource)]
struct AssetFile(String);

#[derive(Resource)]
struct ShowFigure(bool);

fn setup(
    mut commands: Commands,
    mut view: ResMut<View>,
    figure_at: Res<FigureAt>,
    show_figure: Res<ShowFigure>,
    file: Res<AssetFile>,
    asset_server: Res<AssetServer>,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    mut images: ResMut<Assets<Image>>,
) {
    view.scene = asset_server.load(GltfAssetLabel::Scene(0).from_asset(file.0.clone()));
    commands.spawn(WorldAssetRoot(view.scene.clone()));

    // Ground, so the asset's contact with it and its cast shadow are visible.
    commands.spawn((
        Mesh3d(meshes.add(Plane3d::default().mesh().size(200.0, 200.0))),
        MeshMaterial3d(materials.add(StandardMaterial {
            base_color: Color::linear_rgb(0.12, 0.125, 0.135),
            perceptual_roughness: 1.0,
            ..default()
        })),
    ));
    let radius = 0.2;
    if show_figure.0 {
        commands.spawn((
            Mesh3d(meshes.add(Capsule3d::new(radius, PLAYER_HEIGHT - 2.0 * radius))),
            MeshMaterial3d(materials.add(StandardMaterial {
                base_color: Color::linear_rgb(0.25, 0.45, 0.75),
                perceptual_roughness: 0.9,
                ..default()
            })),
            Transform::from_translation(figure_at.0 + Vec3::Y * PLAYER_HEIGHT / 2.0),
        ));
    }

    // Same direction as the review renders' sun: from the asset's front-left, above.
    commands.spawn((
        DirectionalLight {
            illuminance: 8000.0,
            shadow_maps_enabled: true,
            ..default()
        },
        Transform::default().looking_to(Vec3::new(0.4, -1.0, -0.6), Vec3::Y),
    ));
    commands.insert_resource(GlobalAmbientLight {
        brightness: 300.0,
        ..default()
    });

    let camera = (Camera3d::default(), camera_transform(&view, view.orbit));
    if view.screenshot.is_some() {
        let mut image = Image::new_target_texture(SIZE, SIZE, TextureFormat::Rgba8UnormSrgb, None);
        image.texture_descriptor.usage |= TextureUsages::COPY_SRC;
        let target = images.add(image);
        view.target = Some(target.clone());
        commands.spawn((camera, RenderTarget::Image(target.into())));
    } else {
        commands.spawn(camera);
    }
}

/// Three-quarter view from the asset's front right, orbited by `angle` about the vertical.
fn camera_transform(view: &View, angle: f32) -> Transform {
    let direction = Quat::from_rotation_y(angle) * Vec3::new(1.0, 0.7, 1.0).normalize();
    let distance = view.radius / (std::f32::consts::FRAC_PI_4 / 2.0).sin() * 1.1;
    Transform::from_translation(view.centre + direction * distance).looking_at(view.centre, Vec3::Y)
}

fn turntable(time: Res<Time>, view: Res<View>, mut camera: Single<&mut Transform, With<Camera3d>>) {
    **camera = camera_transform(&view, time.elapsed_secs() * 0.3);
}

/// Headless: wait for the asset, let the frame settle, save one image, exit.
fn capture(
    mut commands: Commands,
    mut view: ResMut<View>,
    asset_server: Res<AssetServer>,
    mut exit: MessageWriter<AppExit>,
) {
    view.frames += 1;
    let path = view
        .screenshot
        .clone()
        .expect("capture only runs with --screenshot");
    if view.requested {
        if saved(&path) {
            exit.write(AppExit::Success);
        }
    } else {
        match asset_server.recursive_dependency_load_state(&view.scene) {
            RecursiveDependencyLoadState::Failed(error) => {
                eprintln!("load failed: {error}");
                exit.write(AppExit::error());
            }
            RecursiveDependencyLoadState::Loaded => view.settled += 1,
            _ => {}
        }
        if view.settled == SETTLE_FRAMES {
            let _ = std::fs::remove_file(&path);
            commands
                .spawn(Screenshot::image(view.target.clone().unwrap()))
                .observe(save_to_disk(path));
            view.requested = true;
        }
    }
    if view.frames > TIMEOUT_FRAMES {
        eprintln!("timed out before a screenshot was saved");
        exit.write(AppExit::error());
    }
}

fn saved(path: &Path) -> bool {
    std::fs::metadata(path).is_ok_and(|m| m.len() > 0)
}
