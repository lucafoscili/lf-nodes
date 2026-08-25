from enum import Enum
from types import SimpleNamespace

import pytest

from modules.workflow_runner.services import job_store, job_store_sqlite
from modules.workflow_runner.services.job_contracts import (
    job_status_value,
    validate_submission_identity,
)


VALID_FINGERPRINT = "a" * 64


def test_both_job_stores_use_the_canonical_submission_contract():
    assert job_store._validate_submission_identity is validate_submission_identity
    assert job_store_sqlite._validate_submission_identity is validate_submission_identity


@pytest.mark.parametrize(
    "identity",
    [
        (None, None, None),
        ("submission", VALID_FINGERPRINT, "http://127.0.0.1:8188"),
    ],
)
def test_submission_identity_accepts_absent_or_complete_values(identity):
    validate_submission_identity(*identity)


@pytest.mark.parametrize(
    ("identity", "message"),
    [
        (("submission", None, None), "supplied together"),
        (("x" * 129, VALID_FINGERPRINT, "http://localhost"), "submission_id"),
        (("submission", "A" * 64, "http://localhost"), "lowercase SHA-256"),
        (("submission", "a" * 63, "http://localhost"), "lowercase SHA-256"),
        (("submission", VALID_FINGERPRINT, "x" * 2049), "comfy_url"),
    ],
)
def test_submission_identity_rejects_partial_or_unbounded_values(identity, message):
    with pytest.raises(ValueError, match=message):
        validate_submission_identity(*identity)


class _Status(Enum):
    RUNNING = "running"


def test_job_status_value_normalizes_enum_and_string_statuses():
    assert job_status_value(SimpleNamespace(status=_Status.RUNNING)) == "running"
    assert job_status_value(SimpleNamespace(status="SUCCEEDED")) == "succeeded"
    assert job_status_value(SimpleNamespace()) == ""
