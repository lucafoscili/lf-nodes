# LF DDS Output

`LF_SaveDDS` is a generic, CPU-only DDS output node in
`✨ LF Nodes/IO Operations`. It owns serialization only: upstream nodes own the
pixels, canvas, resizing, cropping, and any consumer-specific export profile.

The public node is consumer-neutral. Callers choose their own export profiles
outside LF Nodes and pass only the resulting image and output-relative filename
prefix into this node.

## Public API

| Input | Type | Default | Contract |
| --- | --- | --- | --- |
| `image` | `IMAGE` | required | RGB or RGBA batch in stable Comfy batch order. |
| `filename_prefix` | `STRING` | `LF_Nodes/DDS` | Safe output-relative path and prefix. `.dds` and a collision counter are added automatically. |
| `pixel_format` | enum | `RGBA32` | `RGB24`, `RGBA32`, `BC1`, or `BC3`. |
| `mip_policy` | enum | `none` | `none` or `full_chain`. |
| `ui_widget` | `LF_TREE` | `{}` | Optional save/verification summary. |

The canonical wire names are deliberately unambiguous:

- `RGB24`: uncompressed RGB, 8 bits per channel, legacy BGR byte layout.
- `RGBA32`: uncompressed RGBA, 8 bits per channel, legacy BGRA byte layout.
- `BC1`: legacy `DXT1` block compression, opaque input only.
- `BC3`: legacy `DXT5` block compression with alpha.

“RGB8” and “RGBA8” are common per-channel descriptions, not additional wire
values. `DXT1` and `DXT5` are legacy aliases for the canonical `BC1` and `BC3`
choices.

The outputs are:

| Output | Type | Contract |
| --- | --- | --- |
| `file_names` | `STRING` list | Ordered output-relative `.dds` filenames. |
| `receipt` | `JSON` | Deterministic `lf.dds.receipt.v1` object. |

The same values are available to Comfy and Workflow Runner consumers at
`ui.lf_output[0].file_names` and `ui.lf_output[0].receipt`. Filenames are kept
outside the deterministic receipt because collision counters depend on the
destination filesystem.

## Pixel and alpha policy

Floating-point tensors are moved to CPU, checked for finite values, clamped to
`[0, 1]`, multiplied by 255, and quantized using round-half-up. Native `uint8`
tensors are preserved. Inputs must have three or four channels; the node does
not infer grayscale or reorder an arbitrary channel layout.

Alpha is never silently discarded:

- `RGB24` and `BC1` accept RGB directly. RGBA is accepted only when every
  normalized alpha byte is 255; otherwise encoding fails with `invalid_alpha`.
- `RGBA32` and `BC3` preserve RGBA alpha. RGB input receives an explicit opaque
  alpha channel.

The receipt records one of `none`, `opaque_required`, `preserve`, or
`opaque_fill` as `alpha_policy`.

## Mip policy

`none` emits the source level only. `full_chain` repeatedly floor-halves each
dimension, clamped to one, until `1×1`. For example, `1920×1080` produces 11
levels.

Mip resampling is pinned to Pillow 12.2.0 `LANCZOS`, with no reducing-gap
optimization. Color channels are filtered in their encoded sRGB byte space.
Pillow filters RGBA through its premultiplied-alpha path before converting back
to straight RGBA. These choices are serialized in every receipt; they are not
hidden quality presets.

## Receipt

The receipt is deterministic for the same normalized pixels, format, mip policy,
and pinned backend. It contains no timestamp or machine path.

```json
{
  "schema": "lf.dds.receipt.v1",
  "files": [
    {
      "index": 0,
      "width": 1920,
      "height": 1080,
      "pixel_format": "BC1",
      "alpha_policy": "none",
      "mip_policy": "full_chain",
      "mip_count": 11,
      "byte_length": 1383240,
      "sha256": "sha256:<64 lowercase hex characters>",
      "encoder": {
        "name": "lf.dds.writer",
        "revision": "1",
        "backend": {
          "name": "Pillow BCN",
          "revision": "12.2.0"
        }
      },
      "normalization": {
        "range": "clamp_0_1",
        "quantization": "round_half_up_u8",
        "mip_filter": "pillow_lanczos",
        "colorspace": "srgb_encoded",
        "alpha_filter": "none",
        "dimension_rule": "floor_half_until_1x1"
      }
    }
  ]
}
```

## Errors

Execution fails closed with a canonical JSON exception string:

```json
{
  "schema": "lf.dds.error.v1",
  "error": {
    "code": "invalid_alpha",
    "message": "The requested DDS format cannot discard non-opaque alpha.",
    "details": {}
  }
}
```

Stable v1 codes are:

- `unsupported_format`: unknown pixel format or mip policy.
- `unsupported_backend`: the pinned codec/resampler revision is unavailable.
- `invalid_alpha`: a non-alpha format received meaningful alpha.
- `invalid_dimensions`: the batch item is not a positive RGB/RGBA image.
- `encode_failure`: normalization, compression, or publication failed.
- `readback_mismatch`: staged or emitted bytes disagree with the requested
  dimensions, format, alpha semantics, mip count, byte length, or SHA-256.

## Writer, backend, and custody

LF Nodes owns the legacy 128-byte DDS header, uncompressed payload writer, mip
layout, strict reader, receipt, and atomic publication. Compressed levels use
Pillow's bundled `DXT1`/`DXT5` encoder only; Pillow's one-level DDS header is not
reused because it does not author a complete mip chain and does not report the
correct compressed linear size for this contract.

Pillow is pinned to `12.2.0` in both Python dependency declarations and is
licensed under MIT-CMU. Its normal cross-platform Python wheels avoid requiring
a downloaded executable. The node checks the runtime revision before any BCn
compression or mip generation, so an environment that overrides the pin fails
closed instead of claiming reproducible bytes.

DirectXTex/`texconv` remains a useful Windows reference implementation, but it
is not an LF runtime dependency: its command-line workflow is platform-oriented
and its WIC-dependent functionality is not identical across operating systems.
See the official [Pillow DDS documentation](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#dds)
and [Microsoft DirectXTex repository](https://github.com/microsoft/DirectXTex).

All batch items are encoded and validated before publication. Each output is
written to a same-directory temporary file, flushed, read back, checksum-checked,
and atomically hard-linked into an unused final path before a second readback.
This create-only publication step cannot replace a path that wins a counter
race. Filesystems without same-directory hard-link support fail closed with
`encode_failure`. A private hard-link custody proof is retained until the whole
batch commits. If any item fails, LF removes a final path only while it still
matches that proof; a path replaced by another actor is preserved. Cleanup
failures never mask the original `lf.dds.error.v1`. Comfy's own output path
resolver enforces output-root containment.

Workflow Runner classifies `.dds` artifacts as `image/vnd-ms.dds` through the
same output-manifest convention used for other saved files.

## Pinned acceptance shapes

The public test suite covers these generic fixtures:

1. `450×150` RGB24, opaque, no mips.
2. `400×320` RGBA32 with alpha, no mips.
3. `29×29` RGBA32 with alpha, no mips.
4. `1920×1080` BC1, opaque, full chain (11 levels).
5. `512×512` BC3 with nontrivial alpha, no mips.

Tests pin the complete DDS SHA-256 for each fixture and reopen the emitted bytes
with Pillow in addition to LF's strict header/payload readback.
