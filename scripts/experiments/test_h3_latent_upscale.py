"""CPU-only structural checks; no Comfy imports or sampling."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("h3_latent_upscale", Path(__file__).with_name("h3_latent_upscale.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.graph = json.loads((ROOT / "modules/workflow_runner/workflows/minimax_h3_reference.json").read_text())
        self.graph["h3"]["inputs"]["prompt"] = "Exact original prompt — no rewrite."
        self.graph["source_1"]["inputs"]["image"] = "accepted/reference.png"

    def test_preserves_recipe_and_original_inputs(self):
        original = deepcopy(self.graph)
        result = module.build_graph(self.graph)
        self.assertEqual(original, self.graph)
        for name, node in original.items():
            if name not in ("h3", "decode_video", "save"):
                self.assertEqual(node, result[name], name)
        for name in ("h3", "experiment_target_conditioning"):
            actual = deepcopy(result[name]["inputs"])
            expected = deepcopy(original["h3"]["inputs"])
            for key in ("width", "height"):
                actual.pop(key)
                expected.pop(key)
            self.assertEqual(actual, expected)
        self.assertFalse(any("lora" in n["class_type"].lower() for n in result.values()))
        result["experiment_target_conditioning"]["inputs"]["clip"][0] = "changed"
        self.assertEqual(self.graph, original)
        self.assertNotEqual(result["h3"]["inputs"]["clip"][0], "changed")

    def test_target_conditioning_audio_and_before_after_outputs(self):
        result = module.build_graph(self.graph)
        target = result["experiment_target_conditioning"]["inputs"]
        params = result["experiment_upscale_params"]["inputs"]
        self.assertEqual((target["width"], target["height"]), (1248, 1664))
        self.assertEqual((params["width"], params["height"]), (1248, 1664))
        self.assertEqual((result["h3"]["inputs"]["width"], result["h3"]["inputs"]["height"]), (768, 1024))
        up = result["experiment_upscale"]["inputs"]
        self.assertEqual(up["latent"], ["sample", 1])
        self.assertEqual(up["sampler"], self.graph["sample"]["inputs"]["sampler"])
        self.assertEqual(up["model"], self.graph["guider"]["inputs"]["model"])
        self.assertNotIn("temporal_split_param", up)
        self.assertNotIn("spatial_split_param", up)
        self.assertEqual(result["decode_audio"], self.graph["decode_audio"])
        self.assertEqual(result["experiment_baseline_create"]["inputs"]["audio"], result["create_video"]["inputs"]["audio"])
        self.assertNotEqual(result["save"]["inputs"]["filename_prefix"], result["experiment_baseline_save"]["inputs"]["filename_prefix"])
        self.assertEqual(result["decode_video"]["inputs"]["samples"], ["experiment_upscale", 0])
        self.assertEqual(result["experiment_baseline_decode"], self.graph["decode_video"])

    def test_configurable_schedule_and_invalid_inputs(self):
        result = module.build_graph(self.graph, second_steps=6, second_denoise=0.3)
        self.assertEqual(result["experiment_schedule"]["inputs"]["steps"], 6)
        self.assertEqual(result["experiment_schedule"]["inputs"]["denoise"], 0.3)
        for opts in ({"base_width": 777}, {"target_width": 64}, {"second_steps": 0}, {"second_denoise": float("nan")}):
            with self.subTest(opts=opts), self.assertRaises(ValueError):
                module.build_graph(self.graph, **opts)
        with self.assertRaises(ValueError):
            module.build_graph(result)

    def test_comparison_shares_base_audio_conditioning_and_noise(self):
        original = deepcopy(self.graph)
        result = module.build_refinement_comparison(self.graph)
        self.assertEqual(self.graph, original)
        self.assertEqual(result["sample"], original["sample"])
        self.assertEqual(sum(n["class_type"] == "SamplerCustomAdvanced" for n in result.values()), 1)
        first = deepcopy(result["experiment_upscale"]["inputs"])
        second = deepcopy(result["experiment_upscale_8"]["inputs"])
        self.assertEqual(first.pop("sigmas"), ["experiment_schedule", 0])
        self.assertEqual(second.pop("sigmas"), ["experiment_schedule_8", 0])
        self.assertEqual(first, second)
        self.assertEqual(first["latent"], ["sample", 1])
        four = deepcopy(result["experiment_schedule"]["inputs"])
        eight = deepcopy(result["experiment_schedule_8"]["inputs"])
        self.assertEqual(four.pop("steps"), 4)
        self.assertEqual(eight.pop("steps"), 8)
        self.assertEqual(four, eight)
        self.assertEqual(result["decode_audio"], original["decode_audio"])
        self.assertEqual(result["experiment_create_8"]["inputs"]["audio"],
                         result["create_video"]["inputs"]["audio"])
        self.assertNotIn("experiment_baseline_save", result)
        with self.assertRaises(ValueError):
            module.build_refinement_comparison(self.graph, second_steps=8)

    def test_comparison_encodes_each_decoded_video_at_both_qualities(self):
        result = module.build_refinement_comparison(self.graph)
        savers = [node["inputs"] for node in result.values() if node["class_type"] == "SaveVideo"]
        self.assertEqual(len(savers), 4)
        self.assertEqual(len({s["filename_prefix"] for s in savers}), 4)
        for video in ("create_video", "experiment_create_8"):
            pair = [s for s in savers if s["video"] == [video, 0]]
            self.assertEqual({s["format.codec.encoding.crf"] for s in pair}, {18.0, 23.0})
            for s in pair:
                self.assertEqual(s["format"], "mp4")
                self.assertEqual(s["format.codec"], "h264")
                self.assertEqual(s["format.codec.encoding"], "re-encode")
                self.assertNotIn("codec", s)
        self.assertFalse(any(node["class_type"] == "LoadVideo" for node in result.values()))


if __name__ == "__main__":
    unittest.main()
