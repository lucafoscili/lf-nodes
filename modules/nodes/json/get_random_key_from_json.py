import hashlib
import random

from . import CATEGORY
from ...utils.constants import FUNCTION, Input, INT_MAX
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.logic import normalize_list_to_value, normalize_json_input


LEGACY_SELECTION_MODE = "uniform_legacy"
WEIGHTED_SELECTION_MODE = "weighted_sha256_v1"
WEIGHTED_SELECTION_DOMAIN = b"lf.get-random-key/weighted-sha256.v1"
JSON_SAFE_SEED_MAX = (1 << 53) - 1
MAX_WEIGHTED_KEYS = 128
# Portrait-appearance preference weights are bounded at 1,000,000 and the
# workflow bucket adds the baseline ticket, so 1,000,001 is the exact wire cap.
MAX_WEIGHT = 1_000_001
MAX_KEY_BYTES = 1024


class WeightedKeySelectionError(ValueError):
    """Raised when an opt-in weighted JSON bucket is not the closed contract."""


def select_weighted_key(seed: int, target: dict) -> str:
    """Select a weighted key with a portable, insertion-order-free draw.

    The binary hash material is deliberately specified without relying on
    Python/JavaScript JSON serialization or Unicode sort behavior:

    ``domain || NUL || decimal seed || NUL || (u32 key bytes || key || u64 weight)*``

    Entries are ordered by their UTF-8 key bytes.  Velora constrains seeds to
    JavaScript's exact integer range because Comfy prompt graphs pass through
    browser JSON before Python receives them.
    """
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0 or seed > JSON_SAFE_SEED_MAX:
        raise WeightedKeySelectionError("weighted selection seed must be a JSON-safe nonnegative integer")
    if not isinstance(target, dict) or not 1 <= len(target) <= MAX_WEIGHTED_KEYS:
        raise WeightedKeySelectionError(f"weighted JSON must contain 1 to {MAX_WEIGHTED_KEYS} keys")

    entries = []
    for key, weight in target.items():
        if not isinstance(key, str) or not key:
            raise WeightedKeySelectionError("weighted JSON keys must be nonempty strings")
        key_bytes = key.encode("utf-8")
        if len(key_bytes) > MAX_KEY_BYTES:
            raise WeightedKeySelectionError(f"weighted JSON keys must be at most {MAX_KEY_BYTES} UTF-8 bytes")
        if isinstance(weight, bool) or not isinstance(weight, int) or weight < 1 or weight > MAX_WEIGHT:
            raise WeightedKeySelectionError(f"weighted JSON values must be integers from 1 to {MAX_WEIGHT}")
        entries.append((key_bytes, key, weight))
    entries.sort(key=lambda entry: entry[0])

    digest = hashlib.sha256()
    digest.update(WEIGHTED_SELECTION_DOMAIN)
    digest.update(b"\0")
    digest.update(str(seed).encode("ascii"))
    digest.update(b"\0")
    for key_bytes, _, weight in entries:
        digest.update(len(key_bytes).to_bytes(4, "big"))
        digest.update(key_bytes)
        digest.update(weight.to_bytes(8, "big"))

    total = sum(weight for _, _, weight in entries)
    draw = int.from_bytes(digest.digest(), "big") % total
    cursor = 0
    for _, key, weight in entries:
        cursor += weight
        if draw < cursor:
            return key
    raise WeightedKeySelectionError("weighted JSON selection did not resolve")

# region LF_GetRandomKeyFromJSON
class LF_GetRandomKeyFromJSON:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "seed": (Input.INTEGER, {
                    "default": 0,
                    "min": 0,
                    "max": INT_MAX,
                    "tooltip": "The seed for the random pick."
                }),
                "json_input": (Input.JSON, {
                    "tooltip": "JSON object from which a random key will be picked."
                }),
            },
            "optional": {
                "ui_widget": (Input.LF_CODE, {
                    "default": ""
                }),
                # Kept after the existing ui_widget so old workflow widget
                # arrays retain their historical positions on load.
                "selection_mode": (Input.COMBO, {
                    "default": LEGACY_SELECTION_MODE,
                    "options": [LEGACY_SELECTION_MODE, WEIGHTED_SELECTION_MODE],
                    "tooltip": "Legacy mode preserves insertion-order random.choice. Weighted mode treats positive integer JSON values as weights."
                }),
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "Randomly selected key from JSON.",
    )
    RETURN_NAMES = ("string",)
    RETURN_TYPES = (Input.STRING,)

    def on_exec(self, **kwargs: dict):
        seed: int = normalize_list_to_value(kwargs.get("seed"))
        json_input = normalize_json_input(kwargs.get("json_input"))

        is_wrapped_single_dict = (
            isinstance(json_input, list)
            and len(json_input) == 1
            and isinstance(json_input[0], dict)
        )

        target = json_input[0] if is_wrapped_single_dict else json_input

        if not isinstance(target, dict) or not target:
            safe_send_sync("getrandomkeyfromjson", {
                "value": "**Warning**: JSON input does not contain any keys.",
            }, kwargs.get("node_id"))
            return ("",)

        selection_mode = normalize_list_to_value(kwargs.get("selection_mode", LEGACY_SELECTION_MODE))
        if selection_mode == LEGACY_SELECTION_MODE:
            # This is intentionally the exact historical behavior.  Existing
            # LoRA Tester buckets use empty-string values and remain unchanged.
            random.seed(seed)
            keys = list(target.keys())
            selected_key = random.choice(keys)
        elif selection_mode == WEIGHTED_SELECTION_MODE:
            selected_key = select_weighted_key(seed, target)
        else:
            raise ValueError("Unsupported random-key selection mode")

        safe_send_sync("getrandomkeyfromjson", {
            "value": f"## Selected key\n{selected_key}\n\n## Content:\n{target.get(selected_key)}",
        }, kwargs.get("node_id"))

        return (selected_key,)
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_GetRandomKeyFromJSON": LF_GetRandomKeyFromJSON,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_GetRandomKeyFromJSON": "Get Random Key From JSON",
}
# endregion
