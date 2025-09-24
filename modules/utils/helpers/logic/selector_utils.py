from typing import Any, Callable, Dict, Optional, Tuple

class LazyCache:
    """
    A simple cache class that lazily stores and retrieves values associated with keys.

    Methods
    -------
    __init__():
        Initializes an empty cache.

    get(key: Any) -> Any:
        Retrieves the value associated with the given key, or None if the key is not present.

    set(key: Any, value: Any) -> None:
        Stores the value in the cache under the specified key.

    get_or_set(key: Any, factory: Callable[[], Any]) -> Any:
        Retrieves the value for the given key if it exists; otherwise, computes the value using
        the provided factory function, stores it in the cache, and returns it.

    clear() -> None:
        Removes all items from the cache.
    """
    def __init__(self):
        self._cache: Dict[Any, Any] = {}

    def get(self, key: Any) -> Any:
        return self._cache.get(key)

    def set(self, key: Any, value: Any) -> None:
        self._cache[key] = value

    def get_or_set(self, key: Any, factory: Callable[[], Any]) -> Any:
        value = self._cache.get(key)
        if value is None:
            value = factory()
            self._cache[key] = value
        return value

    def clear(self) -> None:
        self._cache.clear()

def dtype_to_name(dtype: Any) -> str:
    """
    Converts a data type object to its string name representation.

    Attempts to retrieve the 'name' attribute from the given dtype object. If unavailable,
    returns the string representation of dtype, or "default" if dtype is None.

    Args:
        dtype (Any): The data type object to convert.

    Returns:
        str: The name of the data type, its string representation, or "default" if dtype is None.
    """
    try:
        return getattr(dtype, "name", None) or (str(dtype) if dtype is not None else "default")
    except Exception:
        return "default" if dtype is None else str(dtype)


def make_model_cache_key(path: str, dtype: Any = None, fp8_opt: bool = False, extra: Optional[Tuple[Any, ...]] = None) -> str:
    """
    Generates a stable, readable cache key for loaded models based on input parameters.

    Args:
        path (str): The file path to the model.
        dtype (Any, optional): The data type of the model (used for cache differentiation).
        fp8_opt (bool, optional): Whether FP8 optimization is enabled.
        extra (Optional[Tuple[Any, ...]], optional): Additional parameters to include in the cache key.

    Returns:
        str: A string representing the unique cache key for the model.
    """
    dtype_name = dtype_to_name(dtype)
    extra_str = f"|extra={repr(extra)}" if extra is not None else ""

    return f"{path}|dtype={dtype_name}|fp8opt={fp8_opt}{extra_str}"


def build_is_changed_tuple(randomize: bool, seed: Any, filter_value: Any, *components: Any) -> Tuple[Any, ...]:
    """
    Builds a tuple representing the change state of components, optionally including a randomization key.

    If `randomize` is True, the tuple includes a key composed of `filter_value` and `seed`.
    If `randomize` is False, the key is set to None.

    Args:
        randomize (bool): Whether to include the randomization key.
        seed (Any): The seed value for randomization.
        filter_value (Any): The filter value for randomization.
        *components (Any): Additional components to include in the tuple.

    Returns:
        Tuple[Any, ...]: A tuple containing the provided components and the randomization key.
    """
    rand_key = (filter_value, seed) if randomize else None

    return (*components, rand_key)
