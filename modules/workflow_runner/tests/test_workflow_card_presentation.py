from dataclasses import FrozenInstanceError, fields
from pathlib import Path
from types import SimpleNamespace

import pytest

from modules.workflow_runner.services import registry as registry_module
from modules.workflow_runner.services.registry import (
    WorkflowCardPresentation,
    WorkflowCell,
    WorkflowHeroImage,
    WorkflowNode,
    WorkflowRegistry,
    WorkflowSequenceNode,
    WorkflowSequenceStage,
    WorkflowSubmissionPolicy,
)
from modules.workflow_runner.workflows import _WorkflowDefinitionWithProvenance


@pytest.fixture(autouse=True)
def ready_catalogue(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep this presentation contract independent of host model readiness."""

    monkeypatch.setattr(registry_module, "WorkflowReadinessScanner", lambda: object())
    monkeypatch.setattr(
        registry_module,
        "evaluate_workflow_readiness",
        lambda _definition, **_kwargs: {"status": "ready", "issues": []},
    )


def _card(*, hero: bool = True) -> WorkflowCardPresentation:
    return WorkflowCardPresentation(
        summary="A concise description of the visible result.",
        hero=(
            WorkflowHeroImage(
                asset="example/before-after.webp",
                alt="Before and after: the same subject with its background removed.",
            )
            if hero
            else None
        ),
    )


def _block(
    workflow_id: str = "example",
    *,
    card: WorkflowCardPresentation | None = None,
) -> WorkflowNode:
    return WorkflowNode(
        id=workflow_id,
        value="Example block",
        description="The complete workflow description remains separate.",
        inputs=(),
        outputs=(WorkflowCell(id="result", node_id="save", shape="masonry"),),
        configure_prompt=lambda _prompt, _inputs: None,
        configure_download=lambda _prompt, _inputs: None,
        workflow_path=Path("not-opened-by-this-test.json"),
        category="Tests",
        card=card,
    )


def _orchestra(
    *,
    card: WorkflowCardPresentation | None = None,
) -> WorkflowSequenceNode:
    return WorkflowSequenceNode(
        id="example_orchestra",
        value="Example orchestra",
        description="Compose two independently registered blocks.",
        inputs=(),
        stages=(
            WorkflowSequenceStage(id="first", workflow_id="first"),
            WorkflowSequenceStage(id="last", workflow_id="last"),
        ),
        final_output_ids=("result",),
        category="Tests",
        card=card,
    )


def _listed(registry: WorkflowRegistry, workflow_id: str) -> dict:
    return next(node for node in registry.list()["nodes"] if node["id"] == workflow_id)


def test_presentation_values_are_normalized_and_immutable() -> None:
    hero = WorkflowHeroImage("  example/result.webp  ", "  One\n visible result.  ")
    card = WorkflowCardPresentation("  Short\t useful summary.  ", hero)

    assert hero.asset == "example/result.webp"
    assert hero.alt == "One visible result."
    assert card.summary == "Short useful summary."
    assert card.hero is hero
    assert not hasattr(hero, "__dict__")
    assert not hasattr(card, "__dict__")
    with pytest.raises(FrozenInstanceError):
        hero.asset = "changed.webp"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        card.summary = "Changed"  # type: ignore[misc]


@pytest.mark.parametrize("extension", ("png", "jpg", "jpeg", "webp", "avif", "PNG"))
def test_hero_accepts_simple_relative_raster_keys(extension: str) -> None:
    asset = f"example-v2/result_01.{extension}"

    assert WorkflowHeroImage(asset, "An example result.").asset == asset


@pytest.mark.parametrize(
    "asset",
    (
        None,
        42,
        "",
        "   ",
        "/result.webp",
        "//example.test/result.webp",
        "https://example.test/result.webp",
        "file:///C:/result.webp",
        "C:/result.webp",
        "C:\\result.webp",
        "../result.webp",
        "example/../result.webp",
        "example/./result.webp",
        "example//result.webp",
        "example\\result.webp",
        "example./result.webp",
        ".hidden/result.webp",
        "example/result..webp",
        "example/result.webp?token=secret",
        "example/result.webp#fragment",
        "example%2fresult.webp",
        "%2e%2e/result.webp",
        "%252e%252e/result.webp",
        "example/result with spaces.webp",
        "example/result\x00.webp",
        "example/result\x1f.webp",
        "example/result.svg",
        "example/result.html",
        "example/result.gif",
        "example/result",
        "a" * 236 + ".webp",
    ),
)
def test_hero_rejects_external_ambiguous_or_non_raster_keys(asset: object) -> None:
    with pytest.raises(ValueError, match="hero asset must be a simple relative"):
        WorkflowHeroImage(asset, "An example result.")  # type: ignore[arg-type]


@pytest.mark.parametrize("alt", (None, "", "  ", "bad\x00alt", "bad\x7falt", "x" * 501))
def test_hero_requires_bounded_visible_alt_text(alt: object) -> None:
    with pytest.raises(ValueError, match="hero alt must contain 1 to 500"):
        WorkflowHeroImage("result.webp", alt)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "summary", (None, "", "  ", "bad\x00summary", "bad\x7fsummary", "x" * 181)
)
def test_card_requires_bounded_visible_summary(summary: object) -> None:
    with pytest.raises(ValueError, match="card summary must contain 1 to 180"):
        WorkflowCardPresentation(summary)  # type: ignore[arg-type]


@pytest.mark.parametrize("summary", ("Two\nlines.", "Two\rlines.", "Trailing\n", "Line\u2028break"))
def test_card_summary_rejects_line_breaks(summary: str) -> None:
    with pytest.raises(ValueError, match="card summary must not contain newlines"):
        WorkflowCardPresentation(summary)


def test_presentation_accepts_exact_text_length_limits() -> None:
    hero = WorkflowHeroImage("result.webp", "a" * 500)
    card = WorkflowCardPresentation("s" * 180, hero)

    assert len(card.summary) == 180
    assert len(hero.alt) == 500


def test_presentation_contract_rejects_untyped_values() -> None:
    with pytest.raises(TypeError, match="card hero must be a WorkflowHeroImage"):
        WorkflowCardPresentation("Summary", {"asset": "result.webp"})  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="card must be a WorkflowCardPresentation"):
        _block(card={"summary": "Summary"})  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="card must be a WorkflowCardPresentation"):
        _orchestra(card={"summary": "Summary"})  # type: ignore[arg-type]


def test_card_field_appends_to_every_existing_declaration_slot() -> None:
    assert [item.name for item in fields(WorkflowNode)] == [
        "id",
        "value",
        "description",
        "inputs",
        "outputs",
        "configure_prompt",
        "workflow_path",
        "category",
        "submission_policy",
        "origin",
        "collection",
        "configure_download",
        "required_model_assets",
        "input_option_requirements",
        "card",
    ]
    assert [item.name for item in fields(WorkflowSequenceNode)] == [
        "id",
        "value",
        "description",
        "inputs",
        "stages",
        "final_output_ids",
        "category",
        "origin",
        "collection",
        "card",
    ]
    policy = WorkflowSubmissionPolicy("legacy", 1, 1)
    configure = lambda _prompt, _inputs: None
    block = WorkflowNode(
        "legacy", "Legacy", "Legacy description", (), (), configure,
        Path("unused.json"), "Tests", policy, "custom", "Legacy collection",
        configure, (), (),
    )
    assert block.submission_policy is policy
    assert block.collection == "Legacy collection"
    assert block.configure_download is configure
    assert block.card is None
    orchestra = WorkflowSequenceNode(
        "legacy_orchestra", "Legacy orchestra", "Legacy description", (),
        _orchestra().stages, ("result",), "Tests", "custom", "Legacy collection",
    )
    assert orchestra.collection == "Legacy collection"
    assert orchestra.card is None


@pytest.mark.parametrize("with_hero", (False, True))
def test_catalogue_projects_only_explicit_card_display_fields(with_hero: bool) -> None:
    card = _card(hero=with_hero)
    workflow = _block(card=card)
    registry = WorkflowRegistry()
    registry.register(workflow, origin="shipped")

    listed = _listed(registry, workflow.id)
    expected = {"summary": card.summary}
    if with_hero:
        expected["hero"] = {
            "asset": "example/before-after.webp",
            "alt": "Before and after: the same subject with its background removed.",
        }
    assert listed["card"] == expected
    assert listed["description"] == workflow.description
    assert listed["readiness"] == {"status": "ready", "issues": []}
    listed["card"]["summary"] = "A client mutation"
    if with_hero:
        listed["card"]["hero"]["asset"] = "changed.webp"
    assert _listed(registry, workflow.id)["card"] == expected


def test_absent_or_unrecognized_legacy_card_keeps_the_original_wire_shape() -> None:
    registry = WorkflowRegistry()
    registry.register(_block())
    for workflow_id, extra in (("legacy", {}), ("legacy_card", {"card": "old extension data"})):
        registry.register(SimpleNamespace(
            id=workflow_id,
            value="Legacy",
            description="A structural legacy declaration.",
            category="Tests",
            cells_as_dict=lambda _direction: {},
            **extra,
        ))

    for listed in registry.list()["nodes"]:
        assert set(listed) == {
            "id", "value", "description", "category", "kind", "origin",
            "collection", "readiness", "children",
        }


def test_duck_typed_definition_can_opt_into_the_typed_card_contract() -> None:
    card = _card()
    registry = WorkflowRegistry()
    registry.register(SimpleNamespace(
        id="legacy",
        value="Legacy",
        description="A structural legacy declaration.",
        category="Tests",
        cells_as_dict=lambda _direction: {},
        card=card,
    ))

    assert _listed(registry, "legacy")["card"]["hero"]["asset"] == card.hero.asset


def test_custom_definition_override_does_not_inherit_shipped_card() -> None:
    registry = WorkflowRegistry()
    registry.register(_block(card=_card()), origin="shipped")
    registry.register(_block(), origin="custom")

    listed = _listed(registry, "example")
    assert listed["origin"] == "custom"
    assert "card" not in listed


@pytest.mark.parametrize(
    ("orchestra_origin", "first_origin", "expected_hero"),
    (
        ("shipped", "shipped", True),
        ("shipped", "custom", False),
        ("custom", "shipped", True),
        ("custom", "custom", True),
    ),
)
def test_orchestra_hero_tracks_trusted_resolved_block_provenance(
    orchestra_origin: str,
    first_origin: str,
    expected_hero: bool,
) -> None:
    card = _card()
    registry = WorkflowRegistry()
    first = _block("first")
    first.origin = "shipped"  # The mutable declaration cannot forge registry authority.
    registry.register(first, origin=first_origin)
    registry.register(_block("last"), origin="shipped")
    registry.register(_block("unrelated"), origin="custom")
    orchestra = _orchestra(card=card)
    wrapped = _WorkflowDefinitionWithProvenance(orchestra, orchestra_origin, "Tests")
    registry.register(wrapped, origin=orchestra_origin, collection="Tests")

    listed = _listed(registry, orchestra.id)
    assert listed["kind"] == "orchestra"
    assert listed["card"]["summary"] == card.summary
    assert ("hero" in listed["card"]) is expected_hero
    assert orchestra.card.hero is card.hero
    assert listed["readiness"] == {"status": "ready", "issues": []}


def test_later_custom_block_override_suppresses_only_the_orchestra_hero() -> None:
    registry = WorkflowRegistry()
    for workflow_id in ("first", "last"):
        registry.register(_block(workflow_id), origin="shipped")
    orchestra = _orchestra(card=_card())
    registry.register(orchestra, origin="shipped")
    assert "hero" in _listed(registry, orchestra.id)["card"]

    registry.register(_block("last", card=_card()), origin="custom")

    assert _listed(registry, orchestra.id)["card"] == {"summary": orchestra.card.summary}
    assert "hero" in _listed(registry, "last")["card"]


def test_orchestra_without_card_keeps_card_absent() -> None:
    registry = WorkflowRegistry()
    for workflow_id in ("first", "last"):
        registry.register(_block(workflow_id), origin="shipped")
    registry.register(_orchestra(), origin="shipped")

    assert "card" not in _listed(registry, "example_orchestra")


def test_catalogue_does_not_open_or_stat_hero_assets(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = WorkflowRegistry()
    registry.register(_block(card=_card()), origin="shipped")

    def unexpected_filesystem_access(*_args, **_kwargs):
        raise AssertionError("Card projection must not access the filesystem")

    with monkeypatch.context() as filesystem_guard:
        filesystem_guard.setattr(Path, "open", unexpected_filesystem_access)
        filesystem_guard.setattr(Path, "stat", unexpected_filesystem_access)
        listed = _listed(registry, "example")

    assert listed["card"]["hero"]["asset"] == "example/before-after.webp"
