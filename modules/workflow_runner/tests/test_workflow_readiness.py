import json
from pathlib import Path
from types import SimpleNamespace

from modules.workflow_runner.services.readiness import (
    MAX_READINESS_ISSUES,
    WorkflowReadinessScanner,
    evaluate_workflow_readiness,
)


class _Workflow:
    def __init__(self, path: Path):
        self.workflow_path = path
        self.inputs = ()

    def load_prompt(self):
        with self.workflow_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)


def _write_prompt(tmp_path: Path, prompt: dict) -> _Workflow:
    path = tmp_path / "workflow.json"
    path.write_text(json.dumps(prompt), encoding="utf-8")
    return _Workflow(path)


def _scanner(*, nodes=(), models=None) -> WorkflowReadinessScanner:
    model_files = models or {}
    return WorkflowReadinessScanner(
        node_mapping_loader=lambda: {name: object() for name in nodes},
        model_filename_loader=lambda category: model_files.get(category, ()),
    )


def test_ready_when_nodes_and_default_model_are_present(tmp_path: Path) -> None:
    workflow = _write_prompt(
        tmp_path,
        {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "nested/model.safetensors"},
            },
            "2": {"class_type": "SaveImage", "inputs": {"images": ["1", 0]}},
        },
    )
    scanner = _scanner(
        nodes={"CheckpointLoaderSimple", "SaveImage"},
        models={"checkpoints": {"nested\\model.safetensors"}},
    )

    assert evaluate_workflow_readiness(workflow, scanner=scanner) == {
        "status": "ready",
        "issues": [],
    }


def test_missing_node_is_setup_required(tmp_path: Path) -> None:
    workflow = _write_prompt(
        tmp_path,
        {"1": {"class_type": "CommunityMagic", "inputs": {}}},
    )

    result = evaluate_workflow_readiness(workflow, scanner=_scanner(nodes=set()))

    assert result == {
        "status": "setup_required",
        "issues": [
            {
                "code": "node_missing",
                "message": "Required node type is not installed: CommunityMagic.",
            }
        ],
    }


def test_missing_known_core_loader_model_is_setup_required(tmp_path: Path) -> None:
    workflow = _write_prompt(
        tmp_path,
        {
            "1": {
                "class_type": "UNETLoader",
                "inputs": {"unet_name": "wanted.safetensors"},
            }
        },
    )

    result = evaluate_workflow_readiness(
        workflow,
        scanner=_scanner(nodes={"UNETLoader"}, models={"diffusion_models": set()}),
    )

    assert result == {
        "status": "setup_required",
        "issues": [
            {
                "code": "model_missing",
                "message": (
                    "Required diffusion model file is not installed: "
                    "wanted.safetensors."
                ),
            }
        ],
    }


def test_missing_selectable_default_model_warns_without_blocking(tmp_path: Path) -> None:
    workflow = _write_prompt(
        tmp_path,
        {
            "1": {
                "class_type": "UNETLoader",
                "inputs": {"unet_name": "wanted.safetensors"},
            }
        },
    )
    workflow.inputs = (
        SimpleNamespace(
            node_id="1",
            props={
                "lfDataset": {
                    "nodes": [
                        {
                            "id": "wanted.safetensors",
                            "value": "Wanted model",
                            "workflowValue": "wanted.safetensors",
                        }
                    ]
                },
                "lfValue": "wanted.safetensors",
            },
        ),
    )

    result = evaluate_workflow_readiness(
        workflow,
        scanner=_scanner(nodes={"UNETLoader"}, models={"diffusion_models": set()}),
    )

    assert result == {
        "status": "warning",
        "issues": [
            {
                "code": "default_model_missing",
                "message": (
                    "Default diffusion model file is not installed: wanted.safetensors. "
                    "Choose an installed option before running."
                ),
            }
        ],
    }


def test_other_control_on_loader_does_not_make_missing_asset_selectable(
    tmp_path: Path,
) -> None:
    workflow = _write_prompt(
        tmp_path,
        {
            "1": {
                "class_type": "LoraLoaderModelOnly",
                "inputs": {
                    "lora_name": "required-adapter.safetensors",
                    "strength_model": 1.0,
                },
            }
        },
    )
    workflow.inputs = (
        SimpleNamespace(
            node_id="1",
            props={"lfValue": "1", "lfLabel": "Adapter strength"},
        ),
    )

    result = evaluate_workflow_readiness(
        workflow,
        scanner=_scanner(nodes={"LoraLoaderModelOnly"}, models={"loras": set()}),
    )

    assert result == {
        "status": "setup_required",
        "issues": [
            {
                "code": "model_missing",
                "message": (
                    "Required LoRA file is not installed: "
                    "required-adapter.safetensors."
                ),
            }
        ],
    }


