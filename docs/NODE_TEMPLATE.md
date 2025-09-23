# LF Nodes – Python Node Template

A ready-to-copy skeleton that follows lf-nodes conventions: normalized inputs, single-image loop, async UI logging, and explicit node mappings. It also demonstrates output normalization by returning both a batch and a list, giving downstream nodes flexibility.

## Template

```python
import torch

from server import PromptServer

from . import CATEGORY  # adjust import path based on the folder
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.logic import (
    normalize_input_image,
    normalize_output_image,
    normalize_list_to_value,
)

# region My_NodeName
class My_NodeName:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {"tooltip": "Batch or single image."}),
                "strength": (Input.FLOAT, {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.1}),
            },
            "optional": {
                "note": (Input.STRING, {"default": ""}),
                "ui_widget": (Input.LF_PROGRESSBAR, {"default": {}}),
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION

    # Return both a batch (first) and a list (second) to maximize downstream flexibility
    RETURN_TYPES = ("IMAGE", "IMAGE")
    RETURN_NAMES = ("image", "image_list")
    OUTPUT_IS_LIST = (False, True)

    def on_exec(self, **kwargs):
        node_id = kwargs.get("node_id")
        strength = float(normalize_list_to_value(kwargs.get("strength", 1.0)))
        note = str(normalize_list_to_value(kwargs.get("note", "")) or "")

        # 1) Normalize inputs
        images = normalize_input_image(kwargs.get("image"))  # list of [1,H,W,C]

        # 2) Async UI logging (optional)
        PromptServer.instance.send_sync(
            f"{EVENT_PREFIX}mynodename",
            {"node": node_id, "value": f"## My_NodeName\n\n- Starting with strength = {strength}"},
        )

        # 3) Per-image processing loop
        outputs = []
        for idx, img in enumerate(images):
            # Example operation: scale pixel intensities (no-op if strength = 1.0)
            out = img.to(dtype=torch.float32) * strength
            out = out.clamp(0.0, 1.0).contiguous()
            outputs.append(out)

            # Optional: progress update
            PromptServer.instance.send_sync(
                f"{EVENT_PREFIX}mynodename",
                {"node": node_id, "value": f"- Processed image {idx+1}/{len(images)}"},
            )

        # 4) Normalize outputs back to batch/list
        batch_list, image_list = normalize_output_image(outputs)

        # 5) Final message
        if note:
            PromptServer.instance.send_sync(
                f"{EVENT_PREFIX}mynodename",
                {"node": node_id, "value": f"- Note: {note}"},
            )

        # Return batch (first) and list (second)
        return (batch_list[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "My_NodeName": My_NodeName,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "My_NodeName": "My Node Name",
}
# endregion
```

## Conventions this template follows

- Always normalize inputs at the top (batch → list of [1,H,W,C]).
- Process images one-at-a-time in a for-loop for deterministic behavior.
- Use `send_sync` to emit UI updates while executing.
- Normalize outputs to both a batch and a list using `normalize_output_image`, and return both: `(batch, list)`.
- Keep `CATEGORY`, `FUNCTION`, and explicit `NODE_*_MAPPINGS` at the bottom for discovery.

## Variations

- If your node uses CONDITIONING, import `normalize_conditioning` and apply it to those inputs.
- For mask-heavy nodes, consider creating/using a `normalize_mask` helper to standardize shapes/types.
- If the node is side-effect only (pure UI), you can keep `RETURN_TYPES = ()` and return `()`.

## Mixed outputs variant (batch + list + names + count)

Sometimes you’ll want to return additional metadata (e.g., file names) and a count alongside images. Here’s a minimal signature that mirrors the pattern used by `LF_BlurImages`:

```python
class My_NodeName_Advanced:
    CATEGORY = CATEGORY
    FUNCTION = FUNCTION

    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING", "INT")
    RETURN_NAMES = ("image", "image_list", "file_name", "count")
    OUTPUT_IS_LIST = (False, True, True, False)

    def on_exec(self, **kwargs):
        # ... normalize inputs and process images into `outputs` and `names` ...
        batch_list, image_list = normalize_output_image(outputs)
        count = len(image_list)
        return (batch_list[0], image_list, names, count)
```
