from __future__ import annotations

import importlib
import pytest

from modules.nodes.configuration import civitai_metadata_setup
from modules.nodes.selector import checkpoint_selector
from modules.nodes.selector import diffusion_model_selector
from modules.nodes.selector import embedding_selector
from modules.nodes.selector import lora_and_embedding_selector
from modules.nodes.selector import lora_selector
from modules.nodes.selector import sampler_selector
from modules.nodes.selector import scheduler_selector
from modules.nodes.selector import upscale_model_selector
from modules.nodes.selector import vae_selector
from modules.nodes.selector.checkpoint_selector import LF_CheckpointSelector
from modules.nodes.selector.diffusion_model_selector import LF_DiffusionModelSelector
from modules.nodes.selector.embedding_selector import LF_EmbeddingSelector
from modules.nodes.selector.lora_selector import LF_LoraSelector
from modules.nodes.selector.sampler_selector import LF_SamplerSelector
from modules.nodes.selector.scheduler_selector import LF_SchedulerSelector
from modules.nodes.selector.upscale_model_selector import LF_UpscaleModelSelector
from modules.nodes.selector.vae_selector import LF_VAESelector
from modules.utils.helpers.logic.selector_utils import _SelectorListRefresher

# The api package re-exports a process_model function over its module of the same name.
process_model = importlib.import_module("modules.utils.helpers.api.process_model")


@pytest.mark.parametrize(
    "node_class",
    (
        LF_CheckpointSelector,
        LF_DiffusionModelSelector,
        LF_EmbeddingSelector,
        LF_LoraSelector,
        LF_SamplerSelector,
        LF_SchedulerSelector,
        LF_UpscaleModelSelector,
        LF_VAESelector,
    ),
)
def test_selector_combo_outputs_publish_concrete_option_lists(node_class) -> None:
    assert isinstance(node_class.RETURN_TYPES[0], list)


@pytest.mark.parametrize(
    ("node_class", "input_name"),
    (
        (LF_CheckpointSelector, "checkpoint"),
        (LF_SamplerSelector, "sampler"),
        (LF_SchedulerSelector, "scheduler"),
        (LF_VAESelector, "vae"),
    ),
)
def test_no_selection_remains_an_explicit_prompt_option(
    node_class,
    input_name: str,
) -> None:
    input_config = node_class.INPUT_TYPES()["required"][input_name]

    assert input_config[0][0] == "None"
    assert input_config[1]["default"] == "None"


@pytest.mark.parametrize(
    ("module", "node_class", "input_name", "label", "extra"),
    (
        (checkpoint_selector, LF_CheckpointSelector, "checkpoint", "Checkpoint selector", {}),
        (
            diffusion_model_selector,
            LF_DiffusionModelSelector,
            "diffusion_model",
            "Diffusion model selector",
            {"weight_dtype": "default"},
        ),
    ),
)
@pytest.mark.parametrize("missing", ("None", None))
def test_model_selectors_fail_loud_when_no_model_arrives(
    monkeypatch: pytest.MonkeyPatch,
    module,
    node_class,
    input_name: str,
    label: str,
    extra: dict,
    missing,
) -> None:
    # An API client can submit the combo's "None" default (issue #120); the node
    # names itself and the remedy instead of letting ComfyUI's path join fail.
    monkeypatch.setattr(module, "get_comfy_list", lambda _kind: ["a.safetensors"])
    monkeypatch.setattr(module, "safe_send_sync", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        module.folder_paths,
        "get_full_path_or_raise",
        lambda *_args: pytest.fail("No model may load without a selection."),
    )
    monkeypatch.setattr(
        module,
        "process_model_async",
        lambda *_args, **_kwargs: pytest.fail("No metadata lookup without a selection."),
    )

    with pytest.raises(ValueError) as raised:
        node_class().on_exec(
            **{
                input_name: missing,
                "get_civitai_info": True,
                "randomize": False,
                "filter": "",
                "seed": 42,
                "node_id": "57",
                **extra,
            }
        )

    message = str(raised.value)
    assert message.startswith(f"{label} (node 57): no ")
    assert "randomize" in message


@pytest.mark.parametrize(
    ("module", "node_class", "input_name"),
    (
        (checkpoint_selector, LF_CheckpointSelector, "checkpoint"),
        (diffusion_model_selector, LF_DiffusionModelSelector, "diffusion_model"),
    ),
)
def test_model_selectors_randomize_on_an_empty_folder_fails_loud(
    monkeypatch: pytest.MonkeyPatch,
    module,
    node_class,
    input_name: str,
) -> None:
    monkeypatch.setattr(module, "get_comfy_list", lambda _kind: [])
    monkeypatch.setattr(module, "safe_send_sync", lambda *_args, **_kwargs: None)

    with pytest.raises(ValueError, match="randomize is on"):
        node_class().on_exec(
            **{
                input_name: "None",
                "get_civitai_info": True,
                "randomize": True,
                "filter": "",
                "seed": 42,
                "node_id": "7",
            }
        )


def test_basic_metadata_never_hands_a_missing_name_to_comfy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        process_model.folder_paths,
        "get_full_path",
        lambda *_args: pytest.fail("ComfyUI's path lookup must not see a missing name."),
    )

    metadata = process_model._build_basic_metadata("checkpoint", None, "checkpoints")

    assert metadata["model_path"] is None
    assert metadata["model_name"] is None


