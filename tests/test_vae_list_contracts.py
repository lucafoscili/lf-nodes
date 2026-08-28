"""Mixed-resolution list/batch contracts for the LF VAE wrappers."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
import sys
import uuid

import pytest
import torch


ROOT = Path(__file__).resolve().parents[1]
LOGIC_ROOT = ROOT / "modules" / "utils" / "helpers" / "logic"
LATENT_NODE_ROOT = ROOT / "modules" / "nodes" / "latent"


def _attach(name: str, module: ModuleType) -> ModuleType:
    sys.modules[name] = module
    if "." in name:
        parent_name, child_name = name.rsplit(".", 1)
        parent = sys.modules.get(parent_name)
        if parent is not None:
            setattr(parent, child_name, module)
    return module


def _package(name: str) -> ModuleType:
    package = ModuleType(name)
    package.__path__ = []
    return _attach(name, package)


def _module(name: str, **attributes) -> ModuleType:
    module = ModuleType(name)
    for key, value in attributes.items():
        setattr(module, key, value)
    return _attach(name, module)


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    _attach(name, module)
    spec.loader.exec_module(module)
    return module


def _load_nodes():
    prefix = f"_lf_vae_contract_{uuid.uuid4().hex}"
    _package(prefix)
    _package(f"{prefix}.nodes")
    latent_package = _package(f"{prefix}.nodes.latent")
    latent_package.CATEGORY = "test"
    _package(f"{prefix}.utils")
    _package(f"{prefix}.utils.helpers")
    logic_package = _package(f"{prefix}.utils.helpers.logic")

    for module_name in (
        "not_none",
        "normalize_input_image",
        "normalize_list_to_value",
        "normalize_output_image",
        "normalize_input_latent",
        "normalize_output_latent",
    ):
        loaded = _load(
            f"{prefix}.utils.helpers.logic.{module_name}",
            LOGIC_ROOT / f"{module_name}.py",
        )
        for exported_name in dir(loaded):
            if exported_name.startswith("normalize_"):
                setattr(logic_package, exported_name, getattr(loaded, exported_name))

    class Input:
        IMAGE = "IMAGE"
        LATENT = "LATENT"
        VAE = "VAE"
        LF_CODE = "LF_CODE"

    _module(f"{prefix}.utils.constants", FUNCTION="on_exec", Input=Input)
    sent = []
    _module(
        f"{prefix}.utils.helpers.comfy",
        safe_send_sync=lambda event, payload, node_id: sent.append(
            (event, payload, node_id)
        ),
    )

    encode_module = _load(
        f"{prefix}.nodes.latent.vae_encode",
        LATENT_NODE_ROOT / "vae_encode.py",
    )
    decode_module = _load(
        f"{prefix}.nodes.latent.vae_decode",
        LATENT_NODE_ROOT / "vae_decode.py",
    )
    return encode_module, decode_module, sent


class IdentityVAE:
    def __init__(self) -> None:
        self.encode_shapes: list[tuple[int, ...]] = []
        self.decode_shapes: list[tuple[int, ...]] = []

    def encode(self, image: torch.Tensor) -> torch.Tensor:
        self.encode_shapes.append(tuple(image.shape))
        return image.permute(0, 3, 1, 2).contiguous()

    def decode(self, latent: torch.Tensor) -> torch.Tensor:
        self.decode_shapes.append(tuple(latent.shape))
        return latent[:, :3].permute(0, 2, 3, 1).contiguous()


def test_vae_encode_and_decode_keep_mixed_resolution_items_losslessly() -> None:
    encode_module, decode_module, sent = _load_nodes()
    vae = IdentityVAE()
    first = torch.full((1, 4, 6, 3), 0.2)
    second = torch.full((1, 3, 5, 3), 0.8)

    latent_batch, latent_list = encode_module.LF_VAEEncode().on_exec(
        pixels=[[first], second],
        vae=[vae],
        node_id=[["encode-node"]],
    )

    assert latent_batch["samples"].shape == (1, 3, 4, 6)
    assert [tuple(item["samples"].shape) for item in latent_list] == [
        (1, 3, 4, 6),
        (1, 3, 3, 5),
    ]
    assert [float(item["samples"][0, 0, 0, 0]) for item in latent_list] == pytest.approx([
        0.2,
        0.8,
    ])

    image_batch, image_list = decode_module.LF_VAEDecode().on_exec(
        samples=[latent_list],
        vae=[vae],
        node_id=[["decode-node"]],
    )

    assert image_batch.shape == (1, 4, 6, 3)
    assert [tuple(image.shape) for image in image_list] == [
        (1, 4, 6, 3),
        (1, 3, 5, 3),
    ]
    assert torch.equal(image_list[0], first)
    assert torch.equal(image_list[1], second)
    assert [event for event, _payload, _node_id in sent] == [
        "vaeencode",
        "vaeencode",
        "vaedecode",
        "vaedecode",
    ]


def test_vae_wrappers_preserve_coherent_batch_calls() -> None:
    encode_module, decode_module, _sent = _load_nodes()
    vae = IdentityVAE()
    coherent = torch.stack(
        (
            torch.full((4, 6, 3), 0.2),
            torch.full((4, 6, 3), 0.8),
        )
    )

    latent_batch, latent_list = encode_module.LF_VAEEncode().on_exec(
        pixels=[coherent],
        vae=[vae],
    )

    assert vae.encode_shapes == [(2, 4, 6, 3)]
    assert latent_batch["samples"].shape == (2, 3, 4, 6)
    assert len(latent_list) == 2

    image_batch, image_list = decode_module.LF_VAEDecode().on_exec(
        samples=[latent_batch],
        vae=[vae],
    )

    assert vae.decode_shapes == [(2, 3, 4, 6)]
    assert image_batch.shape == (2, 4, 6, 3)
    assert len(image_list) == 2
    torch.testing.assert_close(image_batch, coherent)


def test_vae_decode_flattens_temporal_frames_without_reordering() -> None:
    _encode_module, decode_module, _sent = _load_nodes()

    class TemporalVAE:
        def __init__(self) -> None:
            self.decode_shapes: list[tuple[int, ...]] = []

        def decode(self, latent: torch.Tensor) -> torch.Tensor:
            self.decode_shapes.append(tuple(latent.shape))
            batches = []
            for batch_index in range(int(latent.shape[0])):
                batches.append(
                    torch.stack(
                        (
                            torch.full((3, 4, 3), batch_index * 10 + 1.0),
                            torch.full((3, 4, 3), batch_index * 10 + 2.0),
                        )
                    )
                )
            return torch.stack(batches)

    vae = TemporalVAE()
    latent = {"samples": torch.zeros((2, 4, 3, 4))}

    image_batch, image_list = decode_module.LF_VAEDecode().on_exec(
        samples=[latent],
        vae=[vae],
    )

    assert vae.decode_shapes == [(2, 4, 3, 4)]
    assert image_batch.shape == (4, 3, 4, 3)
    assert len(image_list) == 4
    assert [float(image[0, 0, 0, 0]) for image in image_list] == [
        1.0,
        2.0,
        11.0,
        12.0,
    ]
