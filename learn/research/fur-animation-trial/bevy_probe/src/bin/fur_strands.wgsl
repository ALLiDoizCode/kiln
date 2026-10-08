// The strand fur of fur_strands.rs. Every vertex of every hair comes here with its hair's root
// and its place along the hair, and is put where the hair is this frame: combed, blown, lagging
// behind the body, ruffled, raised as a hackle or stood up as a quill. The same code runs for the picture and, under
// PREPASS_PIPELINE, for the shadow map.

#import bevy_pbr::{
    mesh_functions,
    mesh_view_bindings::view,
    view_transformations::position_world_to_clip,
}

#ifdef PREPASS_PIPELINE
#import bevy_pbr::prepass_io::VertexOutput
#else
#import bevy_pbr::{
    mesh_bindings::mesh,
    pbr_types,
    pbr_functions,
}
#endif

struct FurParams {
    // xyz: the way the wind blows, in the world. w: its strength.
    wind: vec4<f32>,
    // x: seconds since the gust began. y: how fast its front crosses the world, m/s.
    // z: seconds it lasts at one place. w: the clock, seconds.
    gust: vec4<f32>,
    // How far the hair hangs behind the body's movement: two springs, a slow and a quick one.
    lag_a: vec4<f32>,
    lag_b: vec4<f32>,
    // The same for the body's turning, as a turn vector about `centre`.
    turn_a: vec4<f32>,
    turn_b: vec4<f32>,
    // xyz: the point the body turns about, in the world.
    centre: vec4<f32>,
    // The two ends of the line down the middle of the body, in the model's space.
    // spine_a.w: every hair's width is multiplied by it. spine_b.w: the least width, in pixels.
    spine_a: vec4<f32>,
    spine_b: vec4<f32>,
    // x: quill length is multiplied by it. y: quill width at the base, metres.
    // z: what to draw for looking at it: 1 each hair's agitation as a colour, 2 the guard hairs
    // tinted. w: the height of the ground in the world; no hair goes below it.
    quill: vec4<f32>,
    // x: how rough the coat is when calm, 0 combed. y: how far a quill leans along the body,
    // above 0 toward the head and below 0 toward the tail. z: 1 when the change travels from the
    // tail to the head, 0 from the neck to the tail. w: 1 when the lean follows the body's
    // surface, 0 for the plain fan of the first version.
    style: vec4<f32>,
    // xyz: the way to the light behind the creature, in the world. w: how strongly the fur's
    // edge and the quills catch it; 0 for none.
    rim_to: vec4<f32>,
    rim_colour: vec4<f32>,
    // Agitation, 0 combed to 1 spikes, at four places along the way the change travels: where
    // it arrives first, a third of the way, two thirds, and where it arrives last. All four are
    // the same when it is not changing.
    agitation: vec4<f32>,
    // x: agitation added for a moment to the whole coat when the body is jolted. It ruffles
    // the fur and never raises a quill.
    extra: vec4<f32>,
}

