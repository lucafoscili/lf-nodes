import os
from typing import Any, Dict

import torch
from server import PromptServer
from folder_paths import get_folder_paths

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers import normalize_list_to_value

try:
    from safetensors.torch import load_file as load_safetensors
    _HAS_SAFETENSORS = True
except Exception:
    _HAS_SAFETENSORS = False

def _load_state_dict(file_path: str):
    """Best-effort loader for IPAdapter weight file.

    Supports .safetensors (preferred) and .pt/.bin/.pth via torch.load.
    Returns a state_dict or None if loading fails (error is propagated upstream)."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".safetensors" and _HAS_SAFETENSORS:
        return load_safetensors(file_path, device="cpu")
    
    # Fallback to torch.load (map to cpu to be conservative)
    return torch.load(file_path, map_location="cpu")


def _markdown(title: str, lines: list[str]):
    return f"## {title}\n\n" + "\n".join(lines)


def _send_log(event: str, node_id: str, title: str, lines: list[str]):
    PromptServer.instance.send_sync(f"{EVENT_PREFIX}{event}", {"node": node_id, "value": _markdown(title, lines)})


def _get_ipadapter_base_dir(preferred_folder: str | None = None) -> str:
    """Resolve the base directory where IPAdapter weights are stored.

    ComfyUI exposes model folders via `get_folder_paths(key)`; the `extra_model_paths.yaml`
    typically maps `ipadapter: models/ipadapter`.
    If preferred_folder is provided it is looked up first, otherwise we fallback to the
    canonical 'ipadapter'."""
    search_keys = []
    if preferred_folder:
        search_keys.append(preferred_folder)
    if "ipadapter" not in search_keys:
        search_keys.append("ipadapter")
    for key in search_keys:
        try:
            paths = get_folder_paths(key)
            if paths:
                return paths[0]
        except Exception:
            continue
    raise RuntimeError("Unable to resolve IPAdapter models directory. Ensure extra_model_paths.yaml defines 'ipadapter'.")

# region LF_LoadIPAdapterModel
class LF_LoadIPAdapterModel:
    """Load an IPAdapter weight file (safetensors / pt) and expose it as an `IPADAPTER` object.

    This is an initial / minimal implementation. It does not patch the diffusion model yet; instead
    it prepares an object consumed by a subsequent Apply node. Future iterations can integrate the
    official IP-Adapter repository logic and attention processor injection.
    """

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = ("IPADAPTER",)
    RETURN_NAMES = ("ipadapter",)

    @classmethod
    def INPUT_TYPES(cls):  # noqa: N802 (ComfyUI naming convention)
        return {
            "required": {
                "filename": (Input.STRING, {"default": "", "tooltip": "Exact filename of the IPAdapter weights located in the ipadapter folder."}),
            },
            "optional": {
                "folder_key": (Input.STRING, {"default": "ipadapter", "tooltip": "Custom folder key mapped in extra_model_paths.yaml (defaults to 'ipadapter')."}),
                "load_weights": (Input.BOOLEAN, {"default": True, "tooltip": "If true, the state dict is loaded immediately. If false, only metadata is returned."}),
                "ui_widget": (Input.LF_CODE, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    def on_exec(self, **kwargs: Dict[str, Any]):  # noqa: D401
        node_id = kwargs.get("node_id")
        filename = normalize_list_to_value(kwargs.get("filename"))
        folder_key = normalize_list_to_value(kwargs.get("folder_key")) or "ipadapter"
        load_weights = bool(kwargs.get("load_weights", True))

        lines = []
        if not filename:
            raise ValueError("'filename' is required (e.g. 'ip-adapter-plus-face_sd15.safetensors').")

        base_dir = _get_ipadapter_base_dir(folder_key)
        file_path = os.path.join(base_dir, filename)

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"IPAdapter file not found: {file_path}")

        lines.append(f"- 📄 File: `{file_path}`")
        lines.append(f"- 📦 Load weights: {'yes' if load_weights else 'no'}")
        _send_log("loadipadapter", node_id, "Load IPAdapter Model", lines)

        state_dict = None
        if load_weights:
            try:
                state_dict = _load_state_dict(file_path)
                lines.append("- ✅ Weights loaded into CPU memory")
                # Optional flatten: some files may organize weights in nested sections (e.g. image_proj / ip_adapter)
                try:
                    if isinstance(state_dict, dict) and state_dict and any(isinstance(v, dict) for v in state_dict.values()):
                        flat: Dict[str, Any] = {}
                        for section, block in state_dict.items():
                            if isinstance(block, dict):
                                for k, t in block.items():
                                    flat[f"{section}.{k}"] = t
                            else:
                                flat[str(section)] = block
                        state_dict = flat
                        lines.append(f"- 🔧 Flattened nested sections → {len(state_dict)} tensors")
                except Exception as fe:  # pragma: no cover
                    lines.append(f"- ⚠️ Flatten skipped: {fe}")

                # Structural introspection summary (best-effort)
                try:
                    total_tensors = len(state_dict)
                    perceiver_layers = set()
                    lora_blocks = set()
                    has_proj_k = False
                    has_proj_v = False
                    proj_in = False
                    proj_out = False
                    k_ip = 0
                    v_ip = 0
                    linear_shapes: Dict[str, int] = {}
                    for k, v in list(state_dict.items()):
                        if isinstance(v, torch.Tensor) and v.dim() == 2:
                            shape_key = f"{tuple(v.shape)}"
                            linear_shapes.setdefault(shape_key, 0)
                            linear_shapes[shape_key] += 1
                        if k.startswith("perceiver_resampler.layers."):
                            segs = k.split('.')
                            if len(segs) > 2 and segs[2].isdigit():
                                perceiver_layers.add(int(segs[2]))
                        if k.endswith("to_q_lora.down.weight"):
                            block_id = k.split('.')[0]
                            if block_id.isdigit():
                                lora_blocks.add(int(block_id))
                        if 'proj_k' in k and k.endswith('.weight'):
                            has_proj_k = True
                        if 'proj_v' in k and k.endswith('.weight'):
                            has_proj_v = True
                        if 'proj_in.weight' in k:
                            proj_in = True
                        if 'proj_out.weight' in k:
                            proj_out = True
                        if k.endswith('to_k_ip.weight'):
                            k_ip += 1
                        if k.endswith('to_v_ip.weight'):
                            v_ip += 1
                    lines.append("- 🧩 Structure summary:")
                    lines.append(f"   • total_tensors: {total_tensors}")
                    if perceiver_layers:
                        lines.append(f"   • perceiver_layers: {sorted(perceiver_layers)}")
                    lines.append(f"   • lora_blocks: {len(lora_blocks)}")
                    lines.append(f"   • proj_k: {has_proj_k} | proj_v: {has_proj_v} | proj_in: {proj_in} | proj_out: {proj_out}")
                    lines.append(f"   • ip_k_heads: {k_ip} | ip_v_heads: {v_ip}")
                    if linear_shapes:
                        sample_shapes = list(linear_shapes.items())[:6]
                        shape_str = ", ".join([f"{s}:{c}" for s,c in sample_shapes])
                        lines.append(f"   • linear_shapes_sample: {shape_str}")
                except Exception as ie:  # pragma: no cover
                    lines.append(f"- ⚠️ Introspection failed: {ie}")
            except Exception as e:  # pragma: no cover
                lines.append(f"- ❌ Failed loading weights: {e}")
                _send_log("loadipadapter", node_id, "Load IPAdapter Model", lines)
                raise
        else:
            lines.append("- ⏩ Skipped weight load (metadata only)")

        ipadapter_obj = {
            "type": "ipadapter_weights",
            "path": file_path,
            "filename": filename,
            "state_dict": state_dict,
            "loaded": state_dict is not None,
        }

        _send_log("loadipadaptermodel", node_id, "Load IPAdapter Model", lines)

        return (ipadapter_obj,)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_LoadIPAdapterModel": LF_LoadIPAdapterModel,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_LoadIPAdapterModel": "Load IPAdapter model",
}
# endregion
