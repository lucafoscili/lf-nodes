from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from modules.workflow_runner.services import job_store
from modules.workflow_runner.services.remix_inputs import (
    ARTIFACT_DESCRIPTOR_SCHEMA,
    ARTIFACT_REFERENCE_SCHEMA,
    UPLOAD_PREFILL_SCHEMA,
    UPLOAD_REFERENCE_SCHEMA,
    OutputArtifactReferenceError,
    UploadRemixReferenceError,
    build_durable_input_snapshot,
    materialize_upload_references,
    project_public_output_artifacts,
    project_public_remix_inputs,
    _artifact_id,
)


pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _ref(input_id: str = "image", run_id: str = "source-run") -> dict[str, str]:
    return {
        "schema": UPLOAD_REFERENCE_SCHEMA,
        "sourceRunId": run_id,
        "inputId": input_id,
    }


def _source(
    path_value,
    *,
    owner_id: str | None = "owner",
    workflow_id: str = "workflow",
):
    return SimpleNamespace(
        id="source-run",
        owner_id=owner_id,
        workflow_id=workflow_id,
        inputs={"image": path_value},
    )


def _artifact_ref(
    run_id: str = "source-output",
    artifact_id: str | None = None,
    filename: str = "candidate.png",
) -> dict:
    if artifact_id is None:
        artifact_id = _artifact_id(
            {
                "node_id": "42",
                "filename": filename,
                "subfolder": "handoff",
                "storage_type": "output",
            }
        )
    return {
        "schema": ARTIFACT_REFERENCE_SCHEMA,
        "sourceRunId": run_id,
        "artifactId": artifact_id,
        "filename": filename,
    }


def _artifact_result(filename: str = "candidate.png") -> dict:
    return {
        "http_status": 200,
        "body": {
            "payload": {
                "history": {
                    "outputs": {
                        "42": {
                            "images": [
                                {
                                    "filename": filename,
                                    "subfolder": "handoff",
                                    "type": "output",
                                }
                            ]
                        }
                    }
                }
            }
        },
    }


def _artifact_source(*, owner_id: str | None = "owner", status: str = "succeeded"):
    return SimpleNamespace(
        id="source-output",
        owner_id=owner_id,
        workflow_id="source-workflow",
        status=status,
        result=_artifact_result(),
        inputs={},
    )


def test_public_projection_exposes_only_basenames_and_opaque_authority(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    source = tmp_path / "private-root" / "reference.png"
    source.parent.mkdir()
    source.write_bytes(b"image")
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._upload_input_ids",
        lambda _workflow_id: {"image"},
    )
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._allowed_comfy_roots",
        lambda: (source.parent.resolve(),),
    )

    projected = project_public_remix_inputs(
        "source-run",
        "workflow",
        {"image": str(source), "prompt": "keep the lighting"},
    )

    assert projected == {
        "image": {
            "schema": UPLOAD_PREFILL_SCHEMA,
            "reference": _ref(),
            "names": ["reference.png"],
            "available": True,
        },
        "prompt": "keep the lighting",
    }
    encoded = json.dumps(projected)
    assert str(tmp_path) not in encoded
    assert "private-root" not in encoded


def test_public_projection_marks_expired_upload_without_leaking_its_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    missing = tmp_path / "temp" / "gone.png"
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._upload_input_ids",
        lambda _workflow_id: {"image"},
    )
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._allowed_comfy_roots",
        lambda: (missing.parent.resolve(),),
    )

    projected = project_public_remix_inputs(
        "source-run", "workflow", {"image": str(missing)}
    )

    assert projected["image"]["available"] is False
    assert projected["image"]["names"] == ["gone.png"]
    assert str(tmp_path) not in json.dumps(projected)


def test_durable_snapshot_resolves_portable_upload_without_public_host_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    input_root = tmp_path / "input"
    input_root.mkdir()
    source = input_root / "portrait.png"
    source.write_bytes(b"image")
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._upload_input_ids",
        lambda _workflow_id: {"image"},
    )
    monkeypatch.setattr(
        "modules.workflow_runner.workflows.utils._comfy_image_directories",
        lambda: (("input", input_root),),
    )
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._allowed_comfy_roots",
        lambda: (input_root.resolve(),),
    )

    snapshot = build_durable_input_snapshot(
        {
            "workflowId": "workflow",
            "inputs": {"image": "portrait.png [input]"},
        },
        {
            "workflowId": "workflow",
            "inputs": {"image": "portrait.png [input]"},
        },
    )
    assert snapshot == {"image": str(source.resolve())}

    projected = project_public_remix_inputs("run", "workflow", snapshot)
    assert projected["image"]["available"] is True
    assert projected["image"]["names"] == ["portrait.png"]
    assert str(tmp_path) not in json.dumps(projected)


