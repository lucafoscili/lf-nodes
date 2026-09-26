# H3 Prompt Maker

Start with an idea such as **Walking from behind in a medieval town**, connect a
reference image, and run. `auto` chooses text generation without images and
full-reference generation with images. Duration and Review are ordinary controls;
model, endpoint, explicit frame mode, reasoning, temperature, and optional extra
instructions are marked Advanced in Comfy's schema.

Connect another image to the next reference socket as it appears. Each socket
accepts a single image, batch, or ordered list. Inputs are flattened in socket
number order, then batch/list order; no shared dimensions or resizing is required.
The original `image` socket still accepts an **Images to list** connection.
Up to nine references are supported. The flattened order defines Picture labels;
socket suffixes are not fixed Picture IDs when a socket contains a batch/list.

An image supplies reusable identity/content by default, not an opening frame.
Use `i2va`, `fl2va`, or `l2va` for fixed first/last frames, or describe reference
roles in ordinary words. A short subject binding is enough when unambiguous.
Unspecified environment, action development, camera and sound are creative choices.

## Implementation and outputs

- Public node: `modules/nodes/llm/h3_prompt_maker.py`.
- System instructions: `modules/utils/helpers/llm/h3_prompt/` (local Markdown;
  includes adapted H3 grammar, not just links to a skill).
- Writer sees the original ordered images and user idea directly. Review defaults
  on and returns a revised or unchanged complete prompt. Review off skips that
  call. Structural H3 validation remains on, with at most one format-repair call.
- Compiler: `modules/workflow_runner/prompts/minimax_h3.py`. It accepts labeled
  H3 text and preserves legacy JSON callers. No intermediate `uses` arrays are
  required from the new writer. It checks syntax/reference consistency, not
  visual quality; review completion is not proof of semantic correctness.
- Socket order stays `prompt`, `validation_report`, `visual_inventory`.
  The last socket is retained for saved workflows: `pictures` contains ordered
  ordinals and empty `facts`; `inventoryPerformed: false` explicitly records
  that the exhaustive inventory stage was removed. Consumers needing the old
  facts ledger must not treat this receipt as extracted visual evidence.
- Final prompt/report/receipt remain in `ui.lf_output` and the existing code
  widget, so history and cached output retain the result. No source images or
  base64 payloads are added to that history.

Compatibility change: newly created nodes default to `auto`; saved explicit
mode values remain unchanged. Existing input names/defaults otherwise remain;
`image_2` through `image_9` and `instructions` are appended. For an existing node
saved with `t2va`, select Auto before connecting reference images.

For explicit memory handoff, see [LMS Load/Unload](lms-models.md). Set the same LMS
endpoint on connected operations. A blank model still uses the sole loaded LLM.

## Checks and live evidence

Offline checkpoint, 2026-09-26: 257 focused Python contracts and 241 related
Runner/pipeline contracts passed; the final node-only recheck passed all 38 tests.
The frontend suite passed 590 tests, with 25 focused socket/widget tests rechecked
after type-only adjustments. The full frontend build and static node contracts
passed. At that offline checkpoint, live provider quality and Comfy/Titanic
hydration were untested. The subsequent [Qwen live trial](h3-live-trial.md)
exercises the public Python nodes against LMS, without starting Comfy.

```powershell
python -I scripts/quality/run_pytests.py -q modules/tests/nodes/llm/test_h3_prompt_maker.py modules/workflow_runner/tests/test_minimax_h3_prompt_composer.py modules/tests/utils/helpers/llm/test_h3_prompt_skill.py
corepack yarn exec vitest run web/src/helpers/h3PromptMaker.test.ts --pool=threads
```

The accepted September 7 video baseline is preserved in
[H3_CHECKPOINT.md](../H3_CHECKPOINT.md); it does not prove this new authoring path.
Live acceptance for this batch: one short walking idea plus one reference, then
two differently sized references; inspect concise bindings, identity, new setting,
camera intent, no invented frame anchor, and no internal bookkeeping in the output.
Also verify saved-node reload, growing sockets, review opt-out, and exact-instance
LMS release. Comfy hydration and live provider quality require the running services.
