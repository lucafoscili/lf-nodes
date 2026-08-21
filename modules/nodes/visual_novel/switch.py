from .contracts import CATEGORY, FUNCTION, Input
from .core import (
    append_declaration,
    build_switch_declaration,
    evaluate_switch,
    normalize_switch_body,
    normalize_state,
)


_DEFAULT_BODY = """{
  "cases": [
    {
      "when": {},
      "targetSceneId": ""
    }
  ],
  "fallback": null
}"""


class LF_VNSwitch:
    """Preserve every authored route while selecting one fixture preview."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "state": (
                    Input.LF_VN_STATE,
                    {
                        "forceInput": True,
                        "tooltip": "Fixture state used only to preview route selection.",
                    },
                ),
                "switch_id": (
                    Input.LF_ID,
                    {
                        "default": "",
                        "lf_id_kind": "switch",
                        "tooltip": "LF-owned persistent switch identity. Generated once by the authoring UI.",
                    },
                ),
                "switch_body": (
                    Input.LF_TEXTAREA,
                    {
                        "default": _DEFAULT_BODY,
                        "lf_id_paths": [
                            {"path": "/cases/*", "kind": "switch-case"},
                            {"path": "/fallback", "kind": "switch-fallback"},
                        ],
                        "lf_ref_paths": [
                            {"path": "/cases/*/targetSceneId", "kind": "scene"},
                            {"path": "/fallback/targetSceneId", "kind": "scene"},
                        ],
                        "tooltip": "One strict-JSON switch body containing ordered cases and an explicit fallback object or null.",
                    },
                ),
            },
            "optional": {
                "graph": (
                    Input.LF_VN_GRAPH,
                    {
                        "forceInput": True,
                        "tooltip": "Existing declaration chain.",
                    },
                ),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "Declaration chain retaining every switch case and explicit fallback.",
        "Selected preview case, or an empty object when unmatched.",
        "Selected target scene reference, or an empty string when unmatched.",
        "Machine-readable case evaluation trace.",
    )
    RETURN_NAMES = ("graph", "selected_case", "target_scene_id", "preview_report")
    RETURN_TYPES = (Input.LF_VN_GRAPH, Input.JSON, Input.LF_REF, Input.JSON)

    def on_exec(self, **kwargs: dict):
        state = normalize_state(kwargs.get("state"))
        body = normalize_switch_body(kwargs.get("switch_body", "{}"))
        declaration = build_switch_declaration(
            switch_id=kwargs.get("switch_id", ""),
            cases=body.get("cases"),
            fallback=body.get("fallback"),
            source_node_id=kwargs.get("node_id"),
        )
        selected, report = evaluate_switch(declaration, state)
        graph = append_declaration(kwargs.get("graph"), declaration)
        target_scene_id = selected["targetSceneId"] if selected else ""
        return (graph, selected or {}, target_scene_id, report)


NODE_CLASS_MAPPINGS = {
    "LF_VNSwitch": LF_VNSwitch,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_VNSwitch": "VN Switch",
}
