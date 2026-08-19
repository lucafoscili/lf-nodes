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
folder_paths_mock.get_filename_list.return_value = []
folder_paths_mock.get_input_directory.return_value = "."
folder_paths_mock.get_output_directory.return_value = "."
folder_paths_mock.get_temp_directory.return_value = "."
folder_paths_mock.get_user_directory.return_value = "."
folder_paths_mock.get_save_image_path.return_value = (".", "output", 0, "", None)

sys.modules.setdefault("folder_paths", folder_paths_mock)
sys.modules.setdefault("torch", MagicMock())

helpers_package = types.ModuleType("modules.utils.helpers")
helpers_package.__path__ = [str(REPO_ROOT / "modules" / "utils" / "helpers")]
sys.modules.setdefault("modules.utils.helpers", helpers_package)

ui_mock = MagicMock()
ui_mock.prepare_model_dataset = MagicMock(return_value={})
sys.modules.setdefault("modules.utils.helpers.ui", ui_mock)


from modules.nodes.json.get_value_from_json import LF_GetValueFromJSON


class TestGetValueFromJSONNode(unittest.TestCase):
    def setUp(self):
        self.node = LF_GetValueFromJSON()

    @patch("modules.nodes.json.get_value_from_json.safe_send_sync")
    def test_on_exec_supports_numeric_key_for_json_list(self, mock_safe_send_sync):
        result = self.node.on_exec(json_input=[10, 20], key="1", index=0, node_id="test-node")

        self.assertEqual(result, ({"value": 20}, "20", 20, 20, 20.0, True))
        mock_safe_send_sync.assert_called_once()

    @patch("modules.nodes.json.get_value_from_json.safe_send_sync")
    def test_on_exec_preserves_literal_strings_in_json_list(self, mock_safe_send_sync):
        result = self.node.on_exec(
            json_input=["Alpha", "Beta", "Gamma"],
            key="1",
            index=0,
            node_id="test-node",
        )

        self.assertEqual(result, ({"value": "Beta"}, "Beta", None, None, None, None))
        mock_safe_send_sync.assert_called_once()

    @patch("modules.nodes.json.get_value_from_json.safe_send_sync")
    def test_on_exec_preserves_single_literal_string_in_json_list(self, mock_safe_send_sync):
        result = self.node.on_exec(
            json_input=["Alpha"],
            key="0",
            index=0,
            node_id="test-node",
        )

        self.assertEqual(result, ({"value": "Alpha"}, "Alpha", None, None, None, None))
        mock_safe_send_sync.assert_called_once()

    @patch("modules.nodes.json.get_value_from_json.safe_send_sync")
    def test_on_exec_supports_nested_json_list_output(self, mock_safe_send_sync):
        first_result = self.node.on_exec(
            json_input={"items": [{"name": "alpha"}, {"name": "beta"}]},
            key="items",
            index=0,
            node_id="test-node",
        )

        second_result = self.node.on_exec(
            json_input=first_result[0],
            key="1",
            index=0,
            node_id="test-node",
        )

        self.assertEqual(second_result[0], {"name": "beta"})
        self.assertEqual(second_result[1], "{'name': 'beta'}")
        self.assertIsNone(second_result[2])
        self.assertIsNone(second_result[3])
        self.assertIsNone(second_result[4])
        self.assertIsNone(second_result[5])
        self.assertEqual(mock_safe_send_sync.call_count, 2)

    @patch("modules.nodes.json.get_value_from_json.safe_send_sync")
    def test_on_exec_preserves_object_key_lookup_for_json_list(self, mock_safe_send_sync):
        result = self.node.on_exec(
            json_input=[{"name": "alpha"}, {"name": "beta"}],
            key="name",
            index=1,
            node_id="test-node",
        )

        self.assertEqual(result, ({"value": "beta"}, "beta", None, None, None, None))
        mock_safe_send_sync.assert_called_once()

    @patch("modules.nodes.json.get_value_from_json.safe_send_sync")
    def test_on_exec_preserves_numeric_object_key_lookup(self, mock_safe_send_sync):
        result = self.node.on_exec(
            json_input=[{"1": "legacy value"}, {"1": "other value"}],
            key="1",
            index=0,
            node_id="test-node",
        )

        self.assertEqual(result, ({"value": "legacy value"}, "legacy value", None, None, None, None))
        mock_safe_send_sync.assert_called_once()

    @patch("modules.nodes.json.get_value_from_json.safe_send_sync")
    def test_on_exec_handles_empty_json_list(self, mock_safe_send_sync):
        result = self.node.on_exec(json_input=[], key="0", index=0, node_id="test-node")

        self.assertEqual(result, (None, None, None, None, None, None))
        mock_safe_send_sync.assert_called_once()


if __name__ == "__main__":
    unittest.main()
