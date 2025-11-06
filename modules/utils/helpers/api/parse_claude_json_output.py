import html
import json

from .parse_json_from_text import parse_json_from_text


def parse_claude_json_output(data: dict, extracted_text: str) -> str:
    """
    Parses JSON output from Claude API response with multiple fallback strategies.

    Args:
        data: The full Claude API response dict
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

    # Claude-specific fallbacks
    if parsed is None:
        try:
            # Try to extract from content array
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