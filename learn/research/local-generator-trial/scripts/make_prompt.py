"""Write a ComfyUI prompt (API format) for the trial. Standard library only.

    python3 make_prompt.py <out.json> --image crate_three_quarter.png --name crate_a
        [--generator trellis2|pixal3d] [--resolution 1536] [--structure-seed 56]
        [--chain raw|video] [--target-tris 20000] [--voxel 0.0015] [--cage 0.0019]
        [--texture 4096] [--blender PATH] [--close none|remesh] [--bake-samples N]

The generation half is the video's workflow 2 (PixelArtistry_02_Image_to_GameReady_Asset.json, itself
ComfyUI's own template 3d_pixal3d_trellis2_image_to_model) node for node, with one change: the
structure seed is fixed, where the video's file has it on "randomize".

--chain raw    stops after the generator: saves the decoded mesh with vertex colours, nothing else.
--chain video  goes on through the video's steps. Quad Reconstruct and WTiVo are left out (they do
               not run on Linux here); --close remesh puts ComfyUI's own RemeshMesh in WTiVo's place,
               --close none hands the decoded mesh straight to LODTailor, whose Blender voxel remesh
               closes it.
"""
import argparse, json
p = argparse.ArgumentParser()
p.add_argument("out"); p.add_argument("--image", required=True); p.add_argument("--name", required=True)
p.add_argument("--generator", default="trellis2"); p.add_argument("--resolution", type=int, default=1536)
p.add_argument("--structure-seed", type=int, default=56)
p.add_argument("--chain", default="raw"); p.add_argument("--target-tris", type=int, default=20000)
p.add_argument("--voxel", type=float, default=0.0015); p.add_argument("--cage", type=float, default=0.0019)
p.add_argument("--texture", type=int, default=4096); p.add_argument("--blender", default="blender")
p.add_argument("--close", default="none"); p.add_argument("--bake-samples", type=int, default=1)
p.add_argument("--dense-tris", type=int, default=6000000)
p.add_argument("--close-resolution", type=int, default=768)
p.add_argument("--skip-dense", action="store_true")
p.add_argument("--dense-voxel", action="store_true", help="the video has this on")
p.add_argument("--reference-closed", action="store_true", help="the video bakes against the closed mesh")
p.add_argument("--precluster", type=int, default=20000000)
a = p.parse_args()
g = {}
def node(i, cls, title=None, **inputs):
    g[str(i)] = {"class_type": cls, "inputs": inputs, "_meta": {"title": title or cls}}
    return str(i)
trellis = a.generator == "trellis2"
node(122, "LoadImage", image=a.image)
node(193, "LoadBackgroundRemovalModel", bg_removal_name="birefnet.safetensors")
node(192, "RemoveBackground", bg_removal_model=["193", 0], image=["122", 0])
node(312, "ImageCropToMask", images=["122", 0], masks=["192", 0], width=1024, height=1024,
     pad_factor=1.1, grow_mask=0, background="#000000")
node(15, "CLIPVisionLoader", clip_name="dino_v3_L_naf_fp32.safetensors")
if trellis:
    node(299, "Trellis2Conditioning", clip_vision_model=["15", 0], image=["312", 0]); cond = "299"
    node(40, "UNETLoader", unet_name="trellis_2_int8_convrot.safetensors", weight_dtype="default"); model = "40"
else:
    node(55, "LoadMoGeModel", model_name="moge_2_vitl_normal_fp16.safetensors")
    node(56, "MoGeInference", moge_model=["55", 0], image=["312", 0], resolution_level=9, fov_x_degrees=0,
         batch_size=4, force_projection=True, apply_mask=True, refine_steps=3)
    node(242, "MoGeGeometryToFOV", moge_geometry=["56", 0], axis="horizontal", unit="degrees")
    node(298, "Pixal3DConditioning", clip_vision_model=["15", 0], image=["312", 0], camera_angle_x=["242", 0]); cond = "298"
    node(319, "UNETLoader", unet_name="pixal3d_int8_convrot.safetensors", weight_dtype="default"); model = "319"
