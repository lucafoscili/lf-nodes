#!/usr/bin/env python3
"""Append the reading nodes' specimens to the canonical Titanic workflow.

Run from any directory: python -I scripts/quality/update_titanic_readers_coverage.py
Use --check to inspect reproducibility without writing. The maintainer's user
workflow is never read or written. Existing canonical nodes/links keep their IDs.

The specimens read the texture case's before and after (the pinned stock example
from node 654 and Masked Lab grade 660's graded central square, mask 657):

- ``cpu.inspection``: Image diff, Grade split and Luma ratio map of before
  against after, Region measure of both through a list, and Plot chart's bars
  of the measure.
- ``cpu.tone-readers``: the square and the top band as a named region set over
  the example, Tone profile of before and of after against it, and Region reads
  of the square against the band.
- ``model.face-zones``: Face zones of both generated portraits (node 676) and
  Region reads of their zones, on InsightFace's installed pack.
- ``model.patch-probe``: DINOv3 (loader 649) patch tokens of the example and its
  graded copy, mirrored for a second group, teach a probe that paints where the
  frames read as graded.
- ``model.intrinsic-layers``: the example split into albedo, diffuse shading and
  residual by the installed release.
- ``model.speech``: two designed voices, the first converted onto the second,
  and the match of the converted line against that voice and its text.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import titanic_append as titanic  # noqa: E402

START_NODE = 678
START_LINK = 1318
ORDER = 438
EXAMPLE, GRADED, SQUARE_MASK, BAND_MASK = 654, 660, 657, 659
PORTRAITS, DINO = 676, 649
SIZE = 768
BOXES = "square=192,192,576,576\nband=0,0,768,192"
READS = "square / band\nedge(square) / inside(square)"
FACE_READS = "under_eyes / cheeks\nfolds / cheeks"
LINE = "The morning train was late, so we walked along the river instead."
TARGET_LINE = "A second voice reads a different line for the converter to aim at."
GROUP_COLOR = "#3f789e"
# Sections stack downward from here, right of every older specimen; the gap leaves room for the Vue renderer,
# whose nodes can grow past their saved size to fit a widget.
LEFT, TOP, SECTION_GAP, GAP = 19300, -4700, 480, 400
# Roomy enough that each result widget reads at scale 1; the rest keep the specimen's default.
COMPARE, CHART, TREE = (540, 780), (640, 700), (520, 560)
SIZES = {
    **dict.fromkeys((678, 679, 680, 689, 692, 693, 694, 698, 700, 701, 702), COMPARE),
    681: (420, 480), 682: CHART, 683: (640, 860), 686: (420, 480), 688: (420, 360), 690: TREE, 691: TREE,
    703: (480, 720), 704: (480, 720), 705: (480, 440), 706: (560, 700), 707: (480, 560),
}

IMAGES = (("image", "IMAGE", False), ("image_list", "IMAGE", True))
REGION_SET = (("masks", "MASK", False), ("metadata", "JSON", False), ("mask_list", "MASK", True))
READS_OUT = (("report", "JSON", False), ("preview", "IMAGE", False), ("preview_list", "IMAGE", True))
READS_IN = [("image", "IMAGE"), ("masks", "MASK"), ("metadata", "JSON"), ("reads", "STRING"),
            ("ring_inner", "INT"), ("ring_outer", "INT"), ("edge_px", "INT"), ("inside_px", "INT"),
            ("min_pixels", "INT"), ("masks_2", "MASK"), ("metadata_2", "JSON"), ("facing", "IMAGE"),
            ("facing_gamma", "FLOAT"), ("ui_widget", "LF_COMPARE")]
READS_SETTINGS = {"ring_inner": 12, "ring_outer": 40, "edge_px": 4, "inside_px": 8, "min_pixels": 200,
                  "facing_gamma": 1, "ui_widget": {}}
SPEAKER = ("k2-fsa/OmniVoice", "c5fdb5ccb189668d56333f77ba2629f4cd7535f4")
CONVERTER = ("ResembleAI/chatterbox", "5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18")
SPEAKER_ENCODER = ("microsoft/wavlm-base-plus-sv", "feb593a6c23c1cc3d9510425c29b0a14d2b07b1e")
RECOGNIZER = ("openai/whisper-large-v3-turbo", "41f01f3fe87f28c78e2fbf8b568835947dd65ed9")


def _compare(previews, live, **named):
    return {"minimumPreviewCount": previews, "minimumLivePreviewCount": live, "previewStorageType": "input",
            "requiredNamedValues": named}


CASES = [
    {"id": "cpu.inspection",
     "title": "Image diff, grade split, luma ratio, region measure and plot chart of the stock example's grade",
     "resourceClass": "cpu", "targets": [678, 679, 680, 681, 682, 683], "timeoutSeconds": 300,
     "bindings": {"fixtureImageSourceNodeIds": [EXAMPLE]},
     "execution": {"requiredNodeIds": [678, 679, 680, 682, 683], "forbiddenCachedNodeIds": [678, 679, 680, 682, 683]},
     "expect": {
         "678": _compare(2, 1, schema="lf.image-diff.v1", label="graded", pixels=SIZE * SIZE),
         "679": _compare(4, 2, schema="lf.grade-split.v1"),
         "680": _compare(2, 1, schema="lf.luma-ratio-map.v1"),
         "682": {"minimumChartTabs": 10, "requiredNamedValues": {"title": "square", "value": "before"}},
         "683": {"minimumChartTabs": 1, "requiredNamedValues": {"title": "band", "value": "after"}},
     }},
    {"id": "cpu.tone-readers",
     "title": "Tone profile and region reads of the stock example's square and top band, before and after the grade",
     "resourceClass": "cpu", "targets": [686, 688, 690, 691, 692], "timeoutSeconds": 300,
     "bindings": {"fixtureImageSourceNodeIds": [EXAMPLE]},
     "execution": {"requiredNodeIds": [689, 690, 691, 692], "forbiddenCachedNodeIds": [689, 690, 691, 692]},
     "expect": {
         "689": _compare(4, 2, schema="lf.text-region-masks.v1", empty=False),
         "690": {"minimumLivePreviewCount": 3, "requiredNamedValues": {
             "value": "square: mean 0.780 | shade 0.651 | fill 0.791 | R/B 1.00 | sat 0.48"}},
         "691": {"minimumLivePreviewCount": 3, "requiredNamedValues": {
             "value": "square: mean 0.717 | shade 0.573 | fill 0.716 | R/B 0.75 | sat 0.42"}},
         "692": _compare(4, 2, schema="lf.region-reads.v1", name="square / band"),
     }},
    {"id": "model.face-zones",
     "title": "Face zones of both generated portraits and region reads of their zones",
     "resourceClass": "model-cpu", "targets": [694], "timeoutSeconds": 300,
     "bindings": {"fixtureFaceSourceNodeIds": [PORTRAITS]},
     "execution": {"requiredNodeIds": [693, 694], "forbiddenCachedNodeIds": [693, 694]},
     "expect": {
         "693": _compare(12, 6, schema="lf.face-zones.v1", model_pack="antelopev2", id="under_eyes"),
         "694": _compare(4, 2, schema="lf.region-reads.v1", name="under_eyes / cheeks"),
     }},
    {"id": "model.patch-probe",
     "title": "DINOv3 patch probe taught on the stock example and its graded copy, painting the graded square",
     "resourceClass": "gpu", "targets": [701], "timeoutSeconds": 900,
     "bindings": {"fixtureImageSourceNodeIds": [EXAMPLE]},
     "execution": {"requiredNodeIds": [698, 700, 701], "forbiddenCachedNodeIds": [698, 700, 701]},
     "expect": {
         "698": _compare(2, 1, schema="lf.vision-patch-encode.v1", crop="none", image_count=4),
         "700": _compare(2, 1, schema="lf.vision-patch-encode.v1", crop="none", image_count=2),
         "701": _compare(4, 2, schema="lf.patch-probe.v1", crop="none"),
     }},
    {"id": "model.intrinsic-layers",
     "title": "Intrinsic layers of the stock example: albedo, diffuse shading and residual",
     "resourceClass": "gpu", "targets": [702], "timeoutSeconds": 900,
     "bindings": {"fixtureImageSourceNodeIds": [EXAMPLE]},
     "execution": {"requiredNodeIds": [702], "forbiddenCachedNodeIds": [702]},
     "expect": {"702": _compare(6, 3, schema="lf.intrinsic-layers.v1", release="v21")}},
    {"id": "model.speech",
     "title": "Two designed voices, the first converted onto the second, matched against that voice and its text",
     "resourceClass": "gpu", "targets": [707], "timeoutSeconds": 1200,
     "execution": {"requiredNodeIds": [703, 704, 705, 706], "forbiddenCachedNodeIds": [703, 704, 705, 706]},
     "expect": {
         "703": {"minimumAudioPreviewCount": 1, "previewStorageType": "input",
                 "requiredNamedValues": {"schema": "lf.voice_clone_speech.receipt.v1", "mode": "design",
                                         "text": LINE}},
         "704": {"minimumAudioPreviewCount": 1, "previewStorageType": "input",
                 "requiredNamedValues": {"schema": "lf.voice_clone_speech.receipt.v1", "mode": "design",
                                         "text": TARGET_LINE}},
         "705": {"minimumAudioPreviewCount": 1, "previewStorageType": "input",
                 "requiredNamedValues": {"schema": "lf.voice_convert.receipt.v1"}},
         "706": {"minimumLivePreviewCount": 4,
                 "requiredNamedValues": {"schema": "lf.speech_match.receipt.v1", "expected_text": LINE}},
     }},
]


def add_specimens(workflow):
    specimen = titanic.Specimen("Readers", START_NODE, START_LINK, ORDER)
    def place(identifier, kind, *args, **kwargs):
        """A node whose size and position the section's ``arrange`` sets."""
        return specimen.node(identifier, kind, 0, 0, *args, **kwargs)

    def link(*pairs):
        for origin, output, target, name in pairs:
            specimen.connect(workflow, origin, output, target, name)

    # cpu.inspection: before (the example) against after (its graded square).
    place(678, "LF_ImageDiff",
         [("image_a", "IMAGE"), ("image_b", "IMAGE"), ("threshold", "FLOAT"), ("heat_max", "FLOAT"),
          ("box", "STRING"), ("labels", "STRING"), ("mask", "MASK"), ("ui_widget", "LF_COMPARE")],
         (("heat", "IMAGE", False), ("heat_list", "IMAGE", True), ("report", "JSON", False)),
         {"threshold": 2, "heat_max": 0, "box": "", "labels": "graded", "ui_widget": {}},
         "Where the grade changed the example · CPU")
    place(679, "LF_GradeSplit",
         [("before", "IMAGE"), ("after", "IMAGE"), ("lut_size", "INT"), ("local_size", "INT"),
          ("local_sigma", "FLOAT"), ("fine_sigma", "FLOAT"), ("coarse_sigma", "FLOAT"), ("ui_widget", "LF_COMPARE")],
         (("report", "JSON", False), ("change", "IMAGE", False), ("left", "IMAGE", False)),
         {"lut_size": 32, "local_size": 16, "local_sigma": 1 / 60, "fine_sigma": 2, "coarse_sigma": 16,
          "ui_widget": {}}, "How much of the change a grade explains · CPU")
    place(680, "LF_LumaRatioMap",
         [("before", "IMAGE"), ("after", "IMAGE"), ("sigma", "FLOAT"), ("floor", "FLOAT"), ("band_edges", "STRING"),
          ("stops", "FLOAT"), ("mask", "MASK"), ("ui_widget", "LF_COMPARE")],
         (("report", "JSON", False), ("ratio_map", "IMAGE", False)),
         {"sigma": 3, "floor": 0.03, "band_edges": "0.03,0.06,0.1,0.15,0.2,0.3,0.45,0.65,1.01", "stops": 1,
          "ui_widget": {}}, "Luma after over before inside the square · CPU")
    place(681, "LF_ImageList", [("image_1", "IMAGE"), ("image_2", "IMAGE"), ("ui_widget", "LF_MASONRY")],
         (("images", "IMAGE", True),), {"ui_widget": {}}, "Before, then after")
    place(682, "LF_RegionMeasure",
         [("image", "IMAGE"), ("boxes", "STRING"), ("labels", "STRING"), ("mask", "MASK"),
          ("ui_widget", "LF_TAB_BAR_CHART")],
         (("report", "JSON", False), ("overlay", "IMAGE", False), ("overlay_list", "IMAGE", True)),
         {"boxes": BOXES, "labels": "before,after", "ui_widget": {}}, "The square and the top band, measured · CPU")
    place(683, "LF_PlotChart",
         [("data", "JSON"), ("kind", "COMBO"), ("paths", "STRING"), ("title", "STRING"), ("x_label", "STRING"),
          ("y_label", "STRING"), ("width", "INT"), ("height", "INT"), ("bins", "INT"), ("log_y", "BOOLEAN"),
          ("ui_widget", "LF_TAB_BAR_CHART")],
         (("image", "IMAGE", False), ("image_list", "IMAGE", True), ("numbers", "JSON", False)),
         {"kind": "bar", "paths": ("square = frames.*.label, frames.*.regions.square.mean\n"
                                   "band = frames.*.label, frames.*.regions.band.mean"),
          "title": "Luma mean of the square and the band", "x_label": "frame", "y_label": "luma mean",
          "width": 960, "height": 540, "bins": 40, "log_y": False, "ui_widget": {}},
         "The square's luma moves toward the band's · CPU")
    link((EXAMPLE, 0, 678, "image_a"), (GRADED, 0, 678, "image_b"),
         (EXAMPLE, 0, 679, "before"), (GRADED, 0, 679, "after"),
         (EXAMPLE, 0, 680, "before"), (GRADED, 0, 680, "after"), (SQUARE_MASK, 0, 680, "mask"),
         (EXAMPLE, 0, 681, "image_1"), (GRADED, 0, 681, "image_2"), (681, 0, 682, "image"), (682, 0, 683, "data"))
    bottom = specimen.arrange(LEFT, TOP, [[678, 679, 680], [681, 682, 683]], SIZES, GAP)
    groups = [specimen.group(27, "Image diff, grade split, luma ratio, region measure and plot · CPU coverage",
                             range(678, 684), GROUP_COLOR)]

    # cpu.tone-readers: the square and the band as a named region set over the example.
    place(684, "MaskToImage", [("mask", "MASK")], (("IMAGE", "IMAGE", False),))
    place(685, "MaskToImage", [("mask", "MASK")], (("IMAGE", "IMAGE", False),))
    place(686, "LF_ImageList", [("image_1", "IMAGE"), ("image_2", "IMAGE"), ("ui_widget", "LF_MASONRY")],
         (("images", "IMAGE", True),), {"ui_widget": {}}, "Region-major: the square, then the band")
    place(687, "ImageToMask", [("image", "IMAGE"), ("channel", "COMBO")], (("MASK", "MASK", False),),
         {"channel": "red"})
    regions = [{"id": "square", "prompt": "central square", "priority": 10},
               {"id": "band", "prompt": "top band", "priority": 0}]
    place(688, "LF_WriteJSON", [("ui_widget", "LF_TEXTAREA")], (("json", "JSON", False),),
         {"ui_widget": json.dumps(regions, separators=(",", ":"))}, "The square and the top band")
    place(689, "LF_TextRegionMasks",
         [("image", "IMAGE"), ("masks", "MASK"), ("regions", "JSON"), ("ui_widget", "LF_COMPARE")], REGION_SET,
         {"ui_widget": {}}, "The example's square and band as a region set · CPU")
    tone_in = [("image", "IMAGE"), ("min_pixels", "INT"), ("masks", "MASK"), ("metadata", "JSON"),
               ("reference", "JSON"), ("ui_widget", "LF_TREE")]
    place(690, "LF_ToneProfile", tone_in, (("profile", "JSON", False),),
         {"min_pixels": 200, "ui_widget": {}}, "Tone before the grade · CPU")
    place(691, "LF_ToneProfile", tone_in, (("profile", "JSON", False),),
         {"min_pixels": 200, "ui_widget": {}}, "Tone after the grade, against before · CPU")
    place(692, "LF_RegionReads", READS_IN, READS_OUT, {"reads": READS, **READS_SETTINGS},
         "The graded square against the band · CPU")
    link((SQUARE_MASK, 0, 684, "mask"), (BAND_MASK, 0, 685, "mask"), (684, 0, 686, "image_1"),
         (685, 0, 686, "image_2"), (686, 0, 687, "image"),
         (EXAMPLE, 0, 689, "image"), (687, 0, 689, "masks"), (688, 0, 689, "regions"),
         (EXAMPLE, 0, 690, "image"), (689, 0, 690, "masks"), (689, 1, 690, "metadata"),
         (GRADED, 0, 691, "image"), (689, 0, 691, "masks"), (689, 1, 691, "metadata"), (690, 0, 691, "reference"),
         (GRADED, 0, 692, "image"), (689, 0, 692, "masks"), (689, 1, 692, "metadata"))
    bottom = specimen.arrange(LEFT, bottom + SECTION_GAP, [[684, 685, 686, 687, 688], [689, 690, 691, 692]], SIZES, GAP)
    groups.append(specimen.group(28, "Tone profile and region reads of the square and the band · CPU coverage",
                                 range(684, 693), GROUP_COLOR))

    # model.face-zones: both generated portraits, each zoned and read.
    place(693, "LF_FaceZones",
         [("image", "IMAGE"), ("model_pack", "COMBO"), ("select", "COMBO"), ("det_size", "INT"),
          ("score_threshold", "FLOAT"), ("ui_widget", "LF_COMPARE")],
         (("masks", "MASK", False), ("metadata", "JSON", False), ("overlay", "IMAGE", False)),
         {"model_pack": "antelopev2", "select": "center", "det_size": 640, "score_threshold": 0.5, "ui_widget": {}},
         "Zone both portraits: installed InsightFace pack required")
    place(694, "LF_RegionReads", READS_IN, READS_OUT, {"reads": FACE_READS, **READS_SETTINGS},
         "Under-eyes and folds against the cheeks")
    link((PORTRAITS, 1, 693, "image"), (PORTRAITS, 1, 694, "image"), (693, 0, 694, "masks"),
         (693, 1, 694, "metadata"))
    bottom = specimen.arrange(LEFT, bottom + SECTION_GAP, [[693, 694]], SIZES, GAP)
    groups.append(specimen.group(29, "Face zones and their reads on the generated portraits - model coverage",
                                 (693, 694), GROUP_COLOR))

    # model.patch-probe: label 1 is the graded copy; the mirrored pair is the second group.
    flip_in = [("image", "IMAGE"), ("flip_method", "COMBO")]
    place(695, "ImageFlip", flip_in, (("IMAGE", "IMAGE", False),), {"flip_method": "y-axis: horizontally"})
    place(696, "ImageFlip", flip_in, (("IMAGE", "IMAGE", False),),
         {"flip_method": "y-axis: horizontally"})
    batch = lambda count: [(f"images.image{index}", "IMAGE") for index in range(count + 1)]
    place(697, "BatchImagesNode", batch(4), (("IMAGE", "IMAGE", False),), None,
         "Teaching batch: example, graded, mirrored example, mirrored graded")
    encode_in = [("clip_vision", "CLIP_VISION"), ("image", "IMAGE"), ("crop", "COMBO"), ("ui_widget", "LF_COMPARE")]
    encoded = (("clip_vision_output", "CLIP_VISION_OUTPUT", False),)
    place(698, "LF_VisionPatchEncode", encode_in, encoded, {"crop": "none", "ui_widget": {}},
         "DINOv3 tokens of the teaching batch")
    place(699, "BatchImagesNode", batch(2), (("IMAGE", "IMAGE", False),), None,
         "Frames: the example, then its graded copy")
    place(700, "LF_VisionPatchEncode", encode_in, encoded, {"crop": "none", "ui_widget": {}},
         "DINOv3 tokens of the frames")
    place(701, "LF_PatchProbe",
         [("teach", "CLIP_VISION_OUTPUT"), ("labels", "STRING"), ("groups", "STRING"), ("frames", "CLIP_VISION_OUTPUT"),
          ("frame_images", "IMAGE"), ("crop", "COMBO"), ("l2", "FLOAT"), ("frame_groups", "STRING"),
          ("frame_masks", "MASK"), ("names", "STRING"), ("ui_widget", "LF_COMPARE")],
         (("report", "JSON", False), ("painted", "IMAGE", False), ("probability", "MASK", False)),
         {"labels": "0,1,0,1", "groups": "a,a,b,b", "crop": "none", "l2": 0.01, "frame_groups": "a,a",
          "names": "example,graded", "ui_widget": {}}, "Where the frames read as graded · GPU")
    link((EXAMPLE, 0, 695, "image"), (GRADED, 0, 696, "image"),
         (EXAMPLE, 0, 697, "images.image0"), (GRADED, 0, 697, "images.image1"), (695, 0, 697, "images.image2"),
         (696, 0, 697, "images.image3"), (DINO, 0, 698, "clip_vision"), (697, 0, 698, "image"),
         (EXAMPLE, 0, 699, "images.image0"), (GRADED, 0, 699, "images.image1"),
         (DINO, 0, 700, "clip_vision"), (699, 0, 700, "image"),
         (698, 0, 701, "teach"), (700, 0, 701, "frames"), (699, 0, 701, "frame_images"),
         (SQUARE_MASK, 0, 701, "frame_masks"))
    bottom = specimen.arrange(LEFT, bottom + SECTION_GAP, [[695, 696, 697, 699], [698, 700, 701]], SIZES, GAP)
    groups.append(specimen.group(30, "DINOv3 patch probe on the stock example's grade - model + GPU coverage",
                                 range(695, 702), GROUP_COLOR))

    # model.intrinsic-layers.
    place(702, "LF_IntrinsicLayers",
         [("image", "IMAGE"), ("release", "COMBO"), ("resize_conf", "FLOAT"), ("base_size", "INT"),
          ("ui_widget", "LF_COMPARE")],
         tuple((name, "JSON" if name == "report" else "IMAGE", False) for name in (
             "albedo", "diffuse_shading", "residual", "report", "albedo_display", "shading_display")),
         {"release": "v21", "resize_conf": 0, "base_size": 384, "ui_widget": {}},
         "Albedo, diffuse shading and residual: installed release required")
    link((EXAMPLE, 0, 702, "image"))
    bottom = specimen.arrange(LEFT, bottom + SECTION_GAP, [[702]], SIZES, GAP)
    groups.append(specimen.group(31, "Intrinsic layers of the stock example - model + GPU coverage", (702,),
                                 GROUP_COLOR))

    # model.speech: two designed voices, a conversion and its match.
    speak_in = [("text", "STRING"), ("model", "COMBO"), ("revision", "STRING"), ("language", "STRING"),
                ("seed", "INT"), ("num_step", "INT"), ("guidance_scale", "FLOAT"), ("speed", "FLOAT"),
                ("reference_audio", "AUDIO"), ("reference_text", "STRING"), ("voice_design", "STRING"),
                ("t_shift", "FLOAT"), ("ui_widget", "LF_MASONRY")]
    speech = (("audio", "AUDIO", False), ("receipt", "JSON", False))

    def speak(identifier, text, seed, design, title):
        place(identifier, "LF_VoiceCloneSpeech", speak_in, speech,
             {"text": text, "model": SPEAKER[0], "revision": SPEAKER[1], "language": "English", "seed": seed,
              "control_after_generate": "fixed", "num_step": 32, "guidance_scale": 2, "speed": 0,
              "reference_text": "", "voice_design": design, "t_shift": 0.1, "ui_widget": {}}, title)

    speak(703, LINE, 7, "female, middle-aged, low pitch, british accent", "Designed voice: the line · GPU")
    speak(704, TARGET_LINE, 11, "male, young adult, high pitch, american accent",
          "Designed voice: the converter's target · GPU")
    place(705, "LF_VoiceConvert",
         [("source_audio", "AUDIO"), ("target_audio", "AUDIO"), ("model", "COMBO"), ("revision", "STRING"),
          ("ui_widget", "LF_MASONRY")], speech,
         {"model": CONVERTER[0], "revision": CONVERTER[1], "ui_widget": {}}, "The line in the target's voice · GPU")
    place(706, "LF_SpeechMatch",
         [("audio", "AUDIO"), ("reference_audio", "AUDIO"), ("expected_text", "STRING"), ("language", "STRING"),
          ("speaker_model", "COMBO"), ("speaker_revision", "STRING"), ("asr_model", "COMBO"),
          ("asr_revision", "STRING"), ("ui_widget", "LF_TREE")],
         (("speaker_similarity", "FLOAT", False), ("transcript", "STRING", False), ("word_error_rate", "FLOAT", False),
          ("receipt", "JSON", False)),
         {"expected_text": LINE, "language": "english", "speaker_model": SPEAKER_ENCODER[0],
          "speaker_revision": SPEAKER_ENCODER[1], "asr_model": RECOGNIZER[0], "asr_revision": RECOGNIZER[1],
          "ui_widget": {}}, "Converted line against the target voice and the text · GPU")
    place(707, "LF_DisplayJSON", [("json_input", "JSON"), ("ui_widget", "LF_CODE")],
         (("json", "JSON", False),), {"ui_widget": ""}, "Speech match receipt")
    link((703, 0, 705, "source_audio"), (704, 0, 705, "target_audio"), (705, 0, 706, "audio"),
         (704, 0, 706, "reference_audio"), (706, 3, 707, "json_input"))
    specimen.arrange(LEFT, bottom + SECTION_GAP, [[703, 704, 705], [706, 707]], SIZES, GAP)
    groups.append(specimen.group(32, "Designed voices, conversion and speech match - model + GPU coverage",
                                 range(703, 708), GROUP_COLOR))

    return specimen.append(workflow, *groups)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args()
    workflow = add_specimens(titanic.read_workflow())
    workflow_bytes = titanic.canonical_bytes(workflow)
    manifest = titanic.MANIFEST_PATH.read_text(encoding="utf-8")
    manifest = titanic.upsert_cases(titanic.set_counts(manifest, workflow, workflow_bytes), CASES)
    titanic.check_or_write({titanic.WORKFLOW_PATH: workflow_bytes, titanic.MANIFEST_PATH: manifest.encode()},
                           options.check, "Readers")
    print(f"Readers fixture {'checked' if options.check else 'updated'}: {len(workflow['nodes'])} nodes, "
          f"{len(workflow['links'])} links")


if __name__ == "__main__":
    main()
