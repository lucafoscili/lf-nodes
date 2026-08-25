import json
import logging
import re

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List

from .readiness import WorkflowReadinessScanner, evaluate_workflow_readiness
from ..utils.prompt import json_safe, workflow_to_prompt as _workflow_to_prompt

_LOG = logging.getLogger(__name__)

# region Exceptions
class InputValidationError(ValueError):
    def __init__(self, input_name: str | None = None):
        super().__init__(f"Missing required input {input_name}.")
        self.input_name = input_name
# endregion

# region Dataset
_PROVIDER_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


@dataclass(frozen=True, slots=True)
class WorkflowSubmissionPolicy:
    """Trusted resource policy for one workflow's queue submission.

    Policies live on server-registered workflow definitions. They are not
    serialized into the browser-facing workflow catalogue, so request inputs
    cannot alter admission authority or resource estimates.
    """

    provider_id: str
    expected_vram_mb: int
    max_duration_seconds: int
    required: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.provider_id, str) or not _PROVIDER_ID_PATTERN.fullmatch(
            self.provider_id
        ):
            raise ValueError(
                "provider_id must be a non-empty identifier of at most 128 "
                "ASCII letters, digits, dots, underscores, or hyphens"
            )
        if type(self.expected_vram_mb) is not int or self.expected_vram_mb <= 0:
            raise ValueError("expected_vram_mb must be a positive integer")
        if (
            type(self.max_duration_seconds) is not int
            or self.max_duration_seconds <= 0
        ):
            raise ValueError("max_duration_seconds must be a positive integer")
        if type(self.required) is not bool:
            raise TypeError("required must be a boolean")

    @property
    def fail_closed(self) -> bool:
        """Whether provider failure must prevent direct queue submission."""

        return self.required


@dataclass
class WorkflowCell:
    id: str
    node_id: str
    shape: str = ""
    value: str = ""
    description: str = ""
    props: Dict[str, Any] = field(default_factory=dict)
    required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "nodeId": self.node_id,
            "shape": self.shape,
        }
        if self.props:
            data["props"] = json_safe(self.props)
        if self.value:
            data["value"] = self.value
        if self.description:
            data["title"] = self.description
        if not self.required:
            data["required"] = False

        return json_safe(data)

@dataclass
class WorkflowNode:
    id: str
    value: str
    description: str
    inputs: Iterable[WorkflowCell]
    outputs: Iterable[WorkflowCell]
    configure_prompt: Callable[[Dict[str, Any], Dict[str, Any]], None]
    workflow_path: Path
    category: str
    submission_policy: WorkflowSubmissionPolicy | None = None
    origin: str = "custom"
    collection: str = "Custom"
    configure_download: Callable[[Dict[str, Any], Dict[str, Any]], None] | None = None

    def __post_init__(self) -> None:
        if self.submission_policy is not None and not isinstance(
            self.submission_policy,
            WorkflowSubmissionPolicy,
        ):
            raise TypeError(
                "submission_policy must be a WorkflowSubmissionPolicy or None"
            )

    def load_prompt(self) -> Dict[str, Any]:
        with self.workflow_path.open("r", encoding="utf-8") as workflow_file:
            workflow_graph = json.load(workflow_file)
        # Delegate to the conversion helper already available in utils
        return _workflow_to_prompt(workflow_graph)

    def cells_as_dict(self, input_output: str) -> Dict[str, Any]:
        if input_output == "inputs":
            return {cell.id: cell.to_dict() for cell in self.inputs}
        elif input_output == "outputs":
            return {cell.id: cell.to_dict() for cell in self.outputs}
        return {}
# endregion

