import io
import re

from PIL import Image
from server import PromptServer

from . import CATEGORY
from ...utils.constants import EVENT_PREFIX, FUNCTION, Input
from ...utils.helpers.conversion import pil_to_tensor
from ...utils.helpers.logic import normalize_list_to_value, normalize_output_image

# region LF_BlobToImage
class LF_BlobToImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_blob": (Input.FILE_BLOB, {
                    "tooltip": "Raw byte blob, e.g. from LF_LoadFileOnce"
                })
            },
            "optional": {
                "ui_widget": (Input.LF_CODE, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    EMBEDDED_FORMATS = [
        {"name": "PNG",  "header": b"\x89PNG\r\n\x1a\n", "footer": b"\xAE\x42\x60\x82"},
        {"name": "JPEG","header": b"\xff\xd8\xff",      "footer": b"\xff\xd9"},
        {"name": "GIF",  "header": b"GIF87a",            "footer": b"\x3B"},
        {"name": "WebP", "header": b"RIFF",             "length_offset": 4, "length_size": 4, "length_endian": "little"},
        {"name": "BMP",  "header": b"BM",               "length_offset": 2, "length_size": 4, "length_endian": "little"},
        {"name": "TIFF", "headers": [b"II*\x00", b"MM\x00*"], "use_eof": True},
        {"name": "ICO",  "header": b"\x00\x00\x01\x00",  "use_eof": True},
        {"name": "HEIF", "header": b"ftypheic",         "length_offset": -4, "length_size": 4, "length_endian": "big"},
        {"name": "HEVC", "header": b"ftyphevc",         "length_offset": -4, "length_size": 4, "length_endian": "big"},
    ]
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)

    def on_exec(self, **kwargs: dict):
        blob = normalize_list_to_value(kwargs.get("file_blob"))
        size_bytes = len(blob) if blob else 0
        log_lines = [f"- **Blob Size**: {size_bytes} bytes"]

        try:
            pil_img = Image.open(io.BytesIO(blob))
            log_lines += [
                f"- **Detected Format**: {pil_img.format}",
                f"- **Original Mode**: {pil_img.mode}",
                f"- **Dimensions**: {pil_img.width}x{pil_img.height}",
            ]
            pil_img = pil_img.convert("RGB")
            status = "✅ Decoding successful"
            primary_success = True
        except Exception as e:
            status = f"❌ Decoding failed: {e}"
            pil_img = Image.new("RGB", (1, 1))
            log_lines.append("- **Fallback**: created 1x1 dummy image")
            primary_success = False

        hidden_tensors = []

        for fmt in self.EMBEDDED_FORMATS:
            headers = fmt.get("headers") or [fmt.get("header")]
            for hdr in headers:
                if not hdr:
                    continue
                pattern = re.escape(hdr)
                for m in re.finditer(pattern, blob):
                    start = m.start()

                    if primary_success and start == 0:
                        continue

                    end = None
                    if "length_offset" in fmt:
                        off = start + fmt["length_offset"]
                        length = int.from_bytes(blob[off:off+fmt["length_size"]], fmt["length_endian"])
                        base = off if fmt["length_offset"] < 0 else start
                        end = base + length
                    elif fmt.get("use_eof"):
                        end = len(blob)
                    else:
                        ftr = fmt.get("footer")
                        idx = blob.find(ftr, start) if ftr else -1
                        if idx != -1:
                            end = idx + len(ftr)
                    if end and end > start:
                        slice_start = start + fmt.get("length_offset", 0) if fmt.get("length_offset", 0) < 0 else start
                        chunk = blob[slice_start:end]
                        try:
                            img_hidden = Image.open(io.BytesIO(chunk)).convert("RGB")
                            hidden_tensors.append(pil_to_tensor(img_hidden))
                            log_lines.append(f"- **Found {fmt['name']} @ offset {start}**")
                        except Exception:
                            pass

        if primary_success:
            main_tensor = pil_to_tensor(pil_img)
            all_tensors = [main_tensor] + hidden_tensors
        else:
            if hidden_tensors:
                main_tensor = hidden_tensors.pop(0)
                all_tensors = [main_tensor] + hidden_tensors
                log_lines.append("- **Using first embedded image as primary output**")
            else:
                main_tensor = pil_to_tensor(pil_img)
                all_tensors = [main_tensor]

        log_md = f"""## Blob → Image Breakdown

### Status
{status}

### Details
{chr(10).join(log_lines)}
"""

        image_batch, image_list = normalize_output_image(all_tensors)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}blobtoimage", {
            "node": kwargs.get("node_id"), 
            "value": log_md
        })

        return (image_batch[0], image_list)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_BlobToImage": LF_BlobToImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_BlobToImage": "Blob to Image",
}
# endregion