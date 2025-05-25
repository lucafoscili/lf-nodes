import io
import json
import numpy as np
import os
import re
import time
import torch
import torch.nn.functional as F

from PIL import Image, ImageFilter
from server import PromptServer
from urllib.parse import urlparse, parse_qs

from ..utils.constants import BLUE_CHANNEL_ID, CATEGORY_PREFIX, EVENT_PREFIX, FUNCTION, GREEN_CHANNEL_ID, Input, RED_CHANNEL_ID, RESAMPLERS
from ..utils.helpers import create_compare_node, create_masonry_node, create_resize_node, encode_text_for_sdclip, get_comfy_dir, get_otsu_threshold, get_resource_url, get_text_encoder_from_clip, get_tokenizer_from_clip, hex_to_tuple, normalize_input_image, normalize_input_list, normalize_json_input, normalize_list_item, normalize_list_to_value, normalize_output_image, not_none, numpy_to_tensor, pil_to_tensor, numpy_to_svg, resize_and_crop_image, resize_image, resize_to_square, resolve_filepath, tensor_to_numpy, tensor_to_pil

CATEGORY = f"{CATEGORY_PREFIX}/Image"

# region LF_BlobToImage
class LF_BlobToImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_blob": ("*", {
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
    FUNCTION = FUNCTION
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")
    OUTPUT_IS_LIST = (False, True)
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

# region LF_BlurImages
class LF_BlurImages:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "List of images to blur."
                }),
                "blur_percentage": (Input.FLOAT, {
                    "default": 0.25, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.05, 
                    "tooltip": "0% Blur: No blur applied, the image remains as-is. 100% Blur: Maximum blur applied based on the image's dimensions, which would result in a highly blurred (almost unrecognizable) image."
                }),
            },
            "optional": {
                "file_name": (Input.STRING, {
                    "forceInput": True, 
                    "tooltip": "Corresponding list of file names for the images."
                }),
                "ui_widget": (Input.LF_MASONRY, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = (True, False, False, True)
    OUTPUT_IS_LIST = (False, True, True, False)
    RETURN_NAMES = ("image", "image_list", "file_name", "count")
    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING", "INT")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        blur_percentage: float = normalize_list_to_value(kwargs.get("blur_percentage"))
        file_name: list[str] = normalize_input_list(kwargs.get("file_name"))

        blurred_images = []
        blurred_file_names = []

        nodes = []
        dataset = { "nodes": nodes }

        for index, img in enumerate(image):
            if file_name:
                split_name = file_name[index].rsplit('.', 1)
                if len(split_name) == 2:
                    base_name, _ = split_name
                else:
                    base_name = split_name[0]
            else:
                base_name = ""
            
            pil_image = tensor_to_pil(img)
            
            width, height = pil_image.size
            min_dimension = min(width, height)
            adjusted_blur_radius: float = blur_percentage * (min_dimension / 10)
            
            blurred_image = pil_image.filter(ImageFilter.GaussianBlur(adjusted_blur_radius))
            
            blurred_tensor = pil_to_tensor(blurred_image)
            blurred_images.append(blurred_tensor)

            filename_prefix = f"{base_name}_Blur"
            output_file, subfolder, filename = resolve_filepath(
                    filename_prefix=filename_prefix,
                    add_counter=False,
                    image=blurred_tensor,
            )
            blurred_image.save(output_file, format="PNG")
            url = get_resource_url(subfolder, filename, "temp")

            blurred_file_names.append(filename_prefix)
            nodes.append(create_masonry_node(filename, url, index))

        image_batch, image_list = normalize_output_image(blurred_images)
        
        PromptServer.instance.send_sync(f"{EVENT_PREFIX}blurimages", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (image_batch[0], image_list, blurred_file_names, len(image_list))
# endregion

# region LF_CompareImages
class LF_CompareImages:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image_after": (Input.IMAGE, {
                    "tooltip": "Image to be compared (AFTER)."
                }),
            },
            "optional": {
                "image_before": (Input.IMAGE, {
                    "tooltip": "Reference image (BEFORE). If not provided, the AFTER image is reused."
                }),
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = (True, True, False)
    OUTPUT_IS_LIST = (False, True, True, False)
    OUTPUT_NODE = True
    RETURN_NAMES = ("image", "image_list", "all_images", "dataset")
    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "JSON")

    def on_exec(self, **kwargs: dict):
        has_before : bool = "image_before" in kwargs and kwargs["image_before"] is not None

        image_list_a : list[torch.Tensor] = normalize_input_image(kwargs["image_after"])
        image_list_b : list[torch.Tensor] = normalize_input_image(kwargs["image_before"]) if has_before else image_list_a

        if len(image_list_a) != len(image_list_b):
            raise ValueError("Image lists must have the same length if both inputs are provided.")

        nodes: list[dict] = []
        dataset: dict = {"nodes": nodes}

        for idx, img_a in enumerate(image_list_a):

            pil_a = tensor_to_pil(img_a)
            file_a, sub_a, name_a = resolve_filepath(
                filename_prefix="compare_after", image=img_a
            )
            pil_a.save(file_a, format="PNG")
            url_a = get_resource_url(sub_a, name_a, "temp")

            if has_before:
                img_b = image_list_b[idx]
                pil_b = tensor_to_pil(img_b)
                file_b, sub_b, name_b = resolve_filepath(
                    filename_prefix="compare_before", image=img_b
                )
                pil_b.save(file_b, format="PNG")
                url_b = get_resource_url(sub_b, name_b, "temp")
            else:
                url_b = url_a

            nodes.append(create_compare_node(url_b, url_a, idx))

        image_batch, image_list = normalize_output_image(image_list_a)
        combined = image_list_a + (image_list_b if has_before else [])
        _, all_images = normalize_output_image(combined)

        PromptServer.instance.send_sync(
            f"{EVENT_PREFIX}compareimages", {"node": kwargs.get("node_id"), "dataset": dataset}
        )

        return (image_batch[0], image_list, all_images, dataset)
