# 3. Assets are code, built by headless Blender

Each prop is a Python build script (`source/<asset>/build.py`) plus a spec (`spec.json`). The `.blend` and `.glb` are build outputs. Blender is driven only through `tools/bl`, which runs the pinned binary in background mode with factory settings, no network, an isolated user directory, and a non-zero exit on any exception.

No MCP server or live Blender session is part of the pipeline: both run model-written Python with no record of what produced the result, and a build script can be diffed, reviewed and re-run.

Levels are the expected exception. They will be laid out by hand, so their `.blend` will be the master; that decision is deferred until the first level.
