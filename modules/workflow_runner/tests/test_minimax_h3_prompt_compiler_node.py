"""Focused contract for the private MiniMax H3 prompt compiler node."""

from __future__ import annotations

import json

from modules.workflow_runner.nodes.minimax_h3_prompt_compiler import (
    NODE_CLASS_MAPPINGS,
    WorkflowRunnerH3PromptCompiler,
)


def test_private_compiler_node_exposes_minimal_prompt_and_report_contract() -> None:
    node = WorkflowRunnerH3PromptCompiler
    inputs = node.INPUT_TYPES()["required"]

    assert NODE_CLASS_MAPPINGS == {
        "WorkflowRunnerH3PromptCompiler": WorkflowRunnerH3PromptCompiler,
    }
    assert tuple(inputs) == (
        "response",
        "mode",
        "duration_seconds",
        "reference_image_count",
    )
    assert node.RETURN_NAMES == ("prompt", "validation_report")
    assert node.RETURN_TYPES == ("STRING", "JSON")
    assert node.OUTPUT_IS_LIST == (False, False)
    assert not hasattr(node, "OUTPUT_NODE")


def test_private_compiler_node_delegates_to_deterministic_compiler() -> None:
    response = json.dumps(
        {
            "integrated_multimodal_description": "[Shot 1] A quiet portrait.",
            "overall_soundscape": "A soft room tone.",
            "non_diegetic_music": "N/A",
        }
    )

    prompt, report = WorkflowRunnerH3PromptCompiler().on_exec(
        response=response,
        mode="t2va",
        duration_seconds=6.0,
        reference_image_count=0,
    )

    assert prompt.startswith(
        "integrated_multimodal_description:\n[Shot 1] A quiet portrait."
    )
    assert report["valid"] is True
    assert report["mode"] == "t2va"
    assert report["referenceImageCount"] == 0


def test_private_compiler_node_accepts_semantic_plan_response() -> None:
    response = json.dumps(
        {
            "shots": [
                {
                    "start_seconds": 0,
                    "description": "A quiet portrait holds.",
                    "dialogue": [],
                },
                {
                    "start_seconds": 2.5,
                    "description": "The camera moves closer.",
                    "dialogue": [],
                },
            ],
            "overall_soundscape": "A soft room tone.",
            "non_diegetic_music": "N/A",
        }
    )

    prompt, report = WorkflowRunnerH3PromptCompiler().on_exec(
        response=response,
        mode="t2va",
        duration_seconds=6.0,
        reference_image_count=0,
    )

    assert "[Shot 1] A quiet portrait holds." in prompt
    assert "[Shot 2] At 00:02.500, The camera moves closer." in prompt
    assert report["shotTimestamps"] == ["00:02.500"]
