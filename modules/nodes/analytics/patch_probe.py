"""Teach a linear probe on encoded patches, check it one group held out at a time, and paint where frames read as each label."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_output_image
from ...utils.helpers.torch.patch_probe import CROPS, read_patch_probe
from ...utils.helpers.ui import create_cached_compare_node


class LF_PatchProbe:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "teach": (Input.CLIP_VISION_OUTPUT, {"tooltip": "Patch tokens of the teaching images, one batch (Vision Patch Encode)."}),
                "labels": (Input.STRING, {"default": "0,1", "tooltip": "0 or 1 per teaching image, comma-separated; the map paints the probability of 1."}),
                "groups": (Input.STRING, {"default": "a,a,b,b", "tooltip": "A group per teaching image (a scene, a pair of its shots); each is held out once while the others teach."}),
                "frames": (Input.CLIP_VISION_OUTPUT, {"tooltip": "Patch tokens of the frames to read, encoded with the same model and size."}),
                "frame_images": (Input.IMAGE, {"tooltip": "The same frames, one batch at any one size: the maps are painted over them."}),
                "crop": (list(CROPS), {"tooltip": "The crop both encodes used: none stretches the whole image, center keeps the centred square."}),
                "l2": (Input.FLOAT, {"default": 0.01, "min": 0.0, "max": 100.0, "step": 0.001, "tooltip": "L2 penalty on the probe's weights over standardized tokens: higher leans less on any one feature."}),
            },
            "optional": {
                "frame_groups": (Input.STRING, {"default": "", "tooltip": "A teaching group per frame, comma-separated, read by the probe that held it out; empty entries for frames none of them saw."}),
                "frame_masks": (Input.MASK, {"tooltip": "One mask, or one per frame, at the frames' size: each frame reports its mean probability inside."}),
                "names": (Input.STRING, {"default": "0,1", "tooltip": "Names of label 0 and label 1, for the report and the titles."}),
                "ui_widget": (Input.LF_COMPARE, {"default": {}}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    RETURN_TYPES = (Input.JSON, Input.IMAGE, Input.MASK)
    RETURN_NAMES = ("report", "painted", "probability")
    OUTPUT_IS_LIST = (False, False, False)
    OUTPUT_TOOLTIPS = (
        "lf.patch-probe.v1: each held-out group's accuracy, AUC and image means, and each frame's mean probability and mean logit of label 1 with its patch grid of logits.",
        "Each frame in grey, orange where it reads as label 1 and blue as label 0, by how sure the probe is.",
        "The probability of label 1 per pixel, one mask per frame.",
    )

    def on_exec(self, teach=None, labels="", groups="", frames=None, frame_images=None, crop="none", l2=0.01,
                frame_groups="", frame_masks=None, names="0,1", **kwargs):
        report, painted, probability = read_patch_probe(
            teach, labels, groups, frames, frame_images, crop=crop, l2=float(l2), frame_groups=frame_groups,
            frame_masks=frame_masks, names=names)
        negative, positive = report["names"]
        held = report["held_out"]
        converged = report["converged"]["all_groups"] and all(fold["converged"] for fold in held["folds"])
        nodes = []
        for row in report["frames"]:
            index = row["index"]
            title = f"{positive} {row['mean_probability']:.2f}, logit {row['mean_logit']:+.2f} ({row['read_by']})"
            if row["mask_probability"] is not None:
                title += f" | in mask {row['mask_probability']:.2f}"
            if index == 0 and held["auc"] is not None:
                title += f" | held out: AUC {held['auc']:.2f}, ordered {held['ordered']}"
            if index == 0 and not converged:
                title += (f" | NOT CONVERGED: held out {report['converged']['held_out']}, "
                          f"all groups {report['converged']['all_groups']} (raise l2)")
            nodes.append(create_cached_compare_node(frame_images[index:index + 1], painted[index:index + 1],
                                                    index=index, title=title))
        # The patch grids travel on the socket; the UI keeps the summary.
        summary = {**report, "frames": [{key: value for key, value in row.items() if key != "logits"}
                                        for row in report["frames"]]}
        payload = {"dataset": {"nodes": nodes}, "report": summary}
        safe_send_sync("patchprobe", payload, kwargs.get("node_id"))
        return {"ui": {"lf_output": [payload]},
                "result": (report, normalize_output_image(list(painted.unsqueeze(1)))[0][0], probability)}


NODE_CLASS_MAPPINGS = {"LF_PatchProbe": LF_PatchProbe}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_PatchProbe": "Patch probe"}
