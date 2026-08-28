from __future__ import annotations

import pytest

from modules.nodes.configuration import civitai_metadata_setup
from modules.nodes.selector.checkpoint_selector import LF_CheckpointSelector
from modules.nodes.selector.diffusion_model_selector import LF_DiffusionModelSelector
from modules.nodes.selector.sampler_selector import LF_SamplerSelector
from modules.nodes.selector.scheduler_selector import LF_SchedulerSelector
from modules.nodes.selector.upscale_model_selector import LF_UpscaleModelSelector
from modules.nodes.selector.vae_selector import LF_VAESelector
from modules.utils.constants import Input


@pytest.mark.parametrize(
    ("name", "expected_options"),
    (
        ("checkpoint", civitai_metadata_setup.CHECKPOINT_VALUES),
        ("unet", civitai_metadata_setup.UNET_VALUES),
        ("vae", civitai_metadata_setup.VAE_VALUES),
        ("sampler", civitai_metadata_setup.SAMPLERS),
        ("scheduler", civitai_metadata_setup.SCHEDULERS),
        ("hires_upscaler", civitai_metadata_setup.UPSCALER_VALUES),
    ),
)
def test_v3_optional_combos_publish_none_as_a_real_option(
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    expected_options: list[str],
) -> None:
    monkeypatch.setattr(civitai_metadata_setup, "HAS_V3", True)
    inputs = civitai_metadata_setup.LF_CivitAIMetadataSetup.INPUT_TYPES()["optional"]

    input_type, config = inputs[name]
    assert input_type == Input.COMBO
    assert config["default"] == "None"
    assert config["options"] == [
        "None",
        *(option for option in expected_options if option != "None"),
    ]


@pytest.mark.parametrize(
    ("name", "expected_options"),
    (
        ("checkpoint", civitai_metadata_setup.CHECKPOINT_VALUES),
        ("unet", civitai_metadata_setup.UNET_VALUES),
        ("vae", civitai_metadata_setup.VAE_VALUES),
        ("sampler", civitai_metadata_setup.SAMPLERS),
        ("scheduler", civitai_metadata_setup.SCHEDULERS),
        ("hires_upscaler", civitai_metadata_setup.UPSCALER_VALUES),
    ),
)
def test_legacy_optional_combos_keep_exact_list_socket_types(
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    expected_options: list[str],
) -> None:
    monkeypatch.setattr(civitai_metadata_setup, "HAS_V3", False)
    inputs = civitai_metadata_setup.LF_CivitAIMetadataSetup.INPUT_TYPES()["optional"]

    input_type, config = inputs[name]
    expected = list(expected_options)
    assert input_type == expected
    if expected:
        assert config["default"] == expected[0]
    else:
        assert "default" not in config


def test_combo_outputs_remain_legacy_lists_for_core_receiver_compatibility() -> None:
    output_types = civitai_metadata_setup.LF_CivitAIMetadataSetup.RETURN_TYPES

    assert output_types[1] is civitai_metadata_setup.CHECKPOINT_VALUES
    assert output_types[2] is civitai_metadata_setup.UNET_VALUES
    assert output_types[3] is civitai_metadata_setup.VAE_VALUES
    assert output_types[4] is civitai_metadata_setup.SAMPLERS
    assert output_types[5] is civitai_metadata_setup.SCHEDULERS
    assert output_types[17] is civitai_metadata_setup.UPSCALER_VALUES

    for selector in (
        LF_CheckpointSelector,
        LF_DiffusionModelSelector,
        LF_VAESelector,
        LF_SamplerSelector,
        LF_SchedulerSelector,
        LF_UpscaleModelSelector,
    ):
        assert isinstance(selector.RETURN_TYPES[0], list)


def test_v3_consumers_accept_every_concrete_producer_option_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(civitai_metadata_setup, "HAS_V3", True)
    inputs = civitai_metadata_setup.LF_CivitAIMetadataSetup.INPUT_TYPES()["optional"]
    pairs = (
        (LF_CheckpointSelector.RETURN_TYPES[0], "checkpoint"),
        (LF_DiffusionModelSelector.RETURN_TYPES[0], "unet"),
        (LF_VAESelector.RETURN_TYPES[0], "vae"),
        (LF_SamplerSelector.RETURN_TYPES[0], "sampler"),
        (LF_SchedulerSelector.RETURN_TYPES[0], "scheduler"),
        (LF_UpscaleModelSelector.RETURN_TYPES[0], "hires_upscaler"),
    )

    for producer_options, input_name in pairs:
        input_type, config = inputs[input_name]
        assert isinstance(producer_options, list)
        assert input_type == Input.COMBO
        assert config["options"] == [
            "None",
            *(option for option in producer_options if option != "None"),
        ]


def test_none_sentinels_do_not_trigger_hashes_or_resource_receipts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        civitai_metadata_setup,
        "get_sha256",
        lambda _path: pytest.fail("None must not be hashed"),
    )
    monkeypatch.setattr(civitai_metadata_setup, "safe_send_sync", lambda *_args, **_kwargs: None)

    result = civitai_metadata_setup.LF_CivitAIMetadataSetup().on_exec(
        model_type="none",
        checkpoint="None",
        unet="None",
        vae="None",
        sampler="None",
        scheduler="None",
        embeddings="",
        lora_tags="",
        positive_prompt="",
        negative_prompt="",
        steps=30,
        denoising=1.0,
        clip_skip=-1,
        cfg=7.0,
        seed=0,
        width=1024,
        height=1024,
        hires_upscaler="None",
        hires_upscale=1.5,
    )

    assert "VAE hash: Unknown" in result[0]
    assert "Hires upscaler: Latent" in result[0]
    assert result[-1] == {"nodes": []}
