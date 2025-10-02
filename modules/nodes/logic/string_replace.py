from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.logic import normalize_list_to_value

# region LF_StringReplace
class LF_StringReplace:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "input_text": (Input.STRING, {
                    "default": "", 
                    "tooltip": "The text where replacements will occur."
                }),
                "target": (Input.STRING, {
                    "default": "", 
                    "tooltip": "The substring to be replaced."
                }),
                "replacement": (Input.STRING, {
                    "default": "", 
                    "tooltip": "The substring to replace the target with."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_CODE, {
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
    RETURN_NAMES = ("string", "string_list")
    RETURN_TYPES = (Input.STRING, Input.STRING)

    def on_exec(self, **kwargs: dict):
        input_text: str = normalize_list_to_value(kwargs.get("input_text"))
        target: str = normalize_list_to_value(kwargs.get("target"))
        replacement: str = normalize_list_to_value(kwargs.get("replacement"))

        if not input_text or not target:
            log = f"**Error**: Input text or target is empty. Replacement cannot proceed."
            PromptServer.instance.send_sync(f"{EVENT_PREFIX}stringreplace", {
                "node": kwargs.get("node_id"),
                "value": log,
            })
            return ("", [])

        replacement_count = input_text.count(target)
        modified_text = input_text.replace(target, replacement)

        log = f"""## Result:

  **Original Text**: {input_text}
  **Target Substring**: {target}
  **Replacement Substring**: {replacement}
  **Resulting Text**: {modified_text}
  **Replacements Made**: {replacement_count}
        """

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}stringreplace", {
            "node": kwargs.get("node_id"),
            "value": log,
        })

        return (modified_text, [modified_text])
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_StringReplace": LF_StringReplace,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_StringReplace": "String replace",
}
# endregion