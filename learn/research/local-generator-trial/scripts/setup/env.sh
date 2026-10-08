# Environment for everything under .tools/local-gen: keeps caches out of the home directory.
export LG="$(git rev-parse --show-toplevel)/.tools/local-gen"
export HF_HOME=$LG/cache/hf TORCH_HOME=$LG/cache/torch UV_CACHE_DIR=$LG/cache/uv PIP_CACHE_DIR=$LG/cache/pip
export XDG_CACHE_HOME=$LG/cache/xdg TMPDIR=$LG/tmp
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 DO_NOT_TRACK=1
export BLENDER_USER_RESOURCES=$LG/blender-user
