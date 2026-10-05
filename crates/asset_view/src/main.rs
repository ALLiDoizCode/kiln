//! Shows one asset under Bevy's renderer, beside a player-height figure.
//!
//! With `--screenshot` it renders one fixed view to a PNG with no window and
//! exits (the review gate uses this). Without it, it opens a window with a
//! slow turntable and reloads the asset whenever the GLB changes on disk.
//!
//! `--close` frames the asset alone from about first-person distance, with no figure.
//! `--back` takes the screenshot from the opposite side, the asset's back left.
//! `--stand <metres>` takes it as a player sees it: eye 1.7 m above the ground, that far from
//! the asset's origin (or the manifest's `stand_at`: a leaning trunk's middle at eye height) on its front right, looking at the middle of its height (at most 60
//! degrees up), with a wide field of view and no figure. Add `--back` to stand behind it.
//! `--pitch <degrees>` with `--stand` looks that far above level instead: 0 straight at a trunk,
//! 78 up into a canopy from beside it.
//!
//! A screenshot is saved only when the asset is in it. The same frame is rendered with the
//! asset hidden, and the two must differ where the manifest's bounds fall in the picture; if
//! they do not after a few tries, nothing is saved and the exit code is 1.
//!
//! Usage: asset_view <asset.glb> <manifest.json> [--screenshot <out.png>] [--close] [--back] [--stand <metres>] [--pitch <degrees>]

use std::{
    path::PathBuf,
    sync::{Arc, Mutex},
    time::Duration,
};

use bevy::{
    app::ScheduleRunnerPlugin,
    asset::{RecursiveDependencyLoadState, UnapprovedPathMode},
    camera::RenderTarget,
    prelude::*,
    render::{
        render_resource::{TextureFormat, TextureUsages},
        view::screenshot::{Screenshot, ScreenshotCaptured},
    },
    window::ExitCondition,
    winit::WinitPlugin,
    world_serialization::WorldAsset,
};
use serde::Deserialize;

const SIZE: u32 = 1024;
const PLAYER_HEIGHT: f32 = 1.8;
/// A player's eye, and how they look at an asset they stand beside (`--stand`).
const EYE_HEIGHT: f32 = 1.7;
const STAND_FOV: f32 = 1.31; // 75 degrees
const STAND_MAX_PITCH: f32 = 1.047; // 60 degrees
/// Frames to let shadows and shaders settle before capturing.
const SETTLE_FRAMES: u32 = 30;
const TIMEOUT_FRAMES: u32 = 3600;
/// Frames between showing or hiding the asset and capturing again.
const TOGGLE_FRAMES: u32 = 8;
/// How many times the three captures (asset, no asset, asset) are tried before giving up.
const CAPTURE_TRIES: u32 = 4;
/// A pixel differs when any channel is this far apart, of 255.
const PIXEL_DIFFERS: u8 = 8;
/// The asset is in the picture when this share of the pixels its bounds cover differ from the empty scene.
const MIN_ASSET_SHARE: f32 = 0.005;
/// Two captures of the same scene are the same when at most this share of their pixels differ.
const MAX_UNSTABLE_SHARE: f32 = 0.002;

#[derive(Deserialize)]
struct Manifest {
    bounds: Bounds,
    /// Where a player stands against the asset, as (x, z): a leaning trunk's middle at eye height.
    /// Absent: the origin.
    #[serde(default)]
    stand_at: [f32; 2],
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
    /// A player's view instead: (metres from `stand_at`, the height looked at).
    stand: Option<(f32, f32)>,
    stand_at: Vec3,
    /// With `stand`: radians above level to look, in place of looking at that height.
    pitch: Option<f32>,
    target: Option<Handle<Image>>,
    settled: u32,
    frames: u32,
    /// The asset's bounds, to find where it falls in the picture.
    bounds: (Vec3, Vec3),
    root: Option<Entity>,
    /// Captures so far in this try: the asset, the scene without it, the asset again.
    shots: Arc<Mutex<Vec<Image>>>,
    wait: u32,
    pending: bool,
    expect: usize,
    tries: u32,
}

