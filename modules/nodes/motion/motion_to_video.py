"""Render a portable LF motion file using a locally registered SMPL-X body."""

import json
from pathlib import Path

import folder_paths
import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input, USER_FOLDER
from ...utils.helpers.comfy import resolve_filepath, safe_send_sync
from ...utils.helpers.motion.render import DEFAULT_BETAS, DEFAULT_IMAGE_FRAME_LIMIT, render_motion, resolve_body_model


class LF_MotionToVideo:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "motion_file": (Input.STRING, {"default": "", "tooltip": "Path to an lf.motion.v1 JSON file."}),
                "body": (["female", "neutral", "male"], {"default": "female"}),
                "betas": (Input.STRING, {"default": DEFAULT_BETAS, "tooltip": "1 to 10 SMPL-X shape coefficients; remaining coefficients are zero."}),
                "width": (Input.INTEGER, {"default": 320, "min": 64, "max": 2048, "step": 2, "tooltip": "Width of each view."}),
                "height": (Input.INTEGER, {"default": 560, "min": 64, "max": 2048, "step": 2, "tooltip": "Height of the preview."}),
            },
            "optional": {
                "source_video": (Input.STRING, {"default": "", "tooltip": "Optional source video path for a synchronized comparison."}),
                "ui_widget": (Input.LF_CODE, {"default": ""}),
                "image_frame_limit": (Input.INTEGER, {"default": DEFAULT_IMAGE_FRAME_LIMIT, "min": 0, "tooltip": "Maximum evenly spaced IMAGE frames, including first and last when at least two are selected. 0 requests all. Combined uint8/float32 selection is limited to 256 MiB; MP4 always retains every frame."}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = False
    OUTPUT_NODE = True
    RETURN_TYPES = (Input.STRING, Input.IMAGE, Input.IMAGE)
    RETURN_NAMES = ("video_file", "frames", "frame_list")
    OUTPUT_IS_LIST = (False, False, True)
    OUTPUT_TOOLTIPS = (
        "Saved MP4 path.",
        "Selected preview frames as one RGB IMAGE batch with shared geometry; MP4 retains every frame.",
        "Selected individual preview frames [1,H,W,3] in playback order, sharing batch storage.",
    )

    def on_exec(self, motion_file, body="female", betas=DEFAULT_BETAS, width=320, height=560, source_video="", image_frame_limit=DEFAULT_IMAGE_FRAME_LIMIT, **kwargs):
        model_path = resolve_body_model(body)
        output_root = Path(folder_paths.get_output_directory()).resolve()
        output_file, _, _ = resolve_filepath(
            filename_prefix=f"{USER_FOLDER}/Motion/preview", base_output_path=str(output_root),
            extension="mp4", add_counter=True,
        )
        frames, timing = render_motion(
            motion_file, model_path, body, betas, width, height, output_file, source_video, image_frame_limit,
        )
        batch = torch.from_numpy(frames).to(dtype=torch.float32).div_(255)
        frame_list = [batch[index:index + 1] for index in range(len(batch))]
        relative = Path(output_file).resolve().relative_to(output_root).as_posix()
        summary = {"video_file": relative, **timing, "body": body, "betas": betas}
        payload = {"value": json.dumps(summary), "json": summary, "file_names": [relative]}
        safe_send_sync("motiontovideo", payload, kwargs.get("node_id"))
        return {"ui": {"lf_output": [payload]}, "result": (str(output_file), batch, frame_list)}


NODE_CLASS_MAPPINGS = {"LF_MotionToVideo": LF_MotionToVideo}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_MotionToVideo": "Motion to video"}
