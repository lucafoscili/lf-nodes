# Video motion capture

`LF_VideoToMotion` extracts a single performer's motion through a separately
installed local [RGB MoCap](https://github.com/toyxyz/toyxyz_RGBMocap) runtime.
`LF_MotionToVideo` renders that motion on a
body chosen independently of the performer. The Runner block **Motion → Video
to Motion Capture** connects them and includes the source in a comparison video.

Set LF Nodes' `RGB_MOCAP_PATH` setting to the installed RGB-Mocap checkout on
Windows before starting ComfyUI. The runtime, its Python environment, ExMR weights and export dependencies
must already be installed. LF Nodes does not install or download them. Missing
setup fails with an actionable error when the node executes; importing LF Nodes
does not initialize the extraction runtime.

The adapter targets RGB MoCap commit
`ef05127a0dbddb3f3ac672a0722dddeae42ea651` and rejects other revisions. It calls
the app's project preparation, actor tracking, `exmr_batch`, BVH export and
headless Blender FBX export under the app's own runtimes. Those internals are
not a supported upstream CLI. GVHMR extraction is not exposed: it requires a
separate reconstruction and hand-refinement path.
`CUDA_DEVICE_ORDER=PCI_BUS_ID` makes `gpu_index` a physical PCI-order CUDA
index. Projects, previews, stage logs and writable runtime caches remain under
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
The optional `include_shape` defaults to false. Its four scalar STRING outputs
are `motion_file`, `bvh_file`, `fbx_file`, and `project_dir`, in that order.
The generic motion file omits performer shape unless explicitly requested;
BVH/FBX use neutral shape coefficients by default. The app project retains its
native inference result; its derived export representation uses the selected
shape policy.
BVH/FBX are runtime exports, not guarantees of compatibility with a particular rig.

`LF_MotionToVideo` accepts `motion_file`, `body` (`female`, `neutral`, or `male`;
default `female`), `betas` (comma-separated render-shape coefficients; default
`0.5,-1.5`), `width` (320), and `height` (560). Optional `source_video` adds a source
comparison; an empty value omits it. Outputs are `video_file` (STRING), `frames`
(IMAGE batch), and `frame_list` (ordered IMAGE list), with list flags
`(False, False, True)`. All render frames have one shared geometry.
It is an output node and saves its rendered video under ComfyUI output.

Both nodes have optional observational `LF_CODE` widgets, support headless
execution, and return final result details through `ui.lf_output`. Their events
are `lf-videotomotion` and `lf-motiontovideo`. Saved output-relative file names
allow Runner history to offer downloads and play the comparison video.
`INPUT_IS_LIST=False` on both nodes: ComfyUI maps file lists to independent
invocations. Each rendered clip has a coherent RGB `[N,H,W,3]` float32 batch in
`[0,1]`; `frame_list` contains its `[1,H,W,3]` frames in playback order.

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
(right, down, forward); world coordinates retain the extraction's world frame.
Optional `betas` has shape `[1,10]` or `[N,10]`; it is omitted by default.
The render node uses the caller's body/shape controls rather than copying these
performer coefficients. Its re-centered orthographic inspection view follows
camera orientation; it does not reconstruct a calibrated source-camera overlay.

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
