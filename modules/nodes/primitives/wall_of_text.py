import random

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers.logic import normalize_list_to_value

# region LF_WallOfText
class LF_WallOfText:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "separator": (Input.STRING, {
                    "default": ", ",
                    "tooltip": "Character(s) separating each string apart."}),
                "text_1": (Input.STRING, {
                    "default": "",
                    "tooltip": "The first required string."}),
                "text_2": (Input.STRING, {
                    "default": "",
                    "tooltip": "The second required string."}),
            },
            "optional": {
                "text_3": (Input.STRING, {
                    "default": "",
                    "forceInput": True,
                    "tooltip": "The third optional string."
                }),
                "text_4": (Input.STRING, {
                    "default": "",
                    "forceInput": True,
                    "tooltip": "The fourth optional string."
                }),
                "text_5": (Input.STRING, {
                    "default": "",
                    "forceInput": True,
                    "tooltip": "The fifth optional string."
                }),
                "text_6": (Input.STRING, {
                    "default": "",
                    "forceInput": True,
                    "tooltip": "The sixth optional string."
                }),
                "text_7": (Input.STRING, {
                    "default": "",
                    "forceInput": True,
                    "tooltip": "The seventh optional string."
                }),
                "text_8": (Input.STRING, {
                    "default": "",
                    "forceInput": True,
                    "tooltip": "The eighth optional string."
                }),
                "text_9": (Input.STRING, {
                    "default": "",
                    "forceInput": True,
                    "tooltip": "The ninth optional string."
                }),
                "text_10": (Input.STRING, {
                    "default": "",
                    "forceInput": True,
                    "tooltip": "The tenth optional string."
                }),
                "shuffle_inputs": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Toggle shuffling of input strings."
                }),
                "seed": (Input.INTEGER, {
                    "default": 42,
                    "max": INT_MAX,
                    "tooltip": "Seed to control the randomness of the shuffling."
                }),
                "ui_widget": (Input.LF_CODE, {
                    "default": ""
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
        "Combined text output.",
        "Combined text output as a list."
    )
    RETURN_NAMES = ("string", "string_list")
    RETURN_TYPES = (Input.STRING, Input.STRING)

    def on_exec(self, **kwargs: dict):
        texts: list[str] = [normalize_list_to_value(kwargs.get(f"text_{i}", "")) for i in range(1, 11)]

        if len(texts) > 1:
            separator = kwargs.get("separator", "")
            shuffle_inputs = kwargs.get("shuffle_inputs", False)
            if shuffle_inputs:
                seed = kwargs.get("seed", 42)
                random.seed(seed)
                random.shuffle(texts)
            wall_of_text = separator.join([text for text in texts if text])
        else:
            wall_of_text = texts[0]

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}walloftext", {
            "node": kwargs.get("node_id"),
            "value": wall_of_text,
        })

        return (wall_of_text, wall_of_text)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_WallOfText": LF_WallOfText
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_WallOfText": "Wall of text"
}
# endregion
