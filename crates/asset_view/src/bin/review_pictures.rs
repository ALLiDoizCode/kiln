//! Writes the review pictures of one `.glb`: the fixed set in `asset_view::views`, as PNG files.
//!
//! Usage: review_pictures <model.glb> --size <metres> --closest <metres> --out <folder>
//!
//! The model is shown at the size: scaled so its largest dimension is that many metres, standing
//! on the ground. The file is only read. `--closest` is the target profile's closest viewing
//! distance. One picture per view is written to `<folder>/<view name>.png`, and one line of JSON
//! on standard output says what was written. Everything else is said on standard error.
//!
//! No window is opened and no display is needed, only a graphics card. The scene, the light and
//! the glTF loader are the viewer's, so a picture shows what the viewer shows.
//!
//! The exit status is 0 only when every picture was written. A model that cannot be loaded, that
//! holds no mesh or has no extent, a picture that cannot be written, or 120 seconds without the
//! model loading, all end the program with status 1 and a line saying why.

use std::{
    path::PathBuf,
    sync::{Arc, Mutex},
    time::{Duration, Instant},
};

use asset_view::{
    scene::{self, Model},
    views::{self, PICTURE_SIZE, Placing, Stand, VIEW_SET, VIEWS},
};
use bevy::{
    app::ScheduleRunnerPlugin,
    asset::{LoadState, RecursiveDependencyLoadState},
    camera::RenderTarget,
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
use serde_json::json;

/// The Bevy this crate is built with, for the report. A test holds it to the workspace's pin.
const BEVY: &str = "0.19.1";
/// Frames drawn after the camera moves and before the picture is taken, so that the first
/// picture has the model's meshes and textures on the graphics card and every picture has the
/// camera, the post and the shadows where they belong.
const SETTLE_FRAMES: u32 = 6;
const LOAD_LIMIT: Duration = Duration::from_secs(120);
/// A model whose file is read and whose scene still has no mesh after this many frames has none.
const NO_MESH_FRAMES: u32 = 300;

struct Arguments {
    glb: PathBuf,
    size: f32,
    closest: f32,
    out: PathBuf,
}

const USAGE: &str = "usage: review_pictures <model.glb> --size <metres> --closest <metres> --out <folder>";

fn arguments(args: &[String]) -> Result<Arguments, String> {
    let (mut glb, mut size, mut closest, mut out) = (None, None, None, None);
    let mut rest = args.iter();
    while let Some(arg) = rest.next() {
        let mut value = || rest.next().ok_or(format!("{arg} needs a value"));
        let metres = |text: &String| match text.parse::<f32>() {
            Ok(number) if number > 0.0 && number.is_finite() => Ok(number),
            _ => Err(format!("{arg} must be a number of metres above zero, not {text}")),
        };
        match arg.as_str() {
            "--size" => size = Some(metres(value()?)?),
            "--closest" => closest = Some(metres(value()?)?),
            "--out" => out = Some(PathBuf::from(value()?)),
            _ if arg.starts_with("--") => return Err(format!("there is no option {arg}")),
            _ if glb.is_none() => glb = Some(arg.clone()),
            _ => return Err(format!("one model file only, not also {arg}")),
        }
    }
    let glb = glb.ok_or("no model file was given")?;
    let glb = std::fs::canonicalize(&glb).map_err(|error| format!("cannot open {glb}: {error}"))?;
    Ok(Arguments {
        glb,
        size: size.ok_or("--size was not given")?,
        closest: closest.ok_or("--closest was not given")?,
        out: out.ok_or("--out was not given")?,
    })
}

#[derive(Resource)]
struct Job {
    file_name: String,
    size: f32,
    closest: f32,
    out: PathBuf,
    started: Instant,
}

#[derive(Resource)]
struct Loading(Handle<WorldAsset>);

/// The picture the cameras draw into.
#[derive(Resource)]
struct Target(Handle<Image>);

/// Where the latest picture taken is put by the observer that receives it.
#[derive(Resource, Clone, Default)]
struct Taken(Arc<Mutex<Option<Image>>>);

#[derive(Component)]
struct Post;

#[derive(Resource, Default)]
enum Step {
    /// The model's file is still being read.
    #[default]
    Loading,
    /// The file is read, textures and all. `frames` have been drawn since, and the model's
    /// meshes were in the scene for the last `seen` of them.
    Loaded { frames: u32, seen: u32 },
    /// The camera is in place for view `view`; `frames` more are drawn before the picture.
    Settling { view: usize, frames: u32 },
    /// The picture of view `view` has been asked for.
    Taking { view: usize },
    Finished,
}

#[derive(Resource)]
struct Placed {
    placing: Placing,
    meshes: usize,
}

fn main() -> AppExit {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let args = match arguments(&args) {
        Ok(args) => args,
        Err(error) => {
            eprintln!("review_pictures: {error}\n{USAGE}");
            return AppExit::error();
        }
    };
    if let Err(error) = std::fs::create_dir_all(&args.out) {
        eprintln!("review_pictures: cannot make the folder {}: {error}", args.out.display());
        return AppExit::error();
    }

    let mut app = App::new();
    app.add_plugins(
        // The pictures are of the file as it is now: it is not watched for changes.
        scene::plugins(&args.glb, false)
            // No window: the cameras draw into a picture.
            .set(WindowPlugin { primary_window: None, exit_condition: ExitCondition::DontExit, ..default() })
            .disable::<WinitPlugin>()
            // A shader still being compiled would leave its mesh out of a picture.
            .set(RenderPlugin { synchronous_pipeline_compilation: true, ..default() }),
    )
    .add_plugins(ScheduleRunnerPlugin::run_loop(Duration::ZERO));
    scene::light_the_world(&mut app);
    app.insert_resource(Job {
        file_name: args.glb.file_name().unwrap().to_string_lossy().into_owned(),
        size: args.size,
        closest: args.closest,
        out: args.out,
        started: Instant::now(),
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
    commands.insert_resource(Loading(scene));

    let target = images.add(Image::new_target_texture(PICTURE_SIZE.0, PICTURE_SIZE.1, TextureFormat::Rgba8UnormSrgb, None));
    commands.spawn((Camera3d::default(), RenderTarget::Image(target.clone().into())));
    commands.insert_resource(Target(target));

    commands.spawn((
        Post,
        Mesh3d(meshes.add(Cuboid::new(views::POST_WIDTH, views::POST_HEIGHT, views::POST_WIDTH))),
        MeshMaterial3d(materials.add(StandardMaterial {
            base_color: Color::linear_rgb(0.75, 0.42, 0.1),
            perceptual_roughness: 1.0,
            ..default()
        })),
        Visibility::Hidden,
    ));
}

fn fail(exit: &mut MessageWriter<AppExit>, step: &mut Step, why: impl std::fmt::Display) {
    eprintln!("review_pictures: {why}");
    *step = Step::Finished;
    exit.write(AppExit::error());
}

#[expect(clippy::too_many_arguments, clippy::type_complexity, reason = "one system walks the whole job")]
fn step(
    mut commands: Commands,
    job: Res<Job>,
    loading: Res<Loading>,
    target: Res<Target>,
    taken: Res<Taken>,
    placed: Option<Res<Placed>>,
    adapter: Res<RenderAdapterInfo>,
    asset_server: Res<AssetServer>,
    mesh_assets: Res<Assets<Mesh>>,
    mut step: ResMut<Step>,
    mut exit: MessageWriter<AppExit>,
    model: Single<Entity, With<Model>>,
    children: Query<&Children>,
    mesh_entities: Query<(&Mesh3d, &GlobalTransform)>,
    // What this system moves: the model, the camera and the post.
    mut transforms: ParamSet<(
        Single<&mut Transform, With<Model>>,
        Single<(&mut Transform, &mut Projection), With<Camera3d>>,
        Single<(&mut Transform, &mut Visibility), With<Post>>,
    )>,
) {
    match *step {
        Step::Loading | Step::Loaded { .. } => {
            if let LoadState::Failed(error) = asset_server.load_state(&loading.0) {
                return fail(&mut exit, &mut step, format!("the model could not be loaded: {error}"));
            }
            // A texture that cannot be read fails here: no picture is taken of a model without it.
            if let RecursiveDependencyLoadState::Failed(error) = asset_server.recursive_dependency_load_state(&loading.0) {
                return fail(&mut exit, &mut step, format!("a part of the model could not be loaded: {error}"));
            }
            if job.started.elapsed() > LOAD_LIMIT {
                return fail(&mut exit, &mut step, "the model had not loaded after 120 seconds");
            }
            if !asset_server.is_loaded_with_dependencies(&loading.0) {
                return;
            }
            // The scene's entities appear a frame or two after the file is read, and they are
            // where the scene places them a frame after that.
            let found = scene::vertex_box(*model, &children, &mesh_entities, &mesh_assets);
            let (frames, seen) = if let Step::Loaded { frames, seen } = *step { (frames, seen) } else { (0, 0) };
            if seen < 2 {
                if found.is_none() && frames > NO_MESH_FRAMES {
                    return fail(&mut exit, &mut step, "the model holds no mesh to take a picture of");
                }
                *step = Step::Loaded { frames: frames + 1, seen: if found.is_some() { seen + 1 } else { 0 } };
                return;
            }
            let Some((min, max, meshes)) = found else {
                return fail(&mut exit, &mut step, "the model's meshes went away while it loaded");
            };
            let Some(placing) = views::placing(min, max, job.size) else {
                return fail(&mut exit, &mut step, "the model has no extent, so it cannot be shown at a size");
            };
            **transforms.p0() = Transform::from_translation(placing.translation).with_scale(Vec3::splat(placing.scale));
            commands.insert_resource(Placed { placing, meshes });
            *step = Step::Settling { view: 0, frames: 0 };
        }
        Step::Settling { view, frames } => {
            let placing = placed.expect("placed before settling").placing;
            if frames == 0 {
                let shot = views::shot(&VIEWS[view], &placing, job.size, job.closest);
                let mut camera = transforms.p1();
                *camera.0 = Transform::from_translation(shot.eye).looking_at(shot.looks_at, shot.up);
                *camera.1 = Projection::Perspective(PerspectiveProjection {
                    fov: shot.fov.to_radians(),
                    near: shot.near,
                    ..default()
                });
                let mut post = transforms.p2();
                *post.0 = Transform::from_translation(views::post_middle(&placing));
                *post.1 = if VIEWS[view].stand == Stand::Standing { Visibility::Visible } else { Visibility::Hidden };
            }
            if frames < SETTLE_FRAMES {
                *step = Step::Settling { view, frames: frames + 1 };
                return;
            }
            let taken = taken.clone();
            commands.spawn(Screenshot::image(target.0.clone())).observe(move |captured: On<ScreenshotCaptured>| {
                *taken.0.lock().unwrap() = Some(captured.image.clone());
            });
            *step = Step::Taking { view };
        }
        Step::Taking { view } => {
            let Some(image) = taken.0.lock().unwrap().take() else { return };
            let path = job.out.join(format!("{}.png", VIEWS[view].name));
            if let Err(error) = write_png(image, &path) {
                return fail(&mut exit, &mut step, format!("the picture {} was not written: {error}", path.display()));
            }
            if view + 1 < VIEWS.len() {
                *step = Step::Settling { view: view + 1, frames: 0 };
                return;
            }
            let placed = placed.expect("placed before taking");
            println!("{}", report(&job, &placed, &adapter));
            *step = Step::Finished;
            exit.write(AppExit::Success);
        }
        Step::Finished => {}
    }
}

/// Writes a picture as an 8-bit RGB PNG, and reads the file's size back as proof it is there.
fn write_png(image: Image, path: &std::path::Path) -> Result<(), String> {
    let picture = image.try_into_dynamic().map_err(|error| error.to_string())?.to_rgb8();
    if picture.dimensions() != PICTURE_SIZE {
        return Err(format!("it came out {:?} pixels, not {PICTURE_SIZE:?}", picture.dimensions()));
    }
    picture.save_with_format(path, image::ImageFormat::Png).map_err(|error| error.to_string())?;
    match std::fs::metadata(path) {
        Ok(file) if file.len() > 0 => Ok(()),
        Ok(_) => Err("the file is empty".into()),
        Err(error) => Err(error.to_string()),
    }
}

/// What was written, as one line of JSON.
fn report(job: &Job, placed: &Placed, adapter: &RenderAdapterInfo) -> serde_json::Value {
    // An f32 as the shortest decimal that reads back as it: 0.8, not 0.800000011920929.
    let tidy = |number: f32| number.to_string().parse::<f64>().unwrap_or(number as f64);
    let list = |v: Vec3| json!([tidy(v.x), tidy(v.y), tidy(v.z)]);
    let views: Vec<_> = VIEWS
        .iter()
        .map(|view| {
            let shot = views::shot(view, &placed.placing, job.size, job.closest);
            json!({
                "name": view.name,
                "file": format!("{}.png", view.name),
                "shows": view.shows,
                "eye": list(shot.eye),
                "looks_at": list(shot.looks_at),
                "fov_degrees": tidy(shot.fov),
            })
        })
        .collect();
    json!({
        "view_set": VIEW_SET,
        "renderer": {
            "name": "review_pictures",
            "version": env!("CARGO_PKG_VERSION"),
            "bevy": BEVY,
            "graphics_card": adapter.name,
            "backend": adapter.backend.to_string(),
            "driver": format!("{} {}", adapter.driver, adapter.driver_info).trim(),
        },
        "picture_size": [PICTURE_SIZE.0, PICTURE_SIZE.1],
        "size": tidy(job.size),
        "closest_viewing_distance": tidy(job.closest),
        "meshes": placed.meshes,
        "scale_factor": tidy(placed.placing.scale),
        "extent": list(placed.placing.extent),
        "views": views,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn parse(args: &[&str]) -> Result<Arguments, String> {
        arguments(&args.iter().map(|arg| arg.to_string()).collect::<Vec<_>>())
    }

    #[test]
    fn the_bevy_named_in_the_report_is_the_one_the_workspace_pins() {
        let workspace = include_str!("../../../../Cargo.toml");
        assert!(workspace.contains(&format!("bevy = {{ version = \"={BEVY}\"")), "BEVY is not the pinned version");
    }

    #[test]
    fn arguments_are_read_in_any_order() {
        let here = env!("CARGO_MANIFEST_DIR");
        let file = format!("{here}/Cargo.toml");
        let args = parse(&["--out", "pictures", &file, "--closest", "0.5", "--size", "0.8"]).unwrap();
        assert_eq!((args.size, args.closest, args.out), (0.8, 0.5, PathBuf::from("pictures")));
        assert!(args.glb.is_absolute());
    }

    #[test]
    fn arguments_that_cannot_be_used_are_refused_with_the_reason() {
        let file = format!("{}/Cargo.toml", env!("CARGO_MANIFEST_DIR"));
        for (args, reason) in [
            (vec!["--size", "0.8", "--closest", "0.5", "--out", "p"], "no model file"),
            (vec!["missing.glb", "--size", "0.8", "--closest", "0.5", "--out", "p"], "cannot open missing.glb"),
            (vec![&file, "--closest", "0.5", "--out", "p"], "--size was not given"),
            (vec![&file, "--size", "0.8", "--out", "p"], "--closest was not given"),
            (vec![&file, "--size", "0.8", "--closest", "0.5"], "--out was not given"),
            (vec![&file, "--size", "0", "--closest", "0.5", "--out", "p"], "above zero"),
            (vec![&file, "--size", "nan", "--closest", "0.5", "--out", "p"], "above zero"),
            (vec![&file, "--size", "0.8", "--closest", "-1", "--out", "p"], "above zero"),
            (vec![&file, "--size"], "--size needs a value"),
            (vec![&file, "--turntable"], "no option --turntable"),
            (vec![&file, &file], "one model file only"),
        ] {
            let error = parse(&args).err().unwrap_or_else(|| panic!("{args:?} was accepted"));
            assert!(error.contains(reason), "{args:?}: {error}");
        }
    }
}
