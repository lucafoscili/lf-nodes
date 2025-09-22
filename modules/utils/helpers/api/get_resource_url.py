import urllib

from .get_random_parameter import get_random_parameter

# region get_resource_url
def get_resource_url(subfolder: str, filename: str, resource_type: str = 'output'):
    """
    Generate a URL for accessing resources within the application.

    Args:
        subfolder (str): The subfolder where the resource is located.
        filename (str): The name of the resource file.
        resource_type (str): The type of resource. Defaults to 'output'.

    Returns:
        str: A formatted URL string for accessing the resource.
    """
    params = [
        f"filename={urllib.parse.quote(filename)}",
        f"type={resource_type}",
        f"subfolder={subfolder}",
        f"{get_random_parameter()}"
    ]
    
    return f"/view?{'&'.join(params)}"
# endregion