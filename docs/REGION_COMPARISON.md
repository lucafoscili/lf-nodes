# Region-by-region render comparison

These four project-independent nodes compare registered renders of the same
subject. Core ComfyUI nodes own model loading and SAM inference; Vision Patch
Encode runs a core-loaded vision model. LF Nodes does not download or load weights. No
Workflow Runner catalogue entry is needed: workflows consume the JSON and IMAGE
outputs normally. All four nodes share their final widget payload between live
events and `ui.lf_output`, including persistent generated-preview URLs.

## Text Region Masks (`LF_TextRegionMasks`)

Inputs are `image` (IMAGE), `masks` (MASK batch or list), and `regions` (JSON
array). For example:

```json
[
  {"id": "surface", "prompt": "outer surface", "priority": 0},
  {"id": "detail", "prompt": "small central detail", "priority": 10}
]
```

Use core `CheckpointLoaderSimple` with
`sam3.1_multiplex_fp16.safetensors`. Encode each region's prompt with
`CLIPTextEncode` using that checkpoint's own CLIP output, then run one
`SAM3_Detect` per region with the MODEL, IMAGE and conditioning. Set
`individual_masks=false`: this unions detected objects for each image and
retains an all-zero mask when no objects match. `individual_masks=true`
concatenates object masks and can return zero items, so it cannot maintain this
node's one-mask-per-region contract. SAM v1 weights are not used.

Collect masks in **region-major input order**: every image for region 0, then
every image for region 1, etc. With two images A/B and two regions, this is
`region0-A, region0-B, region1-A, region1-B`. An existing list/batch collector
can do this. Using only Core and LF Nodes, convert each SAM mask with
`MaskToImage`, collect in numeric order with `LF_ImageList`, then use
`ImageToMask` (red channel). Core maps the converter over the list; LF receives
the complete MASK list. All source images and masks must share H,W, and exactly
`image_count * region_count` masks are required.

Masks are binarized at `>= 0.5`. Higher `priority` owns overlapping pixels;
equal priorities favour the earlier table row. Output remains in original
table order, **image-major**: all regions for A, then all regions for B.
Every empty region is retained, marked `empty: true`, and logged with a warning.
Losses are attributed to the final winning region, including triple overlaps.

Outputs are `masks` (MASK `[N*R,H,W]`), `metadata` (JSON), and `mask_list`
(ordered `[1,H,W]` MASK list). Metadata uses `lf.text-region-masks.v1`:

```json
{
  "schema": "lf.text-region-masks.v1",
  "source_size": [640, 480],
  "image_count": 1,
  "ordering": "image-major",
  "regions": [{"id": "surface", "prompt": "outer surface", "priority": 0}],
  "mask_sets": [{"image_index": 0, "regions": [
    {"id": "surface", "area": 1200, "raw_area": 1200,
     "empty": false, "overlap_lost": []}
  ]}]
}
```

An overlap entry is `{"id": "winning-region", "area": 12}`. Empty records
also have a `warning` string. Areas count pixels after thresholding;
`raw_area` is before overlap resolution. Consumers validate dimensions, counts,
ordered IDs, disjoint binary masks, and recorded areas. Metadata is structural
information; it does not establish the identity of the source image.

The default **Compare** widget shows each resolved mask as a coloured fill over
its source image, with the original alongside it. Each entry names the region,
image index and pixel area; empty regions retain their warning. This makes the
region-to-mask assignment visible.

## Region Color Stats (`LF_RegionColorStats`)

Required inputs are `image_a`, `image_b`, `masks`, and `metadata`. A and B must
each contain exactly one RGB/RGBA image with identical H,W; nothing is resized
for measurement. The masks contain either one shared region set or two sets in
A/B order. Metadata can be one two-image document or a list of the two
single-image documents from independently run Text Region Masks nodes. Their
ordered region IDs and source sizes must agree; prompts and priorities may
differ between A and B, and A's table supplies the display metadata. Alpha is
preserved in the preview but excluded from the colour measurements.

Outputs are `stats` (JSON, `lf.region-color-stats.v1`), `overlay` (IMAGE), and
`overlay_list` (one-item IMAGE list). Each `regions` row contains:

- `a` and `b`: pixel `area`, `area_fraction`, `empty`, `lab_mean`, `lab_median`,
  and a `banding` report. Lab arrays are ordered `[L*, a*, b*]`.
