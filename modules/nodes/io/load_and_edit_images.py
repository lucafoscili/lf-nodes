import copy
import torch

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, SAMPLERS, SCHEDULERS
from ...utils.helpers.editing import (
    EditingSession,
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
                "sampler": (SAMPLERS, {
                    "tooltip": "Optional sampler reused by inpaint edits.",
                    "default": "dpmpp_2m"
                }),
                "scheduler": (SCHEDULERS, {
                    "tooltip": "Optional scheduler reused by inpaint edits.",
                    "default": "normal"
                }),
                "cfg": (Input.FLOAT, {
                    "default": 7.0,
                    "min": 0.0,
                    "max": 30.0,
                    "step": 0.1,
                    "tooltip": "CFG scale used as the starting value for inpaint edits."
                }),
                "positive_prompt": (Input.STRING, {
                    "default": "",
                    "tooltip": "Optional positive prompt used to pre-fill the inpaint editor."
                }),
                "negative_prompt": (Input.STRING, {
                    "default": "",
                    "tooltip": "Optional negative prompt used to pre-fill the inpaint editor."
                }),
                "positive_conditioning": (Input.CONDITIONING, {
                    "tooltip": "Optional positive conditioning to reuse during inpaint edits."
                }),
                "negative_conditioning": (Input.CONDITIONING, {
                    "tooltip": "Optional negative conditioning to reuse during inpaint edits."
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
    OUTPUT_IS_LIST = (False, True, True, True, False, False, False, False, False, False)
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
    )

    def on_exec(self, **kwargs: dict):
        node_id = kwargs.get("node_id")
        self._temp_cache.cleanup()

        session = EditingSession(node_id=node_id, temp_cache=self._temp_cache)

        model_value = normalize_list_to_value(kwargs.get("model"))
        clip_value = normalize_list_to_value(kwargs.get("clip"))
        vae_value = normalize_list_to_value(kwargs.get("vae"))
        sampler_value = normalize_list_to_value(kwargs.get("sampler"))
        scheduler_value = normalize_list_to_value(kwargs.get("scheduler"))

        cfg_raw = normalize_list_to_value(kwargs.get("cfg"))
        try:
            cfg_value = float(cfg_raw) if cfg_raw is not None else None
        except (TypeError, ValueError):
            cfg_value = None

        seed_raw = normalize_list_to_value(kwargs.get("seed"))
        try:
            seed_value = int(seed_raw) if seed_raw not in (None, "") else None
        except (TypeError, ValueError):
            seed_value = None

        positive_prompt_raw = normalize_list_to_value(kwargs.get("positive_prompt"))
        positive_prompt_value = str(positive_prompt_raw) if positive_prompt_raw not in (None, "") else ""

        negative_prompt_raw = normalize_list_to_value(kwargs.get("negative_prompt"))
        negative_prompt_value = str(negative_prompt_raw) if negative_prompt_raw not in (None, "") else ""

        positive_conditioning_value = normalize_conditioning(kwargs.get("positive_conditioning"))
        negative_conditioning_value = normalize_conditioning(kwargs.get("negative_conditioning"))

        ui_dataset = normalize_json_input(kwargs.get("ui_widget", {})) or {}
        dataset = self._prepare_dataset(session, ui_dataset)

        inpaint_defaults: dict[str, object] = {}
        if cfg_value is not None:
            inpaint_defaults["cfg"] = cfg_value
        if seed_value is not None and seed_value >= 0:
            inpaint_defaults["seed"] = seed_value
        if positive_prompt_value:
            inpaint_defaults["positive_prompt"] = positive_prompt_value
        if negative_prompt_value:
            inpaint_defaults["negative_prompt"] = negative_prompt_value

        if inpaint_defaults:
            dataset.setdefault("defaults", {})["inpaint"] = inpaint_defaults

        session.register_context(
            dataset,
            model=model_value,
            clip=clip_value,
            vae=vae_value,
            sampler=sampler_value,
            scheduler=scheduler_value,
            cfg=cfg_value,
            seed=seed_value,
            positive_prompt=positive_prompt_value or None,
            negative_prompt=negative_prompt_value or None,
            positive_conditioning=positive_conditioning_value,
            negative_conditioning=negative_conditioning_value,
        )

        PromptServer.instance.send_sync(
            f"{EVENT_PREFIX}loadandeditimages",
            {
                "node": node_id,
                "dataset": dataset,
            },
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
