"""
Mock responses for testing LLM providers without API keys.
"""

from typing import Dict, Any

# region Gemini
def get_mock_gemini_response(text_content: str = "Hello from Gemini!", include_json: bool = False) -> Dict[str, Any]:
    """Generate a mock Gemini API response."""
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
        ],
        "usageMetadata": {
            "promptTokenCount": 10,
            "candidatesTokenCount": 20,
            "totalTokenCount": 30
        }
    }

    if include_json:
        response["candidates"][0]["content"]["parts"][0]["text"] += '\n\n```json\n{"result": "mock_data", "status": "success"}\n```'

    return response
# endregion

# region OpenAI
def get_mock_openai_response(text_content: str = "Hello from OpenAI!", include_json: bool = False) -> Dict[str, Any]:
    """Generate a mock OpenAI API response."""
    response = {
        "id": "chatcmpl-mock123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4o",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": text_content
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }

    if include_json:
        response["choices"][0]["message"]["content"] += '\n\n```json\n{"result": "mock_data", "status": "success"}\n```'

    return response
# endregion

# region Claude
def get_mock_claude_response(text_content: str = "Hello from Claude!", include_json: bool = False) -> Dict[str, Any]:
    """Generate a mock Claude API response."""
    response = {
        "id": "msg_mock123",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": text_content
            }
        ],
        "model": "claude-3-sonnet-20240229",
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {
            "input_tokens": 10,
            "output_tokens": 20
        }
    }

    if include_json:
        response["content"][0]["text"] += '\n\n```json\n{"result": "mock_data", "status": "success"}\n```'

    return response
# endregion

# region Kobold
def get_mock_kobold_response(text_content: str = "Hello from Kobold!", include_json: bool = False) -> Dict[str, Any]:
    """Generate a mock Kobold API response."""
    response = {
        "results": [
            {
                "text": text_content
            }
        ],
        "prompt": "Test prompt",
        "details": {
            "tokens_cached": 0,
            "tokens_evaluated": 10,
            "tokens_generated": 20
        }
    }

    if include_json:
        response["results"][0]["text"] += '\n\n```json\n{"result": "mock_data", "status": "success"}\n```'

    return response
# endregion