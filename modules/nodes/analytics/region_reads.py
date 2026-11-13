"""Reads of one region of a render against another: a face over its surroundings, an outline over its interior."""
import numpy as np
import torch

from . import CATEGORY
from ..image.side_by_side import compose_side_by_side
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.detection.build_overlay import region_mask_preview
from ...utils.helpers.logic import normalize_output_image
from ...utils.helpers.tone import DEFAULT_READS, as_rgb, one_image, evaluate_reads, parse_reads
from ...utils.helpers.tone.region_reads import READS_SCHEMA, region_dict
from ...utils.helpers.ui import create_cached_compare_node



class LF_RegionReads:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (Input.IMAGE, {"tooltip": "Exactly one display-referred image."}),
                "masks": (Input.MASK, {"tooltip": "A region set at the image's size (Text Region Masks, Face Zones)."}),
                "metadata": (Input.JSON, {"tooltip": "The region set's lf.text-region-masks.v1 document."}),
                "reads": (Input.STRING, {"default": DEFAULT_READS, "multiline": True, "tooltip": "One read per line, 'name: A / B'. Terms: a region, frame, ring(x), edge(x), inside(x), near(x) (x a region or a union, face|hair), facing<v, facing>v; operators & | -."}),
                "ring_inner": (Input.INTEGER, {"default": 12, "min": 0, "max": 4096, "tooltip": "ring(x) starts this many pixels outside x; near(x) reaches this far."}),
                "ring_outer": (Input.INTEGER, {"default": 40, "min": 1, "max": 4096, "tooltip": "ring(x) ends this many pixels outside x."}),
                "edge_px": (Input.INTEGER, {"default": 4, "min": 1, "max": 1024, "tooltip": "edge(x) is x's outermost pixels to this depth."}),
                "inside_px": (Input.INTEGER, {"default": 8, "min": 0, "max": 1024, "tooltip": "inside(x) is x without its pixels to this depth."}),
                "min_pixels": (Input.INTEGER, {"default": 200, "min": 1, "max": 1_000_000, "tooltip": "A side with fewer pixels reports a warning instead of numbers."}),
            },
            "optional": {
                "masks_2": (Input.MASK, {"tooltip": "A second region set at the same size; its IDs must differ from the first's."}),
                "metadata_2": (Input.JSON, {"tooltip": "The second set's lf.text-region-masks.v1 document."}),
                "facing": (Input.IMAGE, {"tooltip": "A facing map (N.V: 1 faces the viewer) in its red channel, for facing< and facing> terms."}),
                "facing_gamma": (Input.FLOAT, {"default": 1.0, "min": 0.1, "max": 4.0, "step": 0.1, "tooltip": "Exponent decoding the facing map's stored values (2.2 for a display-encoded map)."}),
                "ui_widget": (Input.LF_COMPARE, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    RETURN_TYPES = (Input.JSON, Input.IMAGE, Input.IMAGE)
    RETURN_NAMES = ("report", "preview", "preview_list")
    OUTPUT_IS_LIST = (False, False, True)
    OUTPUT_TOOLTIPS = (
        "lf.region-reads.v1: per read, both sides' pixel count, mean and median luma, saturation and red over blue, and A over B.",
        "Per read, side A and side B isolated side by side.",
        "The same previews as a list.",
    )

    def on_exec(self, image=None, masks=None, metadata=None, reads=DEFAULT_READS, ring_inner=12, ring_outer=40,
                edge_px=4, inside_px=8, min_pixels=200, masks_2=None, metadata_2=None, facing=None,
                facing_gamma=1.0, **kwargs):
        source = one_image(image, "image")
        rgb = as_rgb(source, "image")
        shape = rgb.shape[:2]
        regions = region_dict(masks, metadata, shape, "masks")
        if masks_2 is not None or metadata_2 is not None:
            if masks_2 is None or metadata_2 is None:
                raise ValueError("masks_2 and metadata_2 come together.")
            second = region_dict(masks_2, metadata_2, shape, "masks_2")
            shared = sorted(set(regions) & set(second))
            if shared:
                raise ValueError(f"region IDs appear in both sets: {', '.join(shared)}.")
            regions.update(second)
        facing_map = None
        if facing is not None:
            facing_map = as_rgb(one_image(facing, "facing"), "facing")[..., 0] ** float(facing_gamma)
        rows, sides = evaluate_reads(rgb, regions, parse_reads(reads), facing=facing_map,
                                     ring_inner=int(ring_inner), ring_outer=int(ring_outer), edge_px=int(edge_px),
                                     inside_px=int(inside_px), min_pixels=int(min_pixels))
        report = {"schema": READS_SCHEMA, "size": [shape[1], shape[0]], "regions": sorted(regions), "reads": rows,
                  "parameters": {"ring_inner": int(ring_inner), "ring_outer": int(ring_outer), "edge_px": int(edge_px),
                                 "inside_px": int(inside_px), "min_pixels": int(min_pixels),
                                 "facing_gamma": float(facing_gamma) if facing is not None else None}}
        previews, nodes = [], []
        for index, (row, (a, b)) in enumerate(zip(rows, sides)):
            first = region_mask_preview(source, torch.from_numpy(a.astype(np.float32)), isolate=True)
            second = region_mask_preview(source, torch.from_numpy(b.astype(np.float32)), isolate=True)
            previews.append(compose_side_by_side(first, second, gap_px=8))
            ratio, saturation = row["luma_ratio"], row["saturation_ratio"]
            label = f"{row['name']}: " + (f"luma x{ratio:.3f}" if ratio is not None
                                          else f"N/A | {row.get('warning', '')}")
            if saturation is not None:
                label += f" | saturation x{saturation:.3f}"
            nodes.append(create_cached_compare_node(first, second, index=index, title=label))
        payload = {"dataset": {"nodes": nodes}, "report": report}
        safe_send_sync("regionreads", payload, kwargs.get("node_id"))
        batches, preview_list = normalize_output_image(previews)
        return {"ui": {"lf_output": [payload]}, "result": (report, batches[0], preview_list)}


NODE_CLASS_MAPPINGS = {"LF_RegionReads": LF_RegionReads}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_RegionReads": "Region reads"}
