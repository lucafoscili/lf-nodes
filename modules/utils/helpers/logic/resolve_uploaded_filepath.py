import os
from typing import Tuple

from .sanitize_filename import sanitize_filename

# region resolve_uploaded_filepath
def resolve_uploaded_filepath(directory: str, file_name: str) -> Tuple[str, str]:
    """
    Resolve an uploaded filename to the path actually present on disk.

    The frontend saves uploaded files using a sanitized filename. This helper
    tries the sanitized name first, then the original name, and returns the
    first path that exists. If neither exists it returns the sanitized path
    (where the frontend most likely wrote the file).

    Returns a tuple (file_path, actual_filename) where actual_filename is the
    basename found on disk (or the sanitized candidate if not found).
    """

    sanitized_name = sanitize_filename(file_name) or file_name
    candidate_paths = [os.path.join(directory, sanitized_name), os.path.join(directory, file_name)]

    for p in candidate_paths:
        if os.path.exists(p):
            return p, os.path.basename(p)

    return os.path.join(directory, sanitized_name), sanitized_name
# endregion