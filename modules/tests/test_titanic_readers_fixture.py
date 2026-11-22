"""Execute the Titanic readers' CPU specimens (cpu.inspection, cpu.tone-readers) through the real nodes.

The live cases assert named values in each node's history; this proves offline that the pinned stock example, its
graded square and the checked-in widget values produce them.
"""
import pytest

from modules.nodes.analytics import (grade_split, image_diff, luma_ratio_map, plot_chart, region_measure, region_reads,
                                     tone_profile)
from modules.nodes.regions import text_region_masks
from modules.nodes.texture import masked_lab_grade
from modules.tests import titanic_specimen as titanic
from modules.utils.helpers.ui import generated_preview

READERS = (grade_split, image_diff, luma_ratio_map, plot_chart, region_measure, region_reads, tone_profile,
           text_region_masks, masked_lab_grade)


@pytest.fixture(autouse=True)
def preview_root(monkeypatch, tmp_path):
    monkeypatch.setattr(generated_preview, "get_comfy_dir", lambda _kind: str(tmp_path / "input"))
    for module in READERS:
        monkeypatch.setattr(module, "safe_send_sync", lambda *_args: None)


@pytest.fixture(scope="module")
def texture():
    """The texture case's before (654), square (657), band (659) and after (Masked Lab grade 660)."""
    example = titanic.stock_example()
    square, band = titanic.placed(655, 656, 657), titanic.placed(655, 658, 659)
    graded = masked_lab_grade.LF_MaskedLabGrade().on_exec(
        image=[example], mask=[square], reference_image=[example], reference_mask=[band],
        **titanic.widgets(660))["result"][0]
    return example, square, band, graded


def test_the_generator_is_the_manifest():
    cases = {item["id"]: item for item in titanic.generator("readers").CASES}
    for identifier, item in cases.items():
        assert titanic.case(identifier) == item


def test_inspection_settings_produce_the_case_expectations(texture):
    example, square, _band, graded = texture
    outputs = {
        "678": image_diff.LF_ImageDiff().on_exec(image_a=[example], image_b=[graded], **titanic.widgets(678)),
        "679": grade_split.LF_GradeSplit().on_exec(before=example, after=graded,
                                                   **titanic.single(titanic.widgets(679))),
        "680": luma_ratio_map.LF_LumaRatioMap().on_exec(before=example, after=graded, mask=square,
                                                        **titanic.single(titanic.widgets(680))),
        "682": region_measure.LF_RegionMeasure().on_exec(image=[example, graded], **titanic.widgets(682)),
    }
    outputs["683"] = plot_chart.LF_PlotChart().on_exec(data=[outputs["682"]["result"][0]], **titanic.widgets(683))
    titanic.assert_named_values(titanic.case("cpu.inspection"), outputs)
    pair = outputs["678"]["result"][2]["pairs"][0]
    # The grade changed the square and nothing else: its changed box lies inside the square, and fills most of it.
    x0, y0, x1, y1 = pair["changed_box"]
    assert 192 <= x0 and 192 <= y0 and x1 <= 576 and y1 <= 576
    assert pair["changed_pixels"] > 0.9 * 384 * 384
    # Ten measures, one tab each, the frames on the axis; the plot's two series share one tab.
    assert len(outputs["682"]["ui"]["lf_output"][0]["datasets"]) == 10
    tabs = outputs["683"]["ui"]["lf_output"][0]["datasets"]
    assert len(tabs) == 1
    (chart,) = tabs.values()
    assert [column["title"] for column in chart["columns"][1:]] == ["square", "band"]
    report = outputs["682"]["result"][0]
    before, after = (frame["regions"] for frame in report["frames"])
    # The square moves toward the band's tone; the band itself is the grade's reference and stays.
    assert abs(after["square"]["mean"] - after["band"]["mean"]) < abs(before["square"]["mean"] - before["band"]["mean"])
    assert after["band"]["mean"] == pytest.approx(before["band"]["mean"])


def test_tone_reader_settings_produce_the_case_expectations(texture):
    example, square, band, graded = texture
    region_set = text_region_masks.LF_TextRegionMasks().on_exec(
        image=[example], masks=[square, band], regions=[titanic.widgets(688, drop=())["ui_widget"][0]])
    masks, metadata = region_set["result"][:2]
    profile = tone_profile.LF_ToneProfile()
    before = profile.on_exec(image=example, masks=masks, metadata=metadata, **titanic.single(titanic.widgets(690)))
    after = profile.on_exec(image=graded, masks=masks, metadata=metadata, reference=before["result"][0],
                            **titanic.single(titanic.widgets(691)))
    reads = region_reads.LF_RegionReads().on_exec(image=graded, masks=masks, metadata=metadata,
                                                  **titanic.single(titanic.widgets(692)))
    outputs = {"689": region_set, "690": before, "691": after, "692": reads}
    titanic.assert_named_values(titanic.case("cpu.tone-readers"), outputs)
    assert [node["value"].split(":")[0] for node in before["ui"]["lf_output"][0]["dataset"]["nodes"]] == [
        "frame", "square", "band"]
    against = after["result"][0]["against_reference"]
    assert set(against) == {"frame", "square", "band"}
    assert against["band"]["mean_ratio"] == pytest.approx(1, abs=1e-6)
    rows = {row["name"]: row for row in reads["result"][0]["reads"]}
    assert set(rows) == {"square / band", "edge(square) / inside(square)"}
    assert rows["square / band"]["luma_ratio"] is not None
