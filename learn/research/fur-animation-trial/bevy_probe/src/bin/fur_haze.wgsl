// The haze over the ground while fur_strands.rs ray traces. Solari lights the ground and the
// body in place of Bevy's own lighting pass, and Bevy's distance fog is part of that pass, so the
// ray-traced ground has none. This is the same ground drawn once more over it, as nothing but
// the fog Bevy would have put there: the fog's own light added, and the ground under it dimmed
// by as much as the fog hides.

#import bevy_pbr::{
    forward_io::VertexOutput,
    mesh_view_bindings as view_bindings,
    pbr_functions,
}

@fragment
fn fragment(in: VertexOutput) -> @location(0) vec4<f32> {
#ifdef DISTANCE_FOG
    let eye = view_bindings::view.world_position.xyz;
    let over_black = pbr_functions::apply_fog(view_bindings::fog, vec4(0.0, 0.0, 0.0, 1.0), in.world_position.xyz, eye, in.position.xy);
    let over_white = pbr_functions::apply_fog(view_bindings::fog, vec4(1.0, 1.0, 1.0, 1.0), in.world_position.xyz, eye, in.position.xy);
    let through = clamp(over_white.g - over_black.g, 0.0, 1.0);
    // Premultiplied: this is added, and what is behind is multiplied by one minus alpha.
    return vec4(over_black.rgb, 1.0 - through);
#else
    return vec4(0.0);
#endif
}
