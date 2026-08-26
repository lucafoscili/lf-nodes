import json

from modules.workflow_runner.services.job_store import Job, JobStatus
from modules.workflow_runner.utils.serialize import (
    build_output_preview,
    serialize_job,
    serialize_run_summary,
)


def _large_result(index: int) -> dict:
    return {
        "http_status": 200,
        "body": {
            "payload": {
                "history": {
                    "outputs": {
                        "save": {
                            "images": [
                                {
                                    "filename": f"portrait-{index}.png",
                                    "subfolder": "workflow-runner/history",
                                    "type": "output",
                                }
                            ]
                        },
                        "metadata": {
                            "lf_output": [{"metadata": "base64-sentinel-" + ("A" * 2_000_000)}]
                        },
                    }
                }
            }
        },
    }


def test_output_preview_keeps_audio_distinct_from_images() -> None:
    result = {
        "body": {
            "payload": {
                "history": {
                    "outputs": {
                        "save": {
                            "images": [
                                {"filename": "portrait.png", "subfolder": "", "type": "output"},
                                {"filename": "mix.wav", "subfolder": "", "type": "output"},
                            ]
                        }
                    }
                }
            }
        }
    }

    preview = build_output_preview(result)

    assert [item["filename"] for item in preview["save"]["images"]] == ["portrait.png"]
    assert [item["filename"] for item in preview["save"]["audios"]] == ["mix.wav"]


def test_output_preview_keeps_only_view_artifacts() -> None:
    preview = build_output_preview(_large_result(7))

    assert preview == {
        "save": {
            "images": [
                {
                    "filename": "portrait-7.png",
                    "subfolder": "workflow-runner/history",
                    "type": "output",
                    "url": "/view?filename=portrait-7.png&subfolder=workflow-runner%2Fhistory&type=output",
                }
            ]
        }
    }
    assert "base64-sentinel" not in json.dumps(preview)


