import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import ANY, BASE64_PNG_PREFIX, EVENT_PREFIX, FUNCTION, Input, NOTIFY_COMBO
from ...utils.helpers.conversion import tensor_to_base64
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value

# region LF_Notify
class LF_Notify:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "any": (ANY, {
                    "tooltip": "Pass-through data."
                }),
                "title": (Input.STRING, {
                    "default": "ComfyUI - LF Nodes", 
                    "tooltip": "The title displayed by the notification."
                }),
                "message": (Input.STRING, {
                    "default": "Your ComfyUI workflow sent you a notification!", 
                    "multiline": True, 
                    "tooltip": "The message displayed by the notification."
                }),
                "on_click_action": (NOTIFY_COMBO, {
                    "tooltip": "Action triggered when clicking on the notification."
                }),
                "silent": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "The notifications will be displayed without triggering a sound effect."
                }),
            },
            "optional": {
                "image": (Input.IMAGE, {
                    "tooltip": "Image displayed in the notification."
                }),
                "tag": (Input.STRING, {
                    "default": '', "tooltip": "Used to group notifications (old ones with the same tag will be replaced)."
                }),
            },
            "hidden": { 
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_NODE = True
    RETURN_NAMES = ("any", "any_list")
    RETURN_TYPES = (ANY, ANY)

    def on_exec(self, **kwargs: dict):
        any: str = normalize_list_to_value(kwargs.get("any"))
        on_click_action: str = normalize_list_to_value(kwargs.get("on_click_action"))
        title: str = normalize_list_to_value(kwargs.get("title"))
        message: str = normalize_list_to_value(kwargs.get("message"))
        silent: str = normalize_list_to_value(kwargs.get("silent"))
        tag: str = normalize_list_to_value(kwargs.get("tag"))
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image", []))

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}notify", {
            "node": kwargs.get("node_id"), 
            "title": title,
            "message": message,
            "action": on_click_action.lower(),
            "image": f"{BASE64_PNG_PREFIX}{tensor_to_base64(image[0])}" if image else None,
            "silent": silent,
            "tag": tag
        })

        return (any, any)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_Notify": LF_Notify,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_Notify": "Notify",
}
# endregion