def test_public_output_projection_is_bounded_opaque_and_reports_availability(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output = tmp_path / "output" / "handoff" / "candidate.png"
    output.parent.mkdir(parents=True)
    output.write_bytes(b"image")
    monkeypatch.setattr("folder_paths.get_output_directory", lambda: str(tmp_path / "output"))

    projected = project_public_output_artifacts("source-output", _artifact_result())

    assert projected == [
        {
            "schema": ARTIFACT_DESCRIPTOR_SCHEMA,
            "reference": _artifact_ref(),
            "filename": "candidate.png",
            "nodeId": "42",
            "available": True,
            "mediaType": "image/png",
        }
    ]
    encoded = json.dumps(projected)
    assert str(tmp_path) not in encoded
    assert "handoff" not in encoded


def test_artifact_identity_is_stable_across_manifest_order_and_path_changes() -> None:
    artifact = {
        "node_id": "42",
        "path": "images[0]",
        "filename": "candidate.png",
        "subfolder": "handoff",
        "storage_type": "output",
    }

    assert _artifact_id(artifact) == _artifact_id(
        {**artifact, "path": "nested.outputs.images[7]"}
    )
    assert _artifact_id(artifact) != _artifact_id(
        {**artifact, "filename": "different.png"}
    )


def test_public_projection_redacts_stale_upload_after_schema_drift(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    old_upload = tmp_path / "private-root" / "old-reference.png"
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._upload_input_ids",
        lambda _workflow_id: {"replacement_image"},
    )

    projected = project_public_remix_inputs(
        "source-run",
        "workflow",
        {
            "image": str(old_upload),
            "prompt": "keep the lighting",
        },
    )

    assert projected == {
        "image": "[omitted: server file reference]",
        "prompt": "keep the lighting",
    }
    assert str(tmp_path) not in json.dumps(projected)


async def test_materializes_owned_same_workflow_reference_and_preserves_batch_order(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root = tmp_path / "temp"
    root.mkdir()
    first = root / "first.png"
    second = root / "second.png"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    source = _source([str(first), str(second)])

    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._upload_input_ids",
        lambda _workflow_id: {"image"},
    )
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._allowed_comfy_roots",
        lambda: (root.resolve(),),
    )

    async def get_job(_run_id: str):
        return source

    monkeypatch.setattr(job_store, "get_job", get_job)

    effective = await materialize_upload_references(
        {
            "workflowId": "workflow",
            "inputs": {"image": _ref(), "prompt": "same composition"},
        },
        "owner",
    )

    assert effective["inputs"]["image"] == [str(first.resolve()), str(second.resolve())]
    assert effective["inputs"]["prompt"] == "same composition"


async def test_materializes_owned_successful_output_into_a_different_workflow(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    output = tmp_path / "output" / "handoff" / "candidate.png"
    output.parent.mkdir(parents=True)
    output.write_bytes(b"image")
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._upload_input_ids",
        lambda workflow_id: {"source_path"} if workflow_id == "target-workflow" else set(),
    )
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._upload_input_accept",
        lambda _workflow_id, _input_id: "image/*",
    )
    monkeypatch.setattr("folder_paths.get_output_directory", lambda: str(tmp_path / "output"))

    async def get_job(_run_id: str):
        return _artifact_source()

    monkeypatch.setattr(job_store, "get_job", get_job)

    effective = await materialize_upload_references(
        {
            "workflowId": "target-workflow",
            "inputs": {"source_path": _artifact_ref(), "prompt": "continue from this image"},
        },
        "owner",
    )

    assert effective["inputs"]["source_path"] == str(output.resolve())
    assert effective["inputs"]["prompt"] == "continue from this image"

    snapshot = build_durable_input_snapshot(
        {
            "workflowId": "target-workflow",
            "inputs": {"source_path": _artifact_ref(), "prompt": "continue from this image"},
        },
        effective,
    )
    assert snapshot["source_path"] == {
        "schema": UPLOAD_PREFILL_SCHEMA,
        "reference": _artifact_ref(),
        "names": ["candidate.png"],
        "available": True,
    }
    assert str(tmp_path) not in json.dumps(snapshot)

    projected = project_public_remix_inputs(
        "downstream-run",
        "target-workflow",
        snapshot,
    )
    assert projected["source_path"] == snapshot["source_path"]


