# Pose Shoot

Open **Orchestras → LF Nodes → MiniMax H3 → Pose Shoot** in Workflow Runner.
Enter one pose per line, upload pose photos, or combine both. Choose the duration
and aspect ratio, then run. The existing Runner form also works through the
installation's phone frontend proxy.

The blocks are:

1. **Krea 2 / Generate Image**, once when no performer is supplied. This existing
   local text-to-image block creates a fictional adult character without taking
   a person's photo as a reference or downloading a model.
2. **Caption image (Vision)** for each photo pose, using the same native LM Studio
   endpoint and model as the writer. It describes body position, weight and limbs;
   only the resulting words continue to Prompt Maker.
3. **MiniMax H3 / Prompt Maker**, with optional review, writes each pose's take.
4. **Render H3 Prompt** receives that prose plus the immutable framing paragraph.
5. **Video to Motion Capture** runs `LF_VideoToMotion`, then connects its motion
   file to `LF_MotionToVideo` for the mannequin/source comparison MP4.

These are ordinary sequence stages, with no separate execution loop or prompt
compiler. Written poses run in line order, followed by photos in upload order.
The Runner sequence limit is 64 stages: each written pose takes three, each photo
four, and automatic performer generation adds one.

## Controls and references

The ordinary form contains **Poses**, **Pose photos**, **Generated performer**,
**My performer is generated**, **Duration**, and **Aspect ratio**. Leave the
performer empty to generate one. To supply one, select a synthetic character
image and declare it generated. That exact image is Picture 1 in every writing
and rendering stage. The automatically generated image is likewise reused for
the entire shoot, rather than generated again for each pose.

Real-person photos belong only in Pose photos. An undeclared performer image or
a pose photo reused as the performer fails with a named `performer` error.
Additional Picture inputs and frame modes are not exposed. The generated-image
declaration is supplied by the caller; it is not an automated photo detector.

Duration and aspect use the same presets as [Idea to Video](h3-video-orchestra.md).
The default is **8 seconds**, with a portrait 9:16 frame. The existing next
preset is 243 frames / 24 fps (10.125 seconds), not exactly ten seconds.
Framing on clips longer than ten seconds is unproven; longer presets remain
available. Writing and rendering receive the same exact duration.

Advanced contains the writer endpoint/model, load-and-release policy, review,
seed, and all capture controls: engine, static camera, smoothing, GPU index,
include shape, stage timeout, and motion correction (on: every take's feet stand
on one floor). The capture defaults and meaning come from
[Video motion capture](../MOTION.md). The mannequin uses that block's default
female body and render shape. Seed is shared with performer generation and each
clip; it does not make the external writer deterministic.

The framing paragraph has one source, `POSE_SHOOT_FRAMING` in `orchestration.py`.
`WorkflowSequenceTextBinding.text_suffix` appends it verbatim **after** writing
and review. The writer cannot edit the appended text. Prompt wording cannot
guarantee the generated camera's behavior; inspect feet, headroom, framing and
camera motion before trusting capture quality.

## Results and failures

Every pose creates visible **Render H3 Prompt** and **Video to Motion Capture**
history entries. The first contains the clip and exact final H3 prompt; the
second contains the `lf.motion.v1` JSON, mannequin comparison MP4, and the
existing BVH/FBX downloads. The parent result also shows the final motion stage.
Intermediate caption/writer runs remain internal sequence stages.

A failed stage stops the shoot. Its error names the pose number/name and stage;
earlier finished clips and captures remain in normal Runner history. Capture
and preview use one existing block, whose node error identifies the failing
operation. Nothing retries a failed pose automatically.

## One-time host setup

Use the same writer host settings described in [Idea to Video](h3-video-orchestra.md).
Photo poses require a vision-capable writer at the native `/api/v1/chat` endpoint.
If model management is enabled, each authoring block loads/reuses the selected
downloaded model and releases that instance afterward. H3 and its Comfy nodes,
the existing Krea 2 generation models for automatic performers, and the motion
runtime/SMPL-X prerequisites must already be installed. The orchestra performs
no installation or model download.
Catalogue setup warnings include optional branches; submission checks only the
stages selected by the supplied poses and performer.

## Owning code and checks

- Assembly and registration: `modules/workflow_runner/workflows/orchestration.py`,
  `minimax_h3_pose_shoot` in the existing `WORKFLOWS` registry list.
- Performer: the existing `krea2.generate` block and its graph.
- Photo description: `caption_image_vision.py`, using `LF_LocalChatCompletions`.
- Writing/rendering: `minimax_h3_prompt_maker.py` and `minimax_h3_prompt_video.py`.
- Capture/preview: `video_to_mocap.py` and the two existing motion nodes.
- Sequence bindings: `services/registry.py` and `services/sequence_runtime.py`.
  Dynamic declarations expand once into the ordinary persisted stage plan;
  selected child runs are visible in history. Existing orchestras keep their
  private child-history behavior. No new public node or required hero asset.

Run each focused group in a separate process, as for Idea to Video:

```sh
python -B -I scripts/quality/run_pytests.py -q modules/workflow_runner/tests/test_h3_pose_shoot_orchestra.py
python -B -I scripts/quality/run_pytests.py -q modules/workflow_runner/tests/test_caption_image_vision_workflow.py
python -B -I scripts/quality/run_pytests.py -q modules/workflow_runner/tests/test_video_to_mocap_workflow.py
python -B -I scripts/quality/run_pytests.py -q modules/workflow_runner/tests/test_minimax_h3_prompt_maker_workflow.py
python -B -I scripts/quality/run_pytests.py -q modules/workflow_runner/tests/test_minimax_h3_prompt_video.py
python -B -I scripts/quality/run_pytests.py -q modules/workflow_runner/tests/test_h3_video_orchestra.py modules/workflow_runner/tests/test_orchestration_workflows.py
python -B -I scripts/quality/run_pytests.py -q modules/workflow_runner/tests/test_sequence_text_binding.py modules/workflow_runner/tests/test_sequence_dynamic_stages.py modules/workflow_runner/tests/test_sequence_runtime.py modules/workflow_runner/tests/test_sequence_store_sqlite.py modules/workflow_runner/tests/test_workflow_sequences.py
python -B -I scripts/quality/run_pytests.py -q modules/tests
```

The new orchestra tests use synthetic inputs and stub execution at model/runtime
boundaries. They exercise words/photos, supplied/generated performers, exact
framing, image isolation, one shared performer, capture options and failures
with retained history. CI includes these focused groups.

Titanic coverage here is **inventory**, checked against its canonical fixture
and declared exemptions. Titanic currently executes Comfy graphs, not Runner
orchestras; its motion nodes remain explicitly disabled in that fixture.
Hydration, targeted execution and visual motion acceptance require the landing
host and are not claimed by offline tests. No live service run is part of this
change.
