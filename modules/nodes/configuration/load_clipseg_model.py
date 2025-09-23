import os

from folder_paths import get_folder_paths
from server import PromptServer
from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.logic import normalize_list_to_value

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
    RETURN_TYPES = ("*", "*")
    RETURN_NAMES = ("processor", "model")

    def on_exec(self, **kwargs: dict):
        node_id = kwargs.get("node_id")
        folder = normalize_list_to_value(kwargs["folder"])
        model_id = normalize_list_to_value(kwargs["model_id"])
        base_dir = get_folder_paths(folder)[0]

        safe_name = model_id.replace("/", "--")
        model_dir = os.path.join(base_dir, safe_name)
        required_any = {"config.json", "preprocessor_config.json"}
        exists = os.path.isdir(model_dir) and any(
            name in required_any for name in os.listdir(model_dir)
        )

        log_lines = []
        if exists:
            log_lines.append(f"- ✅ Model already present → `{model_dir}`")
        else:
            log_lines.append(f"- ⏳ Downloading **{model_id}** → `{model_dir}`")

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}loadclipsegmodel", {
            "node": node_id, 
            "value": "## Load CLIPSeg Model\n\n" + "\n".join(log_lines)
        })

        try:
            if exists:
                processor = CLIPSegProcessor.from_pretrained(model_dir)
                model = CLIPSegForImageSegmentation.from_pretrained(model_dir).eval()
                log_lines.append(f"- ✅ Loaded processor & model from local folder: {model_dir}")
            else:
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
        
        PromptServer.instance.send_sync(f"{EVENT_PREFIX}loadclipsegmodel", {
            "node": node_id, 
            "value": "## Load CLIPSeg Model\n\n" + "\n".join(log_lines)
        })

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