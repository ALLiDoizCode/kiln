//! What the viewer and the review pictures share, so that a picture shows what the viewer shows:
//! the background, the ground, the light, how a model file is loaded, and its bounding box.

use bevy::{
    asset::UnapprovedPathMode, gltf::GltfPlugin, mesh::VertexAttributeValues, pbr::PbrPlugin, prelude::*,
    world_serialization::WorldAsset,
};
use std::path::Path;

use crate::webp::WebpGlbPlugin;

/// The direction the sunlight travels: down, from the front left of the model.
pub const SUN_TO: Vec3 = Vec3::new(0.4, -1.0, -0.6);
/// How strong the sun and the light from all sides are. Set by looking: with Bevy's default
/// exposure a pale model keeps its shading, and its shaded side can still be read.
pub const SUN_LUX: f32 = 3000.0;
pub const AMBIENT: f32 = 600.0;
pub const BACKGROUND: Color = Color::linear_rgb(0.18, 0.19, 0.21);
pub const GROUND: Color = Color::linear_rgb(0.12, 0.125, 0.135);

/// The entity the model's scene hangs from.
#[derive(Component)]
pub struct Model;

/// Bevy's default plugins with the glTF loader that reads WebP textures, and with assets read
/// from the folder that holds the model file. With `hot_reload` the model is loaded again
/// whenever its file changes. Each program then sets its own window, or none.
pub fn plugins(glb: &Path, hot_reload: bool) -> bevy::app::PluginGroupBuilder {
    DefaultPlugins.build().disable::<GltfPlugin>().add_before::<PbrPlugin>(WebpGlbPlugin).set(AssetPlugin {
        file_path: glb.parent().unwrap().to_string_lossy().into_owned(),
        unapproved_path_mode: UnapprovedPathMode::Deny,
        watch_for_changes_override: Some(hot_reload),
        ..default()
    })
}

/// Sets the background and the light that comes from all sides.
pub fn light_the_world(app: &mut App) {
    app.insert_resource(ClearColor(BACKGROUND)).insert_resource(GlobalAmbientLight { brightness: AMBIENT, ..default() });
}

/// Spawns the model (its file name within the asset folder), the ground and the sun.
/// Returns the handle of the model's scene, to ask whether it has loaded.
pub fn spawn_scene(
    commands: &mut Commands,
    asset_server: &AssetServer,
    meshes: &mut Assets<Mesh>,
    materials: &mut Assets<StandardMaterial>,
    file_name: &str,
) -> Handle<WorldAsset> {
    let scene: Handle<WorldAsset> = asset_server.load(GltfAssetLabel::Scene(0).from_asset(file_name.to_owned()));
    commands.spawn((Model, WorldAssetRoot(scene.clone())));

    // Ground, so the model's contact with it and its cast shadow are visible.
    commands.spawn((
        Mesh3d(meshes.add(Plane3d::default().mesh().size(200.0, 200.0))),
        MeshMaterial3d(materials.add(StandardMaterial {
            base_color: GROUND,
            perceptual_roughness: 1.0,
            // Behind the model's own faces where they meet the ground, so the model wins the tie.
            depth_bias: -4.0,
            ..default()
        })),
    ));
    commands.spawn((
        DirectionalLight { illuminance: SUN_LUX, shadow_maps_enabled: true, ..default() },
        Transform::default().looking_to(SUN_TO, Vec3::Y),
    ));
    scene
}

/// The lowest and highest corner of the box that holds every vertex of every mesh under `model`,
/// where the scene now places them, and how many meshes that was. `None` until a mesh is there.
pub fn vertex_box(
    model: Entity,
    children: &Query<&Children>,
    placed: &Query<(&Mesh3d, &GlobalTransform)>,
    meshes: &Assets<Mesh>,
) -> Option<(Vec3, Vec3, usize)> {
    let (mut min, mut max, mut count) = (Vec3::MAX, Vec3::MIN, 0);
    for entity in children.iter_descendants(model) {
        let Ok((mesh, to_world)) = placed.get(entity) else { continue };
        let Some(VertexAttributeValues::Float32x3(positions)) =
            meshes.get(&mesh.0).and_then(|mesh| mesh.attribute(Mesh::ATTRIBUTE_POSITION))
        else {
            continue;
        };
        for position in positions {
            let point = to_world.transform_point(Vec3::from(*position));
            min = min.min(point);
            max = max.max(point);
        }
        count += 1;
    }
    (count > 0 && min.cmple(max).all()).then_some((min, max, count))
}
