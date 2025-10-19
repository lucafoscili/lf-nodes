import json
import requests

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, HEADERS, Input, INT_MAX, get_doc_generator_system
from ...utils.helpers.api import handle_response
from ...utils.helpers.logic import normalize_list_to_value

# region LF_MarkdownDocGenerator
class LF_MarkdownDocGenerator:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "prompt": (Input.STRING, {
                    "default": "",
                    "multiline": True,
                    "tooltip": "The source file to document."
                }),
                "temperature": (Input.FLOAT, {
                    "max": 1.901,
                    "min": 0.1,
                    "step": 0.1,
                    "round": 0.1,
                    "default": 0.5,
                    "tooltip": "Controls the randomness of the generated text. Higher values make the output more random."
                }),
                "max_tokens": (Input.INTEGER, {
                    "max": 8000,
                    "min": 20,
                    "step": 10,
                    "default": 2000,
                    "tooltip": "Limits the length of the generated text. Adjusting this value can help control the verbosity of the output."
                }),
                "seed": (Input.INTEGER, {
                    "default": 42,
                    "min": 0,
                    "max": INT_MAX,
                    "tooltip": "Determines the starting point for generating random numbers. Setting a specific seed ensures reproducibility of results."
                }),
                "url": (Input.STRING, {
                    "default": "http://localhost:5001/v1/chat/completions",
                    "tooltip": "URL of the local endpoint for the LLM."
                }),
            },
            "optional": {
                "extra_context": (Input.STRING, {
                    "default": "",
                    "multiline": True,
                    "tooltip": "Additional context to guide the LLM (out of scope constants and helpers definitions)."
                }),
                "ui_widget" : (Input.LF_CODE, {
                    "default": ""
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, False, False, True)
    OUTPUT_TOOLTIPS = (
        "Request payload for the markdown generation.",
        "Response from the markdown generation API.",
        "Generated markdown content.",
        "Generated markdown content as a list."
    )
    RETURN_NAMES = ("request_json", "response_json", "markdown", "markdown_list")
    RETURN_TYPES = (Input.JSON, Input.JSON, Input.STRING, Input.STRING)

    def on_exec(self, **kwargs: dict):
        temperature: float = normalize_list_to_value(kwargs.get("temperature"))
        max_tokens: int = normalize_list_to_value(kwargs.get("max_tokens"))
        prompt: str = normalize_list_to_value(kwargs.get("prompt"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        url: str = normalize_list_to_value(kwargs.get("url"))
        extra_context: str = normalize_list_to_value(kwargs.get("extra_context", ""))

        request = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "seed": seed,
            "messages": [
              {
                "role": "system",
                "content": get_doc_generator_system(extra_context)
              },
              {
                "role": "user",
                "content": prompt
              },
            ],
        }

        response = requests.post(url, headers=HEADERS, data=json.dumps(request))
        response_data = response.json()
        status_code, _, message = handle_response(response, method="POST")

        if status_code != 200:
            message = f"Oops! Documentation generation failed with status code {status_code}."

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}markdowndocgenerator", {
            "node": kwargs.get("node_id"),
            "value": message,
        })

        return (request, response_data, message, [message])
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_MarkdownDocGenerator": LF_MarkdownDocGenerator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_MarkdownDocGenerator": "Markdown doc. generator"
}
# endregion
