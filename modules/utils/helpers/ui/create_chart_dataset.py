"""Datasets for LF's chart widget (tabBarChart): one node per category, a numeric column per series, and the layout.

LF's ``lf-chart`` draws a category x axis and keeps the layout (axis, series, types) it loaded with, so each
dataset carries its own layout under ``chart``; the widget applies it before the data, on load and on a tab click.
"""
from __future__ import annotations

import math

__all__ = ["CHART_TYPES", "MISSING_VALUE", "axis_labels", "create_chart_dataset"]

CHART_TYPES = ("area", "bar", "line", "scatter")
# ECharts' missing-data mark: a reading without a value is drawn as a gap, never as a zero.
MISSING_VALUE = "-"
AXIS_ID = "x"


def _number_labels(values: list[float]) -> list[str]:
    """The fewest significant digits (four at least) that keep distinct numbers apart."""
    largest = max((abs(value) for value in values if math.isfinite(value)), default=0)
    digits = max(4, len(str(int(largest))))
    while True:
        labels = [str(int(value)) if float(value).is_integer() else f"{value:.{digits}g}" for value in values]
        if digits >= 17 or len(set(labels)) == len(set(values)):
            return labels
        digits += 1


def axis_labels(values: list) -> list[str]:
    """Category labels for an axis: names as given, numbers written short; a repeat is numbered ("3 (2)")."""
    numbers = [value for value in values if isinstance(value, (int, float)) and not isinstance(value, bool)]
    if numbers and len(numbers) == len(values):
        labels = _number_labels(list(values))
    else:
        labels = [str(value) for value in values]
    seen: dict[str, int] = {}
    unique = []
    for label in labels:
        seen[label] = seen.get(label, 0) + 1
        unique.append(label if seen[label] == 1 else f"{label} ({seen[label]})")
    return unique


def create_chart_dataset(axis_title: str, categories: list, series: list[tuple[str, list]], chart_type: str) -> dict:
    """An lf-chart dataset: a node per category (in the order given), a number column per ``(title, values)``.

    ``None`` values become ``MISSING_VALUE``. Every series shares the one chart type.
    """
    if chart_type not in CHART_TYPES:
        raise ValueError(f"chart type must be one of {', '.join(CHART_TYPES)}, not {chart_type!r}.")
    if not series:
        raise ValueError("a chart dataset needs at least one series.")
    for title, values in series:
        if len(values) != len(categories):
            raise ValueError(f"series {title} holds {len(values)} values for {len(categories)} categories.")
    ids = [f"s{index}" for index in range(len(series))]
    columns = [{"id": AXIS_ID, "title": axis_title}]
    columns += [{"id": column, "shape": "number", "title": title} for column, (title, _) in zip(ids, series)]
    nodes = []
    for index, label in enumerate(axis_labels(list(categories))):
        cells = {AXIS_ID: {"value": label}}
        for column, (_, values) in zip(ids, series):
            value = values[index]
            cells[column] = {"value": MISSING_VALUE if value is None else value}
        nodes.append({"id": str(index), "cells": cells})
    return {"columns": columns, "nodes": nodes,
            "chart": {"axis": AXIS_ID, "series": ids, "types": [chart_type] * len(series)}}
