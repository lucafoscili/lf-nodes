"""A chart drawn from any JSON report: series picked by dotted paths, drawn as a line, scatter, histogram or bars."""
from __future__ import annotations

import io
import math
import re

import numpy as np
import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value, normalize_output_image
from ...utils.helpers.ui import cache_generated_preview, create_masonry_node

SCHEMA = "lf.plot-chart.v1"
KINDS = ["line", "scatter", "histogram", "bar"]


def resolve_path(data, path: str):
    """Values at a dotted path: keys, list indices, and ``*`` for every item of a list or value of a dict.

    A path that ends on one dict returns the dict (labels and values for bars); otherwise a flat list.
    """
    current, starred = [data], False
    for step in [part.strip() for part in path.strip().split(".") if part.strip()]:
        following = []
        for value in current:
            if step == "*":
                starred = True
                if isinstance(value, dict):
                    following.extend(value.values())
                elif isinstance(value, list):
                    following.extend(value)
                else:
                    raise ValueError(f"{path}: '*' needs a list or a dict, not {type(value).__name__}.")
            elif isinstance(value, list):
                if not re.fullmatch(r"-?\d+", step) or not -len(value) <= int(step) < len(value):
                    raise ValueError(f"{path}: no index {step!r} in a list of {len(value)}.")
                following.append(value[int(step)])
            elif isinstance(value, dict):
                if step not in value:
                    raise ValueError(f"{path}: no key {step!r}.")
                following.append(value[step])
            else:
                raise ValueError(f"{path}: {step!r} reaches into a {type(value).__name__}.")
        current = following
    if not starred and len(current) == 1 and isinstance(current[0], dict):
        return current[0]
    flat = []
    for value in current:
        flat.extend(value if isinstance(value, list) else [value])
    if not flat:
        raise ValueError(f"{path}: found no values.")
    return flat


def _numbers(values, where: str) -> list[float]:
    numbers = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{where} holds a non-number: {value!r}.")
        numbers.append(value)
    return numbers


def chart_series(data, paths: str) -> list[dict]:
    """Series from ``name = path`` (or ``name = x_path, y_path``) lines, or a ``{"series": [...]}`` document.

    A document's series hold ``values`` (or ``y``), and optionally ``x`` or ``labels``.
    """
    series = []
    lines = [line.strip() for line in str(paths or "").splitlines() if line.strip()]
    if lines:
        for line in lines:
            name, separator, spec = line.partition("=")
            if not separator or not name.strip():
                raise ValueError(f"paths line {line!r} must read name = path, or name = x_path, y_path.")
            parts = [part.strip() for part in spec.split(",")]
            if len(parts) == 1:
                found = resolve_path(data, parts[0])
                if isinstance(found, dict):
                    series.append({"name": name.strip(), "labels": [str(key) for key in found],
                                   "y": _numbers(found.values(), parts[0])})
                else:
                    series.append({"name": name.strip(), "y": _numbers(found, parts[0])})
            elif len(parts) == 2:
                x, y = (_numbers(resolve_path(data, part), part) for part in parts)
                if len(x) != len(y):
                    raise ValueError(f"series {name.strip()}: x holds {len(x)} values and y {len(y)}.")
                series.append({"name": name.strip(), "x": x, "y": y})
            else:
                raise ValueError(f"paths line {line!r} holds {len(parts)} paths; give one or two.")
    else:
        document = data[0] if isinstance(data, list) and len(data) == 1 else data
        if not isinstance(document, dict) or not isinstance(document.get("series"), list):
            raise ValueError('data must hold {"series": [...]} when no paths are given.')
        for index, item in enumerate(document["series"]):
            name = str(item.get("name") or f"series {index + 1}")
            values = item.get("values", item.get("y"))
            if not isinstance(values, list):
                raise ValueError(f"series {name} needs a values list.")
            entry = {"name": name, "y": [float(value) for value in _numbers(values, f"series {name}")]}
            for key in ("x", "labels"):
                if key in item:
                    extra = item[key] if key == "labels" else _numbers(item[key], f"series {name} {key}")
                    if len(extra) != len(entry["y"]):
                        raise ValueError(f"series {name}: {key} holds {len(extra)} values and y {len(entry['y'])}.")
                    entry[key] = [str(label) for label in extra] if key == "labels" else extra
            series.append(entry)
    if not series:
        raise ValueError("data holds no series to draw.")
    return series


def _summary(values: list[float]) -> dict:
    array = np.asarray(values, dtype=np.float64)
    return {"n": int(array.size), "min": float(array.min()), "max": float(array.max()), "mean": float(array.mean()),
            "median": float(np.median(array)), "p5": float(np.quantile(array, 0.05)),
            "p95": float(np.quantile(array, 0.95))}


