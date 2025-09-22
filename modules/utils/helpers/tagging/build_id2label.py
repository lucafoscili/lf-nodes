import pandas as pd

from huggingface_hub import hf_hub_download
from transformers import AutoConfig

# region build_id2label
def build_id2label(model):
    """
    Attempts to build an `id2label` mapping for a given model using several strategies:
    1. Tries to retrieve `id2label` from the model's native Hugging Face config (`model.config.id2label`).
    2. If not found or contains only default labels (e.g., "LABEL_0"), attempts to locate a repository ID
       (from `model.pretrained_cfg` or `model.config`) and download a `selected_tags.csv` file from the Hugging Face Hub,
       using the "name" column to construct the mapping.
    3. If still unsuccessful, tries to load the config using `AutoConfig.from_pretrained` with the repository ID.
    4. Raises a `RuntimeError` if no valid `id2label` mapping can be found.

    Args:
        model: The model object to extract or build the `id2label` mapping from.

    Returns:
        dict: A mapping from integer class IDs to string labels.

    Raises:
        RuntimeError: If no valid `id2label` mapping can be found using any of the strategies.
    """
    try:
        cfg = getattr(model, "config", None)
        id2lab = getattr(cfg, "id2label", None)
    except Exception:
        id2lab = None

    if not id2lab or all(str(v).startswith("LABEL_") for v in id2lab.values()):
        repo = None
        for src in ("hf_hub_id",):
            pcfg = getattr(model, "pretrained_cfg", {}) or {}
            repo = pcfg.get(src) or getattr(getattr(model, "config", {}), src, None)
            if repo:
                break

        if repo:
            try:
                csv_file = hf_hub_download(repo_id=repo, filename="selected_tags.csv")
                names = pd.read_csv(csv_file, usecols=["name"])["name"].tolist()
                id2lab = {i: name for i, name in enumerate(names)}
            except Exception as e:
                id2lab = None

    if not id2lab:
        try:
            cfg2 = AutoConfig.from_pretrained(repo)
            id2lab = cfg2.id2label
        except Exception:
            id2lab = None

    if not id2lab:
        raise RuntimeError(
            f"No valid id2label mapping found on {model.__class__.__name__} "
            f"(tried .config.id2label, CSV fallback, AutoConfig.from_pretrained)."
        )

    return id2lab
# endregion