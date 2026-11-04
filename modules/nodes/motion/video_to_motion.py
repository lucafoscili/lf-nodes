"""Capture local video motion using a separately installed RGB MoCap runtime."""

import json
from pathlib import Path

import folder_paths

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.motion.rgb_mocap import run_video_to_motion


class LF_VideoToMotion:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path": (Input.STRING, {"default": "", "tooltip": "Existing local video file with a visible full body."}),
                "engine": (["ExMR"], {"default": "ExMR", "tooltip": "Uses the installed RGB MoCap ExMR runtime and registered models."}),
                "static_camera": (Input.BOOLEAN, {"default": True, "tooltip": "Use a fixed camera; disable for ExMR SimpleVO camera estimation."}),
                "smoothing": (Input.BOOLEAN, {"default": True, "tooltip": "Apply ExMR global motion smoothing."}),
                "gpu_index": (Input.INTEGER, {"default": 0, "min": 0, "max": 31, "tooltip": "Physical CUDA device visible to the isolated worker."}),
            },
            "optional": {
                "include_shape": (Input.BOOLEAN, {"default": False, "tooltip": "Include inferred body shape in JSON and BVH/FBX. Off uses a neutral export skeleton and pose/root/hand motion only."}),
                "ui_widget": (Input.LF_CODE, {"default": ""}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = False
    RETURN_TYPES = (Input.STRING, Input.STRING, Input.STRING, Input.STRING)
    RETURN_NAMES = ("motion_file", "bvh_file", "fbx_file", "project_dir")
    OUTPUT_IS_LIST = (False, False, False, False)
    OUTPUT_TOOLTIPS = (
        "Versioned lf.motion.v1 pose, root and hand motion JSON under ComfyUI output.",
        "RGB MoCap BVH motion export under ComfyUI output.",
        "RGB MoCap FBX motion export under ComfyUI output.",
        "RGB MoCap model project containing inference artifacts and stage diagnostics.",
    )
    DESCRIPTION = "Capture ExMR body, root and finger motion from a local video using isolated RGB MoCap workers. Requires RGB_MOCAP_PATH and installed registered models; never installs or downloads dependencies."

    def on_exec(self, video_path, engine="ExMR", static_camera=True, smoothing=True,
                gpu_index=0, include_shape=False, ui_widget=None, node_id=None):
        def progress(event):
            if event.get("type") == "progress":
                safe_send_sync("videotomotion", {"value": event.get("message", "Processing motion...")}, node_id)

        output = run_video_to_motion(video_path, folder_paths.get_output_directory(), engine=engine,
            static_camera=static_camera, smoothing=smoothing, gpu_index=gpu_index,
            include_shape=include_shape, progress=progress)
        root = Path(folder_paths.get_output_directory()).resolve()
        files = [Path(output[key]).resolve().relative_to(root).as_posix()
                 for key in ("motion_file", "bvh_file", "fbx_file")]
        payload = {"value": json.dumps(output, indent=2), "json": output, "file_names": files}
        safe_send_sync("videotomotion", payload, node_id)
        return {"ui": {"lf_output": [payload]},
                "result": tuple(output[key] for key in self.RETURN_NAMES)}


NODE_CLASS_MAPPINGS = {"LF_VideoToMotion": LF_VideoToMotion}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_VideoToMotion": "Video to motion"}
