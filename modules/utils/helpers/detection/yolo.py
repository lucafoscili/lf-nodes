from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import ast
import json

import cv2
import numpy as np
import torch

try:
    import onnxruntime as ort
except ImportError as exc:  # pragma: no cover - handled at runtime
    ort = None  # type: ignore
    _ORT_IMPORT_ERROR = exc
else:
    _ORT_IMPORT_ERROR = None

from ..conversion import tensor_to_numpy


COCO_CLASS_NAMES: Tuple[str, ...] = (
    "person",
    "bicycle",
    "car",
    "motorcycle",
    "airplane",
    "bus",
    "train",
    "truck",
    "boat",
    "traffic light",
    "fire hydrant",
    "stop sign",
    "parking meter",
    "bench",
    "bird",
    "cat",
    "dog",
    "horse",
    "sheep",
    "cow",
    "elephant",
    "bear",
    "zebra",
    "giraffe",
    "backpack",
    "umbrella",
    "handbag",
    "tie",
    "suitcase",
    "frisbee",
    "skis",
    "snowboard",
    "sports ball",
    "kite",
    "baseball bat",
    "baseball glove",
    "skateboard",
    "surfboard",
    "tennis racket",
    "bottle",
    "wine glass",
    "cup",
    "fork",
    "knife",
    "spoon",
    "bowl",
    "banana",
    "apple",
    "sandwich",
    "orange",
    "broccoli",
    "carrot",
    "hot dog",
    "pizza",
    "donut",
    "cake",
    "chair",
    "couch",
    "potted plant",
    "bed",
    "dining table",
    "toilet",
    "tv",
    "laptop",
    "mouse",
    "remote",
    "keyboard",
    "cell phone",
    "microwave",
    "oven",
    "toaster",
    "sink",
    "refrigerator",
    "book",
    "clock",
    "vase",
    "scissors",
    "teddy bear",
    "hair drier",
    "toothbrush",
)

_NAME_TO_INDEX = {name: idx for idx, name in enumerate(COCO_CLASS_NAMES)}

_SESSION_CACHE: Dict[Tuple[str, Tuple[str, ...]], Any] = {}

DEFAULT_INPUT_SIZE = 640
_SEGMENTATION_EXTRA_COUNTS = {32, 64, 96, 128, 160, 192, 256}


def _ensure_ort() -> None:
    if ort is None:
        message = (
            "onnxruntime is required to run the LF region detector. "
            "Install it with `pip install onnxruntime` or `onnxruntime-gpu`."
        )
        raise ImportError(message) from _ORT_IMPORT_ERROR


def _select_providers(custom: Optional[Sequence[str]] = None) -> List[str]:
    _ensure_ort()
    available = list(ort.get_available_providers())
    if custom:
        selected = [provider for provider in custom if provider in available]
        if selected:
            return selected
    preferred = [
        "CUDAExecutionProvider",
        "ROCMExecutionProvider",
        "DmlExecutionProvider",
        "CoreMLExecutionProvider",
        "AzureExecutionProvider",
        "CPUExecutionProvider",
    ]
    selected = [provider for provider in preferred if provider in available]
    return selected or available


