import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATHS = (
    REPO_ROOT / ".github" / "workflows" / "nodes-count.yaml",
    REPO_ROOT / ".github" / "workflows" / "publish.yml",
)


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

    assert recorded == len(mappings) == 138


def test_release_workflows_enforce_the_shared_frontend_gate():
    package = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    assert package["scripts"]["check:release"] == (
        "yarn test && yarn test:titanic:unit && yarn test:examples:unit && "
        "yarn sanitize:examples --check && yarn build"
    )
    assert package["scripts"]["sanitize:examples"] == (
        "tsx scripts/quality/sanitize_example_workflows.mts"
    )
    assert package["scripts"]["test:examples:unit"] == (
        "vitest run scripts/quality/tests/sanitize_example_workflows.test.ts"
    )

    for workflow_path in WORKFLOW_PATHS:
        workflow = workflow_path.read_text(encoding="utf-8")
        assert "actions/setup-node@v4" in workflow
        assert "corepack enable" in workflow
        assert "corepack yarn install --immutable" in workflow
        assert workflow.count("corepack yarn check:release") == 1
        assert workflow.index("corepack yarn install --immutable") < workflow.index(
            "corepack yarn check:release"
        )


def test_release_regressions_are_part_of_the_cpu_publication_gate():
    gate = (REPO_ROOT / "scripts" / "quality" / "run_ci_contracts.py").read_text(
        encoding="utf-8"
    )

    for test_path in (
        "modules/tests/test_generate_release_notes.py",
        "modules/tests/test_release_metadata.py",
        "modules/tests/test_release_workflows.py",
    ):
        assert test_path in gate
