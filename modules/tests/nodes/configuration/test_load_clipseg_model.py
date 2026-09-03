import os
from pathlib import Path
from unittest.mock import Mock, call

import pytest

from modules.nodes.configuration import load_clipseg_model

try:
    import _winapi
except ImportError:
    _winapi = None


MODEL_ID = "CIDAS/clipseg-rd64-refined"
LOCAL_LEAF = "CIDAS--clipseg-rd64-refined"


def _model_dir(root: Path) -> Path:
    model_dir = root / LOCAL_LEAF
    model_dir.mkdir(parents=True)
    return model_dir


def _create_junction(source: Path, destination: Path) -> None:
    if _winapi is None:
        pytest.skip("Windows junction coverage")
    try:
        _winapi.CreateJunction(str(source), str(destination))
    except OSError as error:
        pytest.skip(f"junction creation unavailable: {error}")


def _is_within_directory(directory: str, target: str) -> bool:
    try:
        return os.path.commonpath((directory, target)) == directory
    except ValueError:
        return False


def _loaders(monkeypatch, roots: list[Path]):
    processor = Mock()
    processor_loader = Mock()
    processor_loader.from_pretrained.return_value = processor

    model = Mock()
    model.eval.return_value = model
    model_loader = Mock()
    model_loader.from_pretrained.return_value = model

    events = []
    monkeypatch.setattr(
        load_clipseg_model.folder_paths,
        "get_folder_paths",
        lambda _folder: [str(root) for root in roots],
    )
    monkeypatch.setattr(
        load_clipseg_model.folder_paths,
        "is_within_directory",
        _is_within_directory,
        raising=False,
    )
    monkeypatch.setattr(load_clipseg_model, "CLIPSegProcessor", processor_loader)
    monkeypatch.setattr(
        load_clipseg_model,
        "CLIPSegForImageSegmentation",
        model_loader,
    )
    monkeypatch.setattr(
        load_clipseg_model,
        "safe_send_sync",
        lambda *args: events.append(args),
    )
    return processor_loader, processor, model_loader, model, events


def _invoke():
    return load_clipseg_model.LF_LoadCLIPSegModel().on_exec(
        folder="clip_vision",
        model_id=MODEL_ID,
        node_id="node-1",
    )


def test_published_schema_and_socket_contract_remain_unchanged() -> None:
    node = load_clipseg_model.LF_LoadCLIPSegModel
    schema = {
        section: {
            name: declaration if isinstance(declaration, str) else (
                declaration[0],
                {
                    key: value
                    for key, value in declaration[1].items()
                    if key != "tooltip"
                },
            )
            for name, declaration in inputs.items()
        }
        for section, inputs in node.INPUT_TYPES().items()
    }

    assert schema == {
        "required": {
            "folder": ("STRING", {"default": "clip_vision"}),
            "model_id": ("STRING", {"default": MODEL_ID}),
        },
        "optional": {"ui_widget": ("LF_CODE", {"default": {}})},
        "hidden": {"node_id": "UNIQUE_ID"},
    }
    assert list(schema) == ["required", "optional", "hidden"]
    assert list(schema["required"]) == ["folder", "model_id"]
    assert load_clipseg_model.NODE_CLASS_MAPPINGS == {
        "LF_LoadCLIPSegModel": node,
    }
    assert node.RETURN_TYPES == ("CLIP_PROCESSOR", "CLIP_MODEL")
    assert node.RETURN_NAMES == ("processor", "model")
    assert not hasattr(node, "INPUT_IS_LIST")
    assert not hasattr(node, "OUTPUT_IS_LIST")
    assert node.FUNCTION == "on_exec"


def test_local_resolution_preserves_hot_first_precedence(tmp_path, monkeypatch) -> None:
    hot_model_dir = _model_dir(tmp_path / "hot")
    _model_dir(tmp_path / "cold")
    processor_loader, processor, model_loader, model, _events = _loaders(
        monkeypatch,
        [tmp_path / "hot", tmp_path / "cold"],
    )

    assert _invoke() == (processor, model)
    processor_loader.from_pretrained.assert_called_once_with(str(hot_model_dir))
    model_loader.from_pretrained.assert_called_once_with(str(hot_model_dir))
    processor.save_pretrained.assert_not_called()
    model.save_pretrained.assert_not_called()


def test_local_resolution_finds_cold_only_copy_without_remote_call(
    tmp_path,
    monkeypatch,
) -> None:
    hot_root = tmp_path / "hot"
    hot_root.mkdir()
    cold_model_dir = _model_dir(tmp_path / "cold")
    processor_loader, processor, model_loader, model, events = _loaders(
        monkeypatch,
        [hot_root, tmp_path / "cold"],
    )

    assert _invoke() == (processor, model)
    processor_loader.from_pretrained.assert_called_once_with(str(cold_model_dir))
    model_loader.from_pretrained.assert_called_once_with(str(cold_model_dir))
    assert "Downloading" not in str(events)
    assert str(cold_model_dir) in events[-1][1]["value"]
    processor.save_pretrained.assert_not_called()
    model.save_pretrained.assert_not_called()


