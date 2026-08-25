import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_publish_workflow_recovers_a_missing_release_from_an_existing_tag():
    workflow = (REPO_ROOT / ".github" / "workflows" / "publish.yml").read_text(
        encoding="utf-8"
    )

    assert 'git show-ref --verify --quiet "refs/tags/$TAG_NAME"' in workflow
    assert 'if [ "$TAG_SHA" != "$RELEASE_SHA" ]; then' in workflow
    assert "if: steps.check_tag.outputs.tag_exists == 'false'" in workflow
    assert "if: steps.check_release.outputs.release_exists == 'false'" in workflow
    assert workflow.index("- name: Check if GitHub Release Exists") < workflow.index(
        "- name: Generate Release Notes"
    )
    assert workflow.index("- name: Generate Release Notes") < workflow.index(
        "- name: Create GitHub Release"
    )
    assert '--output "$RUNNER_TEMP/github-release-notes.md"' in workflow
    assert "body_path: ${{ runner.temp }}/github-release-notes.md" in workflow
    assert workflow.count("github-release-notes.md") == 2


def test_recorded_node_count_matches_unique_published_mappings():
    from modules.workflow_runner.scripts.workflow_preflight import discover_lf_node_types

    recorded = json.loads((REPO_ROOT / "count.json").read_text(encoding="utf-8"))["nodes"]
    mappings = discover_lf_node_types()

    assert recorded == len(mappings) == 135
