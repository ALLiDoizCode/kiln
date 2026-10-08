#!/usr/bin/env bash
# Download the model files (Comfy-Org repackagings) with curl; resumable.
set -u
M=.tools/local-gen/src/ComfyUI/models
HF=https://huggingface.co
get(){ mkdir -p "$M/$1"; f="$M/$1/$(basename "$2")"; [ -f "$f" ] || { curl -L --fail --retry 3 -sS -C - -o "$f.part" "$HF/$2" && mv "$f.part" "$f"; }; echo "$(date +%T) $f $(stat -c %s "$f" 2>/dev/null)"; }
get diffusion_models Comfy-Org/TRELLIS.2/resolve/430a9d09b2416687018c8fe8edced2ad4858a439/diffusion_models/trellis_2_int8_convrot.safetensors
get vae Comfy-Org/TRELLIS.2/resolve/430a9d09b2416687018c8fe8edced2ad4858a439/vae/trellis_2_shape_vae_bf16.safetensors
get vae Comfy-Org/TRELLIS.2/resolve/430a9d09b2416687018c8fe8edced2ad4858a439/vae/trellis_2_texture_vae_bf16.safetensors
get clip_vision Comfy-Org/TRELLIS.2/resolve/430a9d09b2416687018c8fe8edced2ad4858a439/clip_vision/dino_v3_vit_l.safetensors
get clip_vision Comfy-Org/Pixal3D/resolve/f37641be376725d324c56626007cc477f1249a69/clip_vision/dino_v3_L_naf_fp32.safetensors
get background_removal Comfy-Org/BiRefNet/resolve/25511f8787e51912e1480706b4e47b8f467fbf72/background_removal/birefnet.safetensors
get geometry_estimation Comfy-Org/MoGe/resolve/1484985258ba7ef45c314144fcf0e90924ffbf44/geometry_estimation/moge_2_vitl_normal_fp16.safetensors
get diffusion_models Comfy-Org/Pixal3D/resolve/f37641be376725d324c56626007cc477f1249a69/diffusion_models/pixal3d_int8_convrot.safetensors
echo DONE
