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
    """Use a neutral derived export representation, retaining native inference."""
    if include_shape:
        return
    import torch
    from mocap.engines import save_tensor
    source = project / "hmr4d_results.pt"
    parameters = torch.load(source, map_location="cpu", weights_only=False)
    for space in ("smpl_params_global", "smpl_params_incam"):
        parameters[space]["betas"] = torch.zeros_like(parameters[space]["betas"])
    save_tensor(parameters, source)


def main():
    root, job = (Path(p).resolve() for p in sys.argv[1:3])
    action = sys.argv[3]
    request = json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))
    os.environ["RGB_MOCAP_DATA"] = str(job / "runtime_data")
    os.environ["RGB_MOCAP_MANAGED"] = "1"
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(root))
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
        state["pipeline"] = dict(model="exmr", result="initial")
        atomic_json(project / "project.json", state)
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
        fields = ("global_orient", "transl", "body_pose", "left_hand_pose", "right_hand_pose")
        motion = dict(schema="lf.motion.v1", fps=float(native["fps"]), joint_names=request["joint_names"])
        for space, source in (("world", "smplx_global"), ("camera", "smplx_incam")):
            motion[space] = {key: native[source][key].detach().cpu().tolist() for key in fields}
        if request["include_shape"]:
            motion["betas"] = native["smplx_global"]["betas"][:1].detach().cpu().tolist()
        return dict(motion=motion, frame_count=len(motion["world"]["body_pose"]))
    if action == "export":
        import shutil
        from mocap import engines
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
        bvh = export_project(project, "initial")
        from mocap.motion_tools import selected_export
        source = selected_export(project, "initial")
        if source is None:
            raise RuntimeError("RGB MoCap did not publish the selected export generation.")
        fbx = job / "motion.fbx"
        export_request = job / "fbx_request.json"
        export_request.write_text(json.dumps([dict(project=str(project), kind="initial", source=str(source),
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
