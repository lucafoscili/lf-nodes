import importlib.util
import sys
from pathlib import Path

import torch


def _load_inpaint_module():
    """
    Load the lf_nodes inpaint module in a way that matches how ComfyUI
    loads the custom node package, so relative imports continue to work.
    """
    if "lf_nodes" not in sys.modules:
        lf_root = Path(__file__).resolve().parents[5]
        init_path = lf_root / "__init__.py"
        spec = importlib.util.spec_from_file_location("lf_nodes", init_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["lf_nodes"] = module
        assert spec.loader is not None
        spec.loader.exec_module(module)

    from lf_nodes.modules.utils.filters import inpaint as inpaint_module  # type: ignore[import]

    # Disable debug preview saves during tests to avoid file I/O noise.
    try:
        inpaint_module.DEBUG_PREVIEW_SAVES = False
    except AttributeError:
        pass

    return inpaint_module


class _DummyFirstStage:
    def __init__(self, device):
        self.device = device


class _DummyVAE:
    def __init__(self, device):
        self.first_stage_model = _DummyFirstStage(device)
        self.downscale_factor = 8


def _base_settings():
    # Minimal settings; helper functions in inpaint.py provide defaults.
    return {
        "steps": 4,
        "denoise": 0.5,
        "cfg": 7.0,
        "sampler": "dpmpp_2m",
        "scheduler": "karras",
        "seed": 1,
        "conditioning_mix": 0.0,
    }


def test_prepare_inpaint_region_crops_to_mask_bbox():
    inpaint = _load_inpaint_module()

    h, w = 64, 64
    base_image = torch.zeros((1, h, w, 3), dtype=torch.float32)
    mask = torch.zeros((1, h, w), dtype=torch.float32)
    # Simple square stroke in the centre
    mask[:, 16:32, 20:40] = 1.0

    vae = _DummyVAE(device=base_image.device)
    settings = {"roi_auto": True, "roi_padding": 0, "roi_min_size": 8}

    work_image, work_mask_soft, paste_roi, meta = inpaint._prepare_inpaint_region(  # type: ignore[attr-defined]
        base_image=base_image,
        mask_tensor=mask,
        vae=vae,
        settings=settings,
    )

    y0, x0, y1, x1 = paste_roi
    roi_h = y1 - y0
    roi_w = x1 - x0

    # Work tensors must match the cropped ROI dimensions
    assert work_image.shape[1] == roi_h
    assert work_image.shape[2] == roi_w
    assert work_mask_soft.shape[1] == roi_h
    assert work_mask_soft.shape[2] == roi_w

    # Meta should report the original image shape
    assert meta["image_shape"] == (h, w)


def test_patch_outpainting_expands_only_roi(monkeypatch):
    inpaint = _load_inpaint_module()

    h, w = 64, 64
    base_image = torch.zeros((1, h, w, 3), dtype=torch.float32)
    # Mask covering the full image so it touches all edges.
    mask = torch.ones((1, h, w), dtype=torch.float32)

    vae = _DummyVAE(device=base_image.device)
    settings = _base_settings()

    captured = {}

    def fake_perform_inpaint(*, image, mask, **kwargs):
        captured["image_shape"] = tuple(image.shape)
        captured["mask_shape"] = tuple(mask.shape)
        # Return the input image unchanged.
        return image

    monkeypatch.setattr(inpaint, "perform_inpaint", fake_perform_inpaint)

    processed, _ = inpaint.apply_inpaint_filter_tensor(  # type: ignore[attr-defined]
        image=base_image,
        mask=mask,
        model=object(),
        clip=object(),
        vae=vae,
        settings=settings,
    )

    # Outpainting margin in the implementation is 32px on each touched side.
    outpaint_margin = 32
    expected_h = h + 2 * outpaint_margin
    expected_w = w + 2 * outpaint_margin

    assert captured["image_shape"][1] == expected_h
    assert captured["image_shape"][2] == expected_w
    assert captured["mask_shape"][1] == expected_h
    assert captured["mask_shape"][2] == expected_w

    # Final composited image should still match the original canvas size.
    assert processed.shape == base_image.shape


def test_finalize_inpaint_respects_mask_for_paste():
    inpaint = _load_inpaint_module()

    h, w = 48, 48
    base_image = torch.zeros((1, h, w, 3), dtype=torch.float32)
    mask = torch.zeros((1, h, w), dtype=torch.float32)
    # Smaller ROI well inside the frame so seam logic is inactive.
    mask[:, 8:32, 10:34] = 1.0

    vae = _DummyVAE(device=base_image.device)
    settings = {}

    work_image, _, paste_roi, meta = inpaint._prepare_inpaint_region(  # type: ignore[attr-defined]
        base_image=base_image,
        mask_tensor=mask,
        vae=vae,
        settings=settings,
    )

    # Simulate diffusion having filled the ROI with ones.
    processed_region = torch.ones_like(work_image)

    # Force edge-touch metadata off so seam smoothing does not modify borders.
    meta["edge_touch"] = {"top": False, "bottom": False, "left": False, "right": False}
    meta["roi_edge_touch"] = {
        "top": False,
        "bottom": False,
        "left": False,
        "right": False,
    }

    result, _ = inpaint._finalize_inpaint_output(  # type: ignore[attr-defined]
        processed_region=processed_region,
        base_image=base_image,
        paste_roi=paste_roi,
        meta=meta,
    )

    assert result.shape == base_image.shape

    y0, x0, y1, x1 = paste_roi
    # Outside the ROI, the image should remain identical to the base (zeros).
    outside = torch.ones_like(result, dtype=torch.bool)
    outside[:, y0:y1, x0:x1, :] = False
    assert torch.all(result[outside] == 0.0)

