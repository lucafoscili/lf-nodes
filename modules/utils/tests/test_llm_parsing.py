"""
Unit tests for LLM response parsing functionality.
"""

import json
import re
import html

# Copy the helper functions locally to avoid ComfyUI dependencies
def clean_code_fences(text: str) -> str:
    """Remove markdown code fences from text."""
    # Remove code blocks with language specifier
    text = re.sub(r'```[\w]*\n?', '', text)
    # Remove simple code blocks
    text = re.sub(r'```\n?', '', text)
    return text.strip()
# endregion

# region parse JSON
def parse_json_from_text(text: str) -> dict | list | None:
    """Extract JSON from text using regex."""
    # Look for JSON-like structures
    json_pattern = r'\{.*\}|\[.*\]'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Try to parse the entire text as JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    return None
# endregion

# region parse Gemini
def parse_gemini_json_output(data: dict, extracted_text: str) -> str:
    """Simplified Gemini JSON parsing for testing."""
    clean_text = clean_code_fences(extracted_text)

    parsed = parse_json_from_text(clean_text)
    if parsed is None and extracted_text:
        parsed = parse_json_from_text(extracted_text)

    # Gemini-specific fallbacks
    if parsed is None:
        try:
            candidates = data.get('candidates') if isinstance(data, dict) else None
            if candidates and isinstance(candidates, list) and len(candidates) > 0:
                first = candidates[0]
                if isinstance(first, dict):
                    out = first.get('output')
                    if isinstance(out, (dict, list)):
                        parsed = out
                    elif isinstance(out, str):
                        parsed = parse_json_from_text(out)

                    if parsed is None and isinstance(first.get('content'), list):
                        txt = ''.join([chunk.get('text', '') for chunk in first.get('content', []) if isinstance(chunk, dict)])
                        parsed = parse_json_from_text(txt)
        except Exception:
            parsed = None

    json_text = ""
    if parsed is not None:
        try:
            json_text = json.dumps(parsed, ensure_ascii=False)
        except Exception:
            json_text = ''

    if json_text:
        try:
            json_text = html.unescape(json_text)
        except Exception:
            pass

    return json_text
# endregion

# region parse OpenAI
def parse_openai_json_output(data: dict, extracted_text: str) -> str:
    """Simplified OpenAI JSON parsing for testing."""
    clean_text = clean_code_fences(extracted_text)

    parsed = parse_json_from_text(clean_text)
    if parsed is None and extracted_text:
        parsed = parse_json_from_text(extracted_text)

    # OpenAI-specific fallbacks
    if parsed is None:
        try:
            choices = data.get('choices') if isinstance(data, dict) else None
            if choices and isinstance(choices, list) and len(choices) > 0:
                first_choice = choices[0]
                if isinstance(first_choice, dict):
                    message = first_choice.get('message')
                    if isinstance(message, dict):
                        content = message.get('content', '')
                        parsed = parse_json_from_text(content)
        except Exception:
            parsed = None

    json_text = ""
    if parsed is not None:
        try:
            json_text = json.dumps(parsed, ensure_ascii=False)
        except Exception:
            json_text = ''

    if json_text:
        try:
            json_text = html.unescape(json_text)
        except Exception:
            pass

    return json_text
# endregion

# region parse Claude
def parse_claude_json_output(data: dict, extracted_text: str) -> str:
    """Simplified Claude JSON parsing for testing."""
    clean_text = clean_code_fences(extracted_text)

    parsed = parse_json_from_text(clean_text)
    if parsed is None and extracted_text:
        parsed = parse_json_from_text(extracted_text)

    # Claude-specific fallbacks
    if parsed is None:
        try:
            content = data.get('content') if isinstance(data, dict) else None
            if content and isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_content = item.get('text', '')
                        parsed = parse_json_from_text(text_content)
                        if parsed:
                            break
        except Exception:
            parsed = None

    json_text = ""
    if parsed is not None:
        try:
            json_text = json.dumps(parsed, ensure_ascii=False)
        except Exception:
            json_text = ''

    if json_text:
        try:
            json_text = html.unescape(json_text)
        except Exception:
            pass

    return json_text
# endregion

# region Gemini response
def get_mock_gemini_response(text_content: str = "Hello from Gemini!", include_json: bool = False):
    response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": text_content}
                    ]
                },
                "finishReason": "STOP"
            }
        ]
    }

    if include_json:
        response["candidates"][0]["content"]["parts"][0]["text"] += '\n\n```json\n{"result": "mock_data", "status": "success"}\n```'

    return response
