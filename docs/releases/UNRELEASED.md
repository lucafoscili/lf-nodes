# Next release

Changes since [LF Nodes 5.1.0](https://github.com/lucafoscili/lf-nodes/blob/v5.1.0/docs/releases/5.1.0.md).

## Workflow Runner

- **Pose Shoot** (Orchestras, MiniMax H3) shoots poses written one per line,
  or pose photos turned into words by Caption image (Vision), with one
  generated performer (Krea 2, once per shoot) or a supplied synthetic one.
  Each pose's take is written by the H3 Prompt Maker, a fixed full-length
  camera paragraph is appended after writing and review, H3 renders the clip
  (8 seconds at 9:16 by default), and Video to Motion Capture returns the
  motion file, BVH, FBX and the mannequin comparison MP4. Photos never reach
  H3. See [the Pose Shoot guide](https://github.com/lucafoscili/lf-nodes/blob/main/docs/llm/h3-pose-shoot.md).
- Orchestras can expand their stages from the submitted inputs
  (`stages_factory`, up to 64 stages), append fixed text to a text binding
  (`text_suffix`), keep chosen stages visible in history
  (`expose_in_history`), and a failed stage's error now carries the child's
  reason.
- Caption image (Vision) gains caption instructions, a model choice and
  load-and-release on LM Studio's native `/api/v1/chat` endpoint. Video to
  Motion Capture exposes the engine, include shape and stage timeout.

## Release checks

Pose Shoot adds no node: every class it runs is already in the canonical E2E
workflow, and its test checks that inventory. Titanic executes ComfyUI graphs,
not Runner orchestras, so **no Titanic case runs Pose Shoot**; the motion pair
stays disabled inventory, as in 5.1.0. Its offline tests stub only the model
boundary.
