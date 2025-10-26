from typing import Any

def json_safe(value: Any) -> Any:
    """
    Recursively converts a value to a JSON-safe representation.
    This function ensures that the input value can be serialized to JSON by handling
    non-JSON-serializable types (e.g., custom objects) by converting them to strings.
    It recursively processes dictionaries, lists, tuples, and sets, converting keys
    to strings where necessary.

    Args:
        value (Any): The value to make JSON-safe. Can be of any type.

    Returns:
        Any: A JSON-safe version of the input value. Primitives (None, str, int, float, bool)
             are returned as-is. Dictionaries are returned with string keys and recursively
             processed values. Sequences (lists, tuples, sets) are returned as lists with
             recursively processed elements. All other types are converted to strings.

    Examples:
        >>> _json_safe(42)
        42
        >>> _json_safe({'key': [1, 2, {'nested': 'value'}]})
        {'key': [1, 2, {'nested': 'value'}]}
        >>> _json_safe(SomeCustomClass())
        '<SomeCustomClass object at 0x...>'
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(v) for v in value]

    return str(value)