def _letterbox(
    image: np.ndarray,
    new_shape: Tuple[int, int],
    color: Tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Tuple[np.ndarray, Tuple[float, float], Tuple[float, float]]:
    h, w = image.shape[:2]
    new_h, new_w = new_shape
    if h == 0 or w == 0:
        raise ValueError("Input image must have positive dimensions.")
    r = min(new_h / h, new_w / w)
    ratio = (r, r)
    new_unpad = (int(round(w * r)), int(round(h * r)))
    dw = (new_w - new_unpad[0]) / 2.0
    dh = (new_h - new_unpad[1]) / 2.0

    if (w, h) != new_unpad:
        resized = cv2.resize(image, new_unpad, interpolation=cv2.INTER_LINEAR)
    else:
        resized = image.copy()

    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    bordered = cv2.copyMakeBorder(
        resized,
        top,
        bottom,
        left,
        right,
        borderType=cv2.BORDER_CONSTANT,
        value=color,
    )

    bordered = bordered[:new_h, :new_w]
    return bordered, ratio, (dw, dh)


def _xywh_to_xyxy(boxes: np.ndarray) -> np.ndarray:
    converted = boxes.copy()
    converted[:, 0] = boxes[:, 0] - boxes[:, 2] / 2.0
    converted[:, 1] = boxes[:, 1] - boxes[:, 3] / 2.0
    converted[:, 2] = boxes[:, 0] + boxes[:, 2] / 2.0
    converted[:, 3] = boxes[:, 1] + boxes[:, 3] / 2.0
    return converted


def _scale_boxes(
    boxes: np.ndarray,
    ratio: Tuple[float, float],
    pad: Tuple[float, float],
    original_shape: Tuple[int, int],
) -> np.ndarray:
    scaled = boxes.copy()
    gain_w, gain_h = ratio
    pad_w, pad_h = pad
    scaled[:, [0, 2]] -= pad_w
    scaled[:, [1, 3]] -= pad_h
    scaled[:, [0, 2]] /= gain_w
    scaled[:, [1, 3]] /= gain_h
    scaled[:, [0, 2]] = np.clip(scaled[:, [0, 2]], 0.0, float(original_shape[1]))
    scaled[:, [1, 3]] = np.clip(scaled[:, [1, 3]], 0.0, float(original_shape[0]))
    return scaled


def _compute_iou(box: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    inter_x1 = np.maximum(box[0], boxes[:, 0])
    inter_y1 = np.maximum(box[1], boxes[:, 1])
    inter_x2 = np.minimum(box[2], boxes[:, 2])
    inter_y2 = np.minimum(box[3], boxes[:, 3])
    inter_w = np.clip(inter_x2 - inter_x1, a_min=0.0, a_max=None)
    inter_h = np.clip(inter_y2 - inter_y1, a_min=0.0, a_max=None)
    inter_area = inter_w * inter_h

    box_area = (box[2] - box[0]) * (box[3] - box[1])
    boxes_area = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    union = box_area + boxes_area - inter_area
    iou = np.zeros_like(union, dtype=np.float32)
    np.divide(inter_area, union, out=iou, where=union > 0)
    return iou


def _nms(
    boxes: np.ndarray,
    scores: np.ndarray,
    iou_threshold: float,
    max_detections: int,
) -> List[int]:
    if boxes.size == 0:
        return []
    idxs = scores.argsort()[::-1]
    keep: List[int] = []
    while idxs.size > 0 and len(keep) < max_detections:
        current = int(idxs[0])
        keep.append(current)
        if idxs.size == 1:
            break
        rest = idxs[1:]
        ious = _compute_iou(boxes[current], boxes[rest])
        idxs = rest[ious <= iou_threshold]
    return keep


def _coerce_int(value: Any) -> Optional[int]:
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)) and float(value).is_integer():
        return int(value)
    if isinstance(value, str):
        text = value.strip()
        if text.isdigit():
            return int(text)
    return None


def _resolve_input_shape(
    session: Any,
    requested: Optional[int | Tuple[int, int] | Sequence[int]],
) -> Tuple[int, int]:
    if isinstance(requested, (list, tuple)):
        if len(requested) == 1:
            value = int(round(float(requested[0])))
            value = max(1, value)
            return value, value
        height = int(round(float(requested[0])))
        width = int(round(float(requested[1])))
        return max(1, height), max(1, width)
    if isinstance(requested, (int, float)):
        value = int(round(float(requested)))
        value = max(1, value)
        return value, value

    height = width = None
    try:
        input_meta = session.get_inputs()[0]
        shape = getattr(input_meta, "shape", None)
    except Exception:  # pragma: no cover - runtime guard
        shape = None
    if shape and len(shape) >= 4:
        height = _coerce_int(shape[2])
        width = _coerce_int(shape[3])
    if height is None or width is None:
        return DEFAULT_INPUT_SIZE, DEFAULT_INPUT_SIZE
    return max(1, height), max(1, width)


