from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

Dataset = Dict[str, Any]

# region Helpers
def _as_dict(value: Any) -> Dict[str, Any]:
    """
    Converts the input value to a dictionary if it is already a dictionary, otherwise returns an empty dictionary.

    Args:
        value (Any): The value to check and potentially convert.

    Returns:
        Dict[str, Any]: The original value if it is a dictionary, otherwise an empty dictionary.
    """
    return value if isinstance(value, dict) else {}

def _build_fallback_entries(
    count: int,
    context_id: Optional[str] = None,
) -> Tuple[List[str], List[str], List[Optional[str]], List[Dict[str, Any]]]:
    """
    Generates fallback entries for a dataset, providing default names, URLs, node IDs, and metadata dictionaries.

    Args:
        count (int): The number of fallback entries to generate.
        context_id (Optional[str], optional): An optional context identifier to include in each metadata dictionary. Defaults to None.

    Returns:
        Tuple[
            List[str],                # List of entry names (e.g., "Image 1", "Image 2", ...).
            List[str],                # List of entry URLs (empty strings).
            List[Optional[str]],      # List of node IDs (all None).
            List[Dict[str, Any]]      # List of metadata dictionaries for each entry.
    """
    names = [f"Image {idx + 1}" for idx in range(count)]
    urls = [""] * count
    node_ids: List[Optional[str]] = [None] * count
    metadata = [
        {
            "index": idx,
            "name": names[idx],
            "url": "",
            "node_id": None,
            **({"context_id": context_id} if context_id else {}),
        }
        for idx in range(count)
    ]

    return names, urls, node_ids, metadata
# endregion

# region ensure_dataset_context
def ensure_dataset_context(dataset: Optional[Dataset], fallback_context: Optional[str] = None) -> Optional[str]:
    """
    Ensures that the provided dataset and its selection contain a context identifier.

    This function checks if the `dataset` (expected to be a dictionary) and its nested
    `selection` dictionary have a `"context_id"` key. If not, it uses the provided
    `fallback_context` as the context identifier. The function updates the dataset and
    selection in-place to ensure the `"context_id"` is set where necessary.

    Args:
        dataset (Optional[Dataset]): The dataset dictionary to check and update.
        fallback_context (Optional[str], optional): The context identifier to use if
            none is found in the dataset or selection. Defaults to None.

    Returns:
        Optional[str]: The resolved context identifier, or None if not found.
    """
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
# endregion

# region extract_dataset_entries
def extract_dataset_entries(
    dataset: Optional[Dataset],
    fallback_count: int = 0,
    context_id: Optional[str] = None,
) -> Tuple[List[str], List[str], List[Optional[str]], List[Dict[str, Any]]]:
    """
    Extract lightweight metadata for each image entry in the dataset.

    This function processes a dataset object and extracts lists of image names, URLs, node IDs, and associated metadata dictionaries for each image node. If the dataset is not a dictionary or lacks valid nodes, fallback entries are generated to maintain consistency for downstream logic.

    Args:
        dataset (Optional[Dataset]): The dataset object containing image nodes and metadata. If not a dictionary, fallback entries are used.
        fallback_count (int, optional): Number of fallback entries to generate if the dataset is invalid or empty. Defaults to 0.
        context_id (Optional[str], optional): An optional context identifier to include in the metadata for each entry. Defaults to None.

    Returns:
        Tuple[List[str], List[str], List[Optional[str]], List[Dict[str, Any]]]:
            - names: List of image names (as strings).
            - urls: List of image URLs (as strings).
            - node_ids: List of node IDs (as strings or None).
            - metadata: List of dictionaries containing metadata for each entry, including index, name, url, node_id, and optionally context_id.

    Notes:
        - If the dataset is invalid or contains no nodes, fallback entries are generated.
        - Each metadata dictionary contains at least the keys: "index", "name", "url", and "node_id". If context_id is provided, it is added to each metadata entry.
    """
    if not isinstance(dataset, dict):
        return _build_fallback_entries(fallback_count, context_id)

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

    if not names and fallback_count:
        fallback_names, fallback_urls, fallback_node_ids, fallback_metadata = _build_fallback_entries(
            fallback_count,
            context_id,
        )
        names = fallback_names
        urls = fallback_urls
        node_ids = fallback_node_ids
        metadata = fallback_metadata
    elif context_id:
        for entry in metadata:
            entry.setdefault("context_id", context_id)

    return names, urls, node_ids, metadata
# endregion

# region resolve_image_selection
def resolve_image_selection(
    image_list: Sequence[Any],
    names: Sequence[str],
    *,
    selection_index: Optional[int] = None,
    selection_name: Optional[str] = None,
    selection_node_id: Optional[str] = None,
    selection_url: Optional[str] = None,
    node_ids: Optional[Sequence[Optional[str]]] = None,
    urls: Optional[Sequence[Optional[str]]] = None,
    fallback_to_first: bool = True,
) -> Tuple[Optional[Any], Optional[int], Optional[str]]:
    """
    Resolve a selected image from a list based on various selection criteria.

    This function attempts to select an image from `image_list` using the following priority:
    1. By explicit index (`selection_index`).
    2. By node ID (`selection_node_id` and `node_ids`).
    3. By URL (`selection_url` and `urls`).
    4. By name (`selection_name` and `names`).
    5. Falls back to the first image if `fallback_to_first` is True.

    Args:
        image_list (Sequence[Any]): List of images to select from.
        names (Sequence[str]): List of names corresponding to each image.
        selection_index (Optional[int], optional): Index of the image to select.
        selection_name (Optional[str], optional): Name of the image to select.
        selection_node_id (Optional[str], optional): Node ID associated with the image to select.
        selection_url (Optional[str], optional): URL associated with the image to select.
        node_ids (Optional[Sequence[Optional[str]]], optional): List of node IDs corresponding to each image.
        urls (Optional[Sequence[Optional[str]]], optional): List of URLs corresponding to each image.
        fallback_to_first (bool, optional): Whether to return the first image if no selection criteria match. Defaults to True.

    Returns:
        Tuple[Optional[Any], Optional[int], Optional[str]]:
            - The selected image (or None if not found).
            - The index of the selected image (or None if not found).
            - The resolved name of the selected image (or the provided selection_name if not found).
    """
    def _valid_index(index: Optional[int], items: Sequence[Any]) -> bool:
        return isinstance(index, int) and 0 <= index < len(items)

    def _resolve_by_index(index: int) -> Tuple[Any, int, Optional[str]]:
        resolved_name = names[index] if index < len(names) else selection_name
        return image_list[index], index, resolved_name

    if _valid_index(selection_index, image_list):
        return _resolve_by_index(selection_index)  # type: ignore[arg-type]

    if selection_node_id and node_ids:
        if selection_node_id in node_ids:
            idx = node_ids.index(selection_node_id)
            if _valid_index(idx, image_list):
                return _resolve_by_index(idx)

    if selection_url and urls:
        if selection_url in urls:
            idx = urls.index(selection_url)
            if _valid_index(idx, image_list):
                return _resolve_by_index(idx)

    if selection_name and selection_name in names:
        idx = names.index(selection_name)
        if _valid_index(idx, image_list):
            return _resolve_by_index(idx)

    if fallback_to_first and len(image_list) > 0:
        return _resolve_by_index(0)

    return None, None, selection_name
# endregion
