import json
import requests
import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import BASE64_PNG_PREFIX, EVENT_PREFIX, FUNCTION, HEADERS, Input, INT_MAX, get_image_classifier_system
from ...utils.helpers.api import handle_response
from ...utils.helpers.conversion import tensor_to_base64
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value

# region LF_ImageClassifier
class LF_ImageClassifier:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image" : (Input.IMAGE, {
                    "default": None, 
                    "tooltip": "The image that the LLM will try to classify."
                }),
                "temperature" : (Input.FLOAT, {
                    "max": 1.901, 
                    "min": 0.1, 
                    "step": 0.1, 
                    "round": 0.1, 
                    "default": 0.7, 
                    "tooltip": "Controls the randomness of the generated text. Higher values make the output more random."
                }),
                "max_tokens" : (Input.INTEGER, {
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
                "url": (Input.STRING, {
                    "default": "http://localhost:5001/v1/chat/completions", 
                    "tooltip": "URL of the local endpoint where the request is sent."
                }),
            },
            "optional": {
                "character_bio": (Input.STRING, {
                    "multiline": True, 
                    "default": "", 
                    "tooltip": "Biographical details of the character to be impersonated. Helps in shaping the tone and content of the generated text."
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
    RETURN_NAMES = ("request_json", "response_json", "message")
    RETURN_TYPES = (Input.JSON, Input.JSON, Input.STRING)

    def on_exec(self, **kwargs: dict):
        temperature: float = normalize_list_to_value(kwargs.get("temperature"))
        max_tokens: int = normalize_list_to_value(kwargs.get("max_tokens"))
        prompt: str = normalize_list_to_value(kwargs.get("prompt"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        url: str = normalize_list_to_value(kwargs.get("url"))
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        character_bio: str = normalize_list_to_value(kwargs.get("character_bio", ""))

        system = get_image_classifier_system(character_bio)

        content = []
        if isinstance(image, list) and len(image) > 0:
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
        
        PromptServer.instance.send_sync(f"{EVENT_PREFIX}imageclassifier", {
            "node": kwargs.get("node_id"),
            "value": message,
        })

        return (request, response_data, message)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_ImageClassifier": LF_ImageClassifier,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ImageClassifier": "LLM Image classifier",
}
# endregion