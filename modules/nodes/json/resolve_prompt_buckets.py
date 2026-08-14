"""Resolve one Velora-supplied appearance bucket document inside Comfy.

The workflow deliberately knows no race, role, or catalog.  Velora supplies a
sealed document containing every bucket (including one-candidate fixed traits),
and this node performs the documented weighted-modulo draw.  Keeping the
document in the ``bucket_document`` widget makes the literal part of Comfy's
native prompt metadata whenever this node is upstream of ``SaveImage``.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Iterable, List, Mapping, Tuple

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value


_SCHEMA = "velora.portrait-appearance-buckets.v1"
_MANIFEST_SCHEMA = "velora.prompt-bucket-manifest.v1"
_ALGORITHM = "sha256-weighted-modulo.v1"
_SELECTION_DOMAIN = "velora.prompt-buckets/sha256-weighted-modulo.v1"
_SEED_ENCODING = "uint64-decimal.v1"
_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
_MAX_BUCKETS = 64
_MAX_CANDIDATES = 128
_MAX_LABEL = 160
_MAX_DOCUMENT_BYTES = 128 * 1024
_MAX_WEIGHT = 1_000_001
_UINT64_MAX = 18_446_744_073_709_551_615
_SAMPLER_SEED_MAX = (2 ** 53) - 1


class PromptBucketDocumentError(ValueError):
    """Raised when a document is not the bounded wire contract."""


def _canonical_json(value: object) -> str:
    """The compact, UTF-8 JSON form used by Velora's content-address receipt."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _receipt(value: object) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _exact(value: object, keys: Iterable[str], name: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise PromptBucketDocumentError(f"{name} must be an object")
    expected = set(keys)
    actual = set(value)
    if actual != expected:
        raise PromptBucketDocumentError(f"{name} must contain exactly: {', '.join(sorted(expected))}")
    return value


def _identifier(value: object, name: str) -> str:
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise PromptBucketDocumentError(f"{name} must be a safe identifier")
    return value