# region Registry
class WorkflowRegistry:
    def __init__(self) -> None:
        self._definitions: Dict[str, WorkflowNode] = {}
        self._provenance: Dict[str, tuple[str, str]] = {}

    def register(
        self,
        definition: WorkflowNode,
        *,
        origin: str | None = None,
        collection: str | None = None,
    ) -> None:
        previous = self._definitions.get(definition.id)
        if previous is not None and previous is not definition:
            _LOG.warning(
                "Workflow definition %r replaces an existing registration",
                definition.id,
            )
        # Registering an object is not proof that it belongs to LF's packaged
        # catalogue. Only the trusted module loader passes shipped provenance
        # explicitly; every direct/legacy registration fails closed to Custom.
        resolved_origin = origin
        if resolved_origin not in {"shipped", "custom"}:
            # Unmarked duck-typed registrations are not part of LF's packaged
            # catalogue. Keep them visible, but fail closed into Custom.
            resolved_origin = "custom"

        resolved_collection = collection
        if not isinstance(resolved_collection, str):
            resolved_collection = ""
        resolved_collection = " ".join(resolved_collection.split())
        if (
            not resolved_collection
            or len(resolved_collection) > 80
            or any(ord(char) < 32 for char in resolved_collection)
        ):
            resolved_collection = "LF Nodes" if resolved_origin == "shipped" else "Custom"

        self._definitions[definition.id] = definition
        self._provenance[definition.id] = (
            resolved_origin,
            resolved_collection,
        )

    def list(self) -> Dict[str, List[Dict[str, Any]]]:
        nodes: List[Dict[str, Any]] = []
        readiness_scanner = WorkflowReadinessScanner()
        for definition in self._definitions.values():
            origin, collection = self._provenance.get(
                definition.id,
                ("custom", "Custom"),
            )
            workflow_node = {
                "id": definition.id,
                "value": definition.value,
                "description": definition.description,
                "category": definition.category,
                "origin": origin,
                "collection": collection,
                "readiness": evaluate_workflow_readiness(
                    definition,
                    scanner=readiness_scanner,
                ),
                "children": [{
                    "id": f"{definition.id}:inputs",
                    "value": "Inputs",
                    "description": "Workflow inputs",
                    "cells": definition.cells_as_dict("inputs"),
                    },{
                    "id": f"{definition.id}:outputs",
                    "value": "Outputs",
                    "description": "Workflow outputs",
                    "cells": definition.cells_as_dict("outputs"),
                    },
                ],
            }
            nodes.append(workflow_node)

        return {
            "columns": [],
            "nodes": nodes,
        }
    
    def get(self, id: str) -> WorkflowNode | None:
        return self._definitions.get(id)

    def get_submission_policy(self, id: str) -> WorkflowSubmissionPolicy | None:
        definition = self.get(id)
        if definition is None:
            return None

        policy = getattr(definition, "submission_policy", None)
        if policy is not None and not isinstance(policy, WorkflowSubmissionPolicy):
            raise TypeError(
                f"Workflow definition '{id}' has an invalid submission policy."
            )
        return policy

REGISTRY = WorkflowRegistry()

def _is_workflow_definition(definition: object) -> bool:
    if isinstance(definition, WorkflowNode):
        return True

    required_attrs = (
        "id",
        "value",
        "description",
        "workflow_path",
        "inputs",
        "outputs",
        "configure_prompt",
    )
    required_methods = ("load_prompt", "cells_as_dict")

    return all(hasattr(definition, attr) for attr in (*required_attrs, *required_methods))

def _register_packaged_workflows() -> None:
    """
    Import workflow definitions located in the workflows subpackage and add them to the registry.

    Keeping the import local prevents circular imports while registry types are still being defined.
    """
    from ..workflows import iter_workflow_definitions

    for definition in iter_workflow_definitions():
        if not _is_workflow_definition(definition):
            raise TypeError(
                f"Workflow definition '{definition!r}' is not compatible with WorkflowNode."
            )
        REGISTRY.register(  # type: ignore[arg-type]
            definition,
            origin=getattr(definition, "origin", "custom"),
            collection=getattr(definition, "collection", "Custom"),
        )

_registered = False

def _ensure_registered() -> None:
    global _registered
    if _registered:
        return
    _register_packaged_workflows()
    _registered = True
def list_workflows() -> List[Dict[str, Any]]:
    _ensure_registered()
    return REGISTRY.list()

def get_workflow(id: str) -> WorkflowNode | None:
    _ensure_registered()
    return REGISTRY.get(id)

def get_workflow_submission_policy(id: str) -> WorkflowSubmissionPolicy | None:
    """Return trusted admission metadata for a registered workflow, if any."""

    _ensure_registered()
    return REGISTRY.get_submission_policy(id)
# endregion
