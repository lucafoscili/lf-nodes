import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple, Union

import numpy as np
import torch

from ..conversion import tensor_to_pil
from .tag_image import tag_image

try:
    import onnxruntime as ort
except ImportError as _exc:  # pragma: no cover - handled at runtime
    ort = None  # type: ignore[assignment]
    _ORT_IMPORT_ERROR = _exc
else:  # pragma: no cover - import-time side effect
    _ORT_IMPORT_ERROR = None

try:
    from huggingface_hub import hf_hub_download
except Exception as _hf_exc:  # pragma: no cover - surfaced at runtime
    hf_hub_download = None  # type: ignore[assignment]
    _HF_IMPORT_ERROR = _hf_exc
else:
    _HF_IMPORT_ERROR = None

from PIL import Image as PilImage

KAOMOJIS: List[str] = [
    "0_0",
    "(o)_(o)",
    "+_+",
    "+_-",
    "._.",
    "<o>_<o>",
    "<|>_<|>",
    "=_=",
    ">_<",
    "3_3",
    "6_9",
    ">_o",
    "@_@",
    "^_^",
    "o_o",
    "u_u",
    "x_x",
    "|_|",
    "||_||",
]

# region Helpers
def _ensure_ort() -> None:
    """
    Ensure that onnxruntime is available before running WD14 ONNX inference.

    Raises:
        ImportError: If onnxruntime is not installed.
    """
    if ort is None:
        message = (
            "onnxruntime is required for WD14 ONNX tagging. "
            "Install it with `pip install onnxruntime` or `onnxruntime-gpu`."
        )
        raise ImportError(message) from _ORT_IMPORT_ERROR

def _ensure_hf() -> None:
    """
    Ensure that huggingface_hub is available before downloading WD14 assets.

    Raises:
        ImportError: If huggingface_hub is not installed.
    """
    if hf_hub_download is None:
        message = (
            "huggingface_hub is required to download WD14 ONNX models. "
            "Install it with `pip install huggingface_hub`."
        )
        raise ImportError(message) from _HF_IMPORT_ERROR

def get_tags_to_exclude(tags_to_exclude_string: str) -> List[str]:
    """
    Parse a TagGUI-compatible tags_to_exclude string into a list of tags.

    Commas can be escaped with a backslash (\\,) to be part of a tag.
    """
    if not tags_to_exclude_string or not tags_to_exclude_string.strip():
        return []
    tags = re.split(r"(?<!\\),", tags_to_exclude_string)
    return [tag.strip().replace(r"\,", ",") for tag in tags if tag.strip()]


def _load_onnx_and_tags(model_id: str) -> Tuple["ort.InferenceSession", List[str], List[int], List[int], List[int]]:
    """
    Load WD14 ONNX model and selected_tags.csv either from a local directory or HuggingFace Hub.
    """
    _ensure_ort()
    _ensure_hf()

    model_dir = Path(model_id)

    model_path = model_dir / "model.onnx"
    if not model_path.is_file():
        model_path = Path(
            hf_hub_download(model_id, filename="model.onnx")  # type: ignore[arg-type]
        )

    tags_path = model_dir / "selected_tags.csv"
    if not tags_path.is_file():
        tags_path = Path(
            hf_hub_download(model_id, filename="selected_tags.csv")  # type: ignore[arg-type]
        )

    session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])

    tags: List[str] = []
    rating_indices: List[int] = []
    general_indices: List[int] = []
    character_indices: List[int] = []

    with tags_path.open("r", encoding="utf-8") as tags_file:
        reader = csv.DictReader(tags_file)
        for index, line in enumerate(reader):
            tag = line.get("name", "")
            if tag not in KAOMOJIS:
                tag = tag.replace("_", " ")
            tags.append(tag)

            category = line.get("category", "")
            if category == "9":
                rating_indices.append(index)
            elif category == "0":
                general_indices.append(index)
            elif category == "4":
                character_indices.append(index)

    return session, tags, rating_indices, general_indices, character_indices

def _preprocess_image_for_wd14(
    image: Union[torch.Tensor, PilImage.Image],
    session: "ort.InferenceSession",
) -> np.ndarray:
    """
    Preprocess an LF image tensor or PIL image into a WD14 ONNX input array.
    """
    if isinstance(image, torch.Tensor):
        pil_image = tensor_to_pil(image)
    else:
        pil_image = image

    if pil_image.mode not in ("RGB", "RGBA"):
        pil_image = pil_image.convert("RGBA")
    if pil_image.mode != "RGBA":
        pil_image = pil_image.convert("RGBA")

    canvas = PilImage.new("RGBA", pil_image.size, (255, 255, 255, 255))
    canvas.alpha_composite(pil_image)
    pil_image = canvas.convert("RGB")

    max_dimension = max(pil_image.size)
    square_canvas = PilImage.new("RGB", (max_dimension, max_dimension), (255, 255, 255))
    horizontal_padding = (max_dimension - pil_image.width) // 2
    vertical_padding = (max_dimension - pil_image.height) // 2
    square_canvas.paste(pil_image, (horizontal_padding, vertical_padding))

    input_shape = session.get_inputs()[0].shape
    input_dim: Optional[int] = None
    if isinstance(input_shape, Sequence) and len(input_shape) == 4:
        dim_candidate = input_shape[2]
        if isinstance(dim_candidate, int):
            input_dim = dim_candidate

    if isinstance(input_dim, int) and max_dimension != input_dim and input_dim > 0:
        square_canvas = square_canvas.resize(
            (input_dim, input_dim),
            resample=PilImage.Resampling.BICUBIC,
        )

    array = np.array(square_canvas, dtype=np.float32)
    array = array[:, :, ::-1]  # RGB -> BGR
    array = np.expand_dims(array, axis=0)
    return array
