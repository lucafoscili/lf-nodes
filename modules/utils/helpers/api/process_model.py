import folder_paths
import json
import os

from PIL import Image

from ....utils.constants import BASE64_PNG_PREFIX
from .get_sha256 import get_sha256
from .find_checkpoint_image import find_checkpoint_image
from ..conversion import base64_to_tensor, pil_to_tensor, tensor_to_base64

# region process_model
def process_model(model_type, model_name, folder):
    """
    Processes a model by gathering its path, hash, cover, and saved information.

    Args:
        model_type (str): The type of the model.
        model_name (str): The name of the model.
        folder (str): The folder where the model is located.

    Returns:
        dict: A dictionary containing the model's path, name, hash, cover, base64 representation, and saved info.
    """
    model_path = folder_paths.get_full_path(folder, model_name)
    model_info_path = os.path.splitext(model_path)[0] + ".info"

    saved_info = None
    if os.path.exists(model_info_path):
        try:
            with open(model_info_path, 'r') as f:
                file_content = f.read().strip()

                if not file_content:
                    os.remove(model_info_path)
                else:
                    try:
                        saved_info = json.loads(file_content)
                    except json.JSONDecodeError as e:
                        print(f"JSONDecodeError for {model_info_path}: {e}")
        except Exception as e:
            print(f"Error reading {model_info_path}: {e}")

    try:
        model_hash = get_sha256(model_path)
    except Exception as e:
        model_hash = "Unknown"
        print(f"Error calculating hash for {model_type}: {e}")

    model_base64 = None
    model_cover = None
    model_image_path = find_checkpoint_image(model_path)

    if saved_info:
        try:
            lf_image_value: str = saved_info['nodes'][0]['cells']['lfImage']['value']
            if lf_image_value and lf_image_value.startswith(BASE64_PNG_PREFIX):
                try:
                    model_base64 = lf_image_value.replace(BASE64_PNG_PREFIX, "")
                    model_cover = base64_to_tensor(model_base64)
                except Exception as e:
                    model_cover = None
            else:
                model_cover = None
        except (KeyError, IndexError):
            print("lfImage not found in saved_info, using defaults.")

    if model_image_path and model_cover == None:
        pil_image = Image.open(model_image_path)
        model_cover = pil_to_tensor(pil_image)
        model_base64 = tensor_to_base64(model_cover)

    return {
        "model_path": model_path,
        "model_name": model_name,
        "model_hash": model_hash,
        "model_cover": model_cover,
        "model_base64": model_base64,
        "saved_info": saved_info
    }
# endregion