# endregion

# region OpenAI response
def get_mock_openai_response(text_content: str = "Hello from OpenAI!", include_json: bool = False):
    response = {
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": text_content
                },
                "finish_reason": "stop"
            }
        ]
    }

    if include_json:
        response["choices"][0]["message"]["content"] += '\n\n```json\n{"result": "mock_data", "status": "success"}\n```'

    return response
# endregion

# region Claude response
def get_mock_claude_response(text_content: str = "Hello from Claude!", include_json: bool = False):
    response = {
        "content": [
            {
                "type": "text",
                "text": text_content
            }
        ]
    }

    if include_json:
        response["content"][0]["text"] += '\n\n```json\n{"result": "mock_data", "status": "success"}\n```'

    return response
# endregion

class TestLLMResponseParsing:
    """Test suite for LLM response parsing functions."""

    # region clean_code_fences
    def test_clean_code_fences_basic(self):
        """Test basic code fence removal."""
        input_text = "```python\nprint('hello')\n```"
        result = clean_code_fences(input_text)
        assert result == "print('hello')"

    def test_clean_code_fences_with_language(self):
        """Test code fence removal with language specifier."""
        input_text = "```json\n{\"key\": \"value\"}\n```"
        result = clean_code_fences(input_text)
        assert result == "{\"key\": \"value\"}"

    def test_clean_code_fences_multiple(self):
        """Test multiple code fences in text."""
        input_text = "Before ```code\nmiddle\n``` after"
        result = clean_code_fences(input_text)
        assert result == "Before middle after"

    def test_clean_code_fences_no_fences(self):
        """Test text without code fences."""
        input_text = "Just regular text"
        result = clean_code_fences(input_text)
        assert result == "Just regular text"
    # endregion

    # region Gemini
    def test_gemini_parsing_basic_text(self):
        """Test Gemini parsing with basic text response."""
        mock_data = get_mock_gemini_response("Hello world!")
        extracted_text = clean_code_fences("Hello world!")

        result = parse_gemini_json_output(mock_data, extracted_text)

        # Should return empty string for plain text
        assert result == ""

    def test_gemini_parsing_json_response(self):
        """Test Gemini parsing with JSON in response."""
        mock_data = get_mock_gemini_response("Here's some data:", include_json=True)
        json_text = clean_code_fences('```json\n{"result": "mock_data", "status": "success"}\n```')

        result = parse_gemini_json_output(mock_data, json_text)

        # Should extract and return the JSON
        assert result == '{"result": "mock_data", "status": "success"}'

        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed["result"] == "mock_data"
        assert parsed["status"] == "success"

    def test_gemini_parsing_fallback_structure(self):
        """Test Gemini parsing using response structure fallback."""
        # Create mock data with output field in candidates
        mock_data = {
            "candidates": [
                {
                    "output": {"result": "fallback_data", "status": "ok"}
                }
            ]
        }
        extracted_text = "Some text without JSON"

        result = parse_gemini_json_output(mock_data, extracted_text)

        assert result == '{"result": "fallback_data", "status": "ok"}'
    # endregion

    # region OpenAI
    def test_openai_parsing_basic_text(self):
        """Test OpenAI parsing with basic text response."""
        mock_data = get_mock_openai_response("Hello from GPT!")
        extracted_text = clean_code_fences("Hello from GPT!")

        result = parse_openai_json_output(mock_data, extracted_text)

        # Should return empty string for plain text
        assert result == ""

    def test_openai_parsing_json_response(self):
        """Test OpenAI parsing with JSON in response."""
        mock_data = get_mock_openai_response("Here's some data:", include_json=True)
        json_text = clean_code_fences('```json\n{"result": "mock_data", "status": "success"}\n```')

        result = parse_openai_json_output(mock_data, json_text)

        # Should extract and return the JSON
        assert result == '{"result": "mock_data", "status": "success"}'

        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed["result"] == "mock_data"
        assert parsed["status"] == "success"

    def test_openai_parsing_fallback_structure(self):
        """Test OpenAI parsing using response structure fallback."""
        # Create mock data with content in message
        mock_data = {
            "choices": [
                {
                    "message": {
                        "content": 'Here is your JSON: ```json\n{"result": "fallback_data"}\n```'
                    }
                }
            ]
        }
        extracted_text = "Some text without JSON"

        result = parse_openai_json_output(mock_data, extracted_text)

        assert result == '{"result": "fallback_data"}'
    # endregion

    # region Claude
    def test_claude_parsing_basic_text(self):
        """Test Claude parsing with basic text response."""
        mock_data = get_mock_claude_response("Hello from Claude!")
        extracted_text = clean_code_fences("Hello from Claude!")

        result = parse_claude_json_output(mock_data, extracted_text)

        # Should return empty string for plain text
        assert result == ""

    def test_claude_parsing_json_response(self):
        """Test Claude parsing with JSON in response."""
        mock_data = get_mock_claude_response("Here's some data:", include_json=True)
        json_text = clean_code_fences('```json\n{"result": "mock_data", "status": "success"}\n```')

        result = parse_claude_json_output(mock_data, json_text)

        # Should extract and return the JSON
        assert result == '{"result": "mock_data", "status": "success"}'

        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed["result"] == "mock_data"
        assert parsed["status"] == "success"

    def test_claude_parsing_fallback_structure(self):
        """Test Claude parsing using response structure fallback."""
        # Create mock data with text content in content array
        mock_data = {
            "content": [
                {
                    "type": "text",
                    "text": 'Here is your JSON: ```json\n{"result": "fallback_data"}\n```'
                }
            ]
        }
        extracted_text = "Some text without JSON"

        result = parse_claude_json_output(mock_data, extracted_text)

        assert result == '{"result": "fallback_data"}'
    # endregion

    # region HTML
    def test_html_unescaping(self):
        """Test that HTML entities are properly unescaped in JSON output."""
        mock_data = get_mock_gemini_response("Here's some data:", include_json=True)

        # Create JSON with HTML entities
        json_with_entities = clean_code_fences('```json\n{"text": "Hello &amp; welcome!"}\n```')

        result = parse_gemini_json_output(mock_data, json_with_entities)

        # Should unescape HTML entities
        parsed = json.loads(result)
        assert parsed["text"] == "Hello & welcome!"
    # endregion

    # region Malformed and Empty
    def test_malformed_json_handling(self):
        """Test handling of malformed JSON gracefully."""
        mock_data = get_mock_gemini_response("Some text")
        malformed_json = clean_code_fences('```json\n{"incomplete": json}\n```')

        result = parse_gemini_json_output(mock_data, malformed_json)

        # Should return empty string for malformed JSON
        assert result == ""

    def test_empty_responses(self):
        """Test handling of empty or None responses."""
        result = parse_gemini_json_output({}, "")
        assert result == ""

        result = parse_gemini_json_output(None, "")
        assert result == ""

        result = parse_openai_json_output({}, "")
        assert result == ""

        result = parse_claude_json_output({}, "")
        assert result == ""
    # endregion


