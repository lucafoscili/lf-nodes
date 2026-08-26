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
comfy_helpers.safe_send_sync = lambda *_args, **_kwargs: None
comfy_helpers.get_comfy_dir = getattr(comfy_helpers, "get_comfy_dir", lambda _kind: ".")
comfy_helpers.resolve_filepath = getattr(
    comfy_helpers,
    "resolve_filepath",
    lambda **_kwargs: ("output.file", "", "output.file"),
)

constants = sys.modules.setdefault(
    "modules.utils.constants", types.ModuleType("modules.utils.constants")
)
constants.FUNCTION = "on_exec"
input_values = {
    "BOOLEAN": "BOOLEAN",
    "CONDITIONING": "CONDITIONING",
    "FLOAT": "FLOAT",
    "IMAGE": "IMAGE",
    "INTEGER": "INT",
    "JSON": "JSON",
    "LF_CODE": "LF_CODE",
    "LF_TREE": "LF_TREE",
    "MASK": "MASK",
    "NUMBER": "NUMBER",
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

from modules.nodes.io import register_output_file


def test_registers_nested_file_with_portable_history_payload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_root = tmp_path / "output"
    artifact = output_root / "renders" / "clip.webm"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"generic artifact")
    sent: list[tuple] = []
    monkeypatch.setattr(
        register_output_file.folder_paths,
        "get_output_directory",
        lambda: str(output_root),
    )
    monkeypatch.setattr(
        register_output_file,
        "safe_send_sync",
        lambda *args: sent.append(args),
    )

    response = register_output_file.LF_RegisterOutputFile().on_exec(
        relative_path=r"renders\clip.webm",
        node_id="node-12",
    )

    assert response["result"] == ("renders/clip.webm",)
    lf_output = response["ui"]["lf_output"][0]
    assert lf_output["file_names"] == ["renders/clip.webm"]
    assert lf_output["receipt"] == {
        "schema": "lf.output_file.receipt.v1",
        "file_name": "renders/clip.webm",
        "storage_type": "output",
        "byte_length": len(b"generic artifact"),
    }
    assert lf_output["dataset"]["nodes"][0]["children"][0]["value"] == (
        "renders/clip.webm"
    )
    assert sent == [
        (
            "registeroutputfile",
            {"dataset": lf_output["dataset"]},
            "node-12",
        )
    ]
    assert str(output_root.resolve()) not in json.dumps(response)


@pytest.mark.parametrize(
    "relative_path, message",
    [
        ("../outside.bin", "parent traversal"),
        ("nested/../artifact.bin", "parent traversal"),
        ("bad\nname.bin", "control characters"),
        ("C:\\outside.bin", "must be relative"),
        ("/outside.bin", "must be relative"),
        ("folder/file:name.bin", "alternate stream"),
        ("", "non-empty string"),
        (["one.bin", "two.bin"], "exactly one"),
    ],
)
def test_rejects_nonportable_or_ambiguous_paths(relative_path, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        register_output_file.LF_RegisterOutputFile().on_exec(
            relative_path=relative_path,
        )


def test_rejects_missing_paths_and_directories(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_root = tmp_path / "output"
    directory = output_root / "directory"
    directory.mkdir(parents=True)
    monkeypatch.setattr(
        register_output_file.folder_paths,
        "get_output_directory",
        lambda: str(output_root),
    )

    with pytest.raises(ValueError, match="existing output file"):
        register_output_file.LF_RegisterOutputFile().on_exec(
            relative_path="missing.bin",
        )
    with pytest.raises(ValueError, match="regular output file"):
        register_output_file.LF_RegisterOutputFile().on_exec(
            relative_path="directory",
        )


def test_rejects_symlink_escape(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_root = tmp_path / "output"
    output_root.mkdir()
    external = tmp_path / "external.bin"
    external.write_bytes(b"outside")
    link = output_root / "escape.bin"
    try:
        link.symlink_to(external)
    except OSError as error:
        pytest.skip(f"File symlinks are unavailable: {error}")
    monkeypatch.setattr(
        register_output_file.folder_paths,
        "get_output_directory",
        lambda: str(output_root),
    )

    with pytest.raises(ValueError, match="resolves outside"):
        register_output_file.LF_RegisterOutputFile().on_exec(
            relative_path="escape.bin",
        )


def test_resolved_path_escape_fails_closed_without_symlink_privileges(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_root = tmp_path / "output"
    output_root.mkdir()
    candidate = output_root / "escape.bin"
    external = tmp_path / "external.bin"
    external.write_bytes(b"outside")
    original_resolve = Path.resolve

    def resolve(path: Path, strict: bool = False) -> Path:
        if path == candidate:
            return external
        return original_resolve(path, strict=strict)

    monkeypatch.setattr(
        register_output_file.folder_paths,
        "get_output_directory",
        lambda: str(output_root),
    )
    monkeypatch.setattr(Path, "resolve", resolve)

    with pytest.raises(ValueError, match="resolves outside"):
        register_output_file.LF_RegisterOutputFile().on_exec(
            relative_path="escape.bin",
        )


def test_internal_symlink_is_canonicalized_to_its_managed_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_root = tmp_path / "output"
    target = output_root / "real" / "artifact.bin"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"inside")
    link = output_root / "alias.bin"
    try:
        link.symlink_to(target)
    except OSError as error:
        pytest.skip(f"File symlinks are unavailable: {error}")
    monkeypatch.setattr(
        register_output_file.folder_paths,
        "get_output_directory",
        lambda: str(output_root),
    )

    response = register_output_file.LF_RegisterOutputFile().on_exec(
        relative_path="alias.bin",
    )

    assert response["result"] == ("real/artifact.bin",)


def test_public_contract_is_generic_and_uses_tree_widget() -> None:
    inputs = register_output_file.LF_RegisterOutputFile.INPUT_TYPES()

    assert set(inputs["required"]) == {"relative_path"}
    assert inputs["optional"]["ui_widget"][0] == "LF_TREE"
    assert inputs["hidden"] == {"node_id": "UNIQUE_ID"}
    assert register_output_file.LF_RegisterOutputFile.RETURN_TYPES == ("STRING",)
    assert register_output_file.NODE_CLASS_MAPPINGS == {
        "LF_RegisterOutputFile": register_output_file.LF_RegisterOutputFile,
    }
    contract = repr(inputs).lower()
    assert "velora" not in contract
    assert "stellaris" not in contract
    assert "azeroth" not in contract
