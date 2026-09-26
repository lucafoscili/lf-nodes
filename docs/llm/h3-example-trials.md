# H3 worked-example comparison — 2026-09-26

Follow-up to [the prose-only trials](h3-prose-trials.md), using implementation
`c6b7f25`. The user approved complete examples, potentially more than one, and a
clearer request-specific brief. This batch changes those instructions together;
it cannot isolate the contribution of examples from request framing.

## Change and test boundary

- Nine original complete demonstrations: three Ref2VA, two T2VA, two I2VA, one
  FL2VA, one L2VA. Only the resolved mode's demonstrations reach a request.
- Ref2VA examples cover one identity in a new setting, two separately referenced
  subjects, and exact Spanish dialogue. Example scenes deliberately differ from
  the evaluation scenes; explicit directions prohibit copying their content.
- Repeat the active mode, section order, duration, and image mapping beside the
  unchanged user idea. Review receives the unchanged draft and asks explicitly
  for coverage of each requested action, camera constraint, spoken line, and sound.
- No new provider stages, output parser, schema, compiler, validator, or repair
  loop. Public sockets, defaults, list/image ordering, events, and history stay
  unchanged. The existing review flag still selects one or two provider calls.

The same local Qwen3.5 4B, images, exact ideas, durations, and review/reasoning
settings are reused from the six earlier request receipts. The old two default
reasoning receipts omit that field; the new ones explicitly record `vision`,
which resolves to on for those image requests. Temperature remains 0.2; no seed
is fixed, so these are individual before/after observations, not a statistical
test or a claim of deterministic causal improvement.

The public Python nodes call LMS with inert Comfy host infrastructure. Comfy
itself is not started or restarted; no video is rendered. Local artifacts live
under `output/h3-example-trials/2026-09-26/<case>/` (Git-ignored). Times include
loading and authoring but exclude unloading. No instruction edits occur between
the reruns.

## Results

All six reruns returned prose, versus five returns and one empty-answer failure
in the earlier batch. This is completion evidence, not six quality passes.

| Case | Before | With examples and explicit brief | Observed difference |
| --- | ---: | ---: | --- |
| Mixed references, reasoning off | 9.95 s | 25.86 s | Six sections and concise bindings restored; rear-follow/backward-camera contradiction remains. |
| Text only, review off | 5.52 s | 5.80 s | Quiet ambience restored, but unrequested steam hiss and table creak added. |
| Exact Italian dialogue, reasoning off | 9.86 s | 18.41 s | Six sections, Subject/Speaker IDs, language and dialogue tags restored. |
| Fixed first frame, reasoning off | 7.31 s | 8.70 s | Correct preamble, breathing, and blink restored; unjustified silent soundscape remains. |
| Walking, reasoning on | 139.70 s | 116.20 s | Forward camera travel and Subject-labeled summary restored; odd physical/lighting details remain. |
| Mixed references, reasoning on | ~8.5 min, no answer | 105.42 s | Returns six sections, both bindings, side-by-side movement and correct forward tracking; unresolved prop/visibility details remain. |

### What improved and what did not

The reasoning-off mixed-reference prompt identifies the elf from Picture 1 and panther from
Picture 2 in short definitions and keeps both in a new snowy forest. It does not
copy the examples' cyclist, yellow jacket, bridge, gardener, orchard, dog, or
Spanish line. But it still specifies backward camera travel while following
forward-moving subjects from behind. It introduces an unresolved alternative
about hands resting at the sides or holding a staff, and places the panther a
metre ahead rather than simply beside the elf. Review is byte-for-byte unchanged.

The text-only prompt keeps the red mug, steam, still camera, and exclusions. It
now mentions quiet room ambience rather than N/A, but adds a steam hiss and a
creaking table despite the request for only room ambience. This is partial
improvement, not complete constraint adherence. Review is off in both versions.

The dialogue prompt preserves `Ci vediamo domani.` with `<Subject 1> (S1)` and
`<d>[Italian] ... </d>` syntax, with one static shot and no added speaker or music.
It does not copy the Spanish teaching line. However, it calls the composition a
medium close-up while framing from below the chin to mid-thighs, contradicting
the visible face/eye contact. Its soundscape invokes humming light and creaking
stone. The detailed description is below the suggested word band. Review again
returns the draft exactly unchanged.

The fixed-frame prompt puts the time-zero Picture 1 alignment before the three
sections. Both requested actions now appear in the writer's draft: one blink and
a gentle breath. The subject stays seated and the camera still. Review makes only
small stylistic edits, not those substantive repairs. N/A ambience persists even
though the request excludes only dialogue and music, not all physical sound.

The walking prompt now explicitly moves the camera forward at the character's
pace, keeps a concise identity binding, and uses the Subject label in the
summary. Its 483-word detailed description falls inside the guideline band. The
opening marker is no longer immediately timestamped, though the body redundantly
mentions time zero. The medieval setting remains creative rather than being
locked to the reference background. There is no example-specific scenario
copying. Less credible details persist: vibrations rippling across stone paving,
soft daylight alongside sharp shadows, and an ambiguous final following distance.
Indistinct distant people are added, but the user did not forbid background people
in this case. Review is identical despite 3,245 reasoning tokens and 58.66 seconds.

The previously empty-answer mixed-reference case now completes with reasoning
on: writer 44.05 seconds, reviewer 57.75. It uses both reference identities, the
requested snowy setting and exclusions, side-by-side movement, and explicitly
forward camera travel. The reviewer strengthens identity cues and removes the
literal phrase that the panther's eyes are visible "from behind," but still
claims visible eyes while the camera is locked behind the subjects. The optional
staff wording remains unresolved and invokes preservation of the original pose,
although the reference subject is seated and this request requires walking.
Snow, frozen-ground claw clicks, long diffuse shadows, and whiteout visibility
also merit creative cleanup. This run shows
successful completion, not a proven explanation of the previous empty response.

Of five reviews, three are exactly unchanged; fixed-frame review only polishes
wording, and mixed-reference reasoning-on review makes limited edits without
resolving its main remaining inconsistencies. No authoring result copies the
examples' specific scenes or dialogue.

## Verification and checkpoint judgment

The 72 focused node/instruction tests pass, including example selection and
completeness, preservation of original idea/draft, public compatibility, and
verbatim model output/history. The static check passes for 148 public mappings.
Example-completeness assertions run in tests on checked-in authoring assets;
they are not runtime gates on generated prose. An independent read-only agent
found no public-contract drift and reviewed the live outputs separately.

**Keep** the examples and explicit brief: this batch shows an incremental
improvement in formatting, action coverage, and completion. **Defer** complete
authoring-quality acceptance. Review remains weak at correcting scene
inconsistencies; a future bounded experiment should focus on that weakness,
without reintroducing a compiler or changing model defaults on this evidence.

For all six cases, original ideas, image paths/shapes, durations, modes, reasoning,
and review settings match the old receipts. Final files match the last model
answer after Windows newline normalization, and history matches in every case.
All six probe-owned model instances were unloaded. Initial and final LMS
inventories both contain zero loaded instances. No unrelated model was unloaded.

The skill-directed compatibility checks preserve existing sockets, ordered
heterogeneous images, one/two provider calls, and durable UI/history behavior.
No frontend code changed. Live Comfy/Titanic hydration and video generation were
not exercised, and FL2VA/L2VA examples have asset tests but no live model trial
in this batch. Nothing here is a full end-to-end video acceptance claim.
