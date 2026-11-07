"""Retarget LF motion onto an explicitly mapped rigged GLB."""

import json
from pathlib import Path

import folder_paths

from . import CATEGORY
from ...utils.constants import FUNCTION, Input, USER_FOLDER
from ...utils.helpers.comfy import resolve_filepath, safe_send_sync
from ...utils.helpers.motion.render import DEFAULT_BETAS, resolve_body_model
from ...utils.helpers.motion.retarget_smplx import retarget_motion


def _policy_names(value, name):
    try:
        names = json.loads(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a JSON array of target bone names.") from error
    if not isinstance(names, list) or any(not isinstance(item, str) or not item.strip() for item in names):
        raise ValueError(f"{name} must be a JSON array of target bone names.")
    return tuple(names)


class LF_RetargetMotion:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "motion_file": (Input.STRING, {"default": "", "tooltip": "Path to an lf.motion.v1 JSON file."}),
                "body": (["female", "neutral", "male"], {"default": "female"}),
                "betas": (Input.STRING, {"default": DEFAULT_BETAS, "tooltip": "1 to 10 source SMPL-X shape coefficients; remaining coefficients are zero."}),
                "glb_path": (Input.STRING, {"default": "", "tooltip": "Path to a rigged GLB with embedded skin and mesh data."}),
                "bone_map_path": (Input.STRING, {"default": "", "tooltip": "Path to the explicit SMPL-X to target bone map JSON."}),
            },
            "optional": {
                "keep_rest_facing": (Input.STRING, {"default": "[]", "tooltip": "JSON array of target bone names whose rest facing is preserved."}),
                "flatten_slope": (Input.STRING, {"default": "[]", "tooltip": "JSON array of target bone names whose rest slope is flattened."}),
                "ui_widget": (Input.LF_CODE, {"default": ""}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = False
    OUTPUT_NODE = True
    RETURN_TYPES = (Input.STRING, Input.JSON)
    RETURN_NAMES = ("glb_file", "report")
    OUTPUT_IS_LIST = (False, False)
    OUTPUT_TOOLTIPS = (
        "Saved animated GLB path under ComfyUI output.",
        "Retarget coverage and validation report, including output-relative GLB and report filenames.",
    )

    def on_exec(self, motion_file, body="female", betas=DEFAULT_BETAS, glb_path="", bone_map_path="",
                keep_rest_facing="[]", flatten_slope="[]", **kwargs):
        facing = _policy_names(keep_rest_facing, "keep_rest_facing")
        slope = _policy_names(flatten_slope, "flatten_slope")
        model_path = resolve_body_model(body)
        blob, report = retarget_motion(
            motion_file, model_path, body, betas, glb_path, bone_map_path,
            keep_rest_facing=facing, flatten_slope=slope,
        )
        output_root = Path(folder_paths.get_output_directory()).resolve()
        output_file, _, _ = resolve_filepath(
            filename_prefix=f"{USER_FOLDER}/Motion/retarget", base_output_path=str(output_root),
            extension="glb", add_counter=True,
        )
        output = Path(output_file).resolve()
        report_file = output.with_suffix(".json")
        relative = output.relative_to(output_root).as_posix()
        relative_report = report_file.relative_to(output_root).as_posix()
        summary = {**report, "glb_file": relative, "report_file": relative_report}
        encoded_report = json.dumps(summary, ensure_ascii=False, allow_nan=False, indent=2)
        # Publish the event only after both durable artifacts are complete.
        output.write_bytes(blob)
        report_file.write_text(encoded_report + "\n", encoding="utf-8", newline="\n")
        payload = {"value": encoded_report, "json": summary, "file_names": [relative, relative_report]}
        safe_send_sync("retargetmotion", payload, kwargs.get("node_id"))
        return {"ui": {"lf_output": [payload]}, "result": (str(output), summary)}


NODE_CLASS_MAPPINGS = {"LF_RetargetMotion": LF_RetargetMotion}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_RetargetMotion": "Retarget motion"}
