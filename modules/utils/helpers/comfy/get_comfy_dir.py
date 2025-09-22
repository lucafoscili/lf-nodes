import os

from folder_paths import get_input_directory, get_output_directory, get_temp_directory, get_user_directory

from ....utils.constants import BACKUP_FOLDER, USER_FOLDER

# region get_comfy_dir
def get_comfy_dir(folder: str):
    """
    Retrieve the directory path corresponding to a specified folder type.

    This function returns the full path of directories for various folder types used
    within the application. It uses predefined constants for folder names.

    Args:
        folder (str): The type of folder whose path is required. Valid values include:
            - "backup": Returns path to the backup folder.
            - "base": Returns path to the base user directory.
            - "input": Returns path to the input directory.
            - "output": Returns path to the output directory.
            - "temp": Returns path to the temporary directory.
            - "user": Returns path to the user directory.

    Returns:
        str: The path to the requested folder type.

    Raises:
        ValueError: If the folder type is invalid or unsupported.

    Examples:
        >>> get_directory("input")
        '/path/to/input/directory'

        >>> get_directory("user")
        '/path/to/user/directory'
    """
    if folder == "backup":
        dirpath = os.path.join(get_user_directory(), USER_FOLDER)
        return os.path.join(dirpath, BACKUP_FOLDER)
    if folder == "base":
        return os.path.join(get_user_directory(), USER_FOLDER)
    if folder == "input":
        return get_input_directory()
    elif folder == "output":
        return get_output_directory()
    elif folder == "temp":
        return get_temp_directory()
    elif folder == "user":
        return get_user_directory()
# endregion