# H3 Prompt Maker

Start with an idea such as **Walking from behind in a medieval town**, connect a
reference image, and run. `auto` chooses text generation without images and
full-reference generation with images. Duration and Review are ordinary controls;
model, endpoint, explicit frame mode, reasoning, temperature, and optional extra
instructions are marked Advanced in Comfy's schema.

For a single phone-friendly run through prompt writing and video generation, use
the [Idea to Video orchestra](h3-video-orchestra.md) in Workflow Runner.

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
- Complete teaching examples in `h3_prompt/examples/` are selected by active
  mode. The current request repeats its mode, section order, duration, and image
  mapping beside the original idea; example content must not enter the new scene.
- Writer sees the original ordered images and user idea directly. Review defaults
  on and receives the idea and draft as plain text, returning revised or unchanged
  complete prose. Review off returns the writer's text. There is exactly one
  provider call without review and two with it; provider errors stop the run.
- Generation is prose-only: no intermediate JSON, schema parsing, compilation,
  structural validation, timestamp rewriting, or format-repair loop. H3 labels,
  reference roles, and fixed-frame alignment wording are supplied as writing
  guidance in the system prompt. The final model text is returned unchanged.
  Basic input/cardinality and transport checks remain; review completion does
  not prove format compliance or semantic correctness.
- Socket order stays `prompt`, `validation_report`, `visual_inventory`.
  `validation_report` is a legacy compatibility name for authoring/review status:
  `valid` is `null`, `validation` is `not_performed`. It no longer contains parsed
  section/shot counts or schema-validation findings. This is a deliberate report
  semantics change; consumers must not infer a valid H3 prompt from run success.
  The last socket is retained for saved workflows: `pictures` contains ordered
  ordinals and empty `facts`; `inventoryPerformed: false` explicitly records
  that the exhaustive inventory stage was removed. Consumers needing the old
  facts ledger must not treat this receipt as extracted visual evidence.
- Final prompt/report/receipt remain in `ui.lf_output` and the existing code
  widget, so history and cached output retain the result. No source images or
  base64 payloads are added to that history.

The older compiler/composer helpers remain for legacy helper callers and
separate deterministic H3 workflows. The Prompt Maker no longer imports them.

Compatibility change: newly created nodes default to `auto`; saved explicit
mode values remain unchanged. Existing input names/defaults otherwise remain;
`image_2` through `image_9` and `instructions` are appended. For an existing node
saved with `t2va`, select Auto before connecting reference images.

For explicit memory handoff, see [LMS Load/Unload](lms-models.md). Set the same LMS
endpoint on connected operations. A blank model still uses the sole loaded LLM.

The Runner Prompt Maker block also offers an Advanced **Load and release writer**
toggle (off by default). Select an exact downloaded model key to load it before
authoring and release that instance after review, before exposing the prompt to
the next orchestra stage. This explicitly also releases an already-loaded
matching instance. Authoring failure can leave the writer loaded; this is an
ordered graph handoff, not a guaranteed cleanup handler. Portable preparation
validates settings and reference order without staging uploads or contacting LMS.

## Checks and live evidence

Prose-only revision: 63 focused node/instruction/registry/metadata tests and 50
Runner tests passed, along with syntax compilation and the static node contract
check. These verify unchanged sockets, ordered image inputs, one/two provider
calls, verbatim output/history, and honest unvalidated status. The subsequent
[six prose-only live trials](h3-prose-trials.md) exercised this revision against
Qwen3.5 4B through LMS: five returned prose and one returned no answer. Reference
handling, history, and exact-instance unloading worked, but prompt quality and
review were inconsistent; this is not authoring-quality acceptance. No Comfy
hydration or video render was performed. Frontend code is unchanged, so the
earlier frontend build evidence still applies.

The [worked-example comparison](h3-example-trials.md) records the subsequent
mode-specific teaching examples and explicit-brief revision against the same
ideas and Qwen settings. It separates improvements in format/action coverage from
remaining scene-coherence and review weaknesses.

Offline checkpoint, 2026-09-26: 257 focused Python contracts and 241 related
Runner/pipeline contracts passed; the final node-only recheck passed all 38 tests.
The frontend suite passed 590 tests, with 25 focused socket/widget tests rechecked
after type-only adjustments. The full frontend build and static node contracts
passed. At that offline checkpoint, live provider quality and Comfy/Titanic
hydration were untested. The subsequent [Qwen live trial](h3-live-trial.md)
exercised the earlier compiler-backed Python nodes against LMS without starting
Comfy; it is not live acceptance of this later prose-only revision.

```powershell
python -I scripts/quality/run_pytests.py -q modules/tests/nodes/llm/test_h3_prompt_maker.py modules/workflow_runner/tests/test_minimax_h3_prompt_composer.py modules/tests/utils/helpers/llm/test_h3_prompt_skill.py
corepack yarn exec vitest run web/src/helpers/h3PromptMaker.test.ts --pool=threads
```

The accepted September 7 video baseline is preserved in
[H3_CHECKPOINT.md](../H3_CHECKPOINT.md); it does not prove this new authoring path.
The prose-only trials cover the short walking idea, differently sized references,
review opt-out, exact speech, fixed first-frame intent, and exact-instance release.
Authoring-quality follow-up remains necessary; see the trial's keep/defer judgment.
Saved-node reload and growing sockets still need live Comfy/Titanic inspection,
and prompt observations do not establish rendered-video quality.
