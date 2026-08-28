from .contracts import CATEGORY, FUNCTION, Input
from .core import (
    VNContractError,
    canonical_json,
    compile_graph,
    format_compile_summary,
    normalize_state,
    preview_bundle,
)


def _safe_send_sync(event: str, data: dict, node_id: str | None = None) -> None:
    """Emit observational UI state only when Comfy is already the host."""

    try:
        import sys

        if sys.modules.get("server") is None:
            return
        from ...utils.helpers.comfy import safe_send_sync

        safe_send_sync(event, data, node_id)
    except Exception:
        # VN compilation is intentionally usable in CPU-only/headless tooling.
        # UI delivery must not import Comfy or optional native/provider modules.
        return


class LF_VNCompile:
    """Compile declarations and preview one fixture without target-specific lowering."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "graph": (
                    Input.LF_VN_GRAPH,
                    {
                        "forceInput": True,
                        "tooltip": "Complete authored declaration chain.",
                    },
                ),
                "state": (
                    Input.LF_VN_STATE,
                    {
                        "forceInput": True,
                        "tooltip": "Fixture state used for preview only; it is not embedded in the authored bundle.",
                    },
                ),
                "workflow_id": (
                    Input.LF_ID,
                    {
                        "default": "",
                        "lf_id_kind": "workflow",
                        "tooltip": "LF-owned persistent workflow declaration identity. Generated once by the authoring UI.",
                    },
                ),
                "entry_scene_id": (
                    Input.LF_REF,
                    {
                        "default": "",
                        "lf_ref_kind": "scene",
                        "tooltip": "Bundle-local entry scene reference. Choose by friendly label or connect a scene_ref output.",
                    },
                ),
                "selected_choice_id": (
                    Input.LF_REF,
                    {
                        "default": "",
                        "lf_ref_kind": "choice",
                        "tooltip": "Optional choice reference from the active scene to replay once against the fixture.",
                    },
                ),
            },
            "optional": {
                "ui_widget": (Input.LF_CODE, {"default": ""}),
            },
            "hidden": {"node_id": "UNIQUE_ID"},
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_NODE = True
    OUTPUT_TOOLTIPS = (
        "Deterministic target-neutral VN bundle.",
        "Fixture preview before and after the optional selected choice.",
        "Machine-readable structural validation report.",
        "Derived immutable state after replaying supported core effects once.",
        "Canonical bundle JSON used for byte-identity checks.",
    )
    RETURN_NAMES = ("bundle", "preview", "validation", "derived_state", "canonical_bundle")
    RETURN_TYPES = (
        Input.LF_VN_BUNDLE,
        Input.JSON,
        Input.JSON,
        Input.LF_VN_STATE,
        Input.STRING,
    )

    def on_exec(self, **kwargs: dict):
        node_id = kwargs.get("node_id")
        state = normalize_state(kwargs.get("state"))
        bundle, report = compile_graph(
            graph=kwargs.get("graph"),
            workflow_id=kwargs.get("workflow_id", ""),
            entry_scene_id=kwargs.get("entry_scene_id", ""),
        )
        if report["status"] != "complete":
            summary = format_compile_summary(report)
            _safe_send_sync("vncompile", {"value": summary}, node_id)
            raise VNContractError(report)

        try:
            preview, derived_state = preview_bundle(
                bundle=bundle,
                state=state,
                selected_choice_id=kwargs.get("selected_choice_id", ""),
            )
        except VNContractError as error:
            preview_report = {
                "schema": report["schema"],
                "status": "blocked",
                "source": report["source"],
                "counts": report["counts"],
                "errors": error.payload.get("errors", []),
                "warnings": report["warnings"],
            }
            _safe_send_sync(
                "vncompile",
                {"value": format_compile_summary(preview_report)},
                node_id,
            )
            raise

        summary = format_compile_summary(report, preview)
        _safe_send_sync("vncompile", {"value": summary}, node_id)
        return {
            "ui": {
                "lf_output": [
                    {
                        "bundle": bundle,
                        "preview": preview,
                        "validation": report,
                    }
                ]
            },
            "result": (
                bundle,
                preview,
                report,
                derived_state,
                canonical_json(bundle),
            ),
        }


NODE_CLASS_MAPPINGS = {
    "LF_VNCompile": LF_VNCompile,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_VNCompile": "Compile VN",
}
