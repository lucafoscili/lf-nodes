# region normalize_conditioning
def normalize_conditioning(cond):
    """
    Normalize a ComfyUI CONDITIONING value.

    Parameters:
        cond: The input conditioning value, which can be:
            - None
            - A single pair [tensor, dict] or (tensor, dict)
            - A list of such pairs

    Returns:
        - A list of [tensor, dict] pairs if the input is valid.
        - None if the input is missing or invalid.

    Behavior:
        - If cond is None, returns None.
        - If cond is a list of pairs ([tensor, dict]), returns cond as-is.
        - If cond is a single pair ([tensor, dict] or (tensor, dict)), wraps it in a list.
        - Otherwise, returns None.
    """
    if cond is None:
        return None

    if isinstance(cond, list) and len(cond) > 0 and isinstance(cond[0], (list, tuple)) \
            and len(cond[0]) >= 2 and isinstance(cond[0][1], dict):
        return cond

    if isinstance(cond, (list, tuple)) and len(cond) == 2 and isinstance(cond[1], dict):
        return [list(cond) if not isinstance(cond, list) else cond]

    return None
# endregion
