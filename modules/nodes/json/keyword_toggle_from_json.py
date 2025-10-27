from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.logic import normalize_list_to_value, normalize_json_input

# region LF_KeywordToggleFromJSON
class LF_KeywordToggleFromJSON:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "json_input": (Input.JSON, {
                    "tooltip": "LF Widgets compatible JSON dataset."
                }),
                "separator": (Input.STRING, {
                    "default": ", ",
                    "tooltip": "Separator for keywords in the output prompt."
                }),
                "ui_widget": (Input.LF_CHIP, {
                    "default": ""
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, False, True)
    OUTPUT_TOOLTIPS = (
        "Filtered JSON object with selected keywords.",
        "Concatenated keywords string.",
        "List of selected keywords."
    )
    RETURN_NAMES = ("json", "keywords", "keywords_list")
    RETURN_TYPES = (Input.JSON, Input.STRING, Input.STRING)

    def on_exec(self, **kwargs: dict):
        json_input = normalize_json_input(kwargs.get("json_input"))
        if (
            isinstance(json_input, list)
            and len(json_input) == 1
            and isinstance(json_input[0], dict)
        ):
            json_input = json_input[0]
        separator: str = normalize_list_to_value(kwargs.get("separator"))
        ui_widget: str = normalize_list_to_value(kwargs.get("ui_widget", ""))

        selected_keywords = ui_widget.split(", ")

        filtered_json = {
            "nodes": [
                node for node in json_input["nodes"]
                if node["id"] in selected_keywords or node["value"] in selected_keywords
            ]
        }

        keyword_values = [node["value"] for node in filtered_json["nodes"]]
        keywords_output = separator.join(keyword_values)

        return (filtered_json, keywords_output, keyword_values)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_KeywordToggleFromJSON": LF_KeywordToggleFromJSON,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_KeywordToggleFromJSON": "Keyword toggle from JSON",
}
# endregion
