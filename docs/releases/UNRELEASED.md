# Next release

Changes since [LF Nodes 5.1.0](https://github.com/lucafoscili/lf-nodes/blob/v5.1.0/docs/releases/5.1.0.md).

## Changed nodes

- **Video to motion** runs RGB MoCap's Motion Correction after the engine,
  on by default (`motion_correction`, appended last): one floor found from the
  feet's contacts, each standing foot held on it, so a foot on tiptoe keeps its
  toes on the floor instead of sinking below the other foot's plane. The motion
  JSON, BVH and FBX carry the corrected motion, and the result details report
  the floor and any warning of the app's. Off returns the engine's motion as
  before. Video to Motion Capture and Pose Shoot expose it with the other
  capture controls. See [Video motion capture](https://github.com/lucafoscili/lf-nodes/blob/main/docs/MOTION.md#motion-correction).
- **Video to motion** grounds the feet before that correction, on by default
  (`ground_feet`, `push_in` and `planted_seconds`, appended last): the camera's
  drift along the floor is taken out, a camera that pushes in no longer walks
  the performer toward it, a standing foot on its heel is set flat, and chosen
  seconds hold both feet planted. The correction then runs again on the
  prepared capture, and the result details list each step. Video to Motion
  Capture exposes all three; Pose Shoot the first two. See
  [Grounding the feet](https://github.com/lucafoscili/lf-nodes/blob/main/docs/MOTION.md#grounding-the-feet).

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
