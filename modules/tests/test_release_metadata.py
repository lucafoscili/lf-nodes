from __future__ import annotations

import ast
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _pyproject_version() -> str:
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.MULTILINE)
    assert match is not None
    return match.group(1)


EXPECTED_VERSION = _pyproject_version()


def _runtime_version() -> str:
    module = ast.parse((REPO_ROOT / "__init__.py").read_text(encoding="utf-8"))
    for statement in module.body:
        if not isinstance(statement, ast.Assign):
            continue
        if any(
            isinstance(target, ast.Name) and target.id == "VERSION"
            for target in statement.targets
        ):
            return ast.literal_eval(statement.value)
    raise AssertionError("__init__.py does not declare VERSION")


def test_release_versions_are_coherent() -> None:
    package_version = json.loads(
        (REPO_ROOT / "package.json").read_text(encoding="utf-8")
    )["version"]

    assert package_version == _runtime_version() == EXPECTED_VERSION


def test_current_release_note_links_work_in_copied_github_body() -> None:
    note = REPO_ROOT / "docs" / "releases" / f"{EXPECTED_VERSION}.md"
    text = note.read_text(encoding="utf-8")
    links = re.findall(r"\]\(([^)]+)\)", text)
    prefix = f"https://github.com/lucafoscili/lf-nodes/blob/v{EXPECTED_VERSION}/"

    assert links
    for link in links:
        assert link.startswith(prefix), f"Release link must pin its repository/tag: {link}"
        target = link.removeprefix(prefix).split("#", 1)[0]
        assert (REPO_ROOT / target).is_file(), f"Missing release link target: {target}"


def test_audio_encoder_dependency_is_declared_for_both_install_paths() -> None:
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    requirements = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8")

    assert '"av>=17.0.0"' in pyproject
    assert "av>=17.0.0" in requirements.splitlines()
