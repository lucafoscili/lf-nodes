# Texture tools

Four CPU nodes for texture work, under **LF Nodes/Texture**. They chain in one
workflow (grade a patch, put back its detail, pad past its edge, repack a normal
map) and each also works alone. None downloads or loads a model; none resizes.
Every node runs in list mode, takes one item of each paired input (mask,
reference, detail source) for all images or exactly one per image, and raises
with the reason on anything else. Each returns its images as a batch and an
authoritative list, plus a JSON receipt or report, and shows before and after in
Compare with a one-line summary per image (the mask, when given, is the third
image). The widget payload is the same live and in `ui.lf_output`, so history
restores it.

Masks are Core MASK tensors at the image's H,W. Where a node selects pixels, a
mask value above 0.5 is in; where it weights them, the value is the weight.

## Edge padding (`LF_EdgePadding`)

Fills every pixel outside `mask` from the pixels inside it, so mipmaps and
bilinear filtering never blend the background into the border of a baked
texture or an atlas island. It is a push-pull mip pyramid: pull sums each level
from the one below, counting only covered pixels; push goes back up from 1×1,
and a pixel whose block holds no covered pixel takes its parent's colour. An
uncovered pixel so takes the average of the nearest covered pixels at the
first scale that reaches any: beside an island it continues the island, far
from every island it is their average.

Covered pixels come back unchanged and the image keeps its dtype. Every
channel, alpha included, is filled the same way, so an island's opacity
continues across its border too. Use the bake's UV coverage as the mask. A
mask with no covered pixel raises: there is nothing to pad from.

The receipt (`lf.edge-padding.v1`) gives, per image, the covered and padded
pixel counts, the covered share and the pyramid's levels.

The Workflow Runner block **Texture Edge Padding** (`texture_edge_padding`)
runs it file in, file out: a PNG texture and a PNG coverage mask (white keeps,
read from the red channel) in, the padded texture and the receipt out. Both
files load and the texture saves through [Load PNG and Save PNG](PNG_STORED_VALUES.md):
8 or 16 bits in and the same depth out, alpha padded as a channel, covered
pixels written back with their stored values and filled pixels rounded to the
nearest level.

## Masked Lab grade (`LF_MaskedLabGrade`)

Gives a region the colour of another: `mask` on `image` is measured and graded,
`reference_mask` on `reference_image` is measured. In CIE Lab (D65, decoded
sRGB) each channel is shifted and scaled,
`(lab - mean) * stretch + reference_mean`, where `stretch` is the reference's
spread over the image's, clamped to `[min_stretch, max_stretch]`. The defaults
(0.25 and 1.0) may narrow a spread but never widen it, so a flat reference does
not amplify noise and a noisy one does not add it. Mask values weight the
measurement; with `apply_to: mask` they also weight the blend, so a soft mask
feathers the grade, and `apply_to: image` grades every pixel by the masked
measurement. `amount` scales the change.

Pixels with zero weight and the alpha channel keep their exact input values.
Colours graded outside the sRGB gamut are clipped and counted. The report
(`lf.masked-lab-grade.v1`) gives the Lab mean and spread of the image region,
the reference region and the graded region, the stretch per channel, and the
changed and clipped pixel counts.

## Detail transfer (`LF_DetailTransfer`)

Adds a detail source's fine lightness detail to an image: the source's L*
minus its box blur over `radius` pixels, added to the image's L* weighted by
`mask` (the whole image when absent). Only L* changes; a, b and alpha do not.

With `mode: fixed`, `strength` is the gain. With `mode: match_reference`, the
gain is chosen so the result's fine-detail spread over the mask matches the
spread of `reference_image` over `reference_mask`. Spreads are measured only
on pixels at least `radius` inside their mask, where the blur sees no pixel
from outside. The gain `k` is the non-negative root of
`k² s² + 2 k c + i² = r²`, with `i`, `s` and `r` the image's, source's and
reference's fine spreads and `c` the image and source's covariance. A source
unrelated to the image (`c = 0`) gives `k = sqrt(r² - i²) / s`; an image
already as detailed as the reference gets `k = 0`. A typical use restores the
detail a grade or a soft bake removed, with the original as both source and
reference.

The report (`lf.detail-transfer.v1`) gives the spreads, the covariance, the
gain and the result's spread, which shows how close the match came (clipping
at the sRGB gamut can keep it short).

## Normal map check and repack (`LF_NormalMapRepack`)

Checks that an image is a tangent-space normal map, renormalises it, converts
its green convention and reports what it found. Values decode as `v * 2 - 1`
(load normal maps as stored data, not colour-managed).

- `layout`: `xyz_rgb` (X red, Y green, Z blue) or `xy_ag` (X alpha, Y green, no
  Z: swizzled two-channel maps).
- `green_in` and `green_out`: `opengl` (Y up the image) or `directx` (Y down);
  green is flipped when they differ.
- `z_mode`: `rebuild_z` keeps X and Y, pulls a pair outside the unit disc back
  onto it and rebuilds `Z = sqrt(1 - X² - Y²)`; a pair outside the disc by more
  than block compression explains (`X² + Y² > 1.05`) is invalid.
  `normalize_xyz` scales the stored vector to unit length and keeps Z's sign;
  a vector facing away (Z below 0) or vanishing (shorter than 0.2) is invalid,
  and a vanishing one becomes (0, 0, 1).
- `max_invalid_share`: above this share of invalid pixels the node raises, as
  the image is not a normal map in that layout (or its layout is wrong).
- `mask`: validate only these pixels (such as UV coverage); every pixel is
  still repacked.

The output is RGB; an `xyz_rgb` map's alpha passes through unchanged. The
report (`lf.normal-map-repack.v1`) gives the checked pixel count and the shares
outside the disc, facing away, vanishing, invalid and renormalised (stored
length off 1 by more than 0.02), and the stored lengths' mean, minimum and
maximum.

## A chained workflow

The canonical E2E workflow's `cpu.texture-tools` case
([Titanic](../scripts/quality/TITANIC_E2E.md#texture-tools)) chains three of
them on Core's stock example image: Masked Lab grade gives a central square
the colour of the image's top band, Detail transfer restores the square's
original fine detail (the original as source and reference), and Edge padding
fills everything outside the square from it. A separate branch repacks a flat,
unnormalised normal map from OpenGL to DirectX green.
