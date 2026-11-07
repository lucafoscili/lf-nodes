"""LF motion/bone-map boundary and the SMPL-X adapter to the NumPy solver."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from .format import JOINT_NAMES, read_motion
from . import retarget as core


SOURCE_NAMES = [name for group in JOINT_NAMES.values() for name in group]
# SMPL-X inserts jaw/eyes after the body; LF v1 intentionally carries neither.
MODEL_JOINTS = list(range(22)) + list(range(25, 55))
CORE_BONES = (
    "pelvis", "left_hip", "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow", "left_wrist", "right_wrist",
)


def read_bone_map(path, target_names):
    """Validate lf.bone-map.v1 once, naming the document and offending field."""
    path = Path(path)
    def fail(field, reason):
        raise ValueError(f"Bone map {path}: {field}: {reason}")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        fail("document", str(error))
    if not isinstance(document, dict) or document.get("schema") != "lf.bone-map.v1":
        fail("schema", "expected lf.bone-map.v1")
    if document.get("source") != "smplx":
        fail("source", "expected smplx")
    if document.get("unmapped") != "rest":
        fail("unmapped", "must be present and equal rest")
    bones = document.get("bones")
    if not isinstance(bones, dict):
        fail("bones", "expected source-to-target object")
    source_names, target_names = set(SOURCE_NAMES), set(target_names)
    targets = set()
    for source, target in bones.items():
        if source not in source_names:
            fail("bones", f"unknown source joint {source!r}")
        if not isinstance(target, str) or target not in target_names:
            fail("bones", f"unknown target bone {target!r}")
        if target in targets:
            fail("bones", f"duplicate target bone {target!r}")
        targets.add(target)
    chains = document.get("chains", [])
    if not isinstance(chains, list):
        fail("chains", "expected an array")
    chain_sources, chain_targets = set(), set()
    for index, chain in enumerate(chains):
        field = f"chains[{index}]"
        if not isinstance(chain, dict):
            fail(field, "expected source and target runs")
        for key, known, used in (("source", source_names, chain_sources), ("target", target_names, chain_targets)):
            run = chain.get(key)
            if not isinstance(run, list) or not run:
                fail(f"{field}.{key}", "expected a nonempty joint-name array")
            seen = set()
            for name in run:
                if not isinstance(name, str) or name not in known:
                    fail(f"{field}.{key}", f"unknown joint {name!r}")
                if name in seen or (key == "target" and name in used):
                    fail(f"{field}.{key}", f"duplicate chain joint {name!r}")
                seen.add(name)
                used.add(name)
    # Injective across both fields: a target bone belongs to one pair or one chain.
    for name in sorted(chain_targets & targets):
        fail("chains", f"target bone {name!r} is also a bones target")
    follow = document.get("follow", {})
    if not isinstance(follow, dict):
        fail("follow", "expected a follower-to-leader object")
    try:
        core.follow_pairs(follow, targets | chain_targets, target_names)
    except ValueError as error:
        fail("follow", str(error))
    # Anchors the solve reads by name (root, leg scale, axis check) belong to
    # bones; the spine may arrive through a chain.
    covered = set(bones)
    for name in CORE_BONES:
        if name not in covered:
            fail("bones", f"missing core joint {name!r}")
    if not (covered | chain_sources).intersection(("spine1", "spine2", "spine3")):
        fail("bones", "missing core joint: at least one of spine1, spine2, spine3 (in bones or a chain)")
    if not covered.intersection(("neck", "head")):
        fail("bones", "missing core joint: at least one of neck, head")
    return document


def rest_joints(model, betas):
    """Evaluate shape-dependent SMPL-X rest joints, without pose or translation."""
    import torch

    shape = torch.as_tensor(np.asarray(betas).reshape(-1, 10), dtype=torch.float32)
    results = []
    for start in range(0, len(shape), 16):
        batch = shape[start:start + 16]
        count = len(batch)
        zeros = torch.zeros(count, 3)
        with torch.inference_mode():
            result = model(betas=batch, global_orient=zeros, transl=zeros,
                           body_pose=torch.zeros(count, 63), left_hand_pose=torch.zeros(count, 45),
                           right_hand_pose=torch.zeros(count, 45), jaw_pose=zeros, leye_pose=zeros,
                           reye_pose=zeros, expression=torch.zeros(count, 10))
        results.append(result.joints[:, MODEL_JOINTS].cpu().numpy())
    return np.concatenate(results)


def source_skeleton(motion, model, betas):
    """Adapt model joints and LF's world local axis angles to generic arrays."""
    positions = rest_joints(model, betas)[0]
    model_parents = np.asarray(model.parents.cpu(), dtype=int)
    lookup = {joint: index for index, joint in enumerate(MODEL_JOINTS)}
    parents = np.array([lookup.get(int(model_parents[joint]), -1) for joint in MODEL_JOINTS])
    skeleton = dict(names=SOURCE_NAMES.copy(), parents=parents, rest_positions=positions,
                    rest_rotations=np.tile([0., 0., 0., 1.], (len(SOURCE_NAMES), 1)))
    params = motion["world"]
    count = len(params["transl"])
    angles = np.concatenate([np.asarray(params[key]).reshape(count, -1, 3)
                             for key in ("global_orient", "body_pose", "left_hand_pose", "right_hand_pose")], axis=1)
    rotations = core.local_to_world_rotations(core.axis_angle_to_quaternion(angles), parents)
    roots = np.asarray(params["transl"], dtype=np.float64) + positions[0]
    return skeleton, rotations, roots


