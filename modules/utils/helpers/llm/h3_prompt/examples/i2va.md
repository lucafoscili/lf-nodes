# Complete I2VA examples

These are hypothetical teaching scenarios, not observations of the current
images. Learn the format, opening-frame alignment, and action coverage. Never
copy their subjects, movements, duration, or sound into another request. Return
only the actual prompt, without example headings or briefs.

### Example 1 — A small movement from an exact opening

Example brief: Four seconds. Picture 1 shows a ginger cat sitting on a windowsill
beside a closed window. Start exactly from that image; the cat flicks its tail
once and turns its ears toward a soft tap outside. Keep the camera still. No
speech or music.

Example output:

For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description:
[Shot 1] Naturalistic live-action style. The opening composition exactly follows <Picture 1>: the same ginger cat sits on the same windowsill beside the closed window, preserving its pose, fur markings, scale, and the existing light and background. The camera holds this framing without moving for four seconds. The tail tip flicks once and returns to rest. A soft tap sounds against the outside of the glass; the cat's ears rotate toward it while its body stays seated in place. No new subject enters, and the window remains closed.

overall_soundscape:
Quiet indoor room tone surrounds one soft tap against the window glass.

non_diegetic_music:
N/A

### Example 2 — Two explicit actions and complete silence

Example brief: Three seconds. Picture 1 shows a clockwork bird with folded wings
on a shelf. Start from this exact picture. It opens its beak once, closes it,
then raises its right wing slightly. No camera movement; completely silent.

Example output:

For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description:
[Shot 1] Detailed stop-motion style. The initial frame matches <Picture 1>, retaining the clockwork bird's folded wings, shelf position, metal finish, surrounding objects, and lighting. In a single three-second locked shot, the beak opens once and closes fully. The bird then lifts its right wing a short distance from its body and holds it there. Its feet stay planted and its left wing remains folded. Framing and background stay unchanged. These motions occur in complete silence, without mechanical clicks or room ambience.

overall_soundscape:
N/A

non_diegetic_music:
N/A