# endregion

# region LF_CreateMask
class LF_CreateMask:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "processor": ("*", {
                    "tooltip": "CLIPSegProcessor from LF_LoadHFModel (segmentation model).",
                }),
                "model":     ("*", {
                    "tooltip": "CLIPSegForImageSegmentation from LF_LoadHFModel (segmentation model).",
                }),
                "image": (Input.IMAGE, {
                    "tooltip": "Image tensor to segment."
                }),
                "prompt": (Input.STRING, {
                    "tooltip": "Text prompt for mask."
                }),
                "threshold_mode": (["fixed", "relative", "otsu"], {
                    "default": "otsu",
                    "tooltip": (
                        "Thresholding mode: 'fixed' uses the exact threshold value; "
                        "'relative' scales threshold by max probability; 'otsu' auto-computes."
                    )
                })
            },
            "optional": {
                "clip": (Input.CLIP, {
                    "tooltip": 
                    f"Optional Stable-Diffusion CLIP model:\n "
                    f"⚠️ Embeddings from this CLIP will not perfectly match the segmentation head—"
                    f"expect degraded mask accuracy unless you fine-tune or insert an adapter."
                }),
                "threshold": (Input.FLOAT, {
                    "default": 0.5, 
                    "min": 0.0, 
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Binarization threshold on mask probabilities (0→1). Lower to include more pixels."
                }),
                "relative_scale": (Input.FLOAT, {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "tooltip": "Fraction of peak probability to use when in 'relative' mode."
                }),
                "ui_widget": (Input.LF_COMPARE, {
                    "default":{}
                })
            },
            "hidden": {"node_id":"UNIQUE_ID"}
        }

    RETURN_TYPES   = ("IMAGE","IMAGE")
    RETURN_NAMES   = ("mask","mask_list")
    CATEGORY       = CATEGORY
    FUNCTION       = FUNCTION
    OUTPUT_IS_LIST = (False, True)

    def on_exec(self, **kwargs):
        images = normalize_input_image(kwargs["image"])
        proc = normalize_list_to_value(kwargs["processor"])
        seg_model = normalize_list_to_value(kwargs["model"])
        prompt = normalize_list_to_value(kwargs["prompt"])
        clip = normalize_list_to_value(kwargs.get("clip", None))
        mode = normalize_list_to_value(kwargs.get("threshold_mode", "otsu"))
        fixed_thresh = normalize_list_to_value(kwargs.get("threshold", 0.5))
        rel_scale = normalize_list_to_value(kwargs.get("relative_scale", 0.5))

        seg_model.eval()
        device = next(seg_model.parameters()).device

        masks, nodes = [], []
        dataset = { "nodes": nodes }

        for idx, img_tensor in enumerate(images):
            pil_img = tensor_to_pil(img_tensor)

            if clip is not None:
                text_encoder = get_text_encoder_from_clip(clip)
                tokenizer   = get_tokenizer_from_clip(clip)
                _, token_ids, attn_mask = encode_text_for_sdclip(
                    text_encoder, tokenizer, prompt, device
                )

                img_inputs   = proc(images=pil_img, return_tensors="pt")
                pixel_values = img_inputs.pixel_values.to(device)

                with torch.no_grad():
                    outputs = seg_model(
                        pixel_values=pixel_values,
                        input_ids=token_ids,
                        attention_mask=attn_mask
                    )
            else:
                inputs = proc(text=prompt, images=pil_img, return_tensors="pt")
                inputs = {k:v.to(device) for k,v in inputs.items()}
                with torch.no_grad():
                    outputs = seg_model(**inputs)

            probs = torch.sigmoid(outputs.logits)
            mask_prob = probs[0,0] if probs.ndim==4 else probs[0]

            if mode == "relative":
                thresh = mask_prob.max().item() * rel_scale
            elif mode == "otsu":
                prob_map = mask_prob.cpu().numpy() 
                thresh = get_otsu_threshold(prob_map)
            else:
                thresh = fixed_thresh

            mask_np = (mask_prob.cpu().numpy() >= thresh).astype("uint8")*255
            mask_pil = Image.fromarray(mask_np)
            
            m_t = pil_to_tensor(mask_pil.convert("RGB"))[0:1,...]
            m_t = m_t.to(device)    
            m_t = m_t.permute(0, 3, 1, 2) # [1,1,H,W]
            H, W = img_tensor.shape[1], img_tensor.shape[2]
            up = F.interpolate(m_t, size=(H,W), mode="bicubic", align_corners=False)
            up = up.permute(0,2,3,1) # [1,H,W,1]
            masks.append(up)

            orig_f, so, no = resolve_filepath("mask_orig", image=img_tensor)
            tensor_to_pil(img_tensor).save(orig_f, "PNG")
            mo, sm, nm = resolve_filepath("mask_bin", image=up)
            tensor_to_pil(up).save(mo, "PNG")
            nodes.append(create_compare_node(get_resource_url(so,no,"temp"),
                                               get_resource_url(sm,nm,"temp"),
                                               idx))

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}prompttomask", {
            "node": kwargs.get("node_id"),
            "dataset": dataset
        })

        image_batch, image_list = normalize_output_image(masks)

        return (image_batch[0], image_list)
