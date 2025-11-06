# region clean_code_fences
def clean_code_fences(text: str) -> str:
    """
    Removes markdown code fences from text responses.

    Handles fenced code blocks like:
    ```
    code here
    ```

    And language-specific fences like:
    ```python
    code here
    ```

    Args:
        text: The text that may contain code fences

    Returns:
        Text with code fences removed, keeping only the inner content
    """
    if not text:
        return text

    # Check if text starts with code fence
    if text.startswith('```') and '```' in text[3:]:
        end_fence = text.rfind('```')
        inner_content = text[3:end_fence]

        # Remove language identifier from first line if present
        lines = inner_content.splitlines()
        if lines and lines[0].strip().isalpha():
            inner_content = '\n'.join(lines[1:])

        return inner_content.strip()
    else:
        # Remove backticks but preserve other content
        return text.replace('`', '').strip()
# endregion