def test_select_display_label_does_not_override_its_workflow_value(
    tmp_path: Path,
) -> None:
    workflow = _write_prompt(
        tmp_path,
        {
            "1": {
                "class_type": "UNETLoader",
                "inputs": {"unet_name": "required.safetensors"},
            }
        },
    )
    workflow.inputs = (
        SimpleNamespace(
            node_id="1",
            props={
                "lfDataset": {
                    "nodes": [
                        {
                            "id": "profile-id",
                            "value": "required.safetensors",
                            "workflowValue": "different-profile-value",
                        }
                    ]
                }
            },
        ),
    )

    result = evaluate_workflow_readiness(
        workflow,
        scanner=_scanner(nodes={"UNETLoader"}, models={"diffusion_models": set()}),
    )

    assert result["status"] == "setup_required"
    assert result["issues"][0]["code"] == "model_missing"


def test_scanner_unavailable_is_warning_not_blocker(tmp_path: Path) -> None:
    workflow = _write_prompt(
        tmp_path,
        {
            "1": {
                "class_type": "UNETLoader",
                "inputs": {"unet_name": "wanted.safetensors"},
            }
        },
    )

    def unavailable_nodes():
        raise ImportError("Comfy node registry is still initializing")

    def unavailable_models(_category: str):
        raise RuntimeError("folder scanner is unavailable")

    scanner = WorkflowReadinessScanner(
        node_mapping_loader=unavailable_nodes,
        model_filename_loader=unavailable_models,
    )
    result = evaluate_workflow_readiness(workflow, scanner=scanner)

    assert result["status"] == "warning"
    assert result["issues"] == [
        {
            "code": "node_scanner_unavailable",
            "message": "Installed node types could not be checked; readiness is uncertain.",
        },
        {
            "code": "model_scanner_unavailable",
            "message": (
                "Installed files could not be checked for model category "
                "diffusion_models; readiness is uncertain."
            ),
        },
    ]


def test_proven_blocker_precedes_scanner_uncertainty(tmp_path: Path) -> None:
    workflow = _write_prompt(
        tmp_path,
        {
            "1": {
                "class_type": "UNETLoader",
                "inputs": {"unet_name": "missing.safetensors"},
            }
        },
    )

    def unavailable_nodes():
        raise ImportError("node registry is unavailable")

    scanner = WorkflowReadinessScanner(
        node_mapping_loader=unavailable_nodes,
        model_filename_loader=lambda _category: (),
    )
    result = evaluate_workflow_readiness(workflow, scanner=scanner)

    assert result["status"] == "setup_required"
    assert [issue["code"] for issue in result["issues"]] == [
        "model_missing",
        "node_scanner_unavailable",
    ]


def test_missing_workflow_file_is_setup_required(tmp_path: Path) -> None:
    result = evaluate_workflow_readiness(_Workflow(tmp_path / "gone.json"))

    assert result == {
        "status": "setup_required",
        "issues": [
            {
                "code": "workflow_file_missing",
                "message": "Workflow definition file is missing: gone.json.",
            }
        ],
    }


def test_readiness_issues_are_deterministic_and_bounded(tmp_path: Path) -> None:
    prompt = {
        str(index): {"class_type": f"MissingNode{index:02d}", "inputs": {}}
        for index in range(MAX_READINESS_ISSUES + 5)
    }
    workflow = _write_prompt(tmp_path, prompt)

    result = evaluate_workflow_readiness(workflow, scanner=_scanner(nodes=set()))

    assert result["status"] == "setup_required"
    assert len(result["issues"]) == MAX_READINESS_ISSUES
    assert [issue["code"] for issue in result["issues"][:-1]] == [
        "node_missing"
    ] * (MAX_READINESS_ISSUES - 1)
    assert result["issues"][-1] == {
        "code": "readiness_issues_truncated",
        "message": "6 additional readiness issue(s) were omitted.",
    }
    assert result["issues"][0]["message"].endswith("MissingNode00.")


def test_unknown_custom_loader_does_not_guess_at_file_inputs(tmp_path: Path) -> None:
    workflow = _write_prompt(
        tmp_path,
        {
            "1": {
                "class_type": "CustomLoader",
                "inputs": {"model_name": "not-local.bin"},
            }
        },
    )

    result = evaluate_workflow_readiness(
        workflow,
        scanner=_scanner(nodes={"CustomLoader"}),
    )

    assert result == {"status": "ready", "issues": []}
