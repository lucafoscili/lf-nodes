import json

# region convert_to_json
def convert_to_json(text):
    """
    Convert a given text to a JSON object.

    Args:
        text (str): The text to be parsed as JSON.

    Returns:
        dict or None: The parsed JSON object if successful, otherwise None if conversion fails.
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None
# endregion