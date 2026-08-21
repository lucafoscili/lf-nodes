from .contracts import CATEGORY, FUNCTION, Input
from .core import canonical_json, make_state, strict_json_loads


class LF_VNState:
    """Create an immutable, fixture-only narrative state envelope."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fixture_id": (
                    Input.LF_ID,
                    {
                        "default": "",
                        "lf_id_kind": "fixture",
                        "tooltip": "LF-owned persistent fixture identity. Generated once by the authoring UI; headless prompts must provide it.",
                    },
                ),
                "state_body": (
                    Input.LF_TEXTAREA,
                    {
                        "default": "{\n  \"markers\": []\n}",
                        "tooltip": "Opaque strict-JSON fixture values. Predicate paths are evaluated relative to this object.",
                    },
                ),
            },
            "optional": {
                "profile_ref": (
                    Input.LF_REF,
                    {
                        "default": "",
                        "lf_ref_kind": "profile",
                        "tooltip": "Optional consumer-owned profile reference. Choose it from a consumer catalogue or supply it through a typed connection.",
                    },
                ),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "Versioned immutable VN fixture state.",
        "The same state envelope through the generic JSON socket.",
        "Canonical JSON text for hashing, inspection, and API clients.",
    )
    RETURN_NAMES = ("state", "state_object", "canonical_json")
    RETURN_TYPES = (Input.LF_VN_STATE, Input.JSON, Input.STRING)

    def on_exec(self, **kwargs: dict):
        values = strict_json_loads(
            kwargs.get("state_body", "{}"),
            label="state_body",
            expected_type=dict,
        )
        profile_ref = kwargs.get("profile_ref", "")
        state = make_state(
            profile_id=profile_ref,
            fixture_id=kwargs.get("fixture_id", ""),
            values=values,
        )
        return (state, state, canonical_json(state))


NODE_CLASS_MAPPINGS = {
    "LF_VNState": LF_VNState,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_VNState": "VN State",
}
