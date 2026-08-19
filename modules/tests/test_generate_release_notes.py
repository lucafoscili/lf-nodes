import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "generate_release_notes.py"
SPEC = importlib.util.spec_from_file_location("generate_release_notes", SCRIPT_PATH)
release_notes = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(release_notes)


class GenerateReleaseNotesTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary_directory.name)
        self._git("init", "--initial-branch=main")
        self._git("config", "user.email", "tests@lf-nodes.invalid")
        self._git("config", "user.name", "LF Nodes Tests")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def _git(self, *args):
        return subprocess.run(
            ["git", *args],
            cwd=self.repo,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def _commit(self, subject):
        marker = self.repo / "history.txt"
        previous = marker.read_text(encoding="utf-8") if marker.exists() else ""
        marker.write_text(f"{previous}{subject}\n", encoding="utf-8")
        self._git("add", "history.txt")
        self._git("commit", "-m", subject)
        return self._git("rev-parse", "HEAD")

    def test_current_release_tag_is_excluded_and_all_new_commits_are_listed(self):
        self._commit("previous release")
        self._git("tag", "v2.7.1")
        self._commit("first feature")
        self._commit("second feature")
        release_head = self._commit("prepare release")
        self._git("tag", "v2.8.0")

        notes, previous_tag, commits = release_notes.generate_release_notes(
            self.repo,
            release_head,
            "v2.8.0",
            "2.8.0",
        )

        self.assertEqual("v2.7.1", previous_tag)
        self.assertEqual(3, len(commits))
        self.assertEqual(
            ["prepare release", "second feature", "first feature"],
            [entry.split(" ", 2)[2] for entry in commits],
        )
        self.assertIn("first feature", notes)
        self.assertIn("second feature", notes)
        self.assertIn("prepare release", notes)
        self.assertNotIn("previous release", notes)

    def test_untagged_release_head_uses_previous_release(self):
        self._commit("previous release")
        self._git("tag", "v1.0.0")
        release_head = self._commit("new feature")

        _, previous_tag, commits = release_notes.generate_release_notes(
            self.repo,
            release_head,
            "v1.1.0",
            "1.1.0",
        )

        self.assertEqual("v1.0.0", previous_tag)
        self.assertEqual(1, len(commits))
        self.assertIn("new feature", commits[0])

    def test_captured_release_head_ignores_later_repository_mutation(self):
        self._commit("previous release")
        self._git("tag", "v2.7.1")
        self._commit("release feature")
        release_head = self._commit("prepare release")
        self._commit("later repository mutation")
        self._git("tag", "v2.8.0")

        _, previous_tag, commits = release_notes.generate_release_notes(
            self.repo,
            release_head,
            "v2.8.0",
            "2.8.0",
        )

        self.assertEqual("v2.7.1", previous_tag)
        self.assertEqual(2, len(commits))
        self.assertFalse(any("later repository mutation" in entry for entry in commits))

    def test_repository_without_tags_lists_full_history(self):
        self._commit("initial feature")
        release_head = self._commit("second feature")

        _, previous_tag, commits = release_notes.generate_release_notes(
            self.repo,
            release_head,
            "v0.1.0",
            "0.1.0",
        )

        self.assertIsNone(previous_tag)
        self.assertEqual(2, len(commits))


if __name__ == "__main__":
    unittest.main()