def camera_from_world(motion, model):
    """Clip-shape camera transform, independently of the chosen render shape."""
    shape = np.asarray(motion.get("betas", np.zeros((1, 10))), dtype=np.float32)
    pelvis = rest_joints(model, shape)[:, 0]
    camera = motion["camera"]
    world = motion["world"]
    rotation = core.quaternion_to_matrix(core.quaternion_multiply(
        core.axis_angle_to_quaternion(camera["global_orient"]),
        core.quaternion_inverse(core.axis_angle_to_quaternion(world["global_orient"])),
    ))
    camera_root = np.asarray(camera["transl"]) + pelvis
    world_root = np.asarray(world["transl"]) + pelvis
    translation = camera_root - np.einsum("fij,fj->fi", rotation, world_root)
    return rotation, translation, camera_root


def retarget_motion(motion_file, model_path, body, betas, glb_path, bone_map_path,
                    keep_rest_facing=(), flatten_slope=()):
    """One path: read adapters -> generic solve -> append GLB animation/report."""
    from .render import load_body_model, parse_betas
    from .retarget_glb import load_glb_target, validate_glb_axes, append_glb_animation

    motion = read_motion(motion_file)
    try:
        target = load_glb_target(glb_path)
    except (OSError, ValueError) as error:
        raise ValueError(f"Target GLB {glb_path}: {error}") from error
    target_names = [target["document"]["nodes"][node]["name"] for node in target["joint_nodes"]]
    mapping = read_bone_map(bone_map_path, target_names)
    pairs = list(mapping["bones"].items())
    for field, names in (("keep_rest_facing", keep_rest_facing), ("flatten_slope", flatten_slope)):
        if not isinstance(names, (list, tuple)) or any(not isinstance(name, str) or name not in target_names for name in names):
            raise ValueError(f"{field} must list target skin bone names; got {names!r}")
    try:
        validate_glb_axes(target, pairs)
    except ValueError as error:
        raise ValueError(f"Target GLB {glb_path}: {error}") from error
    model = load_body_model(Path(model_path), body)
    source, rotations, roots = source_skeleton(motion, model, parse_betas(betas))
    try:
        solved = core.retarget_motion(rotations, roots, source, target["skeleton"], pairs,
                                      chains=mapping.get("chains", []), follow=mapping.get("follow", {}),
                                      keep_rest_facing=keep_rest_facing, flatten_slope=flatten_slope)
    except ValueError as error:
        raise ValueError(f"Retarget solve (bone map {bone_map_path}, target {glb_path}): {error}") from error
    covered_source, covered_target = set(mapping["bones"]), set(mapping["bones"].values())
    for chain in mapping.get("chains", []):
        covered_source.update(chain["source"])
        covered_target.update(chain["target"])
    followers = dict(mapping.get("follow", {}))
    covered_target.update(followers)
    root_name = mapping["bones"]["pelvis"]
    target_root = target["skeleton"]["names"].index(root_name)
    report = {
        "held_target_bones": [name for name in target_names if name not in covered_target],
        "followers": followers,
        "dropped_source_joints": [name for name in SOURCE_NAMES if name not in covered_source],
        "fingers": {side: "rest" for side in ("left", "right")
                    if f"{side}_wrist" in covered_source and not covered_source.intersection(JOINT_NAMES[f"{side}_hand"])},
        "s": solved["scale"], "source_rest_pelvis": source["rest_positions"][0].tolist(),
        "target_rest_pelvis": target["skeleton"]["rest_positions"][target_root].tolist(),
        "motion_fingerprint": hashlib.sha256(Path(motion_file).read_bytes()).hexdigest(),
    }
    return append_glb_animation(target, solved, motion["fps"], root_name, report), report
