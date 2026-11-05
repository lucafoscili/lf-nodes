# Video motion capture

`LF_VideoToMotion` extracts a single performer's motion through a separately
installed local [RGB MoCap](https://github.com/toyxyz/toyxyz_RGBMocap) runtime.
`LF_MotionToVideo` renders that motion on a
body chosen independently of the performer. The Runner block **Motion → Video
to Motion Capture** connects them and includes the source in a comparison video.

Set the `RGB_MOCAP_PATH` environment variable to the installed RGB-Mocap checkout on
Windows before starting ComfyUI. The runtime, its Python environment, ExMR weights and export dependencies
must already be installed. LF Nodes does not install or download them. Missing
setup fails with an actionable error when the node executes; importing LF Nodes
does not initialize the extraction runtime.

The adapter targets RGB MoCap commit
`ef05127a0dbddb3f3ac672a0722dddeae42ea651` and rejects other revisions. It calls
the app's project preparation, actor tracking, `exmr_batch`, Motion Correction
(its `correct` stage, on by default), BVH export and headless Blender FBX export
under the app's own runtimes. Those internals are
not a supported upstream CLI. GVHMR extraction is not exposed: it requires a
separate reconstruction and hand-refinement path.
Git must be on ComfyUI's `PATH` to verify that revision; install Git or add its
executable directory to `PATH` before starting ComfyUI. The capture adapter owns
the environment lookup; there is no separate Workflow Runner setting.
`CUDA_DEVICE_ORDER=PCI_BUS_ID` makes `gpu_index` a physical PCI-order CUDA
index. Before creating a project, the adapter enumerates devices in the ExMR
runtime with that ordering and checks the requested index. Missing CUDA or an
unavailable index reports the index and discovered devices. This does not import
PyTorch into the ComfyUI host for device discovery.
Projects, previews, stage logs and writable runtime caches remain under
ComfyUI output's `LF_Nodes/Motion/` folder. Model aliases are hardlinked when possible and copied on different
drives, so a capture may need several GB of output space. The adapter does not
change the application's tracked files.

Rendering requires the separately licensed [SMPL-X](https://smpl-x.is.tue.mpg.de/)
v1.1 model files in ComfyUI's
`models/smplx` directory, registered through `folder_paths`:
`SMPLX_FEMALE.npz`, `SMPLX_NEUTRAL.npz` or `SMPLX_MALE.npz` for the selected body.
No model bytes are included in this repository. Install the rendering dependencies
in the ComfyUI Python environment as described by the project's dependency list.
The added `smplx>=0.1.28` package evaluates the licensed body's blend shapes and
skinning; it contains no model weights. The renderer uses existing NumPy,
PyTorch, Pillow and PyAV dependencies for CPU skinning, smooth shaded depth
rasterization and H.264 encoding. It runs without a display, Blender or an RGB
MoCap installation. Width and height are even pixel counts per view; the MP4
and IMAGE batch are two views wide, or three with the source comparison.

## Node contracts

`LF_VideoToMotion` accepts `video_path` (one local video), `engine` (`ExMR`),
`static_camera` (default true), `smoothing` (true), and `gpu_index` (0).
The optional `include_shape` defaults to false. `stage_timeout_seconds` defaults
to 0 (automatic); a positive value sets the timeout of each worker stage in seconds.
The optional `motion_correction` defaults to true: the app's Motion Correction runs
after the engine and every output carries its result ([below](#motion-correction)).
False returns the engine's motion as it came.
With it, `ground_feet` (default true), `push_in` (`auto`, `yes` or `no`; default
`auto`) and `planted_seconds` (default empty) prepare the capture before the
correction solves it ([grounding the feet](#grounding-the-feet)).
Automatic bounds use the source clip duration `D` in seconds:

| Stage | Timeout in seconds |
| --- | --- |
| prepare | `max(120, 4 * D)` |
| track | `max(300, 30 * D)` |
| capture | `max(600, 120 * D)` |
| correct | `max(300, 20 * D)` |
| export | `max(300, 20 * D)` |

Each bound covers the whole stage, including startup. On timeout the worker's
process tree is stopped, and the error names the stage, elapsed time, bound and
log. There is no retry.

Its four scalar STRING outputs
are `motion_file`, `bvh_file`, `fbx_file`, and `project_dir`, in that order.
The generic motion file omits performer shape unless explicitly requested;
BVH/FBX use neutral shape coefficients by default. The app project retains its
native inference result; its derived export representation uses the selected
shape policy.
BVH/FBX are runtime exports, not guarantees of compatibility with a particular rig.

### Motion Correction

ExMR places the body without a floor: a foot can sink below the other foot's
plane, and a foot on tiptoe reads as standing on a lower level instead of lifted.
The app's Motion Correction finds one flat floor from the feet's contacts, holds
each foot on it while the engine marks it standing (heel or forefoot, whichever
carries the weight, so tiptoe toes stay down with the heel up), and solves the
hips, knees, ankles and root translation to keep them there. The node runs it
through the app's own `correct` worker stage with the app's own defaults
(`mocap/correction_settings.py::correction_options`: automatic floor, preset
`normal`, flat mode, foot lock on, hand lock off) and names the corrected result
in the project's pipeline, so the BVH and FBX are the app's corrected export.

The correction solves on the body the exports describe. With `include_shape`
off, the project's derived export representation is made neutral first, so the
neutral shape's feet are grounded; with it on, the estimated performer shape's.
In the motion file, `world` carries the corrected legs and root translation with
ExMR's root orientation and native flat-hand fingers. `camera` carries the same
corrected motion through ExMR's per-frame camera: its in-camera root
orientation, its in-camera translation moved by the correction's root shift
rotated into the camera, and the corrected, globally smoothed pose (without the
correction, `camera` is ExMR's unsmoothed in-camera prediction). The result
details add `correction`: the result name, the floor height in metres (world
Y), the app's warning text (empty when it has none), its options, method and
which shape it solved on. A warning names a contact it could not resolve;
inspect those frames.

### Grounding the feet

A fixed-camera capture reads camera motion as body motion: when the camera
pushes in, the performer walks toward it with her feet sliding and her body
leaning over them. A foot out of frame is often guessed standing on its heel
with its toes up, and the correction keeps each ankle's world rotation, so the
toes stay up. With `ground_feet`, the bridge runs the correction once to learn
which feet stand when, prepares the capture, and runs the correction again on
the prepared capture, so the motion file, BVH and FBX carry it. The steps live
in `modules/utils/helpers/motion/motion_grounding.py`, which runs in the app's
runtime beside the bridge and is importable by any caller that holds the app:

- **The camera's drift.** The material under the most planted standing foot
  only moves because the camera did. Its step between frames (heel and toe
  blended by the app's support weights), carried across frames where no foot
  stands and smoothed over 0.15 s, is taken out of the root.
- **A push-in.** When that drift moves along the camera's horizontal view by
  more than 15 cm (`push_in` `auto`; `yes` or `no` overrides the reading), the
  pelvis is kept over the middle of both soles along the view, at its offset
  from the opening half second, turned with the body's heading; across the view
  the capture stands. The legs swing at the hips so the feet stay where they
  were.
- **Flat heels.** A standing foot on its heel with its toes 0.5 to 6 cm up is
  pitched about its ankle until its toes meet the floor, easing in and out over
  0.1 s; a foot on its toes stays as it is.
- **Planted seconds.** Spans such as `1.65-2.3, 4-5` hold both feet on the floor
  whatever the capture's foot confidence says, for a clip where the feet are
  planted but the engine lost them.

The correction then solves the prepared capture on the export body (neutral,
or the performer's shape with `include_shape`). The result details' `correction`
adds `grounded`: one line per step and the push-in reading in metres
(`null` when `ground_feet` is off). The module's `seat_on_floor`, which raises a
pelvis whose seat sinks below the floor after the solve, is not run by the node:
it would rewrite the app's corrected result after the app has recorded it.

`LF_MotionToVideo` accepts `motion_file`, `body` (`female`, `neutral`, or `male`;
default `female`), `betas` (comma-separated render-shape coefficients; default
`0.5,-1.5`), `width` (320), and `height` (560). Optional `source_video` adds a source
comparison; an empty value omits it. Outputs are `video_file` (STRING), `frames`
(IMAGE batch), and `frame_list` (ordered IMAGE list), with list flags
`(False, False, True)`. All render frames have one shared geometry.
It is an output node and saves its rendered video under ComfyUI output.
Optional `image_frame_limit` defaults to 32: the IMAGE outputs evenly sample at
most that many frames across the clip, including the first and last (a limit of
1 returns the first). Set it to 0 to request every frame. The MP4 always contains
every frame; changing this limit does not change its pixels or timing.
The selected uint8 frames plus their float32 IMAGE batch must fit a 256 MiB
budget (`selected_frames * height * total_width * 3 * 5` bytes). An oversized
request fails before body evaluation or encoding and reports its size and budget;
reduce the limit or resolution. The list contains views of the batch, not copies.
Skinning uses bounded batches and repeats evaluation to establish the same fixed
camera framing without retaining every mesh. This trades additional CPU skinning
for lower memory use. The motion's JSON parameters are still loaded in memory.

Both nodes have optional observational `LF_CODE` widgets, support headless
execution, and return final result details through `ui.lf_output`. Their events
are `lf-videotomotion` and `lf-motiontovideo`. Saved output-relative file names
allow Runner history to offer downloads and play the comparison video.
`INPUT_IS_LIST=False` on both nodes: ComfyUI maps file lists to independent
invocations. Each selected IMAGE batch is coherent RGB `[N,H,W,3]` float32 in
`[0,1]`; `frame_list` contains its `[1,H,W,3]` frames in playback order.
The render result details retain `frames` as the total MP4 frame count and add
`image_frames`, zero-based `frame_indices`, and `fps` so consumers can identify
each returned image's time.

## Motion interchange

`lf.motion.v1` is a JSON parameter interchange, independent of the source
runtime's project layout. Its required top-level keys are `schema`, `fps`,
`joint_names`, `camera`, and `world`. `fps` is positive and finite.
`joint_names` declares the SMPL-X root, 21 body joints and 15 joints per hand in
the order defined by `modules/utils/helpers/motion/format.py`.

Both coordinate dictionaries contain frame arrays of identical length:

| Field | Shape | Meaning |
| --- | --- | --- |
| `global_orient` | `[N,3]` | Root axis-angle, radians |
| `transl` | `[N,3]` | Root translation, metres |
| `body_pose` | `[N,63]` | 21 body axis-angles, radians |
| `left_hand_pose` | `[N,45]` | 15 left-hand axis-angles, radians |
| `right_hand_pose` | `[N,45]` | 15 right-hand axis-angles, radians |

Hands use the flat-hand rest without PCA. Camera coordinates use OpenCV axes
(+X right, +Y down, +Z forward). Both spaces use metres and right-handed rotations.
World coordinates retain ExMR's gravity-aligned reconstruction frame:

- +Y is up; +Z is the forward basis axis inherited from the first gravity-view
  prediction, with +X completing the right-handed basis (`X cross Y = Z`). The
  estimated gravity-view heading need not exactly match the camera's viewing
  direction or the performer's facing direction.
- Root translation is integrated from zero in the first frame, then corrected
  for static joints, optional fixed-camera drift and temporal smoothing. Those
  corrections can move the first frame away from X=Z=0.
- A single vertical shift places the lowest mesh vertex over the whole clip at
  Y=0. This is an inferred floor, not a measured scene origin or a guarantee that
  every frame touches the floor. `transl` is the SMPL-X translation parameter;
  the posed pelvis is offset by the shape-dependent rest pelvis.
- RGB MoCap calls ExMR with `normalize_world=False` and `snap_to_ground=False`.
  It does not rotate the first pose to face +Z or re-center its pelvis at X=Z=0.
- With Motion Correction the floor is the correction's, reported as
  `correction.floor`; standing feet rest on it rather than on the lowest vertex.

These conventions come from the pinned application's `mocap/exmr_backend.py`
and `third_party/ExMR/exmr/model/{exmr,global_traj}.py`, especially
`rollout_global_params`, `put_on_ground` and the disabled `face_forward` step.
Optional `betas` has shape `[1,10]` or `[N,10]`; it is omitted by default.
The render node uses the caller's body/shape controls rather than copying these
performer coefficients. Its re-centered orthographic inspection view follows
camera orientation; it does not reconstruct a calibrated source-camera overlay.

### Working frames and source time

RGB MoCap's `mocap/video.py::prepare` resamples the source to a **30 fps**
`input.mp4` with FFmpeg's `fps=30` filter. ExMR predicts one pose per working
frame; it does not predict at the original video's rate. The project's `fps=30`
is passed to ExMR and saved as `native["fps"]` by `mocap/exmr_backend.py`.
The LF writer copies that native rate, so captured `lf.motion.v1` files and
their rendered MP4s record **30 fps**, even for a 24, 29.97 or 60 fps source.
Other producers may supply any positive finite `lf.motion.v1` rate; rendering
preserves that file's rate.

For zero-based motion frame `i`, the source-relative time is `i / motion.fps`
seconds. This adapter processes the full clip from its start. A constant-rate
source's fractional frame position is `i * source_fps / motion.fps`; select or
interpolate by that time, rather than pairing source and motion frame numbers.
For variable-rate video use presentation timestamps relative to the first
source frame. The comparison renderer samples the latest source frame at or
before each target time. Resampling can repeat or drop source frames; the
motion file does not imply a one-to-one source-frame mapping.

## Inspection and limits

Upload one video in Runner, choose the render body and shape, then run. The
downloadable graph keeps a portable `video.mp4` placeholder to replace in ComfyUI.
Inspect body direction, hand poses, foot sliding and temporal stability against
the source. Single-view reconstruction can infer hidden joints incorrectly;
exporting files and passing schema checks do not establish motion quality.
Keep the source and extracted motion when comparing alternative render bodies.

Offline tests cover graph wiring, controls and upload cardinality. Live capture,
visual acceptance and Titanic inventory/hydration are separate checks; the
catalogue entry and unit tests do not imply they have been performed.
