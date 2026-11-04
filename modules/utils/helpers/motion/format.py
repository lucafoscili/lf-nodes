"""LF motion v1: SMPL-X axis angles in radians, translations in metres.

Camera coordinates are OpenCV (right, down, forward); world coordinates retain
the reconstruction's world frame. Hands use the flat-hand rest, without PCA.
This interchange contains parameters only, never licensed model data.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np


SCHEMA = "lf.motion.v1"
JOINT_NAMES = {
    "root": ["pelvis"],
    "body": [
        "left_hip", "right_hip", "spine1", "left_knee", "right_knee", "spine2",
        "left_ankle", "right_ankle", "spine3", "left_foot", "right_foot", "neck",
        "left_collar", "right_collar", "head", "left_shoulder", "right_shoulder",
        "left_elbow", "right_elbow", "left_wrist", "right_wrist",
    ],
    **{
        f"{side}_hand": [
            f"{side}_{finger}{joint}"
            for finger in ("index", "middle", "pinky", "ring", "thumb")
            for joint in (1, 2, 3)
        ]
        for side in ("left", "right")
    },
}
POSE_WIDTHS = {
    "global_orient": 3, "transl": 3, "body_pose": 63,
    "left_hand_pose": 45, "right_hand_pose": 45,
}


def validate_motion(motion: dict) -> dict:
    """Reject unsupported or unusable motion at the interchange boundary."""
    if not isinstance(motion, dict) or motion.get("schema") != SCHEMA:
        raise ValueError(f"Motion schema must be {SCHEMA}.")
    try:
        fps = float(motion["fps"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("Motion fps must be a positive finite number.") from error
    if not np.isfinite(fps) or fps <= 0:
        raise ValueError("Motion fps must be a positive finite number.")
    if motion.get("joint_names") != JOINT_NAMES:
        raise ValueError("Motion joint_names must use the LF motion v1 SMPL-X order.")
    count = None
    for space in ("world", "camera"):
        for field, width in POSE_WIDTHS.items():
            try:
                values = np.asarray(motion[space][field], dtype=np.float32)
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(f"Motion {space}.{field} must be a numeric frame array.") from error
            if values.ndim != 2 or values.shape[1] != width or not len(values):
                raise ValueError(f"Motion {space}.{field} must have shape [frames, {width}].")
            if count is not None and len(values) != count:
                raise ValueError(f"Motion {space}.{field} frame count does not match.")
            if not np.isfinite(values).all():
                raise ValueError(f"Motion {space}.{field} contains non-finite values.")
            count = len(values)
    if "betas" in motion:
        try:
            values = np.asarray(motion["betas"], dtype=np.float32)
        except (TypeError, ValueError) as error:
            raise ValueError("Motion betas must be a numeric frame array.") from error
        if values.ndim != 2 or values.shape[1] != 10 or len(values) not in (1, count):
            raise ValueError("Motion betas must have shape [1 or frames, 10].")
        if not np.isfinite(values).all():
            raise ValueError("Motion betas contains non-finite values.")
    return motion


def read_motion(path: str | Path) -> dict:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Motion file is missing: {path}")
    try:
        motion = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError) as error:
        raise ValueError(f"Invalid motion JSON: {path}: {error}") from error
    return validate_motion(motion)


def write_motion(path: str | Path, motion: dict) -> None:
    validate_motion(motion)
    Path(path).write_text(
        json.dumps(motion, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n",
        encoding="utf-8", newline="\n",
    )
