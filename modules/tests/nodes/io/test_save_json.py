from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[4]

server = sys.modules.setdefault("server", types.ModuleType("server"))
server.PromptServer = types.SimpleNamespace(instance=None)

folder_paths = sys.modules.setdefault("folder_paths", types.ModuleType("folder_paths"))
folder_paths.models_dir = getattr(folder_paths, "models_dir", ".")
folder_paths.get_input_directory = getattr(folder_paths, "get_input_directory", lambda: ".")
folder_paths.get_output_directory = getattr(folder_paths, "get_output_directory", lambda: ".")
folder_paths.get_temp_directory = getattr(folder_paths, "get_temp_directory", lambda: ".")
folder_paths.get_user_directory = getattr(folder_paths, "get_user_directory", lambda: ".")
folder_paths.get_filename_list = getattr(folder_paths, "get_filename_list", lambda _kind: [])

helpers = sys.modules.setdefault(
    "modules.utils.helpers", types.ModuleType("modules.utils.helpers")
)
helpers.__path__ = [str(REPO_ROOT / "modules" / "utils" / "helpers")]

comfy_helpers = sys.modules.setdefault(
    "modules.utils.helpers.comfy", types.ModuleType("modules.utils.helpers.comfy")
)
comfy_helpers.safe_send_sync = getattr(
    comfy_helpers, "safe_send_sync", lambda *_args, **_kwargs: None
)
comfy_helpers.get_comfy_dir = getattr(
    comfy_helpers, "get_comfy_dir", lambda _kind: "."
)
comfy_helpers.resolve_filepath = getattr(
    comfy_helpers,
    "resolve_filepath",
    lambda **_kwargs: ("output.json", "", "output.json"),
)

logic_helpers = sys.modules.setdefault(
    "modules.utils.helpers.logic", types.ModuleType("modules.utils.helpers.logic")
)
logic_helpers.normalize_json_input = getattr(
    logic_helpers, "normalize_json_input", lambda value: value
)
logic_helpers.normalize_list_to_value = getattr(
    logic_helpers,
    "normalize_list_to_value",
    lambda value: value[0] if isinstance(value, list) and value else value,
)

constants = sys.modules.setdefault(
    "modules.utils.constants", types.ModuleType("modules.utils.constants")
)
constants.FUNCTION = "on_exec"
input_values = {
    "BOOLEAN": "BOOLEAN",
    "JSON": "JSON",
    "LF_TREE": "LF_TREE",
    "STRING": "STRING",
}
input_stub = getattr(constants, "Input", types.SimpleNamespace())
for input_name, input_value in input_values.items():
    if not hasattr(input_stub, input_name):
        setattr(input_stub, input_name, input_value)
constants.Input = input_stub

io_package = sys.modules.setdefault(
    "modules.nodes.io", types.ModuleType("modules.nodes.io")
)
io_package.__path__ = [str(REPO_ROOT / "modules" / "nodes" / "io")]
io_package.CATEGORY = "LF Nodes/IO Operations"

from modules.nodes.io import save_json
from modules.workflow_runner.services.lifecycle import build_output_manifest


def test_saves_json_and_publishes_portable_runner_artifact(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_root = tmp_path / "output"
    output_file = output_root / "receipts" / "sequence.json"
    output_file.parent.mkdir(parents=True)
    resolve_calls: list[dict] = []
    sent: list[tuple] = []

    monkeypatch.setattr(
        save_json,
        "get_comfy_dir",
        lambda kind: str(output_root) if kind == "output" else pytest.fail(kind),
    )

    def resolve_filepath(**kwargs):
        resolve_calls.append(kwargs)
        return str(output_file), "receipts", "sequence.json"

    monkeypatch.setattr(save_json, "resolve_filepath", resolve_filepath)
    monkeypatch.setattr(
        save_json,
        "safe_send_sync",
        lambda *args: sent.append(args),
    )

    payload = {"title": "café", "indices": [0, 3, 7]}
    response = save_json.LF_SaveJSON().on_exec(
        json_data=payload,
        filename_prefix="receipts/sequence",
        add_timestamp=False,
        node_id="save-json-1",
    )

    assert json.loads(output_file.read_text(encoding="utf-8")) == payload
    assert response["result"] == (payload,)
    assert response["result"][0] is payload
    assert resolve_calls == [
        {
            "filename_prefix": "receipts/sequence",
            "base_output_path": str(output_root.resolve()),
            "add_timestamp": False,
            "extension": "json",
        }
    ]

    lf_output = response["ui"]["lf_output"][0]
    expected_receipt = {
        "schema": "lf.json_file.receipt.v1",
        "file_name": "receipts/sequence.json",
        "storage_type": "output",
        "byte_length": output_file.stat().st_size,
    }
    assert lf_output["file_names"] == ["receipts/sequence.json"]
    assert lf_output["receipt"] == expected_receipt
    assert lf_output["dataset"]["nodes"][0]["children"] == [
        {
            "description": f"{output_file.stat().st_size} bytes",
            "icon": "code",
            "id": "receipts/sequence.json",
            "value": "receipts/sequence.json",
        }
    ]
    assert sent == [
        (
            "savejson",
            {"dataset": lf_output["dataset"]},
            "save-json-1",
        )
    ]
    assert str(output_root.resolve()) not in json.dumps(response)

    manifest = build_output_manifest(
        "submission-1",
        "prompt-1",
        {
            "body": {
                "payload": {
                    "preferred_output": "save-json-1",
                    "history": {"outputs": {"save-json-1": response["ui"]}},
                }
            }
        },
    )
    assert manifest["artifacts"] == [
        {
            "node_id": "save-json-1",
            "path": "lf_output[0].file_names[0]",
            "filename": "sequence.json",
            "subfolder": "receipts",
            "storage_type": "output",
            "media_type": "application/json",
        }
    ]
    assert manifest["outputs"]["save-json-1"]["lf_output"][0]["receipt"] == (
        expected_receipt
    )


def test_rejects_resolved_json_path_outside_output_root_before_writing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_root = tmp_path / "output"
    output_root.mkdir()
    outside_file = tmp_path / "outside.json"
    sent: list[tuple] = []

    monkeypatch.setattr(save_json, "get_comfy_dir", lambda _kind: str(output_root))
    monkeypatch.setattr(
        save_json,
        "resolve_filepath",
        lambda **_kwargs: (str(outside_file), "..", "outside.json"),
    )
    monkeypatch.setattr(save_json, "safe_send_sync", lambda *args: sent.append(args))

    with pytest.raises(ValueError, match="must remain inside"):
        save_json.LF_SaveJSON().on_exec(
            json_data={"safe": True},
            filename_prefix="../outside",
            add_timestamp=False,
            node_id="save-json-2",
        )

    assert not outside_file.exists()
    assert sent == []


def test_public_inputs_and_json_result_socket_remain_unchanged() -> None:
    inputs = save_json.LF_SaveJSON.INPUT_TYPES()

    assert set(inputs["required"]) == {
        "json_data",
        "filename_prefix",
        "add_timestamp",
    }
    assert inputs["optional"]["ui_widget"][0] == "LF_TREE"
    assert inputs["hidden"] == {"node_id": "UNIQUE_ID"}
    assert save_json.LF_SaveJSON.RETURN_NAMES == ("json",)
    assert save_json.LF_SaveJSON.RETURN_TYPES == ("JSON",)
    assert save_json.NODE_CLASS_MAPPINGS == {"LF_SaveJSON": save_json.LF_SaveJSON}
