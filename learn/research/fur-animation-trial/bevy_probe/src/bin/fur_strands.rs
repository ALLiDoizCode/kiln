//! Strand fur on the creature: thousands of separate hairs that sway in wind, hang behind the
//! body when it moves, and travel along one scale of agitation: combed, ruffled, rough, hackles
//! up, and at the top long quills. A throwaway for the "Strand fur" section of
//! `learn/research/fur-animation-trial.md`.
//!
//! fur_strands [model.glb] [--body N] [--light N] [--calm N] [--hairs N] [--keys "B,D,S"] [--out <folder>]
//!             [--hdr 0|1] [--rt 0|1] [--proxy N] [--window WxH]
//! fur_strands --check --out <folder>      no window: three moments in two lightings, each as LDR
//!                                         and HDR, rasterized and ray traced, and contact sheets
//! fur_strands --check --strip --out <folder>   no window: the pictures of the third version
//! fur_strands --bench [--lights | --looks]     window, vsync off: frame times at every hair count
//!                                         and in every lighting; with --lights the lightings only;
//!                                         with --looks LDR and HDR, rasterized and ray traced
//!
//! K switches the camera between a plain LDR picture and the HDR pipeline; P switches the lighting
//! of the body and the ground between Bevy's rasterized lights and its ray tracer, Solari. See
//! `Look`.
//!
//! With no model it shows one of `BODIES`, stepped with N: a body generated without spikes, or
//! `../models/b_pieces_p1_morph.glb` with its `retracted` shape. The hairs are grown when the
//! model has loaded: points spread evenly over the body's surface, each taking the body's colour
//! there. All hairs are one mesh; the vertex shader in `fur_strands.wgsl` bends them every frame.
//!
//! Built with `--features overlay` the keys and the state are drawn in the window.

use std::{
    collections::{HashMap, VecDeque},
    io::Write,
    path::PathBuf,
    sync::{Arc, Mutex},
    time::{Duration, Instant},
};

use asset_view::scene::{self, Model};
use bevy::{
    app::ScheduleRunnerPlugin,
    asset::{RenderAssetUsages, UnapprovedPathMode, uuid_handle},
    camera::{CameraMainTextureUsages, Exposure, Hdr, RenderTarget, visibility::NoFrustumCulling},
    core_pipeline::{
        prepass::{DeferredPrepass, DeferredPrepassDoubleBuffer, DepthPrepass, DepthPrepassDoubleBuffer, MotionVectorPrepass},
        tonemapping::Tonemapping,
    },
    image::{ImageAddressMode, ImageSampler, ImageSamplerDescriptor},
    light::{NotShadowCaster, NotShadowReceiver},
    material::OpaqueRendererMethod,
    math::Affine3A,
    mesh::{Indices, MeshVertexAttribute, MeshVertexBufferLayoutRef, PrimitiveTopology, VertexAttributeValues, morph::MorphWeights},
    pbr::{DefaultOpaqueRendererMethod, DistanceFog, FogFalloff, MaterialPipeline, MaterialPipelineKey},
    post_process::{
        auto_exposure::{AutoExposure, AutoExposurePlugin},
        bloom::Bloom,
    },
    prelude::*,
    reflect::TypePath,
    render::{
        Render, RenderApp, RenderPlugin,
        render_resource::{
            AsBindGroup, Extent3d, RenderPipelineDescriptor, ShaderType, SpecializedMeshPipelineError, TextureDimension, TextureFormat, TextureUsages,
            VertexFormat,
        },
        renderer::{RenderAdapter, RenderDevice, RenderInstance},
        view::{
            screenshot::{Screenshot, save_to_disk},
            window::{ExtractedWindows, create_surfaces},
        },
    },
    anti_alias::taa::TemporalAntiAliasing,
    render::camera::{MipBias, TemporalJitter},
    solari::prelude::{RaytracingMesh3d, SolariLighting, SolariPlugins},
    shader::{Shader, ShaderRef},
    time::TimeUpdateStrategy,
    window::{ExitCondition, MonitorSelection, PresentMode, WindowMode},
    winit::{WinitPlugin, WinitSettings},
};

const FOV: f32 = std::f32::consts::FRAC_PI_4;
const TURN_SPEED: f32 = 0.3;
const CHECK_SIZE: (u32, u32) = (1600, 900);
/// Hair counts asked for with H. The count grown is a little lower: see `grow`.
const PRESETS: [usize; 4] = [10_000, 30_000, 80_000, 200_000];
const DEFAULT_PRESET: usize = 2;
/// A fine hair is a strip of this many pieces along its length; a guard hair, which becomes a
/// quill, has more because it is long.
const FINE_PIECES: usize = 5;
const GUARD_PIECES: usize = 8;
/// Bytes of one vertex of the coat: eight attributes.
const VERTEX_BYTES: f32 = 112.0;
/// Hairs lean toward the tip of the nearest clump; the clumps' middles are about this far apart.
const CLUMP_SPACING: f32 = 0.026;
/// The hair width that covers the body at `PRESETS[2]` hairs; fewer hairs are drawn wider.
const HAIR_WIDTH: f32 = 0.0030;
const QUILL_WIDTH: f32 = 0.012;
/// A part of the model thinner than this is a modelled spike or tuft, and grows no hair.
const THIN: f32 = 0.03;
/// A thin patch of the body smaller than this, in square metres, is flattened onto the body.
const FLATTEN_MOST: f32 = 0.08;
const FLATTEN_RINGS: usize = 0;
/// The least width a hair is drawn, in pixels of the picture.
const LEAST_PIXELS: f32 = 0.75;
/// The same while ray tracing, when a pixel has one sample and not four: a hair thinner than
/// this misses pixels altogether and the body shows through the coat as dark specks.
const LEAST_PIXELS_RT: f32 = 1.3;
/// The way the wind blows: across the creature from its right and toward its tail, so the gusts
/// cross its back as bands, the near flank lifts, and the coat streams off the rump and the tail.
const WIND_TO: Vec3 = Vec3::new(0.75, 0.0, -0.66);
const WIND_DEFAULT: f32 = 1.0;
const WIND_MOST: f32 = 4.0;
/// How rough the coat is at the calm end of the scale, stepped with F: the name and the number
/// the shader gets. The scale runs from there to the same spikes.
const CALM: [(&str, f32); 3] = [("combed", 0.0), ("sleek", 0.2), ("tousled", 0.42)];
const DEFAULT_CALM: usize = 0;
/// The named places on the scale of agitation, keys 1 to 5.
const STAGES: [(&str, f32); 5] = [("combed", 0.0), ("ruffled", 0.3), ("rough", 0.5), ("hackles", 0.7), ("spikes", 1.0)];
/// A change of agitation takes this long to travel the length of the body.
const SWEEP_SECONDS: f32 = 1.6;
/// Seconds B takes over the whole scale, up and down, and a number key takes to its stage.
const RUN_UP_SECONDS: f32 = 5.0;
const RUN_DOWN_SECONDS: f32 = 6.0;
const JUMP_SECONDS: f32 = 1.0;
/// The most a jolt of the body adds to the coat's agitation for a moment.
const STARTLE_MOST: f32 = 0.2;
const LEAN_DEFAULT: f32 = 1.0;
const DEFAULT_MOOD: usize = 1;
/// The bodies fur can be grown on, stepped with N: a short name, and the file from this
/// program's folder. The first has modelled spikes, shrunk into it by its `retracted` shape; the
/// other two were generated without spikes.
const BODIES: [(&str, &str); 3] = [
    ("p1_retracted", "/../models/b_pieces_p1_morph.glb"),
    ("smooth_midpoly", "/../../tripo-api-trial/models/orb_smooth_midpoly_h31_req10000.glb"),
    ("smooth_lowpoly", "/../../tripo-api-trial/models/orb_smooth_lowpoly_h31_req5000.glb"),
];
const DEFAULT_BODY: usize = 1;
const GUST_SPEED: f32 = 0.9;
const GUST_SECONDS: f32 = 1.6;
/// The auto-loop, in seconds from its start: what happens when, and when it starts again.
const LOOP: [(f32, Action); 12] = [
    (0.0, Action::Wind(0.5)),
    (0.0, Action::AgitateTo(0.0, 1.0)),
    // The wind rises and the coat ruffles.
    (3.0, Action::Wind(2.0)),
    (3.0, Action::AgitateTo(0.22, 3.0)),
    (6.5, Action::Gust),
    (9.5, Action::Dash),
    // Slowly up through ruffled, rough and hackles.
    (14.0, Action::AgitateTo(0.76, 10.0)),
    // The spikes sweep forward from the tail.
    (24.5, Action::AgitateTo(1.0, 1.0)),
    // Held; then back down through every stage.
    (29.5, Action::AgitateTo(0.0, 9.0)),
    (31.0, Action::Wind(1.0)),
    (36.0, Action::Wind(0.5)),
    (39.0, Action::Shake),
];
const LOOP_PERIOD: f32 = 42.0;
const KEYS: &str = "Up, Down: agitation by hand | B run the scale to spikes, or back to combed | 1 combed, 2 ruffled, 3 rough, 4 hackles, 5 spikes | F the calm coat: combed, sleek, tousled | Q quill lean: forward, outward, rearward | , . less or more lean | V the change travels: tail to head, or neck to tail | N next body | L lighting | W wind | [ ] wind strength, up to a gale | G gust | D dash | S shake | H hair count | C fur shadows | X show: each hair's agitation, the guard hairs, nothing | K picture: HDR pipeline, or plain LDR | M tone mapper | - = exposure, half a stop | E auto exposure (HDR) | O HDR on the screen itself: why not | P lighting of body and ground: rasterized, or ray traced | J ray traced: what stands in for the coat | I ray traced: blend frames to smooth the grain, or not | T turntable | R reset camera | Space pause the loop | Esc quit";

/// The tone mappers M steps through: how light brighter than the screen can show is brought into
/// what it can. The first does nothing and everything over the top is cut off.
const TONEMAPPERS: [(&str, Tonemapping); 8] = [
    ("none", Tonemapping::None),
    ("Reinhard", Tonemapping::Reinhard),
    ("Reinhard luminance", Tonemapping::ReinhardLuminance),
    ("ACES fitted", Tonemapping::AcesFitted),
    ("AgX", Tonemapping::AgX),
    ("SomewhatBoringDisplayTransform", Tonemapping::SomewhatBoringDisplayTransform),
    ("TonyMcMapface", Tonemapping::TonyMcMapface),
    ("Blender filmic", Tonemapping::BlenderFilmic),
];
/// The tone mapper each picture starts with: LDR none, HDR the one the lightings had before.
const START_TONEMAPPER: [usize; 2] = [0, 3];
/// Bevy's exposure when nothing is said: EV100 9.7.
const EV100: f32 = 9.7;
/// What stands in for the coat in the ray tracer's scene, stepped with J: a name, whether the
/// guard hairs are in it, and one fine hair in how many (0 for none). The ray tracer cannot see
/// the real coat: see `proxy_coat`.
const PROXIES: [(&str, bool, usize); 4] = [("nothing", false, 0), ("the guard hairs", true, 0), ("the guard hairs and one fine hair in 8", true, 8), ("every hair", true, 1)];
const START_PROXY: usize = 2;
/// A fine hair that stands for several is this many times as wide.
const PROXY_WIDER: f32 = 4.0;
/// Frames the ray tracer is given to settle before a picture of `--check` is taken.
const RT_SETTLE_FRAMES: u32 = 150;

/// How the picture is made, apart from the lighting chosen with L.
///
/// `hdr`, key K. On: the camera draws into a 16-bit float picture where light can be any
/// brightness, bloom spreads the brightest parts, and a tone mapper brings it into what the screen
/// shows. Off: the camera draws straight into the 8-bit picture, there is no bloom, and with the
/// tone mapper at "none" anything brighter than white is cut off.
///
/// `rt`, key P. On: the body and the ground are lit by Bevy's ray tracer, Solari, which needs the
/// 16-bit picture whatever K says and one sample a pixel. The fur stays as it is.
#[derive(Resource)]
struct Look {
    hdr: bool,
    /// The window's surface is scRGB (`--display-hdr`, the build of `scrgb/build.sh` only): what
    /// the HDR picture holds above white goes to the screen as it is.
    display_hdr: bool,
    /// Until K or M is pressed or `--hdr` is given, the picture is what each lighting had before
    /// there was a K: the studio lighting LDR with Bevy's own tone mapper, the others HDR.
    untouched: bool,
    rt: bool,
    /// Why ray tracing cannot run here; `None` when it can, or before the graphics card was asked.
    rt_blocked: Option<String>,
    rt_asked: bool,
    /// Which of `TONEMAPPERS`, for the LDR picture and for the HDR one.
    tonemapper: [usize; 2],
    /// Stops brighter than Bevy's exposure.
    stops: f32,
    auto_exposure: bool,
    /// Which of `PROXIES`.
    proxy: usize,
    /// Ray traced only: each frame is blended with the ones before it (Bevy's TAA), which takes
    /// most of the ray tracer's grain away and smears whatever moves without saying how.
    blend_frames: bool,
    /// What the window's surface offers and what the monitors are set to; why the screen gets an
    /// SDR signal. Said when O is pressed.
    display: String,
    /// The last thing a key had to say, and when by the real clock.
    said: String,
    said_at: f32,
    /// Milliseconds the stand-in for the coat took to work out this frame, and its triangles.
    proxy_ms: f32,
    proxy_triangles: usize,
}

impl Look {
    fn ray_traced(&self) -> bool {
        self.rt && self.rt_blocked.is_none() && self.rt_asked
    }
    /// The picture is 16-bit float: asked for, or needed by the ray tracer.
    fn float_picture(&self) -> bool {
        self.hdr || self.ray_traced()
    }
}

/// What the render world found out about the window's surface, for the main world to read.
#[derive(Resource, Clone, Default)]
struct SurfaceFound(Arc<Mutex<Option<String>>>);

/// On what the ray tracer's scene holds besides the body and the ground.
#[derive(Component)]
struct RtOnly;
/// The stand-in for the sky's light: a dome that glows.
#[derive(Component)]
struct RtSky;
/// The stand-in for the lamp: a small ball that glows.
#[derive(Component)]
struct RtLamp(Handle<StandardMaterial>);
/// The stand-in for the coat.
#[derive(Component)]
struct RtProxy;
/// On a mesh of the body or the ground that has been given to the ray tracer.
#[derive(Component)]
struct RtGiven;

const FUR_SHADER: Handle<Shader> = uuid_handle!("5b7f0f0e-6d0c-4f0a-9a57-2d1c3e8a9b41");
const HAZE_SHADER: Handle<Shader> = uuid_handle!("5b7f0f0e-6d0c-4f0a-9a57-2d1c3e8a9b42");

/// The fog over the ray-traced ground: see `fur_haze.wgsl`.
#[derive(Asset, TypePath, AsBindGroup, Clone, Default)]
struct HazeMaterial {}

impl Material for HazeMaterial {
    fn fragment_shader() -> ShaderRef {
        HAZE_SHADER.into()
    }
    fn alpha_mode(&self) -> AlphaMode {
        AlphaMode::Premultiplied
    }
}

#[derive(Component)]
struct Haze;
const ATTRIBUTE_COMB: MeshVertexAttribute = MeshVertexAttribute::new("FurComb", 0x6675_7200_0001, VertexFormat::Float32x4);
const ATTRIBUTE_RAND: MeshVertexAttribute = MeshVertexAttribute::new("FurRand", 0x6675_7200_0002, VertexFormat::Float32x4);
const ATTRIBUTE_TINT: MeshVertexAttribute = MeshVertexAttribute::new("FurTint", 0x6675_7200_0003, VertexFormat::Float32x4);
const ATTRIBUTE_CLUMP: MeshVertexAttribute = MeshVertexAttribute::new("FurClump", 0x6675_7200_0004, VertexFormat::Float32x4);
const ATTRIBUTE_MORE: MeshVertexAttribute = MeshVertexAttribute::new("FurMore", 0x6675_7200_0005, VertexFormat::Float32x4);

/// Which way the quills lean along the body when they stand.
#[derive(Clone, Copy, PartialEq, Debug)]
enum Lean {
    Forward,
    Outward,
    Rearward,
}

/// One lighting: the lights, the air and the ground. Directions are where the light comes from.
struct Mood {
    name: &'static str,
    /// The first version's look: the viewer's own light, flat background and grey ground.
    plain: bool,
    sun_from: Vec3,
    sun: [f32; 3],
    sun_lux: f32,
    /// The light from behind the creature, which casts no shadow, and how strongly the fur's
    /// edge and the quills catch it in the fur shader.
    back_from: Vec3,
    back: [f32; 3],
    back_lux: f32,
    rim: f32,
    ambient: [f32; 3],
    ambient_brightness: f32,
    sky_top: [f32; 3],
    sky_horizon: [f32; 3],
    /// Added to the sky low down in the direction of the sun.
    sky_glow: [f32; 3],
    fog_density: f32,
    ground: [f32; 3],
    /// A warm lamp low at the creature's side, in lumens; it flickers. 0 for none.
    lamp: f32,
    /// The share of the sun that slow clouds take away and give back.
    drift: f32,
    bloom: f32,
}

const MOODS: [Mood; 4] = [
    Mood {
        name: "studio (the first version)",
        plain: true,
        sun_from: Vec3::new(-0.4, 1.0, 0.6),
        sun: [1.0, 1.0, 1.0],
        sun_lux: scene::SUN_LUX,
        back_from: Vec3::Y,
        back: [0.0, 0.0, 0.0],
        back_lux: 0.0,
        rim: 0.0,
        ambient: [1.0, 1.0, 1.0],
        ambient_brightness: scene::AMBIENT,
        sky_top: [0.0; 3],
        sky_horizon: [0.0; 3],
        sky_glow: [0.0; 3],
        fog_density: 0.0,
        ground: [1.0; 3],
        lamp: 0.0,
        drift: 0.0,
        bloom: 0.0,
    },
    // A low warm sun from ahead of the creature, long shadows, a cool light from behind it,
    // haze, and a glow on the horizon under the sun.
    Mood {
        name: "dusk",
        plain: false,
        sun_from: Vec3::new(0.25, 0.27, 1.0),
        sun: [1.0, 0.56, 0.27],
        sun_lux: 5200.0,
        back_from: Vec3::new(-0.8, 0.5, -0.55),
        back: [0.45, 0.62, 1.0],
        back_lux: 1500.0,
        rim: 0.9,
        ambient: [0.42, 0.50, 0.85],
        ambient_brightness: 200.0,
        sky_top: [0.008, 0.012, 0.04],
        sky_horizon: [0.085, 0.06, 0.08],
        sky_glow: [0.75, 0.24, 0.07],
        fog_density: 0.060,
        ground: [0.36, 0.33, 0.33],
        lamp: 0.0,
        drift: 0.22,
        bloom: 0.16,
    },
    // No sky: a cold shaft from above and behind, a flickering warm lamp to one side, the rest
    // dark.
    Mood {
        name: "cavern",
        plain: false,
        sun_from: Vec3::new(-0.45, 1.0, -0.6),
        sun: [0.60, 0.78, 1.0],
        sun_lux: 3600.0,
        back_from: Vec3::new(-0.45, 1.0, -0.6),
        back: [0.60, 0.78, 1.0],
        back_lux: 0.0,
        rim: 1.1,
        ambient: [0.35, 0.5, 0.7],
        ambient_brightness: 45.0,
        sky_top: [0.002, 0.003, 0.005],
        sky_horizon: [0.012, 0.018, 0.024],
        sky_glow: [0.0, 0.0, 0.0],
        fog_density: 0.085,
        ground: [0.26, 0.28, 0.31],
        lamp: 9000.0,
        drift: 0.0,
        bloom: 0.2,
    },
    // A pale moon from behind and to one side, thick mist, everything blue.
    Mood {
        name: "moonlit mist",
        plain: false,
        sun_from: Vec3::new(-1.0, 0.55, 0.15),
        sun: [0.62, 0.74, 1.0],
        sun_lux: 5200.0,
        back_from: Vec3::new(-1.0, 0.55, 0.15),
        back: [0.62, 0.74, 1.0],
        back_lux: 0.0,
        rim: 1.0,
        ambient: [0.45, 0.58, 0.9],
        ambient_brightness: 420.0,
        sky_top: [0.008, 0.014, 0.03],
        sky_horizon: [0.05, 0.068, 0.095],
        sky_glow: [0.10, 0.13, 0.18],
        fog_density: 0.10,
        ground: [0.24, 0.29, 0.34],
        lamp: 0.0,
        drift: 0.12,
        bloom: 0.2,
    },
];

#[derive(Component)]
struct Sun;
#[derive(Component)]
struct BackLight;
#[derive(Component)]
struct Lamp;
#[derive(Component)]
struct PlainGround;
#[derive(Component)]
struct MoodGround;
/// The sky of one mood: a large ball seen from inside.
#[derive(Component)]
struct Sky(usize);

/// The bodies that are there: a name, and the file's path from the root of the disk, which is
/// where assets are read from.
#[derive(Resource)]
struct Bodies(Vec<(String, String)>);

#[derive(Resource)]
struct Scenery {
    ground: Handle<StandardMaterial>,
}

/// What the shader is told every frame. The fields are described in `fur_strands.wgsl`.
#[derive(ShaderType, Clone, Default)]
struct FurParams {
    wind: Vec4,
    gust: Vec4,
    lag_a: Vec4,
    lag_b: Vec4,
    turn_a: Vec4,
    turn_b: Vec4,
    centre: Vec4,
    spine_a: Vec4,
    spine_b: Vec4,
    quill: Vec4,
    style: Vec4,
    rim_to: Vec4,
    rim_colour: Vec4,
    agitation: Vec4,
    extra: Vec4,
}

#[derive(Asset, TypePath, AsBindGroup, Clone, Default)]
struct FurMaterial {
    #[uniform(0)]
    params: FurParams,
    /// `params` of the frame before.
    #[uniform(1)]
    before: FurParams,
}

