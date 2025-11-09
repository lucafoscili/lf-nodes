"""
Unit tests for API helper functions.
Tests cover endpoint validation, response handling, URL resolution, hashing, and secret management.
"""

import hashlib
import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch, mock_open
import urllib.parse


# region Embedded function implementations for standalone testing
def clean_code_fences(text: str) -> str:
    """
    Removes markdown code fences from text responses.
    """
    if not text:
        return text

    # Check if text starts with code fence
    if text.startswith('```') and '```' in text[3:]:
        end_fence = text.rfind('```')
        inner_content = text[3:end_fence]

        # Remove language identifier from first line if present
        lines = inner_content.splitlines()
        if lines and lines[0].strip() in ('python', 'javascript', 'java', 'cpp', 'c++', 'c', 'bash', 'sh', 'json', 'xml', 'html', 'css', 'sql', 'yaml', 'yml'):
            inner_content = '\n'.join(lines[1:])

        return inner_content.strip()
    else:
        # Remove backticks but preserve other content
        return text.replace('`', '').strip()


def get_sha256(file_path: str):
    """
    Calculate or retrieve the SHA-256 hash of a file.
    """
    hash_file_path = f"{os.path.splitext(file_path)[0]}.sha256"

    # Check if hash file exists and is valid
    if os.path.exists(hash_file_path):
        try:
            with open(hash_file_path, "r") as hash_file:
                cached_hash = hash_file.read().strip()
                if cached_hash and len(cached_hash) == 64:  # Valid SHA-256 length
                    return cached_hash
        except (IOError, OSError):
            pass  # If reading fails, recalculate hash

    # Calculate hash with larger buffer for better performance
    sha256_value = hashlib.sha256()
    buffer_size = 8 * 1024 * 1024  # 8MB buffer

    try:
        with open(file_path, "rb") as file:
            while True:
                chunk = file.read(buffer_size)
                if not chunk:
                    break
                sha256_value.update(chunk)

        hex_hash = sha256_value.hexdigest()

        # Save hash to cache file
        try:
            with open(hash_file_path, "w") as hash_file:
                hash_file.write(hex_hash)
        except (IOError, OSError):
            pass  # If writing fails, just return the hash without caching

        return hex_hash
    except (IOError, OSError) as e:
        raise RuntimeError(f"Error calculating hash for {file_path}: {e}")


def handle_response(response: dict, method: str = "GET"):
    """
    Handles the response from a Language Model (LLM) endpoint.
    """
    try:
        # Try status_code first
        try:
            status_val = response.status_code
            if isinstance(status_val, (int, str)) and status_val is not None:
                status = int(status_val)
            else:
                raise ValueError("Invalid status value")
        except (AttributeError, ValueError):
            # Try status attribute
            try:
                status_val = response.status
                if isinstance(status_val, (int, str)) and status_val is not None:
                    status = int(status_val)
                else:
                    raise ValueError("Invalid status value")
            except (AttributeError, ValueError):
                status = None
    except Exception:
        status = None

    if status == 400:
        return status, method, "Bad Request"
    if status == 401:
        return status, method, "Unauthorized"
    if status == 403:
        return status, method, "Forbidden"
    if status == 404:
        return status, method, "Not Found"
    if status == 500:
        return status, method, "Internal Server Error"

    if status == 200:
        try:
            llm_result = response.json()
        except Exception:
            try:
                content = getattr(response, "content", None)
                if isinstance(content, (bytes, bytearray)):
                    return status, method, content.decode("utf-8", errors="replace")
            except Exception:
                pass
            return status, method, "Whoops! Something went wrong."

        try:
            if isinstance(llm_result, dict) and "choices" in llm_result and len(llm_result["choices"]) > 0:
                first = llm_result["choices"][0]
                # OpenAI chat-style
                if isinstance(first, dict) and "message" in first and isinstance(first["message"], dict) and "content" in first["message"]:
                    return status, method, first["message"]["content"]
                # OpenAI legacy choice.text
                if isinstance(first, dict) and "text" in first:
                    return status, method, first["text"]
        except Exception:
            pass

        try:
            if isinstance(llm_result, dict):
                for key in ("text", "result", "output", "content"):
                    if key in llm_result and isinstance(llm_result[key], str):
                        return status, method, llm_result[key]

                for gen_key in ("generations", "generation", "results"):
                    if gen_key in llm_result and isinstance(llm_result[gen_key], (list, tuple)) and len(llm_result[gen_key]) > 0:
                        first_gen = llm_result[gen_key][0]
                        if isinstance(first_gen, dict):
                            # look for common text fields
                            for tkey in ("text", "content", "output", "result"):
                                if tkey in first_gen and isinstance(first_gen[tkey], str):
                                    return status, method, first_gen[tkey]
                        elif isinstance(first_gen, str):
                            return status, method, first_gen
        except Exception:
            pass

        try:
            import json as _json
            pretty = _json.dumps(llm_result)
            return status, method, pretty
        except Exception:
            return status, method, "Whoops! Something went wrong."

    return status, method, "Whoops! Something went wrong."


