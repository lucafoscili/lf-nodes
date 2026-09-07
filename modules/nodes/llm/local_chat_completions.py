from typing import Any

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.api import request_local_chat_completion
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value


_REASONING_OPTIONS = ("auto", "off", "on")


def _scalar(value: Any) -> Any:
    if isinstance(value, list) and not value:
        return None
    return normalize_list_to_value(value)


# region LF_LocalChatCompletions
class LF_LocalChatCompletions:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    Input.STRING,
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "User prompt sent to the local chat-completions endpoint.",
                    },
                ),
                "url": (
                    Input.STRING,
                    {
                        "default": "http://127.0.0.1:1234/v1/chat/completions",
                        "tooltip": (
                            "Local OpenAI-compatible /v1/chat/completions or "
                            "LM Studio native /api/v1/chat endpoint."
                        ),
                    },
                ),
            },
            "optional": {
                "system_message": (
                    Input.STRING,
                    {
                        "default": "",
                        "multiline": True,
                        "tooltip": "Optional system instruction sent before the user prompt.",
                    },
                ),
                "image": (
                    Input.IMAGE,
                    {
                        "tooltip": "Optional ordered reference images for a vision-capable model.",
                    },
                ),
                "model": (
                    Input.STRING,
                    {
                        "default": "",
                        "tooltip": (
                            "Optional. Blank LM Studio native chat requests use "
                            "the sole loaded LLM instance."
                        ),
                    },
                ),
                "temperature": (
                    Input.FLOAT,
                    {
                        "default": 0.2,
                        "min": 0.0,
                        "max": 2.0,
                        "step": 0.1,
                        "tooltip": "Controls response randomness.",
                    },
                ),
                "max_tokens": (
                    Input.INTEGER,
                    {
                        "default": 4096,
                        "min": 1,
                        "tooltip": "Response token budget, including any model reasoning.",
                    },
                ),
                "timeout": (
                    Input.INTEGER,
                    {
                        "default": 120,
                        "min": 1,
                        "tooltip": "Request timeout in seconds.",
                    },
                ),
                "ui_widget": (Input.LF_CODE, {"default": ""}),
                "reasoning": (
                    list(_REASONING_OPTIONS),
                    {
                        "default": "auto",
                        "tooltip": (
                            "LM Studio native reasoning control. auto uses the "
                            "model default; off/on require /api/v1/chat."
                        ),
                    },
                ),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (False, False)
    OUTPUT_TOOLTIPS = (
        "Exact answer text returned by the local model.",
        "Complete JSON response returned by the endpoint.",
    )
    RETURN_NAMES = ("text", "response_json")
    RETURN_TYPES = (Input.STRING, Input.JSON)

    def on_exec(self, **kwargs: dict):
        prompt = _scalar(kwargs.get("prompt", ""))
        url = _scalar(kwargs.get("url", ""))
        system_message = _scalar(kwargs.get("system_message", ""))
        model = _scalar(kwargs.get("model", ""))
        temperature = _scalar(kwargs.get("temperature", 0.2))
        max_tokens = _scalar(kwargs.get("max_tokens", 4096))
        reasoning = _scalar(kwargs.get("reasoning", "auto"))
        timeout = _scalar(kwargs.get("timeout", 120))
        images = normalize_input_image(kwargs.get("image"))

        text, response_data = request_local_chat_completion(
            prompt,
            url,
            system_message=system_message,
            images=images,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            reasoning=reasoning,
            timeout=timeout,
        )
        final_payload = {"value": text}
        safe_send_sync(
            "localchatcompletions",
            final_payload,
            kwargs.get("node_id"),
        )

        return {
            "ui": {"lf_output": [final_payload]},
            "result": (text, response_data),
        }
# endregion


# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LocalChatCompletions": LF_LocalChatCompletions,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LocalChatCompletions": "Local chat completions",
}
# endregion
