# Ref2VA grammar

Return these six sections in this exact order:

1. `subject_definitions`
2. `summary`
3. `retention_analysis`
4. `detailed_description`
5. `overall_soundscape`
6. `non_diegetic_music`

## subject_definitions

Use one short line per independently tracked item. Number `<Subject 1>`,
`<Subject 2>`, etc. consecutively and keep their meanings stable everywhere.
A subject is reusable visible content, not a source file. Define the desired
character, object, environment, style, or action only if independently reused.
An image used only as a source is cited inside that subject's definition; do not
give it a separate definition or retention line. A concise identity binding is
sufficient; avoid exhaustive image descriptions or repeated appearance inventories.
Every attached Picture must be represented as a source or an explicitly assigned
anchor. Several Pictures may supply the same subject; say briefly what each adds.

Use a standalone `<Picture N>` definition only when the user explicitly assigns
the whole image a first-frame, last-frame, keyframe, edited-keyframe, storyboard,
or composition role. Name the applicable shot and role. Distinguish a concrete
frame target from visual planning guidance. Image presence alone grants neither.
Never invent `<Video N>` or `<Audio N>`: this request supplies only images.

## summary

Use one short English paragraph with a square-bracketed task prefix. Use
`[reference generation]` for reusable subjects or guidance, `[keyframe completion]`
for concrete target frames alone, or `[reference generation + keyframe completion]`
when both apply. Storyboard/composition guidance alone is reference generation,
not keyframe completion. Follow the prefix with a plain sentence describing the
target action and main relationships using already-defined labels.

## retention_analysis

Use one line for every independently defined Subject or Picture, with its actual
shot scope, one exact marker, and a brief concrete reason:

`<Subject 1> (all shots): fully_preserved - The character's identity remains consistent.`

For limited scope use `(appears in [Shot 1], [Shot 3])`; frame scope can be
`([Shot 1] first frame)`. Valid markers are `fully_preserved`,
`partially_preserved`, `attribute_transfer`, and `weak_reference`.
They mean respectively preserving the defined role, changing part of that role,
transferring attributes to a different identifiable target, and retaining only
broad similarity. Judge fidelity within the defined reference role: new actions,
backgrounds, or camera movement do not reduce fidelity to a character's identity.
Do not create retention lines for Pictures merely cited as a subject's source.
Do not put speaker IDs in this section.

## detailed_description

Begin with one or two English sentences establishing the visual style before
`[Shot 1]`. This is the difference from the base-mode style opening. Write
normally 350–500 English words for this section, targeting 400–450 words.
Count only this section, not definitions,
summary, retention, or sound sections. A single shot still needs grounded detail:
develop action phases, spatial relationships, framing, light, texture, material
movement, camera continuity, and synchronized sound without adding plot beats,
repeating the same constraint, or inflating subject definitions.

Use `[Shot 1]` without a timestamp and later `[Shot N] At MM:SS.mmm, ...` as in
the shared guide. At each important subject's first appearance, use its label
with a concise visible identity cue, current position, and action. Reuse the
label later instead of redefining it. Insert actual frame anchors where they take
effect, such as `the shot begins from <Picture 1>` or `the shot ends on <Picture 2>`;
do not describe a source-only Picture as a frame anchor.

When a referenced subject speaks, retain both identities: `<Subject N> (Sx)`.
The subject number and speaker number serve different purposes; assign the latter
by first vocal event. All shared voice and sound rules still apply. Complete
requested dialogue belongs here inside `<d>`, never repeated in the sound sections.