impl Material for FurMaterial {
    fn vertex_shader() -> ShaderRef {
        FUR_SHADER.into()
    }
    fn fragment_shader() -> ShaderRef {
        FUR_SHADER.into()
    }
    /// The shadow map is drawn with this, so the shadow is of the hairs where they are now.
    fn prepass_vertex_shader() -> ShaderRef {
        FUR_SHADER.into()
    }
    fn specialize(
        _pipeline: &MaterialPipeline,
        descriptor: &mut RenderPipelineDescriptor,
        layout: &MeshVertexBufferLayoutRef,
        _key: MaterialPipelineKey<Self>,
    ) -> Result<(), SpecializedMeshPipelineError> {
        descriptor.vertex.buffers = vec![layout.0.get_layout(&[
            Mesh::ATTRIBUTE_POSITION.at_shader_location(0),
            Mesh::ATTRIBUTE_NORMAL.at_shader_location(1),
            Mesh::ATTRIBUTE_UV_0.at_shader_location(2),
            ATTRIBUTE_COMB.at_shader_location(3),
            ATTRIBUTE_RAND.at_shader_location(4),
            ATTRIBUTE_TINT.at_shader_location(5),
            ATTRIBUTE_CLUMP.at_shader_location(6),
            ATTRIBUTE_MORE.at_shader_location(7),
        ])?];
        // A strip faces whoever looks at it, from either side.
        descriptor.primitive.cull_mode = None;
        Ok(())
    }
}

/// The body the hairs grow on, read once from the loaded model, in the model's own space.
#[derive(Resource)]
struct Body {
    /// Corner positions, normals and UVs of every triangle with fur on it.
    triangles: Vec<[(Vec3, Vec3, Vec2); 3]>,
    /// The fur-covered area up to and including each triangle, in square metres.
    area_up_to: Vec<f32>,
    image: Option<(u32, u32, Vec<u8>)>,
    factor: [f32; 3],
    min: Vec3,
    max: Vec3,
    /// The height of the top of the back; what is above it is the tail.
    back_top: f32,
    /// The middle of the bare snout, which the fur of the face is combed away from.
    snout: Vec3,
    body_triangles: usize,
    /// The body's material, which the stand-in for the coat borrows in the ray tracer's scene.
    material: Option<Handle<StandardMaterial>>,
}

/// One hair as it was grown: what `grow_coat` gives every vertex of the hair, kept so that the
/// stand-in for the coat can be worked out on the processor. The names are the shader's.
#[derive(Clone, Copy)]
struct Seed {
    root: Vec3,
    normal: Vec3,
    uv: Vec2,
    comb: Vec3,
    soft: f32,
    r1: f32,
    r2: f32,
    delay: f32,
    quill: f32,
    width: f32,
    clump: Vec3,
    clump_random: f32,
    shag: f32,
    tail: f32,
    r3: f32,
    r4: f32,
}

#[derive(Component)]
struct Coat;

#[derive(Resource)]
struct CoatState {
    preset: usize,
    asked: usize,
    hairs: usize,
    quills: usize,
    triangles: usize,
    vertices: usize,
    build_ms: f32,
    entity: Option<Entity>,
    material: Handle<FurMaterial>,
    rebuild: bool,
    shadows: bool,
    shown: bool,
    seeds: Vec<Seed>,
    /// Goes up every time a coat is grown.
    grown: u32,
}

#[derive(Resource)]
struct Show {
    /// Where the coat is on the one scale, 0 combed to 1 spikes; where it is going, and how
    /// fast, a second.
    agitation: f32,
    agitation_target: f32,
    agitation_rate: f32,
    /// What agitation was over the last `SWEEP_SECONDS`, by the show's clock, and from it the
    /// four values along the body the shader gets: a change travels.
    history: VecDeque<(f32, f32)>,
    wave: [f32; 4],
    /// Agitation a jolt of the body has added for a moment.
    startle: f32,
    wind_on: bool,
    wind_strength: f32,
    wind_now: f32,
    gust_began: f32,
    loop_paused: bool,
    loop_clock: f32,
    turntable: bool,
    angle: f32,
    /// What X draws: 0 the coat, 1 each hair's agitation as a colour, 2 the guard hairs tinted.
    debug: u8,
    /// Which of `CALM`, which way the quills lean and how far, whether a change travels from
    /// the tail to the head, and which of `MOODS`.
    calm: usize,
    lean: Lean,
    lean_amount: f32,
    wave_to_head: bool,
    mood: usize,
    /// Which of `Bodies`.
    body: usize,
    /// Seconds of the show's own clock; it starts when the hairs are there.
    clock: f32,
    ready: bool,
}

#[derive(Clone, Copy, PartialEq, Debug)]
enum Action {
    Gust,
    Dash,
    Shake,
    /// Agitation to a value over so many seconds, travelling along the body.
    AgitateTo(f32, f32),
    /// Agitation at once, the whole coat together.
    Agitate(f32),
    /// The rest are settings, changed by `--check` between its pictures.
    Calm(usize),
    Debug(u8),
    Coat(bool),
    LeanTo(Lean),
    WaveToHead(bool),
    Mood(usize),
    Wind(f32),
    Body(usize),
}

/// One damped spring that a body's acceleration pushes, per axis.
#[derive(Clone, Copy, Default)]
struct Spring {
    at: Vec3,
    speed: Vec3,
}

impl Spring {
    fn step(&mut self, push: Vec3, hertz: f32, damping: f32, seconds: f32) {
        let omega = hertz * std::f32::consts::TAU;
        let steps = (seconds / 0.004).ceil().max(1.0);
        let dt = seconds / steps;
        for _ in 0..steps as u32 {
            self.speed += (-omega * omega * self.at - 2.0 * damping * omega * self.speed - push) * dt;
            self.at += self.speed * dt;
        }
    }
}

/// Where the creature is, what it is doing, and how far the fur hangs behind.
#[derive(Resource, Default)]
struct Motion {
    doing: Option<(Action, f32)>,
    place: Vec3,
    speed_along: f32,
    return_from: Vec3,
    yaw: f32,
    roll: f32,
    last_place: Vec3,
    last_turn: Quat,
    velocity: Vec3,
    spin: Vec3,
    steady_velocity: Vec3,
    steady_spin: Vec3,
    lag: [Spring; 2],
    turn: [Spring; 2],
}

/// What the camera looks at and from how far, and where the middle of the body is.
#[derive(Resource, Default)]
struct Framing {
    centre: Vec3,
    radius: f32,
    pivot: Vec3,
    follow: Vec3,
}

#[derive(Component)]
struct View {
    name: &'static str,
    /// The way from the middle of the creature to the camera, and how far as a share of the
    /// framing distance.
    from: Vec3,
    near: f32,
    aim: Vec3,
}

#[derive(Resource)]
struct Out(Option<PathBuf>);

#[derive(Resource, Default)]
struct FrameTimes(VecDeque<f32>);

impl FrameTimes {
    fn mean_ms(&self) -> f32 {
        if self.0.is_empty() { 0.0 } else { self.0.iter().sum::<f32>() / self.0.len() as f32 * 1000.0 }
    }
}

#[derive(Resource, Default)]
struct Status(String);

#[cfg(feature = "overlay")]
#[derive(Component)]
struct Overlay;

