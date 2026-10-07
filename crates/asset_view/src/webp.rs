//! Lets Bevy's glTF loader read a `.glb` whose textures use `EXT_texture_webp`.
//!
//! Bevy decodes WebP images but does not read the extension: a texture that has only
//! `extensions.EXT_texture_webp.source` has no plain `source`, and the extension is listed as
//! required, so the file is refused. [`use_webp_sources`] rewrites the file's JSON chunk so each such
//! texture points at its WebP image through the plain `source`, and drops the requirement.
//! [`WebpGlbLoader`] does that to the bytes of every glTF file and hands them to Bevy's own loader.

use std::borrow::Cow;

use bevy::{
    asset::{AssetLoader, LoadContext, io::Reader},
    gltf::{
        DefaultGltfImageSampler, Gltf, GltfError, GltfLoader, GltfLoaderSettings, GltfMaterial,
        GltfMesh, GltfNode, GltfPlugin, GltfPrimitive, GltfSkin, GltfSkinnedMeshBoundsPolicy,
        convert_coordinates::GltfConvertCoordinates,
        extensions::GltfExtensionHandlers,
    },
    image::CompressedImageFormatSupport,
    prelude::*,
};
use serde_json::Value;

const EXTENSION: &str = "EXT_texture_webp";
const MAGIC: &[u8; 4] = b"glTF";
const JSON_CHUNK: u32 = 0x4E4F_534A;
const HEADER: usize = 12;

/// Takes the place of Bevy's `GltfPlugin` (disable that one in `DefaultPlugins`): the same assets
/// and resources, with [`WebpGlbLoader`] as the loader for `.gltf` and `.glb`. Add it after
/// `DefaultPlugins`, in the place `GltfPlugin` had (before `PbrPlugin`, which adds to the glTF
/// extension handlers, and after `RenderPlugin`, which says which compressed formats the GPU reads).
pub struct WebpGlbPlugin;

impl Plugin for WebpGlbPlugin {
    fn build(&self, app: &mut App) {
        app.init_asset::<Gltf>()
            .init_asset::<GltfNode>()
            .init_asset::<GltfPrimitive>()
            .init_asset::<GltfMesh>()
            .init_asset::<GltfSkin>()
            .init_asset::<GltfMaterial>()
            .preregister_asset_loader::<WebpGlbLoader>(&["gltf", "glb"])
            .init_resource::<GltfExtensionHandlers>();
    }

    fn finish(&self, app: &mut App) {
        let sampler = DefaultGltfImageSampler::new(&GltfPlugin::default().default_sampler);
        let world = app.world();
        let loader = GltfLoader {
            supported_compressed_formats: world
                .get_resource::<CompressedImageFormatSupport>()
                .map(|support| support.0)
                .unwrap_or_default(),
            custom_vertex_attributes: Default::default(),
            default_sampler: sampler.get_internal(),
            default_convert_coordinates: GltfConvertCoordinates::default(),
            extensions: world.resource::<GltfExtensionHandlers>().0.clone(),
            default_skinned_mesh_bounds_policy: GltfSkinnedMeshBoundsPolicy::default(),
        };
        app.insert_resource(sampler)
            .register_asset_loader(WebpGlbLoader(loader));
    }
}

#[derive(TypePath)]
pub struct WebpGlbLoader(GltfLoader);

impl AssetLoader for WebpGlbLoader {
    type Asset = Gltf;
    type Settings = GltfLoaderSettings;
    type Error = GltfError;

    async fn load(
        &self,
        reader: &mut dyn Reader,
        settings: &GltfLoaderSettings,
        load_context: &mut LoadContext<'_>,
    ) -> Result<Gltf, GltfError> {
        let mut bytes = Vec::new();
        reader.read_to_end(&mut bytes).await?;
        let bytes = use_webp_sources(&bytes);
        GltfLoader::load_gltf(&self.0, &bytes, load_context, settings).await
    }

    fn extensions(&self) -> &[&str] {
        &["gltf", "glb"]
    }
}

/// The same `.glb` with every texture that has an `EXT_texture_webp` source using it as its plain
/// `source`, and the extension no longer listed as used or required. A file that does not use the
/// extension, or that is not a well-formed `.glb`, is returned as it is, for Bevy to load or refuse.
pub fn use_webp_sources(glb: &[u8]) -> Cow<'_, [u8]> {
    rewrite(glb).map_or(Cow::Borrowed(glb), Cow::Owned)
}