def get_random_parameter(length: int = 8) -> str:
    """
    Generate a random parameter string.
    """
    import random
    import string
    return "nonce=" + ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_resource_url(subfolder: str, filename: str, resource_type: str = 'output'):
    """
    Generate a URL for accessing resources within the application.
    """
    params = [
        f"filename={urllib.parse.quote(filename)}",
        f"type={resource_type}",
        f"subfolder={urllib.parse.quote(subfolder)}",
        f"{get_random_parameter()}"
    ]

    return f"/view?{'&'.join(params)}"


def resolve_url(api_url: str):
    """
    Parses the given API URL and extracts query parameters.
    """
    from urllib.parse import urlparse, parse_qs

    parsed_url = urlparse(api_url)
    query_params = parse_qs(parsed_url.query)

    filename = query_params.get("filename", [None])[0]
    file_type = query_params.get("type", [None])[0]
    subfolder = query_params.get("subfolder", [None])[0]

    return filename, file_type, subfolder


def read_secret(env_name: str) -> str | None:
    """
    Reads a secret from environment variables or files.
    """
    # Try direct environment variable
    value = os.environ.get(env_name)
    if value:
        return value

    # Try file-based secret
    file_env = f"{env_name}_FILE"
    file_path = os.environ.get(file_env)
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as fh:
                return fh.read().strip()
        except Exception:
            return None

    return None
# endregion


