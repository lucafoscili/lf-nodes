import json
import piexif

from PIL.ExifTags import TAGS

# region extract_jpeg_metadata
def extract_jpeg_metadata(pil_image, file_name):
    """
    Extracts EXIF metadata from a JPEG image using a PIL Image object.

    Args:
        pil_image (PIL.Image): The PIL image object containing the JPEG image data.
        file_name (str): The filename of the JPEG image for error reporting.

    Returns:
        dict: A dictionary containing EXIF metadata if found, error message otherwise.
    """
    try:
        exif_bytes = pil_image.info.get('exif', None)
        if exif_bytes is None:
            return {"error": f"No EXIF metadata found in {file_name}"}

        exif_data = piexif.load(exif_bytes)

        if isinstance(exif_data, bytes):
            return {"format": "JPEG", "metadata": {}}

        if not exif_data:
            return {"error": f"Failed to load EXIF data from {file_name}"}

        exif_json = {}

        def safe_convert_value(v):
            if isinstance(v, bytes):
                return v.decode('utf-8', errors='ignore')
            elif isinstance(v, list):
                return [safe_convert_value(i) for i in v]
            else:
                return v

        for item in exif_data.values():
            if hasattr(item, 'items'):
                for tag, value in item.items():
                    tag_name = TAGS.get(tag, tag)
                    exif_json[tag_name] = safe_convert_value(value)

        try:
            json.dumps(exif_json)
        except TypeError as e:
            for k, v in list(exif_json.items()):
                try:
                    json.dumps({k: v})
                except TypeError:
                    del exif_json[k]

        return  exif_json

    except Exception as e:
        return {"error": f"An unexpected error occurred while extracting EXIF data from {file_name}: {str(e)}"}
# endregion