---
license: mit
tags:
- comfyui
- diffusion-single-file
base_model:
- TencentARC/Pixal3D
---

# Pixal3D

Repackaged model files for ComfyUI.

Original model repository: https://huggingface.co/TencentARC/Pixal3D

Place the files in the following folders:

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 diffusion_models/
│   │   ├── pixal3d_bf16.safetensors
│   │   └── pixal3d_int8_convrot.safetensors
│   │   ├── pixal3d_multiview_bf16.safetensors
│   │   └── pixal3d_multiview_int8_convrot.safetensors
│   ├── 📂 clip_vision/
│   │   └── dino_v3_L_naf_fp32.safetensors
│   ├── 📂 vae/
│   │   ├── trellis_2_shape_vae_bf16.safetensors
│   │   └── trellis_2_texture_vae_bf16.safetensors
```

## Workflows

<table>
<thead>
<tr><th align="center" valign="middle" style="text-align:center;vertical-align:middle">Workflow</th><th colspan="2" align="center" valign="middle" style="text-align:center;vertical-align:middle">Thumb</th></tr>
</thead>
<tbody>
<tr><td align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_pixal3d_trellis2_image_to_model.json">Pixal3D & TRELLIS.2: Image to Model</a></td><td colspan="2" align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_pixal3d_trellis2_image_to_model.json"><img src="https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/3d_pixal3d_trellis2_image_to_model-1.webp" width="200" height="200" alt="Pixal3D & TRELLIS.2: Image to Model"></a></td></tr>
<tr><td align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_pixal3d_multi_views.json">Pixal3D: Multi Views to 3D</a></td><td colspan="2" align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/3d_pixal3d_multi_views.json"><img src="https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/3d_pixal3d_multi_views-1.webp" width="200" height="200" alt="Pixal3D: Multi Views to 3D"></a></td></tr>
</tbody>
</table>
