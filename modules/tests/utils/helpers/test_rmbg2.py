from __future__ import annotations

import builtins
import json
import sys
import types
import weakref
from pathlib import Path

import numpy as np
import pytest
import torch
import torch.nn.functional as F
from PIL import Image

from modules.utils.helpers.detection import rmbg2


class _Model:
    def __init__(self):
        self.calls = []
        self.moves = []
        self.evaluated = False

    def eval(self):
        self.evaluated = True
        return self

    def to(self, *args, **kwargs):
        self.moves.append((args, kwargs))
        return self

    def __call__(self, inputs):
        self.calls.append(inputs)
        return [torch.full((1, 1, 2, 2), -10.0), torch.tensor([[[[-2.0, 0.0], [2.0, 4.0]]]])]


@pytest.fixture
def model_dir(tmp_path):
    for name in rmbg2._REQUIRED_FILES:
        (tmp_path / name).write_text("", encoding="utf-8")
    (tmp_path / "config.json").write_text(json.dumps({"bb_pretrained": False}), encoding="utf-8")
    return tmp_path


@pytest.fixture
def management(monkeypatch):
    events = []
    for name, value in {
        "get_torch_device": lambda: torch.device("cpu"),
        "module_size": lambda _model: 17,
        "minimum_inference_memory": lambda: 23,
        "free_memory": lambda *args: events.append(("free", args)),
        "soft_empty_cache": lambda: events.append(("empty",)),
    }.items():
        monkeypatch.setattr(rmbg2.model_management, name, value, raising=False)
    return events


def test_native_loader_uses_fixed_local_classes_and_strict_cpu_weights(monkeypatch, model_dir):
    calls = []
    model = _Model()

    def config_class(**kwargs):
        calls.append(("config", kwargs))
        return kwargs

    def model_class(**kwargs):
        calls.append(("model", kwargs))
        return model

    def get_class(reference, directory, **kwargs):
        calls.append((reference, directory, kwargs))
        return model_class if reference == "birefnet.BiRefNet" else config_class

    dynamic = types.ModuleType("transformers.dynamic_module_utils")
    dynamic.get_class_from_dynamic_module = get_class
    monkeypatch.setitem(sys.modules, "transformers.dynamic_module_utils", dynamic)
    safetensors = types.ModuleType("safetensors.torch")
    safetensors.load_model = lambda *args, **kwargs: calls.append(("weights", args, kwargs))
    monkeypatch.setitem(sys.modules, "safetensors.torch", safetensors)

    assert rmbg2._load_model(model_dir) is model
    assert calls == [
        ("birefnet.BiRefNet", str(model_dir), {"local_files_only": True}),
        ("BiRefNet_config.BiRefNetConfig", str(model_dir), {"local_files_only": True}),
        ("config", {"bb_pretrained": False}),
        ("model", {"config": {"bb_pretrained": False}}),
        ("weights", (model, str(model_dir / "model.safetensors")), {"strict": True, "device": "cpu"}),
    ]


def test_missing_assets_fail_before_loading_optional_dependencies(tmp_path):
    with pytest.raises(FileNotFoundError, match="missing config.json, birefnet.py, BiRefNet_config.py, model.safetensors") as error:
        rmbg2._load_model(tmp_path)
    assert str(tmp_path) in str(error.value)
    assert "does not download" in str(error.value)


def test_pretrained_backbone_is_rejected(model_dir):
    (model_dir / "config.json").write_text('{"bb_pretrained": true}', encoding="utf-8")
    with pytest.raises(ValueError, match="bb_pretrained to false"):
        rmbg2._load_model(model_dir)


def test_missing_optional_dependency_has_actionable_error(monkeypatch, model_dir):
    original_import = builtins.__import__

    def import_without_transformers(name, *args, **kwargs):
        if name == "transformers.dynamic_module_utils":
            raise ModuleNotFoundError("No module named 'transformers'", name="transformers")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_without_transformers)
    with pytest.raises(RuntimeError, match="ComfyUI's Python environment: No module named 'transformers'"):
        rmbg2._load_model(model_dir)


