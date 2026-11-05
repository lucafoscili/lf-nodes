"""Run only inside RGB MoCap's pinned runtime, never inside the Comfy host.

The application owns preparation, inference and export. This bridge only routes
their files and extracts native, flat-hand SMPL-X parameters into plain JSON.
"""

import json
import os
from pathlib import Path
import sys
import traceback

PREFIX = "@@LF_MOTION@@"


def emit(kind, **value):
    print(PREFIX + json.dumps(dict(type=kind, **value), ensure_ascii=False), flush=True)


def prepare_exmr_assets(job):
    """Prepare app-defined weight aliases under the output job, across drives."""
    import shutil
    from mocap import exmr_backend as backend
    from mocap.models import BY_KEY, ready
    assets = job / "runtime_data/cache/exmr/assets"
    for key, relative in backend.LINKS.items():
        model = BY_KEY[key]
        if not ready(model):
            raise RuntimeError(f"Prepare required RGB MoCap model {model.name}: {model.path}")
        target = assets / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        emit("progress", message="Prepare local ExMR asset: " + model.name)
        try:
            os.link(model.path, target)
        except OSError:
            shutil.copy2(model.path, target)
    # Suppress duplicate alias preparation: otherwise the app replaces copies
    # at every phase because a cross-drive copy cannot compare as samefile.
    backend.LINKS = {}


def prepare_export_parameters(project, include_shape):
    """Use a neutral derived export representation, retaining native inference.

    Motion Correction stamps this file and its result goes stale when the file is
    rewritten afterwards, so a representation that is already neutral is kept as is.
    """
    if include_shape:
        return
    import torch
    from mocap.engines import save_tensor
    source = project / "hmr4d_results.pt"
    parameters = torch.load(source, map_location="cpu", weights_only=False)
    spaces = ("smpl_params_global", "smpl_params_incam")
    if not any(torch.count_nonzero(parameters[space]["betas"]) for space in spaces):
        return
    for space in spaces:
        parameters[space]["betas"] = torch.zeros_like(parameters[space]["betas"])
    save_tensor(parameters, source)


def select_result(state, result):
    """Name the result the project's pipeline delivers; a corrected one runs with the app's own defaults."""
    state["pipeline"] = dict(model="exmr", result=result)
    if result.startswith("corrected_"):
        from mocap.correction_settings import correction_options
        state["correction"] = correction_options()
    return state


GROUND_LOGIT = 20.0  # a planted frame's static confidence logit: sigmoid 1 to float precision


def ground_capture(project, kind, request):
    """Prepare the export representation for a second correction, with motion_grounding's steps.

    The first correction's held feet steer the steps (the camera's drift taken out, the pelvis kept over the
    feet under a push-in, held heels set flat, planted seconds held), as they do on any target body; the app's
    solver then stands the prepared capture on the floor by the export body's own feet. Returns the steps.
    """
    import numpy as np
    import torch
    import smplx
    from scipy.spatial.transform import Rotation
    from mocap.correction import SoleGeometry
    from mocap.engines import save_tensor
    from mocap.mamma_body import body_path
    import motion_grounding as grounding
    source = project / "hmr4d_results.pt"
    record = torch.load(source, map_location="cpu", weights_only=False)
    params = record["smpl_params_global"]
    fps = float(json.loads((project / "project.json").read_text(encoding="utf-8")).get("fps", 30))
    body = smplx.SMPLX(str(body_path(project)), gender="neutral", num_pca_comps=12, flat_hand_mean=False,
                       batch_size=1).eval()
    geometry = SoleGeometry(body, params["betas"][0].numpy())
    array = lambda value: value.detach().cpu().double().numpy()
    raw = {key: array(params[key]) for key in ("global_orient", "body_pose", "transl")}
    n = len(raw["transl"])
    root, quat = grounding.arrays_from_params(raw, geometry.rest[0])
    logits = record["net_outputs"]["static_conf_logits"]
    probabilities = logits[0, :, :4].sigmoid().double().numpy()
    held = np.zeros((n, 2), bool)
    for foot, start, end, *_ in np.load(project / (kind + "_contacts.npz"))["segments"]:
        held[int(start):int(end), int(foot)] = True
    native = torch.load(project / "exmr_results.pt", map_location="cpu", weights_only=False, mmap=True)
    view = grounding.view_directions(array(native["smplx_incam"]["global_orient"]),
                                     array(native["smplx_global"]["global_orient"]))
    ready = grounding.prepare(geometry, root, quat, probabilities, held, fps, view,
                              planted=request["planted_seconds"], push_in=request["push_in"])
    pose = Rotation.from_quat(ready["quat"][..., [1, 2, 3, 0]].reshape(-1, 4)).as_rotvec().reshape(n, 22, 3)
    body_pose = params["body_pose"].clone()
    for joint in grounding.SOLVED_JOINTS:
        body_pose[:, 3 * (joint - 1):3 * joint] = torch.from_numpy(pose[:, joint]).to(body_pose.dtype)
    params["body_pose"] = body_pose
    params["transl"] = torch.from_numpy(ready["root"] - geometry.rest[0]).to(params["transl"].dtype)
    planted = grounding.planted_frames(request["planted_seconds"], fps, n)
    if planted.any():
        logits = logits.clone()
        logits[0, torch.from_numpy(planted), :4] = GROUND_LOGIT
        record["net_outputs"]["static_conf_logits"] = logits
    save_tensor(record, source)
    return dict(steps=ready["steps"], push_in=ready["push_in"], push_in_reading_m=ready["push_in_reading"])


