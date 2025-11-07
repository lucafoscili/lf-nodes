# region parse_openai_response
def parse_openai_response(data: dict) -> str:
    """Extract text from OpenAI API response."""
    if not isinstance(data, dict):
        return str(data)

    choices = data.get('choices', [])
    if choices and isinstance(choices, list):
        first_choice = choices[0]
        if isinstance(first_choice, dict):
            message = first_choice.get('message', {})
            if isinstance(message, dict):
                return message.get('content', '')

    return ''
# endregion