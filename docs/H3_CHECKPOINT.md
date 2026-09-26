# H3 accepted checkpoints

## Current milestone: phone-friendly Idea to Video — 2026-09-26

Decision: **keep**, accepted by Luca after testing the new orchestra from the
phone: "Works beautifully 🤩 I’d milestone this 🦾". This closes the end-to-end
acceptance deferred at the previous handoff. Acceptance is Luca's report, not a
new independent audiovisual inspection by the agent.

Accepted implementation: `af78eb2ca7edecaa366a7cdbd9b07db11b7ea64e` and its
preceding authoring, renderer, and text-handoff commits. See the
[Idea to Video guide](llm/h3-video-orchestra.md) for controls, host setup, owning
code, and verification details.

Durable Runner history contains one matching successful orchestra run. Its
parent and both child records are marked `succeeded`:

- Parent: `lf-sequence:d7e3c0423e884d80b0e4a22011c7f833`,
  2026-09-26 10:52:02–10:56:41 UTC (12:52–12:56 Europe/Rome).
- Prompt Maker: `9dd5e799-1087-4be0-8836-99de747a184e`.
- Renderer: `40263f99-fbed-4706-9e18-11f16a15fb67`.
- Output relative to Comfy output:
  `LF_Nodes/MiniMaxH3/PromptVideo/kitchen_quality/seed-42-refs1-f124_00001_.mp4`.

The output file's presence was checked without replaying, copying, or changing
the media. Run records establish execution success; Luca's report establishes
acceptance of the experience.

The milestone includes:

- A small phone form: ordinary-language idea, optional reference, duration, and
  aspect ratio; extra references and expert controls remain under Advanced.
- Prose-only Prompt Maker with mode-specific teaching examples and optional
  review, on by default; no intermediate prompt schema or compiler.
- A real two-block Runner orchestra passing the exact saved prompt to H3, with
  shared duration and ordered references, returning video and the prompt used.
- Explicit LMS load/release ordering so successful writing and review release
  the selected writer before video rendering. The local host defaults select
  Luca's existing Qwen3.5 4B setup; generic source does not hardcode that endpoint.

Verification retained from the implementation checkpoint: 119 block tests,
23 assembly tests, 105 sequence/submission tests, and 10 executor/preflight tests
passed in isolated groups. The live catalogue reported ready, and the phone-sized
form and existing LAN proxy were checked. No source behavior changed for this
milestone, so these checks were not repeated and no extra render was queued.

This accepts the tested experience, not every reference mode, prompt, identity
constraint, or audio case. **Deferred:** broader creative-quality coverage and
cleanup after authoring failure/cancellation; downstream unload currently runs
only on the successful path. Public-node saved-graph/Titanic acceptance is a
separate scope. The historical baseline below remains preserved for comparison.

## Historical milestone: reviewed compiler pipeline — 2026-09-07

Decision: **keep**, accepted by Luca on 2026-09-07 after viewing the full
prompt-to-video result.

The public `LF_H3PromptMaker` node lives with the LLM nodes and encapsulates
visual inventory, reference scope, planning, independent review, one bounded
repair, re-review, and deterministic H3 compilation. Workflow Runner reuses
that atomic operation. Review defaults on and can be disabled explicitly.
The reviewer uses a 32768-token / 600-second budget; writing stages retain
8192 tokens / 300 seconds. An empty model resolves the loaded LMS model.

The accepted four-reference trial used Qwen3.5 4B with vision. The first trial
failed review after repair and did not render. After tightening planner repair
instructions, the next trial completed `fail -> planner repair -> pass` with
zero final audit findings and a 6421-character compiled prompt.

- Maker run: `2eceb24d-3658-4bd0-84c7-d0543e7791b5` (334 seconds).
- Render run: `501bddf2-22d4-40aa-aac0-8af484252564` (2104 seconds).
- Output relative to Comfy output:
  `velora/minimax_h3_r2v/native_quality/seed-42-refs4-f294_00002_.mp4`.
- SHA-256: `824cc8acb4aeb8040290eae74056475ac194cb83cfe2f78e690f09cb62c05088`.
- Native quality, 1344 x 768, 24 fps, 294 frames, 12.25 seconds, seed 42,
  20 steps, four full-size references, dual-GPU staged execution, EasyCache off.
- All 294 frames decoded; stereo AAC was present and non-silent. Sampled
  frames and user playback established the visual acceptance. Automated audio
  measurements do not establish sound quality or synchronization.

The local trial driver chained two Runner submissions and released Qwen before
H3 rendering; Qwen was restored afterward. This trial-specific resource handoff
is not a packaged public orchestration feature. Source references and the video
remain external media, not repository fixtures.

Verification: 385 H3 workflow tests and 52 public-node tests passed in separate
processes. Combined collection exposes test-double pollution; use the isolated
test groups already declared by the CI contract runner. The live result proves
the targeted H3 chain, not full canonical Titanic execution.

Next refinement: cross-shot identity consistency. The opening uses Picture 1's
blue hair and red facial markings, while later shots drift toward Picture 2's
purple-haired face. A passing prompt audit does not guarantee rendered identity
or exact shot timing. Preserve this accepted baseline when comparing changes.
