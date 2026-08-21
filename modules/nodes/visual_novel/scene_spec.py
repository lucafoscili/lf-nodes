from .contracts import CATEGORY, FUNCTION, Input
from .core import (
    append_declaration,
    build_scene_declaration,
    normalize_scene_body,
)


_DEFAULT_BODY = """{
  "participants": [],
  "entryPredicate": {},
  "beats": [
    {
      "text": "A new story begins."
    }
  ],
  "choices": [],
  "artRequests": []
}"""


class LF_SceneSpec:
    """Append one provider- and target-neutral scene declaration."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scene_id": (
                    Input.LF_ID,
                    {
                        "default": "",
                        "lf_id_kind": "scene",
                        "lf_label_widget": "title",
                        "tooltip": "LF-owned persistent scene identity. Generated once by the authoring UI.",
                    },
                ),
                "title": (
                    Input.STRING,
                    {
                        "default": "Opening",
                        "tooltip": "Optional author-facing scene title.",
                    },
                ),
                "scene_body": (
                    Input.LF_TEXTAREA,
                    {
                        "default": _DEFAULT_BODY,
                        "lf_id_paths": [
                            {"path": "/beats/*", "kind": "beat"},
                            {"path": "/choices/*", "kind": "choice", "label": "label"},
                            {"path": "/choices/*/effects/*", "kind": "effect"},
                            {"path": "/artRequests/*", "kind": "art-request"},
                        ],
                        "lf_ref_paths": [
                            {"path": "/choices/*/nextSceneId", "kind": "scene"},
                        ],
                        "tooltip": "One strict-JSON scene body containing participants, entryPredicate, beats, choices, and artRequests. Missing LF-owned child IDs are materialized only by the authoring UI after valid JSON.",
                    },
                ),
            },
            "optional": {
                "graph": (
                    Input.LF_VN_GRAPH,
                    {
                        "forceInput": True,
                        "tooltip": "An existing declaration chain. Narrative transitions remain symbolic, so this execution chain may stay linear.",
                    },
                ),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "Declaration chain with this scene appended in authored order.",
        "Validated scene declaration through a generic JSON socket.",
        "Persistent scene reference for typed LF_REF connections.",
    )
    RETURN_NAMES = ("graph", "scene", "scene_ref")
    RETURN_TYPES = (Input.LF_VN_GRAPH, Input.JSON, Input.LF_REF)

    def on_exec(self, **kwargs: dict):
        body = normalize_scene_body(kwargs.get("scene_body", "{}"))
        scene = build_scene_declaration(
            scene_id=kwargs.get("scene_id", ""),
            title=str(kwargs.get("title", "")),
            participants=body.get("participants"),
            entry_predicate=body.get("entryPredicate"),
            beats=body.get("beats"),
            choices=body.get("choices"),
            art_requests=body.get("artRequests"),
            source_node_id=kwargs.get("node_id"),
        )
        graph = append_declaration(kwargs.get("graph"), scene)
        return (graph, scene, scene["id"])


NODE_CLASS_MAPPINGS = {
    "LF_SceneSpec": LF_SceneSpec,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_SceneSpec": "Scene Spec",
}
