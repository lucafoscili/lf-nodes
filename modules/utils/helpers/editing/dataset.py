from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

Dataset = Dict[str, Any]


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def ensure_dataset_context(dataset: Optional[Dataset], fallback_context: Optional[str] = None) -> Optional[str]:
    """Ensure dataset and its selection contain a context id.

    Returns the resolved context identifier so callers can reuse it."""

    if not isinstance(dataset, dict):
        return fallback_context

    context_id = dataset.get("context_id") or fallback_context

    selection = _as_dict(dataset.get("selection"))
    selection_context = selection.get("context_id") or context_id

    if selection_context:
        selection["context_id"] = selection_context
        context_id = context_id or selection_context
        dataset["selection"] = selection

    if context_id:
        dataset["context_id"] = context_id

    return context_id


def extract_dataset_entries(dataset: Optional[Dataset]) -> Tuple[List[str], List[str], List[Optional[str]], List[Dict[str, Any]]]:
    """Extract lightweight metadata for each image entry in the dataset."""

    if not isinstance(dataset, dict):
        return [], [], [], []

    names: List[str] = []
    urls: List[str] = []
    node_ids: List[Optional[str]] = []
    metadata: List[Dict[str, Any]] = []

    nodes = dataset.get("nodes")
    if not isinstance(nodes, list):
        return names, urls, node_ids, metadata

    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            continue

        image_cell = _as_dict(_as_dict(node.get("cells")).get("lfImage"))
        html_props = _as_dict(image_cell.get("htmlProps"))

        name = (
            html_props.get("title")
            or html_props.get("id")
            or (node.get("value") if isinstance(node.get("value"), str) else None)
            or f"{index + 1}"
        )

        url = image_cell.get("lfValue") or image_cell.get("value")
        node_id = node.get("id") if isinstance(node.get("id"), str) else None

        names.append(str(name))
        urls.append(url if isinstance(url, str) else "")
        node_ids.append(node_id)
        metadata.append(
            {
                "index": index,
                "name": str(name),
                "url": url if isinstance(url, str) else None,
                "node_id": node_id,
            }
        )

    return names, urls, node_ids, metadata
