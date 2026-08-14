import hashlib
import json
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

folder_paths_mock = MagicMock()
folder_paths_mock.models_dir = "."
sys.modules.setdefault("folder_paths", folder_paths_mock)
sys.modules.setdefault("torch", MagicMock())

helpers_package = types.ModuleType("modules.utils.helpers")
helpers_package.__path__ = [str(REPO_ROOT / "modules" / "utils" / "helpers")]
sys.modules.setdefault("modules.utils.helpers", helpers_package)

ui_mock = MagicMock()
ui_mock.prepare_model_dataset = MagicMock(return_value={})
sys.modules.setdefault("modules.utils.helpers.ui", ui_mock)

from modules.nodes.json.resolve_prompt_buckets import (
    LF_ResolvePromptBuckets,
    PromptBucketDocumentError,
    resolve_prompt_buckets,
)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def sealed_document():
    core = {
        "schema": "velora.portrait-appearance-buckets.v1",
        "selection": {
            "algorithm": "sha256-weighted-modulo.v1",
            "seedEncoding": "uint64-decimal.v1",
            "key": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "samplerSeed": "4503599627370495",
        },
        "buckets": [
            {
                "aspect": {"entityId": "eyes", "label": "eyes"},
                "order": 10,
                "seed": "42",
                "candidates": [{"valueEntityId": "moon-glow", "label": "silver-white moon glow", "order": 10, "weight": 1}],
            },
            {
                "aspect": {"entityId": "hairstyle", "label": "hair"},
                "order": 20,
                "seed": "99",
                "candidates": [
                    {"valueEntityId": "braid", "label": "ceremonial braid", "order": 10, "weight": 1},
                    {"valueEntityId": "high-ponytail", "label": "high ponytail", "order": 20, "weight": 10},
                ],
            },
        ],
    }
    return {**core, "payloadSha256": "sha256:" + hashlib.sha256(canonical(core).encode("utf-8")).hexdigest()}


class TestResolvePromptBuckets(unittest.TestCase):
    def test_resolves_fixed_and_weighted_buckets_from_one_document(self):
        document = sealed_document()
        prompt, manifest, sampler_seed = resolve_prompt_buckets(canonical(document))

        self.assertEqual(sampler_seed, 4503599627370495)
        # Cross-language golden vector: it is also exercised by Velora's TS
        # conformance suite using this exact algorithm/domain/key/seed tuple.
        self.assertEqual(prompt, "silver-white moon glow eyes, high ponytail hair")
        self.assertEqual([item["aspect"]["entityId"] for item in manifest["selections"]], ["eyes", "hairstyle"])
        self.assertEqual(manifest["selections"][0]["selected"]["valueEntityId"], "moon-glow")
        self.assertEqual(manifest["selections"][1]["selected"]["valueEntityId"], "high-ponytail")
        self.assertEqual(manifest["source"]["payloadSha256"], document["payloadSha256"])

    def test_weighted_selection_is_candidate_order_invariant_when_each_document_is_canonical(self):
        first = sealed_document()
        _, first_manifest, _ = resolve_prompt_buckets(first)

        # Change only declared presentation order, then reseal in that order.
        # Selection remains stable because the weighted draw canonicalizes IDs.
        second = sealed_document()
        candidates = second["buckets"][1]["candidates"]
        candidates[0]["order"], candidates[1]["order"] = 20, 10
        candidates.reverse()
        core = {key: value for key, value in second.items() if key != "payloadSha256"}
        second["payloadSha256"] = "sha256:" + hashlib.sha256(canonical(core).encode("utf-8")).hexdigest()
        _, second_manifest, _ = resolve_prompt_buckets(second)

        self.assertEqual(
            first_manifest["selections"][1]["selected"]["valueEntityId"],
            second_manifest["selections"][1]["selected"]["valueEntityId"],
        )

        punctuation = sealed_document()
        punctuation["selection"]["key"] = "sha256:" + ("b" * 64)
        punctuation["buckets"] = [{
            "aspect": {"entityId": "hairstyle", "label": "Hairstyle"},
            "order": 20,
            "seed": "7",
            "candidates": [
                {"valueEntityId": "a-b", "label": "A B", "order": 10, "weight": 1},
                {"valueEntityId": "a_b", "label": "A B", "order": 20, "weight": 3},
            ],
        }]
        punctuation_core = {key: value for key, value in punctuation.items() if key != "payloadSha256"}
        punctuation["payloadSha256"] = "sha256:" + hashlib.sha256(canonical(punctuation_core).encode("utf-8")).hexdigest()
        _, punctuation_manifest, _ = resolve_prompt_buckets(punctuation)
        self.assertEqual(punctuation_manifest["selections"][0]["selected"]["valueEntityId"], "a_b")

    def test_rejects_tampered_receipt_and_noncanonical_candidate_order(self):
        document = sealed_document()
        document["buckets"][0]["candidates"][0]["label"] = "changed"
        with self.assertRaisesRegex(PromptBucketDocumentError, "payloadSha256"):
            resolve_prompt_buckets(document)

        document = sealed_document()
        document["buckets"][1]["candidates"].reverse()
        core = {key: value for key, value in document.items() if key != "payloadSha256"}
        document["payloadSha256"] = "sha256:" + hashlib.sha256(canonical(core).encode("utf-8")).hexdigest()
        with self.assertRaisesRegex(PromptBucketDocumentError, "sorted"):
            resolve_prompt_buckets(document)

    def test_rejects_unsafe_prompt_fragments(self):
        document = sealed_document()
        document["buckets"][0]["aspect"]["label"] = "eyes <lora:unsafe>"
        core = {key: value for key, value in document.items() if key != "payloadSha256"}
        document["payloadSha256"] = "sha256:" + hashlib.sha256(canonical(core).encode("utf-8")).hexdigest()
        with self.assertRaisesRegex(PromptBucketDocumentError, "unsafe"):
            resolve_prompt_buckets(document)

    @patch("modules.nodes.json.resolve_prompt_buckets.safe_send_sync")
    def test_node_exposes_literal_widget_and_returns_manifest(self, mocked_send):
        node = LF_ResolvePromptBuckets()
        result = node.on_exec(bucket_document=canonical(sealed_document()), node_id="fixture")

        self.assertEqual(LF_ResolvePromptBuckets.INPUT_TYPES()["required"]["bucket_document"][0], "LF_TEXTAREA")
        self.assertTrue(LF_ResolvePromptBuckets.OUTPUT_NODE)
        self.assertEqual(result[1]["schema"], "velora.prompt-bucket-manifest.v1")
        mocked_send.assert_called_once()


if __name__ == "__main__":
    unittest.main()
