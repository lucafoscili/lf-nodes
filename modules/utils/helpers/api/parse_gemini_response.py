# region parse_gemini_response
from typing import Any

def parse_gemini_response(response_data: dict) -> str:
    """
    Extracts text content from Gemini API response data.

    Handles various Gemini response formats:
    - Standard candidates with content.parts
    - Legacy output fields
    - Nested response structures

    Args:
        response_data: The JSON response from Gemini API

    Returns:
        Extracted text content as a string
    """
    if not isinstance(response_data, dict):
        return str(response_data)

    # Try standard Gemini format first
    candidates = response_data.get("candidates") or []
    if candidates and isinstance(candidates, list):
        first_candidate = candidates[0]
        if isinstance(first_candidate, dict):
            # Check for content field with parts
            if "content" in first_candidate:
                content = first_candidate["content"]
                if isinstance(content, list):
                    # Extract text from parts
                    return "".join(
                        chunk.get("text", "")
                        for chunk in content
                        if isinstance(chunk, dict)
                    )
                else:
                    return str(content)

            # Check for output field (legacy format)
            elif "output" in first_candidate:
                return str(first_candidate["output"])

            # Fallback to string representation
            else:
                return str(first_candidate)

    # Try legacy response format
    if "response" in response_data and isinstance(response_data["response"], dict):
        output = response_data["response"].get("output")
        if isinstance(output, list):
            return "\n".join(str(x) for x in output)
        else:
            return str(output or "")

    # Fallback to string representation of the entire response
    return str(response_data)
# endregion