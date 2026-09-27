# Named image-region editing

`LF_ExtractImageRegions` takes one RGB/RGBA image, a JSON object containing an
ordered `regions` array, and `canvas_size` (default 512). Each row has a unique
`id`, a `label`, and integer `rect: [x, y, width, height]` in top-origin source
pixels. Rectangles must be nonempty, in bounds and nonoverlapping.

Outputs, in order: `images` (common square IMAGE batch), `image_list` (ordered
individual IMAGEs), `layout` (JSON), and `editor_config` (JSON containing
`image_entries: [{id,label}]`). Crops retain aspect ratio on the common canvas;
padding replicates edge pixels. Labels are metadata, never painted into images.
Layout records the source dimensions/channels, original rectangles and centered
canvas `content_rect` values using schema `lf.image-regions.v1`.

Connect the region images and editor configuration to `LF_ImagesEditingBreakpoint`.
Connect its edited `image_list` and `orig_image_list` to `LF_ComposeImageRegions`,
alongside the exact extraction source image and layout. The editor's named-entry
contract must retain every original entry in its validated original order.
The compositor validates baseline pixels against extraction, rejecting mismatched
source/order or canvas geometry. Unlabelled raw tensors cannot independently
prove the identity of edited images; use the editor's ordered outputs.

Composition transfers RGB **deltas**, not resized replacement crops. Differences
of at most one eight-bit channel step (`1/255`, plus float epsilon) are treated as
PNG transport noise. Deliberate edits that small are also ignored. Content deltas
are resized with bilinear antialiasing and applied to the original source only
where nonzero. Padding edits are discarded. Unchanged regions, uncovered source
pixels and pixels outside the resampling support remain bit-exact; a resized edit
can affect adjacent pixels within its interpolation footprint. The original
alpha channel is always retained, even when the editor changes alpha.

Both nodes use list-mode execution to check exact cardinality. Extraction accepts
exactly one source; composition accepts exactly one original and exactly one
edited/baseline canvas per region, with no broadcasting. RGB/RGBA canvas channels
must agree with the source. Extraction emits float32 canvases; composition retains
source dtype/device. Compose outputs `image` and a single-item `image_list`.
Neither node writes files, emits UI events, or installs an observational widget.
Domain-specific coordinates and any post-composition protection mask belong to
the consuming workflow. Overlapping garment layers are not supported here.

Checks: `python -I scripts/quality/run_pytests.py -q modules/tests/nodes/regions/test_image_regions.py`.
