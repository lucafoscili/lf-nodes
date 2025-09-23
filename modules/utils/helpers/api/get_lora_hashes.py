import folder_paths

from .get_sha256 import get_sha256

# region get_lora_hashes
def get_lora_hashes(lora_tags: str, analytics_dataset: dict):
    """
    Retrieve SHA256 hashes for Lora tags.

    Args:
        lora_tags (str): A string of Lora tags.
        analytics_dataset (dict): A dataset to which nodes can be appended.

    Returns:
        List[str]: A list containing the name and hash of each Lora tag.
    """
    children = []
    lora_hashes = []
    lora_tags = lora_tags.replace("><", ">,<")
    lora_entries = [tag.strip('<>').split(':') for tag in lora_tags.split(',')]
    analytics_dataset["nodes"].append({ "children": children, "id": "loras"})

    for lora_entry in lora_entries:
        if len(lora_entry) >= 2:
            lora_name = lora_entry[1].strip()
            if not lora_name.endswith('.pt') and not lora_name.endswith('.safetensors'):
                lora_name_with_ext = f"{lora_name}.safetensors"
            else:
                lora_name_with_ext = lora_name
            lora_file_path = folder_paths.get_full_path("loras", lora_name_with_ext)
            try:
                lora_hash = get_sha256(lora_file_path)
                lora_hashes.append(f"{lora_name_with_ext}: {lora_hash}")
                children.append({ "id": lora_name, "value": lora_name })
            except Exception:
                lora_hashes.append(f"{lora_name}: Unknown")
    return lora_hashes
# endregion