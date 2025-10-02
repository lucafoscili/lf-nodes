import re

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, LORA_TAG_REGEX
from ...utils.helpers.logic import normalize_list_to_value
from ...utils.helpers.prompt import cleanse_lora_tag

# region LF_ParsePromptWithLoraTags
class LF_ParsePromptWithLoraTags:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "text": (Input.STRING, {
                    "multiline": True, 
                    "tooltip": "The input text containing LoRa tags. These tags will be processed and replaced with extracted keywords."
                }),
                "separator": (Input.STRING, { 
                    "default": "SEP", 
                    "tooltip": "Character(s) used to separate keywords within the name of a single LoRa file. Helps in extracting individual keywords."
                }),
                "weight": (Input.FLOAT, { 
                    "default": 0.5, 
                    "tooltip": "A weight value associated with LoRa tags, which may influence processing or output significance."
                }),
                "weight_placeholder": (Input.STRING, { 
                    "default": "wwWEIGHTww", 
                    "tooltip": "A placeholder within LoRa tags that gets replaced with the actual weight value during processing."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_CODE, {
                    "default": ""
                })
            },
            "hidden": { 
                "node_id": "UNIQUE_ID"
            }
        } 

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_NAMES = ("prompt", "loras")
    RETURN_TYPES = (Input.STRING, Input.STRING)

    def on_exec(self, **kwargs: dict):
        text: str = normalize_list_to_value(kwargs.get("text"))
        separator: str = normalize_list_to_value(kwargs.get("separator"))
        weight: float = normalize_list_to_value(kwargs.get("weight"))
        weight_placeholder: int = normalize_list_to_value(kwargs.get("weight_placeholder"))
        
        loras = re.findall(LORA_TAG_REGEX, text)
        
        lora_keyword_map = {}
        for lora in loras:
            lora_keyword_map[lora] = cleanse_lora_tag(lora, separator)
        
        for lora_tag, keywords in lora_keyword_map.items():
            text = text.replace(lora_tag, keywords)
        
        loras_weighted = [lora.replace(weight_placeholder, str(weight)) for lora in loras]
        loras_string = "".join(loras_weighted)

        log_entries = [f"## Breakdown\n"]
        log_entries.append(f"**Original Text**: {text}")
        log_entries.append(f"**Separator Used**: '{separator}'")
        log_entries.append(f"**Weight Placeholder**: '{weight_placeholder}', Weight Value: {weight}")
        
        log_entries.append("\n### Extracted LoRA Tags:\n")
        for lora_tag in loras:
            log_entries.append(f"- **LoRA Tag**: {lora_tag}")

        log_entries.append("\n### Keyword Mapping:\n")
        for lora_tag, keywords in lora_keyword_map.items():
            log_entries.append(f"- **Original Tag**: {lora_tag}")
            log_entries.append(f"  - **Cleansed Keywords**: {keywords}")

        log_entries.append("\n### Final Prompt Substitution:\n")
        log_entries.append(f"**Modified Text**: {text}")
        
        log = "\n".join(log_entries)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}parsepromptwithloratags", {
            "node": kwargs.get("node_id"), 
            "value": log
        })

        return (text, loras_string)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ParsePromptWithLoraTags": LF_ParsePromptWithLoraTags,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ParsePromptWithLoraTags": "Parse Prompt with LoRA tags",
}
# endregion