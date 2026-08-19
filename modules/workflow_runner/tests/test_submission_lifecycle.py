from __future__ import annotations

import json

import pytest

from modules.workflow_runner.services import lifecycle


pytestmark = pytest.mark.anyio


@pytest.fixture(autouse=True)
async def reset_lifecycle():
    await lifecycle.reset_for_tests()
    yield
    await lifecycle.reset_for_tests()


async def test_stable_submission_id_is_an_idempotent_request_handle():
    payload = {
        "workflowId": "remove_bg",
        "submissionId": "velora:portrait:maeva:front:v1",
        "inputs": {"image": "same-input"},
    }

    first, created = await lifecycle.reserve_submission(payload, "remove_bg")
    replay, replay_created = await lifecycle.reserve_submission(payload, "remove_bg")

    assert created is True
    assert replay_created is False
    assert first["submission_id"] == "velora:portrait:maeva:front:v1"
    assert replay["submission_id"] == first["submission_id"]
    assert replay["event_count"] == 1


async def test_stable_submission_id_rejects_a_different_request():
    base = {
        "workflowId": "remove_bg",
        "submissionId": "velora:portrait:maeva:front:v1",
        "inputs": {"image": "first"},
    }
    await lifecycle.reserve_submission(base, "remove_bg")

    with pytest.raises(lifecycle.SubmissionConflictError) as error:
        await lifecycle.reserve_submission(
            {**base, "inputs": {"image": "different"}},
            "remove_bg",
        )

    assert error.value.detail == "submission_id_conflict"


async def test_stable_submission_id_cannot_replay_across_owners():
    payload = {
        "workflowId": "portrait",
        "submissionId": "portrait-owner-bound",
        "inputs": {},
    }
    await lifecycle.reserve_submission(payload, "portrait", owner_id="owner-a")

    with pytest.raises(lifecycle.SubmissionConflictError) as error:
        await lifecycle.reserve_submission(payload, "portrait", owner_id="owner-b")

    assert error.value.detail == "submission_id_conflict"


async def test_events_and_output_manifest_cover_the_useful_lifecycle():
    payload = {
        "workflowId": "portrait",
        "submissionId": "portrait-001",
        "inputs": {},
    }
    await lifecycle.reserve_submission(payload, "portrait")
    await lifecycle.bind_prompt("portrait-001", "prompt-abc", "http://comfy:8188")
    await lifecycle.record_running("prompt-abc")
    await lifecycle.record_terminal(
        "prompt-abc",
        "succeeded",
        result={
            "http_status": 200,
            "body": {
                "payload": {
                    "preferred_output": "9",
                    "history": {
                        "outputs": {
                            "9": {
                                "images": [
                                    {
                                        "filename": "maeva.png",
                                        "subfolder": "velora",
                                        "type": "output",
                                    }
                                ],
                                "caption": ["Maeva"],
                            }
                        }
                    },
                }
            },
        },
    )

    snapshot = await lifecycle.get_submission("portrait-001")
    assert snapshot is not None
    assert snapshot["run_id"] == "prompt-abc"
    assert snapshot["status"] == "succeeded"
    assert [event["type"] for event in snapshot["events"]] == [
        "accepted",
        "submitted",
        "running",
        "succeeded",
    ]
    assert [event["seq"] for event in snapshot["events"]] == [1, 2, 3, 4]

    manifest = snapshot["output_manifest"]
    assert manifest["schema"] == lifecycle.MANIFEST_SCHEMA_VERSION
    assert manifest["preferred_output"] == "9"
    assert manifest["outputs"]["9"]["caption"] == ["Maeva"]
    assert manifest["outputs_truncated"] is False
    assert manifest["artifacts_truncated"] is False
    assert manifest["output_nodes_truncated"] is False
    assert manifest["traversal_truncated"] is False
    assert manifest["preferred_output_truncated"] is False
    assert manifest["manifest_truncated"] is False
    assert manifest["artifacts"] == [
        {
            "node_id": "9",
            "path": "images[0]",
            "filename": "maeva.png",
            "subfolder": "velora",
            "storage_type": "output",
            "media_type": "image/png",
        }
    ]


