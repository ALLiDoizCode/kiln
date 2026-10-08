---
license: mit
tags:
- comfyui
- diffusion-single-file
base_model:
- ZhengPeng7/BiRefNet
- egeorcun/lucida
---

# BiRefNet

Repackaged model files for ComfyUI.

Original model repository:

- https://huggingface.co/ZhengPeng7/BiRefNet
- https://huggingface.co/egeorcun/lucida

Place the files in the following folders:

```
📂 ComfyUI/
├── 📂 models/
│   ├── 📂 background_removal/
│   │   ├── birefnet.safetensors
│   │   └── lucida.safetensors
```

## Workflows

<table>
<thead>
<tr><th align="center" valign="middle" style="text-align:center;vertical-align:middle">Workflow</th><th colspan="2" align="center" valign="middle" style="text-align:center;vertical-align:middle">Thumb</th></tr>
</thead>
<tbody>
<tr><td align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/utility_birefnet_remove_background.json">Remove Background: BiRefNet</a></td><td align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/utility_birefnet_remove_background.json"><img src="https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/utility_birefnet_remove_background-2.webp" width="200" height="200" alt="Remove Background: BiRefNet"></a><div align="center">Before</div></td><td align="center" valign="middle" style="text-align:center;vertical-align:middle"><a href="https://github.com/Comfy-Org/workflow_templates/blob/main/templates/utility_birefnet_remove_background.json"><img src="https://raw.githubusercontent.com/Comfy-Org/workflow_templates/main/templates/utility_birefnet_remove_background-1.webp" width="200" height="200" alt="Remove Background: BiRefNet"></a><div align="center">After</div></td></tr>
</tbody>
</table>
