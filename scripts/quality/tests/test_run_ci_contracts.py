"""Static contract tests for the shared CPU CI gate."""

from __future__ import annotations

import importlib.util
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUNNER_PATH = ROOT / "scripts" / "quality" / "run_ci_contracts.py"
REQUIREMENTS_PATH = ROOT / "scripts" / "quality" / "requirements-ci-cpu.txt"
WORKFLOW_PATHS = (
    ROOT / ".github" / "workflows" / "nodes-count.yaml",
    ROOT / ".github" / "workflows" / "publish.yml",
)


def _load_runner():
    spec = importlib.util.spec_from_file_location("lf_run_ci_contracts", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load run_ci_contracts.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CpuContractGateTests(unittest.TestCase):
    def test_manifest_paths_exist_and_cover_each_high_risk_cohort(self) -> None:
        runner = _load_runner()

        all_tests = runner.all_behavior_tests()
        self.assertEqual(len(all_tests), len(set(all_tests)))
        self.assertTrue(
            all((ROOT / relative_path).is_file() for relative_path in all_tests)
        )

        manifest = "\n".join(all_tests)
        for required_fragment in (
            "normalization_contracts",
            "vae_list_contracts",
            "safe_send_sync_contract",
            "progressive_preview_event_contract",
            "durable_final_preview_history",
            "test_generated_preview",
            "test_inpaint_list_contract",
            "test_multimodal_payload_contract",
            "test_stability_schema",
            "test_extract_prompt_from_lora_tag_contract",
            "test_switch_tensor_contract",
            "test_save_dds",
            "test_save_json",
            "test_register_output_file",
            "test_visual_novel",
            "test_generate_release_notes",
            "test_release_metadata",
            "test_release_workflows",
        ):
            self.assertIn(required_fragment, manifest)

        commands = runner.build_commands("python-test")
        pytest_commands = commands[3:]
        pytest_command = pytest_commands[0]
        self.assertEqual(
            pytest_command[:4],
            (
                "python-test",
                "-I",
                str(runner.QUALITY_ROOT / "run_pytests.py"),
                "-q",
            ),
        )
        self.assertIn("scripts/quality/fixtures/host_boundary_probe.py", pytest_command)
        self.assertTrue(
            all(command[:4] == pytest_command[:4] for command in pytest_commands)
        )
        executed_tests = tuple(
            path
            for command in pytest_commands
            for path in command[4:]
        )
        self.assertEqual(executed_tests, all_tests)

    def test_cpu_requirements_are_exactly_pinned(self) -> None:
        requirements = [
            line.strip()
            for line in REQUIREMENTS_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith(("#", "--"))
        ]

        self.assertTrue(requirements)
        self.assertTrue(
            all(re.fullmatch(r"[A-Za-z0-9_.-]+==[^\s]+", item) for item in requirements)
        )
        self.assertIn("torch==2.7.0+cpu", requirements)
        self.assertIn("torchvision==0.22.0+cpu", requirements)
        self.assertIn("onnxruntime==1.22.0", requirements)
        self.assertIn("opencv-python-headless==4.8.0.76", requirements)
        self.assertNotIn("opencv-python==4.8.0.76", requirements)

    def test_release_workflows_reuse_the_same_cpu_gate(self) -> None:
        for workflow_path in WORKFLOW_PATHS:
            workflow = workflow_path.read_text(encoding="utf-8")
            with self.subTest(workflow=workflow_path.name):
                self.assertIn("actions/setup-python@v5", workflow)
                self.assertEqual(
                    workflow.count("scripts/quality/requirements-ci-cpu.txt"),
                    2,
                )
                self.assertEqual(
                    workflow.count("python -I scripts/quality/run_ci_contracts.py"),
                    1,
                )


if __name__ == "__main__":
    unittest.main()
