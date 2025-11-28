from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value
from ...utils.helpers.tagging import create_wd14_onnx_tagger

# region LF_LoadWD14Onnx
class LF_LoadWD14Onnx:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_id": (
                    Input.STRING,
                    {
                        "default": "SmilingWolf/wd-vit-large-tagger-v3",
                        "tooltip": "HuggingFace WD14 ONNX repo ID or local directory containing model.onnx and selected_tags.csv.",
                    },
                ),
                "min_probability": (
                    Input.FLOAT,
                    {
                        "default": 0.4,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.01,
                        "tooltip": "Minimum probability for a tag to be kept (TagGUI default: 0.4).",
                    },
                ),
                "max_tags": (
                    Input.INTEGER,
                    {
                        "default": 30,
                        "min": 1,
                        "step": 1,
                        "tooltip": "Maximum number of tags to return (TagGUI default: 30).",
                    },
                ),
                "tags_to_exclude": (
                    Input.STRING,
                    {
                        "default": "",
                        "tooltip": "Tags to exclude (comma-separated, supports TagGUI-style escaped commas).",
                    },
                ),
            },
            "optional": {
                "ui_widget": (
                    Input.LF_CODE,
                    {
                        "default": {},
                    },
                )
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "WD14 ONNX tagger object (session + tag metadata and defaults).",
    )
    RETURN_NAMES = ("tagger",)
    RETURN_TYPES = (Input.TAGGER,)

    def on_exec(self, **kwargs: dict):
        node_id: str = kwargs.get("node_id")
        model_id: str = normalize_list_to_value(
            kwargs.get("model_id") or "SmilingWolf/wd-vit-large-tagger-v3"
        )
        min_probability = float(
            normalize_list_to_value(kwargs.get("min_probability", 0.4))
        )
        max_tags = int(normalize_list_to_value(kwargs.get("max_tags", 30)))
        tags_to_exclude = normalize_list_to_value(
            kwargs.get("tags_to_exclude", "")
        ) or ""

        log_lines: list[str] = [
            "## Load WD14 ONNX\n\n",
            f"- Model: **{model_id}**\n",
        ]

        try:
            tagger = create_wd14_onnx_tagger(
                model_id=model_id,
                min_probability=min_probability,
                max_tags=max_tags,
                tags_to_exclude=tags_to_exclude,
            )
            log_lines.append("- ✅ ONNX model and tags loaded.\n")
        except Exception as exc:
            log_lines.append(f"- ❌ Failed to load WD14 ONNX model: {exc}\n")
            safe_send_sync(
                "loadwd14onnx",
                {
                    "value": "".join(log_lines),
                },
                node_id,
            )
            raise

        safe_send_sync(
            "loadwd14onnx",
            {
                "value": "".join(log_lines),
            },
            node_id,
        )

        return (tagger,)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LoadWD14Onnx": LF_LoadWD14Onnx,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LoadWD14Onnx": "Load WD14 model (ONNX)",
}
# endregion
