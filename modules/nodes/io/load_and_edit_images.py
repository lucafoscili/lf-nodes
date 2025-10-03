import copy

from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input, SAMPLERS, SCHEDULERS
from ...utils.helpers.editing import EditingSession
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
    OUTPUT_IS_LIST = (False, True, False, False)
    RETURN_NAMES = ("image", "image_list", "selection", "dataset")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.JSON, Input.JSON)

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
        image_list = list(results.image_list or [])
        selected_image, selection = self._resolve_selection(results, dataset, image_list)

        dataset_output = dict(dataset)
        dataset_output.setdefault("selection", selection)

        return (selected_image, image_list, selection, dataset_output)

    # region internal helpers
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

        return dataset

    def _resolve_selection(self, results, dataset, image_list):
        selection = results.selected_entry or dataset.get("selection", {}) or {}

        context_id = dataset.get("context_id")
        if context_id:
            if isinstance(selection, dict):
                selection = {**selection, "context_id": context_id}
            else:
                selection = {"context_id": context_id}

        index = selection.get("index") if isinstance(selection, dict) else None
        if isinstance(index, int) and 0 <= index < len(image_list):
            selected_image = image_list[index]
        elif results.batch_list:
            selected_image = results.batch_list[0]
        elif image_list:
            selected_image = image_list[0]
        else:
            selected_image = create_dummy_image_tensor()

        return selected_image, selection
    # endregion
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LoadAndEditImages": LF_LoadAndEditImages,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LoadAndEditImages": "Load and edit images",
}
# endregion
