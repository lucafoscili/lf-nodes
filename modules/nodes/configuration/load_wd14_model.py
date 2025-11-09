import timm

from huggingface_hub import snapshot_download
from tqdm.auto import tqdm
from timm.data import create_transform, resolve_data_config
from torchvision import transforms

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value

class PromptServerTqdm(tqdm):
    """
    A tqdm progress bar subclass that logs model download progress and sends updates via PromptServer.

    Args:
        *args: Positional arguments passed to the tqdm constructor.
        node_id (str): Identifier for the node associated with this progress.
        model_id (str): Identifier of the model being processed.
        log_lines (list[str]): List to append log messages to.
        **kwargs: Additional keyword arguments passed to the tqdm constructor.

    Methods:
        update(n=1):
            Advances the progress bar by n steps, logs progress messages, and sends updates to the PromptServer.
    """
    def __init__(self, *args, node_id: str, model_id: str, log_lines: list[str], **kwargs):
        super().__init__(*args, **kwargs)
        self.node_id = node_id
        self.model_id = model_id
        self.log_lines = log_lines

    def update(self, n=1):
        super().update(n)

        if self.n == 1:
            self.log_lines.append(f"Checking model cache... **{self.model_id}**")

        if self.n > 1:
            pct = self.format_dict.get('percentage', 0)
            rate = self.format_dict.get('rate_fmt', '')
            elapsed = int(self.format_dict.get('elapsed', 0))
            remaining= int(self.format_dict.get('remaining', 0))

            self.log_lines.append(
                f"_⏳ Downloading model files: {self.n}/{self.total} "
                f"({pct:.0f}% • {rate}/s • elapsed {elapsed}s • ETA {remaining}s)_"
            )

        log = "".join(self.log_lines)

        safe_send_sync("loadwd14model", {
            "value": log
        }, self.node_id)

def create_custom_tqdm(node_id: str, model_id: str, log_lines: list[str]):
    """
    Creates a custom subclass of PromptServerTqdm with pre-configured initialization parameters.

    Args:
        node_id (str): The unique identifier for the node.
        model_id (str): The identifier for the model being used.
        log_lines (list[str]): A list of log lines to be associated with the tqdm instance.

    Returns:
        type: A subclass of PromptServerTqdm with the provided parameters set in its constructor.
    """
    class CustomTqdm(PromptServerTqdm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args,
                             node_id=node_id,
                             model_id=model_id,
                             log_lines=log_lines,
                             **kwargs)
    return CustomTqdm

# region LF_LoadWD14Model
class LF_LoadWD14Model:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_id": (Input.STRING, {
                    "default": "SmilingWolf/wd-vit-large-tagger-v3",
                    "tooltip": "HuggingFace model ID."
                }),
                "architecture": (Input.STRING, {
                    "default": "vit_large_patch16_224",
                    "tooltip": "timm model architecture string for WD14 (e.g., vit_large_patch14_224, vit_huge_patch14_224, vit_base_patch16_224, vit_large_patch16_224, etc.)"
                }),
                "num_classes": (Input.INTEGER, {
                    "default": 10861,
                    "tooltip": "Number of classes/tags for WD14 model (e.g., 10861, 8965, 5400, etc.)"
                }),
                "image_size": (Input.INTEGER, {
                    "default": 448,
                    "tooltip": "Input image size for WD14 model (e.g., 448, 224, etc.)"
                }),
                "mean": (Input.STRING, {
                    "default": "0.5,0.5,0.5",
                    "tooltip": "Mean for normalization (comma-separated, e.g., 0.5,0.5,0.5)"
                }),
                "std": (Input.STRING, {
                    "default": "0.5,0.5,0.5",
                    "tooltip": "Std for normalization (comma-separated, e.g., 0.5,0.5,0.5)"
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_CODE, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "WD14 processor.",
        "WD14 model."
    )
    RETURN_NAMES = ("processor", "model")
    RETURN_TYPES = (Input.CLIP_PROCESSOR, Input.CLIP_MODEL)

    def on_exec(self, **kwargs):
        node_id: str  = kwargs.get("node_id")
        model_id: str = normalize_list_to_value(kwargs["model_id"])
        arch: str = normalize_list_to_value(kwargs.get("architecture", "vit_large_patch16_224"))
        num_classes: int = normalize_list_to_value(kwargs.get("num_classes", 10861))
        image_size: int = normalize_list_to_value(kwargs.get("image_size", 448))
        mean: str = normalize_list_to_value(kwargs.get("mean", "0.5,0.5,0.5"))
        std: str = normalize_list_to_value(kwargs.get("std", "0.5,0.5,0.5"))

        log_lines: list[str] = ["## Load WD14 Model\n\n"]
        float_mean: list[float] = [float(x) for x in mean.split(",")]
        float_std: list[float] = [float(x) for x in std.split(",")]

        CustomTqdm = create_custom_tqdm(node_id, model_id, log_lines)

        snapshot_download(
            repo_id=model_id,
            tqdm_class=CustomTqdm,
            local_dir_use_symlinks=False
        )

        try:
            model = timm.create_model(arch, pretrained=False, num_classes=num_classes)
            state_dict = timm.models.load_state_dict_from_hf(model_id)
            state_dict = {k.replace("model.", ""): v for k, v in state_dict.items()}
            model.load_state_dict(state_dict)
            model.eval()
            processor = transforms.Compose([
                transforms.Resize((image_size, image_size)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=float_mean,
                    std=float_std
                ),
            ])
            log_lines.append(f"- ✅ Model loaded! (standard timm)")
        except Exception as e:
            log_lines.append(f"- ⚠️ Standard timm load failed: {e}\n\n")
            try:
                # fallback: let timm pull both architecture & weights from HF Hub
                model = timm.create_model(f"hf_hub:{model_id}", pretrained=True, num_classes=num_classes)
                model.eval()
                # some timm versions use .pretrained_cfg, others .default_cfg
                cfg_attr = getattr(model, "pretrained_cfg", None) or getattr(model, "default_cfg", {})
                data_config = resolve_data_config(cfg_attr, model=model)
                processor = create_transform(**data_config)
                log_lines.append(f"- ✅ Model loaded from HuggingFace Hub via timm ({model_id})")
            except Exception as e:
                raise RuntimeError(f"- ❌ Failed to load model: {e}")

        safe_send_sync("loadwd14model", {
            "value": "".join(log_lines)
        }, node_id)

        return (processor, model)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LoadWD14Model": LF_LoadWD14Model,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LoadWD14Model": "Load WD14 model",
}
# endregion
