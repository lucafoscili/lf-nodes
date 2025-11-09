from pathlib import Path
from typing import Dict, List

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.detection import discover_ultralytics_models
from ...utils.helpers.logic import normalize_json_input, normalize_list_to_value
from ...utils.helpers.ui import create_history_node
from ...utils.helpers.comfy import safe_send_sync


class LF_ONNXSelector:
    @classmethod
    def _available_models(cls) -> Dict[str, Path]:
        return discover_ultralytics_models()

    @classmethod
    def INPUT_TYPES(cls):
        models = cls._available_models()
        choices: List[str] = sorted(models.keys()) if models else ["-- no models found --"]
        default_choice = choices[0] if choices else "-- no models found --"
        return {
            "required": {
                "detector": (choices, {
                    "default": default_choice,
                    "tooltip": "ONNX model discovered in ComfyUI/models/onnx (e.g. yolo/your_model.onnx).",
                }),
                "enable_history": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Track selections in the history widget.",
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_HISTORY, {
                    "default": {}
                }),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = (False, False, False)
    OUTPUT_TOOLTIPS = (
        "Selected ONNX detector model label.",
        "File path of the selected ONNX detector model.",
    )
    RETURN_NAMES = ("detector", "model_path")
    RETURN_TYPES = (Input.ONNX_DETECTOR, Input.ONNX_PATH)

    def on_exec(self, **kwargs: dict):
        detector_label: str = normalize_list_to_value(kwargs.get("detector"))
        enable_history: bool = bool(normalize_list_to_value(kwargs.get("enable_history", True)))
        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))

        models = self._available_models()
        if not models:
            raise ValueError(
                "No ONNX models found. Drop detector files into ComfyUI/models/onnx."
            )

        if detector_label not in models:
            raise ValueError(f"Unknown ONNX model '{detector_label}'. Refresh the selector after adding models.")

        model_path = models[detector_label]

        nodes: List[dict] = ui_widget.get("nodes", []) if isinstance(ui_widget, dict) else []
        if enable_history:
            create_history_node(detector_label, nodes)

        dataset = {"nodes": nodes}
        safe_send_sync("onnxselector", {"dataset": dataset}, kwargs.get("node_id"))

        return (detector_label, str(model_path))


NODE_CLASS_MAPPINGS = {
    "LF_ONNXSelector": LF_ONNXSelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ONNXSelector": "ONNX selector",
}