def _sanitize_labels(labels: Optional[Sequence[str]]) -> Tuple[str, ...]:
    sanitized: List[str] = []
    if labels:
        for label in labels:
            text = str(label).strip()
            if text:
                sanitized.append(text)
    return tuple(sanitized)


def _labels_from_session_metadata(session: Any) -> Optional[Tuple[str, ...]]:
    try:
        meta = session.get_modelmeta()
    except Exception:  # pragma: no cover - runtime guard
        return None
    mapping = getattr(meta, "custom_metadata_map", None) or {}
    for key in ("names", "labels", "classes"):
        raw = mapping.get(key)
        if not raw:
            continue
        parsed: Any = None
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                try:
                    parsed = ast.literal_eval(raw)
                except (ValueError, SyntaxError):
                    parsed = None
        if isinstance(parsed, dict):
            items = []
            for idx, name in parsed.items():
                try:
                    idx_int = int(idx)
                except (TypeError, ValueError):
                    continue
                label = str(name).strip()
                if label:
                    items.append((idx_int, label))
            if items:
                items.sort(key=lambda item: item[0])
                return tuple(label for _, label in items)
        if isinstance(parsed, list):
            labels = [str(item).strip() for item in parsed if str(item).strip()]
            if labels:
                return tuple(labels)
        if isinstance(raw, str):
            tokens = [segment.strip() for segment in raw.split(",") if segment.strip()]
            if tokens:
                return tuple(tokens)
    return None


def _resolve_prediction_labels(
    extra_columns: int,
    override_labels: Tuple[str, ...],
    metadata_labels: Tuple[str, ...],
) -> Tuple[Tuple[str, ...], str]:
    if override_labels:
        return override_labels, "override"
    if metadata_labels:
        return metadata_labels, "onnx_metadata"
    if extra_columns == len(COCO_CLASS_NAMES):
        return COCO_CLASS_NAMES, "coco_default"
    if extra_columns > len(COCO_CLASS_NAMES):
        diff = extra_columns - len(COCO_CLASS_NAMES)
        if diff in _SEGMENTATION_EXTRA_COUNTS:
            return COCO_CLASS_NAMES, "coco_default"
    if extra_columns <= 0:
        return ("region",), "generated"
    return tuple(f"class_{idx}" for idx in range(extra_columns)), "generated"


def _build_label_lookup(names: Sequence[str]) -> Dict[str, int]:
    lookup: Dict[str, int] = {}
    for idx, name in enumerate(names):
        key = str(name).strip().lower()
        if key and key not in lookup:
            lookup[key] = idx
    return lookup


def _resolve_class_whitelist(
    class_whitelist: Optional[Iterable[int | str]],
    name_lookup: Dict[str, int],
    num_classes: int,
) -> Optional[set[int]]:
    if not class_whitelist:
        return None
    if num_classes <= 0:
        return None
    indices: set[int] = set()
    for item in class_whitelist:
        if isinstance(item, str):
            normalized = item.strip().lower()
            if not normalized:
                continue
            if normalized.isdigit():
                idx = int(normalized)
            else:
                idx = name_lookup.get(normalized)
                if idx is None:
                    idx = _NAME_TO_INDEX.get(normalized)
                if idx is None:
                    raise ValueError(
                        f"Unknown class name '{item}'. Provide matching class labels or use numeric ids."
                    )
        else:
            idx = int(item)
        if idx < 0 or idx >= num_classes:
            raise ValueError(f"Class index {idx} out of bounds for model with {num_classes} classes.")
        indices.add(idx)
    return indices or None


