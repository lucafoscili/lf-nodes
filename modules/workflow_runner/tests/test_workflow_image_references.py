"""Filesystem contract for core Comfy ``LoadImage`` references."""

from __future__ import annotations

import hashlib
import sys
import types
from pathlib import Path

import pytest

# Registry needs only ``json_safe`` for these filesystem contract tests. Keep
# collection independent from optional image-processing dependencies.
helpers_module = types.ModuleType("modules.utils.helpers")
helpers_module.__path__ = []  # type: ignore[attr-defined]
conversion_module = types.ModuleType("modules.utils.helpers.conversion")
conversion_module.json_safe = lambda value: value
sys.modules.setdefault("modules.utils.helpers", helpers_module)
sys.modules.setdefault("modules.utils.helpers.conversion", conversion_module)

from modules.workflow_runner.services.registry import InputValidationError
from modules.workflow_runner.workflows import utils as workflow_utils
from modules.workflow_runner.workflows.utils import resolve_load_image_reference, resolve_upload_paths


@pytest.fixture
def comfy_image_directories(tmp_path, monkeypatch) -> dict[str, Path]:
    roots = {
        storage_type: tmp_path / "comfy" / storage_type
        for storage_type in ("input", "temp", "output")
    }
    for root in roots.values():
        root.mkdir(parents=True)
    monkeypatch.setattr(
        workflow_utils,
        "_comfy_image_directories",
        lambda: tuple(roots.items()),
    )
    return roots


@pytest.mark.parametrize("storage_type", ["input", "temp", "output"])
def test_existing_comfy_file_is_reused_with_an_annotated_relative_reference(
    comfy_image_directories, storage_type
) -> None:
    source = comfy_image_directories[storage_type] / "nested" / "portrait.png"
    source.parent.mkdir()
    source.write_bytes(b"portrait")

    reference = resolve_load_image_reference({"source_path": str(source)}, "source_path")

    assert reference == f"nested/portrait.png [{storage_type}]"
    assert not (
        comfy_image_directories["input"]
        / "lf-workflow-runner"
        / "staged-images"
    ).exists()


def test_portable_input_upload_reference_resolves_only_inside_comfy_input(
    comfy_image_directories,
) -> None:
    source = comfy_image_directories["input"] / "portrait.png"
    source.write_bytes(b"portrait")

    resolved = resolve_upload_paths(
        {"source_path": "portrait.png [input]"},
        "source_path",
    )

    assert resolved == [str(source.resolve())]


def test_portable_input_upload_reference_rejects_parent_traversal(
    tmp_path,
    comfy_image_directories,
) -> None:
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"outside")

    with pytest.raises(InputValidationError):
        resolve_upload_paths(
            {"source_path": "../../outside.png [input]"},
            "source_path",
        )


def test_external_image_is_content_addressed_and_atomically_staged_once(
    tmp_path, comfy_image_directories
) -> None:
    payload = b"stable source image bytes"
    source = tmp_path / "outside" / "Source.PNG"
    source.parent.mkdir()
    source.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    expected_relative = Path(
        "lf-workflow-runner", "staged-images", f"sha256-{digest}.png"
    )

    first_reference = resolve_load_image_reference(
        {"source_path": str(source)}, "source_path"
    )
    staged = comfy_image_directories["input"] / expected_relative
    first_mtime = staged.stat().st_mtime_ns
    second_reference = resolve_load_image_reference(
        {"source_path": str(source)}, "source_path"
    )

    assert first_reference == f"{expected_relative.as_posix()} [input]"
    assert second_reference == first_reference
    assert staged.read_bytes() == payload
    assert staged.stat().st_mtime_ns == first_mtime
    assert list(staged.parent.glob(".staging-*.tmp")) == []


def test_corrupt_existing_content_address_is_replaced_atomically(
    tmp_path, comfy_image_directories
) -> None:
    payload = b"authoritative bytes"
    source = tmp_path / "external.webp"
    source.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    staged = (
        comfy_image_directories["input"]
        / "lf-workflow-runner"
        / "staged-images"
        / f"sha256-{digest}.webp"
    )
    staged.parent.mkdir(parents=True)
    staged.write_bytes(b"corrupt")

    reference = resolve_load_image_reference(
        {"source_path": str(source)}, "source_path"
    )

    assert reference.endswith(f"sha256-{digest}.webp [input]")
    assert staged.read_bytes() == payload
    assert list(staged.parent.glob(".staging-*.tmp")) == []


def test_symlink_inside_comfy_root_is_not_misclassified_as_contained(
    tmp_path, comfy_image_directories
) -> None:
    external = tmp_path / "outside.jpg"
    external.write_bytes(b"outside")
    link = comfy_image_directories["input"] / "looks-local.jpg"
    try:
        link.symlink_to(external)
    except OSError as exc:
        pytest.skip(f"Symlinks unavailable on this host: {exc}")

    reference = resolve_load_image_reference(
        {"source_path": str(link)}, "source_path"
    )

    assert reference.startswith("lf-workflow-runner/staged-images/sha256-")
    assert reference.endswith(".jpg [input]")


@pytest.mark.parametrize(
    "value",
    [None, "", Path("relative.png")],
)
def test_missing_empty_or_relative_source_is_rejected(
    tmp_path, comfy_image_directories, monkeypatch, value
) -> None:
    if isinstance(value, Path):
        (tmp_path / value).write_bytes(b"relative")
        monkeypatch.chdir(tmp_path)

    with pytest.raises(InputValidationError):
        resolve_load_image_reference({"source_path": value}, "source_path")


def test_directory_source_is_rejected(tmp_path, comfy_image_directories) -> None:
    source = tmp_path / "not-an-image"
    source.mkdir()

    with pytest.raises(ValueError, match="not a file"):
        resolve_load_image_reference({"source_path": str(source)}, "source_path")


def test_multiple_sources_are_rejected_instead_of_using_only_the_first(
    tmp_path, comfy_image_directories
) -> None:
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    first.write_bytes(b"first")
    second.write_bytes(b"second")

    with pytest.raises(InputValidationError):
        resolve_load_image_reference(
            {"source_path": [str(first), str(second)]},
            "source_path",
        )
