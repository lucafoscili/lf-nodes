"""Plot chart from JSON: path selection, the four kinds, the chart's numbers and failures."""
import pytest

from modules.nodes.analytics.plot_chart import (LF_PlotChart, chart_series, histogram_edges, plot_chart, resolve_path,
                                               widget_datasets)
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


COUNTS = {"kinds": [{"kind": "apples", "count": 12}, {"kind": "pears", "count": 7}, {"kind": "plums", "count": 3}]}
NAMED = "fruit = kinds.*.kind, kinds.*.count"


def test_a_bar_chart_takes_names_on_its_x_path():
    series = chart_series(COUNTS, NAMED, kind="bar")
    assert series == [{"name": "fruit", "labels": ["apples", "pears", "plums"], "y": [12, 7, 3]}]
    image, numbers = plot_chart(series, kind="bar", width=320, height=200)
    assert image.shape == (1, 200, 320, 3)
    assert numbers["series"][0]["n"] == 3 and numbers["series"][0]["labels"] == ["apples", "pears", "plums"]


@pytest.mark.parametrize("kind", ["line", "scatter", "histogram", None])
def test_names_on_x_are_refused_off_a_bar_chart(kind):
    with pytest.raises(ValueError, match=r"kinds\.\*\.kind holds a non-number: 'apples'; names on x draw only as bars"):
        chart_series(COUNTS, NAMED, kind=kind)


def test_names_mixed_with_numbers_on_x_are_refused():
    mixed = {"kinds": [{"kind": "apples", "count": 1}, {"kind": 2, "count": 2}]}
    with pytest.raises(ValueError, match=r"kinds\.\*\.kind mixes names and numbers: 2"):
        chart_series(mixed, NAMED, kind="bar")


def test_names_that_do_not_match_the_values_count_are_refused():
    with pytest.raises(ValueError, match="series fruit: x holds 3 values and y 1"):
        chart_series(COUNTS, "fruit = kinds.*.kind, kinds.0.count", kind="bar")


def test_bar_series_on_different_names_are_refused():
    fruit = chart_series(COUNTS, NAMED, kind="bar")
    other = chart_series({"k": {"apples": 1, "figs": 2, "plums": 3}}, "other = k")
    with pytest.raises(ValueError, match="series other's names differ from series fruit's"):
        plot_chart(fruit + other, kind="bar", width=320, height=200)


def test_a_bar_chart_names_its_bars_by_a_numeric_x():
    series = chart_series(REPORT, "pairs = frames.*.regions.hair.mean, frames.*.regions.face.mean", kind="bar")
    _, numbers = plot_chart(series, kind="bar", width=320, height=200)
    assert numbers["series"][0]["labels"] == ["0.1", "0.3"]


def test_the_node_reads_names_on_a_bar_chart():
    out = LF_PlotChart().on_exec(data=[COUNTS], kind=["bar"], paths=[NAMED], title=[""], x_label=[""],
                                 y_label=[""], width=[320], height=[200], bins=[10], log_y=[False], node_id=["1"])
    assert out["result"][2]["series"][0]["labels"] == ["apples", "pears", "plums"]


def _cells(dataset, column):
    return [node["cells"][column]["value"] for node in dataset["nodes"]]


def test_series_on_one_axis_share_the_widget_chart():
    series = chart_series(REPORT, "face = frames.*.regions.face.mean\nhair = frames.*.regions.hair.mean")
    datasets = widget_datasets(series, kind="line", bins=10)
    assert list(datasets) == ["Chart"]
    chart = datasets["Chart"]
    assert chart["chart"] == {"axis": "x", "series": ["s0", "s1"], "types": ["line", "line"]}
    assert [column["title"] for column in chart["columns"]] == ["Index", "face", "hair"]
    assert _cells(chart, "x") == ["0", "1"] and _cells(chart, "s1") == [0.1, 0.3]


def test_series_on_different_axes_take_a_tab_each():
    series = chart_series({"a": [1, 2, 3], "b": [4, 5]}, "a = a\nb = b")
    datasets = widget_datasets(series, kind="line", bins=10)
    assert list(datasets) == ["a", "b"]
    assert _cells(datasets["b"], "x") == ["0", "1"] and _cells(datasets["b"], "s0") == [4, 5]


def test_a_scatter_is_drawn_in_x_order_each_point_its_own_step():
    series = chart_series({"x": [0.3, 0.1, 0.3], "y": [1, 2, 3]}, "pts = x, y")
    chart = widget_datasets(series, kind="scatter", bins=10, x_label="width")["Chart"]
    assert chart["chart"]["types"] == ["scatter"]
    assert chart["columns"][0]["title"] == "width"
    assert _cells(chart, "x") == ["0.1", "0.3", "0.3 (2)"] and _cells(chart, "s0") == [2, 1, 3]


def test_a_histogram_counts_every_series_on_the_same_bins_as_its_picture():
    series = chart_series({"series": [{"name": "a", "values": [0, 1, 1, 2]}, {"name": "b", "values": [2, 3]}]}, "")
    edges = histogram_edges(series, 3)
    assert list(edges) == pytest.approx([0, 1, 2, 3])
    chart = widget_datasets(series, kind="histogram", bins=3)["Chart"]
    assert chart["chart"]["types"] == ["bar", "bar"]
    assert chart["columns"][0]["title"] == "Bin start"
    assert _cells(chart, "x") == ["0", "1", "2"]
    assert _cells(chart, "s0") == [1, 2, 1] and _cells(chart, "s1") == [0, 0, 2]


def test_bars_on_names_draw_one_bar_each():
    chart = widget_datasets(chart_series(COUNTS, NAMED, kind="bar"), kind="bar", bins=10)["Chart"]
    assert chart["chart"]["types"] == ["bar"]
    assert _cells(chart, "x") == ["apples", "pears", "plums"] and _cells(chart, "s0") == [12, 7, 3]


def test_the_node_sends_its_charts_to_the_widget():
    out = LF_PlotChart().on_exec(data=[COUNTS], kind=["bar"], paths=[NAMED], title=[""], x_label=[""],
                                 y_label=[""], width=[320], height=[200], bins=[10], log_y=[False], node_id=["1"])
    assert list(out["ui"]["lf_output"][0]["datasets"]) == ["Chart"]
