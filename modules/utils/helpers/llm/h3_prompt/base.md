# Shared H3 grammar and base modes

## Sections

For t2va, i2va, fl2va, and l2va, return these three sections in this exact order:

1. `integrated_multimodal_description`
2. `overall_soundscape`
3. `non_diegetic_music`

Start `integrated_multimodal_description` with `[Shot 1]`, followed by the visual
style and initial composition. Base modes do not use `<Subject N>` labels.
For ref2va, use the six sections in the reference guide below instead; the shot,
camera, voice, text, and sound rules here still apply.

## Shot and camera grammar

Write `[Shot 1]` exactly, with the space and no opening timestamp. Number later
shots consecutively. Each later shot begins `[Shot N] At MM:SS.mmm, ...`, for
example `[Shot 2] At 00:03.500, the camera cuts to ...`. Cut times must increase
strictly and remain before the requested end time. Do not add a final shot marker
at the video's endpoint. Fit the full action and spoken timeline to the duration.

Each shot establishes framing, visible subjects and positions, surroundings and
light, observable action and state changes, camera behavior, and synchronized
physical sound. Avoid plot-summary prose. Keep one continuous shot for a simple
action. Use a cut to reveal meaningful new information, not just a slight change
of distance. Cross-dissolves, fades, and wipes require the user's request.

Write camera moves naturally in the action: static hold, push in or pull out,
tracking, truck left/right, pan left/right, tilt up/down, pedestal up/down, arc,
zoom, shake, roll, or POV as appropriate. A zoom changes focal length; a push
moves the camera. Add speed and amplitude when meaningful; do not stack labels.

## Fixed frame modes

- t2va builds from text without image alignment.
- i2va begins at `<Picture 1>` in `[Shot 1]`, preserving the opening composition,
  identity, clothing, objects, and spatial relationships, then develops forward.
- fl2va starts at `<Picture 1>` and reaches `<Picture 2>` in the final shot at the
  requested end time. Describe a physically coherent path between them. Use one
  shot unless the user explicitly requests several.
- l2va infers a plausible earlier state and reaches `<Picture 1>` at the end of
  the final shot. Do not treat the image as the opening by default.

Apply only the resolved mode. Within ref2va, explicit user frame roles are
handled by the reference guide, not inferred from the number of attached images.

For i2va, fl2va, and l2va, place an image-alignment sentence before the three
sections. For final-frame alignment, state the actual final shot number and requested end time,
not placeholder letters. For i2va, write: `For the target video, at 0.00 seconds into the target
video, <Picture 1> (from [Shot 1]) is fully referenced.` For fl2va, explain that
Picture 1 from Shot 1 aligns with 0.00 seconds and Picture 2 from the final shot
aligns with the requested end time. For l2va, explain that Picture 1 from the final
shot aligns with the requested end time. Do not add this preamble for t2va or ref2va.

## Voice and visible text

Add dialogue or singing only when requested. Give actual vocal sources stable
IDs `(S1)`, `(S2)`, etc., in order of their first vocal events; silent characters
get no speaker ID. Establish a voice's audible identity at its first event, and
reuse it. Previously established speakers vocalizing together use `(S1,S2)`.
Keep speaker identity, action, and delivery outside the dialogue block. Use
`<d>[Language] Exact spoken content.</d>` for dialogue or lyrics, retaining the
user's exact words and punctuation. Do not put directions inside `<d>`.

For voiceover use `says in an off-screen voiceover` and immediately after every
dialogue block say the corresponding on-screen character's lips remain closed.
If speech crosses a cut, mark both connecting parts with `<scenetrans>` and state
that audio continues across the cut. Use `<cutoff>` when the ending truncates
speech. Put actual visible text in English double quotation marks while keeping
its original language. Do not invent captions or signs.

## Sound sections

`overall_soundscape` is one paragraph of 1–4 English sentences describing ambient
sound, physical action sounds, and non-verbal human sounds across the video.
Keep specific synchronized events in the shot too. Do not repeat dialogue,
singing, or music here. Use `N/A` only for explicitly requested complete silence.

`non_diegetic_music` is 1–3 English sentences about audience-only score: instruments,
tempo, rhythm, and dynamics, not abstract emotional labels. Use `N/A` when no
score is wanted; for a simple action without a music request, prefer `N/A`.
Music audible to characters belongs in the shot description as a diegetic event.