def test_output_manifest_bounds_large_metadata_without_losing_descriptors():
    result = {
        "body": {
            "payload": {
                "history": {
                    "outputs": {
                        "9": {
                            "images": [
                                {
                                    "filename": "maeva.png",
                                    "subfolder": "velora",
                                    "type": "output",
                                }
                            ],
                            "metadata": "x" * (2 * 1024 * 1024),
                        }
                    }
                }
            }
        }
    }

    manifest = lifecycle.build_output_manifest("submission-1", "prompt-1", result)

    assert manifest["outputs_truncated"] is True
    assert manifest["manifest_truncated"] is True
    assert manifest["outputs"]["_truncated"] is True
    assert manifest["artifacts"][0]["filename"] == "maeva.png"
    assert len(json.dumps(manifest).encode("utf-8")) < 300_000


def test_output_manifest_bounds_large_artifact_collections_and_identifiers():
    descriptor_count = 10_000
    result = {
        "body": {
            "payload": {
                "preferred_output": "preferred-" + ("x" * 10_000),
                "history": {
                    "outputs": {
                        "9": {
                            "images": [
                                {
                                    "filename": f"candidate-{index}.png",
                                    "subfolder": "velora/candidates",
                                    "type": "output",
                                }
                                for index in range(descriptor_count)
                            ]
                        },
                        **{
                            f"node-{index}": {"value": index}
                            for index in range(1_000)
                        },
                    }
                },
            }
        }
    }

    manifest = lifecycle.build_output_manifest("submission-1", "prompt-1", result)
    serialized_size = len(json.dumps(manifest).encode("utf-8"))

    assert 0 < len(manifest["artifacts"]) <= lifecycle._MAX_ARTIFACTS
    assert len(manifest["output_nodes"]) <= lifecycle._MAX_OUTPUT_NODES
    assert manifest["preferred_output"] is None
    assert manifest["artifacts_truncated"] is True
    assert manifest["output_nodes_truncated"] is True
    assert manifest["preferred_output_truncated"] is True
    assert manifest["outputs_truncated"] is True
    assert manifest["manifest_truncated"] is True
    assert serialized_size <= 512 * 1024


@pytest.mark.parametrize("node_output", [list(range(5_000)), None])
def test_output_manifest_bounds_artifact_discovery_traversal(node_output):
    if node_output is None:
        node_output = {"leaf": "value"}
        for _ in range(lifecycle._MAX_MANIFEST_TRAVERSAL_DEPTH + 2):
            node_output = {"nested": node_output}

    result = {
        "body": {
            "payload": {
                "history": {
                    "outputs": {"9": node_output},
                }
            }
        }
    }

    manifest = lifecycle.build_output_manifest("submission-1", "prompt-1", result)

    assert manifest["traversal_truncated"] is True
    assert manifest["manifest_truncated"] is True
    assert len(json.dumps(manifest).encode("utf-8")) <= 512 * 1024


async def test_cancel_request_is_additive_and_idempotent():
    payload = {
        "workflowId": "portrait",
        "submissionId": "portrait-cancel",
        "inputs": {},
    }
    await lifecycle.reserve_submission(payload, "portrait")
    await lifecycle.bind_prompt("portrait-cancel", "prompt-cancel", "http://comfy:8188")
    await lifecycle.record_running("prompt-cancel")

    first = await lifecycle.record_cancel_requested("portrait-cancel")
    second = await lifecycle.record_cancel_requested("portrait-cancel")

    assert first["cancel_requested"] is True
    assert second["event_count"] == first["event_count"]
    events = await lifecycle.get_submission("portrait-cancel")
    assert events is not None
    assert events["events"][-1]["type"] == "cancel_requested"


async def test_invalid_or_conflicting_submission_id_shapes_are_rejected():
    with pytest.raises(lifecycle.SubmissionLifecycleError) as invalid:
        await lifecycle.reserve_submission(
            {"workflowId": "x", "submissionId": "has spaces", "inputs": {}},
            "x",
        )
    assert invalid.value.detail == "invalid_submission_id"

    with pytest.raises(lifecycle.SubmissionLifecycleError) as conflicting:
        await lifecycle.reserve_submission(
            {
                "workflowId": "x",
                "submissionId": "one",
                "submission_id": "two",
                "inputs": {},
            },
            "x",
        )
    assert conflicting.value.detail == "conflicting_submission_id"