@pytest.mark.parametrize(
    ("module", "node_class", "input_name", "stack_name"),
    (
        (lora_selector, LF_LoraSelector, "lora", "lora_stack"),
        (embedding_selector, LF_EmbeddingSelector, "embedding", "embedding_stack"),
    ),
)
@pytest.mark.parametrize("missing", ("None", None))
def test_stack_selectors_pass_the_stack_through_without_a_selection(
    monkeypatch: pytest.MonkeyPatch,
    module,
    node_class,
    input_name: str,
    stack_name: str,
    missing,
) -> None:
    monkeypatch.setattr(module, "safe_send_sync", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        module,
        "process_model_async",
        lambda *_args, **_kwargs: pytest.fail("Passthrough needs no metadata lookup."),
    )

    result = node_class().on_exec(
        **{
            input_name: missing,
            "get_civitai_info": True,
            "weight": 1.0,
            "randomize": False,
            "filter": "",
            "seed": 42,
            stack_name: "<upstream>",
            "node_id": "9",
        }
    )

    assert result == (None, "<upstream>", "", "", None)


@pytest.mark.parametrize(
    ("module", "node_class", "input_name"),
    (
        (sampler_selector, LF_SamplerSelector, "sampler"),
        (scheduler_selector, LF_SchedulerSelector, "scheduler"),
    ),
)
def test_sampling_no_selection_preserves_published_string_sentinel(
    monkeypatch: pytest.MonkeyPatch,
    module,
    node_class,
    input_name: str,
) -> None:
    monkeypatch.setattr(module, "safe_send_sync", lambda *_args, **_kwargs: None)

    result = node_class().on_exec(
        **{
            input_name: "None",
            "enable_history": False,
            "randomize": False,
            "filter": "",
            "seed": 42,
        }
    )

    assert result == ("None", "None")


def test_vae_no_selection_preserves_string_sentinel_without_loading_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(vae_selector, "get_comfy_list", lambda _kind: [])
    monkeypatch.setattr(vae_selector, "safe_send_sync", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        vae_selector.folder_paths,
        "get_full_path_or_raise",
        lambda *_args: pytest.fail("No VAE may load for the None selection."),
    )

    result = LF_VAESelector().on_exec(
        vae="None",
        enable_history=False,
        randomize=False,
        filter="",
        seed=42,
    )

    assert result == ("None", "None", None)


def test_selector_refresh_preserves_list_identity_and_updates_output_contract() -> None:
    original = ["old"]

    class Selector:
        initial_list = original
        RETURN_TYPES = (original, "STRING")

    refresher = _SelectorListRefresher(Selector, lambda: ["new-a", "new-b"])

    result = refresher.clear()

    assert result is original
    assert Selector.initial_list is original
    assert Selector.RETURN_TYPES[0] is original
    assert Selector.RETURN_TYPES[0] == ["new-a", "new-b"]


def test_missing_selector_inventories_refresh_in_place(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cases = (
        (
            embedding_selector,
            embedding_selector._EMBEDDING_SELECTOR_LIST,
            embedding_selector.LF_EmbeddingSelector.initial_list,
            0,
            "embeddings",
        ),
        (
            upscale_model_selector,
            upscale_model_selector._UPSCALE_MODEL_SELECTOR_LIST,
            upscale_model_selector.LF_UpscaleModelSelector.initial_list,
            0,
            "upscale_models",
        ),
        (
            lora_and_embedding_selector,
            lora_and_embedding_selector._LORA_AND_EMBEDDING_LORA_LIST,
            lora_and_embedding_selector.LF_LoraAndEmbeddingSelector.initial_lora_list,
            0,
            "loras",
        ),
        (
            lora_and_embedding_selector,
            lora_and_embedding_selector._LORA_AND_EMBEDDING_EMBEDDING_LIST,
            lora_and_embedding_selector.LF_LoraAndEmbeddingSelector.initial_emb_list,
            1,
            "embeddings",
        ),
    )

    originals = [(target, list(target)) for _, _, target, _, _ in cases]
    try:
        for module, refresher, target, return_index, folder_name in cases:
            monkeypatch.setattr(
                module,
                "get_comfy_list",
                lambda requested, expected=folder_name: [f"{expected}-refreshed"]
                if requested == expected
                else [],
            )
            result = refresher.clear()
            assert result is target
            assert result == [f"{folder_name}-refreshed"]

            owner = refresher._owner_cls
            assert owner.RETURN_TYPES[return_index] is target
    finally:
        for target, original in originals:
            target[:] = original


def test_civitai_output_inventories_refresh_in_place(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    cases = (
        (civitai_metadata_setup._CIVITAI_CHECKPOINT_LIST, civitai_metadata_setup.CHECKPOINT_VALUES, 1, "checkpoints"),
        (civitai_metadata_setup._CIVITAI_UNET_LIST, civitai_metadata_setup.UNET_VALUES, 2, "unet"),
        (civitai_metadata_setup._CIVITAI_VAE_LIST, civitai_metadata_setup.VAE_VALUES, 3, "vae"),
        (civitai_metadata_setup._CIVITAI_UPSCALER_LIST, civitai_metadata_setup.UPSCALER_VALUES, 17, "upscale_models"),
    )
    original_get_comfy_list = civitai_metadata_setup.get_comfy_list
    originals = [(target, list(target)) for _, target, _, _ in cases]

    try:
        for refresher, target, return_index, folder_name in cases:
            monkeypatch.setattr(
                civitai_metadata_setup,
                "get_comfy_list",
                lambda requested, expected=folder_name: [f"{expected}-refreshed"]
                if requested == expected
                else original_get_comfy_list(requested),
            )
            result = refresher.clear()
            assert result is target
            assert result == [f"{folder_name}-refreshed"]
            assert civitai_metadata_setup.LF_CivitAIMetadataSetup.RETURN_TYPES[return_index] is target
    finally:
        for target, original in originals:
            target[:] = original
