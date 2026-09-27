# Scale GLB Nodes

`LF_ScaleGLBNodes` accepts exactly one `glb` (`FILE_3D_GLB`), `targets`
(`JSON` object), and `percent` (`FLOAT`, default 100, range 1–200, step 1).
Its single `glb` output is an in-memory `FILE_3D_GLB` for another transform,
stock 3D viewer, or saver. List mode validates one value per input; there is
no broadcasting, custom widget, live event, or history payload.

Example recipe (indices/names must match the input model):

```json
{"nodes":[{"nodeIndex":4,"nodeName":"joint","anchorLocal":[0,-0.1,0]}],"minPercent":65,"maxPercent":115}
```

Selectors identify distinct skin joints with nonoverlapping subtrees.
`nodeName` optionally checks identity; `anchorLocal` defaults to `[0,0,0]`.
The anchor is expressed in the selected joint's local coordinates. Scaling
keeps that point fixed under the joint's original animated translation,
rotation, and scale. A static child carries the uniform factor and anchor
offset; it receives the old children and replaces the joint in `skins.joints`.
Original animation channels, shared samplers, interpolation (including cubic
splines), accessors, inverse bind matrices, scene roots, and embedded binary
resources stay unchanged. Sequential instances can control independent groups.

At 100 percent the original GLB bytes pass through exactly. Null or empty
recipes allow only 100 percent; changing a value before configuring targets
fails with an actionable error. Recipe limits must stay within 1–200 and are
checked even at 100 percent. Inputs use the same self-contained GLB 2 resource
contract as [Apply Texture to GLB](GLB_TEXTURE.md). Source files are never
written; downstream viewers and savers own their outputs.

Implementation lives in `modules/nodes/io/scale_glb_nodes.py` and
`modules/utils/glb_transform.py`. Offline consumers can load the latter by
file path and call `transform_document(document, controls)` without Comfy.
Controls are the same selectors with a required `factor` (0.01–2); it returns
an independent document and a report with `controls`, `anchoredRoots`,
`changedScaleChannels` (always zero), and `clipCount`. The caller retains its
original binary payload. `scale_glb_nodes(blob, targets, percent)` is the
package-level byte facade; `glb_texture.py` owns GLB reading and packing.

CPU check:

```powershell
python -I scripts/quality/run_pytests.py -q modules/tests/nodes/io/test_scale_glb_nodes.py
```
