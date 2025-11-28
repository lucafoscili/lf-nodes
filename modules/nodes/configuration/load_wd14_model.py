import timm

from huggingface_hub import snapshot_download
from tqdm.auto import tqdm
from timm.data import create_transform, resolve_data_config
from torchvision import transforms
from transformers import AutoImageProcessor, AutoModelForImageClassification

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value
from ...utils.helpers.tagging import create_wd14_hf_tagger

# region PromptServerTqdm
class PromptServerTqdm(tqdm):
    """
    A tqdm progress bar subclass that logs model download progress and sends updates via PromptServer.
    """

    def __init__(self, *args, node_id: str, model_id: str, log_lines: list[str], **kwargs):
        super().__init__(*args, **kwargs)
        self.node_id = node_id
        self.model_id = model_id
        self.log_lines = log_lines

    def update(self, n=1):
        super().update(n)

        if self.n == 1:
            self.log_lines.append(f"Checking model cache... **{self.model_id}**\n")

        if self.n > 1:
            pct = self.format_dict.get("percentage", 0)
            rate = self.format_dict.get("rate_fmt", "")
            elapsed = int(self.format_dict.get("elapsed", 0))
            remaining = int(self.format_dict.get("remaining", 0))

            self.log_lines.append(
                f"_�?� Downloading model files: {self.n}/{self.total} "
                f"({pct:.0f}% �?� {rate}/s �?� elapsed {elapsed}s �?� ETA {remaining}s)_\n"
            )

        log = "".join(self.log_lines)
        safe_send_sync(
            "loadwd14model",
            {"value": log},
            self.node_id,
        )


def create_custom_tqdm(node_id: str, model_id: str, log_lines: list[str]):
    """
    Factory for a PromptServerTqdm subclass with node/model bound.
    """

    class CustomTqdm(PromptServerTqdm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, node_id=node_id, model_id=model_id, log_lines=log_lines, **kwargs)

    return CustomTqdm
# endregion

