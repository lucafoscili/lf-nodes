# region Test OpenAI API Node
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
from modules.nodes.llm.openai_api import LF_OpenAIAPI, NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
from modules.utils.constants import Input
from common_mocks import mock_async_response, mock_openai_response, mock_prompt_server


class TestOpenAINode(unittest.TestCase):
    """Test cases for LF_OpenAIAPI node following TDD principles."""

    def setUp(self):
        """Set up test fixtures."""
        self.node = LF_OpenAIAPI()
        self.test_node_id = "test_node_123"

    def test_input_types_structure(self):
        """Test INPUT_TYPES returns correct structure."""
        inputs = LF_OpenAIAPI.INPUT_TYPES()

        # Check required inputs
        self.assertIn("required", inputs)
        self.assertIn("prompt", inputs["required"])
        self.assertEqual(inputs["required"]["prompt"][1]["default"], "")

        # Check optional inputs
        self.assertIn("optional", inputs)
        self.assertIn("model", inputs["optional"])
        self.assertEqual(inputs["optional"]["model"][1]["default"], "gpt-4")
        self.assertIn("system_message", inputs["optional"])
        self.assertIn("temperature", inputs["optional"])
        self.assertIn("max_tokens", inputs["optional"])
        self.assertIn("timeout", inputs["optional"])

        # Check hidden inputs
        self.assertIn("hidden", inputs)
        self.assertIn("node_id", inputs["hidden"])

    def test_input_types_validation(self):
        """Test INPUT_TYPES parameter validation."""
        inputs = LF_OpenAIAPI.INPUT_TYPES()

        # Check temperature range
        temp_config = inputs["optional"]["temperature"][1]
        self.assertEqual(temp_config["min"], 0.0)
        self.assertEqual(temp_config["max"], 2.0)
        self.assertEqual(temp_config["step"], 0.1)
        self.assertEqual(temp_config["default"], 0.7)

        # Check max_tokens range
        tokens_config = inputs["optional"]["max_tokens"][1]
        self.assertEqual(tokens_config["min"], 1)
        self.assertEqual(tokens_config["max"], 4096)
        self.assertEqual(tokens_config["default"], 1000)

    def test_class_attributes(self):
        """Test class attributes are properly set."""
        self.assertEqual(LF_OpenAIAPI.CATEGORY, "✨ LF Nodes/LLM")
        self.assertEqual(LF_OpenAIAPI.FUNCTION, "on_exec")
        self.assertEqual(len(LF_OpenAIAPI.OUTPUT_TOOLTIPS), 4)
        self.assertEqual(LF_OpenAIAPI.RETURN_NAMES, ("text", "clean", "raw_json", "json"))
        self.assertEqual(LF_OpenAIAPI.RETURN_TYPES, (Input.STRING, Input.STRING, Input.JSON, Input.JSON))

    def test_node_mappings(self):
        """Test node class and display name mappings."""
        self.assertIn("LF_OpenAIAPI", NODE_CLASS_MAPPINGS)
        self.assertEqual(NODE_CLASS_MAPPINGS["LF_OpenAIAPI"], LF_OpenAIAPI)

        self.assertIn("LF_OpenAIAPI", NODE_DISPLAY_NAME_MAPPINGS)
        self.assertEqual(NODE_DISPLAY_NAME_MAPPINGS["LF_OpenAIAPI"], "OpenAI API (Chat)")

    @patch('modules.nodes.llm.openai_api.create_ui_logger')
    def test_on_exec_empty_prompt_raises_error(self, mock_logger):
        """Test on_exec raises error for empty prompt."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        with self.assertRaises(ValueError) as context:
            asyncio.run(self.node.on_exec(prompt="", node_id=self.test_node_id))

        self.assertIn("Prompt must not be empty", str(context.exception))
        mock_logger_instance.log.assert_called_with("Prompt must not be empty.")

    @patch('modules.nodes.llm.openai_api.PromptServer')
    @patch('modules.nodes.llm.openai_api.create_ui_logger')
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
            mock_logger_instance.log.assert_called_with("No proxy URL configured. Set OPENAI_PROXY_URL environment variable or ensure PromptServer is running.")

    @patch('modules.nodes.llm.openai_api.parse_openai_response')  # 1st decorator
    @patch('modules.nodes.llm.openai_api.clean_code_fences')        # 2nd decorator  
    @patch('modules.nodes.llm.openai_api.parse_openai_json_output')    # 3rd decorator
    @patch('aiohttp.ClientSession')                              # 4th decorator
    @patch('modules.nodes.llm.openai_api.create_ui_logger')        # 5th decorator
    def test_on_exec_successful_request(self, mock_logger, mock_session_class, mock_parse_json, mock_clean_fences, mock_parse_response):
        """Test successful OpenAI API request."""
        # Setup mocks
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        # Mock helper functions
        mock_parse_response.return_value = "Hello from GPT!"
        mock_clean_fences.return_value = "Hello from GPT!"
        mock_parse_json.return_value = ""

        mock_session = MagicMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        # Create mock OpenAI response
        openai_data = mock_openai_response("Hello from GPT!")
        mock_response = mock_async_response(
            status=200,
            text=json.dumps(openai_data),
            json_data=openai_data
        )
        mock_session.post.return_value.__aenter__.return_value = mock_response

        # Mock proxy URL
        with patch.dict(os.environ, {"OPENAI_PROXY_URL": "http://test-proxy.com"}):
            result = asyncio.run(self.node.on_exec(
                prompt="Hello",
                model="gpt-4",
                system_message="You are helpful",
                temperature=0.5,
                max_tokens=100,
                node_id=self.test_node_id
            ))

        # Verify result structure
        self.assertEqual(len(result), 4)
        self.assertIn("Hello from GPT!", result[0])  # extracted text
        self.assertIn("Hello from GPT!", result[1])  # clean text
        self.assertIsInstance(result[2], str)  # raw_json
        self.assertIsInstance(result[3], str)  # json_text

        # Verify request payload
        call_args = mock_session.post.call_args
        payload = call_args[1]['json']
        self.assertEqual(payload["model"], "gpt-4")
        self.assertEqual(payload["temperature"], 0.5)
        self.assertEqual(payload["max_tokens"], 100)
        self.assertEqual(len(payload["messages"]), 2)
        self.assertEqual(payload["messages"][0]["role"], "system")
        self.assertEqual(payload["messages"][0]["content"], "You are helpful")
        self.assertEqual(payload["messages"][1]["role"], "user")
        self.assertEqual(payload["messages"][1]["content"], "Hello")

        # Verify logging
        mock_logger_instance.log.assert_any_call("Sending request...")
        mock_logger_instance.log.assert_any_call("Request completed successfully.")

    @patch('aiohttp.ClientSession')
    @patch('modules.nodes.llm.openai_api.create_ui_logger')
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

        with patch.dict(os.environ, {"OPENAI_PROXY_URL": "http://test-proxy.com"}):
            result = asyncio.run(self.node.on_exec(prompt="Test", node_id=self.test_node_id))

        # Should return 2-tuple on JSON error: (text_status, json_wrapper)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "Plain text response")
        parsed_wrapper = json.loads(result[1])
        self.assertEqual(parsed_wrapper["body"], "Plain text response")
        self.assertEqual(parsed_wrapper["lf_http_status"], 200)

        mock_logger_instance.log.assert_called_with("Failed to parse JSON response.")

    @patch('aiohttp.ClientSession')
    @patch('modules.nodes.llm.openai_api.create_ui_logger')
    def test_on_exec_with_proxy_secret(self, mock_logger, mock_session_class):
        """Test request includes proxy secret when available."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        mock_session = MagicMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"choices": [{"message": {"content": "OK"}}]}')
        mock_response.json = AsyncMock(return_value={"choices": [{"message": {"content": "OK"}}]})
        mock_session.post.return_value.__aenter__.return_value = mock_response

        with patch.dict(os.environ, {"OPENAI_PROXY_URL": "http://test-proxy.com"}):
            with patch('modules.nodes.llm.openai_api.read_secret') as mock_read_secret:
                mock_read_secret.return_value = "test_secret"
                asyncio.run(self.node.on_exec(prompt="Test", node_id=self.test_node_id))

        # Verify headers include secret
        call_args = mock_session.post.call_args
        headers = call_args[1]['headers']
        self.assertEqual(headers["X-LF-Proxy-Secret"], "test_secret")

    @patch('aiohttp.ClientSession')
    @patch('modules.nodes.llm.openai_api.create_ui_logger')
    def test_on_exec_default_parameters(self, mock_logger, mock_session_class):
        """Test on_exec uses default parameters when not provided."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        mock_session = MagicMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"choices": [{"message": {"content": "OK"}}]}')
        mock_response.json = AsyncMock(return_value={"choices": [{"message": {"content": "OK"}}]})
        mock_session.post.return_value.__aenter__.return_value = mock_response

        with patch.dict(os.environ, {"OPENAI_PROXY_URL": "http://test-proxy.com"}):
            asyncio.run(self.node.on_exec(prompt="Test", node_id=self.test_node_id))

        # Verify default values
        call_args = mock_session.post.call_args
        payload = call_args[1]['json']
        self.assertEqual(payload["model"], "gpt-4")
        self.assertEqual(payload["temperature"], 0.7)
        self.assertEqual(payload["max_tokens"], 1000)
        self.assertEqual(payload["messages"][0]["content"], "You are a helpful assistant.")

    @patch('aiohttp.ClientSession')
    @patch('modules.nodes.llm.openai_api.create_ui_logger')
    def test_on_exec_custom_timeout(self, mock_logger, mock_session_class):
        """Test on_exec respects custom timeout parameter."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        mock_session = MagicMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"choices": [{"message": {"content": "OK"}}]}')
        mock_response.json = AsyncMock(return_value={"choices": [{"message": {"content": "OK"}}]})
        mock_session.post.return_value.__aenter__.return_value = mock_response

        with patch.dict(os.environ, {"OPENAI_PROXY_URL": "http://test-proxy.com"}):
            asyncio.run(self.node.on_exec(prompt="Test", timeout=120, node_id=self.test_node_id))

        # Verify timeout is passed to aiohttp
        call_args = mock_session.post.call_args
        self.assertEqual(call_args[1]['timeout'], 120)

    @patch('aiohttp.ClientSession')
    @patch('modules.nodes.llm.openai_api.PromptServer')
    @patch('modules.nodes.llm.openai_api.create_ui_logger')
    def test_on_exec_promptserver_proxy_url(self, mock_logger, mock_ps_class, mock_session_class):
        """Test proxy URL construction from PromptServer."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        mock_session = MagicMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"choices": [{"message": {"content": "OK"}}]}')
        mock_response.json = AsyncMock(return_value={"choices": [{"message": {"content": "OK"}}]})
        mock_session.post.return_value.__aenter__.return_value = mock_response

        # Mock PromptServer instance
        mock_ps_instance = mock_prompt_server("127.0.0.1", 8188)
        mock_ps_class.instance = mock_ps_instance

        # Clear OPENAI_PROXY_URL to test PromptServer fallback
        with patch.dict(os.environ, {}, clear=True):
            asyncio.run(self.node.on_exec(prompt="Test", node_id=self.test_node_id))

        # Verify correct proxy URL was used
        call_args = mock_session.post.call_args
        expected_url = "http://127.0.0.1:8188/lf-nodes/proxy/openai"
        self.assertEqual(call_args[0][0], expected_url)

    @patch('aiohttp.ClientSession')
    @patch('modules.nodes.llm.openai_api.PromptServer')
    @patch('modules.nodes.llm.openai_api.create_ui_logger')
    def test_on_exec_dev_env_proxy_url(self, mock_logger, mock_ps_class, mock_session_class):
        """Test proxy URL construction in dev environment."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        mock_session = MagicMock()
        mock_session_class.return_value.__aenter__.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"choices": [{"message": {"content": "OK"}}]}')
        mock_response.json = AsyncMock(return_value={"choices": [{"message": {"content": "OK"}}]})
        mock_session.post.return_value.__aenter__.return_value = mock_response

        # Mock dev environment
        with patch.dict(os.environ, {"DEV_ENV": "1"}):
            mock_ps_class.instance = None  # No PromptServer instance

            asyncio.run(self.node.on_exec(prompt="Test", node_id=self.test_node_id))

        # Verify dev proxy URL was used
        call_args = mock_session.post.call_args
        expected_url = "http://localhost:8080/lf-nodes/proxy/openai"
        self.assertEqual(call_args[0][0], expected_url)


if __name__ == '__main__':
    unittest.main()

# endregion