import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_recorded_node_count_matches_unique_published_mappings():
    from modules.workflow_runner.scripts.workflow_preflight import discover_lf_node_types

    recorded = json.loads((REPO_ROOT / "count.json").read_text(encoding="utf-8"))["nodes"]
    mappings = discover_lf_node_types()

    assert recorded == len(mappings) == 154


def test_canonical_titanic_covers_exactly_the_published_lf_node_types():
    from modules.workflow_runner.scripts.workflow_preflight import discover_lf_node_types

    workflow = json.loads(
        (REPO_ROOT / "scripts/quality/fixtures/E2E.json").read_text(encoding="utf-8")
    )
    fixture_types = {
        node["type"] for node in workflow["nodes"] if node["type"].startswith("LF_")
    }

    assert fixture_types == set(discover_lf_node_types())
