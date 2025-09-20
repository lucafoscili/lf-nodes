from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

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

from .helpers import tensor_to_numpy

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


def load_yolo_session(
    *,
    model_path: Path | str,
    providers: Optional[Sequence[str]] = None,
) -> "ort.InferenceSession":
    """Load (and cache) the YOLO ONNX session used for region detection."""
    _ensure_ort()
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(
            f"YOLO detector model not found at '{path}'. Place the ONNX file inside ComfyUI/models/ultralytics/bbox or segm."
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


def _resolve_class_whitelist(class_whitelist: Optional[Iterable[int | str]]) -> Optional[set[int]]:
    if not class_whitelist:
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
                match = _NAME_TO_INDEX.get(normalized)
                if match is None:
                    raise ValueError(f"Unknown class name '{item}' for COCO model.")
                idx = match
        else:
            idx = int(item)
        if idx < 0 or idx >= len(COCO_CLASS_NAMES):
            raise ValueError(f"Class index {idx} out of bounds for COCO model.")
        indices.add(idx)
    return indices


def detect_regions(
    image: torch.Tensor,
    *,
    session: Optional["ort.InferenceSession"] = None,
    model_path: Optional[Path | str] = None,
    providers: Optional[Sequence[str]] = None,
    input_size: int = 640,
    confidence_threshold: float = 0.25,
    iou_threshold: float = 0.45,
    max_detections: int = 20,
    class_whitelist: Optional[Iterable[int | str]] = None,
) -> List[Dict[str, Any]]:
    """Run YOLO object detection on a single Comfy image tensor."""
    if image.ndim != 4 or image.shape[0] != 1:
        raise ValueError("Expected image tensor with shape [1, H, W, C].")

    session = session or load_yolo_session(model_path=model_path, providers=providers)
    whitelist = _resolve_class_whitelist(class_whitelist)

    np_image = tensor_to_numpy(image, threeD=True, dtype=np.float32)
    orig_h, orig_w = np_image.shape[:2]
    processed, ratio, pad = _letterbox(np_image, (input_size, input_size))

    input_tensor = processed.transpose(2, 0, 1)
    input_tensor = np.expand_dims(input_tensor, axis=0).astype(np.float32)
    input_tensor = np.ascontiguousarray(input_tensor)

    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    predictions = session.run([output_name], {input_name: input_tensor})[0]

    if predictions.ndim != 3:
        raise RuntimeError(f"Unexpected YOLO output shape: {predictions.shape}")

    predictions = predictions[0]
    if predictions.shape[0] <= predictions.shape[1] and predictions.shape[0] <= 8:
        predictions = predictions.transpose(1, 0)

    if predictions.shape[1] < 4:
        raise RuntimeError(f"YOLO output has too few coordinates: {predictions.shape}")

    boxes_xywh = predictions[:, :4]
    objectness = None
    class_scores = None
    confidences = None
    class_probabilities = None
    class_ids = None

    if predictions.shape[1] == 4:
        objectness = np.ones(len(predictions), dtype=np.float32)
        confidences = objectness.copy()
        class_probabilities = objectness.copy()
        class_ids = np.zeros(len(predictions), dtype=int)
    elif predictions.shape[1] == 5:
        objectness = predictions[:, 4]
        confidences = objectness.copy()
        class_probabilities = objectness.copy()
        class_ids = np.zeros(len(predictions), dtype=int)
    else:
        objectness = predictions[:, 4]
        class_scores = predictions[:, 5:]
        scores = class_scores * objectness[:, None]
        class_ids = scores.argmax(axis=1)
        confidences = scores[np.arange(scores.shape[0]), class_ids]
        class_probabilities = class_scores[np.arange(class_scores.shape[0]), class_ids]

    keep_mask = confidences >= confidence_threshold
    if whitelist is not None:
        keep_mask &= np.isin(class_ids, list(whitelist))

    boxes_xywh = boxes_xywh[keep_mask]
    confidences = confidences[keep_mask]
    class_ids = class_ids[keep_mask]
    objectness = objectness[keep_mask] if objectness is not None else None
    class_probabilities = class_probabilities[keep_mask] if class_probabilities is not None else None

    if boxes_xywh.size == 0:
        return []

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
        label = COCO_CLASS_NAMES[cls] if 0 <= cls < len(COCO_CLASS_NAMES) else f"class_{cls}"
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
        results.append(result)

    return results

