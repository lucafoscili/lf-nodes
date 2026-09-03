import ntpath
import os
from pathlib import Path

import folder_paths
from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value


def _local_model_leaf(model_id: str) -> str:
    drive, _ = ntpath.splitdrive(model_id)
    parts = model_id.split("/")
    if (
        not model_id
        or drive
        or "\\" in model_id
        or any(part in {"", ".", ".."} for part in parts)
        or any(
            not all(
                character.isascii()
                and (character.isalnum() or character in "._-")
                for character in part
            )
            for part in parts
        )
    ):
        raise ValueError(f"Invalid Hugging Face model ID for local storage: {model_id!r}")
    local_leaf = "--".join(parts)
    if (
        local_leaf.endswith(".")
        or local_leaf.split(".", 1)[0].upper()
        in {
            "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
        }
    ):
        raise ValueError(f"Invalid Hugging Face model ID for local storage: {model_id!r}")
    return local_leaf


def _model_dir(root: str, local_leaf: str) -> str:
    resolved_root = Path(root).resolve()
    candidate = (resolved_root / local_leaf).resolve()
    if not folder_paths.is_within_directory(str(resolved_root), str(candidate)):
        raise ValueError(f"Local CLIPSeg model path escapes its registered root: {candidate}")
    return str(candidate)

# region LF_LoadCLIPSegModel
class LF_LoadCLIPSegModel:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder": (Input.STRING, {
                    "default": "clip_vision",
                    "tooltip": "Folder to download the model to. This folder must be in the ComfyUI directory."
                }),
                "model_id": (Input.STRING, {
                    "default": "CIDAS/clipseg-rd64-refined",
                    "tooltip": "HuggingFace CLIPSeg model ID."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_CODE, {
                    "default": {}
                })
            },
            "hidden": {"node_id":"UNIQUE_ID"}
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "CLIPSeg processor.",
        "CLIPSeg model."
    )
    RETURN_NAMES = ("processor", "model")
    RETURN_TYPES = (Input.CLIP_PROCESSOR, Input.CLIP_MODEL)

    def on_exec(self, **kwargs: dict):
        node_id = kwargs.get("node_id")
        folder = normalize_list_to_value(kwargs["folder"])
        model_id = normalize_list_to_value(kwargs["model_id"])
        base_dirs = folder_paths.get_folder_paths(folder)
        base_dir = base_dirs[0]

        local_leaf = _local_model_leaf(model_id)
        model_dirs = [_model_dir(root, local_leaf) for root in base_dirs]
        local_model_dirs = [path for path in model_dirs if os.path.isdir(path)]
        model_dir = model_dirs[0]

        log_lines = []
        if local_model_dirs:
            log_lines.append(f"- ⏳ Loading local model → `{local_model_dirs[0]}`")
        else:
            log_lines.append(f"- ⏳ Downloading **{model_id}** → `{model_dir}`")

        safe_send_sync("loadclipsegmodel", {
            "value": "## Load CLIPSeg Model\n\n" + "\n".join(log_lines)
        }, node_id)

        for local_model_dir in local_model_dirs:
            try:
                processor = CLIPSegProcessor.from_pretrained(local_model_dir)
                model = CLIPSegForImageSegmentation.from_pretrained(local_model_dir).eval()
            except Exception as error:
                log_lines.append(f"- ⚠️ Skipped unusable local model: `{local_model_dir}` ({error})")
                continue

            log_lines.append(f"- ✅ Loaded processor & model from local folder: {local_model_dir}")
            safe_send_sync("loadclipsegmodel", {
                "value": "## Load CLIPSeg Model\n\n" + "\n".join(log_lines)
            }, node_id)
            return (processor, model)

        if local_model_dirs:
            log_lines.append(f"- ⏳ No usable local copy; downloading **{model_id}** → `{model_dir}`")

        try:
            os.makedirs(model_dir, exist_ok=True)
            processor = CLIPSegProcessor.from_pretrained(model_id, cache_dir=base_dir)
            model = CLIPSegForImageSegmentation.from_pretrained(model_id, cache_dir=base_dir).eval()
            processor.save_pretrained(model_dir)
            model.save_pretrained(model_dir)
            log_lines.append(f"- ✅ Downloaded from Hub ({model_id}) and saved to: {model_dir}")
        except Exception as e:
            try:
                processor = CLIPSegProcessor.from_pretrained(model_id)
                model = CLIPSegForImageSegmentation.from_pretrained(model_id).eval()
                log_lines.append(f"- ⚠️ Fallback: Loaded from Hub without saving (cache-managed) for {model_id}")
            except Exception as e2:
                raise RuntimeError(
                    f"- ❌ Failed to load CLIPSeg model. Local: '{model_dir}' error: {e}; Hub '{model_id}' error: {e2}"
                )

        safe_send_sync("loadclipsegmodel", {
            "value": "## Load CLIPSeg Model\n\n" + "\n".join(log_lines)
        }, node_id)

        return (processor, model)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LoadCLIPSegModel": LF_LoadCLIPSegModel,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LoadCLIPSegModel": "Load CLIPSeg model",
}
# endregion