# endregion

# region LF_EmptyImage
class LF_EmptyImage:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": (Input.INTEGER, {
                    "default": 1024, 
                    "min": 64, 
                    "max": 8192, 
                    "step": 64,
                    "tooltip": "Width of the empty image."
                }),
                "height": (Input.INTEGER, {
                    "default": 512, 
                    "min": 1, 
                    "max": 4096, 
                    "step": 1,
                    "tooltip": "Height of the empty image."
                }),
                "color": (Input.STRING, {
                    "default": "000000",
                    "tooltip": "Color of the empty image. Format: RRGGBB (hexadecimal)."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_MASONRY, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = (True, True, True)
    OUTPUT_IS_LIST = (False, True)
    RETURN_NAMES = ("image",)
    RETURN_TYPES = ("IMAGE",)

    def on_exec(self, **kwargs: dict):
        width: list[int] = normalize_input_list(kwargs.get("width"))
        height: list[int] = normalize_input_list(kwargs.get("height"))
        color: list[int] = normalize_input_list(kwargs.get("color"))
        
        nodes: list[dict] = []
        dataset: dict = { "nodes": nodes }


        if len(width) != len(height) or len(width) != len(color):
            raise ValueError("Width, height, and color lists must have the same length.")
        
        empty_images = []

        for w, h, c in zip(width, height, color):
            if not isinstance(c, str) or not re.fullmatch(r"[0-9A-Fa-f]{6}", c):
                raise ValueError("Color must be a hexadecimal string in the format RRGGBB.")
            
            rgb = hex_to_tuple(c)
            pil_image = Image.new("RGB", (w, h), rgb)
            empty_image_tensor = pil_to_tensor(pil_image)

            output_file, subfolder, filename = resolve_filepath(
                    filename_prefix="emptyimage",
                    image=empty_image_tensor,
            )
            pil_image.save(output_file, format="PNG")
            url = get_resource_url(subfolder, filename, "temp")

            nodes.append(create_masonry_node(filename, url, len(empty_images)))

            empty_images.append(empty_image_tensor)
        
        image_batch, image_list = normalize_output_image(empty_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}emptyimage", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (image_batch[0], image_list)

# region LF_ImagesEditingBreakpoint
class LF_ImagesEditingBreakpoint:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Batch of images."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_IMAGE_EDITOR, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True, False, True)
    RETURN_NAMES = ("image", "image_list", "orig_image", "orig_image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "IMAGE")

    def on_exec(self, **kwargs):
        def wait_for_editing_completion(json_file_path):
            while True:
                with open(json_file_path, 'r', encoding='utf-8') as json_file:
                    dataset = json.load(json_file)

                status_column: dict = next((col for col in dataset.get("columns", []) if col.get("id") == "status"), None)
                if status_column and status_column.get("title") == "completed":
                    break
                
                time.sleep(0.5)

            return dataset

        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))

        columns: list[dict] = []
        nodes: list[dict] = []
        dataset: dict = {"columns": columns, "nodes": nodes}

        for index, img in enumerate(image):
            pil_image = tensor_to_pil(img)
            output_file, subfolder, filename = resolve_filepath(
                filename_prefix="edit_breakpoint", 
                image=img
            )
            pil_image.save(output_file, format="PNG")
            url = get_resource_url(subfolder, filename, "temp")
            nodes.append(create_masonry_node(filename, url, index))

        temp_json_file: str = os.path.join(get_comfy_dir("temp"), f"{kwargs.get('node_id')}_edit_dataset.json")

        columns.append({"id": "path", "title": temp_json_file})
        columns.append({"id": "status", "title": "pending"})
        
        with open(temp_json_file, 'w', encoding='utf-8') as json_file:
            json.dump(dataset, json_file, ensure_ascii=False, indent=4)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}imageseditingbreakpoint", {
            "node": kwargs.get("node_id"),
            "value": temp_json_file,
        })

        dataset = wait_for_editing_completion(temp_json_file)

        edited_images = []
        for node in dataset["nodes"]:
            image_url = node.get("cells").get("lfImage").get("lfValue")
            
            parsed_url = urlparse(image_url)
            query_params = parse_qs(parsed_url.query)
            
            filename = query_params.get("filename", [None])[0]
            file_type = query_params.get("type", [None])[0]
            subfolder = query_params.get("subfolder", [None])[0]

            image_path = os.path.join(get_comfy_dir(file_type), subfolder or "", filename)

            pil_image = Image.open(image_path).convert("RGB")
            edited_images.append(pil_to_tensor(pil_image))

        batch_list, image_list = normalize_output_image(image)
        edited_batch_list, edited_image_list = normalize_output_image(edited_images)

        return (edited_batch_list[0], edited_image_list, batch_list[0], image_list)      
