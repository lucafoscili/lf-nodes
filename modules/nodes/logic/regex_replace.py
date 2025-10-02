import re

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.logic import normalize_list_to_value

# region LF_RegexReplace
class LF_RegexReplace:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "input_text": (Input.STRING, {
                    "default": "", 
                    "tooltip": "The text where the regex replacements will occur."
                }),
                "pattern": (Input.STRING, {
                    "default": "", 
                    "tooltip": "The regex pattern to match."
                }),
                "replacement": (Input.STRING, {
                    "default": "", 
                    "tooltip": "The substring to replace the regex matches with."
                }),
            },
            "optional": {
                "flags": (Input.STRING, {
                    "default": "0",
                    "tooltip": "Regex flags to use. Comma-separated list: IGNORECASE, MULTILINE, DOTALL, etc."
                }),
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
        pattern: str = normalize_list_to_value(kwargs.get("pattern"))
        replacement: str = normalize_list_to_value(kwargs.get("replacement"))
        flags_raw: str = normalize_list_to_value(kwargs.get("flags", "0"))

        flag_mapping = {
            "IGNORECASE": re.IGNORECASE,
            "MULTILINE": re.MULTILINE,
            "DOTALL": re.DOTALL,
            "VERBOSE": re.VERBOSE,
        }
        flags = 0
        if flags_raw:
            for flag in flags_raw.split(","):
                flag = flag.strip().upper()
                if flag in flag_mapping:
                    flags |= flag_mapping[flag]

        if not input_text or not pattern:
            log = f"**Error**: Input text or pattern is empty. Replacement cannot proceed."
            PromptServer.instance.send_sync(f"{EVENT_PREFIX}regexreplace", {
                "node": kwargs.get("node_id"),
                "value": log,
            })
            return ("", [])

        replacement_count = 0
        modified_text = input_text
        try:
            modified_text, replacement_count = re.subn(pattern, replacement, input_text, flags=flags)
        except re.error as e:
            log = f"""## Regex Error:

  **Invalid Pattern**: {pattern}
  **Error Message**: {str(e)}
            """
            PromptServer.instance.send_sync(f"{EVENT_PREFIX}regexreplace", {
                "node": kwargs.get("node_id"),
                "value": log,
            })
            return ("", [])

        log = f"""## Result:

  **Original Text**: {input_text}
  **Regex Pattern**: {pattern}
  **Replacement Substring**: {replacement}
  **Regex Flags**: {flags_raw}
  **Resulting Text**: {modified_text}
  **Replacements Made**: {replacement_count}
        """

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}regexreplace", {
            "node": kwargs.get("node_id"),
            "value": log,
        })

        return (modified_text, [modified_text])

# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_RegexReplace": LF_RegexReplace,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_RegexReplace": "Regex replace",
}
# endregion