"""Standalone tests for scripts/quality/check_node_contracts.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


CHECKER = Path(__file__).resolve().parents[1] / "check_node_contracts.py"


class CheckerFixture:
    def __init__(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self._temporary_directory.name)
        self.nodes = self.root / "modules" / "nodes"
        self.nodes.mkdir(parents=True)

    def close(self) -> None:
        self._temporary_directory.cleanup()

    def write(self, relative_path: str, source: str, *, bom: bool = False) -> None:
        destination = self.nodes / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        encoding = "utf-8-sig" if bom else "utf-8"
        destination.write_text(textwrap.dedent(source).lstrip(), encoding=encoding)

    def run(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(self.root)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )


class NodeContractCheckerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = CheckerFixture()

    def tearDown(self) -> None:
        self.fixture.close()

    def test_valid_contract_passes_without_importing_fixture(self) -> None:
        self.fixture.write(
            "group/good.py",
            """
            raise RuntimeError("this fixture must never be imported")

            class GoodNode:
                RETURN_TYPES = (Types.STRING, Types.INTEGER)
                RETURN_NAMES = ("text", "count")
                OUTPUT_TOOLTIPS = ("Text", "Count")
                OUTPUT_IS_LIST = (False, True)
                INPUT_IS_LIST = False

                def on_exec(self, choose=False):
                    def helper():
                        return ("nested helper arity is irrelevant",)
                    if choose:
                        return ("text", 1)
                    if unknown_condition():
                        return unresolved_result
                    return {"ui": {}, "result": ("text", 1)}

            NODE_CLASS_MAPPINGS = {"Good": GoodNode}
            NODE_DISPLAY_NAME_MAPPINGS = {"Good": "Good node"}
            """,
            bom=True,
        )

        completed = self.fixture.run()

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(
            completed.stdout,
            "PASS: 1 public mapping(s) checked across 1 Python file(s).\n",
        )
        self.assertEqual(completed.stderr, "")

    def test_mapping_defects_are_reported_and_sorted(self) -> None:
        self.fixture.write(
            "z_second.py",
            """
            class Second:
                RETURN_TYPES = ()

            NODE_CLASS_MAPPINGS = {
                "Shared": Second,
                "MissingClass": NotDefinedHere,
            }
            NODE_DISPLAY_NAME_MAPPINGS = {
                "Shared": "Second",
                "OrphanDisplay": "Orphan",
            }
            """,
        )
        self.fixture.write(
            "a_first.py",
            """
            class First:
                RETURN_TYPES = ()

            NODE_CLASS_MAPPINGS = {"Shared": First}
            NODE_DISPLAY_NAME_MAPPINGS = {"Shared": "First"}
            """,
        )

        first = self.fixture.run()
        second = self.fixture.run()

        self.assertEqual(first.returncode, 1)
        self.assertEqual(first.stdout, second.stdout)
        self.assertIn("DUPLICATE_PUBLIC_KEY", first.stdout)
        self.assertIn("MAPPED_CLASS_NOT_LOCAL", first.stdout)
        self.assertIn("DISPLAY_KEY_MISSING", first.stdout)
        self.assertIn("DISPLAY_KEY_EXTRA", first.stdout)
        finding_lines = first.stdout.splitlines()[:-1]

        def finding_sort_key(line: str) -> tuple[str, int, int, str]:
            path, line_number, column, detail = line.split(":", 3)
            return path, int(line_number), int(column), detail

        self.assertEqual(finding_lines, sorted(finding_lines, key=finding_sort_key))

    def test_class_return_and_direct_send_defects_are_reported(self) -> None:
        self.fixture.write(
            "broken.py",
            """
            class BrokenNode:
                RETURN_TYPES = (Types.STRING, Types.INTEGER)
                RETURN_NAMES = ("only_one",)
                OUTPUT_TOOLTIPS = ("one", "two", "three")
                OUTPUT_IS_LIST = (False, "not a bool")
                INPUT_IS_LIST = (True,)

                def on_exec(self, use_dict=False):
                    def helper():
                        return (1, 2, 3, 4, 5)
                    if use_dict:
                        return {"result": (1, 2, 3)}
                    return (1,)

            NODE_CLASS_MAPPINGS = {"Broken": BrokenNode}
            NODE_DISPLAY_NAME_MAPPINGS = {"Broken": "Broken"}
            PromptServer.instance.send_sync("event", {})
            """,
        )

        completed = self.fixture.run()

        self.assertEqual(completed.returncode, 1)
        self.assertEqual(completed.stdout.count("ATTRIBUTE_ARITY"), 2)
        self.assertEqual(completed.stdout.count("RETURN_ARITY"), 2)
        self.assertEqual(completed.stdout.count("OUTPUT_IS_LIST_NON_BOOL"), 1)
        self.assertEqual(completed.stdout.count("INPUT_IS_LIST_NOT_BOOL"), 1)
        self.assertEqual(completed.stdout.count("DIRECT_SEND_SYNC"), 1)
        self.assertNotIn("has 5 item(s)", completed.stdout)

    def test_dynamic_output_is_list_is_rejected_but_unresolved_returns_are_skipped(self) -> None:
        self.fixture.write(
            "dynamic.py",
            """
            class DynamicNode:
                RETURN_TYPES = tuple(runtime_types)
                RETURN_NAMES = tuple(runtime_names)
                OUTPUT_IS_LIST = tuple([False] * len(runtime_types))

                def on_exec(self):
                    return ("unknown expected arity",)

            NODE_CLASS_MAPPINGS = {"Dynamic": DynamicNode}
            NODE_DISPLAY_NAME_MAPPINGS = {"Dynamic": "Dynamic"}
            """,
        )

        completed = self.fixture.run()

        self.assertEqual(completed.returncode, 1)
        self.assertEqual(completed.stdout.count("OUTPUT_IS_LIST_NOT_LITERAL"), 1)
        self.assertNotIn("RETURN_ARITY", completed.stdout)
        self.assertNotIn("ATTRIBUTE_ARITY", completed.stdout)

    def test_literal_conditional_return_branches_are_checked(self) -> None:
        self.fixture.write(
            "branches.py",
            """
            class BranchNode:
                RETURN_TYPES = (Types.STRING, Types.INTEGER)

                def on_exec(self, choose=False):
                    return ("ok", 1) if choose else ("wrong",)

            NODE_CLASS_MAPPINGS = {"Branch": BranchNode}
            NODE_DISPLAY_NAME_MAPPINGS = {"Branch": "Branch"}
            """,
        )

        completed = self.fixture.run()

        self.assertEqual(completed.returncode, 1)
        self.assertEqual(completed.stdout.count("RETURN_ARITY"), 1)

    def test_list_named_outputs_require_real_list_transport(self) -> None:
        self.fixture.write(
            "list_outputs.py",
            """
            class MissingFlag:
                RETURN_TYPES = (Types.STRING, Types.STRING)
                RETURN_NAMES = ("text", "text_list")

            class FalseFlag:
                RETURN_TYPES = (Types.STRING, Types.STRING)
                RETURN_NAMES = ("text", "text_list")
                OUTPUT_IS_LIST = (False, False)

            class RealList:
                RETURN_TYPES = (Types.STRING, Types.STRING)
                RETURN_NAMES = ("text", "text_list")
                OUTPUT_IS_LIST = (False, True)

            NODE_CLASS_MAPPINGS = {
                "MissingFlag": MissingFlag,
                "FalseFlag": FalseFlag,
                "RealList": RealList,
            }
            NODE_DISPLAY_NAME_MAPPINGS = {
                "MissingFlag": "Missing",
                "FalseFlag": "False",
                "RealList": "Real",
            }
            """,
        )

        completed = self.fixture.run()

        self.assertEqual(completed.returncode, 1)
        self.assertEqual(completed.stdout.count("LIST_OUTPUT_NOT_DECLARED"), 2)

    def test_exact_legacy_scalar_list_output_is_allowlisted(self) -> None:
        self.fixture.write(
            "legacy.py",
            """
            class LF_SetValueInJSON:
                RETURN_TYPES = (Types.JSON, Types.JSON)
                RETURN_NAMES = ("json", "json_list")
                OUTPUT_IS_LIST = (False, False)

            NODE_CLASS_MAPPINGS = {"LF_SetValueInJSON": LF_SetValueInJSON}
            NODE_DISPLAY_NAME_MAPPINGS = {"LF_SetValueInJSON": "Set value"}
            """,
        )

        completed = self.fixture.run()

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_literal_event_suffix_must_match_public_node_name(self) -> None:
        self.fixture.write(
            "event.py",
            """
            class LF_MyNode:
                RETURN_TYPES = ()

                def on_exec(self, node_id=None):
                    safe_send_sync("someothernode", {}, node_id)
                    return ()

            NODE_CLASS_MAPPINGS = {"LF_MyNode": LF_MyNode}
            NODE_DISPLAY_NAME_MAPPINGS = {"LF_MyNode": "My node"}
            """,
        )

        completed = self.fixture.run()

        self.assertEqual(completed.returncode, 1)
        self.assertEqual(completed.stdout.count("EVENT_SUFFIX_MISMATCH"), 1)
        self.assertIn("'lf-mynode'", completed.stdout)
        self.assertIn("'lf-someothernode'", completed.stdout)


if __name__ == "__main__":
    unittest.main()