# endregion

# region LF_ImagesSlideshow
class LF_ImagesSlideshow:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_CAROUSEL, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_NODE = True
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))

        nodes: list[dict] = []
        dataset: dict = { "nodes": nodes }
        
        for index, img in enumerate(image):
            pil_image = tensor_to_pil(img)

            output_file, subfolder, filename = resolve_filepath(
                    filename_prefix="slide",
                    image=img,
            )
            pil_image.save(output_file, format="PNG")
            url = get_resource_url(subfolder, filename, "temp")

            nodes.append(create_masonry_node(filename, url, index))
        
        batch_list, image_list = normalize_output_image(image)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}imagesslideshow", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })
        
        return (batch_list[0], image_list)
# endregion

# region LF_ImageToSVG
class LF_ImageToSVG:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor to vectorize"
                }),
                "threshold": (Input.FLOAT, {
                    "default": 0.5, 
                    "min": 0.0, 
                    "max": 1.0, 
                    "step": 0.01,
                    "tooltip": "Binarization threshold for monochrome mode"
                }),
                "num_colors": (Input.INTEGER, {
                    "default": 2,
                    "min": 1,
                    "max": 16,
                    "step": 1,
                    "tooltip": "Number of colors for quantization (1 = binary)"
                }),
                "simplify_tol": (Input.FLOAT, {
                    "default": 2.0, 
                    "min": 0.0, 
                    "max": 10.0, 
                    "step": 0.1,
                    "tooltip": "Contour simplification tolerance (Douglas-Peucker)"
                }),
                "vector_mode": (["fill", "stroke", "both"], {
                    "default": "fill",
                    "tooltip": "Render mode: fill, stroke, or both."
                }),
                "stroke_width": (Input.FLOAT, {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 10.0,
                    "step": 0.1,
                    "tooltip": "Outline width"
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "IMAGE", "IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("svg", "svg_list", "image", "image_list", "palette", "palette_list")
    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True, False, True, False, True)

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        threshold: float = normalize_list_to_value(kwargs.get("threshold"))
        num_colors: int = normalize_list_to_value(kwargs.get("num_colors"))
        simplify_tol: float = normalize_list_to_value(kwargs.get("simplify_tol"))
        vector_mode: str = normalize_list_to_value(kwargs.get("vector_mode"))
        stroke_width: float = normalize_list_to_value(kwargs.get("stroke_width"))

        nodes: list[dict] = []
        dataset: dict = { "nodes": nodes }

        previews: list[torch.Tensor] = []
        svgs: list[str] = []
        palettes: list[dict] = []

        for index, img in enumerate(image):
            arr = tensor_to_numpy(img)
            svg_str, proc, palette = numpy_to_svg(arr, num_colors, threshold, simplify_tol, vector_mode, stroke_width)
            preview = numpy_to_tensor(proc)

            pil_image_original = tensor_to_pil(img)
            output_file_s, subfolder_s, filename_s = resolve_filepath(
                filename_prefix="svg_s",
                image=img,
            )
            pil_image_original.save(output_file_s, format="PNG")
            filename_s = get_resource_url(subfolder_s, filename_s, "temp")

            pil_image_blended = tensor_to_pil(preview)
            output_file_t, subfolder_t, filename_t = resolve_filepath(
                filename_prefix="svg_t",
                image=preview,
            )
            pil_image_blended.save(output_file_t, format="PNG")
            filename_t = get_resource_url(subfolder_t, filename_t, "temp")

            previews.append(preview)
            svgs.append(svg_str)
            palettes.append(palette)
            nodes.append(create_compare_node(filename_s, filename_t, index))

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}imagetosvg", {
            "node": kwargs.get("node_id"),
            "dataset": dataset
        })

        image_batch, image_list = normalize_output_image(previews)

        return (svgs[0], svgs, image_batch[0], image_list, palettes[0], palettes)