class TestAPIHelpers(unittest.TestCase):
    """Test suite for API helper functions."""

    def test_clean_code_fences_basic(self):
        """Test clean_code_fences with basic fenced code block."""
        input_text = """```
def hello():
    print("world")
```"""
        expected = 'def hello():\n    print("world")'
        result = clean_code_fences(input_text)
        self.assertEqual(result, expected)

    def test_clean_code_fences_with_language(self):
        """Test clean_code_fences with language specifier."""
        input_text = """```python
def hello():
    print("world")
```"""
        expected = 'def hello():\n    print("world")'
        result = clean_code_fences(input_text)
        self.assertEqual(result, expected)

    def test_clean_code_fences_multiple_lines(self):
        """Test clean_code_fences with multiple lines and language."""
        input_text = """```javascript
function test() {
    console.log("Hello");
    return true;
}
```"""
        expected = 'function test() {\n    console.log("Hello");\n    return true;\n}'
        result = clean_code_fences(input_text)
        self.assertEqual(result, expected)

    def test_clean_code_fences_no_fences(self):
        """Test clean_code_fences with text that has no fences."""
        input_text = "This is regular text with `some` backticks"
        expected = "This is regular text with some backticks"
        result = clean_code_fences(input_text)
        self.assertEqual(result, expected)

    def test_clean_code_fences_empty_input(self):
        """Test clean_code_fences with empty input."""
        result = clean_code_fences("")
        self.assertEqual(result, "")

    def test_clean_code_fences_none_input(self):
        """Test clean_code_fences with None input."""
        result = clean_code_fences(None)
        self.assertIsNone(result)

    def test_clean_code_fences_only_backticks(self):
        """Test clean_code_fences with only backticks."""
        input_text = "```code```"
        expected = "code"
        result = clean_code_fences(input_text)
        self.assertEqual(result, expected)

    def test_get_sha256_basic_file(self):
        """Test get_sha256 with a basic text file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            result = get_sha256(temp_path)
            # Verify it's a valid SHA-256 hash
            self.assertEqual(len(result), 64)
            self.assertRegex(result, r'^[a-f0-9]+$')

            # Verify hash is consistent
            result2 = get_sha256(temp_path)
            self.assertEqual(result, result2)
        finally:
            os.unlink(temp_path)
            # Clean up hash file if it exists
            hash_file = f"{os.path.splitext(temp_path)[0]}.sha256"
            if os.path.exists(hash_file):
                os.unlink(hash_file)

    def test_get_sha256_cached_hash(self):
        """Test get_sha256 uses cached hash when available."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content for caching")
            temp_path = f.name

        try:
            # First call should calculate hash
            result1 = get_sha256(temp_path)

            # Manually create a fake hash file to test caching
            hash_file = f"{os.path.splitext(temp_path)[0]}.sha256"
            fake_hash = "a" * 64  # 64 character fake hash
            with open(hash_file, 'w') as hf:
                hf.write(fake_hash)

            # Second call should return cached hash
            result2 = get_sha256(temp_path)
            self.assertEqual(result2, fake_hash)
            self.assertNotEqual(result1, result2)
        finally:
            os.unlink(temp_path)
            if os.path.exists(hash_file):
                os.unlink(hash_file)

    def test_get_sha256_invalid_cached_hash(self):
        """Test get_sha256 recalculates when cached hash is invalid."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            result1 = get_sha256(temp_path)

            # Create invalid hash file (too short)
            hash_file = f"{os.path.splitext(temp_path)[0]}.sha256"
            with open(hash_file, 'w') as hf:
                hf.write("invalid")

            # Should recalculate hash
            result2 = get_sha256(temp_path)
            self.assertEqual(result1, result2)
        finally:
            os.unlink(temp_path)
            if os.path.exists(hash_file):
                os.unlink(hash_file)

    def test_get_sha256_nonexistent_file(self):
        """Test get_sha256 with nonexistent file."""
        with self.assertRaises(RuntimeError) as cm:
            get_sha256("/nonexistent/file.txt")
        self.assertIn("Error calculating hash", str(cm.exception))

    def test_handle_response_openai_chat_style(self):
        """Test handle_response with OpenAI chat-style response."""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Hello, world!"
                    }
                }
            ]
        }

        status, method, message = handle_response(response, "POST")
        self.assertEqual(status, 200)
        self.assertEqual(method, "POST")
        self.assertEqual(message, "Hello, world!")

    def test_handle_response_openai_legacy_style(self):
        """Test handle_response with OpenAI legacy-style response."""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "choices": [
                {
                    "text": "Legacy response text"
                }
            ]
        }

        status, method, message = handle_response(response, "POST")
        self.assertEqual(status, 200)
        self.assertEqual(method, "POST")
        self.assertEqual(message, "Legacy response text")

    def test_handle_response_simple_text_field(self):
        """Test handle_response with simple text field."""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "text": "Simple text response"
        }

        status, method, message = handle_response(response, "GET")
        self.assertEqual(status, 200)
        self.assertEqual(method, "GET")
        self.assertEqual(message, "Simple text response")

    def test_handle_response_generations_field(self):
        """Test handle_response with generations field."""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "generations": [
                {
                    "text": "Generated text"
                }
            ]
        }

        status, method, message = handle_response(response, "POST")
        self.assertEqual(status, 200)
        self.assertEqual(method, "POST")
        self.assertEqual(message, "Generated text")

    def test_handle_response_error_status_codes(self):
        """Test handle_response with various error status codes."""
        test_cases = [
            (400, "Bad Request"),
            (401, "Unauthorized"),
            (403, "Forbidden"),
            (404, "Not Found"),
            (500, "Internal Server Error")
        ]

        for status_code, expected_message in test_cases:
            with self.subTest(status_code=status_code):
                response = MagicMock()
                response.status_code = status_code

                status, method, message = handle_response(response, "GET")
                self.assertEqual(status, status_code)
                self.assertEqual(method, "GET")
                self.assertEqual(message, expected_message)

    def test_handle_response_json_fallback(self):
        """Test handle_response falls back to JSON serialization."""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"custom": "data", "value": 123}

        status, method, message = handle_response(response, "POST")
        self.assertEqual(status, 200)
        self.assertEqual(method, "POST")
        # Should be JSON string
        self.assertIn('"custom": "data"', message)
        self.assertIn('"value": 123', message)

    def test_handle_response_binary_content(self):
        """Test handle_response with binary content."""
        response = MagicMock()
        response.status_code = 200
        response.json.side_effect = Exception("Not JSON")
        response.content = b"Hello binary world"

        status, method, message = handle_response(response, "GET")
        self.assertEqual(status, 200)
        self.assertEqual(method, "GET")
        self.assertEqual(message, "Hello binary world")

    def test_handle_response_no_status(self):
        """Test handle_response with no status code."""
        response = MagicMock()
        # No status_code attribute
        response.status = None

        status, method, message = handle_response(response, "GET")
        self.assertIsNone(status)
        self.assertEqual(method, "GET")
        self.assertEqual(message, "Whoops! Something went wrong.")

    def test_get_random_parameter_default_length(self):
        """Test get_random_parameter with default length."""
        result = get_random_parameter()
        self.assertTrue(result.startswith("nonce="))
        # Should be "nonce=" + 8 characters
        self.assertEqual(len(result), 14)  # 6 for "nonce=" + 8 chars

    def test_get_random_parameter_custom_length(self):
        """Test get_random_parameter with custom length."""
        result = get_random_parameter(12)
        self.assertTrue(result.startswith("nonce="))
        self.assertEqual(len(result), 18)  # 6 for "nonce=" + 12 chars

    def test_get_random_parameter_alphanumeric(self):
        """Test get_random_parameter generates alphanumeric characters."""
        import string
        result = get_random_parameter(100)
        nonce_value = result[6:]  # Remove "nonce=" prefix
        allowed_chars = string.ascii_letters + string.digits

        for char in nonce_value:
            self.assertIn(char, allowed_chars)

    def test_get_resource_url_basic(self):
        """Test get_resource_url with basic parameters."""
        with patch('helpers.test_api_helpers.get_random_parameter') as mock_random:
            mock_random.return_value = "nonce=abc123"

            result = get_resource_url("images", "test.png", "output")
            expected = "/view?filename=test.png&type=output&subfolder=images&nonce=abc123"
            self.assertEqual(result, expected)

    def test_get_resource_url_special_characters(self):
        """Test get_resource_url with special characters in filename."""
        with patch('helpers.test_api_helpers.get_random_parameter') as mock_random:
            mock_random.return_value = "nonce=test"

            result = get_resource_url("my folder", "test file.png", "temp")
            # Should URL encode the filename and subfolder
            expected = "/view?filename=test%20file.png&type=temp&subfolder=my%20folder&nonce=test"
            self.assertEqual(result, expected)

    def test_get_resource_url_default_type(self):
        """Test get_resource_url with default resource type."""
        with patch('helpers.test_api_helpers.get_random_parameter') as mock_random:
            mock_random.return_value = "nonce=xyz789"

            result = get_resource_url("data", "model.json")
            expected = "/view?filename=model.json&type=output&subfolder=data&nonce=xyz789"
            self.assertEqual(result, expected)

    def test_resolve_url_complete_url(self):
        """Test resolve_url with complete URL containing all parameters."""
        url = "/view?filename=test.png&type=output&subfolder=images&nonce=abc123"
        filename, file_type, subfolder = resolve_url(url)

        self.assertEqual(filename, "test.png")
        self.assertEqual(file_type, "output")
        self.assertEqual(subfolder, "images")

    def test_resolve_url_partial_parameters(self):
        """Test resolve_url with only some parameters."""
        url = "/view?filename=test.json&type=temp"
        filename, file_type, subfolder = resolve_url(url)

        self.assertEqual(filename, "test.json")
        self.assertEqual(file_type, "temp")
        self.assertIsNone(subfolder)

    def test_resolve_url_no_parameters(self):
        """Test resolve_url with no query parameters."""
        url = "/view"
        filename, file_type, subfolder = resolve_url(url)

        self.assertIsNone(filename)
        self.assertIsNone(file_type)
        self.assertIsNone(subfolder)

    def test_resolve_url_encoded_parameters(self):
        """Test resolve_url with URL-encoded parameters."""
        url = "/view?filename=test%20file.png&subfolder=my%20folder"
        filename, file_type, subfolder = resolve_url(url)

        self.assertEqual(filename, "test file.png")
        self.assertEqual(subfolder, "my folder")
        self.assertIsNone(file_type)

    def test_resolve_url_empty_url(self):
        """Test resolve_url with empty URL."""
        filename, file_type, subfolder = resolve_url("")
        self.assertIsNone(filename)
        self.assertIsNone(file_type)
        self.assertIsNone(subfolder)

    def test_read_secret_from_env(self):
        """Test read_secret reads from environment variable."""
        env_name = "TEST_API_KEY"
        test_value = "secret123"

        with patch.dict(os.environ, {env_name: test_value}):
            result = read_secret(env_name)
            self.assertEqual(result, test_value)

    def test_read_secret_from_file(self):
        """Test read_secret reads from file when env var not set."""
        env_name = "TEST_API_KEY"
        file_env = f"{env_name}_FILE"
        test_value = "file_secret456"

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(test_value)
            temp_path = f.name

        try:
            with patch.dict(os.environ, {file_env: temp_path}):
                result = read_secret(env_name)
                self.assertEqual(result, test_value)
        finally:
            os.unlink(temp_path)

    def test_read_secret_file_not_found(self):
        """Test read_secret when file doesn't exist."""
        env_name = "TEST_API_KEY"
        file_env = f"{env_name}_FILE"

        with patch.dict(os.environ, {file_env: "/nonexistent/file"}):
            result = read_secret(env_name)
            self.assertIsNone(result)

    def test_read_secret_file_read_error(self):
        """Test read_secret when file can't be read."""
        env_name = "TEST_API_KEY"
        file_env = f"{env_name}_FILE"

        # Use a directory instead of a file to cause an exception
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {file_env: temp_dir}):
                result = read_secret(env_name)
                self.assertIsNone(result)

    def test_read_secret_not_found(self):
        """Test read_secret when neither env var nor file exists."""
        env_name = "NONEXISTENT_SECRET"
        result = read_secret(env_name)
        self.assertIsNone(result)

    def test_read_secret_env_precedence(self):
        """Test read_secret prefers env var over file."""
        env_name = "TEST_API_KEY"
        file_env = f"{env_name}_FILE"
        env_value = "env_secret"
        file_value = "file_secret"

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(file_value)
            temp_path = f.name

        try:
            with patch.dict(os.environ, {env_name: env_value, file_env: temp_path}):
                result = read_secret(env_name)
                self.assertEqual(result, env_value)  # Should prefer env var
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
