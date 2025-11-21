import copy
import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.editing import (
    EditingSession,
    apply_editor_config_to_dataset,
    build_editor_config_from_dataset,
    ensure_dataset_context,
    extract_dataset_entries,
    resolve_image_selection,
)
from ...utils.helpers.logic import normalize_conditioning, normalize_json_input, normalize_list_to_value
from ...utils.helpers.temp_cache import TempFileCache
from ...utils.helpers.torch import create_dummy_image_tensor

# region LF_LoadAndEditImages
class LF_LoadAndEditImages:
    def __init__(self):
        self._temp_cache = TempFileCache()

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {},
            "optional": {
                "model": (Input.MODEL, {
                    "tooltip": "Optional diffusion model reused by inpaint edits."
                }),
                "clip": (Input.CLIP, {
                    "tooltip": "Optional CLIP encoder reused by inpaint edits."
                }),
                "vae": (Input.VAE, {
                    "tooltip": "Optional VAE reused by inpaint edits."
                }),
                "positive_conditioning": (Input.CONDITIONING, {
                    "tooltip": "Optional positive conditioning to reuse during inpaint edits."
                }),
                "negative_conditioning": (Input.CONDITIONING, {
                    "tooltip": "Optional negative conditioning to reuse during inpaint edits."
                }),
                "config": (Input.JSON, {
                    "tooltip": "Optional image editor configuration JSON (navigation/defaults/selection)."
                }),
                "ui_widget": (Input.LF_IMAGE_EDITOR, {
                    "default": {}
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True, True, True, False, False, False, False, False, False, False)
    OUTPUT_TOOLTIPS = (
        "Edited image tensor.",
        "List of edited image tensors.",
        "Names of the images.",
        "Creation dates of the images.",
        "Count of edited images.",
        "Selected image tensor.",
        "Index of the selected image.",
        "Name of the selected image.",
        "Metadata of the images.",
        "Dataset for visualization."
    )
    RETURN_NAMES = (
        "image",
        "image_list",
        "name",
        "creation_date",
        "nr",
        "selected_image",
        "selected_index",
        "selected_name",
        "metadata",
        "dataset",
        "config",
    )
    RETURN_TYPES = (
        Input.IMAGE,
        Input.IMAGE,
        Input.STRING,
        Input.STRING,
        Input.INTEGER,
        Input.IMAGE,
        Input.INTEGER,
        Input.STRING,
        Input.JSON,
        Input.JSON,
        Input.JSON,
    )

    def on_exec(self, **kwargs: dict):
        node_id = kwargs.get("node_id")
        self._temp_cache.cleanup()

        session = EditingSession(node_id=node_id, temp_cache=self._temp_cache)

        model_value = normalize_list_to_value(kwargs.get("model"))
        clip_value = normalize_list_to_value(kwargs.get("clip"))
        vae_value = normalize_list_to_value(kwargs.get("vae"))
        seed_value = None

        positive_conditioning_value = normalize_conditioning(kwargs.get("positive_conditioning"))
        negative_conditioning_value = normalize_conditioning(kwargs.get("negative_conditioning"))

        config_raw = kwargs.get("config")
        try:
            config_value = normalize_json_input(config_raw) if config_raw is not None else None
        except TypeError:
            config_value = None

        ui_dataset = normalize_json_input(kwargs.get("ui_widget", {})) or {}
        dataset = self._prepare_dataset(session, ui_dataset)

        if config_value is None and isinstance(ui_dataset, dict):
            config_value = build_editor_config_from_dataset(ui_dataset)

        if isinstance(config_value, dict):
            apply_editor_config_to_dataset(dataset, config_value)

        session.register_context(
            dataset,
            model=model_value,
            clip=clip_value,
            vae=vae_value,
            seed=seed_value,
            positive_conditioning=positive_conditioning_value,
            negative_conditioning=negative_conditioning_value,
        )

        safe_send_sync(
            "loadandeditimages",
            {
                "dataset": dataset,
            },
            node_id,
        )

        results = session.collect_results(dataset)
        image_batch = list(results.batch_list or [])
        image_list = list(results.image_list or [])

        context_id = ensure_dataset_context(dataset)

        names, urls, node_ids, metadata_entries = extract_dataset_entries(
            dataset,
            fallback_count=len(image_list),
            context_id=context_id,
        )

        creation_dates = ["" for _ in names]
        image_count = len(names) if names else len(image_list)

        raw_selection = results.selected_entry or dataset.get("selection") or {}
        selection = dict(raw_selection) if isinstance(raw_selection, dict) else {}

        sel_idx_raw = selection.get("index") if isinstance(selection.get("index"), int) else None
        sel_name_raw = selection.get("name") if isinstance(selection.get("name"), str) else None
        sel_node_id_raw = selection.get("node_id") if isinstance(selection.get("node_id"), str) else None
        sel_url_raw = selection.get("url") if isinstance(selection.get("url"), str) else None

        selected_image_tensor, selected_index, selected_name = resolve_image_selection(
            image_list,
            names,
            selection_index=sel_idx_raw,
            selection_name=sel_name_raw,
            selection_node_id=sel_node_id_raw,
            selection_url=sel_url_raw,
            node_ids=node_ids,
            urls=urls,
        )

        if selected_index is not None:
            selection["index"] = selected_index

        if selected_name:
            selection["name"] = selected_name

        if selected_index is not None and 0 <= selected_index < len(node_ids):
            node_id_value = node_ids[selected_index]
            if node_id_value:
                selection.setdefault("node_id", node_id_value)
            if selected_index < len(urls):
                url_value = urls[selected_index]
                if url_value:
                    selection.setdefault("url", url_value)

        if context_id:
            selection["context_id"] = context_id

        dataset["selection"] = selection

        metadata_list = []
        for entry in metadata_entries:
            metadata_list.append({k: v for k, v in entry.items() if v is not None})

        if image_batch:
            primary_image = image_batch[0]
        elif isinstance(selected_image_tensor, torch.Tensor):
            primary_image = selected_image_tensor
        elif image_list:
            primary_image = image_list[0]
        else:
            primary_image = create_dummy_image_tensor()

        if not isinstance(selected_image_tensor, torch.Tensor):
            selected_image_tensor = primary_image if isinstance(primary_image, torch.Tensor) else create_dummy_image_tensor()

        ensure_dataset_context(dataset, context_id)
        dataset_output = copy.deepcopy(dataset)
        config_output = build_editor_config_from_dataset(dataset_output)

        return (
            primary_image,
            image_list,
            names,
            creation_dates,
            image_count,
            selected_image_tensor,
            selected_index,
            selected_name,
            metadata_list,
            dataset_output,
            config_output,
        )

    def _prepare_dataset(self, session: EditingSession, ui_dataset: dict) -> dict:
        if isinstance(ui_dataset, dict) and ui_dataset:
            dataset = copy.deepcopy(ui_dataset)
        else:
            dataset = session.build_dataset([], filename_prefix="load_and_edit")

        context_id = dataset.get("context_id")
        if not context_id:
            context_id = session._build_context_path()
            dataset["context_id"] = context_id

        columns = dataset.setdefault("columns", []) if isinstance(dataset.get("columns"), list) else []
        if columns is not dataset.get("columns"):
            dataset["columns"] = columns

        has_path = False
        has_status = False
        for column in columns:
            column_id = column.get("id") if isinstance(column, dict) else None
            if column_id == "path":
                has_path = True
                column.setdefault("title", context_id)
                if not column.get("title"):
                    column["title"] = context_id
            elif column_id == "status":
                has_status = True

        if not has_path:
            columns.insert(0, {"id": "path", "title": context_id})
        if not has_status:
            columns.append({"id": "status", "title": "completed"})

        nodes = dataset.get("nodes")
        if not isinstance(nodes, list):
            dataset["nodes"] = []

        ensure_dataset_context(dataset)

        return dataset
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LoadAndEditImages": LF_LoadAndEditImages,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LoadAndEditImages": "Load and edit images",
}
# endregion
