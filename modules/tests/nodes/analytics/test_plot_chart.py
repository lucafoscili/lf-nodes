"""Plot chart from JSON: path selection, the four kinds, the chart's numbers and failures."""
import pytest

from modules.nodes.analytics.plot_chart import LF_PlotChart, chart_series, plot_chart, resolve_path
from modules.utils.helpers.ui import generated_preview


@pytest.fixture(autouse=True)
def preview_root(monkeypatch, tmp_path):
    monkeypatch.setattr(generated_preview, "get_comfy_dir", lambda _kind: str(tmp_path / "input"))


REPORT = {
    "frames": [
        {"label": "f0", "regions": {"face": {"mean": 0.2}, "hair": {"mean": 0.1}}},
        {"label": "f1", "regions": {"face": {"mean": 0.4}, "hair": {"mean": 0.3}}},
    ],
    "joints": {"hips": 120, "spine": 80},
}


def test_paths_walk_keys_indices_and_stars():
    assert resolve_path(REPORT, "frames.*.regions.face.mean") == [0.2, 0.4]
    assert resolve_path(REPORT, "frames.1.regions.hair.mean") == [0.3]
    assert resolve_path(REPORT, "frames.*.regions.*.mean") == [0.2, 0.1, 0.4, 0.3]
    assert resolve_path(REPORT, "joints") == {"hips": 120, "spine": 80}


def test_a_path_that_finds_nothing_is_named():
    with pytest.raises(ValueError, match="frames.\\*.regions.skin.mean: no key 'skin'"):
        resolve_path(REPORT, "frames.*.regions.skin.mean")


def test_series_from_paths_take_names_x_and_y():
    series = chart_series(REPORT, "face = frames.*.regions.face.mean\nhair=frames.*.regions.hair.mean")
    assert [item["name"] for item in series] == ["face", "hair"]
    assert series[0]["y"] == [0.2, 0.4] and "x" not in series[0]
    scatter = chart_series(REPORT, "pairs = frames.*.regions.hair.mean, frames.*.regions.face.mean")
    assert scatter[0]["x"] == [0.1, 0.3] and scatter[0]["y"] == [0.2, 0.4]
    bars = chart_series(REPORT, "joints = joints")
    assert bars[0]["labels"] == ["hips", "spine"] and bars[0]["y"] == [120, 80]


def test_series_without_paths_read_the_chart_document():
    series = chart_series({"series": [{"name": "d", "values": [1, 2, 3]}]}, "")
    assert series == [{"name": "d", "y": [1.0, 2.0, 3.0]}]


def test_non_numbers_and_unequal_lengths_are_refused():
    with pytest.raises(ValueError, match="frames.\\*.label holds a non-number"):
        chart_series(REPORT, "labels = frames.*.label")
    with pytest.raises(ValueError, match="x holds 4 values and y 2"):
        chart_series(REPORT, "bad = frames.*.regions.*.mean, frames.*.regions.face.mean")
    with pytest.raises(ValueError, match="no series"):
        chart_series({"series": []}, "")


@pytest.mark.parametrize("kind", ["line", "scatter", "histogram", "bar"])
def test_each_kind_draws_at_the_asked_size(kind):
    data = {"series": [{"name": "a", "values": [1, 2, 2, 3, 5, 8]}]}
    image, numbers = plot_chart(chart_series(data, ""), kind=kind, title="t", width=320, height=200)
    assert image.shape == (1, 200, 320, 3)
    assert numbers["series"][0]["n"] == 6
    assert numbers["series"][0]["median"] == pytest.approx(2.5)
    assert numbers["series"][0]["max"] == 8


def test_node_returns_image_list_and_numbers():
    out = LF_PlotChart().on_exec(data=[REPORT], kind=["line"], paths=["face=frames.*.regions.face.mean"],
                                 title=[""], x_label=[""], y_label=[""], width=[320], height=[200], bins=[10],
                                 log_y=[False], node_id=["1"])
    image, image_list, numbers = out["result"]
    assert image.shape == (1, 200, 320, 3) and len(image_list) == 1
    assert numbers["schema"] == "lf.plot-chart.v1"
