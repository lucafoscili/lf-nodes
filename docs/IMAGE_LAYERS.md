# Image layer editing

`LF_LoadImageLayers` and `LF_ComposeImageLayers` provide a generic, reversible
bridge between source-owned RGBA components and the existing LF image editor.
They do not write source files, emit UI events, or retain image pixels in JSON.

## Load Image Layers

The loader accepts exactly one manifest and one scalar `canvas_size` (default
`512`):

```json
{
  "root": "D:/project/components",
  "layers": [
    {
      "id": "sleeve",
      "label": "Sleeve",
      "file": "arms/sleeve.png",
      "rect": [0, 0, 256, 128]
    }
  ]
}
```

- `file` is always relative to the explicit `root`. Resolution through `..` or
  a symlink may not escape that root.
- IDs are non-empty and unique. Array order is composition order; overlapping
  target rectangles are intentional and later entries render above earlier
  entries.
- Sources are decoded once as native-size RGBA. Their aspect ratio must match
  the target rectangle, so no layer is stretched.
- Optional SHA-256 checks the source file before it is admitted.

Outputs are a common square RGBA batch, the authoritative ordered canvas list,
`lf.image-layers.v1` layout metadata, stable `image_entries` editor config, and
the authoritative ordered native RGBA source list. Connect the common batch
and editor config to one `LF_ImagesEditingBreakpoint` session. Keep the native
source list connected directly to the composer; it prevents resized canvases
from becoming source authority.

## Compose Image Layers

The composer requires exactly one base image plus exact-cardinality `edited`,
`original_layers`, and `source_layers` collections. It never broadcasts.
Connect the breakpoint's `image_list` and `orig_image_list` to the first two
collections and the loader's native source list to the third.

RGB edits above the 8-bit PNG transport tolerance are projected only from each
canvas's aspect-fit content rectangle back to its native component. Padding
edits and editor alpha changes are ignored; original alpha is retained. The
restored native layers are resized with Pillow LANCZOS and alpha-composited in
manifest order, matching the established no-edit composition path byte for
byte for 8-bit sources.

Outputs are the RGBA atlas, its single-item list companion, and the restored
native RGBA layer list. The latter is available for an explicit downstream
saver; neither node writes it automatically.

## Combined base and cut-mask editing

Optional loader inputs `base` (one RGB/RGBA image) and `base_regions` must be
supplied together. The region document uses the existing image-region format:
`{"regions":[{"id":"panel","label":"Panel","rect":[0,0,256,128]}]}`.
Regions must not overlap. Their RGBA canvases precede the layer canvases in the
same batch, with IDs `base:<id>`. Base composition reuses Image Regions' local
RGB delta restoration; original base alpha is retained.

Set optional `include_masks` to true to place a cut-mask canvas after each
fabric canvas. Expanded entries use `layer:<id>` and `mask:<id>` IDs. The
complete order is base regions, fabric 1, cut mask 1, fabric 2, cut mask 2, and
so on. Connect the entire edited and original editor lists to the composer;
`source_layers` still contains only the native fabric sources. All editor
canvases share the same square RGBA geometry. With both additions omitted,
the original loader output and layout are unchanged.

Cut masks start with white RGB and the source alpha, so original coverage is
visible over the editor checkerboard. White retains/restores original source
alpha, black cuts it, and gray multiplies it for partial coverage. Colored mask
edits use their mean RGB value. Mask edits cannot expand source coverage;
editor alpha and square padding edits are ignored. Unchanged masks preserve
the native layer exactly, including soft source alpha. Cuts reveal lower
layers and then the edited base.

The composer's optional `base_mask` permits base RGB edits where white and
preserves the original base where black (gray permits partial edits). Supply
exactly one mask with the original base dimensions. It does not change base
alpha or fabric coverage. Expanded layouts validate base identity, entry order,
source identity, original canvases, and exact editor/source cardinalities.
Neither node adds events, history state, or output sockets.
