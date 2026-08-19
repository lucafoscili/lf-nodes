from __future__ import annotations

from modules.workflow_runner.services.lifecycle import build_output_manifest


def manifest_for(output: dict) -> dict:
    return build_output_manifest(
        "submission-1",
        "prompt-1",
        {
            "body": {
                "payload": {
                    "preferred_output": "7",
                    "history": {"outputs": {"7": output}},
                }
            }
        },
    )


def test_normalizes_exact_lf_save_image_history_shape() -> None:
    manifest = manifest_for(
        {
            "lf_output": [
                {
                    "civitai_metadata": "",
                    "dataset": {
                        "nodes": [
                            {
                                "cells": {
                                    "lfSlot": {
                                        "shape": "slot",
                                        "value": "/view?filename=warden.png&type=output&subfolder=",
                                    }
                                }
                            }
                        ]
                    },
                    "file_names": ["warden.png"],
                }
            ]
        }
    )

    assert manifest["artifacts"] == [
        {
            "node_id": "7",
            "path": "lf_output[0].file_names[0]",
            "filename": "warden.png",
            "subfolder": "",
            "storage_type": "output",
            "media_type": "image/png",
        }
    ]


def test_preserves_file_order_and_normalizes_relative_subfolders() -> None:
    manifest = manifest_for(
        {
            "lf_output": [
                {
                    "file_names": [
                        "portraits/first.png",
                        "portraits/nested/second.webp",
                        "third.jpg",
                    ]
                }
            ]
        }
    )

    assert [artifact["filename"] for artifact in manifest["artifacts"]] == [
        "first.png",
        "second.webp",
        "third.jpg",
    ]
    assert [artifact["subfolder"] for artifact in manifest["artifacts"]] == [
        "portraits",
        "portraits/nested",
        "",
    ]
    assert [artifact["path"] for artifact in manifest["artifacts"]] == [
        "lf_output[0].file_names[0]",
        "lf_output[0].file_names[1]",
        "lf_output[0].file_names[2]",
    ]


def test_ignores_empty_malformed_and_unsafe_lf_file_names() -> None:
    manifest = manifest_for(
        {
            "lf_output": [
                {},
                {"file_names": None},
                {"file_names": "not-a-list.png"},
                {
                    "file_names": [
                        "",
                        None,
                        "../escape.png",
                        "/absolute.png",
                        "nested\\windows.png",
                        "C:drive.png",
                        "C:/drive.png",
                        "safe.png",
                    ]
                },
            ]
        }
    )

    assert [artifact["filename"] for artifact in manifest["artifacts"]] == ["safe.png"]


def test_deduplicates_standard_and_legacy_descriptors() -> None:
    manifest = manifest_for(
        {
            "images": [
                {
                    "filename": "warden.png",
                    "subfolder": "",
                    "type": "output",
                }
            ],
            "lf_output": [{"file_names": ["warden.png"]}],
        }
    )

    assert manifest["artifacts"] == [
        {
            "node_id": "7",
            "path": "images[0]",
            "filename": "warden.png",
            "subfolder": "",
            "storage_type": "output",
            "media_type": "image/png",
        }
    ]


def test_rejects_unsafe_standard_artifact_paths() -> None:
    manifest = manifest_for(
        {
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
            ]
        }
    )

    assert manifest["artifacts"] == []
