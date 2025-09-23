import re

# region clean_prompt
def clean_prompt(prompt: str):
    """
    Cleans the given prompt by removing specific suffixes and leading components.

    Args:
        prompt (str): The input prompt string.

    Returns:
        str: The cleaned prompt string with suffix removed.
    """
    return re.sub(r'(embedding:)?(.*?)(\.pt|\.pth|\.sft|\.safetensors)?', r'\2', prompt).strip()
# endregion