import html
import json

from .parse_json_from_text import parse_json_from_text

# region parse_openai_json_output
def parse_openai_json_output(data: dict, extracted_text: str) -> str:
    """
    Parses JSON output from OpenAI API response with multiple fallback strategies.

    Args:
        data: The full OpenAI API response dict
        extracted_text: The text extracted from the response

    Returns:
        JSON string if parsing succeeds, empty string otherwise
    """
    # First try parsing from cleaned text
    clean_text = extracted_text  # Assume already cleaned by caller

    parsed = None
    try:
        parsed = parse_json_from_text(clean_text)
    except Exception:
        parsed = None

    # Fallback: try parsing from original extracted text
    if parsed is None and extracted_text:
        try:
            parsed = parse_json_from_text(extracted_text)
        except Exception:
            parsed = None

    # OpenAI-specific fallbacks
    if parsed is None:
        try:
            # Try to extract from choices array
            choices = data.get('choices') if isinstance(data, dict) else None
            if choices and isinstance(choices, list) and len(choices) > 0:
                first_choice = choices[0]
                if isinstance(first_choice, dict):
                    message = first_choice.get('message')
                    if isinstance(message, dict):
                        content = message.get('content', '')
                        parsed = parse_json_from_text(content)

                    # Try delta content for streaming responses
                    elif first_choice.get('delta'):
                        delta = first_choice.get('delta')
                        if isinstance(delta, dict):
                            content = delta.get('content', '')
                            parsed = parse_json_from_text(content)
        except Exception:
            parsed = None

    # Convert to JSON string
    json_text = ""
    if parsed is not None:
        try:
            json_text = json.dumps(parsed, ensure_ascii=False)
        except Exception:
            json_text = ''

    # HTML unescape
    if json_text:
        try:
            json_text = html.unescape(json_text)
        except Exception:
            pass

    return json_text
# endregion