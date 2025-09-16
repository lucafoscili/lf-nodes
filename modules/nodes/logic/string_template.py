import random
import re

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers import normalize_json_input, normalize_list_to_value

# region LF_StringTemplate
class LF_StringTemplate:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "template": (Input.STRING, {
                    "default": "",
                    "multiline": True,
                    "tooltip": "The string template with placeholders matching the keys of the input dictionaries (e.g.: {name}, {style}, etc.)."
                }),
                "replacements": (Input.JSON, {
                    "default": [{}],
                    "tooltip": "A list of dictionaries for placeholders. Each dictionary is used for a separate result."
                }),
            },
            "optional": {
                "seed": (Input.INTEGER, {
                    "default": 42, 
                    "max": INT_MAX, 
                    "tooltip": "Seed to control the randomness of the shuffling."
                }),
                "randomize": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "If true, randomly pick one dictionary from the replacements list."
                }),
                "use_regex_placeholders": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Enable regex placeholders like {\\w+} for advanced templates."
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
    RETURN_TYPES = ("STRING", "STRING")

    def on_exec(self, **kwargs: dict):
        template: str = normalize_list_to_value(kwargs.get("template"))
        replacements_list: list[dict] | dict = normalize_json_input(kwargs.get("replacements", [{}]))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize", False))
        seed: int = normalize_list_to_value(kwargs.get("seed", 42))
        use_regex: bool = normalize_list_to_value(kwargs.get("use_regex_placeholders", False))

        if not isinstance(replacements_list, list) or not all(isinstance(d, dict) for d in replacements_list):
            log = "**Error**: Replacements must be a list of dictionaries."
            PromptServer.instance.send_sync(f"{EVENT_PREFIX}stringtemplate", {
                "node": kwargs.get("node_id"),
                "value": log,
            })
            return ("", [])

        unmatched_keys = []
        filled_templates = []

        try:
            if randomize:
                random.seed(seed)
                selected_dict = random.choice(replacements_list)
                filled_templates = [self._process_template(template, selected_dict, use_regex, unmatched_keys)]
            else:
                for replacements in replacements_list:
                    filled_templates.append(self._process_template(template, replacements, use_regex, unmatched_keys))

        except Exception as e:
            log = f"**Error**: {str(e)}"
            PromptServer.instance.send_sync(f"{EVENT_PREFIX}stringtemplate", {
                "node": kwargs.get("node_id"),
                "value": log,
            })
            return ("", [])

        log = f"""## Result:

  **Template**: {template}
  **Replacements List**: {replacements_list}
  **Randomized**: {randomize}
  **Unmatched Keys**: {", ".join(unmatched_keys) if unmatched_keys else "None"}
  **Result**: {filled_templates}
        """

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}stringtemplate", {
            "node": kwargs.get("node_id"),
            "value": log,
        })

        return (filled_templates[0], filled_templates)

    def _process_template(self, template, replacements, use_regex, unmatched_keys):
        filled_template = template
        if use_regex:
            pattern = r"\{([^}]+)\}"
            def replace_match(match):
                key = match.group(1)
                if key in replacements:
                    return str(replacements[key])
                unmatched_keys.append(key)
                return match.group(0)
            filled_template = re.sub(pattern, replace_match, template)
        else:
            try:
                filled_template = template.format(**replacements)
            except KeyError as e:
                unmatched_keys.append(str(e).strip("'"))
        return filled_template
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_StringTemplate": LF_StringTemplate,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_StringTemplate": "String template",
}
# endregion