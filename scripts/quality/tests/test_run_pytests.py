from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUNNER = ROOT / "scripts" / "quality" / "run_pytests.py"
PROBE = ROOT / "scripts" / "quality" / "fixtures" / "host_boundary_probe.py"


class IsolatedPytestRunnerTests(unittest.TestCase):
    def test_precollection_boundary_collects_helper_tests_without_gpu_abi_imports(
        self,
    ) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                "-I",
                str(RUNNER),
                "-q",
                "-p",
                "no:cacheprovider",
                str(PROBE),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        output = f"{completed.stdout}\n{completed.stderr}"
        self.assertEqual(completed.returncode, 0, output)
        self.assertIn("1 passed", output)
        self.assertNotIn("Windows fatal exception", output)
        self.assertNotIn("xformers", output.lower())
        self.assertNotIn("flash_attn", output.lower())


if __name__ == "__main__":
    unittest.main()
