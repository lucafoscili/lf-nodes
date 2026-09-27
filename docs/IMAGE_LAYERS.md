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