/// `--check`: the moments to take a picture of, in seconds of the show's clock.
#[derive(Resource)]
struct Check {
    events: Vec<(f32, Action)>,
    /// When, the picture's name, and which cameras take it.
    shots: Vec<(f32, &'static str, &'static [&'static str])>,
    settle: u32,
    sheets_done: bool,
}

/// `--keys`: keys pressed one after another, as if by hand.
#[derive(Resource)]
struct Script {
    keys: Vec<(String, KeyCode)>,
    next: usize,
    held: Option<KeyCode>,
    since: f32,
}

/// `--bench`: one row of the table per stage.
#[derive(Resource)]
struct Bench {
    stages: Vec<Stage>,
    stage: usize,
    began: Option<Instant>,
    samples: Vec<f32>,
    set: bool,
}

/// One row of the bench: the row's label, hair count preset, agitation, fur shadows, fur shown,
/// which of `MOODS`, and the look: HDR, ray traced, which of `PROXIES`.
#[derive(Clone)]
struct Stage {
    label: String,
    preset: usize,
    agitation: f32,
    shadows: bool,
    shown: bool,
    mood: usize,
    hdr: bool,
    rt: bool,
    proxy: usize,
}

/// `--check`: the same moments in every look, and a contact sheet of each moment.
#[derive(Resource)]
struct Compare {
    /// The look (HDR, ray traced), which of `MOODS`, and which of `MOMENTS`.
    steps: Vec<(bool, bool, usize, usize)>,
    step: usize,
    frames: u32,
    shot: bool,
    looks: Vec<(bool, bool)>,
}

/// The moments of `--check`: a name, agitation, and wind.
const MOMENTS: [(&str, f32, f32); 4] = [("combed", 0.0, 0.4), ("rough", 0.5, 0.4), ("spikes", 1.0, 0.4), ("rough_in_a_gale", 0.5, 3.5)];
const COMPARE_MOODS: [usize; 2] = [1, 2];
const COMPARE_VIEWS: [&str; 2] = ["three_quarter", "close"];

struct Rng(u64);

impl Rng {
    fn next(&mut self) -> f32 {
        // SplitMix64: the same hairs every run.
        self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        ((z ^ (z >> 31)) >> 40) as f32 / (1u64 << 24) as f32
    }
}

fn main() -> AppExit {
    let (mut glb, mut out, mut keys, mut hairs) = (None, None, None, None);
    let (mut check, mut bench, mut vsync, mut lights_only) = (false, false, true, false);
    let (mut strip, mut looks_only, mut hdr, mut rt, mut proxy, mut window_size) = (false, false, None, false, START_PROXY, None);
    let mut display_hdr = false;
    let on_off = |value: Option<&String>| value.and_then(|value| match value.as_str() {
        "0" | "off" => Some(false),
        "1" | "on" => Some(true),
        _ => None,
    });
    let (mut mood, mut calm, mut body) = (DEFAULT_MOOD, DEFAULT_CALM, None);
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut rest = args.iter();
    while let Some(arg) = rest.next() {
        match arg.as_str() {
            "--out" => out = rest.next().map(PathBuf::from),
            "--keys" => keys = rest.next().cloned(),
            "--hairs" => hairs = rest.next().and_then(|n| n.parse::<usize>().ok()),
            "--check" | "--frames" => check = true,
            "--bench" => (bench, vsync) = (true, false),
            "--lights" => lights_only = true,
            "--looks" => looks_only = true,
            "--strip" => strip = true,
            "--display-hdr" => display_hdr = true,
            "--hdr" | "--rt" => match on_off(rest.next()) {
                Some(on) if arg == "--hdr" => hdr = Some(on),
                Some(on) => rt = on,
                None => {
                    eprintln!("{arg} takes 0 or 1");
                    return AppExit::error();
                }
            },
            "--proxy" => match rest.next().and_then(|n| n.parse::<usize>().ok()).filter(|n| *n < PROXIES.len()) {
                Some(n) => proxy = n,
                None => {
                    eprintln!("--proxy takes 0 to {}: {}", PROXIES.len() - 1, PROXIES.map(|proxy| proxy.0).join(", "));
                    return AppExit::error();
                }
            },
            "--window" => match rest.next().and_then(|size| size.split_once('x')).and_then(|(w, h)| Some((w.parse::<u32>().ok()?, h.parse::<u32>().ok()?))) {
                Some(size) => window_size = Some(size),
                None => {
                    eprintln!("--window takes a size in pixels, as 1920x1080");
                    return AppExit::error();
                }
            },
            "--body" => match rest.next().and_then(|name| BODIES.iter().position(|body| body.0 == name).or(name.parse::<usize>().ok().filter(|n| *n < BODIES.len()))) {
                Some(n) => body = Some(n),
                None => {
                    eprintln!("--body takes 0 to {} or a name: {}", BODIES.len() - 1, BODIES.map(|body| body.0).join(", "));
                    return AppExit::error();
                }
            },
            "--light" => match rest.next().and_then(|n| n.parse::<usize>().ok()).filter(|n| *n < MOODS.len()) {
                Some(n) => mood = n,
                None => {
                    eprintln!("--light takes 0 to {}: {}", MOODS.len() - 1, MOODS.map(|mood| mood.name).join(", "));
                    return AppExit::error();
                }
            },
            "--calm" | "--rough" => match rest.next().and_then(|n| n.parse::<usize>().ok()).filter(|n| *n < CALM.len()) {
                Some(n) => calm = n,
                None => {
                    eprintln!("--calm takes 0 to {}: {}", CALM.len() - 1, CALM.map(|calm| calm.0).join(", "));
                    return AppExit::error();
                }
            },
            "--no-vsync" => vsync = false,
            other if other.starts_with("--") => {
                eprintln!("unknown option {other}");
                return AppExit::error();
            }
            _ => glb = Some(arg.clone()),
        }
    }
    if display_hdr && (check || !cfg!(feature = "scrgb")) {
        eprintln!(
            "--display-hdr needs a window and the build that scrgb/build.sh makes (target/release/fur_strands_scrgb): Bevy 0.19.1 as published always opens a window's surface in an 8-bit sRGB format"
        );
        return AppExit::error();
    }
    if display_hdr {
        // The patched bevy_render of `scrgb/build.sh` reads this when it opens the surface.
        // SAFETY: nothing else of this program is running yet.
        unsafe { std::env::set_var("BEVY_SCRGB_SURFACE", "1") };
    }
    if check && out.is_none() {
        eprintln!("usage: fur_strands --check --out <folder>");
        return AppExit::error();
    }
    let script = match keys.map(|keys| parse_keys(&keys)) {
        Some(Err(unknown)) => {
            eprintln!("--keys: no key called {unknown}");
            return AppExit::error();
        }
        Some(Ok(keys)) => Some(keys),
        None => None,
    };
    // The bodies: the one file named, or those of `BODIES` that are there. Assets are read from
    // the root of the disk, because the bodies are in two folders.
    let named = glb.is_some();
    let files: Vec<(String, PathBuf)> = match glb {
        Some(glb) => vec![("the file given".to_string(), PathBuf::from(glb))],
        // `scrgb/build.sh` builds from a scratch folder and says where the probe is.
        None => BODIES.iter().map(|(name, file)| (name.to_string(), PathBuf::from(format!("{}{file}", option_env!("FUR_STRANDS_PROBE_DIR").unwrap_or(env!("CARGO_MANIFEST_DIR")))))).collect(),
    };
    let mut bodies = Vec::new();
    let mut first_body = 0;
    for (index, (name, file)) in files.iter().enumerate() {
        match std::fs::canonicalize(file) {
            Ok(file) => {
                if index == body.unwrap_or(DEFAULT_BODY) {
                    first_body = bodies.len();
                }
                bodies.push((name.clone(), file.to_string_lossy().trim_start_matches('/').to_string()));
            }
            Err(error) if named || body == Some(index) => {
                eprintln!("cannot open {}: {error}", file.display());
                return AppExit::error();
            }
            Err(_) => println!("body {name} is not there: {}", file.display()),
        }
    }
    if bodies.is_empty() {
        eprintln!("no body to grow fur on: run scripts/run_all.sh, or name a model file");
        return AppExit::error();
    }
    if let Some(out) = &out {
        std::fs::create_dir_all(out).unwrap();
    }
    let file_name = bodies[first_body].1.clone();
    let assets_at_root =
        AssetPlugin { file_path: "/".to_string(), unapproved_path_mode: UnapprovedPathMode::Deny, watch_for_changes_override: Some(false), ..default() };

    let mut app = App::new();
    let plugins = scene::plugins(std::path::Path::new("/model.glb"), false).set(assets_at_root);
    let compare = check && !strip;
    if check {
        app.add_plugins(
            plugins
                .set(WindowPlugin { primary_window: None, exit_condition: ExitCondition::DontExit, ..default() })
                .disable::<WinitPlugin>()
                .set(RenderPlugin { synchronous_pipeline_compilation: true, ..default() }),
        )
        .add_plugins(ScheduleRunnerPlugin::run_loop(Duration::ZERO))
        // Every run steps the same sixtieth of a second, so the pictures are the same every run.
        .insert_resource(TimeUpdateStrategy::ManualDuration(Duration::from_secs_f64(1.0 / 60.0)));
        if compare {
            app.insert_resource(Compare { steps: Vec::new(), step: 0, frames: 0, shot: false, looks: Vec::new() })
                .add_systems(Update, compare_run.after(find_body).before(animate));
        } else {
            app.insert_resource(check_plan()).add_systems(Update, check_run.after(find_body).before(animate));
        }
    } else {
        let present_mode = if vsync { PresentMode::AutoVsync } else { PresentMode::AutoNoVsync };
        app.add_plugins(plugins.set(WindowPlugin {
            // The bench takes a whole screen, so every run draws the same number of pixels.
            primary_window: Some(Window {
                title: "fur_strands".to_string(),
                present_mode,
                mode: if bench && window_size.is_none() { WindowMode::BorderlessFullscreen(MonitorSelection::Primary) } else { WindowMode::Windowed },
                resolution: match window_size {
                    Some((width, height)) => (width, height).into(),
                    None => default(),
                },
                ..default()
            }),
            ..default()
        }))
        .add_systems(Update, (press_script, keys_pressed, auto_loop).chain().after(find_body).before(animate))
        .add_systems(Update, window_pictures);
        if bench {
            // The hair counts in the first version's light, so the rows can be set beside the
            // first version's; then every lighting at one hair count. With `--hairs N`: that
            // count only, to find where the frame gets slow. With `--lights`: the lightings only.
            let one = if hairs.is_some() { usize::MAX } else { DEFAULT_PRESET };
            // As before these keys there were: the studio lighting LDR, the others HDR.
            let row = |label: &str, preset: usize, agitation: f32, shadows: bool, shown: bool, mood: usize| Stage {
                label: label.to_string(),
                preset,
                agitation,
                shadows,
                shown,
                mood,
                hdr: !MOODS[mood].plain,
                rt: false,
                proxy: START_PROXY,
            };
            let mut stages = vec![row("body only, no fur", one, 0.0, true, false, 0)];
            if hairs.is_some() || looks_only {
                stages.clear();
            }
            for preset in 0..if hairs.is_some() || lights_only || looks_only { 0 } else { PRESETS.len() } {
                stages.push(row("combed 0", preset, 0.0, true, true, 0));
                stages.push(row("rough 0.5", preset, 0.5, true, true, 0));
                stages.push(row("spikes 1", preset, 1.0, true, true, 0));
            }
            for mood in 0..if looks_only { 0 } else { MOODS.len() } {
                let name = MOODS[mood].name.split(" (").next().unwrap();
                stages.push(row(&format!("combed 0, {name}"), one, 0.0, true, true, mood));
                stages.push(row(&format!("rough 0.5, {name}"), one, 0.5, true, true, mood));
                stages.push(row(&format!("spikes 1, {name}"), one, 1.0, true, true, mood));
            }
            if hairs.is_none() && !lights_only && !looks_only {
                stages.push(row("rough 0.5, studio, fur casts no shadow", DEFAULT_PRESET, 0.5, false, true, 0));
                stages.push(row("rough 0.5, dusk, fur casts no shadow", DEFAULT_PRESET, 0.5, false, true, DEFAULT_MOOD));
            }
            if looks_only {
                // Every look in dusk light, combed and spiked; then, ray traced, what each
                // stand-in for the coat costs, and the body with no fur.
                let look = |label: String, agitation: f32, shown: bool, hdr: bool, rt: bool, proxy: usize| Stage { label, hdr, rt, proxy, ..row("", one, agitation, true, shown, DEFAULT_MOOD) };
                for (hdr, rt) in [(false, false), (true, false), (false, true), (true, true)] {
                    let name = format!("{} {}", if hdr { "HDR" } else { "LDR" }, if rt { "ray traced" } else { "rasterized" });
                    stages.push(look(format!("combed 0, {name}"), 0.0, true, hdr, rt, START_PROXY));
                    stages.push(look(format!("spikes 1, {name}"), 1.0, true, hdr, rt, START_PROXY));
                }
                for proxy in [0, 1, 3] {
                    stages.push(look(format!("combed 0, HDR ray traced, stand-in: {}", PROXIES[proxy].0), 0.0, true, true, true, proxy));
                    stages.push(look(format!("spikes 1, HDR ray traced, stand-in: {}", PROXIES[proxy].0), 1.0, true, true, true, proxy));
                }
                stages.push(look("body only, no fur, HDR rasterized".to_string(), 0.0, false, true, false, 0));
                stages.push(look("body only, no fur, HDR ray traced".to_string(), 0.0, false, true, true, 0));
            }
            // Bevy slows a window that does not have the keyboard to 60 frames a second; not here.
            app.insert_resource(WinitSettings::continuous())
                .insert_resource(Bench { stages, stage: 0, began: None, samples: Vec::new(), set: false })
                .add_systems(Update, bench_run.after(find_body).before(grow));
        } else if script.is_none() {
            println!("{KEYS}");
        }
    }
    let scripted = script.is_some();
    if let Some(keys) = script {
        app.insert_resource(Script { keys, next: 0, held: None, since: 0.0 });
    }
    scene::light_the_world(&mut app);
    let preset = hairs.map(|_| usize::MAX).unwrap_or(DEFAULT_PRESET);
    // Solari sets every standard material to be drawn deferred as soon as it is added. Here that
    // is so only while ray tracing is on: see `rt_scene`.
    let found = SurfaceFound::default();
    app.add_plugins((SolariPlugins, AutoExposurePlugin))
        .insert_resource(DefaultOpaqueRendererMethod::forward())
        .insert_resource(found.clone())
        .insert_resource(Look {
            hdr: hdr.unwrap_or(true),
            untouched: hdr.is_none() && !display_hdr,
            display_hdr,
            rt,
            rt_blocked: None,
            rt_asked: false,
            // An HDR signal with a tone mapper that brings everything under white would look
            // like SDR: on an HDR screen the HDR picture starts with none.
            tonemapper: if display_hdr { [START_TONEMAPPER[0], 0] } else { START_TONEMAPPER },
            stops: 0.0,
            auto_exposure: false,
            proxy,
            blend_frames: true,
            display: if check { String::new() } else { monitors_said() },
            said: String::new(),
            said_at: -100.0,
            proxy_ms: 0.0,
            proxy_triangles: 0,
        });
    if !check && let Some(render_app) = app.get_sub_app_mut(RenderApp) {
        render_app.insert_resource(found).add_systems(Render, ask_surface.before(create_surfaces));
    }
    app.add_plugins((MaterialPlugin::<FurMaterial>::default(), MaterialPlugin::<HazeMaterial>::default()))
        .insert_resource(Out(out))
        .insert_resource(CoatState {
            preset,
            asked: hairs.unwrap_or(PRESETS[DEFAULT_PRESET]),
            hairs: 0,
            quills: 0,
            triangles: 0,
            vertices: 0,
            build_ms: 0.0,
            entity: None,
            material: Handle::default(),
            rebuild: true,
            shadows: true,
            shown: true,
            seeds: Vec::new(),
            grown: 0,
        })
        .insert_resource(Show {
            agitation: 0.0,
            agitation_target: 0.0,
            agitation_rate: 0.0,
            history: VecDeque::new(),
            wave: [0.0; 4],
            startle: 0.0,
            wind_on: true,
            wind_strength: WIND_DEFAULT,
            wind_now: WIND_DEFAULT,
            gust_began: -1000.0,
            loop_paused: check || bench || scripted,
            loop_clock: 0.0,
            turntable: !(check || bench),
            angle: 0.0,
            debug: 0,
            calm,
            lean: Lean::Forward,
            lean_amount: LEAN_DEFAULT,
            wave_to_head: true,
            mood,
            body: first_body,
            clock: 0.0,
            ready: false,
        })
        .insert_resource(Bodies(bodies))
        .init_resource::<Motion>()
        .init_resource::<Framing>()
        .init_resource::<FrameTimes>()
        .init_resource::<Status>()
        .add_systems(Startup, move |world: &mut World| setup(world, &file_name, check, compare))
        .add_systems(Update, (change_body, find_body, grow, animate, light, ask_graphics_card, look_untouched, look_apply, rt_scene, proxy_coat, cameras, report).chain());
    #[cfg(feature = "overlay")]
    app.add_systems(Update, overlay.after(report));
    app.run()
}

/// The pictures of the strip: the same cameras at each of these agitations.
const STRIP: [(f32, &str); 9] = [
    (0.0, "01_strip_000"),
    (0.15, "01_strip_015"),
    (0.3, "01_strip_030"),
    (0.45, "01_strip_045"),
    (0.6, "01_strip_060"),
    (0.7, "01_strip_070"),
    (0.8, "01_strip_080"),
    (0.9, "01_strip_090"),
    (1.0, "01_strip_100"),
];
const STRIP_VIEWS: &[&str] = &["three_quarter", "side", "close"];

/// `--check`: what is done when, and which pictures are taken. A setting is changed just after
/// one picture and the next is taken a few frames later.
fn check_plan() -> Check {
    use Action::*;
    const ALL: &[&str] = &["three_quarter", "side", "close"];
    const SIDE_CLOSE: &[&str] = &["side", "close"];
    const WIDE: &[&str] = &["three_quarter", "side"];
    const WIDE_CLOSE: &[&str] = &["three_quarter", "close"];
    const WIDE_CLOSE_REAR: &[&str] = &["three_quarter", "close", "rear"];
    const REAR: &[&str] = &["rear"];
    let mut events = vec![(0.0, Wind(0.4)), (0.0, Agitate(0.0))];
    let mut shots = Vec::new();
    // The strip, in a light breeze so that what changes is the agitation.
    for (index, (agitation, name)) in STRIP.into_iter().enumerate() {
        let at = 1.0 + 0.1 * index as f32;
        events.push((at, Agitate(agitation)));
        shots.push((at + 0.08, name, STRIP_VIEWS));
    }
    events.extend([
        // Combed: the guard hairs tinted, and a moment later not; the body with no coat.
        (1.9, Agitate(0.0)),
        (1.9, Debug(2)),
        (2.0, Debug(0)),
        (2.1, Coat(false)),
        (2.2, Coat(true)),
        (2.2, Mood(0)),
        (2.38, Mood(2)),
        (2.56, Mood(3)),
        (2.74, Mood(0)),
        (2.74, Agitate(0.45)),
        (2.92, Agitate(0.7)),
        (3.0, Calm(2)),
        (3.1, Calm(DEFAULT_CALM)),
        (3.0, Mood(DEFAULT_MOOD)),
        (3.0, Agitate(0.0)),
        (3.1, Agitate(0.45)),
        // Wind on a combed coat and on a ruffled one.
        (3.2, Agitate(0.0)),
        (3.2, Wind(1.0)),
        (4.02, Agitate(0.4)),
        (4.52, Agitate(0.0)),
        (4.52, Gust),
        (5.6, Agitate(0.4)),
        (5.6, Gust),
        (6.7, Wind(3.5)),
        (7.92, Agitate(0.0)),
        (8.5, Wind(1.0)),
        (8.5, Agitate(0.2)),
        (9.0, Dash),
        // The change travelling: ruffling runs ahead of the spikes.
        (13.5, Agitate(0.1)),
        (13.6, AgitateTo(1.0, 3.0)),
        (16.42, Debug(1)),
        (16.47, Debug(0)),
        (18.52, LeanTo(Lean::Outward)),
        (18.62, LeanTo(Lean::Rearward)),
        (18.72, LeanTo(Lean::Forward)),
        (18.74, Mood(0)),
        (18.92, Mood(2)),
        (19.10, Mood(3)),
        (19.28, Mood(DEFAULT_MOOD)),
        (19.4, WaveToHead(false)),
        (19.4, Agitate(0.1)),
        (19.5, AgitateTo(1.0, 3.0)),
        (22.4, WaveToHead(true)),
        (22.4, Agitate(0.3)),
        (22.6, Shake),
        (24.0, Body(0)),
        (24.0, Agitate(0.0)),
        (24.52, Agitate(0.45)),
        (24.72, Agitate(1.0)),
        (25.0, Body(2)),
        (25.0, Agitate(0.0)),
        (25.52, Agitate(0.45)),
        (25.72, Agitate(1.0)),
        (26.0, Body(DEFAULT_BODY)),
    ]);
    shots.extend([
        (1.98, "02_combed_guard_hairs_tinted", WIDE_CLOSE),
        (2.08, "02_combed_no_tint", WIDE_CLOSE),
        (2.18, "02_body_with_no_coat", WIDE_CLOSE_REAR),
        (2.36, "03_combed_light_0_studio", WIDE_CLOSE_REAR),
        (2.54, "03_combed_light_2_cavern", WIDE_CLOSE),
        (2.72, "03_combed_light_3_moonlit_mist", WIDE_CLOSE),
        (2.90, "04_rough_light_0_studio", WIDE_CLOSE_REAR),
        (2.98, "04_hackles_light_0_studio", WIDE_CLOSE),
        (3.09, "04_calm_coat_tousled_at_0", WIDE_CLOSE),
        (3.19, "04_rough_rear", REAR),
        (4.0, "05_combed_in_wind", SIDE_CLOSE),
        (4.5, "05_ruffled_in_wind", SIDE_CLOSE),
        (5.57, "06_combed_gust", ALL),
        (6.65, "06_ruffled_gust", ALL),
        (7.9, "07_ruffled_gale", ALL),
        (8.4, "07_combed_gale", SIDE_CLOSE),
        (9.27, "08_mid_dash", SIDE_CLOSE),
        (9.52, "08_just_stopped", SIDE_CLOSE),
        (16.4, "09_mid_sweep_ruffling_ahead_of_spikes", ALL),
        (16.45, "09_mid_sweep_agitation_as_colours", WIDE),
        (18.5, "10_spikes_forward", ALL),
        (18.60, "10_spikes_outward", WIDE),
        (18.70, "10_spikes_rearward", WIDE),
        (18.90, "11_spikes_light_0_studio", WIDE_CLOSE),
        (19.08, "11_spikes_light_2_cavern", WIDE_CLOSE),
        (19.26, "11_spikes_light_3_moonlit_mist", WIDE_CLOSE),
        (22.3, "12_mid_sweep_neck_to_tail", WIDE),
        (22.92, "13_mid_shake", WIDE_CLOSE),
        (24.5, "14_body_p1_retracted_combed", ALL),
        (24.7, "14_body_p1_retracted_rough", WIDE_CLOSE),
        (24.9, "14_body_p1_retracted_spikes", WIDE),
        (25.5, "15_body_smooth_lowpoly_combed", ALL),
        (25.7, "15_body_smooth_lowpoly_rough", WIDE_CLOSE),
        (25.9, "15_body_smooth_lowpoly_spikes", WIDE),
    ]);
    events.sort_by(|a, b| a.0.total_cmp(&b.0));
    shots.sort_by(|a, b| a.0.total_cmp(&b.0));
    Check { events, shots, settle: 0, sheets_done: false }
}

/// Digits, a full stop and some capitals, 3 by 5 dots each, for the labels of the contact sheets.
const DOTS: [(char, [u8; 5]); 25] = [
    ('A', [2, 5, 7, 5, 5]),
    ('C', [7, 4, 4, 4, 7]),
    ('D', [6, 5, 5, 5, 6]),
    ('E', [7, 4, 6, 4, 7]),
    ('H', [5, 5, 7, 5, 5]),
    ('I', [7, 2, 2, 2, 7]),
    ('K', [5, 5, 6, 5, 5]),
    ('L', [4, 4, 4, 4, 7]),
    ('O', [7, 5, 5, 5, 7]),
    ('R', [6, 5, 6, 5, 5]),
    ('S', [7, 4, 7, 1, 7]),
    ('T', [7, 2, 2, 2, 2]),
    ('Y', [5, 5, 2, 2, 2]),
    ('Z', [7, 1, 2, 4, 7]),
    ('0', [7, 5, 5, 5, 7]),
    ('1', [2, 6, 2, 2, 7]),
    ('2', [7, 1, 7, 4, 7]),
    ('3', [7, 1, 7, 1, 7]),
    ('4', [5, 5, 7, 1, 1]),
    ('5', [7, 4, 7, 1, 7]),
    ('6', [7, 4, 7, 5, 7]),
    ('7', [7, 1, 1, 1, 1]),
    ('8', [7, 5, 7, 5, 7]),
    ('9', [7, 5, 7, 1, 7]),
    ('.', [0, 0, 0, 0, 2]),
];

/// One picture per camera of the whole strip, three across, each labelled with its agitation.
fn contact_sheets(out: &std::path::Path) {
    let (width, height) = (CHECK_SIZE.0 / 2, CHECK_SIZE.1 / 2);
    for view in STRIP_VIEWS {
        let mut sheet = image::RgbaImage::new(width * 3, height * 3);
        for (index, (agitation, name)) in STRIP.into_iter().enumerate() {
            let path = out.join(format!("{name}_{view}.png"));
            let picture = match image::open(&path) {
                Ok(picture) => picture.to_rgba8(),
                Err(error) => {
                    println!("contact sheet: cannot read {}: {error}", path.display());
                    continue;
                }
            };
            let small = image::imageops::resize(&picture, width, height, image::imageops::FilterType::Triangle);
            let (left, top) = ((index as u32 % 3) * width, (index as u32 / 3) * height);
            image::imageops::replace(&mut sheet, &small, left as i64, top as i64);
            stamp(&mut sheet, left + 14, top + 14, &format!("{agitation:.2}"), 6);
        }
        let path = out.join(format!("00_strip_sheet_{view}.png"));
        match sheet.save(&path) {
            Ok(()) => println!("contact sheet: {}", path.display()),
            Err(error) => println!("contact sheet: cannot write {}: {error}", path.display()),
        }
    }
}

/// Writes a label on a sheet in white on a dark strip, each dot of a letter `dot` pixels square.
fn stamp(sheet: &mut image::RgbaImage, left: u32, top: u32, text: &str, dot: u32) {
    let (wide, high) = (text.chars().count() as u32 * 4 * dot + dot, 7 * dot);
    for (x, y) in (0..wide * high).map(|at| (at % wide, at / wide)) {
        if let Some(pixel) = sheet.get_pixel_mut_checked(left + x - dot.min(left + x), top + y - dot.min(top + y)) {
            *pixel = image::Rgba([pixel[0] / 3, pixel[1] / 3, pixel[2] / 3, 255]);
        }
    }
    for (place, letter) in text.chars().enumerate() {
        let Some((_, rows)) = DOTS.iter().find(|(known, _)| *known == letter) else { continue };
        for (row, bits) in rows.iter().enumerate() {
            for column in (0..3).filter(|column| bits & (4 >> column) != 0) {
                for (x, y) in (0..dot * dot).map(|at| (at % dot, at / dot)) {
                    if let Some(pixel) = sheet.get_pixel_mut_checked(left + (place as u32 * 4 + column) * dot + x, top + row as u32 * dot + y) {
                        *pixel = image::Rgba([255, 255, 255, 255]);
                    }
                }
            }
        }
    }
}

/// The name of a look in a file's name and on a sheet.
fn look_names(hdr: bool, rt: bool) -> (&'static str, &'static str) {
    match (hdr, rt) {
        (false, false) => ("1_ldr_rasterized", "LDR RASTERIZED"),
        (true, false) => ("2_hdr_rasterized", "HDR RASTERIZED"),
        (false, true) => ("3_ldr_look_ray_traced", "RAY TRACED LDR LOOK"),
        (true, true) => ("4_hdr_ray_traced", "HDR RAY TRACED"),
    }
}

fn compare_name(mood: usize, moment: usize, view: &str) -> String {
    format!("{}_{}_{view}", MOODS[mood].name.replace(' ', "_"), MOMENTS[moment].0)
}

/// One sheet per moment, lighting and camera: the looks side by side, each labelled.
fn compare_sheets(out: &std::path::Path, looks: &[(bool, bool)]) {
    let (width, height) = (CHECK_SIZE.0 / 2, CHECK_SIZE.1 / 2);
    let across = if looks.len() > 2 { 2 } else { looks.len() as u32 };
    for (mood, moment, view) in COMPARE_MOODS.into_iter().flat_map(|mood| (0..MOMENTS.len()).flat_map(move |moment| COMPARE_VIEWS.map(|view| (mood, moment, view)))) {
        let name = compare_name(mood, moment, view);
        let mut sheet = image::RgbaImage::new(width * across, height * (looks.len() as u32).div_ceil(across));
        for (index, (hdr, rt)) in looks.iter().enumerate() {
            let (slug, label) = look_names(*hdr, *rt);
            let path = out.join(format!("{name}__{slug}.png"));
            let picture = match image::open(&path) {
                Ok(picture) => picture.to_rgba8(),
                Err(error) => {
                    println!("contact sheet: cannot read {}: {error}", path.display());
                    continue;
                }
            };
            let small = image::imageops::resize(&picture, width, height, image::imageops::FilterType::Triangle);
            let (left, top) = ((index as u32 % across) * width, (index as u32 / across) * height);
            image::imageops::replace(&mut sheet, &small, left as i64, top as i64);
            stamp(&mut sheet, left + 12, top + 12, label, 3);
        }
        let path = out.join(format!("00_sheet_{name}.png"));
        match sheet.save(&path) {
            Ok(()) => println!("contact sheet: {}", path.display()),
            Err(error) => println!("contact sheet: cannot write {}: {error}", path.display()),
        }
    }
}

/// `--check`: every moment in every lighting in every look, each picture taken at the same
/// moment of the show's clock so that the hairs, the clouds and the lamp are where they were.
#[expect(clippy::too_many_arguments)]
fn compare_run(
    mut commands: Commands,
    out: Res<Out>,
    mut compare: ResMut<Compare>,
    mut show: ResMut<Show>,
    mut motion: ResMut<Motion>,
    mut look: ResMut<Look>,
    views: Query<(&View, &RenderTarget)>,
    pending: Query<(), With<Screenshot>>,
    mut exit: MessageWriter<AppExit>,
) {
    if !show.ready || !look.rt_asked {
        return;
    }
    if compare.looks.is_empty() {
        compare.looks = vec![(false, false), (true, false)];
        match &look.rt_blocked {
            None => compare.looks.extend([(false, true), (true, true)]),
            Some(why) => println!("the two ray-traced looks are left out: {why}"),
        }
        compare.steps = compare
            .looks
            .clone()
            .into_iter()
            .flat_map(|(hdr, rt)| COMPARE_MOODS.into_iter().flat_map(move |mood| (0..MOMENTS.len()).map(move |moment| (hdr, rt, mood, moment))))
            .collect();
    }
    let Some(&(hdr, rt, mood, moment)) = compare.steps.get(compare.step) else {
        compare.frames += 1;
        if pending.is_empty() && compare.frames > 10 {
            compare_sheets(out.0.as_ref().unwrap(), &compare.looks);
            exit.write(AppExit::Success);
        }
        return;
    };
    let settle = if rt { RT_SETTLE_FRAMES } else { 30 };
    if compare.frames == 0 {
        let (_, agitation, wind) = MOMENTS[moment];
        (look.hdr, look.untouched, look.rt, show.mood) = (hdr, false, rt, mood);
        act(Action::Agitate(agitation), &mut show, &mut motion);
        (show.wind_strength, show.wind_now, show.gust_began, show.startle) = (wind, wind, -1000.0, 0.0);
        show.clock = 20.0 - settle as f32 / 60.0;
        compare.shot = false;
    }
    compare.frames += 1;
    if compare.frames == settle + 1 {
        let (slug, _) = look_names(hdr, rt);
        println!("{}: {}, at {:.3} s of the clock", compare_name(mood, moment, "*"), slug, show.clock);
        for (view, target) in &views {
            let RenderTarget::Image(image) = target else { continue };
            let path = out.0.as_ref().unwrap().join(format!("{}__{slug}.png", compare_name(mood, moment, view.name)));
            commands.spawn(Screenshot::image(image.handle.clone())).observe(save_to_disk(path));
        }
        compare.shot = true;
    } else if compare.frames > settle + 3 && pending.is_empty() && compare.shot {
        (compare.step, compare.frames) = (compare.step + 1, 0);
    }
}

fn parse_keys(keys: &str) -> Result<Vec<(String, KeyCode)>, String> {
    keys.split(',')
        .map(str::trim)
        .filter(|name| !name.is_empty())
        .map(|name| {
            let code = match name.to_ascii_uppercase().as_str() {
                "B" => KeyCode::KeyB,
                "W" => KeyCode::KeyW,
                "G" => KeyCode::KeyG,
                "D" => KeyCode::KeyD,
                "S" => KeyCode::KeyS,
                "H" => KeyCode::KeyH,
                "C" => KeyCode::KeyC,
                "X" => KeyCode::KeyX,
                "T" => KeyCode::KeyT,
                "R" => KeyCode::KeyR,
                "F" => KeyCode::KeyF,
                "Q" => KeyCode::KeyQ,
                "V" => KeyCode::KeyV,
                "L" => KeyCode::KeyL,
                "N" => KeyCode::KeyN,
                "K" => KeyCode::KeyK,
                "M" => KeyCode::KeyM,
                "E" => KeyCode::KeyE,
                "O" => KeyCode::KeyO,
                "P" => KeyCode::KeyP,
                "J" => KeyCode::KeyJ,
                "I" => KeyCode::KeyI,
                "-" | "MINUS" | "DARKER" => KeyCode::Minus,
                "=" | "+" | "EQUAL" | "BRIGHTER" => KeyCode::Equal,
                "1" => KeyCode::Digit1,
                "2" => KeyCode::Digit2,
                "3" => KeyCode::Digit3,
                "4" => KeyCode::Digit4,
                "5" => KeyCode::Digit5,
                // A comma separates the keys, so these two have names.
                "<" | "COMMA" | "LESS" => KeyCode::Comma,
                ">" | "." | "PERIOD" | "MORE" => KeyCode::Period,
                "[" => KeyCode::BracketLeft,
                "]" => KeyCode::BracketRight,
                "UP" => KeyCode::ArrowUp,
                "DOWN" => KeyCode::ArrowDown,
                "SPACE" => KeyCode::Space,
                "ESC" | "ESCAPE" => KeyCode::Escape,
                _ => return Err(name.to_string()),
            };
            Ok((name.to_string(), code))
        })
        .collect()
}

fn setup(world: &mut World, file_name: &str, to_image: bool, compare: bool) {
    world.resource_mut::<Assets<Shader>>().insert(&FUR_SHADER, Shader::from_wgsl(include_str!("fur_strands.wgsl"), "fur_strands.wgsl")).unwrap();
    world.resource_mut::<Assets<Shader>>().insert(&HAZE_SHADER, Shader::from_wgsl(include_str!("fur_haze.wgsl"), "fur_haze.wgsl")).unwrap();
    let material = world.resource_mut::<Assets<FurMaterial>>().add(FurMaterial::default());
    world.resource_mut::<CoatState>().material = material;
    world
        .run_system_cached_with(
            |file: In<String>,
             mut commands: Commands,
             asset_server: Res<AssetServer>,
             mut meshes: ResMut<Assets<Mesh>>,
             mut materials: ResMut<Assets<StandardMaterial>>| {
                scene::spawn_scene(&mut commands, &asset_server, &mut meshes, &mut materials, &file);
            },
            file_name.to_string(),
        )
        .unwrap();

    scenery(world);

    let three_quarter = View { name: "three_quarter", from: Vec3::new(1.0, 0.7, 1.0).normalize(), near: 0.62, aim: Vec3::ZERO };
    let lens = || Projection::Perspective(PerspectiveProjection { fov: FOV, ..default() });
    if to_image {
        // The side view looks at the creature's left flank; the close one at its shoulder.
        let views = [
            three_quarter,
            View { name: "side", from: Vec3::new(1.0, 0.12, 0.0).normalize(), near: 0.62, aim: Vec3::ZERO },
            View { name: "close", from: Vec3::new(1.0, 0.45, 0.75).normalize(), near: 0.33, aim: Vec3::new(0.08, 0.04, 0.12) },
            // From behind and above, at the rump and the root of the tail.
            View { name: "rear", from: Vec3::new(0.55, 0.9, -1.0).normalize(), near: 0.36, aim: Vec3::new(0.0, 0.1, -0.2) },
        ];
        // The comparison of looks takes two of the cameras; a camera that takes no picture would
        // still be drawn, and ray traced, every frame.
        for view in views.into_iter().filter(|view| !compare || COMPARE_VIEWS.contains(&view.name)) {
            let target = Image::new_target_texture(CHECK_SIZE.0, CHECK_SIZE.1, TextureFormat::Rgba8UnormSrgb, None);
            let target = world.resource_mut::<Assets<Image>>().add(target);
            world.spawn((view, Camera3d::default(), lens(), Transform::default(), RenderTarget::Image(target.into())));
        }
    } else {
        world.spawn((three_quarter, Camera3d::default(), lens(), Transform::from_xyz(3.0, 2.0, 3.0).looking_at(Vec3::ZERO, Vec3::Y)));
    }
    #[cfg(feature = "overlay")]
    if !to_image {
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

/// Marks the viewer's own sun and ground, and adds what the other lightings need: a light from
/// behind, a lamp, a darker ground with a pattern, and a sky for each.
fn scenery(world: &mut World) {
    let sun = world.query_filtered::<Entity, With<DirectionalLight>>().single(world).unwrap();
    world.entity_mut(sun).insert(Sun);
    let ground = world.query_filtered::<Entity, (With<Mesh3d>, Without<Model>)>().single(world).unwrap();
    world.entity_mut(ground).insert(PlainGround);
    world.spawn((BackLight, DirectionalLight { illuminance: 0.0, shadow_maps_enabled: false, ..default() }, Transform::default(), Visibility::Hidden));
    world.spawn((
        Lamp,
        PointLight { color: Color::linear_rgb(LAMP_COLOUR[0], LAMP_COLOUR[1], LAMP_COLOUR[2]), intensity: 0.0, range: 14.0, radius: LAMP_RADIUS, shadow_maps_enabled: false, ..default() },
        Transform::from_translation(LAMP_AT),
        Visibility::Hidden,
    ));

    // The ground: a picture of earth made here, repeated every 3 m, tinted by the lighting.
    let mut picture = Image::new(
        Extent3d { width: GROUND_PIXELS as u32, height: GROUND_PIXELS as u32, depth_or_array_layers: 1 },
        TextureDimension::D2,
        ground_picture(),
        TextureFormat::Rgba8UnormSrgb,
        RenderAssetUsages::RENDER_WORLD,
    );
    picture.sampler = ImageSampler::Descriptor(ImageSamplerDescriptor {
        address_mode_u: ImageAddressMode::Repeat,
        address_mode_v: ImageAddressMode::Repeat,
        ..ImageSamplerDescriptor::linear()
    });
    let picture = world.resource_mut::<Assets<Image>>().add(picture);
    let mut plane = Plane3d::default().mesh().size(200.0, 200.0).build();
    if let Some(VertexAttributeValues::Float32x2(uvs)) = plane.attribute_mut(Mesh::ATTRIBUTE_UV_0) {
        for uv in uvs {
            *uv = [uv[0] * 200.0 / 3.0, uv[1] * 200.0 / 3.0];
        }
    }
    let plane = world.resource_mut::<Assets<Mesh>>().add(plane);
    let material = world.resource_mut::<Assets<StandardMaterial>>().add(StandardMaterial {
        base_color_texture: Some(picture),
        perceptual_roughness: 0.92,
        reflectance: 0.3,
        depth_bias: -4.0,
        ..default()
    });
    let haze = world.resource_mut::<Assets<HazeMaterial>>().add(HazeMaterial {});
    world.spawn((Haze, Mesh3d(plane.clone()), MeshMaterial3d(haze), NotShadowCaster, Visibility::Hidden));
    world.spawn((MoodGround, Mesh3d(plane), MeshMaterial3d(material.clone()), Visibility::Hidden));
    world.insert_resource(Scenery { ground: material });

    // The skies: dark above, the fog's colour at the horizon so the ground fades into it, and
    // a glow low down where the sun is.
    for (index, mood) in MOODS.iter().enumerate().filter(|(_, mood)| !mood.plain) {
        let mut ball = Sphere::new(95.0).mesh().uv(64, 32);
        let Some(VertexAttributeValues::Float32x3(positions)) = ball.attribute(Mesh::ATTRIBUTE_POSITION) else { continue };
        let to_sun = Vec3::new(mood.sun_from.x, 0.0, mood.sun_from.z).normalize_or_zero();
        let to_back = Vec3::new(mood.back_from.x, 0.0, mood.back_from.z).normalize_or_zero();
        let colours: Vec<[f32; 4]> = positions
            .iter()
            .map(|position| {
                let way = Vec3::from(*position).normalize();
                let sky = Vec3::from(mood.sky_horizon).lerp(Vec3::from(mood.sky_top), smoothstep(0.0, 0.32, way.y));
                let low = 1.0 - smoothstep(0.0, 0.38, way.y);
                let glow = Vec3::from(mood.sky_glow) * way.dot(to_sun).max(0.0).powf(5.0) * low * low;
                // A fainter glow where the light from behind the creature comes from.
                let behind = Vec3::from(mood.back) * 0.07 * mood.rim * way.dot(to_back).max(0.0).powf(3.0) * low;
                (sky + glow + behind).extend(1.0).to_array()
            })
            .collect();
        ball.insert_attribute(Mesh::ATTRIBUTE_COLOR, colours);
        let ball = world.resource_mut::<Assets<Mesh>>().add(ball);
        let sky = world.resource_mut::<Assets<StandardMaterial>>().add(StandardMaterial { unlit: true, fog_enabled: false, cull_mode: None, ..default() });
        world.spawn((Sky(index), Mesh3d(ball), MeshMaterial3d(sky), NotShadowCaster, NotShadowReceiver, Visibility::Hidden));
    }
}

const GROUND_PIXELS: usize = 512;

/// A picture of dark earth that repeats without a seam: lumps of several sizes, patches of
/// moss, and grit.
fn ground_picture() -> Vec<u8> {
    let corner = |x: usize, y: usize, cells: usize, seed: u64| {
        let mut rng = Rng(seed.wrapping_mul(0x1F3D).wrapping_add(((x % cells) * 7919 + (y % cells) * 104_729) as u64));
        rng.next();
        rng.next()
    };
    // Smooth noise on a grid of `cells` by `cells` that wraps round.
    let noise = |u: f32, v: f32, cells: usize, seed: u64| {
        let (x, y) = (u * cells as f32, v * cells as f32);
        let (column, row) = (x.floor() as usize, y.floor() as usize);
        let (fx, fy) = (smoothstep(0.0, 1.0, x.fract()), smoothstep(0.0, 1.0, y.fract()));
        let top = corner(column, row, cells, seed) * (1.0 - fx) + corner(column + 1, row, cells, seed) * fx;
        let bottom = corner(column, row + 1, cells, seed) * (1.0 - fx) + corner(column + 1, row + 1, cells, seed) * fx;
        top * (1.0 - fy) + bottom * fy
    };
    let mut grit = Rng(0x6772_6974);
    let mut pixels = Vec::with_capacity(GROUND_PIXELS * GROUND_PIXELS * 4);
    for y in 0..GROUND_PIXELS {
        for x in 0..GROUND_PIXELS {
            let (u, v) = (x as f32 / GROUND_PIXELS as f32, y as f32 / GROUND_PIXELS as f32);
            let lumps = 0.5 * noise(u, v, 5, 1) + 0.3 * noise(u, v, 11, 2) + 0.14 * noise(u, v, 23, 3) + 0.06 * noise(u, v, 96, 4);
            let moss = 0.7 * smoothstep(0.45, 0.75, 0.6 * noise(u, v, 4, 5) + 0.4 * noise(u, v, 11, 6));
            let earth = Vec3::new(0.50, 0.43, 0.37).lerp(Vec3::new(0.33, 0.44, 0.27), moss);
            let colour = earth * (0.45 + 0.9 * lumps) * (0.85 + 0.3 * grit.next());
            pixels.extend(colour.to_array().map(|channel| (channel.clamp(0.0, 1.0) * 255.0) as u8));
            pixels.push(255);
        }
    }
    pixels
}

fn smoothstep(low: f32, high: f32, x: f32) -> f32 {
    let t = ((x - low) / (high - low)).clamp(0.0, 1.0);
    t * t * (3.0 - 2.0 * t)
}

fn to_linear(srgb: f32) -> f32 {
    if srgb <= 0.04045 { srgb / 12.92 } else { ((srgb + 0.055) / 1.055).powf(2.4) }
}

impl Body {
    /// The body's colour at a UV, as the file stores it (sRGB, 0 to 1).
    fn colour(&self, uv: Vec2) -> [f32; 3] {
        let Some((width, height, pixels)) = &self.image else { return self.factor };
        let x = ((uv.x.rem_euclid(1.0) * *width as f32) as u32).min(width - 1);
        let y = ((uv.y.rem_euclid(1.0) * *height as f32) as u32).min(height - 1);
        let at = ((y * width + x) * 4) as usize;
        [0, 1, 2].map(|channel| pixels[at + channel] as f32 / 255.0 * self.factor[channel])
    }
}

/// Whether fur grows on a place of this colour and height. The snout is the only strongly red
/// part of the creature, the hooves, claws, eyes and nostrils the only dark ones, and the feet
/// the only part this low.
fn furred(colour: [f32; 3], place: Vec3) -> bool {
    let [r, g, b] = colour;
    let dark = 0.3 * r + 0.6 * g + 0.1 * b < 0.45;
    !is_red(colour) && !dark && place.y > 0.07
}

fn largest_piece(pieces: &HashMap<usize, [f32; 5]>) -> f32 {
    pieces.values().map(|sums| sums[0]).fold(0.0, f32::max)
}

fn is_red([r, g, b]: [f32; 3]) -> bool {
    let (most, least) = (r.max(g).max(b), r.min(g).min(b));
    (most - least) / most.max(0.001) > 0.45 && r > g * 1.5
}

/// How thick the model is behind each triangle: the way from its middle, straight in, to the
/// first triangle met. A body is thick and a modelled spike is thin. Every triangle is tried
/// against every other, on all the processor's threads.
fn thicknesses(triangles: &[[(Vec3, Vec3, Vec2); 3]]) -> Vec<f32> {
    let one = |index: usize| {
        let [a, b, c] = triangles[index];
        let mut inward = -(b.0 - a.0).cross(c.0 - a.0).normalize_or_zero();
        if inward.dot(a.1 + b.1 + c.1) > 0.0 {
            inward = -inward;
        }
        let from = (a.0 + b.0 + c.0) / 3.0 + inward * 1e-4;
        let mut nearest = f32::MAX;
        for (other, [p, q, r]) in triangles.iter().enumerate() {
            // Moeller and Trumbore's ray and triangle test.
            let (edge_1, edge_2) = (q.0 - p.0, r.0 - p.0);
            let h = inward.cross(edge_2);
            let det = edge_1.dot(h);
            if other == index || det.abs() < 1e-12 {
                continue;
            }
            let s = from - p.0;
            let u = s.dot(h) / det;
            let q = s.cross(edge_1);
            let v = inward.dot(q) / det;
            let t = edge_2.dot(q) / det;
            if u >= 0.0 && v >= 0.0 && u + v <= 1.0 && t > 0.0 && t < nearest {
                nearest = t;
            }
        }
        nearest
    };
    let threads = std::thread::available_parallelism().map_or(4, usize::from);
    let share = triangles.len().div_ceil(threads).max(1);
    let mut all = vec![f32::MAX; triangles.len()];
    std::thread::scope(|scope| {
        for (chunk, out) in all.chunks_mut(share).enumerate() {
            scope.spawn(move || {
                for (offset, thickness) in out.iter_mut().enumerate() {
                    *thickness = one(chunk * share + offset);
                }
            });
        }
    });
    all
}

/// When another body is chosen: takes the model and its coat away and loads the other. The
/// show's clock stands still until the new coat has grown.
#[expect(clippy::too_many_arguments)]
fn change_body(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    bodies: Res<Bodies>,
    mut show: ResMut<Show>,
    mut coat: ResMut<CoatState>,
    mut motion: ResMut<Motion>,
    model: Query<Entity, With<Model>>,
    mut shown: Local<Option<usize>>,
) {
    let body = show.body.min(bodies.0.len() - 1);
    if shown.replace(body).is_none_or(|before| before == body) {
        return;
    }
    for model in &model {
        commands.entity(model).despawn();
    }
    commands.spawn((Model, WorldAssetRoot(asset_server.load(GltfAssetLabel::Scene(0).from_asset(bodies.0[body].1.clone())))));
    commands.remove_resource::<Body>();
    *motion = Motion::default();
    (coat.entity, coat.rebuild, show.ready) = (None, true, false);
}

/// Reads the body out of the loaded model once: its triangles in the `retracted` shape if it has
/// one, and its base colour picture.
#[expect(clippy::too_many_arguments)]
fn find_body(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut meshes: ResMut<Assets<Mesh>>,
    materials: Res<Assets<StandardMaterial>>,
    images: Res<Assets<Image>>,
    body: Option<Res<Body>>,
    mut framing: ResMut<Framing>,
    model: Single<(Entity, &WorldAssetRoot), With<Model>>,
    children: Query<&Children>,
    placed: Query<(&Mesh3d, &GlobalTransform, Option<&MeshMaterial3d<StandardMaterial>>), Without<Coat>>,
    mut morphs: Query<&mut MorphWeights>,
    mut waited: Local<u32>,
) {
    // The spikes modelled on the pieces models stay inside the body: the strands are the fur.
    for mut morph in &mut morphs {
        let names = morph.first_mesh().and_then(|mesh| meshes.get(mesh)).and_then(Mesh::morph_target_names).unwrap_or(&[]);
        let retracted = names.iter().position(|name| name == "retracted");
        for (index, weight) in morph.weights_mut().iter_mut().enumerate() {
            *weight = if Some(index) == retracted { 1.0 } else { 0.0 };
        }
    }
    if body.is_some() || !asset_server.is_loaded_with_dependencies(&model.1.0) {
        return;
    }
    *waited += 1;
    if *waited < 4 {
        return;
    }
    let mut triangles = Vec::new();
    // Each mesh's triangles as its own indices, and where they start in `triangles`.
    let mut drawn: Vec<(AssetId<Mesh>, usize, Vec<usize>, Affine3A, bool)> = Vec::new();
    let (mut image, mut factor, mut body_material) = (None, [1.0; 3], None);
    let (mut min, mut max, mut body_triangles) = (Vec3::MAX, Vec3::MIN, 0);
    for entity in children.iter_descendants(model.0) {
        let Ok((mesh, to_world, material)) = placed.get(entity) else { continue };
        let mesh_id = mesh.0.id();
        let Some(mesh) = meshes.get(mesh_id) else { continue };
        let Some(VertexAttributeValues::Float32x3(positions)) = mesh.attribute(Mesh::ATTRIBUTE_POSITION) else { continue };
        let Some(VertexAttributeValues::Float32x3(normals)) = mesh.attribute(Mesh::ATTRIBUTE_NORMAL) else { continue };
        let uvs = match mesh.attribute(Mesh::ATTRIBUTE_UV_0) {
            Some(VertexAttributeValues::Float32x2(uvs)) => uvs.clone(),
            _ => vec![[0.0, 0.0]; positions.len()],
        };
        let retracted = mesh.morph_target_names().and_then(|names| names.iter().position(|name| name == "retracted"));
        let moves = retracted.and_then(|target| mesh.morph_targets().map(|all| &all[target * positions.len()..(target + 1) * positions.len()]));
        let corners: Vec<(Vec3, Vec3, Vec2)> = (0..positions.len())
            .map(|vertex| {
                let (mut position, mut normal) = (Vec3::from(positions[vertex]), Vec3::from(normals[vertex]));
                if let Some(moves) = moves {
                    position += moves[vertex].position;
                    normal += moves[vertex].normal;
                }
                (to_world.transform_point(position), (to_world.affine().matrix3 * normal.to_vec3a()).normalize_or_zero().into(), Vec2::from(uvs[vertex]))
            })
            .collect();
        let indices: Vec<usize> = match mesh.indices() {
            Some(indices) => indices.iter().collect(),
            None => (0..positions.len()).collect(),
        };
        for triangle in indices.chunks_exact(3) {
            triangles.push([corners[triangle[0]], corners[triangle[1]], corners[triangle[2]]]);
        }
        body_triangles += indices.len() / 3;
        drawn.push((mesh_id, triangles.len() - indices.len() / 3, indices, to_world.affine().inverse(), retracted.is_some()));
        for corner in &corners {
            min = min.min(corner.0);
            max = max.max(corner.0);
        }
        body_material = body_material.or(material.map(|material| material.0.clone()));
        if let Some(material) = material.and_then(|material| materials.get(&material.0)) {
            let colour = material.base_color.to_srgba();
            factor = [colour.red, colour.green, colour.blue];
            image = material.base_color_texture.as_ref().and_then(|texture| images.get(texture)).and_then(|texture| {
                let size = texture.texture_descriptor.size;
                let four_bytes = matches!(texture.texture_descriptor.format, TextureFormat::Rgba8UnormSrgb | TextureFormat::Rgba8Unorm);
                texture.data.clone().filter(|data| four_bytes && data.len() as u32 >= size.width * size.height * 4).map(|data| (size.width, size.height, data))
            });
            if image.is_none() {
                println!("the body's base colour picture could not be read: every hair takes the material's one colour");
            }
        }
    }
    if triangles.is_empty() {
        *waited = 0;
        return;
    }
    let length = max.z - min.z;
    // The top of the back: the highest point of the middle of the body's length.
    let back_top = triangles
        .iter()
        .flatten()
        .filter(|corner| (0.3..0.6).contains(&((max.z - corner.0.z) / length)))
        .map(|corner| corner.0.y)
        .fold(min.y, f32::max);
    let mut body = Body { triangles: Vec::new(), area_up_to: Vec::new(), image, factor, min, max, back_top, snout: Vec3::new(0.0, 0.3, max.z), body_triangles, material: body_material };
    let began = Instant::now();
    let mut thickness = thicknesses(&triangles);
    let thickness_ms = began.elapsed().as_secs_f32() * 1000.0;
    let (mut thin, mut snout, mut snout_area) = (0.0, Vec3::ZERO, 0.0);
    let (mut total, mut bare) = (0.0, 0.0);

    // Corners at the same place are one vertex, whatever the file's UV seams say.
    let mut welded: HashMap<[i32; 3], usize> = HashMap::new();
    let mut piece_of: Vec<usize> = Vec::new();
    fn find(piece_of: &mut [usize], mut at: usize) -> usize {
        while piece_of[at] != at {
            piece_of[at] = piece_of[piece_of[at]];
            at = piece_of[at];
        }
        at
    }
    let corners_welded: Vec<[usize; 3]> = triangles
        .iter()
        .map(|triangle| {
            let ids = triangle.map(|corner| {
                let key = (corner.0 * 20_000.0).round().as_ivec3().to_array();
                let next = welded.len();
                let id = *welded.entry(key).or_insert(next);
                if id == piece_of.len() {
                    piece_of.push(id);
                }
                id
            });
            let (a, b, c) = (find(&mut piece_of, ids[0]), find(&mut piece_of, ids[1]), find(&mut piece_of, ids[2]));
            piece_of[b] = a;
            piece_of[c] = a;
            ids
        })
        .collect();

    // A body generated "without spikes" still has small modelled tufts fused to it: a fringe
    // of flaps along the line between the two colours, nicks on the back, fins on the tail.
    // They are thin, so they grew no hair and stood out of the coat as bare shards. Each small
    // thin patch is flattened onto the body: its vertices are moved, over and over, to the
    // middle of their neighbours while the vertices round its edge stay, so the flap sinks to a
    // smooth cap over its foot. Then it grows fur like the rest. Not on a body that morphs.
    if drawn.iter().all(|mesh| !mesh.4) {
        let soft: Vec<bool> = triangles
            .iter()
            .zip(&thickness)
            .map(|([a, b, c], thickness)| *thickness < THIN && !is_red(body.colour((a.2 + b.2 + c.2) / 3.0)) && (a.0.y + b.0.y + c.0.y) / 3.0 > 0.12)
            .collect();
        // Patches of thin triangles that touch, and the area of each.
        let mut patch_of: Vec<usize> = (0..welded.len()).collect();
        for (ids, _) in corners_welded.iter().zip(&soft).filter(|(_, soft)| **soft) {
            let (a, b, c) = (find(&mut patch_of, ids[0]), find(&mut patch_of, ids[1]), find(&mut patch_of, ids[2]));
            patch_of[b] = a;
            patch_of[c] = a;
        }
        let mut patch_area: HashMap<usize, f32> = HashMap::new();
        for ((ids, [a, b, c]), _) in corners_welded.iter().zip(&triangles).zip(&soft).filter(|(_, soft)| **soft) {
            *patch_area.entry(find(&mut patch_of, ids[0])).or_default() += (b.0 - a.0).cross(c.0 - a.0).length() / 2.0;
        }
        let small: Vec<bool> = corners_welded.iter().zip(&soft).map(|(ids, soft)| *soft && patch_area[&find(&mut patch_of, ids[0])] < FLATTEN_MOST).collect();
        // The vertices of a small thin patch move, and those within `FLATTEN_RINGS` edges of
        // it, because a flap is a shingle: only its lip is thin. Nothing of the snout or the
        // feet moves.
        let mut moves = vec![false; welded.len()];
        let mut held = vec![false; welded.len()];
        for ((ids, [a, b, c]), small) in corners_welded.iter().zip(&triangles).zip(&small) {
            let keep = is_red(body.colour((a.2 + b.2 + c.2) / 3.0)) || (a.0.y + b.0.y + c.0.y) / 3.0 <= 0.12;
            for id in ids {
                moves[*id] |= *small;
                held[*id] |= keep;
            }
        }
        for _ in 0..FLATTEN_RINGS {
            let reached: Vec<bool> = corners_welded.iter().map(|ids| ids.iter().any(|id| moves[*id])).collect();
            for (ids, _) in corners_welded.iter().zip(&reached).filter(|(_, reached)| **reached) {
                for id in ids {
                    moves[*id] = true;
                }
            }
        }
        for (moves, held) in moves.iter_mut().zip(&held) {
            *moves &= !*held;
        }
        let touched = vec![true; welded.len()];
        let mut places = vec![Vec3::ZERO; welded.len()];
        let mut normals = vec![Vec3::ZERO; welded.len()];
        let mut neighbours: Vec<Vec<usize>> = vec![Vec::new(); welded.len()];
        for (ids, triangle) in corners_welded.iter().zip(&triangles) {
            for corner in 0..3 {
                places[ids[corner]] = triangle[corner].0;
                normals[ids[corner]] += triangle[corner].1;
                if moves[ids[corner]] {
                    neighbours[ids[corner]].extend([ids[(corner + 1) % 3], ids[(corner + 2) % 3]]);
                }
            }
        }
        let moving: Vec<usize> = (0..welded.len()).filter(|id| moves[*id] && touched[*id] && !neighbours[*id].is_empty()).collect();
        for normal in &mut normals {
            *normal = normal.normalize_or_zero();
        }
        for id in &moving {
            normals[*id] = Vec3::ZERO;
        }
        for _ in 0..200 {
            for id in &moving {
                let count = neighbours[*id].len() as f32;
                places[*id] = neighbours[*id].iter().map(|other| places[*other]).sum::<Vec3>() / count;
                normals[*id] = neighbours[*id].iter().map(|other| normals[*other]).sum::<Vec3>() / count;
            }
        }
        let mut flattened = 0.0;
        for (((ids, triangle), small), thickness) in corners_welded.iter().zip(&mut triangles).zip(&small).zip(&mut thickness) {
            for corner in 0..3 {
                if moves[ids[corner]] {
                    triangle[corner].0 = places[ids[corner]];
                    triangle[corner].1 = normals[ids[corner]].normalize_or(triangle[corner].1);
                }
            }
            if !*small {
                continue;
            }
            // It lies on the body now, and is as thick as the body.
            *thickness = f32::MAX;
            flattened += (triangle[1].0 - triangle[0].0).cross(triangle[2].0 - triangle[0].0).length() / 2.0;
        }
        for (mesh_id, first, indices, to_local, _) in &drawn {
            let Some(mut mesh) = meshes.get_mut(*mesh_id) else { continue };
            for (attribute, normal) in [(Mesh::ATTRIBUTE_POSITION, false), (Mesh::ATTRIBUTE_NORMAL, true)] {
                let Some(VertexAttributeValues::Float32x3(values)) = mesh.attribute_mut(attribute) else { continue };
                for (triangle, corners) in indices.chunks_exact(3).enumerate() {
                    for corner in 0..3 {
                        let id = corners_welded[first + triangle][corner];
                        if moves[id] {
                            let moved = triangles[first + triangle][corner];
                            values[corners[corner]] = if normal { to_local.transform_vector3(moved.1).normalize_or(Vec3::Y).to_array() } else { to_local.transform_point3(moved.0).to_array() };
                        }
                    }
                }
            }
        }
        let patches = patch_area.values().filter(|area| **area < FLATTEN_MOST).count();
        let mut largest: Vec<f32> = patch_area.values().copied().collect();
        largest.sort_by(|a, b| b.total_cmp(a));
        println!(
            "tufts: {patches} small thin patches of the body flattened onto it ({} vertices moved, {:.3} m2 before and {flattened:.3} m2 after); {} larger ones left; the largest patches were {:?} m2",
            moving.len(),
            patch_area.values().filter(|area| **area < FLATTEN_MOST).sum::<f32>(),
            patch_area.len() - patches,
            &largest[..largest.len().min(5)]
        );
    }

    // The model may be loose pieces. A piece that is mostly thin and of the coat's colour is a
    // modelled tuft or bristle left standing out of the fur: it is not drawn and grows no hair.
    // Hooves and claws are thin too, but dark, and stay.
    // Per piece: its area, the thin part of it, the part bare by colour or height, the red part,
    // and its height times its area.
    let mut pieces: HashMap<usize, [f32; 5]> = HashMap::new();
    let triangle_piece: Vec<usize> = corners_welded.iter().map(|ids| find(&mut piece_of, ids[0])).collect();
    for ((triangle, thickness), piece) in triangles.iter().zip(&thickness).zip(&triangle_piece) {
        let [a, b, c] = triangle;
        let area = (b.0 - a.0).cross(c.0 - a.0).length() / 2.0;
        let sums = pieces.entry(*piece).or_default();
        sums[0] += area;
        sums[1] += if *thickness < THIN { area } else { 0.0 };
        let (colour, middle) = (body.colour((a.2 + b.2 + c.2) / 3.0), (a.0 + b.0 + c.0) / 3.0);
        sums[2] += if furred(colour, middle) { 0.0 } else { area };
        sums[3] += if is_red(colour) { area } else { 0.0 };
        sums[4] += middle.y * area;
    }
    // Thin, and either of the coat's colour or standing well above the feet without being the
    // red snout.
    let hide = |[area, thin, bare, red, height]: [f32; 5]| {
        area < largest_piece(&pieces) && area > 1e-8 && thin > 0.5 * area && (bare < 0.5 * area || (height > 0.25 * area && red < 0.3 * area))
    };
    let hidden: Vec<bool> = triangle_piece.iter().map(|piece| hide(pieces[piece])).collect();
    let hidden_pieces = pieces.values().filter(|sums| hide(**sums)).count();
    let hidden_area: f32 = pieces.values().filter(|sums| hide(**sums)).map(|sums| sums[0]).sum();
    for (mesh_id, first, indices, _, _) in &drawn {
        let kept: Vec<u32> = indices.chunks_exact(3).enumerate().filter(|(triangle, _)| !hidden[first + triangle]).flat_map(|(_, corners)| corners.iter().map(|corner| *corner as u32)).collect();
        if kept.len() < indices.len()
            && let Some(mut mesh) = meshes.get_mut(*mesh_id)
        {
            body.body_triangles -= (indices.len() - kept.len()) / 3;
            mesh.insert_indices(Indices::U32(kept));
        }
    }
    println!("pieces: {} in the model; {hidden_pieces} loose thin ones that are not hooves, claws or snout ({:.3} m2) are not drawn", pieces.len(), hidden_area.max(0.0));

    for ((triangle, thickness), hidden) in triangles.into_iter().zip(thickness).zip(hidden) {
        let [a, b, c] = triangle;
        let area = (b.0 - a.0).cross(c.0 - a.0).length() / 2.0;
        // A spike shrunk to a point by `retracted` has no area and gets no hair.
        if area < 1e-9 || hidden {
            continue;
        }
        let middle = (a.0 + b.0 + c.0) / 3.0;
        let colour = body.colour((a.2 + b.2 + c.2) / 3.0);
        if is_red(colour) && (max.z - middle.z) / length < 0.3 {
            snout += middle * area;
            snout_area += area;
        }
        if !furred(colour, middle) {
            bare += area;
            continue;
        }
        if thickness < THIN {
            thin += area;
            continue;
        }
        total += area;
        body.triangles.push(triangle);
        body.area_up_to.push(total);
    }
    if snout_area > 0.0 {
        body.snout = snout / snout_area;
    }
    println!(
        "body: {} triangles, {:.2} by {:.2} by {:.2} m, top of the back at {:.2} m, snout at {:.2} {:.2} {:.2}; fur on {:.2} m2 in {} triangles, bare by colour or height {:.2} m2, too thin {:.2} m2 (thickness took {:.0} ms)",
        body.body_triangles,
        max.x - min.x,
        max.y - min.y,
        length,
        back_top,
        body.snout.x,
        body.snout.y,
        body.snout.z,
        total,
        body.triangles.len(),
        bare,
        thin,
        thickness_ms
    );
    // The camera holds the creature with its quills out, and some room to dash into.
    let reach = 0.34;
    let (low, high) = (Vec3::new(min.x - reach, 0.0, min.z - reach), max + Vec3::splat(reach));
    framing.centre = (low + high) / 2.0;
    framing.radius = (high - low).length() / 2.0;
    framing.pivot = Vec3::new((min.x + max.x) / 2.0, back_top * 0.55, (min.z + max.z) / 2.0);
    commands.insert_resource(body);
}

/// Grows the hairs and builds them into one mesh. Each vertex carries its hair's root, the
/// body's normal and colour there, the comb direction, the lengths and two random numbers;
/// the shader does the rest. Returns the mesh, the number of quills and triangles, and every hair
/// as it was grown.
fn grow_coat(body: &Body, asked: usize) -> (Mesh, usize, usize, Vec<Seed>) {
    struct Site {
        root: Vec3,
        normal: Vec3,
        uv: Vec2,
        colour: [f32; 3],
        along_body: f32,
        tail: f32,
        leg: f32,
        guard_ground: bool,
        random: [f32; 9],
    }
    let mut rng = Rng(0x6B69_6C6E);
    let total = *body.area_up_to.last().unwrap();
    let length = body.max.z - body.min.z;
    let mut sites = Vec::with_capacity(asked);
    let mut triangle = 0;
    for hair in 0..asked {
        // One hair in each equal share of the area, so no part of the body is left bald or
        // crowded by chance; where in its share, and where in the triangle, is random.
        let share = (hair as f32 + rng.next()) / asked as f32 * total;
        while body.area_up_to[triangle] < share && triangle + 1 < body.triangles.len() {
            triangle += 1;
        }
        let [a, b, c] = body.triangles[triangle];
        let (mut u, mut v) = (rng.next(), rng.next());
        if u + v > 1.0 {
            (u, v) = (1.0 - u, 1.0 - v);
        }
        let w = 1.0 - u - v;
        let random = [0; 9].map(|_| rng.next());
        let root = a.0 * w + b.0 * u + c.0 * v;
        let face_normal = (b.0 - a.0).cross(c.0 - a.0).normalize_or_zero();
        let normal = (a.1 * w + b.1 * u + c.1 * v).try_normalize().unwrap_or(face_normal);
        // The colour is read a little toward the middle of the triangle, away from the edge of
        // its island in the picture, where the neighbouring island's colour bleeds in.
        let uv = a.2 * w + b.2 * u + c.2 * v;
        let colour = body.colour(uv.lerp((a.2 + b.2 + c.2) / 3.0, 0.2));
        if !furred(colour, root) {
            continue;
        }
        let along_body = (body.max.z - root.z) / length;
        let tail = smoothstep(body.back_top - 0.02, body.back_top + 0.07, root.y).max(smoothstep(0.88, 0.96, along_body) * smoothstep(0.3, 0.45, root.y));
        let leg = 1.0 - smoothstep(0.10, 0.26, root.y);
        // Quills grow on the back, the flanks and the tail: not the face, the belly or the legs.
        let guard_ground = along_body > 0.16 && normal.y > -0.3 && root.y > 0.22;
        sites.push(Site { root, normal, uv, colour, along_body, tail, leg, guard_ground, random });
    }
    // About as many quills whatever the hair count, so the spiked shape is the same and only
    // the soft coat gets thinner or thicker.
    let ground = sites.iter().filter(|site| site.guard_ground).count().max(1);
    let wanted = (asked as f32 * 0.045).clamp(1800.0, 4500.0);
    let guard_share = (wanted / ground as f32).min(0.5);
    // Fewer hairs are drawn wider, so the coat still covers the body.
    let width_scale = (PRESETS[2] as f32 / asked as f32).sqrt().clamp(0.7, 2.2);

    // Clumps: some hairs, evenly spread, are the middles of clumps about `CLUMP_SPACING` apart
    // whatever the hair count. Every hair belongs to the nearest middle on its own side of the
    // body and, when the coat is rough, leans toward that clump's tip.
    let every = ((sites.len() as f32 * CLUMP_SPACING * CLUMP_SPACING / total) as usize).max(1);
    let cell = |place: Vec3| (place / (CLUMP_SPACING * 1.5)).floor().as_ivec3();
    let mut middles: HashMap<IVec3, Vec<usize>> = HashMap::new();
    for index in (every / 2..sites.len()).step_by(every) {
        middles.entry(cell(sites[index].root)).or_default().push(index);
    }

    let (mut roots, mut normals, mut alongs) = (Vec::new(), Vec::new(), Vec::new());
    let (mut combs, mut rands, mut tints, mut indices) = (Vec::new(), Vec::new(), Vec::new(), Vec::<u32>::new());
    let (mut clumps, mut mores) = (Vec::new(), Vec::new());
    let mut seeds = Vec::with_capacity(sites.len());
    let mut quills = 0;
    for site in &sites {
        let [r_length, _, r_guard, r_a, r_b, r_quill, r_c, r_d, r_clump] = site.random;
        let home = cell(site.root);
        let mut nearest: Option<(f32, usize)> = None;
        for neighbour in (-1..=1).flat_map(|x| (-1..=1).flat_map(move |y| (-1..=1).map(move |z| IVec3::new(x, y, z)))) {
            for middle in middles.get(&(home + neighbour)).into_iter().flatten() {
                let distance = sites[*middle].root.distance(site.root);
                if sites[*middle].normal.dot(site.normal) > 0.3 && nearest.is_none_or(|(least, _)| distance < least) {
                    nearest = Some((distance, *middle));
                }
            }
        }
        let (to_middle, clump_random) = match nearest {
            Some((_, middle)) => ((sites[middle].root - site.root).clamp_length_max(CLUMP_SPACING * 1.2), sites[middle].random[8]),
            None => (Vec3::ZERO, r_clump),
        };
        let guard = site.guard_ground && r_guard < guard_share;
        quills += guard as usize;
        let face = 1.0 - smoothstep(0.08, 0.26, site.along_body);
        let belly = smoothstep(-0.2, -0.7, site.normal.y);
        // Short soft fur, a longer ruff round the face, longer on the tail, short on the legs.
        // A guard hair is grown exactly as a fine hair is: the same length, width, colour, comb
        // and clump. Only its quill length says what it can become, so combed it cannot be
        // told from the fur round it.
        let soft = 0.042 * (0.7 + 0.6 * r_length) * (1.0 + 0.8 * face + 1.2 * site.tail) * (1.0 - 0.5 * site.leg) * (1.0 - 0.3 * belly);
        let width = HAIR_WIDTH * width_scale * (0.8 + 0.4 * r_a);
        let quill = if guard { (0.17 + 0.20 * site.normal.y.max(0.0) + 0.12 * site.tail) * (0.7 + 0.6 * r_quill) } else { 0.0 };
        // Combed from head to tail and downward; up the tail. On the face, away from the snout,
        // so the ruff stands round it. The shader turns each hair off the comb, more the
        // rougher the coat.
        let grain = Vec3::new(0.0, -0.5, -1.0).lerp(Vec3::new(0.0, 1.0, -0.35), site.tail).lerp((site.root - body.snout).normalize_or_zero(), face).normalize();
        let mut comb = grain - site.normal * grain.dot(site.normal);
        if comb.length() < 0.25 {
            comb = Vec3::NEG_Y - site.normal * Vec3::NEG_Y.dot(site.normal);
        }
        let comb = comb.normalize_or(Vec3::NEG_Z);
        // A change of agitation starts behind the face and ends at the tip of the tail.
        // The shader adds the hair's own small delay, and can turn the change round.
        let delay = (smoothstep(0.1, 1.0, site.along_body) * 0.8 + site.tail * 0.15).clamp(0.0, 0.95);
        // Shaggy: the ruff round the face, the lower edge of the flanks, and the tail.
        let skirt = smoothstep(0.2, -0.3, site.normal.y) * (1.0 - site.leg) * (1.0 - belly * 0.6);
        let shag = (face * 0.75).max(site.tail * 0.7).max(skirt * 0.9);
        let tint = site.colour.map(to_linear);

        seeds.push(Seed {
            root: site.root,
            normal: site.normal,
            uv: site.uv,
            comb,
            soft,
            r1: r_a,
            r2: r_b,
            delay,
            quill,
            width,
            clump: to_middle,
            clump_random,
            shag,
            tail: site.tail,
            r3: r_c,
            r4: r_d,
        });
        let pieces = if guard { GUARD_PIECES } else { FINE_PIECES };
        let first = roots.len() as u32;
        for ring in 0..=pieces {
            let t = ring as f32 / pieces as f32;
            // Two vertices at each ring, one for each edge of the strip; one at the tip.
            let sides: &[f32] = if ring == pieces { &[0.0] } else { &[-1.0, 1.0] };
            for side in sides {
                roots.push(site.root.to_array());
                normals.push(site.normal.to_array());
                alongs.push([t, *side]);
                combs.push([comb.x, comb.y, comb.z, soft]);
                rands.push([r_a, r_b, delay, quill]);
                tints.push([tint[0], tint[1], tint[2], width]);
                clumps.push([to_middle.x, to_middle.y, to_middle.z, clump_random]);
                mores.push([shag, site.tail, r_c, r_d]);
            }
        }
        for ring in 0..pieces as u32 {
            let at = first + ring * 2;
            if ring + 1 == pieces as u32 {
                indices.extend([at, at + 1, at + 2]);
            } else {
                indices.extend([at, at + 1, at + 2, at + 1, at + 3, at + 2]);
            }
        }
    }
    let triangles = indices.len() / 3;
    let mesh = Mesh::new(PrimitiveTopology::TriangleList, RenderAssetUsages::RENDER_WORLD)
        .with_inserted_attribute(Mesh::ATTRIBUTE_POSITION, roots)
        .with_inserted_attribute(Mesh::ATTRIBUTE_NORMAL, normals)
        .with_inserted_attribute(Mesh::ATTRIBUTE_UV_0, alongs)
        .with_inserted_attribute(ATTRIBUTE_COMB, combs)
        .with_inserted_attribute(ATTRIBUTE_RAND, rands)
        .with_inserted_attribute(ATTRIBUTE_TINT, tints)
        .with_inserted_attribute(ATTRIBUTE_CLUMP, clumps)
        .with_inserted_attribute(ATTRIBUTE_MORE, mores)
        .with_inserted_indices(Indices::U32(indices));
    (mesh, quills, triangles, seeds)
}

fn grow(
    mut commands: Commands,
    body: Option<Res<Body>>,
    mut coat: ResMut<CoatState>,
    mut show: ResMut<Show>,
    mut meshes: ResMut<Assets<Mesh>>,
    model: Single<Entity, With<Model>>,
) {
    let Some(body) = body else { return };
    if let Some(entity) = coat.entity {
        let mut entity = commands.entity(entity);
        entity.insert(if coat.shown { Visibility::Inherited } else { Visibility::Hidden });
        if coat.shadows {
            entity.remove::<NotShadowCaster>();
        } else {
            entity.insert(NotShadowCaster);
        }
    }
    if !coat.rebuild {
        return;
    }
    coat.rebuild = false;
    let began = Instant::now();
    let (mesh, quills, triangles, seeds) = grow_coat(&body, coat.asked);
    coat.build_ms = began.elapsed().as_secs_f32() * 1000.0;
    let hairs = seeds.len();
    (coat.hairs, coat.quills, coat.triangles, coat.vertices) = (hairs, quills, triangles, mesh.count_vertices());
    (coat.seeds, coat.grown) = (seeds, coat.grown + 1);
    println!(
        "coat: asked for {} hairs, grew {} ({} of them quills) as {} triangles and {} vertices ({:.0} MB of vertices) in {:.0} ms",
        coat.asked,
        hairs,
        quills,
        triangles,
        coat.vertices,
        coat.vertices as f32 * VERTEX_BYTES / 1e6,
        coat.build_ms
    );
    if let Some(old) = coat.entity.take() {
        commands.entity(old).despawn();
    }
    // The hairs are a child of the model, so they go where it goes. Their mesh holds roots only,
    // so Bevy's box for it is the body's and must not be used to decide the coat is out of view.
    let entity = commands.spawn((Coat, Mesh3d(meshes.add(mesh)), MeshMaterial3d(coat.material.clone()), NoFrustumCulling, ChildOf(*model))).id();
    coat.entity = Some(entity);
    show.ready = true;
}

fn act(action: Action, show: &mut Show, motion: &mut Motion) {
    match action {
        Action::Gust => show.gust_began = show.clock,
        Action::AgitateTo(target, seconds) => {
            show.agitation_target = target;
            show.agitation_rate = (target - show.agitation).abs() / seconds.max(0.01);
        }
        Action::Agitate(agitation) => {
            (show.agitation, show.agitation_target) = (agitation, agitation);
            show.history.clear();
        }
        Action::Calm(calm) => show.calm = calm,
        Action::Debug(debug) => show.debug = debug,
        Action::Coat(_) => {}
        Action::LeanTo(lean) => show.lean = lean,
        Action::WaveToHead(to_head) => show.wave_to_head = to_head,
        Action::Mood(mood) => show.mood = mood,
        Action::Wind(strength) => show.wind_strength = strength,
        Action::Body(body) => show.body = body,
        Action::Dash | Action::Shake => {
            if motion.doing.is_none() {
                motion.doing = Some((action, show.clock));
            }
        }
    }
}

/// With `--keys`: presses the next key for one frame, every second and a half.
fn press_script(
    time: Res<Time>,
    script: Option<ResMut<Script>>,
    status: Res<Status>,
    mut input: ResMut<ButtonInput<KeyCode>>,
    mut exit: MessageWriter<AppExit>,
    show: Res<Show>,
) {
    let Some(mut script) = script else { return };
    if let Some(key) = script.held.take() {
        input.release(key);
    }
    if !show.ready {
        return;
    }
    script.since += time.delta_secs();
    if script.since < 1.5 {
        return;
    }
    script.since = 0.0;
    if script.next > 0 {
        println!("after {:>5}: {}", script.keys[script.next - 1].0, status.0);
    }
    let Some((_, key)) = script.keys.get(script.next) else {
        exit.write(AppExit::Success);
        return;
    };
    input.press(*key);
    script.held = Some(*key);
    script.next += 1;
}

#[expect(clippy::too_many_arguments)]
fn keys_pressed(
    time: Res<Time>,
    keys: Res<ButtonInput<KeyCode>>,
    mut show: ResMut<Show>,
    mut motion: ResMut<Motion>,
    mut coat: ResMut<CoatState>,
    mut look: ResMut<Look>,
    real: Res<Time<Real>>,
    bodies: Res<Bodies>,
    scripted: Option<Res<Script>>,
    mut exit: MessageWriter<AppExit>,
) {
    if keys.just_pressed(KeyCode::Escape) {
        exit.write(AppExit::Success);
    }
    if !show.ready {
        return;
    }
    // The look. None of these stops the loop.
    let mut said = None;
    if keys.just_pressed(KeyCode::KeyK) {
        if look.untouched {
            (look.untouched, look.tonemapper) = (false, START_TONEMAPPER);
        }
        look.hdr = !look.hdr;
        said = Some(match (look.hdr, look.ray_traced()) {
            (true, _) => "HDR pipeline: the camera draws a 16-bit float picture, bloom spreads its brightest parts, the tone mapper brings it into what the screen shows".to_string(),
            (false, false) => "plain LDR: the camera draws straight into the 8-bit picture; no bloom; with the tone mapper at none, anything brighter than white is cut off".to_string(),
            (false, true) => "LDR look: no bloom, the LDR tone mapper. The picture stays 16-bit float underneath, because the ray tracer cannot work without it".to_string(),
        });
    }
    if keys.just_pressed(KeyCode::KeyM) {
        look.untouched = false;
        let which = usize::from(look.hdr);
        look.tonemapper[which] = (look.tonemapper[which] + 1) % TONEMAPPERS.len();
        said = Some(format!("tone mapper of the {} picture: {}", if look.hdr { "HDR" } else { "LDR" }, TONEMAPPERS[look.tonemapper[which]].0));
    }
    let brighter = f32::from(keys.just_pressed(KeyCode::Equal)) - f32::from(keys.just_pressed(KeyCode::Minus));
    if brighter != 0.0 {
        look.stops = (look.stops + brighter * 0.5).clamp(-6.0, 6.0);
        said = Some(format!("exposure {:+.1} stops from Bevy's own (EV100 {:.1})", look.stops, EV100 - look.stops));
    }
    if keys.just_pressed(KeyCode::KeyE) {
        look.auto_exposure = !look.auto_exposure;
        said = Some(match (look.auto_exposure, look.hdr) {
            (true, true) => "auto exposure on: the camera meters the picture and adapts over a second or two".to_string(),
            (true, false) => "auto exposure is chosen, but it meters the 16-bit float picture: nothing changes until K turns the HDR pipeline on".to_string(),
            (false, _) => "auto exposure off".to_string(),
        });
    }
    if keys.just_pressed(KeyCode::KeyO) {
        said = Some(if look.display_hdr {
            format!(
                "the screen gets scRGB, an HDR signal: 16-bit float, 1.0 is SDR white and more is brighter. Light goes over white only from the HDR picture (K) with the tone mapper at none (M); the other tone mappers bring everything under white. - and = move the whole picture ({})",
                look.display
            )
        } else {
            format!(
                "HDR on the screen itself is not available in this build: Bevy 0.19.1 always opens a window's surface in an 8-bit sRGB format and has no setting for another, so the screen gets an SDR signal whatever K says. scrgb/build.sh makes a build that can ({})",
                look.display
            )
        });
    }
    if keys.just_pressed(KeyCode::KeyP) {
        said = Some(match (&look.rt_blocked, look.rt_asked) {
            (Some(why), _) => format!("ray tracing is not available here: {why}"),
            (None, false) => "the graphics card has not answered yet".to_string(),
            (None, true) => {
                look.rt = !look.rt;
                if look.rt {
                    "ray traced: the body and the ground are lit by Solari (sun, light from behind, sky, lamp, light bounced between them); the fur is drawn and lit as before, and only its stand-in casts a ray-traced shadow; one sample a pixel, no 4x MSAA".to_string()
                } else {
                    "rasterized: Bevy's lights and shadow maps, 4x MSAA".to_string()
                }
            }
        });
    }
    if keys.just_pressed(KeyCode::KeyI) {
        look.blend_frames = !look.blend_frames;
        said = Some(format!(
            "ray traced: {}{}",
            if look.blend_frames {
                "each frame is blended with the ones before it (TAA): the ray tracer's grain is smoothed, and moving fur smears, because the fur does not say how it moved"
            } else {
                "frames are not blended: the grain of one ray-traced sample a pixel is seen as it is, and nothing smears"
            },
            if look.ray_traced() { "" } else { " (seen only with ray tracing on: P)" }
        ));
    }
    if keys.just_pressed(KeyCode::KeyJ) {
        look.proxy = (look.proxy + 1) % PROXIES.len();
        said = Some(format!("in the ray tracer's scene the coat is: {}{}", PROXIES[look.proxy].0, if look.ray_traced() { "" } else { " (seen only with ray tracing on: P)" }));
    }
    if let Some(said) = said {
        if scripted.is_some() {
            println!("said: {said}");
        }
        (look.said, look.said_at) = (said, real.elapsed_secs());
    }
    // Anything done by hand stops the loop from undoing it; Space starts the loop again.
    let mut by_hand = false;
    if keys.just_pressed(KeyCode::KeyB) {
        let (target, seconds) = if show.agitation_target > 0.5 { (0.0, RUN_DOWN_SECONDS) } else { (1.0, RUN_UP_SECONDS) };
        (show.agitation_target, show.agitation_rate) = (target, 1.0 / seconds);
        by_hand = true;
    }
    for (key, (_, agitation)) in [KeyCode::Digit1, KeyCode::Digit2, KeyCode::Digit3, KeyCode::Digit4, KeyCode::Digit5].into_iter().zip(STAGES) {
        if keys.just_pressed(key) {
            act(Action::AgitateTo(agitation, JUMP_SECONDS), &mut show, &mut motion);
            by_hand = true;
        }
    }
    // A scripted key is down for one frame; it counts as a quarter of a second of holding.
    let held = if scripted.is_some() { 0.25 } else { time.delta_secs() };
    let way = f32::from(keys.pressed(KeyCode::ArrowUp)) - f32::from(keys.pressed(KeyCode::ArrowDown));
    if way != 0.0 {
        show.agitation_target = (show.agitation_target + way * 0.3 * held).clamp(0.0, 1.0);
        show.agitation_rate = 1.0;
        by_hand = true;
    }
    if keys.just_pressed(KeyCode::KeyW) {
        show.wind_on = !show.wind_on;
        by_hand = true;
    }
    let stronger = f32::from(keys.just_pressed(KeyCode::BracketRight)) - f32::from(keys.just_pressed(KeyCode::BracketLeft));
    if stronger != 0.0 {
        show.wind_strength = (show.wind_strength + stronger * 0.25).clamp(0.0, WIND_MOST);
        by_hand = true;
    }
    // How the coat and the quills look. None of these stops the loop: they are for comparing
    // while it runs.
    if keys.just_pressed(KeyCode::KeyF) {
        show.calm = (show.calm + 1) % CALM.len();
    }
    if keys.just_pressed(KeyCode::KeyQ) {
        show.lean = match show.lean {
            Lean::Forward => Lean::Outward,
            Lean::Outward => Lean::Rearward,
            Lean::Rearward => Lean::Forward,
        };
    }
    let more_lean = f32::from(keys.just_pressed(KeyCode::Period)) - f32::from(keys.just_pressed(KeyCode::Comma));
    if more_lean != 0.0 {
        show.lean_amount = (show.lean_amount + more_lean * 0.2).clamp(0.2, 2.0);
    }
    if keys.just_pressed(KeyCode::KeyV) {
        show.wave_to_head = !show.wave_to_head;
    }
    if keys.just_pressed(KeyCode::KeyN) {
        show.body = (show.body + 1) % bodies.0.len();
    }
    if keys.just_pressed(KeyCode::KeyL) {
        show.mood = (show.mood + 1) % MOODS.len();
    }
    for (key, action) in [(KeyCode::KeyG, Action::Gust), (KeyCode::KeyD, Action::Dash), (KeyCode::KeyS, Action::Shake)] {
        if keys.just_pressed(key) {
            act(action, &mut show, &mut motion);
            by_hand = true;
        }
    }
    if keys.just_pressed(KeyCode::KeyH) {
        coat.preset = if coat.preset >= PRESETS.len() { 0 } else { (coat.preset + 1) % PRESETS.len() };
        coat.asked = PRESETS[coat.preset];
        coat.rebuild = true;
    }
    if keys.just_pressed(KeyCode::KeyC) {
        coat.shadows = !coat.shadows;
    }
    if keys.just_pressed(KeyCode::KeyX) {
        show.debug = (show.debug + 1) % 3;
    }
    if keys.just_pressed(KeyCode::KeyT) {
        show.turntable = !show.turntable;
    }
    if keys.just_pressed(KeyCode::KeyR) {
        show.angle = 0.0;
    }
    if keys.just_pressed(KeyCode::Space) {
        show.loop_paused = !show.loop_paused;
    } else if by_hand {
        show.loop_paused = true;
    }
}

/// Combed in a light breeze; the wind rises and the coat ruffles; a gust; a dash and a stop;
/// agitation climbs slowly through ruffled, rough and hackles; the spikes sweep forward; held;
/// back down through every stage to combed; a shake; then again.
fn auto_loop(time: Res<Time>, mut show: ResMut<Show>, mut motion: ResMut<Motion>) {
    if show.loop_paused || !show.ready {
        return;
    }
    let before = show.loop_clock;
    let now = before + time.delta_secs();
    for (at, action) in LOOP {
        if before <= at && now > at {
            act(action, &mut show, &mut motion);
        }
    }
    show.loop_clock = if now >= LOOP_PERIOD { 0.0 } else { now };
}

/// Moves the creature, steps the springs the fur hangs on, and tells the shader.
#[expect(clippy::too_many_arguments)]
fn animate(
    time: Res<Time>,
    real: Res<Time<Real>>,
    body: Option<Res<Body>>,
    coat: Res<CoatState>,
    look: Res<Look>,
    framing: Res<Framing>,
    mut show: ResMut<Show>,
    mut motion: ResMut<Motion>,
    mut frame_times: ResMut<FrameTimes>,
    mut materials: ResMut<Assets<FurMaterial>>,
    mut model: Single<&mut Transform, With<Model>>,
) {
    frame_times.0.push_back(real.delta_secs());
    if frame_times.0.len() > 90 {
        frame_times.0.pop_front();
    }
    let Some(body) = body else { return };
    if !show.ready {
        return;
    }
    let dt = time.delta_secs();
    show.clock += dt;
    let step = show.agitation_rate * dt;
    show.agitation += (show.agitation_target - show.agitation).clamp(-step, step);
    // A change travels along the body: the far end gets what the near end had `SWEEP_SECONDS`
    // ago, and the two places between what it had a third and two thirds of that ago.
    let (clock, agitation) = (show.clock, show.agitation);
    show.history.push_back((clock, agitation));
    while show.history.len() > 2 && show.history[1].0 < clock - SWEEP_SECONDS {
        show.history.pop_front();
    }
    let wave = [0.0, 1.0, 2.0, 3.0].map(|third| {
        let wanted = clock - SWEEP_SECONDS * third / 3.0;
        show.history.iter().rev().find(|(at, _)| *at <= wanted).unwrap_or(&show.history[0]).1
    });
    show.wave = wave;
    let wind_wanted = if show.wind_on { show.wind_strength } else { 0.0 };
    show.wind_now += (wind_wanted - show.wind_now) * (1.0 - (-dt * 3.0).exp());

    // What the creature is doing.
    if let Some((action, began)) = motion.doing {
        let since = show.clock - began;
        match action {
            Action::Dash => {
                // Up to speed in 0.15 s, 0.25 s at speed, stopped dead in 0.07 s: 1.26 m.
                // Then it stands, and walks back so the next dash starts from the same place.
                let speed = 3.5 * (since / 0.15).min(1.0) * (1.0 - (since - 0.40) / 0.07).clamp(0.0, 1.0);
                if since < 0.47 {
                    motion.speed_along = speed;
                    motion.place.z += speed * dt;
                    motion.return_from = motion.place;
                } else if since < 1.9 {
                    motion.speed_along = 0.0;
                } else {
                    let back = smoothstep(1.9, 4.2, since);
                    motion.place = motion.return_from * (1.0 - back);
                    if since >= 4.2 {
                        motion.doing = None;
                    }
                }
            }
            Action::Shake => {
                let swell = (since / 1.2 * std::f32::consts::PI).sin().max(0.0);
                motion.yaw = 0.30 * swell * (since * 4.5 * std::f32::consts::TAU).sin();
                motion.roll = 0.14 * swell * (since * 4.5 * std::f32::consts::TAU + 1.3).sin();
                if since >= 1.2 {
                    (motion.yaw, motion.roll, motion.doing) = (0.0, 0.0, None);
                }
            }
            _ => motion.doing = None,
        }
    }
    let turn = Quat::from_rotation_y(motion.yaw) * Quat::from_rotation_z(motion.roll);
    // It turns about the middle of its body, not about the ground between its feet.
    **model = Transform { translation: motion.place + framing.pivot - turn * framing.pivot, rotation: turn, ..default() };

    if dt > 0.0 {
        let velocity = (motion.place - motion.last_place) / dt;
        let (axis, angle) = (turn * motion.last_turn.inverse()).to_axis_angle();
        let spin = axis * angle / dt;
        let (push, twist) = ((velocity - motion.velocity) / dt, (spin - motion.spin) / dt);
        // The fur is two springs: a slow loose one and a quicker one. Each hair mixes them.
        for (index, (hertz, damping)) in [(2.1, 0.16), (3.3, 0.24)].into_iter().enumerate() {
            motion.lag[index].step(push, hertz, damping, dt);
            motion.turn[index].step(twist, hertz, damping, dt);
        }
        let ease = 1.0 - (-dt * 14.0).exp();
        motion.steady_velocity = motion.steady_velocity.lerp(velocity, ease);
        motion.steady_spin = motion.steady_spin.lerp(spin, ease);
        (motion.velocity, motion.spin, motion.last_place, motion.last_turn) = (velocity, spin, motion.place, turn);
        // A jolt startles the coat: it ruffles at once and settles over a second or two.
        let jolt = (push.length() * 0.006 + twist.length() * 0.003).min(STARTLE_MOST);
        show.startle = jolt.max(show.startle * (-dt / 0.9).exp());
    }
    // How far a spring's stretch bends a hair, and how far steady speed through the air does.
    let stiffness = |hertz: f32, give: f32| (hertz * std::f32::consts::TAU).powi(2) * give;
    let drag = 0.2;
    let lag = [0, 1].map(|index| motion.lag[index].at * stiffness([2.1, 3.3][index], [0.045, 0.03][index]) - motion.steady_velocity * drag);
    let turned = [0, 1].map(|index| motion.turn[index].at * stiffness([2.1, 3.3][index], [0.02, 0.014][index]) - motion.steady_spin * drag);

    let Some(mut material) = materials.get_mut(&coat.material) else { return };
    let mood = &MOODS[show.mood];
    let length = body.max.z - body.min.z;
    let spine = |along: f32| Vec3::new(framing.pivot.x, framing.pivot.y, body.max.z - along * length);
    material.before = material.params.clone();
    material.params = FurParams {
        wind: WIND_TO.normalize().extend(show.wind_now),
        gust: Vec4::new(show.clock - show.gust_began - 0.5, GUST_SPEED, GUST_SECONDS, show.clock),
        lag_a: lag[0].extend(0.0),
        lag_b: lag[1].extend(0.0),
        turn_a: turned[0].extend(0.0),
        turn_b: turned[1].extend(0.0),
        centre: (model.translation + turn * framing.pivot).extend(0.0),
        spine_a: spine(0.32).extend(1.0),
        spine_b: spine(0.68).extend(if look.ray_traced() { LEAST_PIXELS_RT } else { LEAST_PIXELS }),
        quill: Vec4::new(1.0, QUILL_WIDTH, f32::from(show.debug), 0.004),
        style: Vec4::new(
            CALM[show.calm].1,
            match show.lean {
                Lean::Forward => show.lean_amount,
                Lean::Outward => 0.0,
                Lean::Rearward => -show.lean_amount,
            },
            f32::from(show.wave_to_head),
            f32::from(show.lean != Lean::Outward),
        ),
        rim_to: mood.back_from.normalize().extend(mood.rim),
        rim_colour: Vec3::from(mood.back).extend(0.0),
        agitation: Vec4::from_array(show.wave),
        extra: Vec4::new(show.startle, 0.0, 0.0, 0.0),
    };
}

/// Sets the lights, the air and the ground to the lighting chosen, and keeps the slow clouds and
/// the lamp's flicker going.
#[expect(clippy::too_many_arguments, clippy::type_complexity)]
fn light(
    show: Res<Show>,
    scenery: Res<Scenery>,
    mut set: Local<Option<usize>>,
    mut clear: ResMut<ClearColor>,
    mut ambient: ResMut<GlobalAmbientLight>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    mut sun: Single<(&mut DirectionalLight, &mut Transform), (With<Sun>, Without<BackLight>)>,
    mut back: Single<(&mut DirectionalLight, &mut Transform), (With<BackLight>, Without<Sun>)>,
    mut lamp: Single<&mut PointLight, With<Lamp>>,
    mut shown: Query<(&mut Visibility, Option<&Sky>, Has<PlainGround>, Has<Lamp>, Has<BackLight>), Or<(With<Sky>, With<PlainGround>, With<MoodGround>, With<Lamp>, With<BackLight>)>>,
) {
    let mood = &MOODS[show.mood];
    let colour = |[r, g, b]: [f32; 3]| Color::linear_rgb(r, g, b);
    // Slow clouds over the sun; a lamp that flickers as a flame does.
    let clouds = 0.5 + 0.3 * (show.clock * 0.31).sin() + 0.2 * (show.clock * 0.83 + 2.0).sin();
    sun.0.illuminance = mood.sun_lux * (1.0 - mood.drift * clouds.clamp(0.0, 1.0));
    lamp.intensity = mood.lamp * flame(show.clock);
    if *set == Some(show.mood) {
        return;
    }
    *set = Some(show.mood);
    sun.0.color = colour(mood.sun);
    *sun.1 = Transform::default().looking_to(-mood.sun_from, Vec3::Y);
    back.0.color = colour(mood.back);
    back.0.illuminance = mood.back_lux;
    *back.1 = Transform::default().looking_to(-mood.back_from, Vec3::Y);
    *ambient = GlobalAmbientLight { color: colour(mood.ambient), brightness: mood.ambient_brightness, ..default() };
    clear.0 = if mood.plain { scene::BACKGROUND } else { colour(mood.sky_horizon) };
    if let Some(mut ground) = materials.get_mut(&scenery.ground) {
        ground.base_color = colour(mood.ground);
    }
    for (mut visibility, sky, plain_ground, lamp, back_light) in &mut shown {
        let on = match sky {
            Some(sky) => sky.0 == show.mood,
            None if plain_ground => mood.plain,
            None if lamp => mood.lamp > 0.0,
            None if back_light => mood.back_lux > 0.0,
            None => !mood.plain,
        };
        *visibility = if on { Visibility::Visible } else { Visibility::Hidden };
    }
}

/// How bright the lamp's flame is at a moment, about 1.
fn flame(clock: f32) -> f32 {
    0.82 + 0.10 * (clock * 9.1).sin() + 0.06 * (clock * 23.7 + 1.0).sin() + 0.04 * (clock * 41.3).sin()
}

/// Asks the graphics card, once, whether it can do what Bevy's ray tracer needs.
fn ask_graphics_card(device: Option<Res<RenderDevice>>, found: Res<SurfaceFound>, mut look: ResMut<Look>) {
    if let Some(surface) = found.0.lock().unwrap().take() {
        println!("display: the window's surface offers {surface}");
        look.display = format!("the window's surface offers {surface}; {}", look.display);
    }
    if look.rt_asked {
        return;
    }
    let Some(device) = device else { return };
    look.rt_asked = true;
    let missing = SolariPlugins::required_wgpu_features().difference(device.features());
    if missing.is_empty() {
        println!("ray tracing: the graphics card and its driver have what Bevy's Solari needs ({:?})", SolariPlugins::required_wgpu_features());
    } else {
        look.rt_blocked = Some(format!("the graphics card or its driver lacks {missing:?}, which Bevy's Solari needs"));
        println!("ray tracing: not available here: {}", look.rt_blocked.as_ref().unwrap());
    }
}

/// In the render world, once, before Bevy opens the window's surface: opens it, asks which
/// formats it offers, and lets it go. Bevy then takes an 8-bit sRGB one whatever is offered.
fn ask_surface(windows: Res<ExtractedWindows>, instance: Res<RenderInstance>, adapter: Res<RenderAdapter>, found: Res<SurfaceFound>, mut done: Local<bool>) {
    if *done {
        return;
    }
    let Some(window) = windows.windows.values().next() else { return };
    *done = true;
    let target = wgpu::SurfaceTargetUnsafe::RawHandle { raw_display_handle: Some(window.handle.get_display_handle()), raw_window_handle: window.handle.get_window_handle() };
    // SAFETY: the handles are of a window that is there, as in Bevy's own `create_surfaces`, and
    // the surface is let go before this returns.
    let said = match unsafe { instance.create_surface_unsafe(target) } {
        Ok(surface) => format!("{:?}", surface.get_capabilities(&adapter).formats),
        Err(error) => format!("nothing that could be read ({error})"),
    };
    *found.0.lock().unwrap() = Some(said);
}

/// What Hyprland says each monitor is set to. Only read.
fn monitors_said() -> String {
    let Ok(listed) = std::process::Command::new("hyprctl").args(["monitors", "-j"]).output() else { return "the compositor is not Hyprland or could not be asked".to_string() };
    let Ok(serde_json::Value::Array(monitors)) = serde_json::from_slice(&listed.stdout) else { return "Hyprland's answer could not be read".to_string() };
    let each: Vec<String> = monitors
        .iter()
        .map(|monitor| {
            let text = |key: &str| monitor.get(key).and_then(|value| value.as_str()).unwrap_or("?").to_string();
            format!("{} is set to colour preset \"{}\", format {}", text("name"), text("colorManagementPreset"), text("currentFormat"))
        })
        .collect();
    format!("Hyprland: {}", each.join("; "))
}

/// Until the picture is chosen by hand, it is what the lighting had before there was a choice.
fn look_untouched(show: Res<Show>, mut look: ResMut<Look>) {
    if !look.untouched {
        return;
    }
    let plain = MOODS[show.mood].plain;
    // TonyMcMapface is Bevy's own tone mapper, which the studio lighting had.
    let tonemapper = [if plain { 6 } else { START_TONEMAPPER[0] }, START_TONEMAPPER[1]];
    if look.hdr == plain || look.tonemapper != tonemapper {
        (look.hdr, look.tonemapper) = (!plain, tonemapper);
    }
}

/// Sets every camera to the look chosen: the HDR pipeline or the plain picture, the tone mapper,
/// the exposure, the lighting's fog and bloom, and the ray tracer.
fn look_apply(mut commands: Commands, show: Res<Show>, look: Res<Look>, cameras: Query<Entity, With<Camera3d>>, mut set: Local<Option<(usize, bool, bool, usize, i32, bool, bool)>>) {
    let ray_traced = look.ray_traced();
    let tonemapper = look.tonemapper[usize::from(look.hdr)];
    let now = (show.mood, look.hdr, ray_traced, tonemapper, (look.stops * 100.0) as i32, look.auto_exposure, look.blend_frames);
    if *set == Some(now) {
        return;
    }
    *set = Some(now);
    let mood = &MOODS[show.mood];
    let colour = |[r, g, b]: [f32; 3]| Color::linear_rgb(r, g, b);
    for camera in &cameras {
        let mut camera = commands.entity(camera);
        camera.insert((TONEMAPPERS[tonemapper].1, Exposure { ev100: EV100 - look.stops }));
        if mood.plain {
            camera.remove::<DistanceFog>();
        } else {
            camera.insert(DistanceFog {
                color: colour(mood.sky_horizon),
                directional_light_color: colour(mood.sun.map(|channel| channel * 0.35)),
                directional_light_exponent: 12.0,
                falloff: FogFalloff::ExponentialSquared { density: mood.fog_density },
            });
        }
        if look.float_picture() {
            camera.insert(Hdr);
        } else {
            camera.remove::<Hdr>();
        }
        // Bloom and auto exposure work on the 16-bit picture and belong to the HDR look.
        if look.hdr && mood.bloom > 0.0 {
            camera.insert(Bloom { intensity: mood.bloom, ..Bloom::NATURAL });
        } else {
            camera.remove::<Bloom>();
        }
        if look.hdr && look.auto_exposure {
            camera.insert(AutoExposure::default());
        } else {
            camera.remove::<AutoExposure>();
        }
        if ray_traced {
            // Solari asks for one sample a pixel and a picture its compute shaders can write to.
            camera.insert((SolariLighting::default(), Msaa::Off, CameraMainTextureUsages::default().with(TextureUsages::STORAGE_BINDING)));
        } else {
            camera.remove::<(SolariLighting, DeferredPrepass, DepthPrepass, MotionVectorPrepass, DeferredPrepassDoubleBuffer, DepthPrepassDoubleBuffer)>();
            camera.insert((Msaa::default(), CameraMainTextureUsages::default()));
        }
        if ray_traced && look.blend_frames {
            camera.insert(TemporalAntiAliasing::default());
        } else {
            camera.remove::<(TemporalAntiAliasing, TemporalJitter, MipBias)>();
        }
    }
}

/// A copy of a mesh as Solari takes one: positions, normals, UVs and tangents and nothing else,
/// 32-bit indices. A body with a `retracted` shape is copied in that shape.
fn rt_copy(mesh: &Mesh) -> Option<Mesh> {
    let Some(VertexAttributeValues::Float32x3(positions)) = mesh.attribute(Mesh::ATTRIBUTE_POSITION) else { return None };
    let mut positions = positions.clone();
    let mut normals = match mesh.attribute(Mesh::ATTRIBUTE_NORMAL) {
        Some(VertexAttributeValues::Float32x3(normals)) => normals.clone(),
        _ => vec![[0.0, 1.0, 0.0]; positions.len()],
    };
    let uvs = match mesh.attribute(Mesh::ATTRIBUTE_UV_0) {
        Some(VertexAttributeValues::Float32x2(uvs)) => uvs.clone(),
        _ => vec![[0.0, 0.0]; positions.len()],
    };
    let retracted = mesh.morph_target_names().and_then(|names| names.iter().position(|name| name == "retracted"));
    if let Some(moves) = retracted.and_then(|target| mesh.morph_targets().map(|all| &all[target * positions.len()..(target + 1) * positions.len()])) {
        for (vertex, moved) in moves.iter().enumerate() {
            positions[vertex] = (Vec3::from(positions[vertex]) + moved.position).to_array();
            normals[vertex] = (Vec3::from(normals[vertex]) + moved.normal).normalize_or(Vec3::Y).to_array();
        }
    }
    let indices: Vec<u32> = match mesh.indices() {
        Some(indices) => indices.iter().map(|index| index as u32).collect(),
        None => (0..positions.len() as u32).collect(),
    };
    let count = positions.len();
    let mut copy = Mesh::new(PrimitiveTopology::TriangleList, RenderAssetUsages::RENDER_WORLD)
        .with_inserted_attribute(Mesh::ATTRIBUTE_POSITION, positions)
        .with_inserted_attribute(Mesh::ATTRIBUTE_NORMAL, normals)
        .with_inserted_attribute(Mesh::ATTRIBUTE_UV_0, uvs)
        .with_inserted_indices(Indices::U32(indices));
    if copy.generate_tangents().is_err() {
        copy.insert_attribute(Mesh::ATTRIBUTE_TANGENT, vec![[1.0, 0.0, 0.0, 1.0]; count]);
    }
    Some(copy)
}

/// The sky as the ray tracer can have it: a dome that glows evenly, facing in, with a hole
/// toward each light, because Solari's rays to the sun would stop at the dome. Also returns the
/// share of the sky that is left, so that what is left can glow that much more.
fn sky_dome(holes: &[Vec3]) -> (Mesh, f32) {
    const SEGMENTS: usize = 24;
    const RINGS: usize = 6;
    // Far enough away that from anywhere on the ground the sun is seen through the hole made for
    // it. Not further: at 4,000 m a ray-traced frame took ten times as long, and why was not found.
    const RADIUS: f32 = 1000.0;
    let way = |ring: usize, segment: usize| {
        // From a little below the horizon to straight up.
        let up = -0.08 + (std::f32::consts::FRAC_PI_2 + 0.08) * ring as f32 / RINGS as f32;
        let round = std::f32::consts::TAU * segment as f32 / SEGMENTS as f32;
        Vec3::new(up.cos() * round.cos(), up.sin(), up.cos() * round.sin())
    };
    let (mut positions, mut normals, mut indices) = (Vec::new(), Vec::new(), Vec::<u32>::new());
    let (mut all, mut left) = (0.0, 0.0);
    for ring in 0..RINGS {
        for segment in 0..SEGMENTS {
            let corners = [way(ring, segment), way(ring, segment + 1), way(ring + 1, segment + 1), way(ring + 1, segment)];
            let middle = (corners[0] + corners[1] + corners[2] + corners[3]).normalize();
            // How much of the sky this piece is: less the nearer the top.
            let size = (1.0 - middle.y * middle.y).max(0.0).sqrt();
            all += size;
            if holes.iter().any(|hole| middle.dot(hole.normalize()) > 0.94) {
                continue;
            }
            left += size;
            let first = positions.len() as u32;
            for corner in corners {
                positions.push((corner * RADIUS).to_array());
                normals.push((-corner).to_array());
            }
            indices.extend([first, first + 1, first + 2, first, first + 2, first + 3]);
        }
    }
    let count = positions.len();
    let dome = Mesh::new(PrimitiveTopology::TriangleList, RenderAssetUsages::RENDER_WORLD)
        .with_inserted_attribute(Mesh::ATTRIBUTE_POSITION, positions)
        .with_inserted_attribute(Mesh::ATTRIBUTE_NORMAL, normals)
        .with_inserted_attribute(Mesh::ATTRIBUTE_UV_0, vec![[0.0, 0.0]; count])
        .with_inserted_attribute(Mesh::ATTRIBUTE_TANGENT, vec![[1.0, 0.0, 0.0, 1.0]; count])
        .with_inserted_indices(Indices::U32(indices));
    (dome, left / all)
}

const LAMP_AT: Vec3 = Vec3::new(1.25, 0.45, 0.9);
const LAMP_RADIUS: f32 = 0.05;
const LAMP_COLOUR: [f32; 3] = [1.0, 0.42, 0.13];

/// Keeps the ray tracer's scene: with ray tracing on, the body and the ground that is shown are
/// given to it and drawn deferred, which is how Solari lights them; a dome stands in for the
/// light from all sides and a glowing ball for the lamp, because Solari knows directional lights
/// and glowing meshes only. With it off, all of that is taken back.
#[expect(clippy::too_many_arguments, clippy::type_complexity)]
fn rt_scene(
    mut commands: Commands,
    look: Res<Look>,
    show: Res<Show>,
    body: Option<Res<Body>>,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    model: Query<Entity, With<Model>>,
    children: Query<&Children>,
    parts: Query<(&Mesh3d, Has<RtGiven>), (With<MeshMaterial3d<StandardMaterial>>, Without<Coat>, Without<Sky>)>,
    grounds: Query<(Entity, &Mesh3d, Has<PlainGround>, Has<RtGiven>), Or<(With<PlainGround>, With<MoodGround>)>>,
    extras: Query<Entity, With<RtOnly>>,
    lamps: Query<&RtLamp>,
    mut haze: Single<&mut Visibility, With<Haze>>,
    mut made: Local<(Option<(bool, usize)>, Option<(bool, usize)>)>,
) {
    let on = look.ray_traced();
    let mood = &MOODS[show.mood];
    haze.set_if_neq(if on && !mood.plain { Visibility::Visible } else { Visibility::Hidden });
    // Solari lights what is drawn deferred, and nothing draws deferred without it. The skies are
    // unlit pictures and stay as they are.
    if made.0 != Some((on, materials.len())) {
        made.0 = Some((on, materials.len()));
        let wanted: Vec<_> = materials
            .iter()
            .map(|(id, material)| (id, if on && !material.unlit { OpaqueRendererMethod::Deferred } else { OpaqueRendererMethod::Forward }))
            .filter(|(id, wanted)| materials.get(*id).is_some_and(|material| material.opaque_render_method != *wanted))
            .collect();
        for (id, method) in wanted {
            if let Some(mut material) = materials.get_mut(id) {
                material.opaque_render_method = method;
            }
        }
    }
    let mut give = |commands: &mut Commands, entity: Entity, mesh: &Mesh3d, given: bool, wanted: bool| {
        if wanted && !given {
            if let Some(copy) = meshes.get(&mesh.0).and_then(rt_copy) {
                commands.entity(entity).insert((RaytracingMesh3d(meshes.add(copy)), RtGiven));
            }
        } else if !wanted && given {
            commands.entity(entity).remove::<(RaytracingMesh3d, RtGiven)>();
        }
    };
    // The body, once its tufts have been flattened.
    for model in &model {
        for entity in children.iter_descendants(model) {
            if let Ok((mesh, given)) = parts.get(entity) {
                give(&mut commands, entity, mesh, given, on && body.is_some());
            }
        }
    }
    // A ground that is hidden would still be in the ray tracer's scene.
    for (entity, mesh, plain, given) in &grounds {
        give(&mut commands, entity, mesh, given, on && plain == mood.plain);
    }
    if made.1 != Some((on, show.mood)) {
        made.1 = Some((on, show.mood));
        for extra in &extras {
            commands.entity(extra).despawn();
        }
        if on && mood.ambient_brightness > 0.0 {
            let mut holes = vec![mood.sun_from];
            if mood.back_lux > 0.0 {
                holes.push(mood.back_from);
            }
            // As bright as the light from all sides that Bevy's own lighting adds to everything.
            let (dome, left) = sky_dome(&holes);
            let glow = materials.add(StandardMaterial {
                base_color: Color::BLACK,
                emissive: LinearRgba::rgb(mood.ambient[0], mood.ambient[1], mood.ambient[2]) * (mood.ambient_brightness / left),
                ..default()
            });
            commands.spawn((RtOnly, RtSky, RaytracingMesh3d(meshes.add(dome)), MeshMaterial3d(glow), Transform::default()));
        }
        if on && mood.lamp > 0.0 {
            let glow = materials.add(StandardMaterial { base_color: Color::BLACK, ..default() });
            if let Some(ball) = rt_copy(&Sphere::new(LAMP_RADIUS).mesh().ico(1).unwrap()) {
                commands.spawn((RtOnly, RtLamp(glow.clone()), RaytracingMesh3d(meshes.add(ball)), MeshMaterial3d(glow), Transform::from_translation(LAMP_AT)));
            }
        }
    }
    // A point light of so many lumens, as a ball of that radius glowing evenly.
    for lamp in &lamps {
        if let Some(mut glow) = materials.get_mut(&lamp.0) {
            let nits = mood.lamp * flame(show.clock) / (4.0 * std::f32::consts::PI * std::f32::consts::PI * LAMP_RADIUS * LAMP_RADIUS);
            glow.emissive = LinearRgba::rgb(LAMP_COLOUR[0], LAMP_COLOUR[1], LAMP_COLOUR[2]) * nits;
        }
    }
}

fn mix(a: f32, b: f32, t: f32) -> f32 {
    a + (b - a) * t
}

/// One hair this frame, as `place` in `fur_strands.wgsl` works it out, on the processor.
struct Shape {
    root: Vec3,
    normal: Vec3,
    calm: Vec3,
    curl: Vec3,
    up: Vec3,
    bend: Vec3,
    sweep: Vec3,
    pull: Vec3,
    kink_a: Vec3,
    kink_b: Vec3,
    kink: Vec2,
    stand: f32,
    soft: f32,
    length: f32,
    floor: f32,
    /// Width at the root, metres, and how much of a quill the hair is.
    width: f32,
    quill: f32,
}

impl Shape {
    /// `hair_direction` of the shader.
    fn direction(&self, t: f32) -> Vec3 {
        let wobble = self.kink_a * (t * self.kink.x + self.kink.y).sin() + self.kink_b * (t * self.kink.x * 0.8 + self.kink.y * 1.7).cos();
        let soft = (self.calm + ((self.curl + self.pull) * t + wobble) * self.soft).normalize();
        let mut direction = (soft.lerp(self.up, self.stand) + (self.sweep * self.stand + self.bend) * t).normalize();
        let out = direction.dot(self.normal);
        direction = (direction + self.normal * (0.06 - out).max(0.0)).normalize();
        let least = (self.floor - self.root.y) / (self.length * t.max(0.02));
        if direction.y < least && least < 0.95 {
            let level = Vec2::new(direction.x, direction.z);
            let level = level / level.length().max(0.0001) * (1.0 - least * least).max(0.0).sqrt();
            direction = Vec3::new(level.x, least, level.y);
        }
        direction
    }

    fn point(&self, t: f32) -> Vec3 {
        self.root + self.direction(t) * (self.length * t)
    }

    /// `place` of the shader, up to where the strip is turned to the camera. Line for line; a
    /// change there must be made here.
    fn of(seed: &Seed, fur: &FurParams, to_world: &Affine3A) -> Shape {
        let step = |edge: f32, x: f32| f32::from(x >= edge);
        let root = to_world.transform_point3(seed.root);
        let normal = to_world.transform_vector3(seed.normal).normalize();
        let (r1, r2, r3, r4) = (seed.r1, seed.r2, seed.r3, seed.r4);
        let (shag, tail, clump_random) = (seed.shag, seed.tail, seed.clump_random);
        let is_guard = step(0.0001, seed.quill);
        let time = fur.gust.w;

        let wind_to = fur.wind.truncate();
        let wind = fur.wind.w;
        let wind_across = wind_to.cross(Vec3::Y).normalize();
        let along_wind = root.dot(wind_to);
        let across_wind = root.dot(wind_across);
        let swell = 0.5 + 0.5 * (along_wind * 2.4 - time * 1.9 + (across_wind * 2.1 + time * 0.7).sin() * 1.4).sin();
        let crest = 0.5 + 0.5 * (along_wind * 6.5 - time * 6.8 + (across_wind * 3.3 - time * 0.5).sin() * 1.1 + root.y * 1.8).sin();
        let band = crest * crest * crest * crest * (0.6 + 0.4 * (time * 0.83 + 1.0).sin());
        let ripple = (along_wind * 14.0 - time * 8.5 + across_wind * 9.0 + root.y * 6.0).sin();
        let field = 0.25 + 0.4 * swell + band + 0.1 * ripple;
        let since_front = (fur.gust.x - along_wind / fur.gust.y) / fur.gust.z;
        let gust = smoothstep(0.0, 0.2, since_front) * (1.0 - smoothstep(0.45, 1.0, since_front));
        let exposed = (0.55 + 0.45 * (0.5 - 0.5 * normal.dot(wind_to)).clamp(0.0, 1.0)) * (1.0 + 0.8 * tail);

        let reaches = (mix(seed.delay, 0.95 - seed.delay, fur.style.z) + r2 * 0.05).clamp(0.0, 1.0) * 3.0;
        let mut arrived = mix(fur.agitation.x, fur.agitation.y, reaches.clamp(0.0, 1.0));
        arrived = mix(arrived, fur.agitation.z, (reaches - 1.0).clamp(0.0, 1.0));
        arrived = mix(arrived, fur.agitation.w, (reaches - 2.0).clamp(0.0, 1.0));
        let own = (arrived + (r3 - 0.5) * 0.16 * smoothstep(0.0, 0.12, arrived) * (1.0 - smoothstep(0.88, 1.0, arrived))).clamp(0.0, 1.0);
        let passing = fur.extra.x + (0.03 * swell + 0.11 * band + 0.24 * gust) * wind.min(2.5) * exposed;
        let ruffled = own.max((own + passing).min(0.56));

        let ruffle = 0.5 * smoothstep(0.0, 0.58, ruffled) + 0.5 * (ruffled / 0.58).clamp(0.0, 1.0);
        let rough = mix(fur.style.x, 1.0, 0.86 * ruffle + 0.14 * smoothstep(0.6, 1.0, own));
        let flat = 1.0 - smoothstep(0.0, 0.32, rough);
        let hackle = smoothstep(0.5, 0.84, own);
        let spike = smoothstep(0.78, 1.0, own);
        let quill = is_guard * spike;
        let stiff = is_guard * (0.75 * hackle).max(spike);

        let stray = step((r3 * 17.3 + r4 * 5.1).fract(), rough * (0.025 + 0.035 * shag));
        let own_turn = ((r1 * 91.7 + r2 * 37.3).fract() - 0.5) * mix(0.9, 0.22, flat);
        let patch_at = seed.root * 9.0;
        let swirl = (patch_at.x * 1.3 + (patch_at.y * 1.7 + patch_at.z).sin() * 1.5).sin() * (patch_at.z * 1.1 + (patch_at.x * 0.9 + patch_at.y * 1.3).sin() * 1.3).cos();
        let heave = 0.5 + 0.5 * (patch_at.z * 1.7 + patch_at.y * 1.1 + (patch_at.x * 1.9).sin() * 1.6).sin();
        let off_comb = own_turn + rough * (0.75 * swirl + ((clump_random * 7.7).fract() - 0.5) * 1.3 + (r4 - 0.5) * 0.45) + stray * (r4 - 0.5) * 2.4;
        let combed = to_world.transform_vector3(seed.comb).normalize();
        let comb = combed * off_comb.cos() + normal.cross(combed) * off_comb.sin();
        let cross_comb = normal.cross(comb);

        let rough_length = mix(1.0, 0.7 + 0.9 * r3 * r3, rough) * (1.0 + rough * (0.6 * shag + 0.45 * (clump_random - 0.5)));
        let soft_length = seed.soft * rough_length;
        let raised_length = soft_length * (1.0 + 0.2 * ruffle + 0.15 * rough * heave + 0.12 * hackle);
        let length = mix(raised_length * (1.0 + 0.5 * is_guard * hackle), seed.quill * fur.quill.x, is_guard * smoothstep(0.76, 1.0, own));
        let give_fur = mix(0.32, 1.0, ruffle) * (1.0 - 0.4 * spike);
        let give = give_fur * (1.0 - is_guard * 0.5 * hackle) * (1.0 - quill) * (1.0 - quill);

        let spine_a = to_world.transform_point3(fur.spine_a.truncate());
        let spine_b = to_world.transform_point3(fur.spine_b.truncate());
        let spine = spine_b - spine_a;
        let along_spine = (root - spine_a).dot(spine) / spine.dot(spine);
        let nearest = spine_a + spine * along_spine.clamp(0.0, 1.0);
        let radial = (root - nearest).normalize();
        let scatter = comb * (r1 - 0.5) * 0.35 + cross_comb * (r2 - 0.5) * 0.35;
        let outward = normal.lerp(radial, 0.6).normalize();
        let mut up = (outward + spine.normalize() * 0.22 + scatter).normalize();
        let mut sweep = Vec3::ZERO;
        if fur.style.w > 0.5 {
            let ahead = (-spine.normalize() * fur.style.y.signum() + Vec3::new(0.0, 0.3, 0.0)).normalize();
            let along_surface = ahead - outward * ahead.dot(outward);
            let flow = along_surface / along_surface.length().max(0.35);
            let amount = fur.style.y.abs() * mix(0.6, 1.0, smoothstep(-0.1, 0.7, normal.y)) * mix(0.55, 1.0, smoothstep(-0.25, 0.25, along_spine)) * (1.0 - 0.4 * tail);
            up = (outward + flow * (0.5 * amount) + scatter * 0.8).normalize();
            sweep = flow * (0.85 * amount) * (0.7 + 0.6 * r1);
        }

        let mut bend = (wind_to * (field + 2.6 * gust) + normal * 0.55 * (band + gust) + wind_across * 0.35 * band * (across_wind * 9.0 + time * 3.1).sin()) * wind * 0.8 * exposed;
        bend += fur.lag_a.truncate().lerp(fur.lag_b.truncate(), r1) + fur.turn_a.truncate().lerp(fur.turn_b.truncate(), r2).cross(root - fur.centre.truncate());
        let push = bend.length();
        bend *= give * 3.2 * (push / 3.2).tanh() / push.max(0.0001);
        let flutter = (0.07 + 0.22 * gust + 0.16 * band) * wind * give.max(0.55 * (1.0 - stiff));
        bend += comb * (time * (11.0 + 7.0 * r1) + r1 * 40.0).sin() * flutter + cross_comb * (time * (9.0 + 6.0 * r2) + r2 * 31.0).cos() * flutter;
        let shiver = (0.25 + 0.75 * is_guard) * hackle * (1.0 - spike) * (0.03 + 0.09 * wind.min(2.5));
        bend += (comb * (time * (37.0 + 19.0 * r1) + r2 * 50.0).sin() + cross_comb * (time * (31.0 + 23.0 * r2) + r1 * 44.0).cos()) * shiver;

        let lift = mix(0.3 + 0.35 * r2, 0.07 + 0.1 * r2, flat) + rough * (0.2 + 0.45 * heave + 0.55 * (clump_random * 3.3).fract() + 0.12 * r3 + 0.15 * shag) + stray * 0.45 + hackle * (0.4 + 0.4 * r1);
        let kink_size = rough * (0.04 + 0.07 * r4 + 0.04 * shag);
        let soft_width = seed.width * fur.spine_a.w * (1.0 + 0.3 * rough) * mix(1.0, 0.7 + 0.8 * r4, rough);
        Shape {
            root,
            normal,
            calm: (comb + normal * lift).normalize(),
            curl: (comb * 0.35 - normal * 0.55 + Vec3::new(0.0, -0.3, 0.0)) * (0.5 + r1) * mix(1.0, 0.4 + 1.2 * r3, rough) * (1.0 - 0.55 * hackle),
            up,
            bend,
            sweep,
            pull: to_world.transform_vector3(seed.clump) * (rough * 1.15 * (1.0 - stray) / soft_length.max(0.005)),
            kink_a: cross_comb * kink_size,
            kink_b: normal * kink_size * 0.6,
            kink: Vec2::new(2.5 + 4.0 * r1, r2 * 6.283),
            stand: is_guard * mix(0.62 * hackle, 1.0, spike),
            soft: 1.0 - stiff,
            length,
            floor: fur.quill.w,
            width: mix(soft_width * (1.0 + 0.3 * is_guard * hackle), fur.quill.y * (0.7 + 0.6 * r2), is_guard * smoothstep(0.8, 1.0, own)),
            quill,
        }
    }
}

/// Where along a hair the stand-in has a ring of three vertices; then one at the tip.
const PROXY_RINGS_GUARD: &[f32] = &[0.0, 0.2, 0.45, 0.72];
const PROXY_RINGS_FINE: &[f32] = &[0.0, 0.5];

/// The stand-in for the coat in the ray tracer's scene.
///
/// Solari traces rays against the vertex positions of a mesh as they are stored. The coat's
/// stored positions are its roots: every vertex of a hair is at the same point until the vertex
/// shader has moved it, and the mesh carries attributes Solari does not take. So the ray tracer
/// cannot see the coat at all, and the fur and the quills cast no ray-traced shadow. Here some of
/// the hairs are worked out again every frame on the processor, as three-sided tubes that do not
/// turn to the camera, and handed over as a mesh of their own that is not drawn; Bevy uploads it
/// and Solari builds its acceleration structure again, every frame.
#[expect(clippy::too_many_arguments)]
fn proxy_coat(
    mut commands: Commands,
    mut look: ResMut<Look>,
    coat: Res<CoatState>,
    body: Option<Res<Body>>,
    furs: Res<Assets<FurMaterial>>,
    mut meshes: ResMut<Assets<Mesh>>,
    model: Query<&Transform, With<Model>>,
    proxies: Query<(Entity, &RaytracingMesh3d), With<RtProxy>>,
    mut made: Local<Option<(usize, u32)>>,
    mut chosen: Local<Vec<(u32, f32)>>,
) {
    let (_, guards, one_in) = PROXIES[look.proxy];
    let material = body.as_ref().and_then(|body| body.material.clone());
    let (Some(material), Ok(model), Some(fur), true) = (material, model.single(), furs.get(&coat.material), look.ray_traced() && guards && coat.shown && !coat.seeds.is_empty())
    else {
        for (proxy, _) in &proxies {
            commands.entity(proxy).despawn();
        }
        *made = None;
        if look.proxy_triangles != 0 {
            (look.proxy_ms, look.proxy_triangles) = (0.0, 0);
        }
        return;
    };
    let began = Instant::now();
    let fresh = *made != Some((look.proxy, coat.grown)) || proxies.is_empty();
    if fresh {
        let mut fine = 0;
        *chosen = coat
            .seeds
            .iter()
            .enumerate()
            .filter_map(|(index, seed)| {
                if seed.quill > 0.0 {
                    return Some((index as u32, 1.0));
                }
                fine += 1;
                (one_in > 0 && fine % one_in == 0).then_some((index as u32, if one_in > 1 { PROXY_WIDER } else { 1.0 }))
            })
            .collect();
    }
    // The hairs' places now, on all the processor's threads.
    let to_world = model.compute_affine();
    let params = &fur.params;
    let seeds = &coat.seeds;
    let threads = std::thread::available_parallelism().map_or(4, usize::from);
    let share = chosen.len().div_ceil(threads).max(1);
    let mut positions: Vec<[f32; 3]> = Vec::new();
    std::thread::scope(|scope| {
        let workers: Vec<_> = chosen
            .chunks(share)
            .map(|hairs| {
                scope.spawn(move || {
                    let mut places = Vec::with_capacity(hairs.len() * 13);
                    for (index, wider) in hairs {
                        let seed = &seeds[*index as usize];
                        let shape = Shape::of(seed, params, &to_world);
                        let rings = if seed.quill > 0.0 { PROXY_RINGS_GUARD } else { PROXY_RINGS_FINE };
                        for t in rings {
                            let (here, along) = (shape.point(*t), shape.direction(*t));
                            let a = along.cross(shape.normal).try_normalize().unwrap_or(along.any_orthonormal_vector());
                            let b = along.cross(a);
                            let taper = mix((1.0 - t).max(0.0).sqrt(), 1.0 - t, shape.quill);
                            let radius = 0.5 * shape.width * taper * wider;
                            for corner in [0.0f32, 2.094, 4.189] {
                                places.push((here + (a * corner.cos() + b * corner.sin()) * radius).to_array());
                            }
                        }
                        places.push(shape.point(1.0).to_array());
                    }
                    places
                })
            })
            .collect();
        for worker in workers {
            positions.extend(worker.join().unwrap());
        }
    });
    if let (false, Ok((_, mesh))) = (fresh, proxies.single()) {
        if let Some(mut mesh) = meshes.get_mut(&mesh.0) {
            mesh.insert_attribute(Mesh::ATTRIBUTE_POSITION, positions);
        }
    } else {
        let (mut normals, mut uvs, mut indices) = (Vec::with_capacity(positions.len()), Vec::with_capacity(positions.len()), Vec::<u32>::new());
        for (index, _) in chosen.iter() {
            let seed = &seeds[*index as usize];
            let rings = if seed.quill > 0.0 { PROXY_RINGS_GUARD.len() } else { PROXY_RINGS_FINE.len() } as u32;
            let first = normals.len() as u32;
            // The stand-in is lit, where a bounced ray meets it, as the body under it is.
            for _ in 0..rings * 3 + 1 {
                normals.push(seed.normal.to_array());
                uvs.push(seed.uv.to_array());
            }
            let tip = first + rings * 3;
            for ring in 0..rings {
                for side in 0..3 {
                    let (a, b) = (first + ring * 3 + side, first + ring * 3 + (side + 1) % 3);
                    if ring + 1 == rings {
                        indices.extend([a, b, tip]);
                    } else {
                        indices.extend([a, b, a + 3, b, b + 3, a + 3]);
                    }
                }
            }
        }
        look.proxy_triangles = indices.len() / 3;
        let count = positions.len();
        let mesh = Mesh::new(PrimitiveTopology::TriangleList, RenderAssetUsages::default())
            .with_inserted_attribute(Mesh::ATTRIBUTE_POSITION, positions)
            .with_inserted_attribute(Mesh::ATTRIBUTE_NORMAL, normals)
            .with_inserted_attribute(Mesh::ATTRIBUTE_UV_0, uvs)
            .with_inserted_attribute(Mesh::ATTRIBUTE_TANGENT, vec![[1.0, 0.0, 0.0, 1.0]; count])
            .with_inserted_indices(Indices::U32(indices));
        for (proxy, _) in &proxies {
            commands.entity(proxy).despawn();
        }
        commands.spawn((RtProxy, RaytracingMesh3d(meshes.add(mesh)), MeshMaterial3d(material), Transform::default()));
        *made = Some((look.proxy, coat.grown));
        println!("stand-in for the coat in the ray tracer's scene: {}: {} hairs as {} triangles", PROXIES[look.proxy].0, chosen.len(), look.proxy_triangles);
    }
    let took = began.elapsed().as_secs_f32() * 1000.0;
    look.proxy_ms = if look.proxy_ms == 0.0 { took } else { look.proxy_ms * 0.95 + took * 0.05 };
}

/// Circles the cameras round the creature, far enough back to hold its quills, and follows it
/// loosely when it dashes so that the dash is seen.
fn cameras(time: Res<Time>, mut show: ResMut<Show>, mut framing: ResMut<Framing>, motion: Res<Motion>, mut views: Query<(&View, &mut Transform, &Projection)>) {
    if framing.radius == 0.0 {
        return;
    }
    if show.turntable {
        show.angle += time.delta_secs() * TURN_SPEED;
    }
    let follow = framing.follow.lerp(motion.place, 1.0 - (-time.delta_secs() * 3.5).exp());
    framing.follow = follow;
    for (view, mut transform, projection) in &mut views {
        let aspect = if let Projection::Perspective(lens) = projection { lens.aspect_ratio.min(1.0) } else { 1.0 };
        let distance = framing.radius / ((FOV / 2.0).tan() * aspect).atan().sin() * 1.02 * view.near;
        let centre = framing.centre + follow + view.aim;
        // The first version looked down on the creature. The other lightings have a horizon,
        // so the cameras that were high stand lower.
        let mut from = view.from;
        if !MOODS[show.mood].plain && from.y > 0.3 {
            from = Vec3::new(from.x, from.y * 0.5, from.z).normalize();
        }
        let direction = Quat::from_rotation_y(show.angle) * from;
        *transform = Transform::from_translation(centre + direction * distance).looking_at(centre, Vec3::Y);
    }
}

#[expect(clippy::too_many_arguments)]
fn report(
    show: Res<Show>,
    look: Res<Look>,
    coat: Res<CoatState>,
    body: Option<Res<Body>>,
    bodies: Res<Bodies>,
    frame_times: Res<FrameTimes>,
    time: Res<Time<Real>>,
    scripted: Option<Res<Script>>,
    bench: Option<Res<Bench>>,
    mut status: ResMut<Status>,
    mut last: Local<f32>,
    window: Option<Single<&mut Window>>,
) {
    let Some(body) = body else { return };
    let mood = &MOODS[show.mood];
    let tonemapper = TONEMAPPERS[look.tonemapper[usize::from(look.hdr)]].0;
    let picture = match (look.hdr, look.ray_traced()) {
        (true, _) => format!(
            "HDR pipeline (16-bit float, tone mapper {tonemapper}, bloom {}{})",
            if mood.bloom > 0.0 { "on" } else { "off in this lighting" },
            if look.auto_exposure { ", auto exposure" } else { "" }
        ),
        (false, false) => format!("plain LDR (8-bit, no bloom, tone mapper {tonemapper}){}", if look.untouched { ", as this lighting always was" } else { "" }),
        (false, true) => format!("LDR look (no bloom, tone mapper {tonemapper}; 16-bit float underneath for the ray tracer)"),
    };
    let lighting = match (look.ray_traced(), &look.rt_blocked, look.rt) {
        (true, _, _) => format!(
            "body and ground ray traced (Solari), fur rasterized, 1 sample a pixel, frames {}; coat in the ray tracer's scene: {}{}",
            if look.blend_frames { "blended (TAA)" } else { "not blended" },
            PROXIES[look.proxy].0,
            if look.proxy_triangles > 0 { format!(" ({} triangles, {:.1} ms a frame to work out)", look.proxy_triangles, look.proxy_ms) } else { String::new() }
        ),
        (false, Some(why), true) => format!("rasterized; ray tracing is not available here: {why}"),
        _ => "rasterized (shadow maps, 4x MSAA)".to_string(),
    };
    let said = if time.elapsed_secs() - look.said_at < 14.0 { format!(" | > {}", look.said) } else { String::new() };
    let line = format!(
        "{} hairs ({} guard hairs), {} triangles of fur + {} of body ({}) | frame {:.2} ms | agitation {:.2}: {}{} | calm coat: {} | quills lean {} | change travels {} | light: {} | wind {} | picture: {picture}, exposure {:+.1} stops; the screen gets {} | lighting: {lighting} | {}{}{}{}{said}",
        coat.hairs,
        coat.quills,
        coat.triangles,
        body.body_triangles,
        bodies.0[show.body.min(bodies.0.len() - 1)].0,
        frame_times.mean_ms(),
        show.agitation,
        stage_name(show.agitation),
        if (show.wave[0] - show.wave[3]).abs() > 0.02 { format!(" (travelling, {:.2} to {:.2})", show.wave[0], show.wave[3]) } else { String::new() },
        CALM[show.calm].0,
        match show.lean {
            Lean::Forward => format!("forward {:.1}", show.lean_amount),
            Lean::Outward => "outward".to_string(),
            Lean::Rearward => format!("rearward {:.1}", show.lean_amount),
        },
        if show.wave_to_head { "tail to head" } else { "neck to tail" },
        MOODS[show.mood].name,
        match (show.wind_on, show.wind_strength) {
            (false, _) => "off".to_string(),
            (true, strength) if strength >= 3.0 => format!("{strength:.2} (gale)"),
            (true, strength) => format!("{strength:.2}"),
        },
        look.stops,
        match (look.display_hdr, look.hdr && look.tonemapper[1] == 0) {
            (false, _) => "SDR",
            (true, true) => "scRGB, with light over white",
            (true, false) => "scRGB, all of it under white",
        },
        if show.loop_paused { "loop paused (Space)".to_string() } else { format!("loop {:.0} s of {LOOP_PERIOD:.0}", show.loop_clock) },
        if coat.shadows { "" } else { " | fur casts no shadow" },
        if show.turntable { "" } else { " | turntable off" },
        [" ", " | showing each hair's agitation", " | showing the guard hairs"][show.debug as usize].trim_end(),
    );
    status.0 = line;
    // In a window: the terminal gets the line once a second, unless a key script is printing.
    if window.is_some() && scripted.is_none() && bench.is_none() && time.elapsed_secs() - *last >= 1.0 {
        *last = time.elapsed_secs();
        print!("\r{:<150}", status.0);
        std::io::stdout().flush().ok();
    }
}

/// The stage of the scale an agitation is in.
fn stage_name(agitation: f32) -> &'static str {
    match agitation {
        a if a < 0.12 => "combed",
        a if a < 0.40 => "ruffled",
        a if a < 0.58 => "rough",
        a if a < 0.82 => "hackles",
        _ => "spikes",
    }
}

#[cfg(feature = "overlay")]
fn overlay(status: Res<Status>, mut text: Single<&mut Text, With<Overlay>>) {
    text.0 = format!("{}\n{}", status.0.replace(" | ", "\n"), KEYS.replace(" | ", "\n"));
}

/// With `--out`, the window saves a picture of itself every two seconds.
fn window_pictures(mut commands: Commands, time: Res<Time>, out: Res<Out>, look: Res<Look>, bench: Option<Res<Bench>>, mut next: Local<(f32, u32)>) {
    let Some(out) = &out.0 else { return };
    // A PNG file cannot hold what an scRGB surface holds.
    if time.elapsed_secs() < next.0 || bench.is_some() || look.display_hdr {
        return;
    }
    if next.1 > 0 {
        commands.spawn(Screenshot::primary_window()).observe(save_to_disk(out.join(format!("window_{:02}.png", next.1))));
    }
    *next = (next.0 + 2.0, next.1 + 1);
}

/// `--check`: does the things and takes the pictures of `Check`, then quits.
#[expect(clippy::too_many_arguments)]
fn check_run(
    mut commands: Commands,
    out: Res<Out>,
    mut check: ResMut<Check>,
    mut show: ResMut<Show>,
    mut motion: ResMut<Motion>,
    mut coat: ResMut<CoatState>,
    views: Query<(&View, &RenderTarget)>,
    pending: Query<(), With<Screenshot>>,
    mut exit: MessageWriter<AppExit>,
) {
    if !show.ready {
        return;
    }
    // A few frames for the hairs to reach the graphics card before the clock means anything.
    check.settle += 1;
    if check.settle < 10 {
        show.clock = 0.0;
        return;
    }
    while check.events.first().is_some_and(|(at, _)| show.clock >= *at) {
        let (_, action) = check.events.remove(0);
        if let Action::Coat(shown) = action {
            coat.shown = shown;
        }
        act(action, &mut show, &mut motion);
    }
    while check.shots.first().is_some_and(|(at, _, _)| show.clock >= *at) {
        let (at, name, by) = check.shots.remove(0);
        println!(
            "{name}: at {at:.2} s, agitation {:.2} ({}; along the body {:.2} {:.2} {:.2} {:.2}), startle {:.2}, wind {:.2}, creature at z {:.2} m",
            show.agitation,
            stage_name(show.agitation),
            show.wave[0],
            show.wave[1],
            show.wave[2],
            show.wave[3],
            show.startle,
            show.wind_now,
            motion.place.z
        );
        for (view, target) in views.iter().filter(|(view, _)| by.contains(&view.name)) {
            let RenderTarget::Image(image) = target else { continue };
            let path = out.0.as_ref().unwrap().join(format!("{name}_{}.png", view.name));
            commands.spawn(Screenshot::image(image.handle.clone())).observe(save_to_disk(path));
        }
    }
    // The pictures asked for this frame are not in `pending` until the next one.
    if !check.shots.is_empty() {
        check.settle = 10;
    }
    if check.shots.is_empty() && pending.is_empty() && check.settle > 20 {
        if !check.sheets_done {
            check.sheets_done = true;
            contact_sheets(out.0.as_ref().unwrap());
        }
        exit.write(AppExit::Success);
    }
}

/// The graphics memory this process holds, as `nvidia-smi` reports it, in MiB.
fn graphics_memory() -> Option<u32> {
    let listed = std::process::Command::new("nvidia-smi").args(["--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"]).output().ok()?;
    let own = std::process::id().to_string();
    String::from_utf8_lossy(&listed.stdout).lines().find_map(|line| {
        let (pid, memory) = line.split_once(',')?;
        (pid.trim() == own).then(|| memory.trim().parse().ok())?
    })
}

/// `--bench`: sets each stage, waits, times three seconds of frames, prints a row.
fn bench_run(
    mut bench: ResMut<Bench>,
    mut coat: ResMut<CoatState>,
    mut show: ResMut<Show>,
    mut look: ResMut<Look>,
    real: Res<Time<Real>>,
    window: Single<&Window>,
    mut exit: MessageWriter<AppExit>,
) {
    if !show.ready {
        return;
    }
    if !look.rt_asked {
        return;
    }
    let Some(Stage { label, preset, agitation, shadows, shown, mood, hdr, rt, proxy }) = bench.stages.get(bench.stage).cloned() else {
        exit.write(AppExit::Success);
        return;
    };
    if rt && look.rt_blocked.is_some() {
        println!("| | | | {label} | not run: ray tracing is not available here | | | | | |");
        bench.stage += 1;
        return;
    }
    if !bench.set {
        if bench.stage == 0 {
            println!("window {} by {} pixels, vsync off, MSAA 4x", window.physical_width(), window.physical_height());
            println!("| Hairs asked | Hairs | Fur triangles | State | Mean ms | Median ms | Slowest 1% ms | Frames a second | Graphics memory MiB | Build ms | Stand-in triangles | Stand-in ms |");
            println!("|---|---|---|---|---|---|---|---|---|---|---|---|");
        }
        if coat.preset != preset {
            (coat.preset, coat.asked, coat.rebuild) = (preset, PRESETS[preset], true);
        }
        show.mood = mood;
        (look.hdr, look.untouched, look.rt, look.proxy) = (hdr, false, rt, proxy);
        (coat.shadows, coat.shown) = (shadows, shown);
        (show.agitation, show.agitation_target) = (agitation, agitation);
        show.history.clear();
        (bench.set, bench.began) = (true, Some(Instant::now()));
        bench.samples.clear();
        return;
    }
    // The ray tracer's pipelines are made the first time they are used, and its light settles.
    let (wait, since) = (if rt { 4.0 } else { 1.5 }, bench.began.unwrap().elapsed().as_secs_f32());
    if since < wait {
        return;
    }
    if since < wait + 3.0 {
        bench.samples.push(real.delta_secs() * 1000.0);
        return;
    }
    let mut samples = std::mem::take(&mut bench.samples);
    samples.sort_by(f32::total_cmp);
    let mean = samples.iter().sum::<f32>() / samples.len() as f32;
    let memory = graphics_memory().map(|mib| mib.to_string()).unwrap_or("not listed".to_string());
    println!(
        "| {} | {} | {} | {label} | {mean:.2} | {:.2} | {:.2} | {:.0} | {memory} | {:.0} | {} | {:.2} |",
        if shown { coat.asked.to_string() } else { "0".to_string() },
        if shown { coat.hairs } else { 0 },
        if shown { coat.triangles } else { 0 },
        samples[samples.len() / 2],
        samples[samples.len() * 99 / 100],
        1000.0 / mean,
        coat.build_ms,
        look.proxy_triangles,
        look.proxy_ms,
    );
    bench.stage += 1;
    bench.set = false;
}
