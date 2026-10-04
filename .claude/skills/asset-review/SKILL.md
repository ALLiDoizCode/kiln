---
name: asset-review
description: Independent review of an asset by agents that did not build it, then a retrospective. Use when an asset has passed its gates and before the user is asked to approve it, or when the user asks for an asset to be reviewed.
---

# Asset review

The agent that built an asset reads its own contact sheet charitably. A review is done by **reviewers that did not build it** and see only what a stranger would: the brief, the spec, the contact sheet, the reports and the exported file.

## 1. Dispatch two reviewers

Launch two sub-agents in parallel with the Agent tool. Give each the asset's name, the repo path, and its section below as the whole brief. Leave out the build script, your own observations and anything you believe about the asset: a reviewer told what to expect finds it.

Each reviewer reads `CONTEXT.md` first, then only these: `source/<asset>/brief.md`, `spec.json`, `review/<phase>/sheet.png` and its tiles, `out/reports/*.json`, and `assets/models/<asset>.glb` (inspected with `python tools/bevy_lint.py` or by reading its JSON chunk; the reviewer writes no files in the repo).

### Reviewer A: spec

Does the asset match what was asked for? For each sentence of the brief that makes a claim about the asset, find the tile or report line that confirms or refutes it and quote the measurement. Then the reverse: list anything visible in the sheet that the brief never asked for. Then list every number in the brief's prose that has no row in its Numbers table.

### Reviewer B: standards

Is the asset well made, whatever it is? Check each **smell** below against the tiles and reports, and report it as present, absent, or not visible in this sheet:

- **Scale**: implausible beside the player-height figure, in the scale tiles and the bevy tile.
- **Wasted triangles**: edges in the clay tiles that sit on no silhouette, colour boundary or shading break.
- **Starved silhouette**: a curve or corner that reads as faceted or crude at the brief's closest viewing distance.
- **Shading break**: a face lighter or darker than its neighbours with no lighting reason.
- **Engine mismatch**: the bevy tile differing from the material tiles in colour, contrast or shading by more than lighting explains.
- **Flat read**: adjacent materials too close in value to tell apart in the bevy tile.
- **Floating or sunk**: the base above or below the ground in the scale and bevy tiles.
- **Hidden faces**: geometry no camera could ever see, visible as overdraw in the wireframe.
- **Material sprawl**: more material slots than colours the eye can tell apart.
- **Naming**: default or meaningless object, mesh or material names in the reports.
- **Budget slack**: triangle count far under budget on an asset that looks crude, or at budget on one that looks simple.

Each reviewer returns findings only, each one tied to a named tile or a report line and a measurement. A finding with no evidence is dropped.

## 2. Reconcile

Put both reports side by side with your own `observations.md`. For each finding, either show the evidence that it is wrong, or accept it. Every accepted finding becomes one of: a fix to the asset, a change to the brief put to the user, or a question for the user. Write the result to `source/<asset>/review/<phase>/review.md`, findings first, with the reviewer that raised each.

Done when every finding from both reviewers appears in `review.md` with its outcome.

## 3. The user decides

Give the user the sheet path and the open findings. Approval is theirs: on an explicit yes, run `python tools/baseline.py approve <asset> <phase>`.

## 4. Retrospective

After the user's verdict, list everything that was caught by an eye (yours, a reviewer's or the user's) at any point in this asset's life. For each, answer: could a number have caught it? If yes, it is an **escaped defect**: hand it to the `asset-checks` skill. If a smell was missing from the list above, add it. If a term was missing from `CONTEXT.md`, add it.

Done when each caught-by-eye item has a check, a new smell, or a written reason why only an eye can catch it, in `review.md`.