# endregion

# region LF_LUTApplication
class LF_LUTApplication:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Target image to which the LUT will be applied."
                }),
                "lut_dataset": (Input.JSON, {
                    "tooltip": "LUT dataset generated by LUT Generation Node."
                }),
                "strength" : (Input.FLOAT, {
                    "default": 0.5, "min": 0, "max": 1, "step": 0.05,
                    "tooltip": "The strength of the filter (from 0 - no effect, to 1 - full effect)."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_COMPARE, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_NODE = True
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image", []))
        strength: float = normalize_list_to_value(kwargs.get("strength"))
        lut_dataset: dict = normalize_json_input(kwargs.get("lut_dataset", {}))

        nodes: list[dict] = []
        dataset: dict = { "nodes": nodes }

        if len(image) != len(lut_dataset):
            raise ValueError("Number of target images does not match the number of LUT datasets.")

        adjusted_images: list[torch.Tensor] = []
        for index, img in enumerate(image):
            lut = lut_dataset.get(f"Image #{index + 1}", None)
            if not lut:
                raise ValueError(f"LUT for Image #{index + 1} not found in dataset.")

            r = np.array([int(node["cells"][RED_CHANNEL_ID]["value"]) for node in lut["nodes"]], dtype=np.uint8)
            g = np.array([int(node["cells"][GREEN_CHANNEL_ID]["value"]) for node in lut["nodes"]], dtype=np.uint8)
            b = np.array([int(node["cells"][BLUE_CHANNEL_ID]["value"]) for node in lut["nodes"]], dtype=np.uint8)

            image_np = tensor_to_numpy(img)
            image_np = image_np.astype(np.uint8)
            adjusted_np = np.zeros_like(image_np)

            adjusted_np[:, :, 0] = r[image_np[:, :, 0]]
            adjusted_np[:, :, 1] = g[image_np[:, :, 1]]
            adjusted_np[:, :, 2] = b[image_np[:, :, 2]]

            image_np_float = image_np.astype(np.float32)
            adjusted_np_float = adjusted_np.astype(np.float32)

            blended_np = (1 - strength) * image_np_float + strength * adjusted_np_float
            blended_np = np.clip(blended_np, 0, 255).astype(np.uint8)

            adjusted_tensor = numpy_to_tensor(blended_np)

            pil_image_original = tensor_to_pil(img)
            output_file_s, subfolder_s, filename_s = resolve_filepath(
                filename_prefix="lut_s",
                image=img,
            )
            pil_image_original.save(output_file_s, format="PNG")
            filename_s = get_resource_url(subfolder_s, filename_s, "temp")

            pil_image_blended = tensor_to_pil(adjusted_tensor)
            output_file_t, subfolder_t, filename_t = resolve_filepath(
                filename_prefix="lut_t",
                image=adjusted_tensor,
            )
            pil_image_blended.save(output_file_t, format="PNG")
            filename_t = get_resource_url(subfolder_t, filename_t, "temp")

            adjusted_images.append(adjusted_tensor)
            nodes.append(create_compare_node(filename_s, filename_t, index))

        image_batch, image_list = normalize_output_image(adjusted_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}lutapplication", {
            "node": kwargs.get("node_id"),
            "dataset": dataset
        })

        return (image_batch[0], image_list)