node(117, "VAELoader", "shape VAE", vae_name="trellis_2_shape_vae_bf16.safetensors")
node(118, "VAELoader", "texture VAE", vae_name="trellis_2_texture_vae_bf16.safetensors")
node(87, "EmptyTrellis2LatentStructure", batch_size=1)
node(199, "CFGOverride", model=[model, 0], cfg=1, start_percent=0.667, end_percent=1)
node(125, "RescaleCFG", model=["199", 0], multiplier=0.7)
node(108, "ModelSamplingSD3", model=["125", 0], shift=5)
node(3, "KSampler", "1 structure sampler", model=["108", 0], seed=a.structure_seed, steps=12, cfg=7.5,
     sampler_name="euler", scheduler="normal", positive=[cond, 0], negative=[cond, 1], latent_image=["87", 0], denoise=1)
node(119, "VaeDecodeStructureTrellis2", "1 structure decode", samples=["3", 0], vae=["117", 0], resolution="32")
node(91, "Trellis2ShapeStage", positive=[cond, 0], negative=[cond, 1], voxel=["119", 0])
node(279, "CFGOverride", model=[model, 0], cfg=1, start_percent=0.769, end_percent=1)
node(126, "RescaleCFG", model=["279", 0], multiplier=0.5)
node(18, "KSampler", "2 shape sampler (512)", model=["126", 0], seed=42, steps=20, cfg=7.5, sampler_name="euler",
     scheduler="normal", positive=["91", 0], negative=["91", 1], latent_image=["91", 2], denoise=1)
node(94, "Trellis2UpsampleStage", "3 upsample stage", positive=["91", 0], negative=["91", 1], shape_latent=["18", 0],
     vae=["117", 0], target_resolution=a.resolution)
node(23, "KSampler", "3 shape sampler (upsampled)", model=["126", 0], seed=42, steps=12, cfg=7.5, sampler_name="euler",
     scheduler="simple", positive=["94", 0], negative=["94", 1], latent_image=["94", 2], denoise=1)
node(92, "VaeDecodeShapeTrellis", "3 shape decode", samples=["23", 0], vae=["117", 0])
node(98, "Trellis2TextureStage", positive=["94", 0], negative=["94", 1], shape_latent=["23", 0])
node(12, "KSampler", "4 texture sampler", model=[model, 0], seed=43, steps=12, cfg=1, sampler_name="euler",
     scheduler="normal", positive=["98", 0], negative=["98", 1], latent_image=["98", 2], denoise=1)
node(93, "VaeDecodeTextureTrellis", "4 texture decode", samples=["12", 0], vae=["118", 0], shape_subdivides=["92", 1])
node(400, "PaintMesh", "raw: vertex colours", mesh=["92", 0], voxel_colors=["93", 0])
node(401, "SaveGLB", "raw: save", mesh=["400", 0], filename_prefix=f"3d/{a.name}_raw")
if a.chain in ("video", "close"):
    closed = "92"
    if a.close == "remesh":   # ComfyUI's own closing node: unsigned distance field, inner shell and enclosed parts dropped
        node(326, "MemoryCleaner", "free VRAM before closing (as the video does before WTiVo)", input_1=["92", 0],
             enabled=True, always_run=True, clean_vram=True, clean_ram=True)
        node(241, "RemeshMesh", "SUBSTITUTE for WTiVo: RemeshMesh", **{"mesh": ["326", 0], "resolution": a.close_resolution,
             "sign_mode": "udf", "sign_mode.qef": False, "sign_mode.drop_inverted_components": True,
             "sign_mode.drop_enclosed_components": True, "band": 1.0, "project_back": 0.0, "fix_poles": False,
             "smooth_iters": 0, "drop_small_components": 0.01, "precluster_max_verts": a.precluster})
        closed = "241"
        node(402, "SaveGLB", "closed: save", mesh=["241", 0], filename_prefix=f"3d/{a.name}_closed")
if a.chain == "video" and a.skip_dense:
    g["328"] = None; dense = closed       # the closed mesh is already near the video's 6,000,000 target
if a.chain == "video" and not a.skip_dense:
    dense = "328"
    node(328, "LODTailorTheMeshTrimmer", "LODTailor dense (Blender)", mesh=[closed, 0], blender_path=a.blender,
         target_tris=a.dense_tris, passes=100, tolerance=1.05, intermediate_ratio=0.5, last_ratio=0.25, final_ratio=0.2,
         triangulate=True, symmetry=False, voxel_rebuild=a.dense_voxel, relative_voxel_size=0.001, minimum_voxel_size=1e-06,
         seal_distance=0.0001, seal_max_steps=100, seal_keep_trying=True, timeout_seconds=1800)