def plot_chart(series: list[dict], *, kind: str = "line", title: str = "", x_label: str = "", y_label: str = "",
               width: int = 960, height: int = 540, bins: int = 40, log_y: bool = False) -> tuple[torch.Tensor, dict]:
    """Draw the series with Matplotlib's Agg canvas; return the RGB image and each series' numbers."""
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {', '.join(KINDS)}, not {kind!r}.")
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure
    from matplotlib.ticker import MaxNLocator
    from PIL import Image

    dpi = 100
    figure = Figure(figsize=(width / dpi, height / dpi), dpi=dpi)
    FigureCanvasAgg(figure)
    axes = figure.add_subplot(1, 1, 1)
    for index, item in enumerate(series):
        y = item["y"]
        if kind == "histogram":
            axes.hist(y, bins=int(bins), alpha=0.6 if len(series) > 1 else 0.9, label=item["name"])
        elif kind == "bar":
            labels = item.get("labels") or [str(position) for position in range(len(y))]
            offset = (index - (len(series) - 1) / 2) * 0.8 / len(series)
            positions = np.arange(len(y)) + offset
            axes.bar(positions, y, width=0.8 / len(series), label=item["name"])
            axes.set_xticks(np.arange(len(y)), labels, rotation=60 if len(labels) > 8 else 0, fontsize=8, ha="right"
                            if len(labels) > 8 else "center")
        else:
            x = item.get("x") or list(range(len(y)))
            if kind == "line":
                axes.plot(x, y, marker="o", markersize=3, label=item["name"])
            else:
                axes.scatter(x, y, s=10, label=item["name"])
            if item.get("labels") and not item.get("x"):
                axes.set_xticks(range(len(y)), item["labels"], rotation=60 if len(y) > 8 else 0, fontsize=8)
            elif not item.get("x"):
                axes.xaxis.set_major_locator(MaxNLocator(integer=True))
    if log_y:
        axes.set_yscale("log")
    axes.set_title(title)
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)
    axes.grid(True, alpha=0.3)
    if len(series) > 1:
        axes.legend(fontsize=8)
    figure.tight_layout()
    buffer = io.BytesIO()
    figure.savefig(buffer, format="png", dpi=dpi)
    buffer.seek(0)
    with Image.open(buffer) as picture:
        rgb = picture.convert("RGB")
        if rgb.size != (width, height):
            rgb = rgb.resize((width, height), Image.LANCZOS)
        array = np.asarray(rgb, dtype=np.float32) / 255.0
    numbers = {"schema": SCHEMA, "kind": kind, "series": [{"name": item["name"], **_summary(item["y"])}
                                                          for item in series]}
    return torch.from_numpy(array)[None], numbers


class LF_PlotChart:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "data": (Input.JSON, {"tooltip": "Any JSON report, or a chart document {\"series\": [{\"name\", \"values\", \"x\"?, \"labels\"?}]}."}),
                "kind": (KINDS, {"default": "line", "tooltip": "Line or scatter (y over x or its index), histogram of the values, or bars."}),
                "paths": (Input.STRING, {"default": "", "multiline": True, "tooltip": "One series per line: name = path, or name = x_path, y_path. A path is dotted keys and indices, '*' for every item. Empty reads a chart document."}),
                "title": (Input.STRING, {"default": "", "tooltip": "Chart title."}),
                "x_label": (Input.STRING, {"default": "", "tooltip": "X axis label."}),
                "y_label": (Input.STRING, {"default": "", "tooltip": "Y axis label."}),
                "width": (Input.INTEGER, {"default": 960, "min": 160, "max": 4096, "step": 8, "tooltip": "Image width in pixels."}),
                "height": (Input.INTEGER, {"default": 540, "min": 120, "max": 4096, "step": 8, "tooltip": "Image height in pixels."}),
                "bins": (Input.INTEGER, {"default": 40, "min": 2, "max": 1000, "tooltip": "Histogram bins."}),
                "log_y": (Input.BOOLEAN, {"default": False, "tooltip": "Logarithmic Y axis."}),
            },
            "optional": {"ui_widget": (Input.LF_MASONRY, {"default": {}})},
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    DESCRIPTION = ("Draw a chart from a JSON report: pick series by dotted paths and draw them as a line, scatter, "
                   "histogram or bars, with each series' count, range, mean, median and 5th/95th percentiles.")
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (False, True, False)
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "The chart as an RGB image.",
        "The chart as a one-item image list.",
        "lf.plot-chart.v1: each series' count, min, max, mean, median, p5 and p95.",
    )
    RETURN_NAMES = ("image", "image_list", "numbers")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.JSON)

    def on_exec(self, data=None, kind="line", paths="", title="", x_label="", y_label="", width=960, height=540,
                bins=40, log_y=False, **kwargs):
        document = normalize_list_to_value(data)
        if document is None:
            raise ValueError("data must hold a JSON report.")
        series = chart_series(document, normalize_list_to_value(paths) or "")
        image, numbers = plot_chart(
            series, kind=str(normalize_list_to_value(kind)), title=str(normalize_list_to_value(title) or ""),
            x_label=str(normalize_list_to_value(x_label) or ""), y_label=str(normalize_list_to_value(y_label) or ""),
            width=int(normalize_list_to_value(width)), height=int(normalize_list_to_value(height)),
            bins=int(normalize_list_to_value(bins)), log_y=bool(normalize_list_to_value(log_y)))
        payload = {"dataset": {"nodes": [create_masonry_node("Chart", cache_generated_preview(image).url, 0)]},
                   "numbers": numbers}
        safe_send_sync("plotchart", payload, normalize_list_to_value(kwargs.get("node_id")))
        batch_groups, image_list = normalize_output_image([image])
        return {"ui": {"lf_output": [payload]}, "result": (batch_groups[0], image_list, numbers)}


NODE_CLASS_MAPPINGS = {"LF_PlotChart": LF_PlotChart}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_PlotChart": "Plot chart"}
