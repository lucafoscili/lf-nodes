from __future__ import annotations

import pytest
import torch

from modules.nodes.filters import inpaint, inpaint_advanced
from modules.utils.filters import inpaint as inpaint_filter


@pytest.mark.parametrize(
    ("module", "node", "controls"),
    [
        (
            inpaint,
            inpaint.LF_Inpaint(),
            {
                "steps": [8],
                "denoise_percentage": [40.0],
                "cfg": [1.0],
                "sampler": ["euler"],
                "scheduler": ["normal"],
                "upsample_target": [0],
            },
        ),
        (
            inpaint_advanced,
            inpaint_advanced.LF_InpaintAdvanced(),
            {
                "steps": [8],
                "denoise": [0.4],
                "cfg": [1.0],
                "sampler": ["euler"],
                "scheduler": ["normal"],
                "seed": [42],
                "roi_auto": [True],
                "roi_padding": [0],
                "roi_align": [8],
                "roi_align_auto": [False],
                "roi_min_size": [1],
                "dilate": [0],
                "feather": [0],
                "upsample_target": [0],
            },
        ),
    ],
)
def test_inpaint_nodes_preserve_semantic_conditioning_in_true_list_mode(
    monkeypatch,
    module,
    node,
    controls: dict,
) -> None:
    images = torch.zeros((2, 3, 4, 3), dtype=torch.float32)
    masks = torch.ones((2, 3, 4), dtype=torch.float32)
    model, clip, vae = object(), object(), object()
    positive = [[torch.tensor([1.0]), {"label": "positive"}]]
    negative = [[torch.tensor([0.0]), {"label": "negative"}]]
    calls = []

    def fake_apply(**kwargs):
        calls.append(kwargs)
        return kwargs["image"], {}

    monkeypatch.setattr(module, "apply_inpaint_filter_tensor", fake_apply)
    monkeypatch.setattr(
        module,
        "process_and_save_image",
        lambda images, filter_function, filter_args, nodes: [
            filter_function(image, **filter_args) for image in images
        ],
    )
    monkeypatch.setattr(module, "safe_send_sync", lambda *_args: None)

    response = node.on_exec(
        image=[images],
        mask=[masks],
        model=[model],
        clip=[clip],
        vae=[vae],
        positive_prompt=["edit"],
        negative_prompt=[""],
        positive_conditioning=[positive],
        negative_conditioning=[negative],
        **controls,
    )

    assert node.INPUT_IS_LIST is True
    assert len(response["result"][1]) == 2
    assert len(calls) == 2
    assert all(call["model"] is model for call in calls)
    assert all(call["clip"] is clip for call in calls)
    assert all(call["vae"] is vae for call in calls)
    assert all(call["settings"]["positive_conditioning"] is positive for call in calls)
    assert all(call["settings"]["negative_conditioning"] is negative for call in calls)


def test_tensor_inpaint_treats_a_zero_mask_as_a_model_free_noop(monkeypatch) -> None:
    image = torch.tensor([[[[0.2, 0.4, 0.6, 0.8]]]], dtype=torch.float32)
    mask = torch.zeros((1, 1, 1), dtype=torch.float32)

    def fail_if_sampled(**_kwargs):
        raise AssertionError("an empty mask must not enter the diffusion/VAE path")

    monkeypatch.setattr(inpaint_filter, "perform_inpaint", fail_if_sampled)

    processed, info = inpaint_filter.apply_inpaint_filter_tensor(
        image=image,
        mask=mask,
        model=object(),
        clip=object(),
        vae=object(),
        settings={},
    )

    assert torch.equal(processed, image)
    assert processed.shape == (1, 1, 1, 4)
    assert info == {"status": "noop", "reason": "empty_mask"}


def test_zero_source_mask_still_allows_an_explicit_outpaint_band(monkeypatch) -> None:
    image = torch.full((1, 16, 16, 3), 0.25, dtype=torch.float32)
    mask = torch.zeros((1, 16, 16), dtype=torch.float32)
    sampled_masks = []

    def fake_sample(*, image, mask, **_kwargs):
        sampled_masks.append(mask.clone())
        return image

    monkeypatch.setattr(inpaint_filter, "perform_inpaint", fake_sample)

    processed, info = inpaint_filter.apply_inpaint_filter_tensor(
        image=image,
        mask=mask,
        model=object(),
        clip=object(),
        vae=object(),
        settings={
            "outpaint_amount": 8,
            "outpaint_top": True,
            "roi_auto": False,
            "dilate": 0,
            "feather": 0,
            "apply_unsharp_mask": False,
        },
    )

    assert len(sampled_masks) == 1
    assert bool((sampled_masks[0] > 0.5).any())
    assert processed.shape == (1, 24, 16, 3)
    assert info.get("status") != "noop"


@pytest.mark.parametrize(
    ("module", "node", "controls"),
    [
        (
            inpaint,
            inpaint.LF_Inpaint(),
            {
                "steps": [8],
                "denoise_percentage": [40.0],
                "cfg": [1.0],
                "sampler": ["euler"],
                "scheduler": ["normal"],
                "upsample_target": [0],
            },
        ),
        (
            inpaint_advanced,
            inpaint_advanced.LF_InpaintAdvanced(),
            {
                "steps": [8],
                "denoise": [0.4],
                "cfg": [1.0],
                "sampler": ["euler"],
                "scheduler": ["normal"],
                "seed": [42],
                "roi_auto": [True],
                "roi_padding": [0],
                "roi_align": [8],
                "roi_align_auto": [False],
                "roi_min_size": [1],
                "dilate": [0],
                "feather": [0],
                "upsample_target": [0],
            },
        ),
    ],
)
def test_inpaint_nodes_share_the_zero_mask_noop_contract(
    monkeypatch,
    module,
    node,
    controls: dict,
) -> None:
    image = torch.tensor([[[[0.1, 0.3, 0.7]]]], dtype=torch.float32)
    mask = torch.zeros((1, 1, 1), dtype=torch.float32)

    def fail_if_sampled(**_kwargs):
        raise AssertionError("an empty mask must not enter the diffusion/VAE path")

    monkeypatch.setattr(inpaint_filter, "perform_inpaint", fail_if_sampled)
    monkeypatch.setattr(
        module,
        "process_and_save_image",
        lambda images, filter_function, filter_args, nodes: [
            filter_function(item, **filter_args) for item in images
        ],
    )
    monkeypatch.setattr(module, "safe_send_sync", lambda *_args: None)

    response = node.on_exec(
        image=[image],
        mask=[mask],
        model=[object()],
        clip=[object()],
        vae=[object()],
        **controls,
    )

    primary_batch, image_list = response["result"]
    assert torch.equal(primary_batch, image)
    assert len(image_list) == 1
    assert torch.equal(image_list[0], image)
