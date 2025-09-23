import random
import string

# region get_random_parameter
def get_random_parameter(length: int = 8) -> str:
    """
    Generate a random parameter string.

    Args:
        length (int): The length of the random string. Defaults to 8.

    Returns:
        str: A random alphanumeric string prefixed with '?'.
    """
    return "nonce=" + ''.join(random.choices(string.ascii_letters + string.digits, k=length))
# endregion