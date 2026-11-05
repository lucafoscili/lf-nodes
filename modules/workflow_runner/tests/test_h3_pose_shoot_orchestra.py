"""Pose Shoot executes real plans and block configuration with synthetic outputs.

Only child model execution is simulated. No queue, model, download or service is
started; artifact authority, materialization and graph configuration stay real.
"""

import json
from copy import deepcopy
from pathlib import Path

from PIL import Image
import pytest
import pytest_asyncio

from modules.workflow_runner.services import (
    job_store, lifecycle, registry, remix_inputs, sequence_runtime, sequence_store,
)
from modules.workflow_runner.workflows import orchestration


ORCHESTRA = orchestration.minimax_h3_pose_shoot
BLOCKS = {block.id: block for block in (
    orchestration.krea2_generate, orchestration.caption_image_vision,
    orchestration.h3_prompt_maker, orchestration.h3_prompt_video,
    orchestration.video_to_mocap,
)}
MOTION_OPTIONS = {
    "engine": "ExMR", "static_camera": False, "smoothing": False,
    "gpu_index": "2", "include_shape": True, "stage_timeout_seconds": "123.5",
}
EXPECTED_FRAMING = (
    "The camera sits on a tripod that never moves, zooms or pushes in. "
    "A full-length shot size for the whole clip: her bare feet stay a hand's width "
    "above the bottom edge of the frame and her head stays clear of the top, even "
    "when she raises her arms overhead, and her whole figure stays the same size "
    "in the frame from the first frame to the last; she never steps toward the "
    "edges of the frame."
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(autouse=True)
async def clear_sequences():
    await sequence_runtime.stop_sequence_supervisors()
    await sequence_store.reset_for_tests()
    yield
    await sequence_runtime.stop_sequence_supervisors()
    await sequence_store.reset_for_tests()


@pytest.fixture
def synthetic_files(tmp_path, monkeypatch):
    import folder_paths

    for storage in ("input", "output", "temp"):
        directory = tmp_path / storage
        directory.mkdir()
        monkeypatch.setattr(folder_paths, f"get_{storage}_directory", lambda directory=directory: str(directory))
    # The materializer consults catalogue declarations, not service readiness.
    monkeypatch.setattr(registry, "get_workflow", BLOCKS.get)
    files = {}
    for name, color in (("performer", "blue"), ("left_arm", "red"), ("right_leg", "green")):
        path = tmp_path / "input" / f"{name}.png"
        Image.new("RGB", (8, 12), color).save(path)
        files[name] = str(path)
    return tmp_path, files


def _output_node(workflow_id, output_id):
    return next(cell.node_id for cell in BLOCKS[workflow_id].outputs if cell.id == output_id)


def _plan(inputs):
    return sequence_runtime.normalize_sequence_definition(
        ORCHESTRA, inputs, workflow_resolver=BLOCKS.get,
        output_node_resolver=_output_node,
    )


def _result(outputs):
    return {"http_status": 200, "body": {"payload": {"history": {"outputs": outputs}}}}


class SyntheticChildren:
    """Replace the external model boundary while configuring every real block."""

    def __init__(self, root, *, fail_at=None):
        self.root = root
        self.fail_at = fail_at
        self.calls = []
        self.writer_texts = []
        self.caption_texts = []

    def artifact(self, filename, *, png=False):
        path = self.root / "output" / filename
        if png:
            Image.new("RGB", (8, 12), "purple").save(path)
        else:
            # Encoded model output is opaque to the orchestration. No decoder
            # runs here; these sentinel bytes test real file handoff only.
            path.write_bytes(b"synthetic model boundary output")
        return {"filename": filename, "subfolder": "", "type": "output"}

    async def __call__(self, payload, *, owner_id):
        effective = await remix_inputs.materialize_upload_references(payload, owner_id)
        block = BLOCKS[payload["workflowId"]]
        graph = block.load_prompt()
        block.configure_prompt(graph, effective["inputs"])
        self.calls.append({"payload": deepcopy(payload), "inputs": effective["inputs"], "graph": graph})
        run_id = f"synthetic-child-{len(self.calls)}"
        await job_store.create_job(
            run_id, block.id, owner_id=owner_id, inputs=effective["inputs"],
            submission_id=payload["submissionId"],
            request_fingerprint=lifecycle._fingerprint_payload(payload),
            comfy_url="http://unused.invalid:8188",
        )
        if len(self.calls) == self.fail_at:
            await job_store.set_job_status(run_id, job_store.JobStatus.FAILED, error="synthetic model failure")
        else:
            if block is orchestration.krea2_generate:
                outputs = {_output_node(block.id, "image"): {"images": [self.artifact("generated-performer.png", png=True)]}}
            elif block is orchestration.caption_image_vision:
                text = f"  Raise the left arm; bend the right knee. Pose {len(self.caption_texts) + 1}.\n"
                self.caption_texts.append(text)
                outputs = {_output_node(block.id, "string"): {"lf_output": [{"string": text}]}}
            elif block is orchestration.h3_prompt_maker:
                # Keep whitespace to prove suffixing happens after writing and
                # review without trimming or rewriting the model's text.
                text = f"  [Shot {len(self.writer_texts) + 1}]\nSlow transition, then hold.\t  "
                self.writer_texts.append(text)
                outputs = {_output_node(block.id, "prompt"): {"lf_output": [{"value": text}]}}
            elif block is orchestration.h3_prompt_video:
                outputs = {
                    _output_node(block.id, "video"): {"videos": [self.artifact(f"clip-{len(self.calls)}.mp4")]},
                    _output_node(block.id, "prompt"): {"lf_output": [{"string": effective["inputs"]["prompt"]}]},
                }
            else:
                assert block is orchestration.video_to_mocap
                preview = self.artifact(f"preview-{len(self.calls)}.mp4")["filename"]
                motion = self.artifact(f"motion-{len(self.calls)}.lf.json")["filename"]
                outputs = {
                    _output_node(block.id, "comparison"): {"lf_output": [{
                        "value": json.dumps({"video_file": preview}),
                        "json": {"video_file": preview}, "file_names": [preview],
                    }]},
                    _output_node(block.id, "motion"): {"lf_output": [{
                        "value": json.dumps({"motion_file": motion}),
                        "json": {"motion_file": motion}, "file_names": [motion],
                    }]},
                }
            await job_store.set_job_status(run_id, job_store.JobStatus.SUCCEEDED, result=_result(outputs))
        return {"run_id": run_id, "submission_id": payload["submissionId"]}

    def for_block(self, block):
        return [call for call in self.calls if call["payload"]["workflowId"] == block.id]


async def _execute(inputs, children):
    # Exercise explicit normalization as well as create's durable frozen plan.
    expected = _plan(inputs)
    created = await sequence_runtime.create_sequence_execution(
        ORCHESTRA, inputs, owner_id="pose-owner", parent_run_id="lf-sequence:pose-shoot",
        workflow_resolver=BLOCKS.get, output_node_resolver=_output_node,
    )
    assert created["definition_fingerprint"] == expected["definition_fingerprint"]
    return await sequence_runtime.drive_sequence_execution(
        created["parent_run_id"], child_runner=children, poll_interval=0,
    )


@pytest.mark.anyio
@pytest.mark.parametrize("source", ["words", "photos", "mixed"])
@pytest.mark.parametrize("supplied_performer", [False, True])
async def test_shoot_runs_real_graphs_with_one_identity_and_verbatim_framing(
    synthetic_files, source, supplied_performer,
):
    root, files = synthetic_files
    values = {"manage_model": False, "review": True, **MOTION_OPTIONS}
    if source in {"words", "mixed"}:
        values["poses"] = "Arms overhead\n\nBalance on left leg"
    if source in {"photos", "mixed"}:
        values["pose_photos"] = [files["left_arm"], files["right_leg"]]
    if supplied_performer:
        values.update(performer=files["performer"], performer_is_generated=True)
    children = SyntheticChildren(root)
    terminal = await _execute(values, children)
    assert terminal["status"] == "succeeded", terminal
    assert orchestration.POSE_SHOOT_FRAMING == EXPECTED_FRAMING
    assert "pending-orchestra-artifact" not in json.dumps(children.calls)
    assert "Pending text from an earlier orchestra stage" not in json.dumps(children.calls)
    count = 4 if source == "mixed" else 2
    generators = children.for_block(orchestration.krea2_generate)
    assert len(generators) == (0 if supplied_performer else 1)
    captions = children.for_block(orchestration.caption_image_vision)
    assert len(captions) == (0 if source == "words" else 2)
    assert [call["inputs"]["source_path"] for call in captions] == (
        [] if source == "words" else [files["left_arm"], files["right_leg"]]
    )
    writers = children.for_block(orchestration.h3_prompt_maker)
    renders = children.for_block(orchestration.h3_prompt_video)
    captures = children.for_block(orchestration.video_to_mocap)
    assert len(writers) == len(renders) == len(captures) == count
    if captions:
        assert [call["inputs"]["intent"] for call in writers[-2:]] == children.caption_texts
    performer_path = files["performer"] if supplied_performer else str(root / "output" / "generated-performer.png")
    expected_image = "performer.png [input]" if supplied_performer else "generated-performer.png [output]"
    for index, (writer, render, capture) in enumerate(zip(writers, renders, captures)):
        assert writer["inputs"]["picture_1"] == render["inputs"]["picture_1"] == performer_path
        assert writer["graph"]["picture_1"]["inputs"]["image"] == expected_image
        assert [key for key in writer["graph"] if key.startswith("picture_")] == ["picture_1"]
        graph = render["graph"]
        assert graph["source_1"]["inputs"]["image"] == expected_image
        assert [key for key in graph if key.startswith("source_")] == ["source_1"]
        exact = children.writer_texts[index] + "\n\n" + EXPECTED_FRAMING
        assert graph["h3"]["inputs"]["prompt"] == exact
        assert graph["display_prompt"]["inputs"]["string"] == exact
        assert exact.count(orchestration.POSE_SHOOT_FRAMING) == 1
        assert writer["graph"]["h3_prompt_maker"]["inputs"]["duration_seconds"] == 8.0
        assert graph["h3"]["inputs"]["length"] == 8 * 24
        assert render["inputs"]["duration"] == writer["inputs"]["duration"] == "8.0"
        assert render["inputs"]["aspect_ratio"] == "9:16"
        assert not any(photo in json.dumps(graph) for photo in (files["left_arm"], files["right_leg"]))
        options = capture["graph"]["extract_motion"]["inputs"]
        assert {name: options[name] for name in MOTION_OPTIONS} == {
            **MOTION_OPTIONS, "gpu_index": 2, "stage_timeout_seconds": 123.5,
        }
        video_path = Path(capture["inputs"]["video_path"])
        assert video_path.parent == root / "output" and video_path.is_file()
        assert options["video_path"] == str(video_path)
        assert capture["graph"]["render_motion"]["inputs"]["source_video"] == str(video_path)
        assert capture["graph"]["render_motion"]["inputs"]["motion_file"] == ["extract_motion", 0]
    # Ordinary history children retain every clip and every mocap/preview result.
    jobs = await job_store.list_jobs(owner_id="pose-owner")
    exposed = [job for job in jobs.values() if job.submission_id and job.submission_id.startswith("lfstage:")]
    assert len(exposed) == count * 2
    assert all(job.status == job_store.JobStatus.SUCCEEDED and job.result for job in exposed)
    assert all(not sequence_runtime.is_sequence_child_job(job) for job in exposed)
    private_submissions = [call["payload"]["submissionId"] for call in writers + captions + generators]
    assert all(sequence_runtime.is_sequence_child_submission_id(value) for value in private_submissions)


@pytest.mark.anyio
@pytest.mark.parametrize("failure_stage", ["write_prompt", "render_video", "capture_and_preview"])
async def test_failed_second_pose_names_stage_and_keeps_completed_clip_and_capture(synthetic_files, failure_stage):
    root, files = synthetic_files
    values = {"poses": "Arms overhead\nBalance", "performer": files["performer"],
              "performer_is_generated": True, "manage_model": False}
    fail_at = 4 + ("write_prompt", "render_video", "capture_and_preview").index(failure_stage)
    children = SyntheticChildren(root, fail_at=fail_at)
    terminal = await _execute(values, children)
    assert terminal["status"] == "failed"
    assert f"pose_2_Balance.{failure_stage}" in terminal["error"]
    assert "synthetic model failure" in terminal["error"]
    assert len(children.calls) == fail_at
    for stage in terminal["stages"][1:3]:
        assert stage["expose_in_history"] is True
        job = await job_store.get_job(stage["child_run_id"])
        assert job.status == job_store.JobStatus.SUCCEEDED
        assert job.submission_id.startswith("lfstage:")
        assert not sequence_runtime.is_sequence_child_job(job)
        artifacts = remix_inputs.project_public_output_artifacts(job.id, job.result)
        assert artifacts and all(artifact["available"] for artifact in artifacts)


@pytest.mark.parametrize("declaration", [None, False, "true", 1])
def test_supplied_performer_requires_explicit_generated_declaration(synthetic_files, declaration):
    _, files = synthetic_files
    with pytest.raises(ValueError, match="performer.*real-person"):
        _plan({"poses": "Hands raised", "performer": files["performer"],
               "performer_is_generated": declaration})


def test_pose_photo_cannot_be_reused_as_h3_performer(synthetic_files):
    _, files = synthetic_files
    with pytest.raises(ValueError, match="pose photo cannot also be Picture 1"):
        _plan({"pose_photos": [files["left_arm"]], "performer": files["left_arm"],
               "performer_is_generated": True})


@pytest.mark.parametrize("injected", ["picture_1", "picture_2", "mode", "prompt"])
def test_undeclared_h3_inputs_cannot_bypass_pose_shoot_contract(injected):
    with pytest.raises(ValueError, match="unknown port"):
        _plan({"poses": "Hands raised", injected: "untrusted.png"})


def test_one_generated_performer_and_at_least_one_pose_are_required(synthetic_files):
    _, files = synthetic_files
    with pytest.raises(ValueError, match="at least one pose"):
        _plan({"poses": "\n\t  "})
    with pytest.raises(ValueError, match="select one generated character"):
        _plan({"poses": "Hands raised", "performer": [files["performer"], files["left_arm"]],
               "performer_is_generated": True})


def test_duration_choices_are_the_renderer_presets_and_eight_seconds_is_default():
    public = next(cell for cell in ORCHESTRA.inputs if cell.id == "duration")
    renderer = next(cell for cell in orchestration.h3_prompt_video.inputs if cell.id == "duration")
    assert public.props["lfValue"] == "8.0"
    assert public.props["lfDataset"] == renderer.props["lfDataset"]


@pytest.mark.anyio
async def test_photo_description_failure_names_pose_and_keeps_previous_results(synthetic_files):
    root, files = synthetic_files
    children = SyntheticChildren(root, fail_at=4)
    terminal = await _execute({
        "poses": "Arms overhead", "pose_photos": [files["left_arm"]],
        "performer": files["performer"], "performer_is_generated": True,
        "manage_model": False,
    }, children)
    assert terminal["status"] == "failed"
    assert "pose_2_left_arm.describe_pose" in terminal["error"]
    for stage in terminal["stages"][1:3]:
        job = await job_store.get_job(stage["child_run_id"])
        assert not sequence_runtime.is_sequence_child_job(job)
        assert job.status == job_store.JobStatus.SUCCEEDED and job.result


@pytest.mark.parametrize("missing_generator", [False, True])
def test_catalogue_preflights_bound_outputs_and_keeps_optional_branches_runnable(
    synthetic_files, monkeypatch, missing_generator,
):
    from modules.workflow_runner.services.readiness import WorkflowReadinessScanner

    # Supply an installed environment through scanner boundaries; readiness and
    # portable graph configuration remain real, including the catalogue template.
    _, files = synthetic_files
    plan = _plan({"pose_photos": [files["left_arm"]], "manage_model": False})
    nodes, filenames = set(), set()
    for index, stage in enumerate(plan["stages"]):
        block = BLOCKS[stage["workflow_id"]]
        graph = block.load_prompt()
        block.configure_download(graph, sequence_runtime.sequence_stage_preflight_inputs(plan, index))
        for node in graph.values():
            nodes.add(node["class_type"])
            filenames.update(value for value in node["inputs"].values() if isinstance(value, str))
    nodes.add("LF_LocalChatCompletions")
    if missing_generator:
        nodes.remove("KSampler")
    scanner = WorkflowReadinessScanner(
        node_mapping_loader=lambda: dict.fromkeys(nodes),
        model_filename_loader=lambda _category: filenames,
        model_file_exists_loader=lambda _path: True,
    )
    monkeypatch.setattr(registry, "WorkflowReadinessScanner", lambda: scanner)
    catalogue = registry.WorkflowRegistry()
    for block in BLOCKS.values():
        catalogue.register(block)
    catalogue.register(ORCHESTRA)
    entry = next(item for item in catalogue.list()["nodes"] if item["id"] == ORCHESTRA.id)
    assert not any(issue["code"] == "workflow_configuration_invalid" for issue in entry["readiness"]["issues"])
    assert entry["readiness"]["status"] == ("warning" if missing_generator else "ready"), entry["readiness"]


@pytest.mark.parametrize("source", ["words", "photos"])
@pytest.mark.parametrize("supplied_performer", [False, True])
def test_every_expanded_stage_preflights_through_real_portable_graph_configuration(
    synthetic_files, source, supplied_performer,
):
    _, files = synthetic_files
    inputs = {"manage_model": False}
    if source == "words":
        inputs["poses"] = "Hands raised\nBalance on left leg"
    else:
        inputs["pose_photos"] = [files["left_arm"], files["right_leg"]]
    if supplied_performer:
        inputs.update(performer=files["performer"], performer_is_generated=True)
    plan = _plan(inputs)
    frozen = deepcopy(plan)
    for index, stage in enumerate(plan["stages"]):
        block = BLOCKS[stage["workflow_id"]]
        graph = block.load_prompt()
        portable = sequence_runtime.sequence_stage_preflight_inputs(plan, index)
        # Do not fill missing artifacts here: the runtime must make every real
        # expanded block preflightable before any child model has executed.
        block.configure_download(graph, portable)
        assert graph
    assert plan == frozen


def test_titanic_inventory_covers_expanded_lf_nodes_without_claiming_motion_execution(synthetic_files):
    _, files = synthetic_files
    plan = _plan({"pose_photos": [files["left_arm"]], "manage_model": False})
    classes = set()
    for index, stage in enumerate(plan["stages"]):
        block = BLOCKS[stage["workflow_id"]]
        inputs = sequence_runtime.sequence_stage_preflight_inputs(plan, index)
        graph = block.load_prompt()
        block.configure_download(graph, inputs)
        classes.update(node["class_type"] for node in graph.values())
    repository = Path(__file__).resolve().parents[3]
    fixture = json.loads((repository / "scripts/quality/fixtures/E2E.json").read_text(encoding="utf-8"))
    manifest = json.loads((repository / "scripts/quality/titanic_cases.json").read_text(encoding="utf-8"))
    inventory = {node["type"] for node in fixture["nodes"]}
    lf_classes = {name for name in classes if name.startswith("LF_")}
    assert {"LF_H3PromptMaker", "LF_LocalChatCompletions", "LF_VideoToMotion", "LF_MotionToVideo"} <= lf_classes
    assert lf_classes <= inventory
    disabled = {item["type"]: item for item in manifest["disabledNodes"]}
    for name, identifier in (("LF_VideoToMotion", 669), ("LF_MotionToVideo", 670)):
        assert disabled[name]["id"] == identifier
        assert "inventory only" in disabled[name]["reason"]
        assert next(node for node in fixture["nodes"] if node["id"] == identifier)["mode"] == 2
