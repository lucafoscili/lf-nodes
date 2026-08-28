# LF Nodes Python node template

Start with the smallest headless transform. Add observational UI only when the
node has final state that is genuinely useful to show or retain.

```python
import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.logic import normalize_input_image, normalize_output_image


class LF_MyNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {"tooltip": "Input image or batch."}),
                "strength": (
                    Input.FLOAT,
                    {
                        "default": 1.0,
                        "min": 0.0,
                        "max": 10.0,
                        "step": 0.1,
                        "tooltip": "Effect strength.",
                    },
                ),
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)
    RETURN_NAMES = ("image", "image_list")
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_TOOLTIPS = (
        "First-signature stack-compatible image batch.",
        "All processed images in source order.",
    )

    def on_exec(self, image, strength):
        images = normalize_input_image(image)
        outputs = []

        for item in images:
            channels = int(item.shape[-1])
            if channels not in (3, 4):
                raise ValueError("LF_MyNode expects RGB or RGBA images.")

            working = item.to(dtype=torch.float32)
            rgb = working[..., :3].mul(float(strength)).clamp(0.0, 1.0)
            output = (
                torch.cat((rgb, working[..., 3:4]), dim=-1)
                if channels == 4
                else rgb
            )
            outputs.append(output.contiguous())

        batch_groups, image_list = normalize_output_image(outputs)
        primary_batch = batch_groups[0]
        return (primary_batch, image_list)


NODE_CLASS_MAPPINGS = {"LF_MyNode": LF_MyNode}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_MyNode": "My node"}
```

This unary transform deliberately uses Core's normal mapped execution. Add
`INPUT_IS_LIST = True` only when one invocation must inspect a true list,
validate exact pairing, or implement singleton broadcasting itself. With list
mode disabled, Core may map inputs before `on_exec` and repeat the final item of
a shorter input; do not rely on seeing the original cardinalities in that mode.

The list socket is the authoritative, complete, ordered result. The batch
socket is a compatibility projection containing only the first encountered
height/width/channel/dtype/device signature. For an interleaved `A, B, A`
result, `image_list` remains `A, B, A`, while `primary_batch` contains the two
stack-compatible `A` items. Every image node must declare one of these policies:

- expose this first-signature projection plus the authoritative list;
- reject heterogeneous output geometry; or
- derive one shared output geometry so every result stacks.

The example transforms RGB only and carries RGBA alpha through unchanged.

## Optional observational UI

Add UI only when there is actual final observational state. Make the widget
optional, keep execution headless, and mirror the final live payload into
history:

```python
from ...utils.helpers.comfy import safe_send_sync

# INPUT_TYPES additions:
"optional": {"ui_widget": (Input.LF_PROGRESSBAR, {"default": {}})},
"hidden": {"node_id": "UNIQUE_ID"},

# on_exec finalization:
final_payload = {"value": f"Processed {len(image_list)} image(s)."}
safe_send_sync("mynode", final_payload, node_id)
return {
    "ui": {"lf_output": [final_payload]},
    "result": (primary_batch, image_list),
}
```

No event or `ui.lf_output` is needed when the node has no useful final UI
state. Temporary progress assets stay transactional; replace them with
generated-preview URLs before putting the final payload into durable history.

## Registration and compatibility

Every public class also needs a `NodeName` enum member and exactly one
`NODE_WIDGET_MAP` entry. Use `[]` when native Comfy UI is sufficient.

Before changing a published node, snapshot and assert its existing:

- input types, keys, defaults, and required/optional placement;
- output indices, types, names, and every `OUTPUT_IS_LIST` flag;
- consumed `ui.lf_output` and receipt keys.

The standalone checker validates the current schema internally; it cannot tell
whether a current schema drifted from a prior release. Keep an exact regression
assertion for any published contract you touch. Append missing outputs rather
than reordering or prepending them.

## Variations and verification

- Two collections must implement and test exact pairing, singleton broadcast,
  or explicit mismatch failure.
- Use MASK/LATENT normalizers rather than treating those structures as IMAGE.
- Use `normalize_conditioning`; never scalar-unwrap CONDITIONING.
- A viewer/saver that must run unconnected may opt into `OUTPUT_NODE = True`.
- Use generated-preview helpers for final preview URLs. Temporary assets are
  only for an active editing/progress transaction.
- Test interleaved heterogeneous resolutions to prove authoritative list order
  and the declared batch policy.

Before handoff, run the standalone contract checker, focused behavior tests,
`modules/tests/test_frontend_widget_registry.py`,
`modules/tests/nodes/test_output_metadata_contract.py`, frontend build checks
where relevant, and the repository Titanic experience gate described in
`docs/ARCHITECTURE.md`.
