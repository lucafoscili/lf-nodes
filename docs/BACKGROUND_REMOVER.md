# Background Remover / RMBG-2.0

`LF_BackgroundRemover` supports BRIA RMBG-2.0 directly. Choose **RMBG-2.0**
in the existing model dropdown; VNCCS is not required. The default remains
`u2net`, and the six previous rembg choices keep their existing behavior.

## Setup and use

Install LF's Python requirements in ComfyUI's environment and restart ComfyUI.
The RMBG backend uses torch, torchvision, transformers, safetensors, timm and
kornia. The [main installation guide](../README.md#installation) names the
environment-specific dependency commands.

Place a trusted, compatible RMBG-2.0 package at this path under ComfyUI:

```text
models/RMBG/RMBG-2.0/
  config.json
  birefnet.py
  BiRefNet_config.py
  model.safetensors
```

The same four-file package used by the earlier LF sprite cards is reusable;
no duplicate weights are needed. `config.json` must set `bb_pretrained` to
`false`, so construction does not request a separate pretrained backbone.
Missing files produce an error naming the expected path and files. LF does
not download this package or silently fall back to a different model.

The two Python files are **executable model code**. Install them only from a
trusted source alongside compatible weights; local-only loading is not a
code sandbox. LF does not bundle or modify them. Model access and licensing
remain separate from LF: BRIA describes the self-hosted weights as available
for non-commercial use, with commercial use requiring its agreement. See the
[BRIA model card and access conditions](https://huggingface.co/briaai/RMBG-2.0).

Connect an image or an ordered image list. For differently sized references,
use **Images to list** (`LF_ImageList`) rather than forcing them into one
resized batch. Leave `transparent_background` enabled for RGBA cutouts, or
disable it and choose `background_color` for an RGB composite.

## Outputs and lifetime

All seven existing output indices remain unchanged:

| Index | Output | Meaning |
| --- | --- | --- |
| 0 | `image` | Primary same-size image batch, transparent or color-filled |
| 1 | `image_list` | Every processed image, preserving order and dimensions |
| 2 | `cutout_list` | Every RGBA cutout in order |
| 3 | `mask` | Primary same-size foreground-alpha mask batch |
| 4 | `mask_list` | Every foreground-alpha mask in order |
| 5 | `stats` | Per-image dimensions, coverage and bounds |
| 6 | `cutout` | Primary same-size RGBA cutout batch |

For a mixed-size list, batch sockets contain the first size group; list
sockets are authoritative for the complete sequence. Masks use 1 for
foreground and 0 for background. RMBG-2.0 intersects inferred coverage with
existing source alpha, so transparent source pixels cannot become opaque.
The compare widget and durable history previews work with either backend.

RMBG-2.0 loads once per node invocation, processes frames one at a time in
float32, and releases its model after the whole list, including on failure.
It asks Comfy's model manager for device/headroom rather than retaining an
unmanaged global model. It does not unload unrelated third-party models.
Internal inference is 1024×1024; masks return to the original dimensions.
Alpha is inferred independently per frame, not temporally stabilized.

The adapter constructs the package's native BiRefNet class and strictly loads
the local safetensors weights. This avoids the observed Transformers 5
`from_pretrained` failure caused by the package's architecture config lacking
`model_type`; no model monkeypatch or Transformers downgrade is installed.

## Runner and existing workflows

Sprite Loop Cut, cardinal-turnaround assembly, and H3 anchored-sprite/character
turnaround paths now use this public LF node. Their alpha verification,
registration and saver chains are unchanged. Runner still checks the four
model files and shows **Setup required** if they are missing.

Previously downloaded graphs and custom project workflows are not rewritten.
Those still containing `VNCCS_RMBG2` may continue using VNCCS; its
[historical decoder repair](compatibility/vnccs-rmbg.md) remains available.
Do not substitute nodes by socket number blindly: VNCCS and LF do not share
the same mask-output index.

## Implementation and checks

- Public contract: `modules/nodes/filters/background_remover.py`.
- Shared filtering/compositing: `modules/utils/filters/background_remover.py`.
- Local model lifetime: `modules/utils/helpers/detection/rmbg2.py`.
- Focused tests: `tests/test_background_remover_contract.py`,
  `modules/tests/nodes/filters/test_background_remover_rmbg2.py`, and
  `modules/tests/utils/helpers/test_rmbg2.py`.
- Run `python -I scripts/quality/run_ci_contracts.py` from LF's root for the
  CPU publication gate, using ComfyUI's Python. It does not load models or
  certify GPU/matte quality. Live comparison and Runner evidence are recorded
  in [release readiness](RELEASE_READINESS.md#direct-rmbg-20--2026-10-02).
