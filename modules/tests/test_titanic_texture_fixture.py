"""Execute the Titanic texture specimen's settings through the real CPU nodes.

The live case asserts named values in each node's history; this proves offline
that the pinned stock example and the checked-in widget values produce them.
"""
import numpy as np
import pytest
import torch

from modules.nodes.texture.detail_transfer import LF_DetailTransfer
from modules.nodes.texture.edge_padding import LF_EdgePadding
from modules.nodes.texture.masked_lab_grade import LF_MaskedLabGrade
from modules.nodes.texture.normal_map_repack import LF_NormalMapRepack
from modules.tests.titanic_specimen import (assert_named_values, case as manifest_case, generator, placed,
                                            stock_example, widgets)
from modules.utils.helpers.ui import generated_preview


@pytest.fixture(autouse=True)
def preview_root(monkeypatch, tmp_path):
    monkeypatch.setattr(generated_preview, "get_comfy_dir", lambda _kind: str(tmp_path / "input"))
    from modules.nodes.texture import detail_transfer, edge_padding, masked_lab_grade, normal_map_repack
    for module in (detail_transfer, edge_padding, masked_lab_grade, normal_map_repack):
        monkeypatch.setattr(module, "safe_send_sync", lambda *_args: None)


def test_specimen_settings_produce_the_case_expectations():
    case = manifest_case("cpu.texture-tools")
    assert case == generator("texture").CASE
    example = stock_example()
    square, band = placed(655, 656, 657), placed(655, 658, 659)
    outputs = {}
    outputs["660"] = LF_MaskedLabGrade().on_exec(image=[example], mask=[square], reference_image=[example],
                                                 reference_mask=[band], **widgets(660))
    graded = outputs["660"]["result"][0]
    outputs["661"] = LF_DetailTransfer().on_exec(image=[graded], detail_source=[example], mask=[square],
                                                 reference_image=[example], reference_mask=[square],
                                                 **widgets(661))
    outputs["662"] = LF_EdgePadding().on_exec(image=[outputs["661"]["result"][0]], mask=[square], **widgets(662))
    normal = widgets(664)
    color = normal["color"][0]
    rgb = [int(color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    flat = torch.tensor(rgb).expand(1, normal["height"][0], normal["width"][0], 3).clone()
    outputs["665"] = LF_NormalMapRepack().on_exec(image=[flat], **widgets(665))
    assert_named_values(case, outputs)
    # The grade moved the square toward the band, and the detail transfer put fine detail back.
    grade = outputs["660"]["result"][1]["images"][0]
    # sRGB clipping keeps the darkest blues short of the band, so the gap closes most of the way, not all.
    before, after = (np.subtract(grade[key]["lab_mean"], grade["reference"]["lab_mean"]) for key in ("target", "result"))
    assert np.linalg.norm(after) < 0.25 * np.linalg.norm(before)
    assert grade["clipped_pixels"] > 0
    detail = outputs["661"]["result"][1]["images"][0]
    assert detail["result_fine_l_std"] == pytest.approx(detail["reference_fine_l_std"], rel=0.1)
    repacked = outputs["665"]["result"][0]
    assert float(repacked[0, 0, 0, 1]) < 0.5 < float(flat[0, 0, 0, 1])
