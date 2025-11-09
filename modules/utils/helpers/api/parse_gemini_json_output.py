import html
import json

from .parse_json_from_text import parse_json_from_text

# region parse_gemini_json_output
def parse_gemini_json_output(data: dict, extracted_text: str) -> str:
    """
    Parses JSON output from Gemini API response with multiple fallback strategies.

    Args:
        data: The full Gemini API response dict
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

    # Gemini-specific fallbacks
    if parsed is None:
        try:
            candidates = data.get('candidates') if isinstance(data, dict) else None
            if candidates and isinstance(candidates, list) and len(candidates) > 0:
                first = candidates[0]
                if isinstance(first, dict):
                    # Try output field
                    out = first.get('output')
                    if isinstance(out, (dict, list)):
                        parsed = out
                    elif isinstance(out, str):
                        parsed = parse_json_from_text(out)

                    # Try content chunks
                    if parsed is None and isinstance(first.get('content'), list):
                        txt = ''.join([chunk.get('text', '') for chunk in first.get('content', []) if isinstance(chunk, dict)])
                        parsed = parse_json_from_text(txt)

            # Legacy response format fallback
            if parsed is None and isinstance(data, dict) and isinstance(data.get('response'), dict):
                out = data['response'].get('output')
                if isinstance(out, (dict, list)):
                    parsed = out
                elif isinstance(out, str):
                    parsed = parse_json_from_text(out)
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