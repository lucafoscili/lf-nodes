# Idea to Video

Open **Orchestras → LF Nodes → MiniMax H3 → MiniMax H3 / Idea to Video** in
Workflow Runner. Write a short idea, optionally upload Picture 1, choose duration
and aspect ratio, and run. The same Runner page works on a phone through the
installation's existing frontend proxy.

The two blocks are:

1. **Prompt Maker** writes the H3 prompt and, by default, reviews it.
2. **Render H3 Prompt** receives that exact prose and renders video with audio.

No prompt schema or compiler is inserted between them. The final result includes
the video and the exact prompt sent to H3. Each child run remains in Runner history
for diagnosing authoring versus rendering failures. Review is an optional second
LLM pass, not a guarantee that the prose or resulting video is correct.

## Controls and references

The ordinary form contains only the idea, Picture 1, duration, and aspect ratio.
Advanced contains review, explicit H3 mode, connection/model controls, additional
instructions, Pictures 2–9, and seed. References may have different dimensions;
fill them consecutively so the writer and renderer see identical Picture order.

Automatic mode uses text-to-video without images and full-reference generation
with images. Explicit first-frame, last-frame, and first-plus-last modes remain
available. References do not become opening frames unless a frame mode is chosen.

Duration is selected from the existing H3 frame presets. Both blocks receive the
same precise seconds value; the renderer uses the corresponding frame count at
24 fps. The UI rounds the seconds label, not the underlying value. Rendering uses
the existing native-canvas, Kitchen 20-step recipe and existing device policy.

## One-time host setup

The following optional settings in LF Nodes' local `.env` supply this orchestra's
Advanced defaults. Restart Comfy after changing them:

```dotenv
WORKFLOW_RUNNER_LMS_ENDPOINT=http://127.0.0.1:1234/api/v1/chat
WORKFLOW_RUNNER_LMS_MODEL=your-exact-downloaded-model-key
```

The endpoint is reached by the server, not by the phone. Setting a model key also
defaults **Load and release writer** on for this orchestra. It loads or reuses that
exact model, performs writing/review, then releases that instance before video
generation. It does not unload other models or reload the writer after rendering.
If authoring fails, the writer may remain loaded. Turn the option off to manage
residency yourself; with a blank model the sole already-loaded LLM is used.

These settings do not change standalone Prompt Maker defaults or public nodes.
H3 weights, required Comfy nodes, LMS, and a downloaded vision-capable writer must
already be installed. No model downloads are performed by this orchestra.

## Owning code and checks

- Assembly: `modules/workflow_runner/workflows/orchestration.py`,
  `minimax_h3_video_orchestra`.
- Authoring: `minimax_h3_prompt_maker.py` and its existing public atomic node.
- Rendering: `minimax_h3_prompt_video.py`, reusing the existing H3 graph templates.
- Text handoff: `WorkflowSequenceTextBinding` in the Runner registry/runtime;
  reads the declared prior output from durable history with the existing owner
  and earlier-stage checks. Missing or ambiguous text stops the sequence.
- Focused integration tests: `test_h3_video_orchestra.py`; block contracts:
  `test_minimax_h3_prompt_maker_workflow.py`, `test_minimax_h3_prompt_video.py`.

Checkpoint 2026-09-26: 119 authoring/render-block tests and 23 assembly tests
passed; separately, 105 generic sequence/submission tests and 10 executor/preflight
tests passed. The suites are separate because existing workflow tests install
module doubles that interfere with the broader service imports in one process.
The real catalogue loaded the orchestra, the 390×844 phone-sized form was visually
checked, and the existing LAN proxy served the page. Qwen's configured model key
was found in LMS with no loaded instance. No video render was submitted during
that implementation check; end-to-end acceptance was left for Luca's phone trial.

## Accepted milestone — 2026-09-26

Luca subsequently tested the orchestra from the phone and accepted the result:
"Works beautifully 🤩 I’d milestone this 🦾". **Keep:** the two-block,
prose-preserving phone workflow. The accepted source baseline is `af78eb2`.
See [H3 accepted checkpoints](../H3_CHECKPOINT.md) for the milestone boundary.

This is user-reported end-to-end acceptance, not an additional agent-reviewed
render. The unchanged implementation checks above remain valid; no extra GPU
run was needed to record the milestone. **Deferred:** broader creative-quality
coverage and failure/cancellation cleanup. Acceptance of this run does not
guarantee every reference mode, identity constraint, or audio case.
