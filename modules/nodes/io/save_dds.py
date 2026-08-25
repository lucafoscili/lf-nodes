from __future__ import annotations

from pathlib import Path

import torch

from . import CATEGORY
from .dds_codec import (
    DDS_RECEIPT_SCHEMA,
    DDSFileCustody,
    DDSOutputError,
    MIP_POLICIES,
    PIXEL_FORMATS,
    encode_dds,
    normalize_tensor_image,
    write_dds_atomic,
)
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import get_comfy_dir, resolve_filepath, safe_send_sync
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value


class LF_SaveDDS:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (
                    Input.IMAGE,
                    {"tooltip": "Input RGB or RGBA image batch to encode as DDS."},
                ),
                "filename_prefix": (
                    Input.STRING,
                    {
                        "default": "LF_Nodes/DDS",
                        "tooltip": "Output-relative path and filename prefix. Files are always saved with .dds and a collision-safe counter.",
                    },
                ),
                "pixel_format": (
                    list(PIXEL_FORMATS),
                    {
                        "default": "RGBA32",
                        "tooltip": "RGB24/RGBA32 are uncompressed 8-bit channels; BC1/BC3 are legacy DXT1/DXT5 block compression.",
                    },
                ),
                "mip_policy": (
                    list(MIP_POLICIES),
                    {
                        "default": "none",
                        "tooltip": "Save only the source level or a complete floor-halved chain down to 1x1.",
                    },
                ),
            },
            "optional": {
                "ui_widget": (Input.LF_TREE, {"default": {}}),
            },
            "hidden": {
                "node_id": "UNIQUE_ID",
            },
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_IS_LIST = (True, False)
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "Ordered output-relative DDS filenames.",
        "Deterministic lf.dds.receipt.v1 receipt.",
    )
    RETURN_NAMES = ("file_names", "receipt")
    RETURN_TYPES = (Input.STRING, Input.JSON)

    def on_exec(self, **kwargs: dict):
        custody_tokens: list[DDSFileCustody] = []
        try:
            try:
                images: list[torch.Tensor] = normalize_input_image(kwargs.get("image"))
            except (TypeError, ValueError) as error:
                raise DDSOutputError(
                    "invalid_dimensions",
                    "DDS input batch structure is invalid.",
                    {"stage": "batch_normalization"},
                ) from error

            if not images:
                raise DDSOutputError(
                    "invalid_dimensions",
                    "DDS input batch must contain at least one image.",
                )

            filename_prefix = normalize_list_to_value(kwargs.get("filename_prefix"))
            pixel_format = str(normalize_list_to_value(kwargs.get("pixel_format")))
            mip_policy = str(normalize_list_to_value(kwargs.get("mip_policy")))

            encoded_batch: list[tuple[bytes, dict]] = []
            for image in images:
                pixels = normalize_tensor_image(image)
                encoded_batch.append(encode_dds(pixels, pixel_format, mip_policy))

            output_root = get_comfy_dir("output")
            file_names: list[str] = []
            receipt_items: list[dict] = []

            for index, (data, item_receipt) in enumerate(encoded_batch):
                output_file, subfolder, filename = resolve_filepath(
                    filename_prefix=filename_prefix,
                    base_output_path=output_root,
                    add_timestamp=False,
                    extension="dds",
                    add_counter=True,
                )
                output_path = Path(output_file)
                custody = write_dds_atomic(
                    output_path,
                    data,
                    item_receipt,
                    retain_custody=True,
                )
                if custody is None:
                    raise DDSOutputError(
                        "encode_failure",
                        "DDS publication did not return a custody proof.",
                        {"stage": "batch_publication"},
                    )
                custody_tokens.append(custody)

                relative_name = f"{subfolder}/{filename}" if subfolder else filename
                file_names.append(relative_name.replace("\\", "/"))
                receipt_items.append({"index": index, **item_receipt})

            receipt = {
                "schema": DDS_RECEIPT_SCHEMA,
                "files": receipt_items,
            }

            nodes: list[dict] = []
            root = {
                "children": nodes,
                "icon": "check",
                "id": "root",
                "value": f"Saved and verified {len(file_names)} DDS file(s).",
            }
            dataset = {"nodes": [root]}
            for file_name, item in zip(file_names, receipt_items):
                nodes.append(
                    {
                        "description": item["sha256"],
                        "icon": "file",
                        "id": file_name,
                        "value": file_name,
                    }
                )

            safe_send_sync("savedds", {"dataset": dataset}, kwargs.get("node_id"))
            for custody in custody_tokens:
                custody.commit()

            return {
                "ui": {
                    "lf_output": [
                        {
                            "dataset": dataset,
                            "file_names": file_names,
                            "receipt": receipt,
                        }
                    ]
                },
                "result": (file_names, receipt),
            }
        except DDSOutputError:
            for custody in custody_tokens:
                custody.rollback()
            raise
        except Exception as error:
            for custody in custody_tokens:
                custody.rollback()
            raise DDSOutputError(
                "encode_failure",
                "DDS node execution failed.",
                {"stage": "node_execution"},
            ) from error


NODE_CLASS_MAPPINGS = {
    "LF_SaveDDS": LF_SaveDDS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SaveDDS": "Save DDS",
}
