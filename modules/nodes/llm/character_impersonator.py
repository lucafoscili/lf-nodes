import json
import requests
import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import BASE64_PNG_PREFIX, EVENT_PREFIX, FUNCTION, HEADERS, Input, INT_MAX, get_character_impersonator_system
from ...utils.helpers.api import handle_response
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.conversion import tensor_to_base64
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value

# region LF_CharacterImpersonator
class LF_CharacterImpersonator:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "temperature": (Input.FLOAT, {
                    "max": 1.901,
                    "min": 0.1,
                    "step": 0.1,
                    "round": 0.1,
                    "default": 0.7,
                    "tooltip": "Controls the randomness of the generated text. Higher values make the output more random."
                }),
                "max_tokens": (Input.INTEGER, {
                    "max": 8000,
                    "min": 20,
                    "step": 10,
                    "default": 500,
                    "tooltip": "Limits the length of the generated text. Adjusting this value can help control the verbosity of the output."
                }),
                "prompt": (Input.STRING, {
                    "multiline": True,
                    "default": "",
                    "tooltip": "The initial input or question that guides the generation process. Can be a single line or multiple lines of text."
                }),
                "seed": (Input.INTEGER, {
                    "default": 42,
                    "min": 0,
                    "max": INT_MAX,
                    "tooltip": "Determines the starting point for generating random numbers. Setting a specific seed ensures reproducibility of results."
                }),
                "character_bio": (Input.STRING, {
                    "multiline": True,
                    "default": "",
                    "tooltip": "Biographical details of the character to be impersonated. Helps in shaping the tone and content of the generated text."
                }),
                "url": (Input.STRING, {
                    "default": "http://localhost:5001/v1/chat/completions",
                    "tooltip": "URL of the local endpoint where the request is sent."
                }),
            },
            "optional":{
                "image" : (Input.IMAGE, {
                    "default": None,
                    "tooltip": "An optional image that can be included in the generation process to influence the output based on visual cues."
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
    OUTPUT_TOOLTIPS = (
        "Request payload for the character impersonation.",
        "Response from the character impersonation API.",
        "Final generated answer from the character impersonation."
    )
    RETURN_NAMES = ("request_json", "response_json", "answer")
    RETURN_TYPES = (Input.JSON, Input.JSON, Input.STRING)

    def on_exec(self, **kwargs: dict):
        temperature: float = normalize_list_to_value(kwargs.get("temperature"))
        max_tokens: int = normalize_list_to_value(kwargs.get("max_tokens"))
        prompt: str = normalize_list_to_value(kwargs.get("prompt"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        character_bio: str = normalize_list_to_value(kwargs.get("character_bio"))
        url: str = normalize_list_to_value(kwargs.get("url"))
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image", []))

        system = get_character_impersonator_system(character_bio)

        content = []
        if isinstance(image, list) and len(image) > 0:
            image = normalize_input_image(image)
            b64_image = tensor_to_base64(image[0])
            image_url = f"{BASE64_PNG_PREFIX}{b64_image}"
            content.append({"type": "image_url", "image_url": {"url":image_url}})

        if prompt:
            content.append({"type": "text", "text": prompt})

        request = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "seed": seed,
            "messages": [
              {
                "role": "system",
                "content": system
              },
              {
                "role": "user",
                "content": content
              },
            ],
        }

        response = requests.post(url, headers=HEADERS, data=json.dumps(request))
        response_data = response.json()
        status_code, method, message = handle_response(response, method="POST")
        if status_code != 200:
            message = f"Whoops! Request failed with status code {status_code} and method {method}."

        safe_send_sync("characterimpersonator", {
            "value": message,
        }, kwargs.get("node_id"))

        return (request, response_data, message)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_CharacterImpersonator": LF_CharacterImpersonator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_CharacterImpersonator": "LLM <-> Character",
}
# endregion