- `delta_b_minus_a`: mean and median differences in the same channel order.
- `ciede2000`: `mean`, `p10`, `p50`, `p90`, plus the row's `matched_count` and
  `intersection_count`. Empty or nonoverlapping regions retain their rows with
  null unavailable measurements and warnings, also logged.

The conversion decodes sRGB's piecewise transfer function before multiplying
linear RGB into XYZ, then uses CIE Lab with the D65 2-degree reference white
`[0.95047, 1, 1.08883]`. Means and medians use all pixels in each image's own
region mask. CIEDE2000 uses `kL=kC=kH=1` and matches the **same coordinates in
the A/B mask intersection**. Up to 65,536 samples are selected in row-major
order at indices `floor(i*N/65536)`; smaller intersections use every pixel.
This measures aligned colour changes, not correspondence between moved parts.
Per-image summaries still include the entire respective region.

Banding is an explicitly labelled heuristic. A region needs at least 64 pixels,
32 horizontal/vertical in-mask neighbour pairs, and an L* range of at least 4.
It must pass a smoothness test: neighbour absolute L* differences have p90 at
most 4 and mean at most 2. The occupied L* range is mapped to 64 equal-step bins
by rounding. The reported `empty_bin_fraction` is the share of missing bins.
`suspected` requires at least four occupied bins, empty fraction at least 0.35,
and at least half the neighbour pairs differing by less than 0.05 L*. Flat,
tiny or textured regions report ineligibility and its reason. Sparse palettes
can resemble banding; inspect the preview before interpreting the flag.

The preview shows A left and B right, separated by eight black pixels, with
one-pixel inner region outlines in table order. The default **Compare** widget
keeps that overview and adds one A/B comparison per region, dimming the area
outside it. Labels show the region ID, mean CIEDE2000, A/B Lab means and B-minus-A
mean differences; unavailable measurements say N/A with their warning. Compare
keeps the numbers beside the pixels that produced them. `create_cached_compare_node`
provides the same persistent generated-preview cache used by LF Compare Images;
the final dataset and stats are shared between `safe_send_sync` and
`ui.lf_output`. Omitting the widget does not affect execution.

## Region Feature Similarity (`LF_RegionFeatureSimilarity`)