# endregion

# region Tagger Classes
@dataclass
class Wd14OnnxTagger:
    """
    Lightweight wrapper around a WD14 ONNX model and its tag metadata.

    This object is what flows through the TAGGER socket between nodes.
    """

    model_id: str
    inference_session: "ort.InferenceSession"
    tags: List[str]
    rating_tags_indices: List[int]
    general_tags_indices: List[int]
    character_tags_indices: List[int]
    min_probability: float = 0.4
    max_tags: int = 30
    tags_to_exclude: str = ""

    backend: str = "wd14-onnx"

    def tag(
        self,
        image: Union[torch.Tensor, PilImage.Image],
        *,
        min_probability: Optional[float] = None,
        max_tags: Optional[int] = None,
        tags_to_exclude: Optional[str] = None,
    ) -> List[Tuple[str, float]]:
        """
        Generate (tag, probability) pairs for a single image.
        """
        array = _preprocess_image_for_wd14(image, self.inference_session)

        input_name = self.inference_session.get_inputs()[0].name
        output_name = self.inference_session.get_outputs()[0].name
        probabilities = self.inference_session.run(
            [output_name], {input_name: array}
        )[0][0].astype(np.float32)

        tags = [
            tag
            for index, tag in enumerate(self.tags)
            if index not in self.rating_tags_indices
        ]
        probabilities = np.array(
            [
                probability
                for index, probability in enumerate(probabilities)
                if index not in self.rating_tags_indices
            ],
            dtype=np.float32,
        )

        min_prob = float(min_probability) if min_probability is not None else float(self.min_probability)
        max_k = int(max_tags) if max_tags is not None else int(self.max_tags)
        exclude_raw = tags_to_exclude if tags_to_exclude is not None else self.tags_to_exclude
        exclude_list = {t.lower() for t in get_tags_to_exclude(exclude_raw)}

        tags_and_probabilities: List[Tuple[str, float]] = []
        for tag, probability in zip(tags, probabilities):
            prob_value = float(probability)
            if prob_value < min_prob:
                continue
            if tag.lower() in exclude_list:
                continue
            tags_and_probabilities.append((tag, prob_value))

        tags_and_probabilities.sort(key=lambda x: x[1], reverse=True)
        return tags_and_probabilities[:max_k]

def create_wd14_onnx_tagger(
    model_id: str,
    *,
    min_probability: float = 0.4,
    max_tags: int = 30,
    tags_to_exclude: str = "",
) -> Wd14OnnxTagger:
    """
    Factory for a Wd14OnnxTagger with TagGUI-compatible defaults.
    """
    session, tags, rating_indices, general_indices, character_indices = _load_onnx_and_tags(model_id)
    return Wd14OnnxTagger(
        model_id=model_id,
        inference_session=session,
        tags=tags,
        rating_tags_indices=rating_indices,
        general_tags_indices=general_indices,
        character_tags_indices=character_indices,
        min_probability=float(min_probability),
        max_tags=int(max_tags),
        tags_to_exclude=str(tags_to_exclude or ""),
    )

__all__ = [
    "Wd14OnnxTagger",
    "Wd14HfTagger",
    "create_wd14_onnx_tagger",
    "create_wd14_hf_tagger",
    "get_tags_to_exclude",
]

@dataclass
class Wd14HfTagger:
    """
    Wrapper around a HF / timm WD14 model and its processor, exposing the same tag() API as the ONNX tagger.
    """

    model_id: str
    processor: object
    model: object
    min_probability: float = 0.25
    max_tags: int = 20
    tags_to_exclude: str = ""
    remove_underscore: bool = True

    backend: str = "wd14-hf"

    def tag(
        self,
        image: Union[torch.Tensor, PilImage.Image],
        *,
        min_probability: Optional[float] = None,
        max_tags: Optional[int] = None,
        tags_to_exclude: Optional[str] = None,
    ) -> List[Tuple[str, float]]:
        """
        Generate (tag, probability) pairs for a single image using the HF/timm backend.
        """
        if not isinstance(image, torch.Tensor):
            raise TypeError("Wd14HfTagger.tag expects a torch.Tensor image.")

        min_prob = float(min_probability) if min_probability is not None else float(self.min_probability)
        max_k = int(max_tags) if max_tags is not None else int(self.max_tags)
        exclude_raw = tags_to_exclude if tags_to_exclude is not None else self.tags_to_exclude
        exclude_list = {t.lower() for t in get_tags_to_exclude(exclude_raw)}

        pairs = tag_image(
            processor=self.processor,
            model=self.model,
            image_tensor=image,
            threshold=min_prob,
            top_k=max_k,
            remove_underscore=self.remove_underscore,
            blacklist=list(exclude_list),
        )
        return pairs

def create_wd14_hf_tagger(
    model_id: str,
    processor: object,
    model: object,
    *,
    min_probability: float = 0.25,
    max_tags: int = 20,
    tags_to_exclude: str = "",
    remove_underscore: bool = True,
) -> Wd14HfTagger:
    """
    Factory for a Wd14HfTagger that aligns with the TAGGER interface and defaults of the legacy HF/timm path.
    """
    return Wd14HfTagger(
        model_id=model_id,
        processor=processor,
        model=model,
        min_probability=float(min_probability),
        max_tags=int(max_tags),
        tags_to_exclude=str(tags_to_exclude or ""),
        remove_underscore=bool(remove_underscore),
    )
# endregion
