# Apply Texture to GLB

For pose-preserving joint scaling, see [Scale GLB Nodes](GLB_SCALE.md).

`LF_ApplyTextureToGLB` connects an edited IMAGE to an existing animated GLB
without converting the scene into Comfy's flattened MESH representation.

Inputs: `source_glb` (absolute read-only path or Comfy input filename), `texture`
(one RGB/RGBA IMAGE), `material_index` (integer, default 0). Output: `glb`
(`FILE_3D_GLB`), directly connectable to **Preview 3D (Advanced)**.

The operation keeps the original binary prefix, scene, geometry, UVs, skin,
animations, material settings and existing image/texture records. It appends a
PNG and a cloned texture binding and changes only the selected material's
base-color texture index. Other materials sharing the old image are unchanged.
Sampler and texture-coordinate/transform settings are retained. Supplied alpha
is preserved, but the source material's OPAQUE/MASK/BLEND mode still applies.

This first version requires one self-contained GLB 2 with embedded images and
one image input. Multi-image batches/lists, external resources and texture-source
extensions on the selected texture fail explicitly. It does not unwrap UVs,
project brush strokes, modify source files, or install assets anywhere.

Implementation: `modules/nodes/io/apply_texture_to_glb.py` and
`modules/utils/glb_texture.py`. The returned file exists in memory; downstream
viewers/savers own their outputs. There is no custom widget, live event or final
`ui.lf_output` state on the transform itself. Source hashing invalidates Core's
cache when GLB content changes.

CPU check:

```powershell
python -I scripts/quality/run_pytests.py -q modules/tests/nodes/io/test_apply_texture_to_glb.py
```
