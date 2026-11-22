"""Chart datasets for LF's chart widget: columns, one node per category, the layout, labels and failures."""
import pytest

from modules.utils.helpers.ui import MISSING_VALUE, axis_labels, create_chart_dataset


def test_a_dataset_holds_a_node_per_category_and_its_layout():
    dataset = create_chart_dataset("Frame", ["a", "b"], [("face", [0.2, 0.4]), ("hair", [0.1, None])], "bar")
    assert dataset["chart"] == {"axis": "x", "series": ["s0", "s1"], "types": ["bar", "bar"]}
    assert dataset["columns"] == [
        {"id": "x", "title": "Frame"},
        {"id": "s0", "shape": "number", "title": "face"},
        {"id": "s1", "shape": "number", "title": "hair"},
    ]
    first, second = dataset["nodes"]
    assert first == {"id": "0", "cells": {"x": {"value": "a"}, "s0": {"value": 0.2}, "s1": {"value": 0.1}}}
    # A reading that has no value is drawn as a gap, never as a zero.
    assert second["cells"]["s1"] == {"value": MISSING_VALUE}


def test_labels_take_the_digits_that_tell_values_apart_and_number_repeats():
    assert axis_labels([0.1, 0.15, 0.2]) == ["0.1", "0.15", "0.2"]
    assert axis_labels([1.00001, 1.00002]) == ["1.00001", "1.00002"]
    assert axis_labels([3, 3, 4]) == ["3", "3 (2)", "4"]
    assert axis_labels(["apples", "pears", "apples"]) == ["apples", "pears", "apples (2)"]


def test_series_must_match_the_axis_and_types_must_be_known():
    with pytest.raises(ValueError, match="series face holds 1 values for 2 categories"):
        create_chart_dataset("Frame", ["a", "b"], [("face", [0.2])], "bar")
    with pytest.raises(ValueError, match="chart type must be one of"):
        create_chart_dataset("Frame", ["a"], [("face", [0.2])], "pie")
    with pytest.raises(ValueError, match="needs at least one series"):
        create_chart_dataset("Frame", ["a"], [], "bar")
