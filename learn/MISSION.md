# Mission: A production asset pipeline for my games

## Why
I want to make games alone, on Bevy, as a software engineer who is not a 3D artist. I need a pipeline I designed and understand, which reliably turns out assets good enough to ship, so that art stops being the thing that blocks every game I start.

## Success looks like
- For any asset class (prop, rock, plant, building piece) I can write down what "production ready" means in numbers and checks, and say why each one is there.
- Handed any asset file, from Tripo3D, a store or a script, I can open it, name what it holds and list what is wrong with it.
- I can give kiln a reference image, a prompt and a target profile, and get back a static asset that is production ready for that profile and polished.
- I can say when a bought or hand-modelled asset is the better choice than a generated one, and pass it through the same checks.
- I have designed kiln's pipeline from a clean start: its stages, its tools and the checks between them, each of which I can explain.
- An asset from that pipeline stands in the pit game in Bevy, seen from 0.5 m in first person, inside the frame budget of a GTX 1660.

## Constraints
- Kiln is general: it is not built for one game. It takes a reference image, a prompt and a target profile (decided 2026-10-07; terms in `CONTEXT.md`).
- Tools: Bevy and Blender. The generator is called through one interface so it can be swapped; Tripo3D is a candidate to be evaluated, not a given.
- Output is verified in Bevy only, at the version this repo pins.
- Assets go into games that will be sold, so a generator plan or library is usable only if its licence gives commercial rights without attribution.
- Starting point: an experienced software engineer with almost no 3D vocabulary (2026-10-07).
- The worked case, and the first target profile, is the pit game: first person, assets seen from as close as 0.5 m, a 1.8 m player, a 3 m building grid, and a GTX 1660 or RX 5600 class GPU at 60 frames per second. Principles are taught through it and should carry to other games.
- The repo was cleared on 2026-10-07 for a clean start. The first attempt, made without this knowledge, is at the git tag `first-attempt`; it is a specimen to examine, never the authority.

## Out of scope
- Becoming a hand modeller or sculptor. Enough Blender to inspect, fix and automate, not to make art by hand.
- Characters, rigging and animation, and plants that need transparency, until static assets are solved. (Confirmed 2026-10-07.)
- Building assets by script. Kiln's first shape comes from a generator.
- Consistency of style across a set of assets. It follows from giving consistent reference images.
- Game design and engine systems, which belong in the `pit` repo.
