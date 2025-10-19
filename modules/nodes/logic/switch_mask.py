import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.logic import normalize_list_to_value

# region LF_SwitchMask
class LF_SwitchMask:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "on_true": (Input.MASK, {
                    "lazy": True,
                    "tooltip": "Value to return if the boolean condition is true."
                }),
                "on_false": (Input.MASK, {
                    "lazy": True,
                    "tooltip": "Value to return if the boolean condition is false."
                }),
                "boolean": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Boolean condition to switch between 'on_true' and 'on_false' values."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_PROGRESSBAR, {
                    "default": {}
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_TOOLTIPS = (
        "Final output mask.",
        "List of all output masks (if any)."
    )
    RETURN_NAMES = ("mask", "mask_list")
    RETURN_TYPES = (Input.MASK, Input.MASK)

    def check_lazy_status(self, **kwargs: dict):
        switch_value = kwargs["boolean"]
        if switch_value:
            return ["on_true"]
        else:
            return ["on_false"]

    def on_exec(self, **kwargs: dict):
        boolean: bool = normalize_list_to_value(kwargs.get("boolean"))
        on_false: torch.Tensor = kwargs.get("on_false")
        on_true: torch.Tensor = kwargs.get("on_true")

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}switchmask", {
            "node": kwargs.get("node_id"),
            "bool": boolean,
        })

        value = on_true if boolean else on_false

        return (value, [value])
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SwitchMask": LF_SwitchMask,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SwitchMask": "Switch Mask",
}
# endregion
