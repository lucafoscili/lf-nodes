import random
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

folder_paths_mock = MagicMock()
folder_paths_mock.models_dir = "."
sys.modules.setdefault("folder_paths", folder_paths_mock)
sys.modules.setdefault("torch", MagicMock())

helpers_package = types.ModuleType("modules.utils.helpers")
helpers_package.__path__ = [str(REPO_ROOT / "modules" / "utils" / "helpers")]
sys.modules.setdefault("modules.utils.helpers", helpers_package)

ui_mock = MagicMock()
ui_mock.prepare_model_dataset = MagicMock(return_value={})
sys.modules.setdefault("modules.utils.helpers.ui", ui_mock)

from modules.nodes.json.get_random_key_from_json import (
    JSON_SAFE_SEED_MAX,
    LEGACY_SELECTION_MODE,
    WEIGHTED_SELECTION_MODE,
    LF_GetRandomKeyFromJSON,
    WeightedKeySelectionError,
    MAX_WEIGHT,
    select_weighted_key,
)


class TestGetRandomKeyFromJSON(unittest.TestCase):
    def test_legacy_mode_remains_the_default_and_preserves_random_choice(self):
        target = {"first": "", "second": "", "third": ""}
        expected = random.Random(42).choice(list(target.keys()))

        with patch("modules.nodes.json.get_random_key_from_json.safe_send_sync"):
            actual = LF_GetRandomKeyFromJSON().on_exec(seed=42, json_input=target)

        self.assertEqual(actual, (expected,))
        optional = LF_GetRandomKeyFromJSON.INPUT_TYPES()["optional"]
        self.assertEqual(list(optional), ["ui_widget", "selection_mode"])
        self.assertEqual(optional["selection_mode"][1]["default"], LEGACY_SELECTION_MODE)

    def test_numeric_values_are_weights_only_when_explicitly_enabled(self):
        target = {"braid hairstyle": 1, "high ponytail hairstyle": 10}
        expected_legacy = random.Random(17).choice(list(target.keys()))

        with patch("modules.nodes.json.get_random_key_from_json.safe_send_sync"):
            legacy = LF_GetRandomKeyFromJSON().on_exec(seed=17, json_input=target)
            weighted = LF_GetRandomKeyFromJSON().on_exec(
                seed=17,
                json_input=target,
                selection_mode=WEIGHTED_SELECTION_MODE,
            )

        self.assertEqual(legacy, (expected_legacy,))
        self.assertEqual(weighted, ("high ponytail hairstyle",))

    def test_weighted_mode_is_insertion_order_independent_and_has_a_golden_vector(self):
        first = {"braid hairstyle": 1, "high ponytail hairstyle": 10, "loose long hairstyle": 3}
        second = {"loose long hairstyle": 3, "high ponytail hairstyle": 10, "braid hairstyle": 1}

        self.assertEqual(select_weighted_key(4_503_599_627_370_495, first), "high ponytail hairstyle")
        self.assertEqual(select_weighted_key(4_503_599_627_370_495, second), "high ponytail hairstyle")

    def test_fixed_bucket_uses_the_same_weighted_path(self):
        self.assertEqual(select_weighted_key(0, {"silver-white moon glow eyes": 1}), "silver-white moon glow eyes")

    def test_weighted_mode_fails_closed_on_invalid_weights_and_unsafe_seeds(self):
        invalid = [
            {"a": ""},
            {"a": 0},
            {"a": -1},
            {"a": True},
            {"a": 1.5},
        ]
        for target in invalid:
            with self.subTest(target=target), self.assertRaises(WeightedKeySelectionError):
                select_weighted_key(1, target)
        with self.assertRaises(WeightedKeySelectionError):
            select_weighted_key(JSON_SAFE_SEED_MAX + 1, {"a": 1})
        self.assertEqual(select_weighted_key(1, {"a": MAX_WEIGHT}), "a")
        with self.assertRaises(WeightedKeySelectionError):
            select_weighted_key(1, {"a": MAX_WEIGHT + 1})

    def test_weighted_mode_does_not_mutate_python_global_random_state(self):
        random.seed(9188)
        before = random.getstate()
        select_weighted_key(42, {"a": 1, "b": 2})
        self.assertEqual(random.getstate(), before)


if __name__ == "__main__":
    unittest.main()