fn main() -> AppExit {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut positional = Vec::new();
    let mut screenshot = None;
    let mut close = false;
    let mut back = false;
    let mut stand = None;
    let mut pitch = None;
    let mut iter = args.iter();
    while let Some(arg) = iter.next() {
        if arg == "--screenshot" {
            screenshot = iter.next().map(PathBuf::from);
        } else if arg == "--close" {
            close = true;
        } else if arg == "--back" {
            back = true;
        } else if arg == "--stand" {
            stand = iter.next().and_then(|metres| metres.parse::<f32>().ok());
            if stand.is_none() {
                eprintln!("--stand needs a distance in metres");
                return AppExit::error();
            }
        } else if arg == "--pitch" {
            pitch = iter.next().and_then(|degrees| degrees.parse::<f32>().ok()).map(f32::to_radians);
            if pitch.is_none() {
                eprintln!("--pitch needs an angle in degrees");
                return AppExit::error();
            }
        } else {
            positional.push(PathBuf::from(arg));
        }
    }
    if positional.len() != 2 || (pitch.is_some() && stand.is_none()) {
        eprintln!(
            "usage: asset_view <asset.glb> <manifest.json> [--screenshot <out.png>] [--close] [--back] [--stand <metres> [--pitch <degrees>]]"
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
    let close = close || stand.is_some();
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
            stand: stand.map(|metres| (metres, (min.y + max.y) / 2.0)),
            pitch,
            stand_at: Vec3::new(manifest.stand_at[0], 0.0, manifest.stand_at[1]),
            target: None,
            settled: 0,
            frames: 0,
            bounds: (min, max),
            root: None,
            shots: Arc::default(),
            wait: 0,
            pending: false,
            expect: 0,
            tries: 0,
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
    view.root = Some(commands.spawn(WorldAssetRoot(view.scene.clone())).id());

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

    let camera = (
        Camera3d::default(),
        camera_transform(&view, view.orbit),
        Projection::Perspective(PerspectiveProjection {
            fov: if view.stand.is_some() { STAND_FOV } else { std::f32::consts::FRAC_PI_4 },
            ..default()
        }),
    );
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
    if let Some((metres, height)) = view.stand {
        let turn = Quat::from_rotation_y(angle);
        let eye = view.stand_at + turn * Vec3::new(metres, 0.0, metres) * std::f32::consts::FRAC_1_SQRT_2 + Vec3::Y * EYE_HEIGHT;
        let pitch = view.pitch.unwrap_or(((height - EYE_HEIGHT) / metres).atan().min(STAND_MAX_PITCH));
        let toward = turn * Vec3::new(-1.0, 0.0, -1.0).normalize() * pitch.cos() + Vec3::Y * pitch.sin();
        return Transform::from_translation(eye).looking_to(toward, Vec3::Y);
    }
    let direction = Quat::from_rotation_y(angle) * Vec3::new(1.0, 0.7, 1.0).normalize();
    let distance = view.radius / (std::f32::consts::FRAC_PI_4 / 2.0).sin() * 1.1;
    Transform::from_translation(view.centre + direction * distance).looking_at(view.centre, Vec3::Y)
}

fn turntable(time: Res<Time>, view: Res<View>, mut camera: Single<&mut Transform, With<Camera3d>>) {
    **camera = camera_transform(&view, time.elapsed_secs() * 0.3);
}

/// Headless: wait for the asset, let the frame settle, capture it, the scene without it and it
/// again, and save the picture only if the asset is in it. Exits 1 otherwise.
fn capture(
    mut commands: Commands,
    mut view: ResMut<View>,
    asset_server: Res<AssetServer>,
    mut visibility: Query<&mut Visibility>,
    mut exit: MessageWriter<AppExit>,
) {
    view.frames += 1;
    if view.frames > TIMEOUT_FRAMES {
        eprintln!("timed out before a screenshot was saved");
        exit.write(AppExit::error());
        return;
    }
    if view.settled < SETTLE_FRAMES {
        match asset_server.recursive_dependency_load_state(&view.scene) {
            RecursiveDependencyLoadState::Failed(error) => {
                eprintln!("load failed: {error}");
                exit.write(AppExit::error());
            }
            RecursiveDependencyLoadState::Loaded => view.settled += 1,
            _ => {}
        }
        return;
    }
    if view.wait > 0 {
        view.wait -= 1;
        return;
    }
    let taken = view.shots.lock().unwrap().len();
    if !view.pending {
        let shots = view.shots.clone();
        commands
            .spawn(Screenshot::image(view.target.clone().unwrap()))
            .observe(move |captured: On<ScreenshotCaptured>| shots.lock().unwrap().push(captured.image.clone()));
        view.pending = true;
        view.expect = taken + 1;
        return;
    }
    // Captures arrive a frame or more after they are asked for.
    if taken < view.expect {
        return;
    }
    view.pending = false;
    let show = |visibility: &mut Query<&mut Visibility>, root: Option<Entity>, shown: bool| {
        if let Some(mut value) = root.and_then(|root| visibility.get_mut(root).ok()) {
            *value = if shown { Visibility::Inherited } else { Visibility::Hidden };
        }
    };
    match taken {
        1 => show(&mut visibility, view.root, false),
        2 => show(&mut visibility, view.root, true),
        _ => {
            let shots: Vec<Image> = std::mem::take(&mut *view.shots.lock().unwrap());
            let (with, without, again) = (&shots[0], &shots[1], &shots[2]);
            let region = view.region();
            let whole = (0, 0, SIZE, SIZE);
            let unstable = differing(with, again, whole);
            let present = differing(again, without, region);
            if unstable <= MAX_UNSTABLE_SHARE && present >= MIN_ASSET_SHARE {
                let path = view.screenshot.clone().expect("capture only runs with --screenshot");
                let saved = again.clone().try_into_dynamic().map_err(|e| e.to_string()).and_then(|image| image.to_rgb8().save(&path).map_err(|e| e.to_string()));
                match saved {
                    Ok(()) => exit.write(AppExit::Success),
                    Err(error) => {
                        eprintln!("cannot save {}: {error}", path.display());
                        exit.write(AppExit::error())
                    }
                };
                return;
            }
            view.tries += 1;
            if view.tries >= CAPTURE_TRIES {
                eprintln!(
                    "asset.in_picture: after {CAPTURE_TRIES} tries the asset is not in the picture: {:.4} of the pixels its bounds cover ({region:?}, as x0 y0 x1 y1) differ from the scene without it (wanted at least {MIN_ASSET_SHARE}), and {:.4} of all pixels changed between two captures of it (allowed {MAX_UNSTABLE_SHARE}); nothing saved",
                    present, unstable
                );
                exit.write(AppExit::error());
                return;
            }
            view.wait = SETTLE_FRAMES;
            return;
        }
    }
    view.wait = TOGGLE_FRAMES;
}

impl View {
    /// Where the manifest's bounds fall in the screenshot, as pixels (x0, y0, x1, y1); the whole
    /// picture when a corner of them is beside or behind the camera.
    fn region(&self) -> (u32, u32, u32, u32) {
        let camera = camera_transform(self, self.orbit);
        let from_world = camera.to_matrix().inverse();
        let fov = if self.stand.is_some() { STAND_FOV } else { std::f32::consts::FRAC_PI_4 };
        let reach = (fov / 2.0).tan();
        let (min, max) = self.bounds;
        let (mut lo, mut hi) = (Vec2::splat(f32::MAX), Vec2::splat(f32::MIN));
        for corner in 0..8 {
            let point = Vec3::new(
                if corner & 1 == 0 { min.x } else { max.x },
                if corner & 2 == 0 { min.y } else { max.y },
                if corner & 4 == 0 { min.z } else { max.z },
            );
            let seen = from_world.transform_point3(point);
            if seen.z > -0.05 {
                return (0, 0, SIZE, SIZE);
            }
            let at = Vec2::new(seen.x, seen.y) / (-seen.z * reach);
            lo = lo.min(at);
            hi = hi.max(at);
        }
        let pixel = |value: f32| (((value + 1.0) / 2.0 * SIZE as f32).clamp(0.0, SIZE as f32)) as u32;
        // The picture's y runs down.
        (pixel(lo.x), pixel(-hi.y), pixel(hi.x), pixel(-lo.y))
    }
}

/// The share of the pixels in a region (x0, y0, x1, y1) that differ between two captures.
fn differing(a: &Image, b: &Image, (x0, y0, x1, y1): (u32, u32, u32, u32)) -> f32 {
    let (Some(a_data), Some(b_data)) = (&a.data, &b.data) else {
        return 0.0;
    };
    let (width, stride) = (a.width() as usize, a_data.len() / (a.width() * a.height()).max(1) as usize);
    if a_data.len() != b_data.len() || x1 <= x0 || y1 <= y0 {
        return 0.0;
    }
    let mut differ = 0usize;
    for y in y0 as usize..y1 as usize {
        for x in x0 as usize..x1 as usize {
            let at = (y * width + x) * stride;
            if (0..stride.min(3)).any(|c| a_data[at + c].abs_diff(b_data[at + c]) > PIXEL_DIFFERS) {
                differ += 1;
            }
        }
    }
    differ as f32 / ((x1 - x0) * (y1 - y0)) as f32
}
