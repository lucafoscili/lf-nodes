"""Workflow dependencies for loading and releasing one LM Studio LLM."""

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.api.lm_studio_lifecycle import (
    lifecycle_scalar,
    load_lm_studio_model,
    unload_lm_studio_model,
)


class LF_LMSLoadModel:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": (Input.STRING, {
                    "default": "",
                    "tooltip": "Exact downloaded LM Studio model key. Reuses its sole loaded instance.",
                }),
                "url": (Input.STRING, {
                    "default": "http://127.0.0.1:1234/api/v1/chat",
                    "tooltip": "LM Studio native chat URL; uses the matching models/load endpoint.",
                }),
            },
            "optional": {
                "timeout": (Input.INTEGER, {"default": 120, "min": 1}),
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    RETURN_TYPES = (Input.STRING,)
    RETURN_NAMES = ("instance_id",)
    OUTPUT_IS_LIST = (False,)
    OUTPUT_TOOLTIPS = (
        "Exact loaded instance ID. Connect to Prompt Maker model and LMS Unload Model instance_id.",
    )

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # External model residency is not represented by Comfy's input cache.
        return float("nan")

    def on_exec(self, model, url, timeout=120):
        instance_id = load_lm_studio_model(
            lifecycle_scalar(model, "model"),
            lifecycle_scalar(url, "url"),
            lifecycle_scalar(timeout, "timeout"),
        )
        return (instance_id,)


class LF_LMSUnloadModel:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (Input.STRING, {
                    "forceInput": True,
                    "tooltip": "Completed prompt. Connect the output prompt onward to order downstream generation after unload.",
                }),
                "instance_id": (Input.STRING, {
                    "forceInput": True,
                    "tooltip": "Exact instance ID from LMS Load Model. Only this instance is unloaded.",
                }),
                "url": (Input.STRING, {
                    "default": "http://127.0.0.1:1234/api/v1/chat",
                    "tooltip": "Same LM Studio native chat URL used by LMS Load Model.",
                }),
            },
            "optional": {
                "timeout": (Input.INTEGER, {"default": 120, "min": 1}),
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    RETURN_TYPES = (Input.STRING,)
    RETURN_NAMES = ("prompt",)
    OUTPUT_IS_LIST = (False,)
    OUTPUT_TOOLTIPS = ("Unchanged prompt, available only after the exact instance is unloaded.",)

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def on_exec(self, prompt, instance_id, url, timeout=120):
        completed_prompt = lifecycle_scalar(prompt, "prompt")
        if not isinstance(completed_prompt, str):
            raise ValueError("prompt must be a string.")
        unload_lm_studio_model(
            lifecycle_scalar(instance_id, "instance_id"),
            lifecycle_scalar(url, "url"),
            lifecycle_scalar(timeout, "timeout"),
        )
        return (completed_prompt,)


NODE_CLASS_MAPPINGS = {
    "LF_LMSLoadModel": LF_LMSLoadModel,
    "LF_LMSUnloadModel": LF_LMSUnloadModel,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LMSLoadModel": "LMS Load Model",
    "LF_LMSUnloadModel": "LMS Unload Model",
}
