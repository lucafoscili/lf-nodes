# region parse_json_from_text
import json
import re

def parse_json_from_text(text: str) -> dict | list | None:
    """
    Attempts to parse JSON from a text string that may contain JSON embedded in other content.

    Handles various formats:
    - Direct JSON strings
    - JSON with unicode escapes
    - JSON embedded in markdown or other text using regex to find JSON objects/arrays

    Args:
        text: The text that may contain JSON

    Returns:
        Parsed JSON object/array, or None if parsing fails
    """
    if not text:
        return None

    text = text.strip()

    # Try direct parsing first
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try with unicode escape decoding
    try:
        decoded = bytes(text, 'utf-8').decode('unicode_escape')
        return json.loads(decoded)
    except Exception:
        pass

    # Try to find JSON objects or arrays using regex
    json_pattern = r'(\{[\s\S]*\}|\[[\s\S]*\])'
    match = re.search(json_pattern, text)
    if match:
        candidate = match.group(1)
        try:
            return json.loads(candidate)
        except Exception:
            pass

    # Last attempt with the full decoded text
    try:
        return json.loads(text.replace('\\/', '/'))
    except Exception:
        return None
# endregion