# region LF_LoadWD14Model
class LF_LoadWD14Model:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model_id": (
                    Input.STRING,
                    {
                        "default": "SmilingWolf/wd-vit-large-tagger-v3",
                        "tooltip": "HuggingFace WD14 model ID.",
                    },
                ),
                "architecture": (
                    Input.STRING,
                    {
                        "default": "vit_large_patch16_224",
                        "tooltip": "timm architecture for fallback path (kept for compatibility).",
                    },
                ),
                "num_classes": (
                    Input.INTEGER,
                    {
                        "default": 10861,
                        "tooltip": "Number of classes/tags for WD14 model (used only in timm fallback).",
                    },
                ),
                "image_size": (
                    Input.INTEGER,
                    {
                        "default": 448,
                        "tooltip": "Input image size for WD14 in timm fallback (Transformers path ignores this).",
                    },
                ),
                "mean": (
                    Input.STRING,
                    {
                        "default": "0.5,0.5,0.5",
                        "tooltip": "Mean for normalization in timm fallback (comma-separated).",
                    },
                ),
                "std": (
                    Input.STRING,
                    {
                        "default": "0.5,0.5,0.5",
                        "tooltip": "Std for normalization in timm fallback (comma-separated).",
                    },
                ),
            },
            "optional": {
                "min_probability": (
                    Input.FLOAT,
                    {
                        "default": 0.25,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.01,
                        "tooltip": "Minimum confidence to keep a tag when using the HF/timm backend.",
                    },
                ),
                "max_tags": (
                    Input.INTEGER,
                    {
                        "default": 20,
                        "min": 1,
                        "step": 1,
                        "tooltip": "Maximum number of tags to output when using the HF/timm backend.",
                    },
                ),
                "tags_to_exclude": (
                    Input.STRING,
                    {
                        "default": "",
                        "tooltip": "Tags to exclude (comma-separated; TagGUI-style escaped commas are supported).",
                    },
                ),
                "ui_widget": (
                    Input.LF_CODE,
                    {
                        "default": {},
                    },
                )
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "WD14 HF/timm tagger object (processor + model + defaults).",
    )
    RETURN_NAMES = ("tagger",)
    RETURN_TYPES = (Input.TAGGER,)

    def on_exec(self, **kwargs):
        node_id: str = kwargs.get("node_id")
        model_id: str = normalize_list_to_value(kwargs["model_id"])
        arch: str = normalize_list_to_value(kwargs.get("architecture", "vit_large_patch16_224"))
        num_classes: int = normalize_list_to_value(kwargs.get("num_classes", 10861))
        image_size: int = normalize_list_to_value(kwargs.get("image_size", 448))
        mean: str = normalize_list_to_value(kwargs.get("mean", "0.5,0.5,0.5"))
        std: str = normalize_list_to_value(kwargs.get("std", "0.5,0.5,0.5"))
        min_probability: float = float(
            normalize_list_to_value(kwargs.get("min_probability", 0.25))
        )
        max_tags: int = int(
            normalize_list_to_value(kwargs.get("max_tags", 20))
        )
        tags_to_exclude: str = normalize_list_to_value(
            kwargs.get("tags_to_exclude", "")
        ) or ""

        log_lines: list[str] = ["## Load WD14 Model\n\n"]
        float_mean: list[float] = [float(x) for x in mean.split(",")]
        float_std: list[float] = [float(x) for x in std.split(",")]

        CustomTqdm = create_custom_tqdm(node_id, model_id, log_lines)

        snapshot_download(
            repo_id=model_id,
            tqdm_class=CustomTqdm,
            local_dir_use_symlinks=False,
        )

        # Preferred path: use the official Transformers image processor + model
        # so pre-processing (resize / normalization / color space) matches the
        # reference WD14 implementation.
        try:
            processor = AutoImageProcessor.from_pretrained(model_id)
            model = AutoModelForImageClassification.from_pretrained(model_id)
            model.eval()
            # Hint to downstream helpers (build_id2label) which HF repo to
            # pull tag metadata from, so we can load selected_tags.csv when
            # config.id2label only contains generic LABEL_x entries.
            try:
                if getattr(model.config, "hf_hub_id", None) is None:
                    model.config.hf_hub_id = model_id
            except Exception:
                pass
            log_lines.append("- �o. Model loaded via Transformers (AutoImageProcessor/AutoModelForImageClassification).\n")
        except Exception as e:
            log_lines.append(f"- �s���? Transformers load failed: {e}\n\n")
            try:
                model = timm.create_model(arch, pretrained=False, num_classes=num_classes)
                state_dict = timm.models.load_state_dict_from_hf(model_id)
                state_dict = {k.replace("model.", ""): v for k, v in state_dict.items()}
                model.load_state_dict(state_dict)
                model.eval()
                processor = transforms.Compose(
                    [
                        transforms.Resize((image_size, image_size)),
                        transforms.ToTensor(),
                        transforms.Normalize(
                            mean=float_mean,
                            std=float_std,
                        ),
                    ]
                )
                log_lines.append("- �o. Model loaded! (standard timm fallback)\n")
            except Exception as e2:
                log_lines.append(f"- �s���? Standard timm load failed: {e2}\n\n")
                try:
                    # Secondary fallback: let timm pull both architecture & weights from HF Hub
                    model = timm.create_model(f"hf_hub:{model_id}", pretrained=True, num_classes=num_classes)
                    model.eval()
                    cfg_attr = getattr(model, "pretrained_cfg", None) or getattr(model, "default_cfg", {})
                    data_config = resolve_data_config(cfg_attr, model=model)
                    processor = create_transform(**data_config)
                    log_lines.append(f"- �o. Model loaded from HuggingFace Hub via timm ({model_id})\n")
                except Exception as e3:
                    raise RuntimeError(f"- �?O Failed to load model: {e3}")

        tagger = create_wd14_hf_tagger(
            model_id=model_id,
            processor=processor,
            model=model,
            min_probability=min_probability,
            max_tags=max_tags,
            tags_to_exclude=tags_to_exclude,
        )

        safe_send_sync(
            "loadwd14model",
            {
                "value": "".join(log_lines),
            },
            node_id,
        )

        return (tagger,)


# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LoadWD14Model": LF_LoadWD14Model,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LoadWD14Model": "Load WD14 model (timm)",
}
# endregion