FIELDS = ("global_orient", "transl", "body_pose", "left_hand_pose", "right_hand_pose")


def native_motion(native, joint_names, include_shape):
    """ExMR's native flat-hand SMPL-X parameters, world and camera, as LF motion."""
    motion = dict(schema="lf.motion.v1", fps=float(native["fps"]), joint_names=joint_names)
    for space, source in (("world", "smplx_global"), ("camera", "smplx_incam")):
        motion[space] = {key: native[source][key].detach().cpu().tolist() for key in FIELDS}
    if include_shape:
        motion["betas"] = native["smplx_global"]["betas"][:1].detach().cpu().tolist()
    return motion


def corrected_motion(native, corrected, joint_names, include_shape):
    """The app's corrected result as LF motion.

    Motion Correction replaces the legs and root translation of the world motion
    and keeps its root orientation. Fingers stay ExMR's native flat-hand pose (the
    corrected record holds them about the neutral body's hand mean). The camera
    space is the corrected world motion through ExMR's per-frame camera: its
    in-camera root orientation, its in-camera translation moved by the correction's
    root shift rotated into the camera, and the corrected (globally smoothed) pose.
    """
    import numpy as np
    from scipy.spatial.transform import Rotation
    world, camera = native["smplx_global"], native["smplx_incam"]
    array = lambda value: value.detach().cpu().double().numpy()
    orient, fixed = array(world["global_orient"]), array(corrected["global_orient"])
    if fixed.shape != orient.shape or not np.allclose(fixed, orient, atol=1e-5):
        raise RuntimeError("Motion Correction result does not match this ExMR capture; apply the correction again.")
    to_camera = Rotation.from_rotvec(array(camera["global_orient"])) * Rotation.from_rotvec(orient).inv()
    shift = array(corrected["transl"]) - array(world["transl"])
    body_pose = array(corrected["body_pose"])
    hands = {key: array(world[key]) for key in ("left_hand_pose", "right_hand_pose")}
    spaces = {
        "world": dict(global_orient=orient, transl=array(corrected["transl"]), body_pose=body_pose, **hands),
        "camera": dict(global_orient=array(camera["global_orient"]),
                       transl=array(camera["transl"]) + to_camera.apply(shift), body_pose=body_pose, **hands),
    }
    motion = dict(schema="lf.motion.v1", fps=float(native["fps"]), joint_names=joint_names)
    for space, values in spaces.items():
        motion[space] = {key: values[key].astype("float32").tolist() for key in FIELDS}
    if include_shape:
        motion["betas"] = native["smplx_global"]["betas"][:1].detach().cpu().tolist()
    return motion


