import comfy.sd
import comfy.utils
import folder_paths
import random
import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input, INT_MAX
from ...utils.helpers.comfy import get_comfy_list, safe_send_sync
from ...utils.helpers.logic import (
    build_is_changed_tuple,
    filter_list,
    LazyCache,
    normalize_json_input,
    normalize_list_to_value,
    register_cache,
    register_selector_list,
)
from ...utils.helpers.ui import create_history_node

# region LF_VAESelector
class LF_VAESelector:
    initial_list: list[str] = []
    _CACHE = LazyCache()
    register_cache(_CACHE)

    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "vae": (["None"] + self.initial_list, {
                    "default": "None",
                    "tooltip": "VAE used to generate the image."
                }),
                "enable_history": (Input.BOOLEAN, {
                    "default": True,
                    "tooltip": "Enables history, saving the execution value and date of the widget."
                }),
                "randomize": (Input.BOOLEAN, {
                    "default": False,
                    "tooltip": "Selects a VAE randomly."
                }),
                "filter": (Input.STRING, {
                    "default": "",
                    "tooltip": "When randomization is active, this field can be used to filter VAE names. Supports wildcards (*)."
                }),
                "seed": (Input.INTEGER, {
                    "default": 42,
                    "min": 0,
                    "max": INT_MAX,
                    "tooltip": "Seed value for when randomization is active."
                }),
            },
            "optional":{
                "ui_widget": (Input.LF_HISTORY, {
                    "default": {}
                }),
            },
            "hidden": {"node_id": "UNIQUE_ID"}
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "Combo list of VAEs.",
        "Selected VAE item as a string.",
        "Loaded VAE model.",
    )
    RETURN_NAMES = ("combo", "string", "vae")
    RETURN_TYPES = (initial_list, Input.STRING, Input.VAE)

    def on_exec(self, **kwargs: dict):
        vae: str = normalize_list_to_value(kwargs.get("vae"))
        enable_history: bool = normalize_list_to_value(kwargs.get("enable_history"))
        randomize: bool = normalize_list_to_value(kwargs.get("randomize"))
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        filter: str = normalize_list_to_value(kwargs.get("filter"))
        ui_widget: dict = normalize_json_input(kwargs.get("ui_widget", {}))

        vaes = get_comfy_list("vae")

        nodes: list[dict] = ui_widget.get("nodes", [])
        dataset: dict = {
            "nodes": nodes
        }

        if randomize:
            if filter:
                vaes = filter_list(filter, vaes)
                if not vaes:
                    raise ValueError(f"Not found a model with the specified filter: {filter}")
            random.seed(seed)
            vae = random.choice(vaes)

        vae_model = None
        if vae and vae != "None":
            if vae in ["taesd", "taesdxl", "taesd3", "taef1"]:
                def _make_taesd_vae():
                    m = comfy.sd.VAE(sd=self.load_taesd(vae))
                    m.throw_exception_if_invalid()
                    return m
                vae_model = self._CACHE.get_or_set(("taesd-obj", vae), _make_taesd_vae)
            else:
                vae_path = folder_paths.get_full_path_or_raise("vae", vae)
                def _make_vae():
                    m = comfy.sd.VAE(sd=comfy.utils.load_torch_file(vae_path))
                    m.throw_exception_if_invalid()
                    return m
                vae_model = self._CACHE.get_or_set(("vae-obj", vae_path), _make_vae)

        if enable_history:
            create_history_node(vae, nodes)

        safe_send_sync("vaeselector", {
            "dataset": dataset,
        }, kwargs.get("node_id"))

        return (vae, vae, vae_model)

    @classmethod
    def IS_CHANGED(
        cls,
        vae,
        enable_history,
        randomize,
        filter,
        seed,
        ui_widget,
        node_id
    ):
        return build_is_changed_tuple(
            normalize_list_to_value(randomize),
            normalize_list_to_value(seed),
            normalize_list_to_value(filter),
            normalize_list_to_value(vae),
            normalize_list_to_value(enable_history),
        )

    @staticmethod
    def load_taesd(name):
        sd = {}
        approx_vaes = folder_paths.get_filename_list("vae_approx")

        encoder = next(filter(lambda a: a.startswith("{}_encoder.".format(name)), approx_vaes))
        decoder = next(filter(lambda a: a.startswith("{}_decoder.".format(name)), approx_vaes))

        enc = comfy.utils.load_torch_file(folder_paths.get_full_path_or_raise("vae_approx", encoder))
        for k in enc:
            sd["taesd_encoder.{}".format(k)] = enc[k]

        dec = comfy.utils.load_torch_file(folder_paths.get_full_path_or_raise("vae_approx", decoder))
        for k in dec:
            sd["taesd_decoder.{}".format(k)] = dec[k]

        if name == "taesd":
            sd["vae_scale"] = torch.tensor(0.18215)
            sd["vae_shift"] = torch.tensor(0.0)
        elif name == "taesdxl":
            sd["vae_scale"] = torch.tensor(0.13025)
            sd["vae_shift"] = torch.tensor(0.0)
        elif name == "taesd3":
            sd["vae_scale"] = torch.tensor(1.5305)
            sd["vae_shift"] = torch.tensor(0.0609)
        elif name == "taef1":
            sd["vae_scale"] = torch.tensor(0.3611)
            sd["vae_shift"] = torch.tensor(0.1159)
        return sd
# endregion

_VAE_SELECTOR_LIST = register_selector_list(
    LF_VAESelector,
    lambda: get_comfy_list("vae"),
)

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_VAESelector": LF_VAESelector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_VAESelector": "VAE selector",
}
# endregion
