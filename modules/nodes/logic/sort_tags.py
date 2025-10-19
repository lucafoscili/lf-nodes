from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.logic import normalize_list_to_value
from ...utils.helpers.torch import get_clip_tokens

# region LF_SortTags
class LF_SortTags:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": (Input.CLIP, {
                    "tooltip": "CLIP model to use for tokenization."
                }),
                "caption": (Input.STRING, {
                    "tooltip": "The caption(s) whose tags need re-ordering. One per line or comma-separated."
                }),
                "desired_order": (Input.STRING, {
                    "default": "masterpiece, best quality",
                    "tooltip": "Comma-separated list indicating the desired leading order."
                }),
                "clip_limit": (Input.INTEGER, {
                    "default": 75,
                    "step": 1,
                    "tooltip": "Maximum number of CLIP tokens allowed. Exceeding this will display a warning in the output widget."
                }),
            },
            "optional": {
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
        "Final sorted caption string.",
        "List of all sorted caption strings (if any)."
    )
    RETURN_NAMES = ("string", "string_list")
    RETURN_TYPES = (Input.STRING, Input.STRING)

    def on_exec(self, **kwargs):
        def normalise_caption(caption: str) -> list[str]:
            """
            Normalises a comma-separated caption string into a list of trimmed caption elements.

            Parameters:
                caption (str): A string that may contain multiple captions separated by commas.

            Returns:
                list[str]: A list containing each non-empty caption string stripped of leading and trailing whitespace.
            """
            if not caption:
                return []
            return [t.strip() for t in caption.split(',') if t.strip()]


        def serialise_caption(tags: list[str]) -> str:
            """
            Serialises a list of tags into a comma-separated string.

            Parameters:
                tags (list[str]): A list of tags to be serialised.

            Returns:
                str: A comma-separated string of tags.
            """
            return ', '.join(tags)

        def make_log(original: str, sorted_caption: str) -> str:
            """
            Creates a log entry for the original and sorted captions, including token count.

            Parameters:
                original (str): The original caption string.
                sorted_caption (str): The sorted caption string.
                token_count (int): The number of CLIP tokens in the sorted caption.

            Returns:
                str: A formatted string containing the log entry.
            """
            token_count, token_list = get_clip_tokens(clip, sorted_caption)
            over = token_count > clip_limit
            warn = "⚠️ **TRUNCATES**" if over else "✅ within limit"
            token_lines = [f"{i+1:02d}: {tok}" for i, tok in enumerate(token_list)]
            token_lines = "\n".join(token_lines)
            return (
                f"### Original\n`{original}`\n\n"
                f"### Sorted\n`{sorted_caption}`\n\n"
                f"**CLIP tokens:** {token_count} / {clip_limit} {warn}\n\n---\n"
                f"<details><summary>Show tokens</summary>\n\n"
                f"{token_lines}\n\n</details>"
            )

        caption: str = normalize_list_to_value(kwargs.get("caption", ""))
        desired_order: str = normalize_list_to_value(kwargs.get("desired_order", ""))
        clip_limit: int = normalize_list_to_value(kwargs.get("clip_limit", 75))
        clip = normalize_list_to_value(kwargs.get("clip", None))
        node_id = kwargs.get("node_id")

        order_tokens = normalise_caption(desired_order)
        out_lines: list[str] = []
        logs: list[str] = []

        for line in caption.splitlines():
            original = line.strip()
            tokens = normalise_caption(original)
            leading = [tok for tok in order_tokens if tok in tokens]
            trailing = [tok for tok in tokens if tok not in order_tokens]
            sorted_tokens = leading + trailing
            sorted_caption = serialise_caption(sorted_tokens)

            out_lines.append(sorted_caption)
            logs.append(make_log(original, sorted_caption))

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}sorttags", {
            "node": node_id, "value": "\n".join(logs)},
        )

        result = "\n".join(out_lines)
        return (result, [result])
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_SortTags": LF_SortTags,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SortTags": "Sort tags",
}
# endregion