# region load_yolo_session
def load_yolo_session(
    *,
    model_path: Path | str,
    providers: Optional[Sequence[str]] = None,
) -> Any:
    """
    Loads and caches a YOLO ONNX inference session for region detection.

    Args:
        model_path (Path | str): Path to the YOLO ONNX model file.
        providers (Optional[Sequence[str]], optional): List of ONNX Runtime execution providers to use. If None, defaults are selected.

    Returns:
        ort.InferenceSession: The loaded and cached ONNX inference session.

    Raises:
        FileNotFoundError: If the specified model file does not exist.
        RuntimeError: If the ONNX session fails to initialize.

    Notes:
        - The ONNX session is cached based on the model path and provider list.
        - The ONNX Runtime must be available in the environment.
        - The ONNX model file should be placed inside 'ComfyUI/models/onnx'.
    """
    _ensure_ort()
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(
            f"YOLO detector model not found at '{path}'. Place the ONNX file inside ComfyUI/models/onnx."
        )

    provider_list = _select_providers(providers)
    cache_key = (str(path.resolve()), tuple(provider_list))
    session = _SESSION_CACHE.get(cache_key)
    if session is None:
        session_options = ort.SessionOptions()
        session_options.enable_mem_pattern = False
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        try:
            session = ort.InferenceSession(
                str(path),
                sess_options=session_options,
                providers=list(provider_list),
            )
        except Exception as exc:  # pragma: no cover - defensive
            raise RuntimeError(f"Failed to initialise ONNX session: {exc}") from exc
        _SESSION_CACHE[cache_key] = session
    return session
# endregion


