# H3 prose-only behavior trials — 2026-09-26

This batch tests the prose-only Prompt Maker introduced in `a019117`, not the
earlier compiler-backed trial. No generation instructions or runtime behavior
are changed during the batch. The test driver exposes existing mode, duration,
and reasoning controls for comparison.

## Scope and method

User-authorized local Qwen3.5 4B (`qwen3.5-4b-uncensored-hauhaucs-aggressive`)
through LMS native chat at port 5001. Calls exercise the public load, prompt maker,
and unload nodes with inert Comfy host infrastructure. This is not Comfy graph
execution, Titanic hydration, or video rendering. Reviews are compared with the
actual draft from the same run, not an unrelated independent generation.

Reference A is the original teal-haired elf image, 410 × 512. Reference B is the
1344 × 768 panther frame from the accepted September 7 video. They are supplied
without resizing, through separate sockets. Source paths, ordered dimensions,
idea, settings, successful stage text/timing/token metrics, and lifecycle results
are saved under `output/h3-prose-trials/2026-09-26/<case>/`. These local generated
artifacts are ignored by Git; this report is the committed evidence summary.

Default settings are Auto, six seconds, temperature 0.2, vision reasoning,
review on. Vision reasoning means on for images and off for text-only requests.
The first two request receipts predate the probe's reasoning option and omit that
field; they use this node default. Later receipts record the option explicitly.
The node has no structural output validator: transport success, user-intent
fidelity, creative coherence, and H3 writing-guidance adherence are separate
judgments made by reading the returned prose.

## Cases

- `walking`: “Walking from behind in a medieval town” plus reference A.
- `mixed-references`: “The elf from picture 1 walks beside the panther from
  picture 2 through a snowy forest. Follow them from directly behind without
  cuts. No other people, no dialogue, no music.” References A and B.
- `mixed-references-reasoning-off`: identical mixed-reference request with
  reasoning off; no instruction changes.
- `text-only`: “A red ceramic mug sits on a wooden table while a curl of steam
  rises. One locked-off close-up, no camera movement, no people, no text, no
  speech, and no music. Only quiet room ambience.” No references; review off.
- `exact-dialogue`: “The elf from picture 1 looks into the camera and says
  exactly: Ci vediamo domani. Keep one static medium close-up, no subtitles, no
  other speakers, and no music.” Reference A; eight seconds; reasoning off.
- `fixed-first-frame`: “She stays seated, breathes gently, and blinks once. Keep
  the camera still and preserve the original composition. No dialogue or music.”
  Reference A; explicit i2va; reasoning off.

## Observed results

These are six individual runs, not a statistical evaluation. Successful elapsed
times include model loading and authoring, but exclude unloading. The failed
run's approximate wall time comes from artifact timestamps; its provider-stage
duration and token metrics were not captured.

| Case | Mode / reasoning / review | Elapsed | Observed outcome |
| --- | --- | ---: | --- |
| Walking | ref2va / on / on | 139.70 s | Concise identity binding and requested setting; conflicting camera motion and H3 guidance misses. |
| Mixed references | ref2va / on / on | ~8.5 min | Writer returned no answer text; no review or final prompt. |
| Mixed references, reasoning off | ref2va / off / on | 9.95 s | Correct two subjects and new setting, but wrong three-section base format and conflicting camera motion. |
| Text only | t2va / off / off | 5.52 s | Correct visual action and base format; requested quiet room ambience omitted. |
| Exact dialogue | ref2va / off / on | 9.86 s | Exact Italian words retained; reference structure and dialogue markup missing. |
| Fixed first frame | i2va / off / on | 7.31 s | Seated pose and static composition retained; breathing and blink omitted. |

### Walking

`walking` completed in 139.70 seconds. Writer: 30.78 s; review: 104.72 s. Review
returned the draft exactly unchanged. The intended character and medieval town
are retained, with one subject and no dialogue/music. The prose nevertheless
has conflicting camera directions (tracking backward while following a subject
walking away, yet maintaining distance), an opening Shot 1 timestamp, a summary
without the Subject label, and a description below the suggested word band.
The reviewer used 5,501 reasoning tokens and did not correct these issues.
History matched the final text; the probe-owned model instance was unloaded.

### Mixed references and reasoning comparison