# endregion

# region LF_MultipleImageResizeForWeb
class LF_MultipleImageResizeForWeb:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "type": "IMAGE", 
                    "tooltip": "List of images to process."
                }),
                "file_name": (Input.STRING, {
                    "forceInput": True, 
                    "tooltip": "Corresponding list of file names for the images."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_TREE, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = (True, True)
    OUTPUT_IS_LIST = (False, True, False, True, True, False)
    RETURN_NAMES = ("image", "image_list", "name", "name_list", "names_with_dir", "dataset")
    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING", "STRING", "STRING", "JSON")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        file_name: list[str] = normalize_input_list(kwargs.get("file_name"))

        nodes: list[dict] = []
        dataset: dict = { "nodes": nodes }

        output_file_names: list[str] = []
        output_file_names_with_dir: list[str] = []
        output_images: list[torch.Tensor] = []
        resolutions: list[int] = [256, 320, 512, 640, 1024, 1280, 2048, 2560]

        for index, img in enumerate(image):
            f_name = file_name[index]
            split_name = f_name.rsplit('.', 1)
            if len(split_name) == 2:
                base_name, original_extension = split_name
                original_extension.lower()
            else:
                base_name = split_name[0]
                original_extension = ""

            img = tensor_to_pil(img)

            img_byte_arr = io.BytesIO()

            try:
                image_format = 'PNG' if original_extension not in ['jpeg', 'jpg', 'png', 'webp'] else original_extension.upper()
                img.save(img_byte_arr, format=image_format)
            except KeyError:
                print(f"Unknown format '{original_extension}', falling back to PNG.")
                img.save(img_byte_arr, format='PNG')

            img_byte_arr = img_byte_arr.getvalue()

            output_images.append(pil_to_tensor(img)) 
            output_file_names.append(f"{base_name}")
            output_file_names_with_dir.append(f"HD/{base_name}")

            children:list[dict] = []
            rootNode: dict = {
                "children": children,
                "id": base_name,
                "value": base_name
            }

            for r in resolutions:
                if img.width > img.height:
                    new_width = r
                    new_height = int(img.height * r / img.width)
                else:
                    new_height = r
                    new_width = int(img.width * r / img.height)

                resized_image = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                img_byte_arr = io.BytesIO()
                resized_image.save(img_byte_arr, format='WEBP', quality=60)
                img_byte_arr = img_byte_arr.getvalue()

                output_images.append(pil_to_tensor(resized_image))
                output_file_names.append(f"{r}w_{base_name}")
                output_file_names_with_dir.append(f"{r}w/{r}w_{base_name}")

                childNode = {
                    "id": f"{r}w_{base_name}",
                    "value": f"{r}w_{base_name}"
                }
                children.append(childNode)

            nodes.append(rootNode)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}multipleimageresizeforweb", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        image_batch, image_list = normalize_output_image(output_images)

        return (image_batch[0], image_list, output_file_names, output_file_names, output_file_names_with_dir, dataset)
# endregion

# region LF_ResizeImageByEdge
class LF_ResizeImageByEdge:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "longest_edge": (Input.BOOLEAN, {
                    "default": False, 
                    "tooltip": "Resizes the image by the longest side if set to True. Otherwise, resizes by the shortest side."
                }),
                "new_size": (Input.INTEGER, {
                    "default": 1024, 
                    "tooltip": "The size of the longest edge of the output image."
                }),
                "resize_method": (RESAMPLERS, {
                    "default": "bicubic", 
                    "tooltip": "Method to resize the image."
                })
            },
            "optional": {
                "ui_widget": (Input.LF_TREE, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = (True, False, True, False, False)
    OUTPUT_IS_LIST = (False, True, False)
    RETURN_NAMES = ("image", "image_list", "count")
    RETURN_TYPES = ("IMAGE", "IMAGE", "INT")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        longest_edge: bool = normalize_list_to_value(kwargs.get("longest_edge"))
        new_size: list[int] = normalize_input_list(kwargs.get("new_size"))
        resize_method: str = normalize_list_to_value(kwargs.get("resize_method"))

        nodes: list[dict] = []
        root: dict = { "children": nodes, "icon":"info-hexagon", "id": "", "value": "" }
        dataset: dict = { "nodes": [root] }

        original_heights: list[int] = []
        original_widths: list[int] = []
        heights: list[int] = []
        widths: list[int] = []

        resized_images: list[torch.Tensor] = []

        for index, img in enumerate(image):
            n_size = normalize_list_item(new_size, index)

            original_height, original_width = img.shape[1], img.shape[2]
            original_heights.append(original_height)
            original_widths.append(original_width)

            resized_img = resize_image(img, resize_method, longest_edge, n_size)
            resized_images.append(resized_img)

            new_height, new_width = resized_img.shape[1], resized_img.shape[2]
            heights.append(new_height)
            widths.append(new_width)

            nodes.append(create_resize_node(original_height, original_width, new_height, new_width, index))
            
        num_resized = len(resized_images)
        summary_message = f"Resized {num_resized} {'image' if num_resized == 1 else 'images'}"
        root["id"] = summary_message
        root["value"] = summary_message

        image_batch, image_list = normalize_output_image(resized_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}resizeimagebyedge", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (image_batch[0], image_list, num_resized)
# endregion

# region LF_ResizeImageToDimension
class LF_ResizeImageToDimension:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "height": (Input.INTEGER, {
                    "default": 1216, 
                    "tooltip": "The target height for the output image."
                }),
                "width": (Input.INTEGER, {
                    "default": 832, 
                    "tooltip": "The target width for the output image."
                }),
                "resize_method": (RESAMPLERS, {
                    "default": "bicubic", 
                    "tooltip": "Method to resize the image."
                }),
                "resize_mode": (["crop", "pad"], {
                    "default": "crop", 
                    "tooltip": "Choose whether to crop or pad when resizing."
                }),
                "pad_color": (Input.STRING, {
                    "default": "000000", 
                    "tooltip": "Color to use for padding if 'pad' mode is selected (hexadecimal)."
                })
            },
            "optional": {
                "ui_widget": (Input.LF_TREE, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = (True, True, True, False, False, False, False)
    OUTPUT_IS_LIST = (False, True, False)
    RETURN_NAMES = ("image", "image_list", "count")
    RETURN_TYPES = ("IMAGE", "IMAGE", "INT")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        height: list[int] = normalize_input_list(kwargs.get("height"))
        width: list[int] = normalize_input_list(kwargs.get("width"))
        resize_method: str = normalize_list_to_value(kwargs.get("resize_method"))
        resize_mode: str = normalize_list_to_value(kwargs.get("resize_mode"))
        pad_color: str = normalize_list_to_value(kwargs.get("pad_color"))

        nodes: list[dict] = []
        root: dict = { "children": nodes, "icon":"info-hexagon", "id": "", "value": "" }
        dataset: dict = { "nodes": [root] }

        original_heights: list[int] = []
        original_widths: list[int] = []
        heights: list[int] = []
        widths: list[int] = []

        resized_images: list[torch.Tensor] = []

        for index, img in enumerate(image):
            h: int = normalize_list_item(height, index)
            w: int = normalize_list_item(width, index)

            original_height, original_width = img.shape[1], img.shape[2]
            original_heights.append(original_height)
            original_widths.append(original_width)

            resized_img = resize_and_crop_image(img, resize_method, h, w, resize_mode, pad_color)
            resized_images.append(resized_img)

            new_height, new_width = resized_img.shape[1], resized_img.shape[2]
            heights.append(new_height)
            widths.append(new_width)

            nodes.append(create_resize_node(original_height, original_width, new_height, new_width, index))
        
        num_resized = len(resized_images)
        summary_message = f"Resized {num_resized} {'image' if num_resized == 1 else 'images'}"
        root["id"] = summary_message
        root["value"] = summary_message

        image_batch, image_list = normalize_output_image(resized_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}resizeimagetodimension", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (image_batch[0], image_list, num_resized)
# endregion

# region LF_ResizeImageToSquare
class LF_ResizeImageToSquare:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
                "square_size": (Input.INTEGER, {
                    "default": 1024, 
                    "tooltip": "The length of the square's edge."
                }),
                "resize_method": (RESAMPLERS, {
                    "default": "bicubic", 
                    "tooltip": "Resampling method for resizing."
                }),
                "crop_position": (["top", "bottom", "left", "right", "center"], {
                    "default": "center", 
                    "tooltip": "Where to crop the image."
                })
            },
            "optional": {
                "ui_widget": (Input.LF_TREE, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = (True, True, False, False, False)
    OUTPUT_IS_LIST = (False, True, False)
    RETURN_NAMES = ("image", "image_list", "count")
    RETURN_TYPES = ("IMAGE", "IMAGE", "INT")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
        square_size: list[int] = normalize_input_list(kwargs.get("square_size"))
        resize_method: str = normalize_list_to_value(kwargs.get("resize_method"))
        crop_position: str = normalize_list_to_value(kwargs.get("crop_position"))

        nodes: list[dict] = []
        root: dict = { "children": nodes, "icon":"info-hexagon", "id": "", "value": "" }
        dataset: dict = { "nodes": [root] }

        original_heights: list[int] = []
        original_widths: list[int] = []
        heights: list[int] = []
        widths: list[int] = []

        resized_images: list[torch.Tensor] = []

        for index, img in enumerate(image):
            s: int = normalize_list_item(square_size, index)

            original_height, original_width = img.shape[1], img.shape[2]
            original_heights.append(original_height)
            original_widths.append(original_width)

            resized_img = resize_to_square(img, s, resize_method, crop_position)
            resized_images.append(resized_img)

            new_height, new_width = resized_img.shape[1], resized_img.shape[2]
            heights.append(new_height)
            widths.append(new_width)

            nodes.append(create_resize_node(original_height, original_width, new_height, new_width, index))

        num_resized = len(resized_images)
        summary_message = f"Resized {num_resized} {'image' if num_resized == 1 else 'images'}"
        root["id"] = summary_message
        root["value"] = summary_message

        image_batch, image_list = normalize_output_image(resized_images)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}resizeimagetosquare", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })

        return (image_batch[0], image_list, num_resized)
# endregion

# region LF_ViewImages
class LF_ViewImages:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "image": (Input.IMAGE, {
                    "tooltip": "Input image tensor or a list of image tensors."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_MASONRY, {
                    "default": {}
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_NODE = True
    RETURN_NAMES = ("image", "image_list")
    RETURN_TYPES = ("IMAGE", "IMAGE")

    def on_exec(self, **kwargs: dict):
        image: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))

        nodes: list[dict] = []
        dataset: dict = { "nodes": nodes }
        
        for index, img in enumerate(image):
            pil_image = tensor_to_pil(img)

            output_file, subfolder, filename = resolve_filepath(
                    filename_prefix="view",
                    image=img,
            )
            pil_image.save(output_file, format="PNG")
            url = get_resource_url(subfolder, filename, "temp")

            nodes.append(create_masonry_node(filename, url, index))
        
        batch_list, image_list = normalize_output_image(image)

        PromptServer.instance.send_sync(f"{EVENT_PREFIX}viewimages", {
            "node": kwargs.get("node_id"),
            "dataset": dataset,
        })
        
        return (batch_list[0], image_list)
# endregion

NODE_CLASS_MAPPINGS = {
    "LF_BlobToImage": LF_BlobToImage,
    "LF_BlurImages": LF_BlurImages,
    "LF_CompareImages": LF_CompareImages,
    "LF_CreateMask": LF_CreateMask,
    "LF_EmptyImage": LF_EmptyImage,
    "LF_ImagesEditingBreakpoint": LF_ImagesEditingBreakpoint,
    "LF_ImagesSlideshow": LF_ImagesSlideshow,
    "LF_ImageToSVG": LF_ImageToSVG,
    "LF_LUTApplication": LF_LUTApplication,
    "LF_MultipleImageResizeForWeb": LF_MultipleImageResizeForWeb,
    "LF_ResizeImageToDimension": LF_ResizeImageToDimension,
    "LF_ResizeImageToSquare": LF_ResizeImageToSquare,
    "LF_ResizeImageByEdge": LF_ResizeImageByEdge,
    "LF_ViewImages": LF_ViewImages,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_BlobToImage": "Blob to Image",
    "LF_BlurImages": "Blur images",
    "LF_CompareImages": "Compare images",
    "LF_CreateMask": "Create Mask",
    "LF_EmptyImage": "Empty image",
    "LF_ImagesEditingBreakpoint": "Images editing breakpoint",
    "LF_ImagesSlideshow": "Images slideshow",
    "LF_ImageToSVG": "Image to SVG",
    "LF_LUTApplication": "LUT Application (filter)",
    "LF_MultipleImageResizeForWeb": "Multiple image resize for Web",
    "LF_ResizeImageToDimension": "Resize image to dimension",
    "LF_ResizeImageToSquare": "Resize image to square",
    "LF_ResizeImageByEdge": "Resize image by edge",
    "LF_ViewImages": "View images",
}