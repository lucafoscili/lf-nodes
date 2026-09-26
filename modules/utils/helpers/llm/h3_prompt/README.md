# H3 authoring instructions

`build_authoring_system(mode, duration_seconds, reference_image_count,
review=False, instructions="")` assembles checked-in Markdown into one system
message. Supply the original user idea and original ordered images separately
to both writer and reviewer. Resolve `auto` in the caller: no images means
`t2va`; images mean `ref2va`. Explicit frame modes retain their fixed meanings.

- `SKILL.md`: creative brief and direct-output contract.
- `base.md`: shared shot, voice, sound grammar and base-mode sections.
- `reference.md`: Ref2VA's six sections, concise bindings, and role-specific retention.
- `__init__.py`: deterministic local builder and runtime constraints.
- `modules/tests/utils/helpers/llm/test_h3_prompt_skill.py`: focused coverage.

Writer and reviewer return final H3 labeled sections. The existing compiler
validates them and adds official alignment preambles for base frame modes. This
bundle performs no provider calls or runtime downloads. It introduces no public
node schema and does not independently prove live model quality.

## Sources and deliberate local choices

Reviewed 2026-09-26 against MiniMax's official
[H3 prompt-writing skill](https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills/h3-prompt-writing),
[base guide](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/base-en.txt),
and [reference guide](https://github.com/MiniMax-AI/MiniMax-H3/blob/main/skills/h3-prompt-writing/references/ref-en.txt).
The Markdown is a compact, independently written adaptation of the relevant
image-only grammar, not a runtime router to unavailable external files.

The official generation guideline normally calls for 350–500 English words in
`detailed_description`; this bundle targets 400–450 without rejecting otherwise
valid section text solely for its word count. Short bindings and identity preservation leave unspecified
scene, action, and camera choices open. A simple action defaults to one continuous
shot, no unsolicited speech, and no audience-only music. Review returns a whole
usable prompt rather than an audit object. These are local authoring defaults.

Run the focused tests through the repository's CPU-safe harness:

```powershell
python -I scripts/quality/run_pytests.py -q modules/tests/utils/helpers/llm/test_h3_prompt_skill.py
```
