# Teaching notes

- The workspace is `learn/` inside the kiln repo (chosen 2026-10-07), so the course sits beside the pipeline it informs. Shared lesson components are in `learn/assets/`.
- The learner called kiln "a weak uninformed first attempt" to be kept "in name only". On 2026-10-07 they asked for a clean start and the repo was cleared: only the Bevy viewer, the Blender wrapper and installer, and `learn/` remain; the rest is at the git tag `first-attempt`. Do not cite the first attempt's ADRs, CONTEXT.md or gates as correct. Two of its models are kept in `learn/specimens/` to inspect.
- Glossary: add a term to `reference/glossary.html` only once the learner has used it correctly (quiz answer or their own explanation). None added yet; lesson 1 introduced mesh, primitive, vertex, attribute, normal, UV, index, material.
- Each quiz ends with a "copy results" button; ask the learner to paste the result so learning records rest on evidence.
- Quiz options must match in word count and nearly in length.
- Mission out-of-scope line on characters and animation was the teacher's assumption; confirm it.
- Likely next lessons, in order: what a material and its textures are (base colour, normal map, roughness); UVs and texel density; why high-poly to low-poly baking exists; reading a Tripo output against all of that; budgets.