if a.chain == "video":
    g.pop("328", None) if g.get("328") is None else None
    node(330, "UnwrapMesh", "dense: unwrap", mesh=[dense, 0], segmenter="pec", resolution=1536, padding=1, weld_distance=0.0002)
    node(329, "MemoryCleaner", "ADDED: free VRAM before the bake from generation", input_1=["330", 0],
         enabled=True, always_run=True, clean_vram=True, clean_ram=True)
    node(331, "BakeTextureFromVoxel", "dense: bake from generation", mesh=["329", 0], voxel_colors=["93", 0],
         texture_size=a.texture, reference_mesh=[closed if a.reference_closed else dense, 0])
    node(332, "ApplyTextureToMesh", "dense: apply textures", mesh=["330", 0], base_color=["331", 0], metallic=["331", 1], roughness=["331", 2])
    node(333, "MeshToFile3D", "dense: to GLB", mesh=["332", 0])
    node(334, "SaveGLB", "dense: save", mesh=["333", 0], filename_prefix=f"3d/{a.name}_highpoly")
    node(335, "LODTailorTheMeshTrimmer", "LODTailor low-poly (Blender)", mesh=[dense, 0], blender_path=a.blender,
         target_tris=a.target_tris, passes=3, tolerance=1.05, intermediate_ratio=0.5, last_ratio=0.25, final_ratio=0.2,
         triangulate=True, symmetry=False, voxel_rebuild=True, relative_voxel_size=a.voxel, minimum_voxel_size=1e-06,
         seal_distance=0.0001, seal_max_steps=100, seal_keep_trying=True, timeout_seconds=1800)
    node(336, "PaintMesh", "low: vertex colours", mesh=["335", 0], voxel_colors=["93", 0])
    node(337, "UnwrapMesh", "low: unwrap", mesh=["336", 0], segmenter="pec", resolution=1536, padding=2, weld_distance=0.0002)
    node(338, "MeshSmoothNormals", "low: smooth normals", mesh=["337", 0], crease_angle=180)
    node(339, "MeshToFile3D", "low: to GLB", mesh=["338", 0])
    node(340, "MemoryCleaner", "free memory before baking", input_1=["339", 0], input_2=["333", 0],
         enabled=True, always_run=True, clean_vram=True, clean_ram=True)
    T = a.texture
    node(341, "LODTailorBakeForger", "Bake Forger (Blender)", high_poly=["340", 1], low_poly=["340", 0], blender_path=a.blender,
         prefer_gpu_baking=True, hybrid_cpu_gpu_baking=True, bake_sample_count=a.bake_samples,
         bake_normal_detail=True, normal_map_resolution=T, copy_base_color_texture=True, base_color_resolution=T,
         bake_roughness_texture=True, roughness_resolution=T, bake_metallic_texture=True, metallic_resolution=T,
         bake_emission_texture=True, emission_resolution=T, bake_ao_texture=True, ao_resolution=T, brighter=False,
         auto_bake_margin=True, bake_margin_pixels=16, bake_margin_minimum_pixels=16, bake_margin_resolution_divisor=256,
         fallback_bake_mode="AUTO", coverage_probe_sample_count=4096, extended_ray_sample_ratio=0.005,
         fallback_minimum_recoverable_samples=8, tight_cage_extrusion_factor=a.cage, tight_max_ray_distance_factor=0.029,
         far_cage_extrusion_factor=0.02, far_max_ray_distance_factor=0.092, coverage_alpha_threshold=0.5,
         normal_length_tolerance=0.35, neutral_normal_color="0.5,0.5,1.0,1.0", material_base_color="0.8,0.8,0.8,1.0",
         material_roughness=0.9, material_metallic=0.0, material_specular_level=0.5, load_output_images=False)
    node(342, "WTiVoFastMergeByDistance", "Fast Merge (TEXTURE_SAFE)", model=["341", 0], merge_distance=0.0001,
         centroid_merge=False, remove_degenerate=True, topology_mode="TEXTURE_SAFE", adaptive_retry_step=True, max_attempts=100)
    node(343, "SaveGLB", "low: save", mesh=["342", 0], filename_prefix=f"3d/{a.name}_lowpoly")
json.dump(g, open(a.out, "w"), indent=1)
print("wrote", a.out, len(g), "nodes")
