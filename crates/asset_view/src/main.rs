//! Shows one `.glb` in a window, on a ground plane, under a slow turntable. The camera frames
//! the model by its bounding box, and the model reloads whenever the file changes on disk.
//!
//! Usage: asset_view <asset.glb>

use bevy::{
    asset::UnapprovedPathMode, camera::primitives::Aabb, prelude::*, world_serialization::WorldAsset,
};

const FOV: f32 = std::f32::consts::FRAC_PI_4;
/// Radians per second the camera circles the model.
const TURN_SPEED: f32 = 0.3;
const SUN_TO: Vec3 = Vec3::new(0.4, -1.0, -0.6);
const SUN_LUX: f32 = 8000.0;
const AMBIENT: f32 = 900.0;

#[derive(Resource)]
struct AssetFile(String);

#[derive(Component)]
struct Model;

fn main() -> AppExit {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let [path] = args.as_slice() else {
        eprintln!("usage: asset_view <asset.glb>");
        return AppExit::error();
    };
    let glb = match std::fs::canonicalize(path) {
        Ok(glb) => glb,
        Err(error) => {
            eprintln!("cannot open {path}: {error}");
            return AppExit::error();
        }
    };
    let name = glb.file_name().unwrap().to_string_lossy().into_owned();

    App::new()
        .add_plugins(
            DefaultPlugins
                .set(AssetPlugin {
                    file_path: glb.parent().unwrap().to_string_lossy().into_owned(),
                    unapproved_path_mode: UnapprovedPathMode::Deny,
                    ..default()
                })
                .set(WindowPlugin {
                    primary_window: Some(Window {
                        title: format!("asset_view: {name}"),
                        ..default()
                    }),
                    ..default()
                }),
        )
        .insert_resource(ClearColor(Color::linear_rgb(0.18, 0.19, 0.21)))
        .insert_resource(GlobalAmbientLight {
            brightness: AMBIENT,
            ..default()
        })
        .insert_resource(AssetFile(name))
        .add_systems(Startup, setup)
        .add_systems(Update, frame_model)
        .run()
}

fn setup(
    mut commands: Commands,
    file: Res<AssetFile>,
    asset_server: Res<AssetServer>,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
) {
    let scene: Handle<WorldAsset> = asset_server.load(GltfAssetLabel::Scene(0).from_asset(file.0.clone()));
    commands.spawn((Model, WorldAssetRoot(scene)));

    // Ground, so the model's contact with it and its cast shadow are visible.
    commands.spawn((
        Mesh3d(meshes.add(Plane3d::default().mesh().size(200.0, 200.0))),
        MeshMaterial3d(materials.add(StandardMaterial {
            base_color: Color::linear_rgb(0.12, 0.125, 0.135),
            perceptual_roughness: 1.0,
            // Behind the model's own faces where they meet the ground, so the model wins the tie.
            depth_bias: -4.0,
            ..default()
        })),
    ));
    commands.spawn((
        DirectionalLight {
            illuminance: SUN_LUX,
            shadow_maps_enabled: true,
            ..default()
        },
        Transform::default().looking_to(SUN_TO, Vec3::Y),
    ));
    commands.spawn((
        Camera3d::default(),
        Projection::Perspective(PerspectiveProjection { fov: FOV, ..default() }),
        Transform::from_xyz(3.0, 2.0, 3.0).looking_at(Vec3::ZERO, Vec3::Y),
    ));
}

/// Circles the camera round the middle of the model's bounding box, far enough back to hold all
/// of it. The box is taken from the loaded scene every frame, so a reload is framed too.
fn frame_model(
    time: Res<Time>,
    model: Single<Entity, With<Model>>,
    children: Query<&Children>,
    meshes: Query<(&Aabb, &GlobalTransform)>,
    mut camera: Single<&mut Transform, With<Camera3d>>,
) {
    let (mut min, mut max) = (Vec3::MAX, Vec3::MIN);
    for entity in children.iter_descendants(*model) {
        let Ok((aabb, to_world)) = meshes.get(entity) else { continue };
        let (centre, half) = (Vec3::from(aabb.center), Vec3::from(aabb.half_extents));
        for corner in 0..8 {
            let sign = |bit: u32| if corner & bit == 0 { -1.0 } else { 1.0 };
            let point = centre + half * Vec3::new(sign(1), sign(2), sign(4));
            let point = to_world.transform_point(point);
            min = min.min(point);
            max = max.max(point);
        }
    }
    if min.x > max.x {
        return; // nothing loaded yet
    }
    let centre = (min + max) / 2.0;
    let radius = ((max - min).length() / 2.0).max(0.01);
    let distance = radius / (FOV / 2.0).sin() * 1.1;
    let turn = Quat::from_rotation_y(time.elapsed_secs() * TURN_SPEED);
    let direction = turn * Vec3::new(1.0, 0.7, 1.0).normalize();
    **camera = Transform::from_translation(centre + direction * distance).looking_at(centre, Vec3::Y);
}
