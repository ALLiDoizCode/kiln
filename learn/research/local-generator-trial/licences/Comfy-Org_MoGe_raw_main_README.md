---
license: mit
tags:
- comfyui
- diffusion-single-file
base_model:
- Ruicheng/moge-vitl
- Ruicheng/moge-2-vitl
- Ruicheng/moge-3-vitg
- Ruicheng/moge-3-vitl
---

# MoGe: Accurate Monocular Geometry Estimation

Repackaged model files for ComfyUI.

Original model repository:

- https://github.com/microsoft/moge
- https://huggingface.co/Ruicheng/moge-vitl
- https://huggingface.co/Ruicheng/moge-2-vitl
- https://huggingface.co/Ruicheng/moge-3-vitg
- https://huggingface.co/Ruicheng/moge-3-vitl

Place the files in the following folders:

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 geometry_estimation/
│   │   ├── moge_1_vitl_fp16.safetensors
│   │   ├── moge_2_vitl_normal_fp16.safetensors
│   │   ├── moge_3_vitg_fp16.safetensors
│   │   └── moge_3_vitl_fp16.safetensors
```

## Workflows

<table>
<thead>
<tr><th align="center" valign="middle" style="text-align:center;vertical-align:middle">Workflow</th><th colspan="2" align="center" valign="middle" style="text-align:center;vertical-align:middle">Thumb</th></tr>
</thead>
<tbody>
<tr><td align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_moge_perspective_to_mesh.json">MoGe: Perspective Geometry Estimation</a></td><td colspan="2" align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_moge_perspective_to_mesh.json"><img src="https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/3d_moge_perspective_to_mesh-1.webp" width="200" height="200" alt="MoGe: Perspective Geometry Estimation"></a></td></tr>
<tr><td align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_moge_panorama_to_mesh.json">Moge: Panorama to Mesh</a></td><td colspan="2" align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_moge_panorama_to_mesh.json"><img src="https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/3d_moge_panorama_to_mesh-1.webp" width="200" height="200" alt="Moge: Panorama to Mesh"></a></td></tr>
<tr><td align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/utility_moge_depth_estimation.json">Depth Estimation: MoGe</a></td><td align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/utility_moge_depth_estimation.json"><img src="https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/utility_moge_depth_estimation-2.webp" width="200" height="200" alt="Depth Estimation: MoGe"></a><div align="center">Before</div></td><td align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/utility_moge_depth_estimation.json"><img src="https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/utility_moge_depth_estimation-1.webp" width="200" height="200" alt="Depth Estimation: MoGe"></a><div align="center">After</div></td></tr>
<tr><td align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/utility_moge3_geometry_estimation.json">Geometry Estimation: MoGe 3</a></td><td align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/utility_moge3_geometry_estimation.json"><img src="https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/utility_moge3_geometry_estimation-2.webp" width="200" height="200" alt="Geometry Estimation: MoGe 3"></a><div align="center">Before</div></td><td align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/utility_moge3_geometry_estimation.json"><img src="https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/utility_moge3_geometry_estimation-1.webp" width="200" height="200" alt="Geometry Estimation: MoGe 3"></a><div align="center">After</div></td></tr>
</tbody>
</table>
