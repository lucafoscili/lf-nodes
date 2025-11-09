import random

from typing import Optional, Tuple

from . import CATEGORY
from ...utils.constants import FUNCTION, Input, INT_MAX
from ...utils.helpers.api import process_model_async
from ...utils.helpers.comfy import get_comfy_list, safe_send_sync
from ...utils.helpers.logic import dataset_from_metadata, filter_list, is_none, normalize_list_to_value

# region LF_LoraAndEmbeddingSelector
class LF_LoraAndEmbeddingSelector:
    initial_emb_list = get_comfy_list("embeddings")
    initial_lora_list = get_comfy_list("loras")
    _LAST_SELECTION: dict[str, Tuple[Optional[str], Optional[str]]] = {}

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
    OUTPUT_TOOLTIPS = (
        "Combo list of LoRAs.",
        "Combo list of embeddings.",
        "Selected LoRA item as a tag.",
        "Selected embedding item as a prompt string.",
        "Selected LoRA item as a string.",
        "Selected embedding item as a string.",
        "Path to the selected LoRA.",
        "Path to the selected embedding.",
        "Cover image of the selected LoRA.",
        "Cover image of the selected embedding.",
    )
    RETURN_NAMES = ("lora_combo", "emb_combo", "lora_tag", "emb_prompt", "lora_string", "emb_string",
                    "lora_path", "emb_path", "lora_image", "emb_image")
    RETURN_TYPES = (initial_lora_list, initial_emb_list, Input.STRING, Input.STRING, Input.STRING, Input.STRING,
                    Input.STRING, Input.STRING, Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        lora: str = normalize_list_to_value(kwargs.get("lora"))
        get_civitai_info: bool = normalize_list_to_value(kwargs.get("get_civitai_info"))
        weight: float = normalize_list_to_value(kwargs.get("weight"))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        filter: str = normalize_list_to_value(kwargs.get("filter"))
        lora_stack: str = normalize_list_to_value(kwargs.get("lora_stack", ""))
        embedding_stack: str = normalize_list_to_value(kwargs.get("embedding_stack", ""))
        node_id = kwargs.get("node_id")

        if is_none(lora):
            lora = None

        passthrough = bool(not lora and not randomize)

        if passthrough:

            safe_send_sync("loraandembeddingselector", {
                "apiFlags": [False],
            }, node_id)

            if node_id:
                self._LAST_SELECTION.pop(node_id, None)

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

        should_fetch_civitai = bool(get_civitai_info)

        combined_metadata = {"lora": None, "embedding": None}

        def send_update() -> None:
            l_metadata = combined_metadata["lora"]
            e_metadata = combined_metadata["embedding"]
            if l_metadata is None or e_metadata is None:
                return

            l_dataset, l_hash = dataset_from_metadata(l_metadata)
            e_dataset, e_hash = dataset_from_metadata(e_metadata)

            l_pending = bool(l_metadata.get("metadata_pending", False))
            e_pending = bool(e_metadata.get("metadata_pending", False))

            def _should_fetch(meta: dict, hash_value: str, pending: bool) -> bool:
                if not should_fetch_civitai:
                    return False
                if meta.get("saved_info"):
                    return False
                if pending:
                    return False
                return bool(hash_value) and hash_value != "Unknown"

            fetch_flags = [
                _should_fetch(l_metadata, l_hash, l_pending),
                _should_fetch(e_metadata, e_hash, e_pending),
            ]

            safe_send_sync(
                "loraandembeddingselector",
                {
                    "datasets": [l_dataset, e_dataset],
                    "hashes": [l_hash if l_hash else "", e_hash if e_hash else ""],
                    "apiFlags": fetch_flags,
                    "paths": [
                        l_metadata.get("model_path") or "",
                        e_metadata.get("model_path") or "",
                    ],
                },
                node_id,
            )

        def _metadata_callback(kind: str):
            def _callback(metadata_ready: dict) -> None:
                if node_id:
                    current = self._LAST_SELECTION.get(node_id)
                    ready_l_path = (
                        metadata_ready.get("model_path")
                        if kind == "lora"
                        else (combined_metadata["lora"].get("model_path") if combined_metadata["lora"] else None)
                    )
                    ready_e_path = (
                        metadata_ready.get("model_path")
                        if kind == "embedding"
                        else (combined_metadata["embedding"].get("model_path") if combined_metadata["embedding"] else None)
                    )
                    ready_tuple = (ready_l_path, ready_e_path)
                    if current and current != ready_tuple:
                        return

                combined_metadata[kind] = metadata_ready

                if node_id:
                    l_path_sel = combined_metadata["lora"].get("model_path") if combined_metadata["lora"] else None
                    e_path_sel = (
                        combined_metadata["embedding"].get("model_path") if combined_metadata["embedding"] else None
                    )
                    if l_path_sel or e_path_sel:
                        self._LAST_SELECTION[node_id] = (l_path_sel, e_path_sel)
                    else:
                        self._LAST_SELECTION.pop(node_id, None)

                send_update()

            return _callback

        l_callback = _metadata_callback("lora") if node_id and lora else None
        e_callback = _metadata_callback("embedding") if node_id and embedding else None

        combined_metadata["lora"] = process_model_async("lora", lora, "loras", on_complete=l_callback)
        combined_metadata["embedding"] = process_model_async(
            "embedding", embedding, "embeddings", on_complete=e_callback
        )

        if node_id:
            l_path_sel = combined_metadata["lora"].get("model_path") if combined_metadata["lora"] else None
            e_path_sel = combined_metadata["embedding"].get("model_path") if combined_metadata["embedding"] else None
            if l_path_sel or e_path_sel:
                self._LAST_SELECTION[node_id] = (l_path_sel, e_path_sel)
            else:
                self._LAST_SELECTION.pop(node_id, None)

        send_update()

        l_metadata = combined_metadata["lora"]
        e_metadata = combined_metadata["embedding"]

        l_name = l_metadata.get("model_name") or lora
        e_name = e_metadata.get("model_name") or embedding
        l_path = l_metadata.get("model_path")
        e_path = e_metadata.get("model_path")

        lora_tag = f"<lora:{l_name}:{weight}>"
        formatted_embedding = f"embedding:{e_name}" if weight == 1 else f"(embedding:{e_name}:{weight})"

        if lora_stack:
            lora_tag = f"{lora_tag}, {lora_stack}"

        if embedding_stack:
            formatted_embedding = f"{formatted_embedding}, {embedding_stack}"

        return (
            lora,
            embedding,
            lora_tag,
            formatted_embedding,
            l_name,
            e_name,
            l_path,
            e_path,
            l_metadata.get("model_cover"),
            e_metadata.get("model_cover"),
        )

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