def test_output_preview_projects_registered_lf_3d_file_names() -> None:
    result = {
        "body": {
            "payload": {
                "history": {
                    "outputs": {
                        "register": {
                            "lf_output": [
                                {
                                    "file_names": [
                                        "LF_Nodes/TRELLIS2/seed-42.glb",
                                        "LF_Nodes/TripoSplat/seed-42.spz",
                                        "../private.glb",
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        }
    }

    preview = build_output_preview(result)

    assert preview == {
        "register": {
            "3d": [
                {
                    "filename": "seed-42.glb",
                    "subfolder": "LF_Nodes/TRELLIS2",
                    "type": "output",
                    "url": (
                        "/view?filename=seed-42.glb&"
                        "subfolder=LF_Nodes%2FTRELLIS2&type=output"
                    ),
                },
                {
                    "filename": "seed-42.spz",
                    "subfolder": "LF_Nodes/TripoSplat",
                    "type": "output",
                    "url": (
                        "/view?filename=seed-42.spz&"
                        "subfolder=LF_Nodes%2FTripoSplat&type=output"
                    ),
                },
            ]
        }
    }


def test_output_preview_normalizes_windows_comfy_subfolders() -> None:
    result = _large_result(9)
    descriptor = result["body"]["payload"]["history"]["outputs"]["save"]["images"][0]
    descriptor["subfolder"] = "LF_Nodes\\Krea2\\CharacterRestage"

    preview = build_output_preview(result)

    assert preview["save"]["images"] == [
        {
            "filename": "portrait-9.png",
            "subfolder": "LF_Nodes/Krea2/CharacterRestage",
            "type": "output",
            "url": (
                "/view?filename=portrait-9.png&"
                "subfolder=LF_Nodes%2FKrea2%2FCharacterRestage&type=output"
            ),
        }
    ]


def test_output_preview_extracts_lf_dataset_view_url() -> None:
    result = {
        "body": {
            "payload": {
                "history": {
                    "outputs": {
                        "7": {
                            "lf_output": [
                                {
                                    "dataset": {
                                        "nodes": [
                                            {
                                                "cells": {
                                                    "lfImage": {
                                                        "shape": "image",
                                                        "lfValue": (
                                                            "/view?filename=sample.png&type=output"
                                                            "&subfolder=portraits&nonce=ignored"
                                                        ),
                                                    }
                                                }
                                            }
                                        ]
                                    },
                                    "metadata": "base64-sentinel-" + ("A" * 100_000),
                                }
                            ]
                        }
                    }
                }
            }
        }
    }

    preview = build_output_preview(result)

    assert preview == {
        "7": {
            "images": [
                {
                    "filename": "sample.png",
                    "subfolder": "portraits",
                    "type": "output",
                    "url": "/view?filename=sample.png&subfolder=portraits&type=output",
                }
            ]
        }
    }
    assert "base64-sentinel" not in json.dumps(preview)


def test_output_preview_rejects_unsafe_view_paths() -> None:
    result = {
        "body": {
            "payload": {
                "history": {
                    "outputs": {
                        "7": {
                            "images": [
                                {
                                    "filename": "../secret.png",
                                    "subfolder": "",
                                    "type": "output",
                                },
                                {
                                    "filename": "safe.png",
                                    "subfolder": "../private",
                                    "type": "output",
                                },
                            ],
                            "url": (
                                "/view?filename=secret.png&subfolder=..%2Fprivate"
                                "&type=output"
                            ),
                        }
                    }
                }
            }
        }
    }

    assert build_output_preview(result) == {}


def test_output_preview_rejects_windows_ads_control_and_overlong_paths() -> None:
    overlong_subfolder = "a" * 1025
    result = {
        "body": {
            "payload": {
                "history": {
                    "outputs": {
                        "7": {
                            "images": [
                                {"filename": "portrait:preview.png", "type": "output"},
                                {"filename": "portrait\n.png", "type": "output"},
                                {
                                    "filename": "portrait.png",
                                    "subfolder": overlong_subfolder,
                                    "type": "output",
                                },
                                {
                                    "filename": "safe.png",
                                    "subfolder": "LF_Nodes\\Krea2",
                                    "type": "output",
                                },
                            ]
                        }
                    }
                }
            }
        }
    }

    preview = build_output_preview(result)

    assert [item["filename"] for item in preview["7"]["images"]] == ["safe.png"]
    assert preview["7"]["images"][0]["subfolder"] == "LF_Nodes/Krea2"


def test_summary_serialization_does_not_publish_terminal_result() -> None:
    job = Job(id="run-7", workflow_id="portrait", status=JobStatus.SUCCEEDED)
    job.result = _large_result(7)

    summary = serialize_job(job, summary_only=True, include_output_preview=True)

    assert summary["result"] is None
    assert summary["outputs"]["save"]["images"][0]["url"].startswith("/view?")
    assert "base64-sentinel" not in json.dumps(summary)


def test_run_summary_accepts_status_mapping_without_echoing_result() -> None:
    summary = serialize_run_summary(
        {
            "run_id": "run-mapping",
            "workflow_id": "portrait",
            "status": "succeeded",
            "seq": 4,
            "error": "E" * 10_000,
            "result": _large_result(8),
        }
    )

    assert summary["id"] == "run-mapping:4"
    assert summary["outputs"]["save"]["images"][0]["filename"] == "portrait-8.png"
    assert len(summary["error"]) == 4096
    assert "result" not in summary
    assert "base64-sentinel" not in json.dumps(summary)


def test_history_payload_budget_for_200_runs() -> None:
    jobs = []
    for index in range(200):
        job = Job(
            id=f"run-{index}",
            workflow_id="portrait",
            status=JobStatus.SUCCEEDED,
            owner_id="owner",
            seq=2,
        )
        # One pathological result is enough to catch accidental result echoing;
        # the remaining jobs exercise the actual 200-card response budget.
        job.result = _large_result(index) if index == 0 else {
            "http_status": 200,
            "body": {
                "payload": {
                    "history": {
                        "outputs": {
                            "save": {
                                "images": [
                                    {
                                        "filename": f"portrait-{index}.png",
                                        "subfolder": "workflow-runner/history",
                                        "type": "output",
                                    }
                                ]
                            }
                        }
                    }
                }
            },
        }
        jobs.append(job)

    payload = {"runs": [serialize_run_summary(job) for job in jobs]}
    encoded = json.dumps(payload).encode("utf-8")
    assert len(payload["runs"]) == 200
    assert len(encoded) < 1_000_000
    assert all("result" not in run for run in payload["runs"])
    assert b"base64-sentinel" not in encoded
    assert payload["runs"][0]["outputs"]["save"]["images"][0]["url"].startswith(
        "/view?"
    )