# region detect_regions
def detect_regions(
    image: torch.Tensor,
    *,
    session: Optional[Any] = None,
    model_path: Optional[Path | str] = None,
    providers: Optional[Sequence[str]] = None,
    input_size: Optional[int | Tuple[int, int]] = None,
    confidence_threshold: float = 0.25,
    iou_threshold: float = 0.45,
    max_detections: int = 20,
    class_whitelist: Optional[Iterable[int | str]] = None,
    class_labels: Optional[Sequence[str]] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Detects regions (bounding boxes) in an input image tensor using a YOLO-based ONNX model.

    Args:
        image (torch.Tensor): Input image tensor of shape [1, H, W, C].
        session (Optional[ort.InferenceSession], optional): Preloaded ONNX inference session. If None, a session is loaded from `model_path`.
        model_path (Optional[Path | str], optional): Path to the ONNX model file. Used if `session` is not provided.
        providers (Optional[Sequence[str]], optional): List of ONNX runtime providers to use for inference.
        input_size (Optional[int | Tuple[int, int]], optional): Model input size (height, width). If None, inferred from model.
        confidence_threshold (float, optional): Minimum confidence score to keep a detection. Defaults to 0.25.
        iou_threshold (float, optional): IoU threshold for non-maximum suppression (NMS). Defaults to 0.45.
        max_detections (int, optional): Maximum number of detections to return after NMS. Defaults to 20.
        class_whitelist (Optional[Iterable[int | str]], optional): List of class indices or names to keep. If None, all classes are kept.
        class_labels (Optional[Sequence[str]], optional): Optional override for class labels.

    Returns:
        Tuple[List[Dict[str, Any]], Dict[str, Any]]:
            - List of detection results, each as a dictionary containing bounding box coordinates, confidence scores, class information, and optional mask coefficients.
            - Context dictionary with metadata about the detection process (class labels, label source, input shape, mask prototype shape, etc.).

    Raises:
        ValueError: If the input image tensor does not have shape [1, H, W, C].
        RuntimeError: If the model output shape is unexpected or detection confidences cannot be computed.

    Notes:
        - Supports YOLO models with various output formats (with/without class scores and mask coefficients).
        - Applies non-maximum suppression (NMS) to filter overlapping detections.
        - Optionally restricts detections to a whitelist of classes.
    """
    if image.ndim != 4 or image.shape[0] != 1:
        raise ValueError("Expected image tensor with shape [1, H, W, C].")

    session = session or load_yolo_session(model_path=model_path, providers=providers)

    override_labels = _sanitize_labels(class_labels)
    metadata_labels: Tuple[str, ...] = ()
    if not override_labels:
        metadata_labels = _sanitize_labels(_labels_from_session_metadata(session))

    input_shape = _resolve_input_shape(session, input_size)

    np_image = tensor_to_numpy(image, threeD=True, dtype=np.float32)
    orig_h, orig_w = np_image.shape[:2]
    processed, ratio, pad = _letterbox(np_image, input_shape)

    input_tensor = processed.transpose(2, 0, 1)
    input_tensor = np.expand_dims(input_tensor, axis=0).astype(np.float32)
    input_tensor = np.ascontiguousarray(input_tensor)

    input_name = session.get_inputs()[0].name
    output_names = [output.name for output in session.get_outputs()]
    raw_outputs = session.run(output_names, {input_name: input_tensor})
    predictions = raw_outputs[0]
    mask_proto = raw_outputs[1] if len(raw_outputs) > 1 else None

    if predictions.ndim != 3:
        raise RuntimeError(f"Unexpected YOLO output shape: {predictions.shape}")

    predictions = predictions[0]
    if predictions.shape[0] <= predictions.shape[1] and predictions.shape[0] <= 8:
        predictions = predictions.transpose(1, 0)

    if predictions.shape[1] < 4:
        raise RuntimeError(f"YOLO output has too few coordinates: {predictions.shape}")

    num_columns = predictions.shape[1]
    boxes_xywh = predictions[:, :4]
    objectness = None
    class_scores = None
    confidences = None
    class_probabilities = None
    class_ids = None
    mask_coefficients = None
    label_source = "generated"
    active_labels: Tuple[str, ...]

    if num_columns == 4:
        objectness = np.ones(len(predictions), dtype=np.float32)
        confidences = objectness.copy()
        class_probabilities = objectness.copy()
        class_ids = np.zeros(len(predictions), dtype=int)
        active_labels, label_source = _resolve_prediction_labels(1, override_labels, metadata_labels)
        if not active_labels:
            active_labels = ("region",)
    elif num_columns == 5:
        objectness = predictions[:, 4]
        confidences = objectness.copy()
        class_probabilities = objectness.copy()
        class_ids = np.zeros(len(predictions), dtype=int)
        active_labels, label_source = _resolve_prediction_labels(1, override_labels, metadata_labels)
        if not active_labels:
            active_labels = ("region",)
    else:
        objectness = predictions[:, 4]
        extra_columns = num_columns - 5
        active_labels, label_source = _resolve_prediction_labels(extra_columns, override_labels, metadata_labels)
        if not active_labels:
            if extra_columns > 0:
                active_labels = tuple(f"class_{idx}" for idx in range(extra_columns))
            else:
                active_labels = ("region",)
        class_columns = min(len(active_labels), extra_columns) if extra_columns > 0 else len(active_labels)
        if class_columns == 0 and extra_columns > 0:
            class_columns = extra_columns
            active_labels = tuple(f"class_{idx}" for idx in range(class_columns))
        if class_columns > 0 and len(active_labels) > class_columns:
            active_labels = active_labels[:class_columns]
        class_scores = predictions[:, 5 : 5 + class_columns] if class_columns > 0 else None
        mask_columns = max(0, extra_columns - class_columns)
        if mask_columns > 0:
            mask_coefficients = predictions[:, 5 + class_columns : 5 + class_columns + mask_columns]
        if class_scores is not None and class_scores.size > 0:
            scores = class_scores * objectness[:, None]
            class_ids = scores.argmax(axis=1)
            confidences = scores[np.arange(scores.shape[0]), class_ids]
            class_probabilities = class_scores[np.arange(class_scores.shape[0]), class_ids]
        else:
            confidences = objectness.copy()
            class_probabilities = objectness.copy()
            class_ids = np.zeros(len(predictions), dtype=int)
    if predictions.shape[1] in (4, 5):
        active_labels = _sanitize_labels(active_labels) or ("region",)

    if confidences is None or class_ids is None or class_probabilities is None:
        raise RuntimeError("Failed to compute detection confidences.")

    name_lookup = _build_label_lookup(active_labels)
    effective_class_count = max(1, len(active_labels))
    whitelist_indices = _resolve_class_whitelist(class_whitelist, name_lookup, effective_class_count)

    keep_mask = confidences >= confidence_threshold
    if whitelist_indices is not None:
        keep_mask &= np.isin(class_ids, list(whitelist_indices))

    boxes_xywh = boxes_xywh[keep_mask]
    confidences = confidences[keep_mask]
    class_ids = class_ids[keep_mask]
    objectness = objectness[keep_mask] if objectness is not None else None
    class_probabilities = class_probabilities[keep_mask] if class_probabilities is not None else None
    mask_coefficients = mask_coefficients[keep_mask] if mask_coefficients is not None else None

    context: Dict[str, Any] = {
        "class_labels": list(active_labels),
        "label_source": label_source,
        "input_shape": {"height": int(input_shape[0]), "width": int(input_shape[1])},
        "mask_coefficient_count": int(mask_coefficients.shape[1]) if mask_coefficients is not None else 0,
    }
    if mask_proto is not None:
        context["mask_prototype_shape"] = [int(dim) for dim in mask_proto.shape]

    if boxes_xywh.size == 0:
        return [], context

    boxes_xyxy = _xywh_to_xyxy(boxes_xywh)
    boxes_xyxy = _scale_boxes(boxes_xyxy, ratio, pad, (orig_h, orig_w))
    boxes_xyxy[:, [0, 2]] = np.clip(boxes_xyxy[:, [0, 2]], 0.0, float(orig_w - 1))
    boxes_xyxy[:, [1, 3]] = np.clip(boxes_xyxy[:, [1, 3]], 0.0, float(orig_h - 1))

    keep_indices = _nms(boxes_xyxy, confidences, iou_threshold, max_detections)

    results: List[Dict[str, Any]] = []
    for order, idx in enumerate(keep_indices):
        x1, y1, x2, y2 = boxes_xyxy[idx]
        width = max(0.0, float(x2 - x1))
        height = max(0.0, float(y2 - y1))
        area = width * height
        cls = int(class_ids[idx])
        if 0 <= cls < len(active_labels):
            label = active_labels[cls]
        elif 0 <= cls < len(COCO_CLASS_NAMES):
            label = COCO_CLASS_NAMES[cls]
        else:
            label = f"class_{cls}"
        result = {
            "id": f"region_{order}",
            "index": order,
            "bbox": [int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))],
            "bbox_float": [float(x1), float(y1), float(x2), float(y2)],
            "bbox_xywh": [
                float(boxes_xywh[idx][0]),
                float(boxes_xywh[idx][1]),
                float(boxes_xywh[idx][2]),
                float(boxes_xywh[idx][3]),
            ],
            "width": width,
            "height": height,
            "area": area,
            "confidence": float(confidences[idx]),
            "confidence_object": float(objectness[idx]) if objectness is not None else float(confidences[idx]),
            "confidence_class": float(class_probabilities[idx]) if class_probabilities is not None else float(confidences[idx]),
            "class_id": cls,
            "label": label,
        }
        if mask_coefficients is not None and mask_coefficients.shape[1] > 0:
            result["mask_coefficients"] = mask_coefficients[idx].astype(float).tolist()
        results.append(result)

    return results, context
# endregion
