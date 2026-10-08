//! Shows a creature's fur changing between its calm and its spiked shape, in a window, on the
//! viewer's ground and light, under a slow turntable. A throwaway for looking at the models of
//! `learn/research/fur-animation-trial.md`.
//!
//! fur_view [model.glb] [--out <folder>] [--frames N]
//!
//! With no model it shows the three models of the note from `../models/` (those that are there).
//! With a model it shows that file and moves its first morph target from 0 to 1 and back.
//! `--frames N --out <folder>`: no window; writes N pictures of each model, from calm to spiked.
//! `--out <folder>` alone: the window also saves a picture of itself every two seconds.
//!
//! Built with `--features overlay` the keys and the state are drawn in the window; without it
//! they are printed to the terminal and the state is the window's title.

use std::{io::Write, path::PathBuf, time::Duration};

use asset_view::scene::{self, Model};
use bevy::{
    app::ScheduleRunnerPlugin,
    camera::RenderTarget,
    mesh::{VertexAttributeValues, morph::MorphWeights},
    prelude::*,
    render::{
        RenderPlugin,
        render_resource::TextureFormat,
        view::screenshot::{Screenshot, save_to_disk},
    },
    window::ExitCondition,
    winit::WinitPlugin,
    world_serialization::WorldAsset,
};

/// The camera, as `crates/asset_view/src/main.rs` has it.
const FOV: f32 = std::f32::consts::FRAC_PI_4;
const TURN_SPEED: f32 = 0.3;
/// Seconds: calm to spiked, held spiked, back to calm, held calm.
const OUT: f32 = 1.5;
const HOLD: f32 = 1.0;
const PERIOD: f32 = 2.0 * (OUT + HOLD);
/// How much of the way Left and Right move in a second, while paused.
const NUDGE: f32 = 0.5;
const SIZE: (u32, u32) = (1280, 960);
const SETTLE: u32 = 8;
const KEYS: &str = "Space pause or resume | Left, Right: less or more spiked, while paused | 1 2 3 model | T turntable | R reset camera | Esc quit";
const DIGITS: [KeyCode; 3] = [KeyCode::Digit1, KeyCode::Digit2, KeyCode::Digit3];

/// The note's three models: file, what it is, and how its fur is driven.
const MODELS: [(&str, &str, Fur); 3] = [
    ("a_fused_morph.glb", "one fused surface (H3.1)", Fur::Fused),
    ("b_pieces_p1_morph.glb", "loose pieces (P1.0)", Fur::Pieces),
    ("b_pieces_p2_morph.glb", "loose pieces (P2.0)", Fur::Pieces),
];

/// Which morph targets of a model the amount (0 calm, 1 spiked) drives.
#[derive(Clone, Copy)]
enum Fur {
    /// `a_morph_fused.py`: target 3, `spiked_axial`, from 0 (as generated) to 1.
    Fused,
    /// `b_morph_pieces.py`: target 0, `retracted`, from 1 down to 0 (as generated, half way),
    /// then target 1, `extended`, from 0 to 1.
    Pieces,
    /// Any other file: its first target, from 0 to 1.
    First,
}

impl Fur {
    fn driven(self) -> &'static [usize] {
        match self {
            Fur::Fused => &[3],
            Fur::Pieces => &[0, 1],
            Fur::First => &[0],
        }
    }

    /// The weight of target `index` at `amount`; a target that is not driven stays at 0.
    fn weight(self, index: usize, amount: f32) -> f32 {
        match (self, index) {
            (Fur::Fused, 3) | (Fur::First, 0) => amount,
            (Fur::Pieces, 0) => (1.0 - 2.0 * amount).max(0.0),
            (Fur::Pieces, 1) => (2.0 * amount - 1.0).max(0.0),
            _ => 0.0,
        }
    }
}

struct Shown {
    file_name: String,
    what: String,
    fur: Fur,
    key: KeyCode,
    scene: Handle<WorldAsset>,
}

#[derive(Resource)]
struct Show {
    models: Vec<Shown>,
    current: usize,
}

/// Where the loop is. `amount` is what is shown; `clock` only moves while it plays.
#[derive(Resource)]
struct Play {
    amount: f32,
    clock: f32,
    paused: bool,
}