def test_broken_hot_copy_falls_through_to_good_cold_copy_before_remote(
    tmp_path,
    monkeypatch,
) -> None:
    hot_model_dir = _model_dir(tmp_path / "hot")
    cold_model_dir = _model_dir(tmp_path / "cold")
    processor_loader, processor, model_loader, model, events = _loaders(
        monkeypatch,
        [tmp_path / "hot", tmp_path / "cold"],
    )

    def load_model(source, **kwargs):
        assert not kwargs
        if source == str(hot_model_dir):
            raise OSError("missing model weights")
        assert source == str(cold_model_dir)
        return model

    model_loader.from_pretrained.side_effect = load_model

    assert _invoke() == (processor, model)
    assert processor_loader.from_pretrained.call_args_list == [
        call(str(hot_model_dir)),
        call(str(cold_model_dir)),
    ]
    assert model_loader.from_pretrained.call_args_list == [
        call(str(hot_model_dir)),
        call(str(cold_model_dir)),
    ]
    assert all(
        invocation.args != (MODEL_ID,)
        for invocation in processor_loader.from_pretrained.mock_calls
    )
    assert all(
        invocation.args != (MODEL_ID,)
        for invocation in model_loader.from_pretrained.mock_calls
    )
    assert "Skipped unusable local model" in str(events)
    assert "Downloading" not in str(events)


def test_missing_model_keeps_first_root_as_download_destination(
    tmp_path,
    monkeypatch,
) -> None:
    hot_root = tmp_path / "hot"
    cold_root = tmp_path / "cold"
    hot_root.mkdir()
    cold_root.mkdir()
    processor_loader, processor, model_loader, model, _events = _loaders(
        monkeypatch,
        [hot_root, cold_root],
    )

    assert _invoke() == (processor, model)
    model_dir = hot_root / LOCAL_LEAF
    processor_loader.from_pretrained.assert_called_once_with(
        MODEL_ID,
        cache_dir=str(hot_root),
    )
    model_loader.from_pretrained.assert_called_once_with(
        MODEL_ID,
        cache_dir=str(hot_root),
    )
    processor.save_pretrained.assert_called_once_with(str(model_dir))
    model.save_pretrained.assert_called_once_with(str(model_dir))


@pytest.mark.parametrize(
    "model_id",
    (
        ".",
        "..",
        "org/./model",
        "org/../model",
        "/rooted",
        "C:drive-relative",
        "C:/drive-absolute",
        r"\root-relative",
        r"\\server\share\model",
        r"org\model",
        "model.",
        "model name",
        "model\nname",
        "NUL",
    ),
)
def test_unsafe_model_ids_are_rejected_before_local_or_remote_access(
    tmp_path,
    monkeypatch,
    model_id,
) -> None:
    root = tmp_path / "models"
    root.mkdir()
    processor_loader, _processor, model_loader, _model, events = _loaders(
        monkeypatch,
        [root],
    )

    with pytest.raises(ValueError, match="Invalid Hugging Face model ID"):
        load_clipseg_model.LF_LoadCLIPSegModel().on_exec(
            folder="clip_vision",
            model_id=model_id,
        )

    processor_loader.from_pretrained.assert_not_called()
    model_loader.from_pretrained.assert_not_called()
    assert events == []


def test_registered_root_may_itself_be_a_junction(tmp_path, monkeypatch) -> None:
    actual_root = tmp_path / "actual-models"
    actual_model_dir = _model_dir(actual_root)
    registered_root = tmp_path / "registered-models"
    _create_junction(actual_root, registered_root)
    processor_loader, processor, model_loader, model, _events = _loaders(
        monkeypatch,
        [registered_root],
    )

    assert _invoke() == (processor, model)
    processor_loader.from_pretrained.assert_called_once_with(str(actual_model_dir))
    model_loader.from_pretrained.assert_called_once_with(str(actual_model_dir))


def test_child_reparse_escape_is_rejected_when_supported(tmp_path, monkeypatch) -> None:
    root = tmp_path / "models"
    outside_model = _model_dir(tmp_path / "outside")
    root.mkdir()
    escaping_child = root / LOCAL_LEAF
    _create_junction(outside_model, escaping_child)

    processor_loader, _processor, model_loader, _model, events = _loaders(
        monkeypatch,
        [root],
    )
    with pytest.raises(ValueError, match="escapes its registered root"):
        _invoke()

    processor_loader.from_pretrained.assert_not_called()
    model_loader.from_pretrained.assert_not_called()
    assert events == []
