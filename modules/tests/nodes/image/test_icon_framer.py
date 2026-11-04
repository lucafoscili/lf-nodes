from __future__ import annotations

import pytest
import torch

from modules.nodes.image import icon_framer as icon_framer_module
from modules.nodes.image.icon_framer import LF_IconFramer, frame_icon


def _subject(height: int = 96, width: int = 128) -> tuple[torch.Tensor, torch.Tensor]:
    """A red square subject off-centre on a white field, with its mask."""

    image = torch.ones(1, height, width, 3)
    mask = torch.zeros(1, height, width)
    image[0, 20:50, 70:100] = torch.tensor([1.0, 0.0, 0.0])
    mask[0, 20:50, 70:100] = 1.0
    return image, mask


def test_schema_is_published_as_list_mode_with_four_outputs() -> None:
    schema = LF_IconFramer.INPUT_TYPES()
    assert list(schema["required"])[:2] == ["image", "mask"]
    assert schema["required"]["backdrop"][0] == icon_framer_module.BACKDROPS
    assert "ui_widget" in schema["optional"]
    assert LF_IconFramer.INPUT_IS_LIST is True
    assert LF_IconFramer.RETURN_NAMES == ("master", "master_list", "icon", "icon_list")
    assert LF_IconFramer.RETURN_TYPES == ("IMAGE", "IMAGE", "IMAGE", "IMAGE")
    assert LF_IconFramer.OUTPUT_IS_LIST == (False, True, False, True)


def test_subject_is_centred_and_fills_the_inner_square() -> None:
    image, mask = _subject()
    master, icon = frame_icon(
        image, mask, master_size=100, icon_size=20, fill=0.8, bevel=0.0, outline=0.0, vignette=0.0,
    )
    assert master.shape == (1, 100, 100, 3)
    assert icon.shape == (1, 20, 20, 3)
    red = (master[0, ..., 0] > 0.5) & (master[0, ..., 1] < 0.5)
    ys, xs = torch.nonzero(red, as_tuple=True)
    # The 30 px subject fills 80% of the square: 80 px, centred.
    assert 78 <= int(ys.max() - ys.min() + 1) <= 82
    assert 78 <= int(xs.max() - xs.min() + 1) <= 82
    assert abs(float(ys.float().mean()) - 49.5) < 1.5
    assert abs(float(xs.float().mean()) - 49.5) < 1.5
    # Everything else is the black backdrop.
    assert float(master[0, 2, 2].max()) == pytest.approx(0.0, abs=1e-6)


def test_source_backdrop_keeps_the_surroundings_and_pads_with_the_colour() -> None:
    image, mask = _subject()
    master, _ = frame_icon(
        image, mask, master_size=64, icon_size=16, fill=0.25, backdrop="source",
        backdrop_color="#0000ff", bevel=0.0, outline=0.0, vignette=0.0,
    )
    # Above the subject lies the white source field; the crop reaches past the top edge,
    # where the blue backdrop colour fills in.
    assert master[0, 20, 32].tolist() == pytest.approx([1.0, 1.0, 1.0], abs=0.02)
    assert master[0, 0, 32].tolist() == pytest.approx([0.0, 0.0, 1.0], abs=0.02)


def test_rim_is_lit_top_left_and_shaded_bottom_right() -> None:
    image, mask = _subject()
    master, _ = frame_icon(image, mask, master_size=200, icon_size=50, bevel=0.05, vignette=0.0)
    width = 10
    top = master[0, width // 2, 100].mean()
    bottom = master[0, 199 - width // 2, 100].mean()
    left = master[0, 100, width // 2].mean()
    right = master[0, 100, 199 - width // 2].mean()
    assert float(top) > float(bottom)
    assert float(left) > float(right)
    assert float(top) > 0.3


def test_glow_lights_the_backdrop_around_the_subject() -> None:
    image, mask = _subject()
    plain, _ = frame_icon(image, mask, master_size=100, icon_size=20, fill=0.5, bevel=0.0, vignette=0.0, outline=0.0)
    glow, _ = frame_icon(
        image, mask, master_size=100, icon_size=20, fill=0.5, bevel=0.0, vignette=0.0, outline=0.0,
        glow_color="#00ff00", glow_strength=1.0,
    )
    assert float(glow[0, 50, 20, 1]) > float(plain[0, 50, 20, 1]) + 0.1


def test_empty_mask_and_bad_colour_fail_loud() -> None:
    image, mask = _subject()
    with pytest.raises(ValueError, match="no subject"):
        frame_icon(image, torch.zeros_like(mask))
    with pytest.raises(ValueError, match="backdrop_color"):
        frame_icon(image, mask, backdrop_color="black")
    with pytest.raises(ValueError, match="must match"):
        frame_icon(image, mask[:, :10])


def test_on_exec_pairs_images_with_one_shared_mask_and_sends_the_compare(monkeypatch) -> None:
    sent = []
    monkeypatch.setattr(icon_framer_module, "safe_send_sync", lambda event, payload, node_id: sent.append((event, payload, node_id)))
    monkeypatch.setattr(icon_framer_module, "create_cached_compare_node", lambda before, after, index: {"id": f"image_{index + 1}"})
    image, mask = _subject()
    result = LF_IconFramer().on_exec(
        image=[image, image.clone()], mask=[mask], master_size=[64], icon_size=[16], node_id=["7"],
    )
    master, master_list, icon, icon_list = result["result"]
    assert master.shape == (2, 64, 64, 3)
    assert icon.shape == (2, 16, 16, 3)
    assert len(master_list) == 2 and len(icon_list) == 2
    assert sent[0][0] == "iconframer"
    assert sent[0][2] == "7"
    assert result["ui"]["lf_output"] == [sent[0][1]]
    assert [node["id"] for node in sent[0][1]["dataset"]["nodes"]] == ["image_1", "image_2"]
