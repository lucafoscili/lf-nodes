# Next release

Changes since [LF Nodes 5.1.0](https://github.com/lucafoscili/lf-nodes/blob/v5.1.0/docs/releases/5.1.0.md).

## New nodes

Six readers measure how a rendered frame looks rather than eyeballing it. Each
returns a JSON report with its own schema and shows its result in the Compare
widget (Tone profile in a tree).

- **Grade split** (`lf.grade-split.v1`) fits a 3D colour lookup from a before
  frame to an after frame of the same view and reports how much of the change
  the lookup (a global grade) explains, how much a local tone operator (the
  lookup keyed by the neighbourhood's brightness too) adds, and what is left by
  spatial band; with the grade's tone curve and its saturation by luma band.
- **Luma ratio map** (`lf.luma-ratio-map.v1`) pictures after over before as a
  signed map and reports the median ratio per luma band, inside and outside an
  optional mask and over the whole frame.
- **Tone profile** (`lf.tone-profile.v1`) reads luma, saturation and percentiles
  per region of a Text region masks set, and against a reference profile gives
  each region's ratio. Its UI shows the profile as a tree; the report itself
  travels on its socket.
- **Region reads** (`lf.region-reads.v1`) evaluates lines such as
  `face / ring(face) - near(hair)`: regions combined with `&`, `|` and `-`, a
  ring, edge, inside or near band around a region or a union of them
  (`ring(face|hair)`), and `facing<v` or `facing>v`
  on an optional facing (N·V) map.
- **Face zones** (`lf.face-zones.v1`) places under-eye, cheek, fold, forehead
  and chin zones from 68 landmarks, sized by the eyes' distance (never less
  than about half the face's height, so a turned face keeps its zones; the far
  side's under-eye and cheek go once its eye hides behind the nose), as a
  region mask set (InsightFace packs on ONNX Runtime, like Face align).
- **Intrinsic layers** (`lf.intrinsic-layers.v1`) splits an image into albedo,
  diffuse shading and residual with Careaga and Aksoy's pipeline. Neither the
  `intrinsic` package nor its weights ship with LF Nodes, and their authors
  provide them for academic use only. Its loader fails loud instead of waiting
  on torch hub's console trust prompt.

**Patch probe** (`lf.patch-probe.v1`) learns what tells two kinds of image
apart from their encoded patches (Vision Patch Encode with DINOv3) and paints
where new frames read as each. Teaching images carry a label, 0 or 1, and a
group (a scene, or a pair of shots of it); the probe is a class-balanced
logistic regression on standardized patch tokens, and each group is held out
once while the others teach, so its report says whether the probe reads a
scene it never saw (accuracy, AUC, log loss and each image's mean). A frame
naming a teaching group is read by the probe that held that group out; any
other is read by the probe every group taught, with the range of the held-out
probes' readings beside it. A frame's score is its mean probability and its
patches' mean logit, which keeps counting where the probabilities saturate
(a held-out pair's order is its logits'; the AUC is per patch). Each fit says
whether it converged, and the first frame's title names any that stopped at
its cap. Each frame comes back painted (orange label 1, blue label 0, by how
sure the probe is), as a probability mask, and as its patch grid of logits in
the report.

Three speech nodes, each loading its model from a pinned Hugging Face revision
for its run and freeing the GPU after it, and each returning a JSON receipt of
what ran (model, revision, settings, seconds of audio, load and run time):

- **Voice clone speech** (`lf.voice_clone_speech.receipt.v1`) says a text in
  the voice of a reference recording and its transcript, or in a voice designed
  from words alone (`male, elderly, american accent`), with OmniVoice. Its text
  reads OmniVoice's inline tags (`[laughter]`, `[sigh]`) and pronunciations
  (`[B EY1 S]`), and its decoding's time-step shift is a setting (`t_shift`,
  OmniVoice's 0.1 by default; higher can read a line livelier).
- **Voice convert** (`lf.voice_convert.receipt.v1`) keeps a recording's words
  and timing and gives them the voice of a target recording (its first ten
  seconds), with Chatterbox's converter; its output carries Chatterbox's
  implicit watermark.
- **Speech match** (`lf.speech_match.receipt.v1`) measures a recording against
  a reference voice (WavLM's speaker embedding, their cosine) and against its
  expected text (Whisper's transcript and its word error rate), and reads how it
  moves: its prosody in the receipt (pitch median, range and spread in
  semitones, loudness range in decibels and voiced share, over the frames where
  a voice sounds; librosa's probabilistic YIN).

Each run lets go of its model before the GPU's cache is emptied: the
collector runs, and method caches that would keep the model (transformers'
Higgs audio tokenizer caches one, which kept each OmniVoice run's decoder) are
cleared. None of their packages or weights ship with LF Nodes; Speech match
needs librosa for its prosody, and says so before any model loads where it is
missing. OmniVoice's weights are
licensed CC BY-NC (non-commercial, by their training data's terms) and WavLM's CC BY-SA 3.0; Chatterbox
and Whisper are MIT. Only clone a voice you have the right to use.

Three inspection nodes answer the questions a contact sheet raises (what changed
between two renders, how a region reads across frames, how a set of numbers is
spread) with a picture and the numbers behind it.

- **Image diff** (`lf.image-diff.v1`) compares registered images pair by pair,
  or one reference against many: a heat picture of where they differ over the
  reference in grey, every pair on one scale, and per pair the difference in
  8-bit levels (mean, median, p95, p99, max), the share and box of the pixels
  changed past a threshold, and the shift in mean luma; over an optional pixel
  box and mask. Images of different sizes, an empty box or a region without
  pixels are refused by name. Its result shows in the Compare widget.
- **Region measure** (`lf.region-measure.v1`) reads named pixel boxes across
  frames, optionally narrowed by a mask: per frame and box, Tone profile's
  numbers (luma mean, median, deciles, shade, sheen, detail, saturation) with
  the RGB mean and median, and the frames with their boxes outlined.
- **Plot chart** (`lf.plot-chart.v1`) draws any JSON report as a line, scatter,
  histogram or bar chart: each series is picked by a dotted path (`*` for every
  item, so `frames.*.regions.face.mean` follows a region across frames), and
  each series' count, range, mean, median and 5th and 95th percentiles come back
  beside the picture.

## Changed nodes

- **Image grid** takes optional `captions` (appended last): one line per image,
  burnt into its cell's upper-left corner, so a contact sheet names each frame.
  The layout receipt records each item's caption.
- **Video to motion** runs RGB MoCap's Motion Correction after the engine,
  on by default (`motion_correction`, appended last): one floor found from the
  feet's contacts, each standing foot held on it, so a foot on tiptoe keeps its
  toes on the floor instead of sinking below the other foot's plane. The motion
  JSON, BVH and FBX carry the corrected motion, and the result details report
  the floor and any warning of the app's. Off returns the engine's motion as
  before. Video to Motion Capture and Pose Shoot expose it with the other
  capture controls. See [Video motion capture](https://github.com/lucafoscili/lf-nodes/blob/main/docs/MOTION.md#motion-correction).
- **Video to motion** grounds the feet before that correction, on by default
  (`ground_feet`, `push_in` and `planted_seconds`, appended last): the camera's
  drift along the floor is taken out, a camera that pushes in no longer walks
  the performer toward it, a standing foot on its heel is set flat, and chosen
  seconds hold both feet planted. The correction then runs again on the
  prepared capture, and the result details list each step. Video to Motion
  Capture exposes all three; Pose Shoot the first two. See
  [Grounding the feet](https://github.com/lucafoscili/lf-nodes/blob/main/docs/MOTION.md#grounding-the-feet).

## Workflow Runner

- **Pose Shoot** (Orchestras, MiniMax H3) shoots poses written one per line,
  or pose photos turned into words by Caption image (Vision), with one
  generated performer (Krea 2, once per shoot) or a supplied synthetic one.
  Each pose's take is written by the H3 Prompt Maker, a fixed full-length
  camera paragraph is appended after writing and review, H3 renders the clip
  (8 seconds at 9:16 by default), and Video to Motion Capture returns the
  motion file, BVH, FBX and the mannequin comparison MP4. Photos never reach
  H3. See [the Pose Shoot guide](https://github.com/lucafoscili/lf-nodes/blob/main/docs/llm/h3-pose-shoot.md).
- Orchestras can expand their stages from the submitted inputs
  (`stages_factory`, up to 64 stages), append fixed text to a text binding
  (`text_suffix`), keep chosen stages visible in history
  (`expose_in_history`), and a failed stage's error now carries the child's
  reason.
- Caption image (Vision) gains caption instructions, a model choice and
  load-and-release on LM Studio's native `/api/v1/chat` endpoint. Video to
  Motion Capture exposes the engine, include shape and stage timeout.

## Release checks

Pose Shoot adds no node: every class it runs is already in the canonical E2E
workflow, and its test checks that inventory. Titanic executes ComfyUI graphs,
not Runner orchestras, so **no Titanic case runs Pose Shoot**; the motion pair
stays disabled inventory, as in 5.1.0. Its offline tests stub only the model
boundary.

The six readers and Patch probe have offline tests on synthetic inputs and a
Compare registration, but **no Titanic case and no place in the canonical E2E
workflow yet**: they are not ready to release until they have both.

Image diff, Region measure and Plot chart have offline tests on synthetic
images and a widget registration (Compare, Masonry and Masonry), but **no
Titanic case and no place in the canonical E2E workflow yet**: they are not
ready to release until they have both.

The three speech nodes have offline tests on synthetic tones with their models
stubbed, but **no widget, no Titanic case and no place in the canonical E2E
workflow yet**: they are not ready to release until they have all three.
