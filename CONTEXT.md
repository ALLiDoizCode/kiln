# kiln

Kiln turns a reference image and a prompt into a 3D asset that is production ready for a stated target. It exists so that a software engineer who is not a 3D artist can get shippable assets without making them by hand.

## Language

### A run

**Run**:
One pass through kiln for one asset, given a reference image, a prompt, a size and a target profile.

**Size**:
The asset's largest dimension in metres, given to a run because neither the reference image nor the generator knows it.
_Avoid_: Scale (which is the factor applied, not the result)

**Reference image**:
The picture given to a run that shows what the asset should look like.
_Avoid_: Concept, input image

**Target profile**:
A named set of numbers that says where an asset will be used: viewing distance, triangle and texture budgets, hardware and engine. The pit game's profile is the first.
_Avoid_: Preset, quality level, spec

**Production ready**:
Passing every check of the run's target profile. An asset is never production ready in general, only for a profile.
_Avoid_: Game ready, done, final

**Polished**:
Free of defects visible at the profile's viewing distance and faithful to the reference image. It does not include consistency with other assets.

**Asset**:
What a run produces: a model file together with its asset record.

**Asset record**:
The file beside the model that holds its licence, its source, the reference image and prompt, the target profile it was checked against and the check results.
_Avoid_: Manifest, metadata, sidecar

**Raw output**:
The file a generator returns, kept unchanged as an input so that every later stage can be repeated without generating again.
_Avoid_: Draft, source mesh

### Where an asset comes from

**Generator**:
An external AI service or model that produces a first shape from a reference image and a prompt. Kiln calls one and owns every stage after it.
_Avoid_: Model (which means a 3D model elsewhere), AI tool

**Generated asset**:
An asset whose first shape came from a generator.

**Bought asset**:
An asset taken from a library or store, paid or free, which enters kiln at the stage after generation.
_Avoid_: Downloaded asset, stock asset

**Hand-modelled asset**:
An asset whose shape a person made in an authoring tool, which enters kiln at the stage after generation.

**Production**:
Making assets in general, by any source. "Generation" always means by a generator.

**Generator trial**:
A comparison in which the same reference images are put through several generators and the raw outputs are measured and looked at the same way, to choose which generator kiln calls.
_Avoid_: Bake-off (baking means something else here), benchmark

### What kiln handles

**Static asset**:
An asset with no skeleton and no animation, such as a prop, rock, building piece or piece of furniture. The only kind kiln handles for now.

### Review

**Shape review**:
The first stop in a run, where a person approves or rejects the generator's raw output against the reference image.

**Final review**:
The last stop in a run, where a person approves or rejects the finished asset in the viewer.

**Review pictures**:
The fixed set of renders kiln makes at each review, from set distances and angles including the target profile's closest viewing distance, so that reviews can be compared across runs.
_Avoid_: Contact sheet, screenshots
