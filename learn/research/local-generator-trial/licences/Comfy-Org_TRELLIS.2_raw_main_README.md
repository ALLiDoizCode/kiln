---
license: mit
tags:
- comfyui
- diffusion-single-file
base_model:
- microsoft/TRELLIS.2-4B
---

# TRELLIS.2

Repackaged model files for ComfyUI.

Original model repository: https://huggingface.co/microsoft/TRELLIS.2-4B

Place the files in the following folders:

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 clip_vision/
│   │   └── dino_v3_vit_l.safetensors
│   ├── 📂 diffusion_models/
│   │   ├── trellis_2_int8_convrot.safetensors
│   │   └── trellis_2_bf16.safetensors
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
</tbody>
</table>