class TestLLMResponseParsing:
    """Test suite for LLM response parsing functions."""

    # region clean_code_fences
    def test_clean_code_fences_basic(self):
        """Test basic code fence removal."""
        input_text = "```python\nprint('hello')\n```"
        result = clean_code_fences(input_text)
        assert result == "print('hello')"
    # endregion

    # region clean_code_fences
    def test_clean_code_fences_with_language(self):
        """Test code fence removal with language specifier."""
        input_text = "```json\n{\"key\": \"value\"}\n```"
        result = clean_code_fences(input_text)
        assert result == "{\"key\": \"value\"}"

    def test_clean_code_fences_multiple(self):
        """Test multiple code fences in text."""
        input_text = "Before ```code\nmiddle\n``` after"
        result = clean_code_fences(input_text)
        assert result == "Before middle after"

    def test_clean_code_fences_no_fences(self):
        """Test text without code fences."""
        input_text = "Just regular text"
        result = clean_code_fences(input_text)
        assert result == "Just regular text"
    # endregion

    # region Gemini
    def test_gemini_parsing_basic_text(self):
        """Test Gemini parsing with basic text response."""
        mock_data = get_mock_gemini_response("Hello world!")
        extracted_text = clean_code_fences("Hello world!")

        result = parse_gemini_json_output(mock_data, extracted_text)

        # Should return empty string for plain text
        assert result == ""

    def test_gemini_parsing_json_response(self):
        """Test Gemini parsing with JSON in response."""
        mock_data = get_mock_gemini_response("Here's some data:", include_json=True)
        json_text = clean_code_fences('```json\n{"result": "mock_data", "status": "success"}\n```')

        result = parse_gemini_json_output(mock_data, json_text)

        # Should extract and return the JSON
        assert result == '{"result": "mock_data", "status": "success"}'

        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed["result"] == "mock_data"
        assert parsed["status"] == "success"

    def test_gemini_parsing_fallback_structure(self):
        """Test Gemini parsing using response structure fallback."""
        # Create mock data with output field in candidates
        mock_data = {
            "candidates": [
                {
                    "output": {"result": "fallback_data", "status": "ok"}
                }
            ]
        }
        extracted_text = "Some text without JSON"

        result = parse_gemini_json_output(mock_data, extracted_text)

        assert result == '{"result": "fallback_data", "status": "ok"}'
    # endregion

    # region OpenAI
    def test_openai_parsing_basic_text(self):
        """Test OpenAI parsing with basic text response."""
        mock_data = get_mock_openai_response("Hello from GPT!")
        extracted_text = clean_code_fences("Hello from GPT!")

        result = parse_openai_json_output(mock_data, extracted_text)

        # Should return empty string for plain text
        assert result == ""

    def test_openai_parsing_json_response(self):
        """Test OpenAI parsing with JSON in response."""
        mock_data = get_mock_openai_response("Here's some data:", include_json=True)
        json_text = clean_code_fences('```json\n{"result": "mock_data", "status": "success"}\n```')

        result = parse_openai_json_output(mock_data, json_text)

        # Should extract and return the JSON
        assert result == '{"result": "mock_data", "status": "success"}'

        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed["result"] == "mock_data"
        assert parsed["status"] == "success"

    def test_openai_parsing_fallback_structure(self):
        """Test OpenAI parsing using response structure fallback."""
        # Create mock data with content in message
        mock_data = {
            "choices": [
                {
                    "message": {
                        "content": 'Here is your JSON: ```json\n{"result": "fallback_data"}\n```'
                    }
                }
            ]
        }
        extracted_text = "Some text without JSON"

        result = parse_openai_json_output(mock_data, extracted_text)

        assert result == '{"result": "fallback_data"}'
    # endregion

    # region Claude
    def test_claude_parsing_basic_text(self):
        """Test Claude parsing with basic text response."""
        mock_data = get_mock_claude_response("Hello from Claude!")
        extracted_text = clean_code_fences("Hello from Claude!")

        result = parse_claude_json_output(mock_data, extracted_text)

        # Should return empty string for plain text
        assert result == ""

    def test_claude_parsing_json_response(self):
        """Test Claude parsing with JSON in response."""
        mock_data = get_mock_claude_response("Here's some data:", include_json=True)
        json_text = clean_code_fences('```json\n{"result": "mock_data", "status": "success"}\n```')

        result = parse_claude_json_output(mock_data, json_text)

        # Should extract and return the JSON
        assert result == '{"result": "mock_data", "status": "success"}'

        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed["result"] == "mock_data"
        assert parsed["status"] == "success"

    def test_claude_parsing_fallback_structure(self):
        """Test Claude parsing using response structure fallback."""
        # Create mock data with text content in content array
        mock_data = {
            "content": [
                {
                    "type": "text",
                    "text": 'Here is your JSON: ```json\n{"result": "fallback_data"}\n```'
                }
            ]
        }
        extracted_text = "Some text without JSON"

        result = parse_claude_json_output(mock_data, extracted_text)

        assert result == '{"result": "fallback_data"}'
    # endregion

    # region HTML
    def test_html_unescaping(self):
        """Test that HTML entities are properly unescaped in JSON output."""
        mock_data = get_mock_gemini_response("Here's some data:", include_json=True)

        # Create JSON with HTML entities
        json_with_entities = clean_code_fences('```json\n{"text": "Hello &amp; welcome!"}\n```')

        result = parse_gemini_json_output(mock_data, json_with_entities)

        # Should unescape HTML entities
        parsed = json.loads(result)
        assert parsed["text"] == "Hello & welcome!"
    # endregion

    # region Malformed and Empty
    def test_malformed_json_handling(self):
        """Test handling of malformed JSON gracefully."""
        mock_data = get_mock_gemini_response("Some text")
        malformed_json = clean_code_fences('```json\n{"incomplete": json}\n```')

        result = parse_gemini_json_output(mock_data, malformed_json)

        # Should return empty string for malformed JSON
        assert result == ""

    def test_empty_responses(self):
        """Test handling of empty or None responses."""
        result = parse_gemini_json_output({}, "")
        assert result == ""

        result = parse_gemini_json_output(None, "")
        assert result == ""

        result = parse_openai_json_output({}, "")
        assert result == ""

        result = parse_claude_json_output({}, "")
        assert result == ""
    # endregion