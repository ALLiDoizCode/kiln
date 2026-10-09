---
status: accepted
---

# The generator is Tripo, used by a person through its web app

Kiln does not call a generator. A person makes the model in Tripo Studio (H3.1, defaults, Privacy set to Private), exports it as a `.glb`, and gives it to `kiln run --model`, which keeps it as the raw output. The owner decided this on 2026-10-08: the Pro subscription's credits can be spent in the web app and the API wallet is empty, and the web app "works well enough". On the text of Tripo's terms a paid plan gives commercial rights with no attribution asked (`learn/research/mixar-vs-tripo.md`).

This sets aside, for now, the constraint in `learn/MISSION.md` that the generator is called through one interface. What keeps the generator swappable is the stage boundary instead: everything after take-in reads only the raw output and the asset record, so a raw output from another generator, a library or a person enters the same way.

## Consequences

- A run starts from a model file, not from a reference image and a prompt. The settings used in the web app are known only to the person, so the asset record has to be told them.
- Nothing about a generation can be repeated: the web app gives no seed and no request record. The kept raw output is the only copy.
- A setting that belongs to the generator, such as which way it faces its models (Tripo: towards glTF's forward, a half-turn from Bevy's), is given with the run until kiln knows generators by name.
- Issue #9 (the generator behind one interface) is not built as written.