def _label(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise PromptBucketDocumentError(f"{name} must be text")
    text = value.strip()
    if not text or len(text) > _MAX_LABEL:
        raise PromptBucketDocumentError(f"{name} must be nonempty and at most {_MAX_LABEL} characters")
    # Labels become prompt text. Keep them a single benign text fragment: no
    # control characters, LoRA/embedding syntax, markup delimiters, or escapes.
    if any(ord(character) < 32 or ord(character) == 127 for character in text):
        raise PromptBucketDocumentError(f"{name} cannot contain control characters")
    if any(token in text for token in ("<", ">", "(", ")", "[", "]", "{", "}", "\\", ",", ":")):
        raise PromptBucketDocumentError(f"{name} contains unsafe prompt syntax")
    return text


def _order(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1 or value > 1_000_000:
        raise PromptBucketDocumentError(f"{name} must be a bounded positive integer")
    return value


def _seed(value: object, name: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"0|[1-9][0-9]{0,19}", value):
        raise PromptBucketDocumentError(f"{name} must be a uint64 decimal string")
    if int(value) > _UINT64_MAX:
        raise PromptBucketDocumentError(f"{name} exceeds uint64")
    return value


def _weight(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1 or value > _MAX_WEIGHT:
        raise PromptBucketDocumentError(f"{name} must be an integer from 1 to {_MAX_WEIGHT}")
    return value


def _weighted_modulo_choice(selection_key: str, bucket: Mapping[str, Any]) -> Dict[str, Any]:
    """Integer-only, cross-language selector pinned by the v1 wire contract."""
    candidates = sorted(bucket["candidates"], key=lambda candidate: candidate["valueEntityId"])
    total = sum(candidate["weight"] for candidate in candidates)
    # The contract's bounds make this impossible in normal operation, but the
    # explicit check keeps the modulo operand finite and easy to audit.
    if total < 1 or total > _MAX_CANDIDATES * _MAX_WEIGHT:
        raise PromptBucketDocumentError("bucket candidate weights have an invalid total")
    material = f"{_SELECTION_DOMAIN}\0{selection_key}\0{bucket['seed']}\0{bucket['aspect']['entityId']}"
    draw = int(hashlib.sha256(material.encode("utf-8")).hexdigest(), 16) % total
    cursor = 0
    for candidate in candidates:
        cursor += candidate["weight"]
        if draw < cursor:
            return candidate
    raise PromptBucketDocumentError("bucket selection did not resolve")


def _decode_document(raw: object) -> Dict[str, Any]:
    if isinstance(raw, list):
        if len(raw) != 1:
            raise PromptBucketDocumentError("bucket_document must be one JSON document")
        raw = raw[0]
    if isinstance(raw, str):
        if len(raw.encode("utf-8")) > _MAX_DOCUMENT_BYTES:
            raise PromptBucketDocumentError("bucket_document exceeds the size limit")
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError as error:
            raise PromptBucketDocumentError("bucket_document is not valid JSON") from error

    try:
        if len(_canonical_json(raw).encode("utf-8")) > _MAX_DOCUMENT_BYTES:
            raise PromptBucketDocumentError("bucket_document exceeds the size limit")
    except (TypeError, ValueError) as error:
        raise PromptBucketDocumentError("bucket_document must contain JSON-compatible values") from error

    document = _exact(raw, ("schema", "selection", "buckets", "payloadSha256"), "bucket_document")
    if document["schema"] != _SCHEMA:
        raise PromptBucketDocumentError("bucket_document.schema is unsupported")

    selection = _exact(document["selection"], ("algorithm", "seedEncoding", "key", "samplerSeed"), "bucket_document.selection")
    if selection["algorithm"] != _ALGORITHM:
        raise PromptBucketDocumentError("bucket_document.selection.algorithm is unsupported")
    if selection["seedEncoding"] != _SEED_ENCODING:
        raise PromptBucketDocumentError("bucket_document.selection.seedEncoding is unsupported")
    selection_key = selection["key"]
    if not isinstance(selection_key, str) or not _SHA256.fullmatch(selection_key):
        raise PromptBucketDocumentError("bucket_document.selection.key must be a SHA-256 receipt")
    sampler_seed = _seed(selection["samplerSeed"], "bucket_document.selection.samplerSeed")
    if int(sampler_seed) > _SAMPLER_SEED_MAX:
        raise PromptBucketDocumentError("bucket_document.selection.samplerSeed exceeds the JSON-safe integer range")

    supplied_receipt = document["payloadSha256"]
    if not isinstance(supplied_receipt, str) or not _SHA256.fullmatch(supplied_receipt):
        raise PromptBucketDocumentError("bucket_document.payloadSha256 must be a SHA-256 receipt")
    core = {"schema": document["schema"], "selection": selection, "buckets": document["buckets"]}
    if _receipt(core) != supplied_receipt:
        raise PromptBucketDocumentError("bucket_document.payloadSha256 does not match its canonical content")

    buckets = document["buckets"]
    if not isinstance(buckets, list) or not 1 <= len(buckets) <= _MAX_BUCKETS:
        raise PromptBucketDocumentError(f"bucket_document.buckets must contain 1 to {_MAX_BUCKETS} buckets")

    decoded_buckets: List[Dict[str, Any]] = []
    previous_bucket_key: Tuple[int, str] | None = None
    seen_aspects = set()
    for bucket_index, value in enumerate(buckets):
        name = f"bucket_document.buckets[{bucket_index}]"
        bucket = _exact(value, ("aspect", "order", "seed", "candidates"), name)
        aspect = _exact(bucket["aspect"], ("entityId", "label"), f"{name}.aspect")
        aspect_id = _identifier(aspect["entityId"], f"{name}.aspect.entityId")
        aspect_label = _label(aspect["label"], f"{name}.aspect.label")
        order = _order(bucket["order"], f"{name}.order")
        stable_bucket_key = (order, aspect_id)
        if previous_bucket_key is not None and stable_bucket_key <= previous_bucket_key:
            raise PromptBucketDocumentError("bucket_document.buckets must be sorted by order then aspect.entityId")
        previous_bucket_key = stable_bucket_key
        if aspect_id in seen_aspects:
            raise PromptBucketDocumentError("bucket_document buckets cannot repeat an aspect.entityId")
        seen_aspects.add(aspect_id)
        bucket_seed = _seed(bucket["seed"], f"{name}.seed")
        candidates = bucket["candidates"]
        if not isinstance(candidates, list) or not 1 <= len(candidates) <= _MAX_CANDIDATES:
            raise PromptBucketDocumentError(f"{name}.candidates must contain 1 to {_MAX_CANDIDATES} candidates")

        decoded_candidates: List[Dict[str, Any]] = []
        previous_candidate_key: Tuple[int, str] | None = None
        seen_candidate_ids = set()
        for candidate_index, candidate_value in enumerate(candidates):
            candidate_name = f"{name}.candidates[{candidate_index}]"
            candidate = _exact(candidate_value, ("valueEntityId", "label", "order", "weight"), candidate_name)
            candidate_id = _identifier(candidate["valueEntityId"], f"{candidate_name}.valueEntityId")
            candidate_order = _order(candidate["order"], f"{candidate_name}.order")
            candidate_key = (candidate_order, candidate_id)
            if previous_candidate_key is not None and candidate_key <= previous_candidate_key:
                raise PromptBucketDocumentError(f"{name}.candidates must be sorted by order then valueEntityId")
            previous_candidate_key = candidate_key
            if candidate_id in seen_candidate_ids:
                raise PromptBucketDocumentError(f"{name}.candidates cannot repeat a valueEntityId")
            seen_candidate_ids.add(candidate_id)
            decoded_candidates.append({
                "valueEntityId": candidate_id,
                "label": _label(candidate["label"], f"{candidate_name}.label"),
                "order": candidate_order,
                "weight": _weight(candidate["weight"], f"{candidate_name}.weight"),
            })
        decoded_buckets.append({
            "aspect": {"entityId": aspect_id, "label": aspect_label},
            "order": order,
            "seed": bucket_seed,
            "candidates": decoded_candidates,
        })

    return {
        "schema": _SCHEMA,
        "selection": {
            "algorithm": _ALGORITHM,
            "seedEncoding": _SEED_ENCODING,
            "key": selection_key,
            "samplerSeed": sampler_seed,
        },
        "buckets": decoded_buckets,
        "payloadSha256": supplied_receipt,
    }


def resolve_prompt_buckets(document: object) -> Tuple[str, Dict[str, Any], int]:
    """Pure resolver, deliberately shared by the Comfy node and unit tests."""
    decoded = _decode_document(document)
    selected: List[Dict[str, Any]] = []
    for bucket in decoded["buckets"]:
        winner = _weighted_modulo_choice(decoded["selection"]["key"], bucket)
        prompt_fragment = f"{winner['label']} {bucket['aspect']['label']}"
        selected.append({
            "aspect": bucket["aspect"],
            "order": bucket["order"],
            "seed": bucket["seed"],
            "selected": winner,
            "promptFragment": prompt_fragment,
        })
    manifest = {
        "schema": _MANIFEST_SCHEMA,
        "source": {"schema": decoded["schema"], "payloadSha256": decoded["payloadSha256"]},
        "selection": decoded["selection"],
        "selections": selected,
    }
    return ", ".join(item["promptFragment"] for item in selected), manifest, int(decoded["selection"]["samplerSeed"])


class LF_ResolvePromptBuckets:
    """One self-contained, deterministic Velora prompt-bucket resolver."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # This is intentionally a literal widget rather than a hidden
                # server lookup. Comfy stores it in the native prompt metadata.
                "bucket_document": (Input.LF_TEXTAREA, {
                    "default": "{}",
                    "tooltip": "One sealed velora.portrait-appearance-buckets.v1 JSON document. Keep this node upstream of SaveImage to retain the literal in PNG prompt metadata.",
                }),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    RETURN_TYPES = (Input.STRING, Input.JSON, Input.INTEGER)
    RETURN_NAMES = ("prompt", "selected_manifest", "sampler_seed")
    OUTPUT_TOOLTIPS = (
        "Comma-separated selected prompt clauses, in canonical bucket order.",
        "Canonical selected trait manifest; preserve it alongside the generated image.",
        "Velora-supplied uint64 sampler seed (as Comfy INT).",
    )

    def on_exec(self, **kwargs: Any) -> Tuple[str, Dict[str, Any], int]:
        raw = normalize_list_to_value(kwargs.get("bucket_document", "{}"))
        prompt, manifest, sampler_seed = resolve_prompt_buckets(raw)
        safe_send_sync("resolvepromptbuckets", {
            "value": _canonical_json(manifest),
            "prompt": prompt,
            "samplerSeed": str(sampler_seed),
        }, kwargs.get("node_id"))
        return prompt, manifest, sampler_seed


NODE_CLASS_MAPPINGS = {
    "LF_ResolvePromptBuckets": LF_ResolvePromptBuckets,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_ResolvePromptBuckets": "Resolve Prompt Buckets",
}