#[derive(Resource)]
struct Turn {
    angle: f32,
    on: bool,
}

/// The middle and the radius of the box that holds the model in every shape of the loop.
/// Found again, a few frames after a model is put in place.
#[derive(Resource, Default)]
struct Framing {
    waited: u32,
    found: Option<(Vec3, f32)>,
}

#[derive(Resource)]
struct Out(Option<PathBuf>);

/// The pictures of `--frames`: which model and picture is next.
#[derive(Resource)]
struct Frames {
    count: u32,
    frame: u32,
    waited: u32,
    asked: bool,
}

/// The line that says what is on screen.
#[derive(Resource, Default)]
struct Status(String);

#[cfg(feature = "overlay")]
#[derive(Component)]
struct Overlay;

fn main() -> AppExit {
    let (mut glb, mut out, mut frames) = (None, None, None);
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut rest = args.iter();
    while let Some(arg) = rest.next() {
        match arg.as_str() {
            "--out" => out = rest.next().map(PathBuf::from),
            "--frames" => frames = rest.next().and_then(|n| n.parse::<u32>().ok()).filter(|n| *n > 0),
            _ => glb = Some(arg.clone()),
        }
    }
    if args.iter().any(|a| a == "--frames") && (frames.is_none() || out.is_none()) {
        eprintln!("usage: fur_view [model.glb] [--out <folder>] [--frames N]   (--frames needs a count and --out)");
        return AppExit::error();
    }

    // The folder assets are read from, and the models in it to show.
    let (folder, models): (PathBuf, Vec<(String, String, Fur, KeyCode)>) = match glb {
        Some(path) => match std::fs::canonicalize(&path) {
            Ok(glb) => {
                let name = glb.file_name().unwrap().to_string_lossy().into_owned();
                (glb.parent().unwrap().to_owned(), vec![(name, "first morph target".to_string(), Fur::First, DIGITS[0])])
            }
            Err(error) => {
                eprintln!("cannot open {path}: {error}");
                return AppExit::error();
            }
        },
        None => {
            let folder = PathBuf::from(concat!(env!("CARGO_MANIFEST_DIR"), "/../models"));
            let there = MODELS.iter().zip(DIGITS).filter(|((file, ..), _)| folder.join(file).is_file());
            (folder.clone(), there.map(|((file, what, fur), key)| (file.to_string(), what.to_string(), *fur, key)).collect())
        }
    };
    if models.is_empty() {
        eprintln!("none of the note's models is in {}: run scripts/run_all.sh, or give a model file", folder.display());
        return AppExit::error();
    }
    if let Some(out) = &out {
        std::fs::create_dir_all(out).unwrap();
    }

    let mut app = App::new();
    let plugins = scene::plugins(&folder.join(&models[0].0), false);
    if frames.is_some() {
        app.add_plugins(
            plugins
                .set(WindowPlugin { primary_window: None, exit_condition: ExitCondition::DontExit, ..default() })
                .disable::<WinitPlugin>()
                .set(RenderPlugin { synchronous_pipeline_compilation: true, ..default() }),
        )
        .add_plugins(ScheduleRunnerPlugin::run_loop(Duration::ZERO))
        .insert_resource(Frames { count: frames.unwrap(), frame: 0, waited: 0, asked: false })
        .add_systems(Update, take_frames.before(set_weights));
    } else {
        app.add_plugins(plugins.set(WindowPlugin {
            primary_window: Some(Window { title: "fur_view".to_string(), ..default() }),
            ..default()
        }))
        .add_systems(Update, (keys, play, window_pictures).chain().before(set_weights));
        println!("{KEYS}");
    }
    scene::light_the_world(&mut app);
    app.insert_resource(Out(out))
        // The loop starts in its calm hold, so the first thing seen is the model as it is at rest.
        .insert_resource(Play { amount: 0.0, clock: PERIOD - HOLD, paused: false })
        .insert_resource(Turn { angle: 0.0, on: frames.is_none() })
        .init_resource::<Framing>()
        .init_resource::<Status>()
        .add_systems(Startup, move |world: &mut World| setup(world, &models, frames.is_some()))
        .add_systems(Update, (set_weights, frame_model, report).chain());
    #[cfg(feature = "overlay")]
    app.add_systems(Update, overlay.after(report));
    app.run()
}