fn rewrite(glb: &[u8]) -> Option<Vec<u8>> {
    let word = |at: usize| Some(u32::from_le_bytes(glb.get(at..at + 4)?.try_into().ok()?));
    if glb.get(..4)? != MAGIC || word(HEADER + 4)? != JSON_CHUNK {
        return None;
    }
    let json_end = HEADER + 8 + word(HEADER)? as usize;
    let mut json: Value = serde_json::from_slice(glb.get(HEADER + 8..json_end)?).ok()?;

    let mut changed = false;
    for texture in json.get_mut("textures")?.as_array_mut()? {
        let source = texture.pointer(&format!("/extensions/{EXTENSION}/source")).cloned();
        if let Some(source) = source.filter(Value::is_u64) {
            texture["source"] = source;
            changed = true;
        }
    }
    if !changed {
        return None;
    }
    for list in ["extensionsUsed", "extensionsRequired"] {
        if let Some(names) = json.get_mut(list).and_then(Value::as_array_mut) {
            names.retain(|name| name != EXTENSION);
        }
        if json[list].as_array().is_some_and(Vec::is_empty) {
            json.as_object_mut()?.remove(list);
        }
    }

    let mut text = serde_json::to_vec(&json).ok()?;
    text.resize(text.len().next_multiple_of(4), b' ');
    let mut out = Vec::with_capacity(glb.len() + text.len());
    out.extend_from_slice(&glb[..HEADER]);
    out.extend_from_slice(&(text.len() as u32).to_le_bytes());
    out.extend_from_slice(&JSON_CHUNK.to_le_bytes());
    out.extend_from_slice(&text);
    out.extend_from_slice(&glb[json_end..]);
    let total = out.len() as u32;
    out[8..12].copy_from_slice(&total.to_le_bytes());
    Some(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A `.glb` with this JSON text and a small binary chunk after it.
    fn glb(json: &str) -> Vec<u8> {
        let mut text = json.as_bytes().to_vec();
        text.resize(text.len().next_multiple_of(4), b' ');
        let binary = [1u8, 2, 3, 4, 5, 6, 7, 8];
        let mut out = b"glTF".to_vec();
        out.extend_from_slice(&2u32.to_le_bytes());
        out.extend_from_slice(&((HEADER + 8 + text.len() + 8 + binary.len()) as u32).to_le_bytes());
        out.extend_from_slice(&(text.len() as u32).to_le_bytes());
        out.extend_from_slice(&JSON_CHUNK.to_le_bytes());
        out.extend_from_slice(&text);
        out.extend_from_slice(&(binary.len() as u32).to_le_bytes());
        out.extend_from_slice(&0x004E_4942u32.to_le_bytes());
        out.extend_from_slice(&binary);
        out
    }

    fn json_of(glb: &[u8]) -> Value {
        let length = u32::from_le_bytes(glb[12..16].try_into().unwrap()) as usize;
        serde_json::from_slice(&glb[20..20 + length]).unwrap()
    }

    const WEBP_ONLY: &str = r#"{"asset":{"version":"2.0"},"extensionsUsed":["EXT_texture_webp"],
        "extensionsRequired":["EXT_texture_webp"],
        "textures":[{"extensions":{"EXT_texture_webp":{"source":1}},"sampler":0}],
        "images":[{"mimeType":"image/png"},{"mimeType":"image/webp"}]}"#;

    #[test]
    fn a_file_without_the_extension_is_unchanged() {
        let plain = glb(r#"{"asset":{"version":"2.0"},"textures":[{"source":0}],"images":[{}]}"#);
        assert!(matches!(use_webp_sources(&plain), Cow::Borrowed(_)));
        assert_eq!(use_webp_sources(&plain), plain.as_slice());
    }

    #[test]
    fn something_that_is_not_a_glb_is_unchanged() {
        for bytes in [&b""[..], b"glTF", b"{\"asset\":{}}", &glb("not json")] {
            assert_eq!(use_webp_sources(bytes), bytes);
        }
    }

    #[test]
    fn a_webp_only_texture_gets_its_source_and_the_requirement_goes() {
        let before = glb(WEBP_ONLY);
        let after = use_webp_sources(&before).into_owned();
        let json = json_of(&after);
        assert_eq!(json["textures"][0]["source"], 1);
        assert_eq!(json["textures"][0]["sampler"], 0);
        assert!(json.get("extensionsRequired").is_none());
        assert!(json.get("extensionsUsed").is_none());
        assert_eq!(json["images"][1]["mimeType"], "image/webp");
    }

    #[test]
    fn the_webp_source_wins_over_a_fallback_and_other_extensions_stay() {
        let both = glb(
            r#"{"asset":{"version":"2.0"},"extensionsUsed":["KHR_a","EXT_texture_webp"],
            "extensionsRequired":["EXT_texture_webp","KHR_b"],
            "textures":[{"source":0,"extensions":{"EXT_texture_webp":{"source":1}}},{"source":0}]}"#,
        );
        let json = json_of(&use_webp_sources(&both));
        assert_eq!(json["textures"][0]["source"], 1);
        assert_eq!(json["textures"][1]["source"], 0);
        assert_eq!(json["extensionsUsed"], serde_json::json!(["KHR_a"]));
        assert_eq!(json["extensionsRequired"], serde_json::json!(["KHR_b"]));
    }

    #[test]
    fn the_result_is_a_well_formed_glb() {
        let before = glb(WEBP_ONLY);
        let after = use_webp_sources(&before).into_owned();
        assert_eq!(&after[..8], &before[..8]);
        assert_eq!(u32::from_le_bytes(after[8..12].try_into().unwrap()) as usize, after.len());
        let json_length = u32::from_le_bytes(after[12..16].try_into().unwrap()) as usize;
        assert_eq!(json_length % 4, 0);
        assert_eq!(&after[16..20], &JSON_CHUNK.to_le_bytes());
        // The binary chunk after the JSON is carried over untouched.
        assert_eq!(&after[20 + json_length..], &before[before.len() - 16..]);
        // Padding is spaces.
        let text = &after[20..20 + json_length];
        assert!(text.ends_with(b"}") || text.ends_with(b" "));
        assert!(serde_json::from_slice::<Value>(text).is_ok());
    }
}