def test_one_model_serves_frames_with_exact_preprocessing_and_mask_resize(monkeypatch, management):
    model = _Model()
    loads = []
    monkeypatch.setattr(rmbg2, "_load_model", lambda path: loads.append(path) or model)
    images = [Image.new("RGB", (5, 3), (255, 0, 128)), Image.new("RGBA", (2, 4), (255, 0, 128, 0))]
    with rmbg2.rmbg2_session() as predict:
        masks = [predict(image) for image in images]
        assert model.evaluated
        assert model.moves == [((), {"dtype": torch.float32}), ((torch.device("cpu"),), {})]

    assert loads == [Path(rmbg2.folder_paths.models_dir) / "RMBG" / "RMBG-2.0"]
    assert model.moves[-1] == ((torch.device("cpu"),), {})
    assert management == [("empty",)]
    assert [mask.size for mask in masks] == [(5, 3), (2, 4)]
    assert all(mask.mode == "L" for mask in masks)
    expected_pixel = (torch.tensor([1.0, 0.0, 128 / 255]) - torch.tensor([0.485, 0.456, 0.406])) / torch.tensor([0.229, 0.224, 0.225])
    for inputs in model.calls:
        assert inputs.shape == (1, 3, 1024, 1024)
        assert inputs.dtype == torch.float32
        assert inputs.is_contiguous()
        torch.testing.assert_close(inputs[0, :, 0, 0], expected_pixel)
    logits = torch.tensor([[[[-2.0, 0.0], [2.0, 4.0]]]])
    expected_alpha = (F.interpolate(logits.sigmoid(), size=(3, 5), mode="bilinear", align_corners=False)[0, 0].numpy() * 255).astype(np.uint8)
    np.testing.assert_array_equal(np.array(masks[0]), expected_alpha)
    # The mask backend ignores source alpha; the compositing boundary intersects it.
    torch.testing.assert_close(model.calls[0], model.calls[1])


def test_pil_bilinear_resize_and_normalization_match_training_transform(monkeypatch, management):
    model = _Model()
    monkeypatch.setattr(rmbg2, "_load_model", lambda _path: model)
    pixels = np.arange(5 * 7 * 3, dtype=np.uint8).reshape(5, 7, 3)
    image = Image.fromarray(pixels)
    with rmbg2.rmbg2_session() as predict:
        predict(image)

    resized = np.array(image.resize((1024, 1024), Image.Resampling.BILINEAR), copy=True)
    expected = torch.from_numpy(resized).permute(2, 0, 1).to(dtype=torch.float32).div(255)
    expected = (expected - torch.tensor([0.485, 0.456, 0.406])[:, None, None]) / torch.tensor([0.229, 0.224, 0.225])[:, None, None]
    assert torch.equal(model.calls[0], expected.unsqueeze(0))


@pytest.mark.parametrize("failure", ["placement", "inference", "consumer"])
def test_cleanup_on_failure(monkeypatch, management, failure):
    model = _Model()
    monkeypatch.setattr(rmbg2, "_load_model", lambda _path: model)
    if failure == "placement":
        original_to = model.to

        def failed_to(*args, **kwargs):
            if kwargs.get("dtype") == torch.float32:
                raise RuntimeError("placement failed")
            return original_to(*args, **kwargs)

        model.to = failed_to
    elif failure == "inference":
        monkeypatch.setattr(_Model, "__call__", lambda *_args: (_ for _ in ()).throw(RuntimeError("inference failed")))

    with pytest.raises(RuntimeError, match=f"{failure} failed"):
        with rmbg2.rmbg2_session() as predict:
            if failure == "inference":
                predict(Image.new("RGB", (3, 2)))
            else:
                raise RuntimeError("consumer failed")
    assert model.moves[-1] == ((torch.device("cpu"),), {})
    assert management == [("empty",)]


def test_accelerator_reservation_is_targeted_and_model_reference_is_released(monkeypatch, management):
    refs = []

    def load(_path):
        model = _Model()
        refs.append(weakref.ref(model))
        return model

    device = torch.device("cuda:0")
    monkeypatch.setattr(rmbg2, "_load_model", load)
    monkeypatch.setattr(rmbg2.model_management, "get_torch_device", lambda: device)
    with rmbg2.rmbg2_session() as predict:
        assert refs[0]() is not None
    assert refs[0]() is None
    assert callable(predict)  # A retained callable cannot retain model weights.
    assert management == [("free", (40, device)), ("empty",)]