The default writer eventually returned a response with no usable answer text:
`Writer stage failed: The model returned no answer text. Check the model response
and its generation settings before trying again.` LMS inventory remained
responsive during the wait. This was not the request-timeout error and is not
evidence of an API outage. The probe captures stats only after the transport
helper successfully extracts text, so the failed response's token usage and
finish reason are unavailable. Token exhaustion or excessive hidden reasoning
are possible explanations, not established causes.

With the same idea, images, and review setting but reasoning off, writer and
review took 3.20 and 3.23 seconds. Both reported zero reasoning tokens. The draft
and revision depict the intended elf and panther in snow, with no extra person,
dialogue, or music. The two different image sizes were accepted without resizing.

However, the returned prompt uses `integrated_multimodal_description` and the two
sound sections rather than Ref2VA's six sections. There are no Subject/Picture
bindings. Review changes the camera wording to “tracks backward from directly
behind,” leaving the contradiction with following forward-moving subjects. Soft
overcast light with long shadows is also muddled. Faster completion did not
establish better overall authoring quality.

### Text only

The single writer call took 1.69 seconds with zero reasoning tokens. The locked
close-up, red ceramic mug, wooden table, rising steam, and exclusions are all
retained. Base sections and the untimestamped `[Shot 1]` are correct. But
`overall_soundscape: N/A` drops the explicitly requested quiet room ambience;
the instructions reserve N/A there for complete silence. Review was deliberately
off, so this run says nothing about whether review would repair that omission.

### Exact dialogue

Writer and review took 3.00 and 3.08 seconds, with zero reasoning tokens. The
Italian line `Ci vediamo domani.` is preserved, including punctuation. Static
medium close-up, direct gaze, one speaker, and no music are retained. The prose
explicitly excludes subtitles, although “visible text ... heard through audio”
is confusing wording, not proof that subtitles would be generated.

The output again uses the three base sections in Ref2VA, omitting reference
bindings. It also omits `<d>[Italian]...</d>`, `(S1)`, and an audible voice
description. The within-shot speech onset is not the erroneous opening Shot 1
timestamp seen in the walking case. Review returns the draft exactly unchanged.

### Fixed first frame

Writer and review took 2.12 and 1.73 seconds, with zero reasoning tokens. The
seated elf, stained-glass background, and still camera preserve the intended
opening concept. Picture 1 is explicitly aligned with time zero, but that sentence
is inside the description rather than the required preamble before the sections.

More importantly, both requested actions—gentle breathing and one blink—are
entirely missing. The final prose describes a static scene. It also supplies
N/A sound despite no request for complete silence. Review returns this draft
exactly unchanged. These are prompt observations, not a rendered-video verdict.

## Review and integration findings

- Four runs reached review. Three reviews returned exactly unchanged text;
  the fourth made a small camera edit without fixing the main errors.
- The walking reviewer spent 104.72 seconds and 5,501 reasoning tokens without
  changing the draft. Completion is not evidence of meaningful review.
- All five successful runs preserved final text in UI history. Saved prompt files
  match the last model response after Windows CRLF/LF normalization; the node
  does not rewrite the model's prose. Reports honestly state `valid: null` and
  `validation: not_performed`.
- Every run unloaded only its probe-owned model, including the failure. Initial
  and final LMS inventories both had zero loaded instances. Comfy was untouched.
- A second, read-only agent independently reviewed semantic intent and writing
  guidance. This is human-style artifact review, not a new runtime validator.

## Checkpoint judgment and next experiment

**Keep** the simple prose-only path, ordered heterogeneous references, optional
review, and explicit LMS release. These mechanical behaviors worked in this
batch. **Defer** acceptance of consistently usable H3 authoring with this Qwen4B
configuration: every returned prompt has at least one meaningful omission or
instruction miss. The batch does not establish the model's universal ceiling.

The next useful bounded experiment is a shorter, mode-specific system prompt:
one active output-format guide plus a small example and an explicit instruction
to preserve every requested action. The current Ref2VA request includes both
base and reference guides; their coexistence is a candidate explanation for mode
confusion, not a demonstrated cause. Compare the same ideas before changing
defaults. Review instructions should likewise emphasize checking the original
request against the draft, not merely returning plausible prose. No schema,
compiler, or format-repair loop is proposed.

No production instructions or defaults were changed during these tests. The only
code changes expose existing mode, duration, and reasoning settings in the live
probe (`e11a527`, `116fdea`), checked with syntax compilation and CLI help. Comfy
graph execution, frontend hydration, and end-to-end video quality remain untested
for this prose-only revision.