@pytest.mark.parametrize(
    ("source", "reference", "accept", "expected_code"),
    [
        (_artifact_source(owner_id="someone-else"), _artifact_ref(), "image/*", "artifact_reference_unavailable"),
        (_artifact_source(status="running"), _artifact_ref(), "image/*", "artifact_reference_unavailable"),
        (_artifact_source(), _artifact_ref(artifact_id="0" * 64), "image/*", "artifact_reference_unavailable"),
        (_artifact_source(), {**_artifact_ref(), "path": "spoof"}, "image/*", "invalid_artifact_reference"),
        (
            _artifact_source(),
            _artifact_ref(
                artifact_id=_artifact_ref()["artifactId"],
                filename="spoof.png",
            ),
            "image/*",
            "invalid_artifact_reference",
        ),
        (_artifact_source(), _artifact_ref(), "video/*", "artifact_media_incompatible"),
    ],
)
async def test_rejects_unavailable_malformed_and_incompatible_output_references(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    source,
    reference: dict,
    accept: str,
    expected_code: str,
) -> None:
    output = tmp_path / "output" / "handoff" / "candidate.png"
    output.parent.mkdir(parents=True)
    output.write_bytes(b"image")
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._upload_input_ids",
        lambda _workflow_id: {"source_path"},
    )
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._upload_input_accept",
        lambda _workflow_id, _input_id: accept,
    )
    monkeypatch.setattr("folder_paths.get_output_directory", lambda: str(tmp_path / "output"))

    async def get_job(_run_id: str):
        return source

    monkeypatch.setattr(job_store, "get_job", get_job)

    with pytest.raises(OutputArtifactReferenceError) as error:
        await materialize_upload_references(
            {"workflowId": "target-workflow", "inputs": {"source_path": reference}},
            "owner",
        )
    assert error.value.error_code == expected_code
    assert str(tmp_path) not in str(error.value)


@pytest.mark.parametrize(
    ("source_overrides", "reference", "expected_code"),
    [
        ({"owner_id": "different"}, _ref(), "upload_reference_unavailable"),
        ({"workflow_id": "other"}, _ref(), "upload_reference_unavailable"),
        ({}, {**_ref(), "names": ["spoof.png"]}, "invalid_upload_reference"),
        ({}, _ref(input_id="other"), "invalid_upload_reference"),
    ],
)
async def test_rejects_cross_owner_workflow_and_malformed_references_without_detail(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    source_overrides: dict,
    reference: dict,
    expected_code: str,
) -> None:
    root = tmp_path / "temp"
    root.mkdir()
    image = root / "image.png"
    image.write_bytes(b"image")
    source = _source(str(image), **source_overrides)
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._upload_input_ids",
        lambda _workflow_id: {"image"},
    )
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._allowed_comfy_roots",
        lambda: (root.resolve(),),
    )

    async def get_job(_run_id: str):
        return source

    monkeypatch.setattr(job_store, "get_job", get_job)

    with pytest.raises(UploadRemixReferenceError) as error:
        await materialize_upload_references(
            {"workflowId": "workflow", "inputs": {"image": reference}},
            "owner",
        )
    assert error.value.error_code == expected_code
    assert error.value.input_name == "image"
    assert str(tmp_path) not in str(error.value)


async def test_rejects_reference_in_non_upload_field(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._upload_input_ids",
        lambda _workflow_id: {"image"},
    )
    with pytest.raises(UploadRemixReferenceError) as error:
        await materialize_upload_references(
            {"workflowId": "workflow", "inputs": {"prompt": _ref("prompt")}},
            "owner",
        )
    assert error.value.error_code == "invalid_upload_reference"
    assert error.value.input_name == "prompt"


async def test_rejects_missing_directory_and_outside_root_sources(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root = tmp_path / "temp"
    root.mkdir()
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"outside")
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._upload_input_ids",
        lambda _workflow_id: {"image"},
    )
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._allowed_comfy_roots",
        lambda: (root.resolve(),),
    )

    for value in (str(root / "missing.png"), str(root), str(outside)):
        async def get_job(_run_id: str, candidate=value):
            return _source(candidate)

        monkeypatch.setattr(job_store, "get_job", get_job)
        with pytest.raises(UploadRemixReferenceError) as error:
            await materialize_upload_references(
                {"workflowId": "workflow", "inputs": {"image": _ref()}},
                "owner",
            )
        assert error.value.error_code == "upload_reference_unavailable"


async def test_rejects_symlink_escape_when_supported(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root = tmp_path / "temp"
    root.mkdir()
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"outside")
    link = root / "link.png"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation is not available on this host")
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._upload_input_ids",
        lambda _workflow_id: {"image"},
    )
    monkeypatch.setattr(
        "modules.workflow_runner.services.remix_inputs._allowed_comfy_roots",
        lambda: (root.resolve(),),
    )

    async def get_job(_run_id: str):
        return _source(str(link))

    monkeypatch.setattr(job_store, "get_job", get_job)
    with pytest.raises(UploadRemixReferenceError):
        await materialize_upload_references(
            {"workflowId": "workflow", "inputs": {"image": _ref()}},
            "owner",
        )
