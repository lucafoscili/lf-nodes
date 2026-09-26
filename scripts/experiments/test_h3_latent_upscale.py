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


if __name__ == "__main__":
    unittest.main()