def main():
    root, job = (Path(p).resolve() for p in sys.argv[1:3])
    action = sys.argv[3]
    request = json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))
    os.environ["RGB_MOCAP_DATA"] = str(job / "runtime_data")
    os.environ["RGB_MOCAP_MANAGED"] = "1"
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(root))
    # -I leaves the script's own folder off the path; motion_grounding lives beside this bridge.
    sys.path.insert(1, str(Path(__file__).resolve().parent))
    from mocap.runtime_registry import activate
    activate(root, "exmr" if action == "capture" else "shared")
    # Keep model assets and their registrations read-only at their installed home.
    from mocap import models
    models.MODELS = root / "models"
    from mocap import paths
    paths.MODELS = root / "models"
    if action == "prepare":
        from mocap.video import prepare
        project = prepare(Path(request["video_path"]), motion_tool="exmr", project=job / "project")
        from mocap.storage import atomic_json
        state = json.loads((project / "project.json").read_text(encoding="utf-8"))
        state["exmr_options"] = dict(static_camera=request["static_camera"],
                                     smoothing="global" if request["smoothing"] else "none")
        atomic_json(project / "project.json", select_result(state, request["result"]))
        return dict(project_dir=str(project))
    project = Path(request["project_dir"]).resolve()
    if not project.is_relative_to(job):
        raise ValueError("Motion project is outside its output directory.")
    stage_errors = []
    def observe(kind, **value):
        if kind in ("failed", "blocked") and value.get("message"):
            stage_errors.append(value["message"])
        emit(kind, **value)
    if action == "track":
        absent = models.missing("track")
        if absent:
            raise RuntimeError("Prepare required RGB MoCap models: " + ", ".join(model.name for model in absent))
        from mocap import worker
        worker.emit = observe
        sys.argv = ["mocap.worker", "track", "--project", str(project), "--result", "initial"]
        if worker.main():
            raise RuntimeError(stage_errors[-1] if stage_errors else "Actor tracking failed; check the visible full body and model readiness.")
        return dict(project_dir=str(project))
    if action == "capture":
        prepare_exmr_assets(job)
        from mocap.batch_worker import main as capture
        batch_path = job / "exmr_batch.json"
        batch_path.write_text(json.dumps(dict(version=1, root=str(job), phase="all",
            jobs=[dict(project=str(project), result="initial", force=False)])), encoding="utf-8")
        if capture(["exmr_batch", "--request", str(batch_path), "--project", str(project)], observe):
            raise RuntimeError(stage_errors[-1] if stage_errors else "ExMR reconstruction failed; inspect the preceding stage error.")
        import torch
        native = torch.load(project / "exmr_results.pt", map_location="cpu", weights_only=False, mmap=True)
        motion = native_motion(native, request["joint_names"], request["include_shape"])
        return dict(motion=motion, frame_count=len(motion["world"]["body_pose"]))
    if action == "correct":
        kind = request["result"]
        if not kind.startswith("corrected_"):
            raise ValueError("Motion Correction needs a corrected result, not " + kind)
        # The correction stamps the export representation it solves on: neutral it first.
        prepare_export_parameters(project, request["include_shape"])
        absent = models.missing("correct")
        if absent:
            raise RuntimeError("Prepare required RGB MoCap models: " + ", ".join(model.name for model in absent))
        from mocap import worker
        worker.emit = observe
        def correct():
            sys.argv = ["mocap.worker", "correct", "--project", str(project), "--result", kind]
            if worker.main():
                raise RuntimeError(stage_errors[-1] if stage_errors else "Motion Correction failed; inspect the preceding stage error.")
        correct()
        grounded = None
        if request["ground_feet"]:
            emit("progress", message="Ground the feet: the camera's drift, a push-in and heels set flat")
            grounded = ground_capture(project, kind, request)
            correct()
        import torch
        from mocap.motion_tools import RESULTS
        filename, key = RESULTS[kind]
        native = torch.load(project / "exmr_results.pt", map_location="cpu", weights_only=False, mmap=True)
        corrected = torch.load(project / filename, map_location="cpu", weights_only=False, mmap=True)[key]
        motion = corrected_motion(native, corrected, request["joint_names"], request["include_shape"])
        report = json.loads((project / (kind + "_correction.json")).read_text(encoding="utf-8"))
        correction = dict(result=kind, floor=report["floor"], warning=report["warning"],
                          options=report["options"], method=report["method"],
                          solved_on="estimated performer shape" if request["include_shape"] else "neutral shape",
                          grounded=grounded)
        return dict(motion=motion, frame_count=len(motion["world"]["body_pose"]), correction=correction)
    if action == "export":
        import shutil
        from mocap import engines
        kind = request["result"]
        prepare_export_parameters(project, request["include_shape"])
        # Route GVHMR's shared SMPL-X evaluator to job-local model aliases.
        # Its normal link_models helper writes into the application checkout.
        engines.activate("GVHMR")
        from hmr4d.utils import smplx_utils
        evaluator_root = job / "runtime_data/export"
        body_target = evaluator_root / "inputs/checkpoints/body_models/smplx/SMPLX_NEUTRAL.npz"
        body_target.parent.mkdir(parents=True, exist_ok=True)
        body_source = job / "runtime_data/cache/exmr/assets/body_models/smplx/SMPLX_NEUTRAL.npz"
        try:
            os.link(body_source, body_target)
        except OSError:
            shutil.copy2(body_source, body_target)
        smplx_utils.PROJ_ROOT = evaluator_root
        engines.link_models = lambda upstream: None
        from mocap.export import export_project
        bvh = export_project(project, kind)
        from mocap.motion_tools import selected_export
        source = selected_export(project, kind)
        if source is None:
            raise RuntimeError("RGB MoCap did not publish the selected export generation.")
        fbx = job / "motion.fbx"
        export_request = job / "fbx_request.json"
        export_request.write_text(json.dumps([dict(project=str(project), kind=kind, source=str(source),
            target=str(fbx), prepend_tpose=False)]), encoding="utf-8")
        from mocap.fbx_export import run
        run(export_request, emit)
        return dict(bvh_file=str(bvh), fbx_file=str(fbx))
    raise ValueError("Unsupported bridge action: " + action)


if __name__ == "__main__":
    try:
        emit("result", result=main())
    except Exception as error:
        traceback.print_exc()
        emit("failed", message=str(error))
        raise SystemExit(1)
