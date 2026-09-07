# Reviewed H3 prompt maker: accepted checkpoint

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
