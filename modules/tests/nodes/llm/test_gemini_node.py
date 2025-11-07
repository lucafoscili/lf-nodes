# region Test Gemini API Node
# Set up common mocks before any imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from common_mocks import setup_common_mocks
setup_common_mocks()

import asyncio
import json
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Import the actual node implementation
from modules.nodes.llm.gemini_api import LF_GeminiAPI, NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
from modules.utils.constants import Input
from common_mocks import mock_async_response, mock_gemini_response, mock_prompt_server


class TestGeminiNode(unittest.TestCase):
    """Test cases for LF_GeminiAPI node following TDD principles."""

    def setUp(self):
        """Set up test fixtures."""
        self.node = LF_GeminiAPI()
        self.test_node_id = "test_node_123"

    def test_input_types_structure(self):
        """Test INPUT_TYPES returns correct structure."""
        inputs = LF_GeminiAPI.INPUT_TYPES()

        # Check required inputs
        self.assertIn("required", inputs)
        self.assertIn("prompt", inputs["required"])
        self.assertEqual(inputs["required"]["prompt"][1]["default"], "")

        # Check optional inputs
        self.assertIn("optional", inputs)
        self.assertIn("model", inputs["optional"])
        self.assertEqual(inputs["optional"]["model"][1]["default"], "gemini-2.0-flash")
        self.assertIn("timeout", inputs["optional"])
        self.assertIn("ui_widget", inputs["optional"])

        # Check hidden inputs
        self.assertIn("hidden", inputs)
        self.assertIn("node_id", inputs["hidden"])

    def test_input_types_validation(self):
        """Test INPUT_TYPES parameter validation."""
        inputs = LF_GeminiAPI.INPUT_TYPES()

        # Check timeout range
        timeout_config = inputs["optional"]["timeout"][1]
        self.assertEqual(timeout_config["default"], 60)

        # Check ui_widget type
        ui_widget_config = inputs["optional"]["ui_widget"][1]
        self.assertEqual(ui_widget_config["default"], "")

    def test_class_attributes(self):
        """Test class attributes are properly set."""
        self.assertEqual(LF_GeminiAPI.CATEGORY, "✨ LF Nodes/LLM")
        self.assertEqual(LF_GeminiAPI.FUNCTION, "on_exec")
        self.assertEqual(len(LF_GeminiAPI.OUTPUT_TOOLTIPS), 4)
        self.assertEqual(LF_GeminiAPI.RETURN_NAMES, ("text", "clean", "raw_json", "json"))
        self.assertEqual(LF_GeminiAPI.RETURN_TYPES, (Input.STRING, Input.STRING, Input.JSON, Input.JSON))

    def test_node_mappings(self):
        """Test node class and display name mappings."""
        self.assertIn("LF_GeminiAPI", NODE_CLASS_MAPPINGS)
        self.assertEqual(NODE_CLASS_MAPPINGS["LF_GeminiAPI"], LF_GeminiAPI)

        self.assertIn("LF_GeminiAPI", NODE_DISPLAY_NAME_MAPPINGS)
        self.assertEqual(NODE_DISPLAY_NAME_MAPPINGS["LF_GeminiAPI"], "Gemini API (Google)")

    @patch('modules.nodes.llm.gemini_api.create_ui_logger')
    def test_on_exec_empty_prompt_raises_error(self, mock_logger):
        """Test on_exec raises error for empty prompt."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        with self.assertRaises(ValueError) as context:
            asyncio.run(self.node.on_exec(prompt="", node_id=self.test_node_id))

        self.assertIn("Prompt must not be empty", str(context.exception))
        mock_logger_instance.log.assert_called_with("Prompt must not be empty.")

    @patch('modules.nodes.llm.gemini_api.PromptServer')
    @patch('modules.nodes.llm.gemini_api.create_ui_logger')
    def test_on_exec_no_proxy_url_raises_error(self, mock_logger, mock_ps_class):
        """Test on_exec raises error when no proxy URL is configured."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        # Mock environment and PromptServer to return no proxy URL
        with patch.dict(os.environ, {}, clear=True):
            mock_ps_class.instance = None

            with self.assertRaises(ValueError) as context:
                asyncio.run(self.node.on_exec(prompt="Test prompt", node_id=self.test_node_id))

            self.assertIn("No proxy URL configured", str(context.exception))
            mock_logger_instance.log.assert_called_with("No proxy URL configured. Set GEMINI_PROXY_URL environment variable or ensure PromptServer is running.")

    @patch('modules.nodes.llm.gemini_api.parse_gemini_json_output')  # 1st decorator
    @patch('modules.nodes.llm.gemini_api.clean_code_fences')        # 2nd decorator
    @patch('modules.nodes.llm.gemini_api.parse_gemini_response')    # 3rd decorator
    @patch('aiohttp.ClientSession')                              # 4th decorator
    @patch('modules.nodes.llm.gemini_api.create_ui_logger')        # 5th decorator
    def test_on_exec_successful_request(self, mock_logger, mock_session_class, mock_parse_response, mock_clean_fences, mock_parse_json):
        """Test successful Gemini API request."""
        # Setup mocks
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        # Mock helper functions
        mock_parse_response.return_value = "Hello from Gemini!"
        mock_clean_fences.return_value = "Hello from Gemini!"
        mock_parse_json.return_value = ""

        mock_session = MagicMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        # Create mock Gemini response
        gemini_data = mock_gemini_response("Hello from Gemini!")
        mock_response = mock_async_response(
            status=200,
            text=json.dumps(gemini_data),
            json_data=gemini_data
        )
        mock_session.post.return_value.__aenter__.return_value = mock_response

        # Mock proxy URL
        with patch.dict(os.environ, {"GEMINI_PROXY_URL": "http://test-proxy.com"}):
            result = asyncio.run(self.node.on_exec(
                prompt="Hello",
                model="gemini-2.0-flash",
                node_id=self.test_node_id
            ))

        # Verify result structure
        self.assertEqual(len(result), 4)
        self.assertIn("Hello from Gemini!", result[0])  # extracted text
        self.assertIn("Hello from Gemini!", result[1])  # clean text
        self.assertIsInstance(result[2], str)  # raw_json
        self.assertIsInstance(result[3], str)  # json_text

        # Verify request payload structure
        call_args = mock_session.post.call_args
        payload = call_args[1]['json']
        self.assertEqual(payload["model"], "gemini-2.0-flash")
        self.assertIn("contents", payload)
        self.assertEqual(len(payload["contents"]), 1)
        self.assertEqual(len(payload["contents"][0]["parts"]), 1)
        self.assertEqual(payload["contents"][0]["parts"][0]["text"], "Hello")

        # Verify logging
        mock_logger_instance.log.assert_any_call("Sending request...")
        mock_logger_instance.log.assert_any_call("Request completed successfully.")

    @patch('aiohttp.ClientSession')
    @patch('modules.nodes.llm.gemini_api.create_ui_logger')
    def test_on_exec_json_response_error(self, mock_logger, mock_session_class):
        """Test handling of non-JSON response."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        mock_session = MagicMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        # Create mock response that fails JSON parsing
        mock_response = mock_async_response(
            status=200,
            text="Plain text response"
            # No json_data provided, so json() will raise exception
        )
        mock_session.post.return_value.__aenter__.return_value = mock_response

        with patch.dict(os.environ, {"GEMINI_PROXY_URL": "http://test-proxy.com"}):
            result = asyncio.run(self.node.on_exec(prompt="Test", node_id=self.test_node_id))

        # Should return 2-tuple on JSON error: (text_status, json_wrapper)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "Plain text response")
        parsed_wrapper = json.loads(result[1])
        self.assertEqual(parsed_wrapper["body"], "Plain text response")
        self.assertEqual(parsed_wrapper["lf_http_status"], 200)

        mock_logger_instance.log.assert_called_with("Failed to parse JSON response.")

    @patch('aiohttp.ClientSession')
    @patch('modules.nodes.llm.gemini_api.create_ui_logger')
    def test_on_exec_with_proxy_secret(self, mock_logger, mock_session_class):
        """Test request includes proxy secret when available."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        mock_session = MagicMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        gemini_data = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "OK"}]
                }
            }]
        }
        mock_response = mock_async_response(
            status=200,
            text=json.dumps(gemini_data),
            json_data=gemini_data
        )
        mock_session.post.return_value.__aenter__.return_value = mock_response

        with patch.dict(os.environ, {"GEMINI_PROXY_URL": "http://test-proxy.com"}):
            with patch('modules.nodes.llm.gemini_api.read_secret') as mock_read_secret:
                mock_read_secret.return_value = "test_secret"
                asyncio.run(self.node.on_exec(prompt="Test", node_id=self.test_node_id))

        # Verify headers include secret
        call_args = mock_session.post.call_args
        headers = call_args[1]['headers']
        self.assertEqual(headers["X-LF-Proxy-Secret"], "test_secret")

    @patch('aiohttp.ClientSession')
    @patch('modules.nodes.llm.gemini_api.create_ui_logger')
    def test_on_exec_default_parameters(self, mock_logger, mock_session_class):
        """Test on_exec uses default parameters when not provided."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        mock_session = MagicMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        gemini_data = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "OK"}]
                }
            }]
        }
        mock_response = mock_async_response(
            status=200,
            text=json.dumps(gemini_data),
            json_data=gemini_data
        )
        mock_session.post.return_value.__aenter__.return_value = mock_response

        with patch.dict(os.environ, {"GEMINI_PROXY_URL": "http://test-proxy.com"}):
            asyncio.run(self.node.on_exec(prompt="Test", node_id=self.test_node_id))

        # Verify default values
        call_args = mock_session.post.call_args
        payload = call_args[1]['json']
        self.assertEqual(payload["model"], "gemini-2.0-flash")

    @patch('aiohttp.ClientSession')
    @patch('modules.nodes.llm.gemini_api.create_ui_logger')
    def test_on_exec_custom_timeout(self, mock_logger, mock_session_class):
        """Test on_exec respects custom timeout parameter."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        mock_session = MagicMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        gemini_data = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "OK"}]
                }
            }]
        }
        mock_response = mock_async_response(
            status=200,
            text=json.dumps(gemini_data),
            json_data=gemini_data
        )
        mock_session.post.return_value.__aenter__.return_value = mock_response

        with patch.dict(os.environ, {"GEMINI_PROXY_URL": "http://test-proxy.com"}):
            asyncio.run(self.node.on_exec(prompt="Test", timeout=120, node_id=self.test_node_id))

        # Verify timeout is passed to aiohttp
        call_args = mock_session.post.call_args
        self.assertEqual(call_args[1]['timeout'], 120)

    @patch('aiohttp.ClientSession')
    @patch('modules.nodes.llm.gemini_api.PromptServer')
    @patch('modules.nodes.llm.gemini_api.create_ui_logger')
    def test_on_exec_promptserver_proxy_url(self, mock_logger, mock_ps_class, mock_session_class):
        """Test proxy URL construction from PromptServer."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        mock_session = MagicMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        gemini_data = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "OK"}]
                }
            }]
        }
        mock_response = mock_async_response(
            status=200,
            text=json.dumps(gemini_data),
            json_data=gemini_data
        )
        mock_session.post.return_value.__aenter__.return_value = mock_response

        # Mock PromptServer instance
        mock_ps_instance = mock_prompt_server("127.0.0.1", 8188)
        mock_ps_class.instance = mock_ps_instance

        # Clear GEMINI_PROXY_URL to test PromptServer fallback
        with patch.dict(os.environ, {}, clear=True):
            asyncio.run(self.node.on_exec(prompt="Test", node_id=self.test_node_id))

        # Verify correct proxy URL was used
        call_args = mock_session.post.call_args
        expected_url = "http://127.0.0.1:8188/lf-nodes/proxy/gemini"
        self.assertEqual(call_args[0][0], expected_url)

    @patch('aiohttp.ClientSession')
    @patch('modules.nodes.llm.gemini_api.PromptServer')
    @patch('modules.nodes.llm.gemini_api.create_ui_logger')
    def test_on_exec_dev_env_proxy_url(self, mock_logger, mock_ps_class, mock_session_class):
        """Test proxy URL construction in dev environment."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        mock_session = MagicMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        gemini_data = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "OK"}]
                }
            }]
        }
        mock_response = mock_async_response(
            status=200,
            text=json.dumps(gemini_data),
            json_data=gemini_data
        )
        mock_session.post.return_value.__aenter__.return_value = mock_response

        # Mock dev environment
        with patch.dict(os.environ, {"DEV_ENV": "1"}):
            mock_ps_class.instance = None  # No PromptServer instance

            asyncio.run(self.node.on_exec(prompt="Test", node_id=self.test_node_id))

        # Verify dev proxy URL was used
        call_args = mock_session.post.call_args
        expected_url = "http://localhost:8080/lf-nodes/proxy/gemini"
        self.assertEqual(call_args[0][0], expected_url)


if __name__ == '__main__':
    unittest.main()

# endregion