Load `dino_v3_vit_h.safetensors` with core `CLIPVisionLoader` and encode A and B
separately with [Vision Patch Encode](#vision-patch-encode-lf_visionpatchencode)
(core `CLIPVisionEncode` raises with DINOv3; see below). Connect their
`CLIP_VISION_OUTPUT`s to `features_a` and `features_b`, plus the same `masks` and
`metadata` used above. Set both encoders and this node's `crop` to `none` to
retain the full image, or set all three to `center` for matching centre-crop
geometry.
`model_file` records the filename selected by the workflow. Core's output does
not include model identity, so JSON marks this name as `workflow_input` rather
than claiming to have inspected the model file.

With patch tokens, exactly one encoded full image is required per side. The
node reads `last_hidden_state` and `image_sizes` (`[C,H,W]` per image). DINOv3
ViT-H/16+ has one CLS token followed by four register tokens; all five are
excluded. Remaining row-major patch tokens form the encoded H/16 by W/16 grid.
Both sides must have matching grids and feature dimensions. The inspected
ViT-H configuration uses 1024-square input, hence a 64 by 64 grid.

Masks are area-resampled to that grid. For `center`, they first follow Core's
rounded resize of the shorter side and floor-centred square crop. The weighted
mean feature is `sum(coverage * patch_feature) / sum(coverage)` for each mask,
then the two means are compared by cosine. This retains fractional patch
coverage. Features themselves already contain the encoder's image context;
mask weighting does not remove background context from those tokens.

If **both** outputs have no `last_hidden_state`, the node instead reads
`image_embeds`. The workflow must crop each image region first and encode those
crops in table order: exactly R pooled embeddings for A and R for B, either
as one batched output or a list of single-crop outputs. Existing crop nodes,
including [Extract Image Regions](IMAGE_REGIONS.md), can prepare ordered crops
from workflow-supplied rectangles. Define the crop bounds and any background
masking in the workflow. A full-image pooled embedding is never broadcast over
multiple regions. Malformed patch tensors raise instead of selecting this
pooled-only path; mixed patch/pooled inputs also raise.

The `similarity` JSON uses schema `lf.region-feature-similarity.v1`, names the
model file, and records `method` as `coverage_weighted_patch_mean_cosine` or
`per_region_crop_pooled_cosine`. Region rows contain `id`, `area_a`, `area_b`,
`empty`, and `similarity`. No covered patches produces null plus a logged
warning, including a nonempty region entirely removed by the centre crop. A
zero-norm feature raises because cosine is undefined.

The **Tree** widget lists one searchable record per region, labelled with its
exact cosine score and any warning; expanding it shows the region's `id`,
`area_a`, `area_b`, `similarity` and `empty` flag. Unavailable scores read N/A
with their warning rather than a misleading zero. There are no file output
sockets.

## Vision Patch Encode (`LF_VisionPatchEncode`)

A drop-in for core `CLIPVisionEncode`: the same inputs `clip_vision` (core
`CLIP_VISION` from `CLIPVisionLoader`), `image` and `crop` (`center` | `none`),
and one `CLIP_VISION_OUTPUT`. Use it in place of `CLIPVisionEncode` whenever the
loaded model is DINOv3:

```text
CLIPVisionLoader (dino_v3_vit_h) -> Vision Patch Encode (image A, crop none) -> features_a
                                 -> Vision Patch Encode (image B, crop none) -> features_b
```

Why: in ComfyUI revision `651ca296a`, `comfy/image_encoders/dino3.py` returns
`(sequence_output, None, pooled_output, None)`, while
`comfy/clip_vision.py:ClipVisionModel.encode_image` unconditionally calls
`out[1].to(...)` for `penultimate_hidden_states`, so `CLIPVisionEncode` raises
on that `None` before delivering an output. Core's own DINOv3 consumer
(`comfy_extras/nodes_triposplat.py`) skips `encode_image` and calls the model
directly; this node does the same while keeping `encode_image`'s output.

It never loads a model itself: it asks core to put the given `CLIP_VISION` on
its device (`load_model_gpu`), preprocesses exactly as `encode_image` does
(`clip_preprocess` with the model's `image_size`, `image_mean`, `image_std`, and
crop `center` as true), runs the model with `intermediate_output=-2` (`all` for
models that return every hidden state), and returns core's `Output` on the
intermediate device. `last_hidden_state` is the sequence (for DINOv3: CLS, four
registers, then row-major 16-pixel patches), `image_embeds` the pooled output,
`image_sizes` one `[C,H,W]` per image, and `mm_projected` as core sets it.
`penultimate_hidden_states` is set only when the model returns that tensor, so
DINOv3 outputs omit it. Other CLIP-family models encode as with core.

It fails loud, naming the input: a missing `clip_vision`, a non-`[B,H,W,C]`
`image`, an unknown `crop`, a `siglip2_vision_model` (its preprocessing
differs; use core `CLIPVisionEncode`), or a model output without a sequence
tensor at index 0 or a pooled tensor at index 2.

The default **Compare** widget shows the actual preprocessed image with and
without its patch grid, so the crop and encoded coverage can be inspected.
Labels include source/encoded size, crop, sequence and pooled tensor shapes,
grid dimensions and prefix-token count. The grid uses the loaded model's
declared patch size and the returned sequence length; unavailable geometry is
explicitly labelled with its reason. It is a geometry preview, not a feature
similarity map, and does not claim a verified model filename.

Each node's `ui_widget` input type matches its `NODE_WIDGET_MAP` entry. The
widget manager hydrates the same view from live events and from cached history
(`ui.lf_output`).

## CPU checks

```text
python -I scripts/quality/run_pytests.py -q -p no:cacheprovider modules/tests/nodes/regions/test_text_region_masks.py modules/tests/nodes/analytics/test_region_color_stats.py modules/tests/nodes/analytics/test_region_feature_similarity.py modules/tests/nodes/analytics/test_vision_patch_encode.py modules/tests/test_frontend_widget_registry.py modules/tests/nodes/test_output_metadata_contract.py
python -I scripts/quality/check_node_contracts.py
```

Fixtures are generated images, masks and deterministic tensors only. Feature
tests use an attribute object with the exact fields read from Core's output;
importing Core's output module also imports its GPU stack. The encoder test uses
a tiny model returning DINOv3's tuple shape and stubs Core's `Output`,
`clip_preprocess` and `load_model_gpu`. These tests exercise
LF's numerical and node contracts, not SAM detection or DINO inference.
Real model execution and live widget hydration require a separate runtime test.
