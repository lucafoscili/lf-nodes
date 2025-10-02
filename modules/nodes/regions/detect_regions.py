from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, SELECTION_STRATEGY_COMBO
from ...utils.helpers.detection import append_compare_entry, build_overlay, detect_regions, load_label_map, load_yolo_session, parse_class_filter, parse_class_labels, select_region
from ...utils.helpers.logic import normalize_input_image, normalize_json_input, normalize_list_to_value
from ...utils.helpers.temp_cache import TempFileCache

# region LF_DetectRegions
class LF_DetectRegions:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Image tensor or batch to analyse."
                }),
                "model_path": (Input.ONNX_PATH, {
                    "default": "",
                    "tooltip": "Absolute path to a YOLO ONNX model (use LF_ONNXSelector; files live under ComfyUI/models/onnx).",
                }),
            },
            "optional": {
                "model_label": (Input.ONNX_DETECTOR, {
                    "default": "",
                    "tooltip": "Optional label reported in metadata; defaults to the filename.",
                }),
                "confidence_threshold": (Input.FLOAT, {
                    "default": 0.25,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Discard detections below this confidence score.",
                }),
                "iou_threshold": (Input.FLOAT, {
                    "default": 0.45,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Intersection-over-Union threshold for non-maximum suppression.",
                }),
                "max_regions": (Input.INTEGER, {
                    "default": 5,
                    "min": 1,
                    "max": 100,
                    "tooltip": "Maximum number of regions to keep per image after NMS.",
                }),
                "class_filter": (Input.STRING, {
                    "default": "",
                    "tooltip": "Optional comma-separated list of class names or IDs to keep.",
                }),
                "class_labels": (Input.STRING, {
                    "default": "",
                    "tooltip": "Optional class label override (comma, newline or JSON).",
                }),
                "preferred_label": (Input.STRING, {
                    "default": "",
                    "tooltip": "First region whose label matches this string will be selected.",
                }),
                "selection_strategy": (SELECTION_STRATEGY_COMBO, {
                    "default": "confidence",
                    "tooltip": "Fallback strategy when auto-selecting a region.",
                }),
                "select_index": (Input.INTEGER, {
                    "default": -1,
                    "min": -1,
                    "max": 256,
                    "tooltip": "Manually select the Nth region (after filtering). -1 chooses automatically.",
                }),
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {},
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = (True, False, False, False, False, False, False, False, False, False, False, False)
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("region_meta", "region_meta_list")
    RETURN_TYPES = (Input.REGION_META, Input.REGION_META)

    def on_exec(self, **kwargs):
        self._temp_cache.cleanup()
        
        node_id = kwargs.get("node_id")
        images = normalize_input_image(kwargs["image"])

        model_path_raw = normalize_list_to_value(kwargs.get("model_path"))
        model_label_raw = normalize_list_to_value(kwargs.get("model_label", "")) or ""
        if not model_path_raw:
            raise ValueError("Provide a YOLO ONNX model path (use LF_ONNXSelector).")

        model_path = Path(str(model_path_raw)).expanduser()
        if not model_path.is_file():
            raise FileNotFoundError(
                f"YOLO detector model not found at '{model_path}'. Place the ONNX file under ComfyUI/models/onnx."
            )
        model_label = model_label_raw or model_path.name

        confidence_threshold = float(normalize_list_to_value(kwargs.get("confidence_threshold", 0.25)))
        iou_threshold = float(normalize_list_to_value(kwargs.get("iou_threshold", 0.45)))
        max_regions = int(normalize_list_to_value(kwargs.get("max_regions", 5)))
        max_regions = max(1, min(max_regions, 512))

        raw_filter = normalize_list_to_value(kwargs.get("class_filter", "")) or ""
        class_whitelist = parse_class_filter(str(raw_filter))

        label_input_raw = normalize_list_to_value(kwargs.get("class_labels", "")) or ""
        manual_label_override = parse_class_labels(label_input_raw)
        sidecar_labels = load_label_map(model_path) if not manual_label_override else None
        label_override = manual_label_override or sidecar_labels
        label_override_source = "manual" if manual_label_override else ("sidecar" if sidecar_labels else None)

        preferred_label_raw = normalize_list_to_value(kwargs.get("preferred_label", "")) or ""
        preferred_label_clean = preferred_label_raw.strip()
        preferred_label = preferred_label_clean.lower() or None

        selection_strategy = normalize_list_to_value(kwargs.get("selection_strategy", "confidence")) or "confidence"
        selection_strategy = str(selection_strategy).lower()
        if selection_strategy not in ("confidence", "area"):
            selection_strategy = "confidence"

        select_index = int(normalize_list_to_value(kwargs.get("select_index", -1)))

        ui_widget = normalize_json_input(kwargs.get("ui_widget", {}))
        nodes: List[dict] = ui_widget.get("nodes", []) if isinstance(ui_widget, dict) else []
        dataset = {"nodes": nodes}

        session = load_yolo_session(model_path=model_path)
        providers = session.get_providers()

        region_meta_list: List[dict] = []
        last_runtime: Optional[Dict[str, Any]] = None

        for index, image in enumerate(images):
            detections, runtime_info = detect_regions(
                image,
                session=session,
                confidence_threshold=confidence_threshold,
                iou_threshold=iou_threshold,
                max_detections=max_regions,
                class_whitelist=class_whitelist,
                class_labels=label_override,
            )
            last_runtime = runtime_info

            enriched: List[dict] = []
            for order, detection in enumerate(detections):
                region = dict(detection)
                region_id = f"region_{index}_{order}"
                region["detector_id"] = detection.get("id")
                region["id"] = region_id
                region["image_index"] = index
                enriched.append(region)

            selected = select_region(enriched, select_index, selection_strategy, preferred_label)
            selected_copy = dict(selected) if selected else None

            for region in enriched:
                region["is_selected"] = bool(selected and region["id"] == selected["id"])

            if selected_copy is not None:
                selected_copy["is_selected"] = True

            overlay = build_overlay(image, enriched)
            append_compare_entry(image, overlay, nodes, index, temp_cache=self._temp_cache)

            input_shape_info = runtime_info.get("input_shape") if runtime_info else None
            input_size_value = None
            if isinstance(input_shape_info, dict):
                height = input_shape_info.get("height")
                width = input_shape_info.get("width")
                if isinstance(height, int) and isinstance(width, int) and height == width:
                    input_size_value = height

            detector_info = {
                "model_label": model_label,
                "model_path": str(model_path),
                "model_name": model_path.name,
                "providers": providers,
                "input_shape": input_shape_info,
                "input_size": input_size_value,
                "class_labels": runtime_info.get("class_labels") if runtime_info else None,
                "class_labels_source": runtime_info.get("label_source") if runtime_info else None,
                "mask_coefficient_count": runtime_info.get("mask_coefficient_count") if runtime_info else None,
                "mask_prototype_shape": runtime_info.get("mask_prototype_shape") if runtime_info else None,
                "label_override_source": label_override_source,
            }

            settings = {
                "confidence_threshold": confidence_threshold,
                "iou_threshold": iou_threshold,
                "max_regions": max_regions,
                "class_filter": class_whitelist,
                "class_filter_raw": raw_filter or None,
                "class_labels_override": manual_label_override,
                "preferred_label": preferred_label_clean,
                "selection_strategy": selection_strategy,
                "select_index": select_index,
            }

            meta = {
                "image_index": index,
                "image_height": int(image.shape[1]),
                "image_width": int(image.shape[2]),
                "regions": enriched,
                "selected_region": selected_copy,
                "selected_index": selected_copy.get("index") if selected_copy else None,
                "detector": detector_info,
                "settings": settings,
                "count": len(enriched),
            }
            region_meta_list.append(meta)

        PromptServer.instance.send_sync(
            f"{EVENT_PREFIX}detectregions",
            {"node": node_id, "dataset": dataset},
        )

        if region_meta_list:
            region_meta = region_meta_list[0]
        else:
            runtime_info = last_runtime or {}
            input_shape_info = runtime_info.get("input_shape") if runtime_info else None
            input_size_value = None
            if isinstance(input_shape_info, dict):
                height = input_shape_info.get("height")
                width = input_shape_info.get("width")
                if isinstance(height, int) and isinstance(width, int) and height == width:
                    input_size_value = height
            detector_info = {
                "model_label": model_label,
                "model_path": str(model_path),
                "model_name": model_path.name,
                "providers": providers,
                "input_shape": input_shape_info,
                "input_size": input_size_value,
                "class_labels": runtime_info.get("class_labels"),
                "class_labels_source": runtime_info.get("label_source"),
                "mask_coefficient_count": runtime_info.get("mask_coefficient_count"),
                "mask_prototype_shape": runtime_info.get("mask_prototype_shape"),
                "label_override_source": label_override_source,
            }
            settings = {
                "confidence_threshold": confidence_threshold,
                "iou_threshold": iou_threshold,
                "max_regions": max_regions,
                "class_filter": class_whitelist,
                "class_filter_raw": raw_filter or None,
                "class_labels_override": manual_label_override,
                "preferred_label": preferred_label_clean,
                "selection_strategy": selection_strategy,
                "select_index": select_index,
            }
            region_meta = {
                "image_index": 0,
                "image_height": None,
                "image_width": None,
                "regions": [],
                "selected_region": None,
                "selected_index": None,
                "detector": detector_info,
                "settings": settings,
                "count": 0,
            }

        return (region_meta, region_meta_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_DetectRegions": LF_DetectRegions,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_DetectRegions": "Detect Regions (YOLO)",
}
# endregion