import random

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, INT_MAX
from ...utils.helpers import filter_list, get_comfy_list, is_none, normalize_list_to_value, prepare_model_dataset, process_model

# region LF_LoraAndEmbeddingSelector
class LF_LoraAndEmbeddingSelector:
    initial_emb_list = get_comfy_list("embeddings")
    initial_lora_list = get_comfy_list("loras")
        
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "lora": (["None"] + self.initial_lora_list, {
                    "default": "None", 
                    "tooltip": "Lora model to use, it will also select the embedding with the same name."
                }),
                "get_civitai_info": (Input.BOOLEAN, {
                    "default": True, 
                    "tooltip": "Attempts to retrieve more info about the models from CivitAI."
                }),
                "weight": (Input.FLOAT, {
                    "default": 1.0, 
                    "min": -3.0, 
                    "max": 3.0, 
                    "tooltip": "Lora and embedding weights."
                }),
                "randomize": (Input.BOOLEAN, {
                    "default": False, 
                    "tooltip": "Selects a combination of Lora and Embedding randomly from your directories."
                }),
                "filter": (Input.STRING, {
                    "default": "", 
                    "tooltip": "When randomization is active, this field can be used to filter file names. Supports wildcards (*)."
                }),
                "seed": (Input.INTEGER, {
                    "default": 42, 
                    "min": 0, 
                    "max": INT_MAX, 
                    "tooltip": "Seed value for when randomization is active."
                }),
            },
            "optional": {
                "lora_stack": (Input.STRING, {
                    "default": "", 
                    "forceInput": True, 
                    "tooltip": "Optional string usable to concatenate subsequent Lora selector nodes."
                }),
                "embedding_stack": (Input.STRING, {
                    "default": "", 
                    "forceInput": True, 
                    "tooltip": "Optional string usable to concatenate subsequent embedding selector nodes."
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
    RETURN_NAMES = ("lora_combo", "emb_combo", "lora_tag", "emb_prompt", "lora_string", "emb_string",
                    "lora_path", "emb_path", "lora_image", "emb_image")
    RETURN_TYPES = (initial_lora_list, initial_emb_list, "STRING", "STRING", "STRING", "STRING",
                    "STRING", "STRING", "IMAGE", "IMAGE",)

    def on_exec(self, **kwargs: dict):
        lora: str = normalize_list_to_value(kwargs.get("lora"))
        get_civitai_info: bool = normalize_list_to_value(kwargs.get("get_civitai_info"))
        weight: float = normalize_list_to_value(kwargs.get("weight"))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        filter: str = normalize_list_to_value(kwargs.get("filter"))
        lora_stack: str = normalize_list_to_value(kwargs.get("lora_stack", ""))
        embedding_stack: str = normalize_list_to_value(kwargs.get("embedding_stack", ""))

        if is_none(lora):
            lora = None
        
        passthrough = bool(not lora and not randomize)

        if passthrough:

            PromptServer.instance.send_sync(f"{EVENT_PREFIX}loraandembeddingselector", {
                "node": kwargs.get("node_id"),
                "apiFlags": [False],
            })

            return (None, None, lora_stack, embedding_stack, "", "", "", "", None, None)
        
        EMBEDDINGS = get_comfy_list("embeddings")
        LORAS = get_comfy_list("loras")

        if randomize:
            if filter:
                LORAS = filter_list(filter, LORAS)
                if not LORAS:
                    raise ValueError(f"Not found a model with the specified filter: {filter}")
            random.seed(seed)
            lora = random.choice(LORAS)

        embedding = lora
        if embedding not in EMBEDDINGS:
            raise ValueError(f"Not found an embedding named {lora}")

        lora_data = process_model("lora", lora, "loras")
        l_name = lora_data["model_name"]
        l_hash = lora_data["model_hash"]
        l_path = lora_data["model_path"]
        l_base64 = lora_data["model_base64"]
        l_cover = lora_data["model_cover"]
        l_saved_info = lora_data["saved_info"]

        embedding_data = process_model("embedding", embedding, "embeddings")
        e_name = embedding_data["model_name"]
        e_hash = embedding_data["model_hash"]
        e_path = embedding_data["model_path"]
        e_base64 = embedding_data["model_base64"]
        e_cover = embedding_data["model_cover"]
        e_saved_info = embedding_data["saved_info"]

        lora_tag = f"<lora:{l_name}:{weight}>"
        formatted_embedding = f"embedding:{e_name}" if weight == 1 else f"(embedding:{e_name}:{weight})"

        if l_saved_info:
            l_dataset = l_saved_info
        else:
            l_dataset = prepare_model_dataset(l_name, l_hash, l_base64, l_path)

        if e_saved_info:
            e_dataset = e_saved_info
        else:
            e_dataset = prepare_model_dataset(e_name, e_hash, e_base64, e_path)

        if lora_stack:
            lora_tag = f"{lora_tag}, {lora_stack}"

        if embedding_stack:
            formatted_embedding = f"{formatted_embedding}, {embedding_stack}"

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}loraandembeddingselector", {
            "node": kwargs.get("node_id"),
            "datasets": [l_dataset, e_dataset],
            "hashes": [l_hash, e_hash],
            "apiFlags": [False if l_saved_info else get_civitai_info, False if e_saved_info else get_civitai_info],
            "paths": [l_path, e_path],
        })

        return (lora, embedding, lora_tag, formatted_embedding, l_name, e_name, l_path, e_path, l_cover, e_cover)
    
    @classmethod
    def VALIDATE_INPUTS(self, **kwargs):
         return True
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LoraAndEmbeddingSelector": LF_LoraAndEmbeddingSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LoraAndEmbeddingSelector": "LoRA and embedding selector",
}
# endregion