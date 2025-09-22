import folder_paths
import re

from .get_sha256 import get_sha256

# region get_embedding_hashes
def get_embedding_hashes(embeddings: str, analytics_dataset: dict):
    """
    Retrieve SHA256 hashes for the given embeddings.

    Args:
        embeddings (str): A comma-separated string of embedding names.
        analytics_dataset (dict): A dataset to which nodes can be appended.

    Returns:
        List[str]: A list containing the name and hash of each embedding.
    """
    children = []
    emb_hashes = []
    emb_entries = [emb.strip() for emb in embeddings.split(',')]
    analytics_dataset["nodes"].append({ "children": children, "id": "embeddings"})

    for emb_entry in emb_entries:
        match = re.match(r'(?:embedding:)?(.*)', emb_entry)
        if match:
            emb_name = match.group(1).strip()
            if emb_name:
                if not emb_name.endswith('.pt') and not emb_name.endswith('.safetensors'):
                    emb_name_with_ext = f"{emb_name}.safetensors"
                else:
                    emb_name_with_ext = emb_name
                    emb_file_path = folder_paths.get_full_path("embeddings", emb_name_with_ext)
                try:
                    emb_hash = get_sha256(emb_file_path)
                    emb_hashes.append(f"{emb_name_with_ext}: {emb_hash}")
                    children.append({ "id": emb_name, "value": emb_name })
                except Exception as e:
                    emb_hashes.append(f"{emb_name}: Unknown")
    return emb_hashes
# endregion