fn setup(world: &mut World, models: &[(String, String, Fur, KeyCode)], to_image: bool) {
    let scenes: Vec<Handle<WorldAsset>> = {
        let asset_server = world.resource::<AssetServer>();
        // Every model is loaded now and kept, so changing model does not wait for the disk.
        models.iter().map(|(file, ..)| asset_server.load(GltfAssetLabel::Scene(0).from_asset(file.clone()))).collect()
    };
    world
        .run_system_cached_with(
            |file: In<String>,
             mut commands: Commands,
             asset_server: Res<AssetServer>,
             mut meshes: ResMut<Assets<Mesh>>,
             mut materials: ResMut<Assets<StandardMaterial>>| {
                scene::spawn_scene(&mut commands, &asset_server, &mut meshes, &mut materials, &file);
            },
            models[0].0.clone(),
        )
        .unwrap();
    let shown = models.iter().zip(scenes).map(|((file_name, what, fur, key), scene)| Shown {
        file_name: file_name.clone(),
        what: what.clone(),
        fur: *fur,
        key: *key,
        scene,
    });
    let show = Show { models: shown.collect(), current: 0 };
    world.insert_resource(show);

    let camera = world.spawn((
        Camera3d::default(),
        Projection::Perspective(PerspectiveProjection { fov: FOV, ..default() }),
        Transform::from_xyz(3.0, 2.0, 3.0).looking_at(Vec3::ZERO, Vec3::Y),
    ));
    if to_image {
        let target = Image::new_target_texture(SIZE.0, SIZE.1, TextureFormat::Rgba8UnormSrgb, None);
        let camera = camera.id();
        let target = world.resource_mut::<Assets<Image>>().add(target);
        world.entity_mut(camera).insert(RenderTarget::Image(target.into()));
    }
    #[cfg(feature = "overlay")]
    {
        let camera = world.query_filtered::<Entity, With<Camera3d>>().single(world).unwrap();
        world.spawn((
            Overlay,
            Text::default(),
            TextFont::from_font_size(15.0),
            Node { position_type: PositionType::Absolute, left: px(10), top: px(8), ..default() },
            UiTargetCamera(camera),
        ));
    }
}

/// Puts model `index` in place of the one shown. Bevy takes the old one away when the root changes.
fn change_model(index: usize, show: &mut Show, framing: &mut Framing, commands: &mut Commands, model: Entity) {
    show.current = index;
    *framing = Framing::default();
    commands.entity(model).insert(WorldAssetRoot(show.models[index].scene.clone()));
}

#[expect(clippy::too_many_arguments)]
fn keys(
    mut commands: Commands,
    time: Res<Time>,
    keys: Res<ButtonInput<KeyCode>>,
    mut show: ResMut<Show>,
    mut play: ResMut<Play>,
    mut turn: ResMut<Turn>,
    mut framing: ResMut<Framing>,
    model: Single<Entity, With<Model>>,
    mut exit: MessageWriter<AppExit>,
) {
    if keys.just_pressed(KeyCode::Escape) {
        exit.write(AppExit::Success);
    }
    if keys.just_pressed(KeyCode::Space) {
        play.paused = !play.paused;
        if !play.paused {
            // Go on towards spiked from the amount on screen: the easing of `eased`, undone.
            play.clock = OUT * (0.5 - ((1.0 - 2.0 * play.amount).asin() / 3.0).sin());
        }
    }
    if play.paused {
        let way = f32::from(keys.pressed(KeyCode::ArrowRight)) - f32::from(keys.pressed(KeyCode::ArrowLeft));
        play.amount = (play.amount + way * NUDGE * time.delta_secs()).clamp(0.0, 1.0);
    }
    if keys.just_pressed(KeyCode::KeyT) {
        turn.on = !turn.on;
    }
    if keys.just_pressed(KeyCode::KeyR) {
        turn.angle = 0.0;
    }
    let wanted = show.models.iter().position(|shown| keys.just_pressed(shown.key));
    if let Some(index) = wanted.filter(|index| *index != show.current) {
        change_model(index, &mut show, &mut framing, &mut commands, *model);
    }
}

