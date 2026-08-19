from __future__ import annotations

import logging
import os
import sys
from types import ModuleType, SimpleNamespace

helpers_module = ModuleType("modules.utils.helpers")
helpers_module.__path__ = []  # type: ignore[attr-defined]
conversion_module = ModuleType("modules.utils.helpers.conversion")
conversion_module.json_safe = lambda value: value  # type: ignore[attr-defined]
sys.modules.setdefault("modules.utils.helpers", helpers_module)
sys.modules.setdefault("modules.utils.helpers.conversion", conversion_module)

from modules.workflow_runner.services.registry import WorkflowRegistry
from modules.workflow_runner import config
from modules.workflow_runner import workflows


def _forget_external_modules(*module_names: str) -> None:
    for module_name in module_names:
        sys.modules.pop(f"{workflows.__name__}.custom.{module_name}", None)
    workflows._configure_custom_package_paths(())


def test_extra_roots_are_absolute_existing_directories(tmp_path, caplog) -> None:
    valid_root = tmp_path / "valid"
    valid_root.mkdir()
    ordinary_file = tmp_path / "workflow.py"
    ordinary_file.write_text("WORKFLOW = None\n", encoding="utf-8")

    with caplog.at_level(logging.WARNING):
        roots = workflows._resolve_extra_workflow_roots(
            [valid_root, valid_root, "relative/workflows", tmp_path / "missing", ordinary_file]
        )

    assert roots == (valid_root.resolve(),)
    assert "relative Workflow Runner root" in caplog.text
    assert "unavailable Workflow Runner root" in caplog.text
    assert "non-directory Workflow Runner root" in caplog.text


def test_extra_roots_are_read_from_runner_settings(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        config,
        "get_settings",
        lambda: SimpleNamespace(
            WORKFLOW_RUNNER_EXTRA_WORKFLOW_ROOTS=[str(tmp_path), str(tmp_path / "second")]
        ),
    )

    assert workflows._extra_workflow_roots_from_settings() == (
        str(tmp_path),
        str(tmp_path / "second"),
    )


def test_external_module_uses_existing_custom_package_contract(tmp_path) -> None:
    module_name = "lf_external_workflow_fixture"
    qualified_name = f"{workflows.__name__}.custom.{module_name}"
    (tmp_path / f"{module_name}.py").write_text(
        "from ..utils import resolve_upload_paths\n"
        "WORKFLOW = {'loader': resolve_upload_paths.__name__}\n",
        encoding="utf-8",
    )

    custom_package = workflows._configure_custom_package_paths([tmp_path])
    assert custom_package is not None
    try:
        loaded = workflows._import_workflow_module(f"custom.{module_name}")
        assert loaded.WORKFLOW == {"loader": "resolve_upload_paths"}
        assert os.fspath(tmp_path.resolve()) in custom_package.__path__
    finally:
        sys.modules.pop(qualified_name, None)
        workflows._configure_custom_package_paths(())


def test_iter_workflow_modules_discovers_external_module(monkeypatch, tmp_path) -> None:
    module_name = "lf_external_discovery_fixture"
    (tmp_path / f"{module_name}.py").write_text("WORKFLOW = {'source': 'external'}\n", encoding="utf-8")
    monkeypatch.setattr(workflows, "_WORKFLOW_MODULES", ())

    try:
        loaded = list(workflows.iter_workflow_modules([tmp_path]))
        fixture = next(module for module in loaded if module.__name__.endswith(module_name))
        assert fixture.WORKFLOW == {"source": "external"}
    finally:
        _forget_external_modules(module_name)


def test_broken_external_module_does_not_hide_valid_modules(monkeypatch, tmp_path, caplog) -> None:
    valid_name = "lf_external_valid_fixture"
    broken_name = "lf_external_broken_fixture"
    (tmp_path / f"{valid_name}.py").write_text("WORKFLOW = {'status': 'valid'}\n", encoding="utf-8")
    (tmp_path / f"{broken_name}.py").write_text("raise RuntimeError('broken fixture')\n", encoding="utf-8")
    monkeypatch.setattr(workflows, "_WORKFLOW_MODULES", ())

    try:
        with caplog.at_level(logging.ERROR):
            loaded = list(workflows.iter_workflow_modules([tmp_path]))
        assert any(module.__name__.endswith(valid_name) for module in loaded)
        assert f"custom.{broken_name}" in caplog.text
    finally:
        _forget_external_modules(valid_name, broken_name)


def test_first_root_wins_duplicate_module_filename(monkeypatch, tmp_path, caplog) -> None:
    module_name = "lf_external_duplicate_fixture"
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_root.mkdir()
    second_root.mkdir()
    (first_root / f"{module_name}.py").write_text("ORIGIN = 'first'\n", encoding="utf-8")
    (second_root / f"{module_name}.py").write_text("ORIGIN = 'second'\n", encoding="utf-8")
    monkeypatch.setattr(workflows, "_WORKFLOW_MODULES", ())

    try:
        with caplog.at_level(logging.WARNING):
            loaded = list(workflows.iter_workflow_modules([first_root, second_root]))
        fixture = next(module for module in loaded if module.__name__.endswith(module_name))
        assert fixture.ORIGIN == "first"
        assert "Ignoring duplicate Workflow Runner module" in caplog.text
    finally:
        _forget_external_modules(module_name)


def test_external_definition_can_be_registered(monkeypatch, tmp_path) -> None:
    module_name = "lf_external_definition_fixture"
    (tmp_path / f"{module_name}.py").write_text(
        "from types import SimpleNamespace\n"
        "WORKFLOW = SimpleNamespace(id='external-definition')\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(workflows, "_WORKFLOW_MODULES", ())

    try:
        definition = next(
            item
            for item in workflows.iter_workflow_definitions([tmp_path])
            if getattr(item, "id", None) == "external-definition"
        )
        registry = WorkflowRegistry()
        registry.register(definition)  # type: ignore[arg-type]
        assert registry.get("external-definition") is definition
    finally:
        _forget_external_modules(module_name)


def test_registry_logs_deterministic_last_registration(caplog) -> None:
    registry = WorkflowRegistry()
    first = SimpleNamespace(id="duplicate")
    replacement = SimpleNamespace(id="duplicate")

    registry.register(first)  # type: ignore[arg-type]
    with caplog.at_level(logging.WARNING):
        registry.register(replacement)  # type: ignore[arg-type]

    assert registry.get("duplicate") is replacement
    assert "replaces an existing registration" in caplog.text
