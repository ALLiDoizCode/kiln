# 6. Colours are written as sRGB hex

Briefs and specs give colours as sRGB hex (`#5a3820`), the form colour pickers and people use. Blender and glTF store base colour as linear RGB; `linear_rgb` in `tools/pipeline.py` converts, and build scripts read their colours from the spec through it.

The crate's first brief gave linear values directly. "Dark wood" at linear (0.30, 0.17, 0.08) rendered as a mid tan, because linear 0.30 displays at about 58% brightness. Nobody can judge a linear triple by reading it, so the brief could not be checked against the render.