/// 0 to 1 with a slow start and a slow end.
fn eased(x: f32) -> f32 {
    x * x * (3.0 - 2.0 * x)
}

fn play(time: Res<Time>, framing: Res<Framing>, mut play: ResMut<Play>) {
    if play.paused || framing.found.is_none() {
        return;
    }
    play.clock = (play.clock + time.delta_secs()) % PERIOD;
    let back = play.clock - OUT - HOLD;
    play.amount = if play.clock < OUT {
        eased(play.clock / OUT)
    } else if back < 0.0 {
        1.0
    } else {
        eased((1.0 - back / OUT).max(0.0))
    };
}

/// Normals need nothing here: Bevy morphs them with the positions when the file carries them.
fn set_weights(show: Res<Show>, play: Res<Play>, mut morphs: Query<&mut MorphWeights>) {
    let fur = show.models[show.current].fur;
    for mut morph in &mut morphs {
        for (index, weight) in morph.weights_mut().iter_mut().enumerate() {
            *weight = fur.weight(index, play.amount);
        }
    }
}

/// The lowest and highest corner of the box that holds every vertex under `model` when calm,
/// half way and spiked. `scene::vertex_box` and Bevy's own boxes know the stored shape only.
fn fur_box(
    model: Entity,
    fur: Fur,
    children: &Query<&Children>,
    placed: &Query<(&Mesh3d, &GlobalTransform)>,
    meshes: &Assets<Mesh>,
) -> Option<(Vec3, Vec3)> {
    let (mut min, mut max) = (Vec3::MAX, Vec3::MIN);
    for entity in children.iter_descendants(model) {
        let Ok((mesh, to_world)) = placed.get(entity) else { continue };
        let Some(mesh) = meshes.get(&mesh.0) else { continue };
        let Some(VertexAttributeValues::Float32x3(positions)) = mesh.attribute(Mesh::ATTRIBUTE_POSITION) else { continue };
        // Bevy keeps the targets one after another, each as long as the list of vertices.
        let moves = mesh.morph_targets().map(Vec::as_slice).unwrap_or(&[]);
        for amount in [0.0, 0.5, 1.0] {
            for (vertex, position) in positions.iter().enumerate() {
                let mut point = Vec3::from(*position);
                for (target, moved) in moves.chunks_exact(positions.len()).enumerate() {
                    point += moved[vertex].position * fur.weight(target, amount);
                }
                let point = to_world.transform_point(point);
                min = min.min(point);
                max = max.max(point);
            }
        }
    }
    min.cmple(max).all().then_some((min, max))
}

/// Circles the camera round the middle of the model's box, far enough back to hold all of it:
/// `frame_model` of `crates/asset_view/src/main.rs`, with the box of every shape of the loop
/// and room for a narrow window.
#[expect(clippy::too_many_arguments)]
fn frame_model(
    time: Res<Time>,
    show: Res<Show>,
    asset_server: Res<AssetServer>,
    mesh_assets: Res<Assets<Mesh>>,
    mut framing: ResMut<Framing>,
    mut turn: ResMut<Turn>,
    model: Single<Entity, With<Model>>,
    children: Query<&Children>,
    placed: Query<(&Mesh3d, &GlobalTransform)>,
    mut camera: Single<(&mut Transform, &Projection), With<Camera3d>>,
) {
    let shown = &show.models[show.current];
    if framing.found.is_none() && asset_server.is_loaded_with_dependencies(&shown.scene) {
        // A few frames, so the model before this one is gone and this one is placed.
        framing.waited += 1;
        if framing.waited > 3 {
            let found = fur_box(*model, shown.fur, &children, &placed, &mesh_assets);
            framing.found = found.map(|(min, max)| ((min + max) / 2.0, ((max - min).length() / 2.0).max(0.01)));
        }
    }
    let Some((centre, radius)) = framing.found else { return };
    if turn.on {
        turn.angle += time.delta_secs() * TURN_SPEED;
    }
    // FOV is the angle from top to bottom; a window taller than wide sees less from side to side.
    let aspect = if let Projection::Perspective(lens) = camera.1 { lens.aspect_ratio.min(1.0) } else { 1.0 };
    let distance = radius / ((FOV / 2.0).tan() * aspect).atan().sin() * 1.1;
    let direction = Quat::from_rotation_y(turn.angle) * Vec3::new(1.0, 0.7, 1.0).normalize();
    *camera.0 = Transform::from_translation(centre + direction * distance).looking_at(centre, Vec3::Y);
}

