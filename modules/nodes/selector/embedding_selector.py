import random

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers.api import process_model
from ...utils.helpers.comfy import get_comfy_list
from ...utils.helpers.logic import filter_list, is_none, normalize_list_to_value
from ...utils.helpers.ui import prepare_model_dataset

# region LF_EmbeddingSelector
class LF_EmbeddingSelector:
    initial_list = get_comfy_list("embeddings")

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "embedding": (["None"] + self.initial_list, {
                    "default": "None", 
                    "tooltip": "Embedding to use."
                }),
                "get_civitai_info": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Attempts to retrieve more info about the model from CivitAI."
                }),
                "weight": (Input.FLOAT, {
                    "default": 1.0, 
                    "min": -3.0, 
                    "max": 3.0, 
                    "tooltip": "Embedding's weight."
                }),
                "randomize": (Input.BOOLEAN, {
                    "default": False, 
                    "tooltip": "Selects an embedding randomly from your embeddings directory."
                }),
                "seed": (Input.INTEGER, {
                    "default": 42, 
                    "min": 0, 
                    "max": INT_MAX, 
                    "tooltip": "Seed value for when randomization is active."
                }),
                "filter": (Input.STRING, {
                    "default": "", 
                    "tooltip": "When randomization is active, this field can be used to filter embedding file names. Supports wildcards (*)."
                }),
            },
            "optional": {
                "embedding_stack": (Input.STRING, {
                    "default": "", 
                    "forceInput": True, 
                    "tooltip": "Optional string usable to concatenate subsequent selector nodes."
                }),
                "ui_widget": (Input.LF_CARD, {
                    "default": {}
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_NAMES = ("combo", "prompt", "string", "path", "image")
    RETURN_TYPES = (initial_list, "STRING", "STRING", "STRING", "IMAGE")

    def on_exec(self, **kwargs: dict):
        embedding: str = normalize_list_to_value(kwargs.get("embedding"))
        get_civitai_info: bool = normalize_list_to_value(kwargs.get("get_civitai_info"))
        weight: float = normalize_list_to_value(kwargs.get("weight"))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        filter: str = normalize_list_to_value(kwargs.get("filter"))
        embedding_stack: str = normalize_list_to_value(kwargs.get("embedding_stack", ""))

        if is_none(embedding):
            embedding = None

        passthrough = bool(not embedding and not randomize)

        if passthrough:

            PromptServer.instance.send_sync(f"{EVENT_PREFIX}embeddingselector", {
                "node": kwargs.get("node_id"),
                "apiFlags": [False],
            })

            return (None, embedding_stack, "", "", None)
        
        embeddings = get_comfy_list("embeddings")

        if randomize:
            if filter:
                embeddings = filter_list(filter, embeddings)
                if not embeddings:
                    raise ValueError(f"Not found a model with the specified filter: {filter}")
            random.seed(seed)
            embedding = random.choice(embeddings)

        embedding_data = process_model("embedding", embedding, "embeddings")
        model_name = embedding_data["model_name"]
        model_hash = embedding_data["model_hash"]
        model_path = embedding_data["model_path"]
        model_base64 = embedding_data["model_base64"]
        model_cover = embedding_data["model_cover"]
        saved_info = embedding_data["saved_info"]

        formatted_embedding =  f"embedding:{model_name}" if weight == 1 else f"(embedding:{model_name}:{weight})"

        if saved_info:
            dataset = saved_info
            get_civitai_info = False
        else:
            dataset = prepare_model_dataset(model_name, model_hash, model_base64, model_path)

        if embedding_stack:
            formatted_embedding = f"{formatted_embedding}, {embedding_stack}"

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}embeddingselector", {
            "node": kwargs.get("node_id"),
            "datasets": [dataset],
            "hashes": [model_hash],
            "apiFlags": [get_civitai_info],
            "paths": [model_path],
        })

        return (embedding, formatted_embedding, model_name, model_path, model_cover)
    
    @classmethod
    def VALIDATE_INPUTS(self, **kwargs):
         return True
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_EmbeddingSelector": LF_EmbeddingSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_EmbeddingSelector": "Embedding selector",
}
# endregion