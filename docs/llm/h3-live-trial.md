# H3 direct-authoring live trial — 2026-09-26

Historical trial: these runs preceded the user's subsequent prose-only
simplification. They exercised the then-present compiler and its timestamp
normalization; the current Prompt Maker has neither. See
[current behavior](h3-prompt-maker.md). Do not treat these results as live
acceptance of the later revision.

Decision: **keep** direct authoring as a candidate; **defer** semantic-quality
acceptance and any claim that review reliably improves the result. No runtime
instructions or validation rules were changed during this trial.

## Boundary

User-authorized local Qwen3.5 4B vision test through LMS native chat on port 5001.
The probe calls the real `LF_LMSLoadModel`, `LF_H3PromptMaker`, and
`LF_LMSUnloadModel` Python implementations. Only Comfy host infrastructure is
stubbed; model residency, image encoding, provider requests, compiler, and final
history payloads are real. This is **not** Comfy graph execution or Titanic
hydration. Comfy stayed stopped; no video was generated.

Model key: `qwen3.5-4b-uncensored-hauhaucs-aggressive`. Node defaults used:
Auto, six seconds, temperature 0.2, vision reasoning, no extra instructions.

Picture 1 was the original teal-haired armored elf reference, 410 × 512.
Picture 2 was a 1344 × 768 frame extracted at five seconds from the previously
accepted September 7 video, containing the panther and a different elf. Inputs
were passed through separate sockets without resizing. These local media are
not new committed fixtures.

## Results

| Case | Provider calls | Elapsed to result | Finding |
| --- | --- | --- | --- |
| “Walking from behind in a medieval town” + one reference, review on | Writer + review | 63.41 s | One concise subject; correct action/setting; description only 107 words after review. |
| Elf from Picture 1 beside panther from Picture 2, same setting/rear view, review on | Writer + review | 81.95 s | Correct separate bindings, no extra elf, mixed geometry accepted; semantic misses survive review. |
| Original short idea + one reference, review off | Writer only | 30.27 s | Valid usable structure with 361-word draft; camera and duration plausibility still need judgment. |

All three returned the six Ref2VA sections, correct Picture counts, a single shot,
no dialogue or music, matching durable history text, and no extra format-repair
call. Existing deterministic compilation removed spurious zero timestamps from
Shot 1 where the model included them. Load/unload completed for each probe-owned
instance; a final inventory confirmed **zero loaded instances**, restoring the
initial residency state. Timings include load and authoring, not final unload.

The reviewed single-reference output uses a short binding:

> `<Subject 1> is the elf warrior with teal hair and silver armor from <Picture 1>.`

This directly improves the old inventory-heavy experience, but does not prove
rendered identity retention or full compliance with authoring guidance.

## Quality observations

- Single-reference review takes 39.30 s and adds only “away” plus source-derived
  stained-glass lighting. The latter is compatible with a medieval town, but
  unnecessary. It leaves the 98-word draft at 107 words versus the 350–500-word
  guideline, omits the Subject label in the summary, and leaves footsteps only
  in the soundscape rather than synchronized within the shot.
- Mixed-reference review takes 51.28 s. Its 463-word description is in range
  (writer: 425), but it still calls the panther `partially_preserved` merely
  because it walks. This contradicts identity-scoped retention. It preserves
  the ambiguous “hands ... at her sides or holding an unseen weapon,” leaves
  look-backs in a rear-view brief, adds visible eyes from the rear angle, and
  duplicates dust-mote detail.
- Review-off reaches the word guideline and uses correct summary/retention
  labels, but overpacks a six-second walk with several locations and includes
  conflicting camera directions and alternatives such as “bridge or archway.”
  It is an independent generation, not proof that disabling review improves
  quality generally.
- Total output tokens were 1,428–3,522 per call, comfortably below 32,768.
  These observed misses are not explained by output-cap exhaustion.

Next evidence question: can a more focused reviewer correct retention semantics,
rear-view camera consistency, and six-second action feasibility while leaving
already-good concise bindings alone? Compare draft and review on these same
references before increasing pipeline complexity or accepting the reviewer.

## Repeating the bounded probe

`scripts/quality/live_h3_prompt.py` requires an explicit model, endpoint, idea,
reference paths, and a fresh output directory. It never starts Comfy or downloads
a model. Obtain permission before using another shared machine/model session.
An already-loaded exact instance is reused and left loaded; only an instance
loaded by the probe is released in its cleanup path.

```powershell
python -I scripts/quality/live_h3_prompt.py --model <downloaded-model-key> --url http://127.0.0.1:5001/api/v1/chat --idea "Walking from behind in a medieval town" --reference <image-path> --output output/h3-prompt-live/<fresh-case-name>
```

Repeat `--reference` for mixed-size inputs; add `--no-review` for opt-out.
Use `--mode i2va` (or another explicit H3 mode) to probe fixed-frame behavior,
and `--duration` to set the requested seconds. Defaults remain Auto and six seconds.
Local trial artifacts live under `output/h3-prompt-live/` in the named directories
`2026-09-26-single-reference`, `2026-09-26-mixed-references`, and
`2026-09-26-review-off`. Each has `request.json`, `stages.json`, `prompt.txt`,
`result.json`, and `lifecycle.json`. Stage captures include response text and
token/timing metrics, not hidden reasoning, credentials, or base64 images.

Probe verification: syntax compilation plus the three successful live runs.
Existing automated node/frontend evidence is recorded in
[H3 Prompt Maker](h3-prompt-maker.md); it was not rerun for documentation-only
results. Actual growing-socket UI, save/reload hydration, and downstream H3 video
quality remain untested for this revision.
