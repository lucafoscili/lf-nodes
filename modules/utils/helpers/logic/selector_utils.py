import logging
from typing import Any, Callable, Dict, Optional, Tuple, List, Protocol

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
        """
        Retrieve the value associated with the given key from the cache.

        Args:
            key (Any): The key to look up in the cache.

        Returns:
            Any: The value associated with the key if it exists, otherwise None.
        """
        return self._cache.get(key)

    def set(self, key: Any, value: Any) -> None:
        """
        Sets the value for the specified key in the cache.

        Args:
            key (Any): The key to set in the cache.
            value (Any): The value to associate with the key.

        Returns:
            None
        """
        self._cache[key] = value

    def get_or_set(self, key: Any, factory: Callable[[], Any]) -> Any:
        """
        Retrieves the value associated with the given key from the cache.
        If the key does not exist, creates a new value using the provided factory function,
        stores it in the cache, and returns it.

        Args:
            key (Any): The key to look up in the cache.
            factory (Callable[[], Any]): A function that returns a value to store if the key is not found.

        Returns:
            Any: The value associated with the key, either retrieved from the cache or newly created.
        """
        value = self._cache.get(key)
        if value is None:
            value = factory()
            self._cache[key] = value
        return value

    def clear(self) -> None:
        """
        Clears all items from the internal cache.

        This method removes all entries from the `_cache` attribute,
        effectively resetting the cache to an empty state.
        """
        self._cache.clear()

class CacheLike(Protocol):
    """
    Protocol representing a cache-like object.

    Classes implementing this protocol should provide a `clear` method
    that removes all items from the cache.

    Methods
    -------
    clear() -> None
        Removes all items from the cache.
    """
    def clear(self) -> None:
        ...

# Registry of caches so they can be cleared centrally (e.g., via a custom API)
_CACHE_REGISTRY: List[CacheLike] = []

def register_cache(cache: CacheLike) -> None:
    """
    Registers a cache instance in the global cache registry if it is not already present.

    Args:
        cache (CacheLike): The cache instance to register.

    Returns:
        None
    """
    if cache not in _CACHE_REGISTRY:
        _CACHE_REGISTRY.append(cache)

def clear_registered_caches() -> None:
    for cache in list(_CACHE_REGISTRY):
        try:
            cache.clear()
        except Exception:
            pass


class _SelectorListRefresher:
    """
    Utility class to refresh and manage a list attribute within an owner class, 
    typically used for dynamic selection lists in UI components.

    Args:
        owner_cls (Any): The class instance or type that owns the list attribute.
        loader (Callable[[], List[str]]): A callable that returns the latest list of string values.
        attr_name (str, optional): The name of the attribute in `owner_cls` to refresh. Defaults to "initial_list".
        return_index (Optional[int], optional): The index in the `RETURN_TYPES` tuple to update with the refreshed list. 
            If None, no update is performed. Defaults to 0.

    Methods:
        clear() -> List[str]:
            Refreshes the target list attribute in `owner_cls` using the loader.
            If the attribute exists and is a list, it is cleared and extended with new values.
            Otherwise, the attribute is set to the new list.
            Optionally updates the `RETURN_TYPES` tuple in `owner_cls` at `return_index` with the refreshed list.
            Returns the refreshed list.
    """
    def __init__(
        self,
        owner_cls: Any,
        loader: Callable[[], List[str]],
        attr_name: str = "initial_list",
        return_index: Optional[int] = 0,
    ) -> None:
        self._owner_cls = owner_cls
        self._loader = loader
        self._attr_name = attr_name
        self._return_index = return_index

    def clear(self) -> List[str]:
        """
        Clears and resets the target attribute list of the owner class to the values loaded by the loader.
        If the attribute is a list, it is cleared and extended with the loaded values; otherwise, it is set to the loaded values.
        Optionally updates the owner class's RETURN_TYPES tuple at the specified return index with the new list.
        
        Returns:
            List[str]: The updated list of values.
        """
        try:
            values = list(self._loader() or [])
        except Exception:
            logging.getLogger(__name__).exception("Selector loader failed; falling back to empty list.")
            values = []

        current = getattr(self._owner_cls, self._attr_name, None)
        if isinstance(current, list):
            current.clear()
            current.extend(values)
            target_list = current
        else:
            target_list = values
            setattr(self._owner_cls, self._attr_name, target_list)

        if self._return_index is not None:
            return_types = getattr(self._owner_cls, "RETURN_TYPES", None)
            if isinstance(return_types, tuple):
                rt_list = list(return_types)
                if self._return_index < len(rt_list):
                    rt_list[self._return_index] = target_list
                else:
                    rt_list.extend([None] * (self._return_index - len(rt_list) + 1))
                    rt_list[self._return_index] = target_list
                self._owner_cls.RETURN_TYPES = tuple(rt_list)

        return target_list


def register_selector_list(
    owner_cls: Any,
    loader: Callable[[], List[str]],
    attr_name: str = "initial_list",
    return_index: Optional[int] = 0,
):
    """
    Registers a selector list refresher for a given owner class.

    This function creates a _SelectorListRefresher instance using the provided owner class, loader function,
    attribute name, and return index. It clears the refresher, registers it in the cache, and returns the refresher instance.

    Args:
        owner_cls (Any): The class or object that owns the selector list.
        loader (Callable[[], List[str]]): A callable that returns a list of strings to populate the selector.
        attr_name (str, optional): The attribute name to store the initial list. Defaults to "initial_list".
        return_index (Optional[int], optional): The index to return from the selector list. Defaults to 0.

    Returns:
        _SelectorListRefresher: The registered selector list refresher instance.
    """
    refresher = _SelectorListRefresher(owner_cls, loader, attr_name, return_index)
    refresher.clear()
    register_cache(refresher)
    return refresher

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