/// Says what is on screen: in the window's title and on one line of the terminal.
fn report(
    show: Res<Show>,
    play: Res<Play>,
    turn: Res<Turn>,
    mesh_assets: Res<Assets<Mesh>>,
    morphs: Query<&MorphWeights>,
    mut status: ResMut<Status>,
    window: Option<Single<&mut Window>>,
) {
    let shown = &show.models[show.current];
    let mut line = format!("[{}] {} - {}", show.current + 1, shown.file_name, shown.what);
    if let Some(morph) = morphs.iter().next() {
        let names = morph.first_mesh().and_then(|mesh| mesh_assets.get(mesh)).and_then(Mesh::morph_target_names).unwrap_or(&[]);
        for index in shown.fur.driven().iter().filter(|index| **index < morph.weights().len()) {
            let name = names.get(*index).cloned().unwrap_or(format!("target {index}"));
            line += &format!(" | {name} {:.2}", morph.weights()[*index]);
        }
    } else {
        line += " | no morph targets";
    }
    line += if play.paused { " | paused" } else { " | playing" };
    line += if turn.on { "" } else { " | turntable off" };
    if line == status.0 {
        return;
    }
    if let Some(mut window) = window {
        window.title = format!("fur_view: {line}");
        print!("\r{line:<110}");
        std::io::stdout().flush().ok();
    }
    status.0 = line;
}

#[cfg(feature = "overlay")]
fn overlay(status: Res<Status>, mut text: Single<&mut Text, With<Overlay>>) {
    if status.is_changed() {
        text.0 = format!("{}\n{}", status.0, KEYS.replace(" | ", "\n"));
    }
}

/// With `--out`, the window saves a picture of itself every two seconds.
fn window_pictures(mut commands: Commands, time: Res<Time>, out: Res<Out>, mut next: Local<(f32, u32)>) {
    let Some(out) = &out.0 else { return };
    if time.elapsed_secs() < next.0 {
        return;
    }
    if next.1 > 0 {
        commands.spawn(Screenshot::primary_window()).observe(save_to_disk(out.join(format!("window_{:02}.png", next.1))));
    }
    *next = (next.0 + 2.0, next.1 + 1);
}

/// `--frames`: for each model, `count` pictures with the amount going evenly from 0 to 1.
#[expect(clippy::too_many_arguments)]
fn take_frames(
    mut commands: Commands,
    out: Res<Out>,
    mut frames: ResMut<Frames>,
    mut show: ResMut<Show>,
    mut play: ResMut<Play>,
    mut framing: ResMut<Framing>,
    model: Single<Entity, With<Model>>,
    target: Single<&RenderTarget, With<Camera3d>>,
    pending: Query<(), With<Screenshot>>,
    mut exit: MessageWriter<AppExit>,
) {
    if framing.found.is_none() || !pending.is_empty() {
        return;
    }
    if frames.asked {
        (frames.asked, frames.waited, frames.frame) = (false, 0, frames.frame + 1);
        if frames.frame == frames.count {
            frames.frame = 0;
            if show.current + 1 == show.models.len() {
                exit.write(AppExit::Success);
                framing.found = None;
            } else {
                let next = show.current + 1;
                change_model(next, &mut show, &mut framing, &mut commands, *model);
            }
        }
        return;
    }
    play.amount = if frames.count == 1 { 0.0 } else { frames.frame as f32 / (frames.count - 1) as f32 };
    frames.waited += 1;
    if frames.waited < SETTLE {
        return;
    }
    let stem = show.models[show.current].file_name.trim_end_matches(".glb").to_string();
    let path = out.0.as_ref().unwrap().join(format!("{stem}_{:02}_of_{:02}.png", frames.frame + 1, frames.count));
    println!("{} amount {:.2}", path.display(), play.amount);
    let RenderTarget::Image(image) = *target else { return };
    commands.spawn(Screenshot::image(image.handle.clone())).observe(save_to_disk(path));
    frames.asked = true;
}
