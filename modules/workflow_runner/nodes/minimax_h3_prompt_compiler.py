"""Deterministic MiniMax H3 prompt compiler for Workflow Runner."""

from __future__ import annotations

from ...utils.constants import CATEGORY_PREFIX, FUNCTION, Input
from ..prompts.minimax_h3 import compile_h3_prompt_response


class WorkflowRunnerH3PromptCompiler:
    """Compile a structured LMS response into strict H3 prompt text."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "response": (
                    Input.STRING,
                    {
                        "default": "",
                        "forceInput": True,
                        "multiline": True,
                        "tooltip": "Structured JSON returned by the prompt-writing model.",
                    },
                ),
                "mode": (
                    ["t2va", "i2va", "fl2va", "l2va", "ref2va"],
                    {
                        "default": "t2va",
                        "tooltip": "MiniMax H3 prompt format to compile.",
                    },
                ),
                "duration_seconds": (
                    Input.FLOAT,
                    {
                        "default": 6.0,
                        "min": 0.001,
                        "max": 5_999.999,
                        "step": 0.001,
                        "tooltip": "Exact target duration used for keyframe alignment and timing checks.",
                    },
                ),
                "reference_image_count": (
                    Input.INTEGER,
                    {
                        "default": 0,
                        "min": 0,
                        "max": 9,
                        "tooltip": "Number of ordered Picture references visible to the model.",
                    },
                ),
            }
        }

    CATEGORY = f"{CATEGORY_PREFIX}/Workflow Runner"
    FUNCTION = FUNCTION
    RETURN_NAMES = ("prompt", "validation_report")
    RETURN_TYPES = (Input.STRING, Input.JSON)
    OUTPUT_IS_LIST = (False, False)
    OUTPUT_TOOLTIPS = (
        "Copy-ready MiniMax H3 prompt with deterministic outer formatting.",
        "Machine-readable validation receipt for the compiled prompt.",
    )

    def on_exec(
        self,
        response: str,
        mode: str,
        duration_seconds: float,
        reference_image_count: int,
    ):
        prompt, report = compile_h3_prompt_response(
            response,
            mode=mode,
            duration_seconds=duration_seconds,
            reference_image_count=reference_image_count,
        )
        return (prompt, report)


NODE_CLASS_MAPPINGS = {
    "WorkflowRunnerH3PromptCompiler": WorkflowRunnerH3PromptCompiler,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WorkflowRunnerH3PromptCompiler": "Workflow Runner · MiniMax H3 prompt compiler",
}