@group(#{MATERIAL_BIND_GROUP}) @binding(0) var<uniform> fur_now: FurParams;
// The same a frame ago, so that the camera's depth prepass can say how far each hair moved.
@group(#{MATERIAL_BIND_GROUP}) @binding(1) var<uniform> fur_before: FurParams;

struct Vertex {
    @builtin(instance_index) instance_index: u32,
    // The hair's root, the same for all its vertices.
    @location(0) root: vec3<f32>,
    // The body's normal at the root.
    @location(1) normal: vec3<f32>,
    // x: place along the hair, 0 root to 1 tip. y: side of the strip, -1 or 1, 0 at the tip.
    @location(2) along: vec2<f32>,
    // xyz: the way the hair is combed, along the body. w: its length when soft, metres.
    @location(3) comb: vec4<f32>,
    // x, y: two random numbers of the hair. z: when a change of agitation reaches it, 0 to 1.
    // w: its length as a quill, metres; 0 for a fine hair, which never becomes one.
    @location(4) rand: vec4<f32>,
    // rgb: the body's colour at the root. a: width at the root, metres.
    @location(5) color: vec4<f32>,
    // xyz: from the root to the middle of the hair's clump, in the model's space.
    // w: a random number shared by the whole clump.
    @location(6) clump: vec4<f32>,
    // x: how shaggy this part of the body is (ruff, lower flank, tail), 0 to 1.
    // y: how much of the tail it is. z, w: two more random numbers of the hair.
    @location(7) more: vec4<f32>,
}

struct Hair {
    root: vec3<f32>,
    normal: vec3<f32>,
    calm: vec3<f32>,
    curl: vec3<f32>,
    up: vec3<f32>,
    bend: vec3<f32>,
    // A quill's sweep along the body: it leans further the further along it is, so it curves.
    sweep: vec3<f32>,
    // Toward the tip of the hair's clump.
    pull: vec3<f32>,
    // The kink: two directions across the hair, and x: turns along the hair, y: where it starts.
    kink_a: vec3<f32>,
    kink_b: vec3<f32>,
    kink: vec2<f32>,
    stand: f32,
    // How much of the soft shape is left: 1 for fur, 0 for a straight quill.
    soft: f32,
    length: f32,
    floor: f32,
}

// The way the hair points at `t` along it. Bending grows with t, so the root does not move;
// the direction is one unit long at every t, so the tip is never further from the root than
// the hair is long, however hard the wind blows.
fn hair_direction(hair: Hair, t: f32) -> vec3<f32> {
    let wobble = hair.kink_a * sin(t * hair.kink.x + hair.kink.y) + hair.kink_b * cos(t * hair.kink.x * 0.8 + hair.kink.y * 1.7);
    let soft = normalize(hair.calm + ((hair.curl + hair.pull) * t + wobble) * hair.soft);
    var direction = normalize(mix(soft, hair.up, hair.stand) + (hair.sweep * hair.stand + hair.bend) * t);
    // Never into the body: a hair pushed below the surface is lifted back onto it.
    let out = dot(direction, hair.normal);
    direction = normalize(direction + hair.normal * max(0.0, 0.06 - out));
    // Never into the ground: a hair that would reach below it is turned to run along it.
    let least = (hair.floor - hair.root.y) / (hair.length * max(t, 0.02));
    if direction.y < least && least < 0.95 {
        let level = direction.xz / max(length(direction.xz), 0.0001) * sqrt(1.0 - least * least);
        direction = vec3(level.x, least, level.y);
    }
    return direction;
}

fn hair_point(hair: Hair, t: f32) -> vec3<f32> {
    return hair.root + hair_direction(hair, t) * (hair.length * t);
}

struct Placed {
    position: vec3<f32>,
    tangent: vec3<f32>,
    normal: vec3<f32>,
    // x: across the strip, -1 to 1. y: how much of a quill this hair is now, 0 to 1.
    // z: the hair's own agitation. w: place along the hair.
    shade: vec4<f32>,
    // x: how rough the coat is at this hair, 0 combed to 1. y: 1 for a guard hair.
    look: vec2<f32>,
}

// `fur` is this frame's numbers or the last frame's, and `world_from_local` the body's place then.
fn place(vertex: Vertex, fur: FurParams, world_from_local: mat4x4<f32>) -> Placed {
    let root = (world_from_local * vec4(vertex.root, 1.0)).xyz;
    let normal = normalize((world_from_local * vec4(vertex.normal, 0.0)).xyz);
    let t = vertex.along.x;
    let r1 = vertex.rand.x;
    let r2 = vertex.rand.y;
    let r3 = vertex.more.z;
    let r4 = vertex.more.w;
    let shag = vertex.more.x;
    let tail = vertex.more.y;
    let clump_random = vertex.clump.w;
    let is_guard = step(0.0001, vertex.rand.w);
    let time = fur.gust.w;

    // Wind, in layers: a slow swell; narrow crests that travel across the coat with the wind
    // as bands, in groups; a fine ripple; one large gust with a front (key G); and a flutter of
    // each hair. Neighbours sway together and the two flanks do not.
    let wind_to = fur.wind.xyz;
    let wind = fur.wind.w;
    let wind_across = normalize(cross(wind_to, vec3(0.0, 1.0, 0.0)));
    let along_wind = dot(root, wind_to);
    let across_wind = dot(root, wind_across);
    let swell = 0.5 + 0.5 * sin(along_wind * 2.4 - time * 1.9 + sin(across_wind * 2.1 + time * 0.7) * 1.4);
    let crest = 0.5 + 0.5 * sin(along_wind * 6.5 - time * 6.8 + sin(across_wind * 3.3 - time * 0.5) * 1.1 + root.y * 1.8);
    let band = crest * crest * crest * crest * (0.6 + 0.4 * sin(time * 0.83 + 1.0));
    let ripple = sin(along_wind * 14.0 - time * 8.5 + across_wind * 9.0 + root.y * 6.0);
    let field = 0.25 + 0.4 * swell + 1.0 * band + 0.1 * ripple;
    let since_front = (fur.gust.x - along_wind / fur.gust.y) / fur.gust.z;
    let gust = smoothstep(0.0, 0.2, since_front) * (1.0 - smoothstep(0.45, 1.0, since_front));
    // The side the wind comes from feels more of it than the side in its lee; the long hair
    // of the tail streams.
    let exposed = (0.55 + 0.45 * clamp(0.5 - 0.5 * dot(normal, wind_to), 0.0, 1.0)) * (1.0 + 0.8 * tail);

    // Agitation is the one scale the whole coat travels along: combed, ruffled, rough, hackles
    // up, spikes. A change of it travels along the body: `rand.z` is 0 at the neck and nearly 1
    // at the tip of the tail, and the change runs that way or, turned round, from the tail
    // forward to the head. The program hands over the value at four places along the way.
    let reaches = clamp(mix(vertex.rand.z, 0.95 - vertex.rand.z, fur.style.z) + r2 * 0.05, 0.0, 1.0) * 3.0;
    var arrived = mix(fur.agitation.x, fur.agitation.y, clamp(reaches, 0.0, 1.0));
    arrived = mix(arrived, fur.agitation.z, clamp(reaches - 1.0, 0.0, 1.0));
    arrived = mix(arrived, fur.agitation.w, clamp(reaches - 2.0, 0.0, 1.0));
    // Each hair is a little ahead of or behind its neighbours, so they do not change in step;
    // not at the two ends of the scale, where every hair is combed or every guard hair a quill.
    let own = clamp(arrived + (r3 - 0.5) * 0.16 * smoothstep(0.0, 0.12, arrived) * (1.0 - smoothstep(0.88, 1.0, arrived)), 0.0, 1.0);
    // Wind and a jolt ruffle the coat where they hit it and for as long as they last. They add
    // to the fur's roughness only, and never by enough to raise hackles.
    let passing = fur.extra.x + (0.03 * swell + 0.11 * band + 0.24 * gust) * min(wind, 2.5) * exposed;
    let ruffled = max(own, min(own + passing, 0.56));

    // The four overlapping parts of the scale. `rough` is how tufted, uneven and lifted the fur
    // is; `flat` how closely combed; `hackle` how far the guard hairs have stood up out of the
    // coat, still as fur; `spike` how far they have hardened into quills.
    let ruffle = 0.5 * smoothstep(0.0, 0.58, ruffled) + 0.5 * clamp(ruffled / 0.58, 0.0, 1.0);
    let rough = mix(fur.style.x, 1.0, 0.86 * ruffle + 0.14 * smoothstep(0.6, 1.0, own));
    let flat = 1.0 - smoothstep(0.0, 0.32, rough);
    let hackle = smoothstep(0.5, 0.84, own);
    let spike = smoothstep(0.78, 1.0, own);
    let quill = is_guard * spike;
    // How straight and stiff a guard hair is: most of the way as a hackle, wholly as a quill.
    let stiff = is_guard * max(0.75 * hackle, spike);

    // Combed, every hair lies along the comb. Roughness turns hairs off it: each hair a little,
    // every clump its own way, and a few strays any way at all.
    let stray = step(fract(r3 * 17.3 + r4 * 5.1), rough * (0.025 + 0.035 * shag));
    let own_turn = (fract(r1 * 91.7 + r2 * 37.3) - 0.5) * mix(0.9, 0.22, flat);
    // A ruffled coat is disturbed in patches a hand wide: here swirled one way and lifted,
    // there the other way and lying.
    let patch_at = vertex.root * 9.0;
    let swirl = sin(patch_at.x * 1.3 + sin(patch_at.y * 1.7 + patch_at.z) * 1.5) * cos(patch_at.z * 1.1 + sin(patch_at.x * 0.9 + patch_at.y * 1.3) * 1.3);
    let heave = 0.5 + 0.5 * sin(patch_at.z * 1.7 + patch_at.y * 1.1 + sin(patch_at.x * 1.9) * 1.6);
    let off_comb = own_turn + rough * (0.75 * swirl + (fract(clump_random * 7.7) - 0.5) * 1.3 + (r4 - 0.5) * 0.45) + stray * (r4 - 0.5) * 2.4;
    let combed = normalize((world_from_local * vec4(vertex.comb.xyz, 0.0)).xyz);
    let comb = combed * cos(off_comb) + cross(normal, combed) * sin(off_comb);
    let cross_comb = cross(normal, comb);

    // Rough fur is of every length: most hairs shorter, a few much longer, each clump its own,
    // and longer where the coat is shaggy. Raised, all of it is a little longer, so the coat
    // is thicker in outline.
    let rough_length = mix(1.0, 0.7 + 0.9 * r3 * r3, rough) * (1.0 + rough * (0.6 * shag + 0.45 * (clump_random - 0.5)));
    let soft_length = vertex.comb.w * rough_length;
    let raised_length = soft_length * (1.0 + 0.2 * ruffle + 0.15 * rough * heave + 0.12 * hackle);
    // A hackle is half as long again as the fur round it; a quill grows to its own length.
    let hair_length = mix(raised_length * (1.0 + 0.5 * is_guard * hackle), vertex.rand.w * fur.quill.x, is_guard * smoothstep(0.76, 1.0, own));
    // How much the hair gives way to wind and movement: combed fur little, ruffled fur most,
    // hackles half of that, quills not at all.
    let give_fur = mix(0.32, 1.0, ruffle) * (1.0 - 0.4 * spike);
    let give = give_fur * (1.0 - is_guard * 0.5 * hackle) * (1.0 - quill) * (1.0 - quill);

    // Stood up, a quill points out from the line down the middle of the body, so the quills fan
    // out evenly whatever the small bumps of the surface say.
    let spine_a = (world_from_local * vec4(fur.spine_a.xyz, 1.0)).xyz;
    let spine_b = (world_from_local * vec4(fur.spine_b.xyz, 1.0)).xyz;
    let spine = spine_b - spine_a;
    let along_spine = dot(root - spine_a, spine) / dot(spine, spine);
    let nearest = spine_a + spine * clamp(along_spine, 0.0, 1.0);
    let radial = normalize(root - nearest);
    let scatter = comb * (r1 - 0.5) * 0.35 + cross_comb * (r2 - 0.5) * 0.35;
    let outward = normalize(mix(normal, radial, 0.6));
    // The first version: a plain fan, a little toward the tail.
    var up = normalize(outward + normalize(spine) * 0.22 + scatter);
    var sweep = vec3(0.0);
    if fur.style.w > 0.5 {
        // The lean flows along the body's surface toward the head (or the tail), and a little
        // upward so the quills of the rump rise and do not point straight back. It is strongest
        // on the back and the shoulders, less on the flanks, less again just behind the head so
        // the face is not hidden, and each quill bends further over toward its tip.
        let ahead = normalize(-normalize(spine) * sign(fur.style.y) + vec3(0.0, 0.3, 0.0));
        let along_surface = ahead - outward * dot(ahead, outward);
        let flow = along_surface / max(length(along_surface), 0.35);
        let amount = abs(fur.style.y) * mix(0.6, 1.0, smoothstep(-0.1, 0.7, normal.y)) * mix(0.55, 1.0, smoothstep(-0.25, 0.25, along_spine)) * (1.0 - 0.4 * tail);
        up = normalize(outward + flow * (0.5 * amount) + scatter * 0.8);
        sweep = flow * (0.85 * amount) * (0.7 + 0.6 * r1);
    }

    // A crest lifts the coat off the body as it passes and swirls it a little sideways.
    var bend = (wind_to * (field + 2.6 * gust) + normal * 0.55 * (band + gust) + wind_across * 0.35 * band * sin(across_wind * 9.0 + time * 3.1)) * wind * 0.8 * exposed;
    // Movement: the springs are stepped on the CPU; each hair takes its own mix of the two,
    // so the coat does not swing as one piece.
    bend += mix(fur.lag_a.xyz, fur.lag_b.xyz, r1) + cross(mix(fur.turn_a.xyz, fur.turn_b.xyz, r2), root - fur.centre.xyz);
    // However hard it is pushed, a hair only turns: a push of any size leaves it lying along
    // the push, as long as it was.
    let push = length(bend);
    bend *= give * 3.2 * tanh(push / 3.2) / max(push, 0.0001);
    // The flutter of each hair is at its tip, and combed fur keeps it: the coat stays sleek
    // and its tips tremble.
    let flutter = (0.07 + 0.22 * gust + 0.16 * band) * wind * max(give, 0.55 * (1.0 - stiff));
    bend += comb * sin(time * (11.0 + 7.0 * r1) + r1 * 40.0) * flutter + cross_comb * cos(time * (9.0 + 6.0 * r2) + r2 * 31.0) * flutter;
    // A raised hackle shivers in the wind, and a little without any; a quill is still.
    let shiver = (0.25 + 0.75 * is_guard) * hackle * (1.0 - spike) * (0.03 + 0.09 * min(wind, 2.5));
    bend += (comb * sin(time * (37.0 + 19.0 * r1) + r2 * 50.0) + cross_comb * cos(time * (31.0 + 23.0 * r2) + r1 * 44.0)) * shiver;

    // Combed, the hair leaves the body at a very low angle along the comb and lies on the coat.
    // Rougher, it lifts, each clump stands at its own angle, the hairs of a clump lean toward
    // its tip so the coat breaks into tufts, a stray stands well off the coat, and every hair
    // has a kink. With the hackles up the fine fur stands on end.
    let lift = mix(0.3 + 0.35 * r2, 0.07 + 0.1 * r2, flat) + rough * (0.2 + 0.45 * heave + 0.55 * fract(clump_random * 3.3) + 0.12 * r3 + 0.15 * shag) + stray * 0.45 + hackle * (0.4 + 0.4 * r1);
    let pull = (world_from_local * vec4(vertex.clump.xyz, 0.0)).xyz;
    let kink_size = rough * (0.04 + 0.07 * r4 + 0.04 * shag);
    var hair: Hair;
    hair.root = root;
    hair.normal = normal;
    hair.calm = normalize(comb + normal * lift);
    hair.curl = (comb * 0.35 - normal * 0.55 + vec3(0.0, -0.3, 0.0)) * (0.5 + r1) * mix(1.0, 0.4 + 1.2 * r3, rough) * (1.0 - 0.55 * hackle);
    hair.up = up;
    hair.bend = bend;
    hair.sweep = sweep;
    hair.pull = pull * (rough * 1.15 * (1.0 - stray) / max(soft_length, 0.005));
    hair.kink_a = cross_comb * kink_size;
    hair.kink_b = normal * kink_size * 0.6;
    hair.kink = vec2(2.5 + 4.0 * r1, r2 * 6.283);
    hair.stand = is_guard * mix(0.62 * hackle, 1.0, spike);
    hair.soft = 1.0 - stiff;
    hair.length = hair_length;
    hair.floor = fur.quill.w;

    let here = hair_point(hair, t);
    let tangent = normalize(hair_point(hair, min(t + 0.08, 1.0)) - hair_point(hair, max(t - 0.08, 0.0)));

    // The strip is turned to face whoever looks: the camera, or the light for the shadow map.
    let orthographic = view.clip_from_view[3][3] == 1.0;
    var to_eye = normalize(view.world_position - here);
    var pixel = 2.0 * length(view.world_position - root) / (view.clip_from_view[1][1] * view.viewport.w);
    if orthographic {
        to_eye = normalize(view.world_from_view[2].xyz);
        pixel = 2.0 / (view.clip_from_view[1][1] * view.viewport.w);
    }
    let across = normalize(cross(tangent, to_eye));

    // Width: fur keeps most of its width and ends in a point; a hackle is a little coarser;
    // a quill is a long cone.
    let soft_width = vertex.color.a * fur.spine_a.w * (1.0 + 0.3 * rough) * mix(1.0, 0.7 + 0.8 * r4, rough);
    let root_width = mix(soft_width * (1.0 + 0.3 * is_guard * hackle), fur.quill.y * (0.7 + 0.6 * r2), is_guard * smoothstep(0.8, 1.0, own));
    let taper = mix(pow(max(1.0 - t, 0.0), 0.5), 1.0 - t, quill);
    var width = root_width * taper;

    // A hair thinner than a pixel flickers as it moves. Far away the hair is drawn at least
    // `spine_b.w` pixels wide, and so that the coat does not get heavier, only a share of the
    // hairs are drawn there: the same ones every frame.
    // With ray tracing on the camera draws its depth first, with the PREPASS_PIPELINE code (seen
    // here by MOTION_VECTOR_PREPASS, which a shadow map never has). That depth must be of the same
    // hairs, as wide, as the picture's, or the picture has holes where a hair was dropped.
#ifdef PREPASS_PIPELINE
#ifdef MOTION_VECTOR_PREPASS
    let as_picture = true;
#else
    let as_picture = false;
#endif
#else
    let as_picture = true;
#endif
    if as_picture {
        let least = pixel * fur.spine_b.w;
        let kept = clamp(root_width / least, 0.25, 1.0);
        if fract(r1 * 7.31 + r2 * 3.17) > kept {
            width = 0.0;
        } else {
            width = max(width, least * step(t, 0.999));
        }
    } else {
        width = max(width, pixel * step(t, 0.999));
    }

    var placed: Placed;
    placed.position = here + across * (vertex.along.y * width * 0.5);
    placed.tangent = tangent;
    placed.normal = normal;
    placed.shade = vec4(vertex.along.y, quill, own, t);
    placed.look = vec2(rough, is_guard);
    return placed;
}

#ifdef PREPASS_PIPELINE

@vertex
fn vertex(vertex: Vertex) -> VertexOutput {
    let placed = place(vertex, fur_now, mesh_functions::get_world_from_local(vertex.instance_index));
    var out: VertexOutput;
    out.world_position = vec4(placed.position, 1.0);
    out.position = position_world_to_clip(placed.position);
#ifdef UNCLIPPED_DEPTH_ORTHO_EMULATION
    out.unclipped_depth = out.position.z;
    out.position.z = min(out.position.z, 1.0);
#endif
#ifdef NORMAL_PREPASS_OR_DEFERRED_PREPASS
    out.world_normal = placed.normal;
#endif
#ifdef MOTION_VECTOR_PREPASS
    // Where this vertex was a frame ago: the same hair placed with the last frame's numbers. With
    // it, blending frames (TAA) follows a hair as it moves and does not smear it.
    let before = place(vertex, fur_before, mesh_functions::get_previous_world_from_local(vertex.instance_index));
    out.previous_world_position = vec4(before.position, 1.0);
#endif
#ifdef VERTEX_OUTPUT_INSTANCE_INDEX
    out.instance_index = vertex.instance_index;
#endif
    return out;
}

#else

struct FurOutput {
    @builtin(position) position: vec4<f32>,
    @location(0) world_position: vec4<f32>,
    @location(1) body_normal: vec3<f32>,
    @location(2) tangent: vec3<f32>,
    @location(3) color: vec3<f32>,
    @location(4) shade: vec4<f32>,
    @location(5) @interpolate(flat) instance_index: u32,
    @location(6) look: vec2<f32>,
}

@vertex
fn vertex(vertex: Vertex) -> FurOutput {
    let placed = place(vertex, fur_now, mesh_functions::get_world_from_local(vertex.instance_index));
    var out: FurOutput;
    out.world_position = vec4(placed.position, 1.0);
    out.position = position_world_to_clip(placed.position);
    out.body_normal = placed.normal;
    out.tangent = placed.tangent;
    // Each hair a little lighter or darker than its neighbours, so strands can be told apart:
    // barely when the coat is combed, plainly when it is rough.
    let apart = mix(0.14, 0.4, placed.look.x);
    out.color = vertex.color.rgb * (1.0 - 0.5 * apart + apart * vertex.rand.x);
    out.shade = placed.shade;
    out.look = placed.look;
    out.instance_index = vertex.instance_index;
    return out;
}

const QUILL: vec3<f32> = vec3<f32>(0.86, 0.80, 0.66);
const QUILL_TIP: vec3<f32> = vec3<f32>(0.20, 0.13, 0.10);

@fragment
fn fragment(in: FurOutput) -> @location(0) vec4<f32> {
    let side = in.shade.x;
    let quill = in.shade.y;
    // Between a triangle's samples a value can be read a little outside the triangle, and a
    // power of a number below nothing is no number at all: a black dot in the picture.
    let t = clamp(in.shade.w, 0.0, 1.0);
    let rough = clamp(in.look.x, 0.0, 1.0);

    var pbr_input = pbr_types::pbr_input_new();
    pbr_input.flags = mesh[in.instance_index].flags;
    pbr_input.is_orthographic = view.clip_from_view[3][3] == 1.0;
    pbr_input.V = pbr_functions::calculate_view(in.world_position, pbr_input.is_orthographic);
    pbr_input.frag_coord = in.position;
    pbr_input.world_position = in.world_position;

    // The flat strip is shaded as if it were round: its normal turns from one edge to the other.
    let tangent = normalize(in.tangent);
    // A hair seen exactly end on has no across; any will do.
    let sideways = cross(tangent, pbr_input.V);
    let across = normalize(sideways + vec3(1e-5, 0.0, 0.0) * step(dot(sideways, sideways), 1e-10));
    let facing = cross(across, tangent);
    let round = normalize(facing * sqrt(max(1.0 - side * side, 0.0)) + across * side);
    // Soft hair is lit mostly as the body under it is, or every hair would catch the light its
    // own way and the coat would be noise. A quill is lit as the hard cone it is.
    let body_normal = normalize(in.body_normal);
    // Combed fur is one smooth surface; rough fur is broken, each tuft catching its own light.
    let normal = normalize(mix(body_normal, round, mix(mix(0.18, 0.48, rough), 0.92, quill)));
    pbr_input.world_normal = normal;
    pbr_input.N = normal;

    // Darker at the root, where the coat shades itself, and lighter at the tip.
    let coat = in.color * mix(0.5, 1.12, pow(t, 0.7));
    // A quill keeps the colour of the coat it grew from for most of its length, pales toward
    // the tip, and has a dark point.
    var hard = mix(in.color, mix(QUILL, in.color, 0.3), smoothstep(0.45, 0.85, t));
    hard = mix(hard, QUILL_TIP, smoothstep(0.86, 0.98, t));
    var color = mix(coat, hard, quill);
    if fur_now.quill.z > 1.5 {
        // The guard hairs, which become the quills, in a colour no coat has.
        color = mix(color, vec3(0.0, 0.9, 1.0), step(0.5, in.look.y));
    } else if fur_now.quill.z > 0.5 {
        // Each hair's agitation: blue combed, green ruffled, yellow hackles, red spikes.
        let a = in.shade.z;
        color = mix(vec3(0.1, 0.2, 0.9), vec3(0.1, 0.8, 0.2), smoothstep(0.0, 0.4, a));
        color = mix(color, vec3(1.0, 0.85, 0.1), smoothstep(0.4, 0.7, a));
        color = mix(color, vec3(1.0, 0.1, 0.05), smoothstep(0.7, 1.0, a));
    }
    pbr_input.material.base_color = vec4(color, 1.0);
    // Combed fur has a sheen; rough fur is matt; a quill is hard and shines.
    pbr_input.material.perceptual_roughness = mix(mix(0.52, 0.95, rough), 0.38, quill);
    pbr_input.material.metallic = 0.0;
    pbr_input.material.reflectance = vec3(mix(mix(0.42, 0.2, rough), 0.5, quill));

    var out = pbr_functions::apply_pbr_lighting(pbr_input);

    // Light from behind. Fur is read by its lit edge: light that comes from beyond the creature
    // passes through the outer hairs and glances off them. Two cheap terms, neither shadowed:
    // a glow where the coat is seen edge on, stronger toward the tips, and Kajiya and Kay's
    // highlight of a thin strand, which runs along a hair and makes a quill glint.
    if fur_now.rim_to.w > 0.0 {
        let to_light = fur_now.rim_to.xyz;
        let eye = pbr_input.V;
        let behind = pow(clamp(0.5 - 0.5 * dot(eye, to_light), 0.0, 1.0), 1.5);
        let lit_side = clamp(dot(body_normal, to_light) + 0.65, 0.0, 1.0);
        // Two unit vectors can have a dot product a hair over 1; see `t` above.
        let edge = pow(clamp(1.0 - abs(dot(body_normal, eye)), 0.0, 1.0), 2.5);
        let along_light = dot(tangent, to_light);
        let along_view = dot(tangent, eye);
        let strand = max(sqrt(max(1.0 - along_light * along_light, 0.0)) * sqrt(max(1.0 - along_view * along_view, 0.0)) - along_light * along_view, 0.0);
        let glance = pow(strand, mix(14.0, 90.0, quill));
        let through = edge * (0.25 + 0.75 * t) * (0.35 + 0.65 * behind);
        let glint = glance * (0.15 + 0.85 * behind) * mix(0.25 * t * (1.6 - rough), 0.1 + 0.3 * t, quill);
        let rim = fur_now.rim_colour.rgb * fur_now.rim_to.w * lit_side * (color * through * 1.6 + mix(color, vec3(1.0), 0.5) * glint);
        out = vec4(out.rgb + rim, out.a);
    }
    out = pbr_functions::main_pass_post_lighting_processing(pbr_input, out);
    return vec4(out.rgb, 1.0);
}

#endif
