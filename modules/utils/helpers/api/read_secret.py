# region read_secret
import os

def read_secret(env_name: str) -> str | None:
    """
    Reads a secret from environment variables or files.

    First checks the environment variable directly.
    If not found, checks for a file path in {env_name}_FILE and reads from that file.

    Args:
        env_name: The base environment variable name (e.g., "API_KEY")

    Returns:
        The secret value as a string, or None if not found
    """
    # Try direct environment variable
    value = os.environ.get(env_name)
    if value:
        return value

    # Try file-based secret
    file_env = f"{env_name}_FILE"
    file_path = os.environ.get(file_env)
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as fh:
                return fh.read().strip()
        except Exception:
            return None

    return None
# endregion