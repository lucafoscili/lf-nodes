from __future__ import annotations

import ast
import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_VERSION = "3.0.0"


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
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.MULTILINE)
    assert match is not None
    python_version = match.group(1)
    package_version = json.loads(
        (REPO_ROOT / "package.json").read_text(encoding="utf-8")
    )["version"]

    assert python_version == package_version == _runtime_version() == EXPECTED_VERSION


def test_current_version_has_a_user_facing_migration_note() -> None:
    note = REPO_ROOT / "docs" / "releases" / f"{EXPECTED_VERSION}.md"
    text = note.read_text(encoding="utf-8")

    assert "LF_ExtractPromptFromLoraTag" in text
    assert "Sockets 0" in text and "Sockets 2" in text
    assert "keywords_list" in text and "keywords_count_list" in text
