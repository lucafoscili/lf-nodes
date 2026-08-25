"""Dependency-free contracts shared by Workflow Runner job stores."""

from __future__ import annotations

from typing import Any, Optional


def validate_submission_identity(
    submission_id: Optional[str],
    request_fingerprint: Optional[str],
    comfy_url: Optional[str],
) -> None:
    """Reject partial or unbounded durable lifecycle authority."""

    values = (submission_id, request_fingerprint, comfy_url)
    if all(value is None for value in values):
        return
    if not all(isinstance(value, str) and value for value in values):
        raise ValueError("submission identity fields must be supplied together")
    assert submission_id is not None
    assert request_fingerprint is not None
    assert comfy_url is not None
    if len(submission_id) > 128:
        raise ValueError("submission_id exceeds 128 characters")
    if (
        len(request_fingerprint) != 64
        or any(character not in "0123456789abcdef" for character in request_fingerprint)
    ):
        raise ValueError("request_fingerprint must be a lowercase SHA-256 hex digest")
    if len(comfy_url) > 2048:
        raise ValueError("comfy_url exceeds 2048 characters")


def job_status_value(job: Any) -> str:
    """Return a normalized status string from enum- or string-backed jobs."""

    value = getattr(job, "status", "")
    return str(getattr(value, "value", value) or "").lower()


__all__ = ["job_status_value", "validate_submission_identity"]
