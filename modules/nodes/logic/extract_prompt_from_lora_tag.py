import re

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, LORA_TAG_REGEX
from ...utils.helpers.logic import normalize_input_list, normalize_list_to_value
from ...utils.helpers.prompt import count_words_in_comma_separated_string, cleanse_lora_tag
from ...utils.helpers.comfy import safe_send_sync

# region LF_ExtractPromptFromLoraTag
class LF_ExtractPromptFromLoraTag:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "tag": (Input.STRING, {
                    "multiline": True,
                    "tooltip": "The LoRA tag to be converted."
                }),
                "separator": (Input.STRING, {
                    "default": "SEP",
                    "tooltip": "String separating each keyword in a LoRA filename."
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
    OUTPUT_TOOLTIPS = (
        "Extracted keywords from the LoRA tag.",
        "Count of keywords extracted.",
        "List of all extracted keywords.",
        "List of keyword counts for each entry."
    )
    RETURN_NAMES = ("keywords", "keywords_count", "keywords_list", "keywords_count_list")
    RETURN_TYPES = (Input.STRING, Input.INTEGER, Input.STRING, Input.INTEGER)

    def on_exec(self, **kwargs: dict):
        tag_list: list[str] = normalize_input_list(kwargs.get("tag"))
        separator: str = normalize_list_to_value(kwargs.get("separator"))

        clean_loras: list[str] = []
        keyword_counts: list[int] = []
        log_entries: list[str] = []

        for tag_entry in tag_list:
            tags_in_entry = re.findall(LORA_TAG_REGEX, tag_entry)

            for t in tags_in_entry:
                clean_lora = cleanse_lora_tag(t, separator)
                keywords_count = count_words_in_comma_separated_string(clean_lora)
                clean_loras.append(clean_lora)
                keyword_counts.append(keywords_count)

                log_entries.append(f"""
### LoRA Tag Entry:

- **Original Tag**: {t}
- **Cleaned LoRA Tag**: {clean_lora}
- **Number of Keywords**: {keywords_count}
- **Keywords Extracted**: {clean_lora.split(', ') if clean_lora else '*No keywords extracted*'}
                """)

        log = f"""## Breakdown

### Input Details:

- **Original Tags**: {tag_list}
- **Separator Used**: '{separator}'

{''.join(log_entries)}
        """

        safe_send_sync("extractpromptfromloratag", {
            "value": log
        }, kwargs.get("node_id"))

        return (clean_loras, keyword_counts, clean_loras, keyword_counts)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ExtractPromptFromLoraTag": LF_ExtractPromptFromLoraTag,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ExtractPromptFromLoraTag": "Extract prompt from LoRA tag",
}
# endregion
