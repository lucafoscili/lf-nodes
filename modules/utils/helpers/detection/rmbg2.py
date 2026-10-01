from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator

import folder_paths
import numpy as np
import torch
import torch.nn.functional as F
from comfy import model_management
from PIL import Image


_REQUIRED_FILES = ("config.json", "birefnet.py", "BiRefNet_config.py", "model.safetensors")


def _load_model(model_dir: Path):
    missing = [name for name in _REQUIRED_FILES if not (model_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(
            f"RMBG-2.0 local model is incomplete at {model_dir}: missing {', '.join(missing)}. "
            "Install the trusted RMBG-2.0 model package there; LF does not download it."
        )
    config = json.loads((model_dir / "config.json").read_text(encoding="utf-8"))
    if config.get("bb_pretrained") is not False:
        raise ValueError("RMBG-2.0 config.json must set bb_pretrained to false for local-only loading.")

    try:
        from safetensors.torch import load_model
        from transformers.dynamic_module_utils import get_class_from_dynamic_module

        model_class = get_class_from_dynamic_module(
            "birefnet.BiRefNet", str(model_dir), local_files_only=True
        )
        config_class = get_class_from_dynamic_module(
            "BiRefNet_config.BiRefNetConfig", str(model_dir), local_files_only=True
        )
        # The package replaces its HF config with an architecture Config, which
        # Transformers 5's from_pretrained conversion pipeline cannot consume.
        model = model_class(config=config_class(bb_pretrained=False))
        load_model(model, str(model_dir / "model.safetensors"), strict=True, device="cpu")
    except ImportError as exc:
        raise RuntimeError(
            "RMBG-2.0 requires transformers, safetensors, timm, torchvision and kornia "
            f"in ComfyUI's Python environment: {exc}"
        ) from exc
    return model


@contextmanager
def rmbg2_session(model_dir: Path | None = None) -> Iterator[Callable[[Image.Image], Image.Image]]:
    """Load one local model for an invocation; yield an RGB-to-L mask callable."""
    if model_dir is None:
        model_dir = Path(folder_paths.models_dir) / "RMBG" / "RMBG-2.0"
    model = _load_model(Path(model_dir))
    try:
        model.eval()
        model.to(dtype=torch.float32)
        device = model_management.get_torch_device()
        if device.type != "cpu":
            model_management.free_memory(
                model_management.module_size(model) + model_management.minimum_inference_memory(),
                device,
            )
        model.to(device)

        def predict_mask(image: Image.Image) -> Image.Image:
            rgb = image.convert("RGB").resize((1024, 1024), Image.Resampling.BILINEAR)
            pixels = np.array(rgb, dtype=np.float32) / 255.0
            pixels = (pixels - np.array((0.485, 0.456, 0.406), dtype=np.float32)) / np.array(
                (0.229, 0.224, 0.225), dtype=np.float32
            )
            inputs = torch.from_numpy(pixels).permute(2, 0, 1).contiguous().unsqueeze(0).to(device)
            # Match the package's final segmentation head and VNCCS's mask resize.
            probabilities = model(inputs)[-1].sigmoid().detach().cpu()
            alpha = F.interpolate(
                probabilities, size=(image.height, image.width), mode="bilinear", align_corners=False
            )[0, 0]
            return Image.fromarray((alpha.numpy() * 255.0).astype(np.uint8))

        yield predict_mask
    finally:
        try:
            model.to(torch.device("cpu"))
        finally:
            model = None
            model_management.soft_empty_cache()


__all__ = ["rmbg2_session"]
