import json
import logging
import math
import re

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping

from .definition_inputs import default_input_values, select_option_value
from .readiness import (
    MAX_READINESS_ISSUES,
    READINESS_READY,
    READINESS_SETUP_REQUIRED,
    READINESS_WARNING,
    WorkflowReadinessScanner,
    evaluate_input_option_requirement,
    evaluate_workflow_readiness,
    filter_unavailable_input_options,
    normalize_model_relative_path,
    selected_input_option_requirements,
)
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
_INPUT_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_HERO_ASSET_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]*(?:/[A-Za-z0-9][A-Za-z0-9._-]*)*$"
)
_HERO_RASTER_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".avif")


def _normalized_identifier(value: object, *, label: str) -> str:
    normalized = value.strip() if isinstance(value, str) else ""
    if not _INPUT_ID_PATTERN.fullmatch(normalized):
        raise ValueError(
            f"{label} must be a non-empty identifier of at most 128 ASCII "
            "letters, digits, dots, underscores, or hyphens"
        )
    return normalized


def _normalized_visible_text(value: object, *, label: str, limit: int) -> str:
    normalized = " ".join(value.split()) if isinstance(value, str) else ""
    if (
        not normalized
        or len(normalized) > limit
        or any(ord(char) < 32 or ord(char) == 127 for char in normalized)
    ):
        raise ValueError(f"{label} must contain 1 to {limit} visible characters")
    return normalized


@dataclass(frozen=True, slots=True)
class WorkflowHeroImage:
    """One curated raster, relative to ``assets/workflow-runner/heroes``.

    The image may be one result or a labelled before/after composition. Asset
    identity and output provenance are curated separately; catalogue rendering
    never opens files or resolves private run history.
    """

    asset: str
    alt: str

    def __post_init__(self) -> None:
        asset = self.asset.strip() if isinstance(self.asset, str) else ""
        if (
            not asset
            or len(asset) > 240
            or ".." in asset
            or not _HERO_ASSET_PATTERN.fullmatch(asset)
            or any(part.endswith(".") for part in asset.split("/"))
            or not asset.lower().endswith(_HERO_RASTER_EXTENSIONS)
        ):
            raise ValueError(
                "hero asset must be a simple relative PNG, JPEG, WebP, or AVIF "
                "path below assets/workflow-runner/heroes"
            )
        object.__setattr__(self, "asset", asset)
        object.__setattr__(
            self,
            "alt",
            _normalized_visible_text(self.alt, label="hero alt", limit=500),
        )


@dataclass(frozen=True, slots=True)
class WorkflowCardPresentation:
    """Optional catalogue copy and a single curated cover image."""

    summary: str
    hero: WorkflowHeroImage | None = None

    def __post_init__(self) -> None:
        summary = _normalized_visible_text(
            self.summary,
            label="card summary",
            limit=180,
        )
        if self.summary.splitlines() != [self.summary]:
            raise ValueError("card summary must not contain newlines")
        object.__setattr__(self, "summary", summary)
        if self.hero is not None and not isinstance(self.hero, WorkflowHeroImage):
            raise TypeError("card hero must be a WorkflowHeroImage or None")


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


@dataclass(frozen=True, slots=True)
class WorkflowModelAsset:
    """One explicitly declared local model asset used by a workflow.

    ``relative_paths`` are portable paths below ComfyUI's configured model
    root.  Grouping the files lets readiness report one useful setup issue for
    a multi-file model package without exposing host-specific absolute paths.
    """

    label: str
    relative_paths: tuple[str, ...]

    def __post_init__(self) -> None:
        normalized_label = " ".join(self.label.split()) if isinstance(self.label, str) else ""
        if not normalized_label or len(normalized_label) > 120:
            raise ValueError("model asset label must contain 1 to 120 visible characters")
        if any(ord(char) < 32 or ord(char) == 127 for char in normalized_label):
            raise ValueError("model asset label must not contain control characters")

        if isinstance(self.relative_paths, (str, bytes)):
            raise TypeError("model asset relative_paths must be a sequence of paths")
        normalized_paths = tuple(
            normalize_model_relative_path(path) for path in self.relative_paths
        )
        if not normalized_paths:
            raise ValueError("model asset must declare at least one relative path")
        if len(set(normalized_paths)) != len(normalized_paths):
            raise ValueError("model asset relative paths must be unique")

        object.__setattr__(self, "label", normalized_label)
        object.__setattr__(self, "relative_paths", normalized_paths)


@dataclass(frozen=True, slots=True)
class WorkflowInputOptionRequirement:
    """Host prerequisites for one optional workflow input choice.

    The base workflow remains runnable when an optional recipe is unavailable.
    Catalogue serialization can omit only the affected choice, while execution
    re-checks the same trusted declaration for headless callers.
    """

    input_id: str
    option_value: str | int
    required_node_types: tuple[str, ...] = ()
    required_model_assets: tuple[WorkflowModelAsset, ...] = ()

    def __post_init__(self) -> None:
        input_id = self.input_id.strip() if isinstance(self.input_id, str) else ""
        if not _INPUT_ID_PATTERN.fullmatch(input_id):
            raise ValueError("input option requirement needs a valid input id")

        option_value = self.option_value
        if isinstance(option_value, str):
            option_value = option_value.strip()
            if (
                not option_value
                or len(option_value) > 256
                or any(ord(char) < 32 or ord(char) == 127 for char in option_value)
            ):
                raise ValueError("input option requirement needs a bounded option value")
        elif type(option_value) is not int:
            raise TypeError("input option requirement value must be a string or integer")

        if isinstance(self.required_node_types, (str, bytes)):
            raise TypeError("required_node_types must be a sequence")
        raw_node_types = tuple(self.required_node_types)
        node_types = tuple(
            node_type.strip()
            for node_type in raw_node_types
            if isinstance(node_type, str) and node_type.strip()
        )
        if (
            len(node_types) != len(raw_node_types)
            or len(set(node_types)) != len(node_types)
            or any(
                len(node_type) > 200
                or any(ord(char) < 32 or ord(char) == 127 for char in node_type)
                for node_type in node_types
            )
        ):
            raise ValueError("required_node_types must contain unique bounded node names")

        if isinstance(self.required_model_assets, (str, bytes)):
            raise TypeError("required_model_assets must be a sequence")
        model_assets = tuple(self.required_model_assets)
        if not all(isinstance(asset, WorkflowModelAsset) for asset in model_assets):
            raise TypeError(
                "required_model_assets must contain WorkflowModelAsset values"
            )
        if not node_types and not model_assets:
            raise ValueError("input option requirement must declare a prerequisite")

        object.__setattr__(self, "input_id", input_id)
        object.__setattr__(self, "option_value", option_value)
        object.__setattr__(self, "required_node_types", node_types)
        object.__setattr__(self, "required_model_assets", model_assets)


@dataclass
class WorkflowCell:
    id: str
    node_id: str
    shape: str = ""
    value: str = ""
    description: str = ""
    props: Dict[str, Any] = field(default_factory=dict)
    required: bool = True
    advanced: bool = False

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
        if self.advanced:
            data["advanced"] = True

        return json_safe(data)


@dataclass(frozen=True, slots=True)
class WorkflowSequencePublicInputBinding:
    """Bind one sequence-level input to one block input."""

    target_input_id: str
    public_input_id: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "target_input_id",
            _normalized_identifier(
                self.target_input_id,
                label="sequence binding target input id",
            ),
        )
        object.__setattr__(
            self,
            "public_input_id",
            _normalized_identifier(
                self.public_input_id,
                label="sequence public input id",
            ),
        )


@dataclass(frozen=True, slots=True)
class WorkflowSequenceLiteralBinding:
    """Bind one immutable JSON scalar directly to one block input."""

    target_input_id: str
    value: str | int | float | bool | None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "target_input_id",
            _normalized_identifier(
                self.target_input_id,
                label="sequence binding target input id",
            ),
        )
        value = self.value
        if isinstance(value, str):
            if len(value) > 100_000 or "\x00" in value:
                raise ValueError(
                    "sequence literal strings must be bounded and contain no NUL"
                )
        elif type(value) is float:
            if not math.isfinite(value):
                raise ValueError("sequence literal floats must be finite")
        elif value is not None and type(value) not in {bool, int}:
            raise TypeError("sequence literals must be immutable JSON scalar values")


@dataclass(frozen=True, slots=True)
class WorkflowSequenceArtifactBinding:
    """Feed one artifact from an earlier block into an upload.

    Omitting ``source_stage_id`` preserves the original linear contract: the
    artifact comes from the immediately previous stage.  Naming a stage keeps
    orchestras sequential while allowing bounded fan-out and fan-in without a
    second graph scheduler.
    """

    target_input_id: str
    output_id: str
    source_stage_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "target_input_id",
            _normalized_identifier(
                self.target_input_id,
                label="sequence binding target input id",
            ),
        )
        object.__setattr__(
            self,
            "output_id",
            _normalized_identifier(
                self.output_id,
                label="sequence artifact output id",
            ),
        )
        if self.source_stage_id is not None:
            object.__setattr__(
                self,
                "source_stage_id",
                _normalized_identifier(
                    self.source_stage_id,
                    label="sequence artifact source stage id",
                ),
            )


@dataclass(frozen=True, slots=True)
class WorkflowSequenceTextBinding:
    """Feed one durable text output from an earlier block into a text input."""

    target_input_id: str
    output_id: str
    source_stage_id: str | None = None

    def __post_init__(self) -> None:
        for name in ("target_input_id", "output_id", "source_stage_id"):
            value = getattr(self, name)
            if name == "source_stage_id" and value is None:
                continue
            object.__setattr__(
                self, name,
                _normalized_identifier(value, label=f"sequence text {name}"),
            )


WorkflowSequenceBinding = (
    WorkflowSequencePublicInputBinding
    | WorkflowSequenceLiteralBinding
    | WorkflowSequenceArtifactBinding
    | WorkflowSequenceTextBinding
)


@dataclass(frozen=True, slots=True)
class WorkflowSequenceStage:
    """One ordinary workflow block in a linear sequence."""

    id: str
    workflow_id: str
    bindings: tuple[WorkflowSequenceBinding, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "id",
            _normalized_identifier(self.id, label="sequence stage id"),
        )
        object.__setattr__(
            self,
            "workflow_id",
            _normalized_identifier(
                self.workflow_id,
                label="sequence stage workflow id",
            ),
        )
        if isinstance(self.bindings, (str, bytes)):
            raise TypeError("sequence stage bindings must be a sequence")
        bindings = tuple(self.bindings)
        if not all(
            isinstance(
                binding,
                (
                    WorkflowSequencePublicInputBinding,
                    WorkflowSequenceLiteralBinding,
                    WorkflowSequenceArtifactBinding,
                    WorkflowSequenceTextBinding,
                ),
            )
            for binding in bindings
        ):
            raise TypeError("sequence stage contains an invalid binding")
        targets = [binding.target_input_id for binding in bindings]
        if len(set(targets)) != len(targets):
            raise ValueError(
                "sequence stage bindings must not overlap on a target input"
            )
        object.__setattr__(self, "bindings", bindings)


@dataclass(frozen=True, slots=True)
class WorkflowSequenceNode:
    """A graph-free, linear assembly of registered ordinary workflows.

    A sequence deliberately owns no prompt graph, model declarations,
    configuration callback, download callback, or submission policy. Each
    stage keeps those responsibilities in its referenced workflow block.
    """

    id: str
    value: str
    description: str
    inputs: tuple[WorkflowCell, ...]
    stages: tuple[WorkflowSequenceStage, ...]
    final_output_ids: tuple[str, ...]
    category: str
    origin: str = "custom"
    collection: str = "Custom"
    card: WorkflowCardPresentation | None = None

    def __post_init__(self) -> None:
        if self.card is not None and not isinstance(self.card, WorkflowCardPresentation):
            raise TypeError("card must be a WorkflowCardPresentation or None")
        object.__setattr__(
            self,
            "id",
            _normalized_identifier(self.id, label="sequence id"),
        )
        object.__setattr__(
            self,
            "value",
            _normalized_visible_text(
                self.value,
                label="sequence value",
                limit=120,
            ),
        )
        object.__setattr__(
            self,
            "description",
            _normalized_visible_text(
                self.description,
                label="sequence description",
                limit=1_000,
            ),
        )
        object.__setattr__(
            self,
            "category",
            _normalized_visible_text(
                self.category,
                label="sequence category",
                limit=80,
            ),
        )

        if isinstance(self.inputs, (str, bytes)):
            raise TypeError("sequence inputs must be a sequence")
        inputs = tuple(self.inputs)
        if not all(isinstance(cell, WorkflowCell) for cell in inputs):
            raise TypeError("sequence inputs must contain WorkflowCell values")
        input_ids = [
            _normalized_identifier(cell.id, label="sequence input id")
            for cell in inputs
        ]
        if len(set(input_ids)) != len(input_ids):
            raise ValueError("sequence input ids must be unique")

        if isinstance(self.stages, (str, bytes)):
            raise TypeError("sequence stages must be a sequence")
        stages = tuple(self.stages)
        if not 2 <= len(stages) <= 8:
            raise ValueError("a workflow sequence must contain between 2 and 8 stages")
        if not all(isinstance(stage, WorkflowSequenceStage) for stage in stages):
            raise TypeError("sequence stages must contain WorkflowSequenceStage values")
        stage_ids = [stage.id for stage in stages]
        if len(set(stage_ids)) != len(stage_ids):
            raise ValueError("sequence stage ids must be unique")

        if isinstance(self.final_output_ids, (str, bytes)):
            raise TypeError("sequence final_output_ids must be a sequence")
        final_output_ids = tuple(
            _normalized_identifier(output_id, label="sequence final output id")
            for output_id in self.final_output_ids
        )
        if not final_output_ids:
            raise ValueError("a workflow sequence must expose at least one final output")
        if len(set(final_output_ids)) != len(final_output_ids):
            raise ValueError("sequence final output ids must be unique")

        object.__setattr__(self, "inputs", inputs)
        object.__setattr__(self, "stages", stages)
        object.__setattr__(self, "final_output_ids", final_output_ids)

    def cells_as_dict(self, input_output: str) -> Dict[str, Any]:
        if input_output == "inputs":
            return {cell.id: cell.to_dict() for cell in self.inputs}
        # Final output cells belong to the last registered block and are
        # projected by WorkflowRegistry after cross-definition validation.
        return {}

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
    required_model_assets: tuple[WorkflowModelAsset, ...] = ()
    input_option_requirements: tuple[WorkflowInputOptionRequirement, ...] = ()
    card: WorkflowCardPresentation | None = None

    def __post_init__(self) -> None:
        if self.card is not None and not isinstance(self.card, WorkflowCardPresentation):
            raise TypeError("card must be a WorkflowCardPresentation or None")
        if self.submission_policy is not None and not isinstance(
            self.submission_policy,
            WorkflowSubmissionPolicy,
        ):
            raise TypeError(
                "submission_policy must be a WorkflowSubmissionPolicy or None"
            )
        if isinstance(self.required_model_assets, (str, bytes)):
            raise TypeError("required_model_assets must be a sequence")
        assets = tuple(self.required_model_assets)
        if not all(isinstance(asset, WorkflowModelAsset) for asset in assets):
            raise TypeError("required_model_assets must contain WorkflowModelAsset values")
        object.__setattr__(self, "required_model_assets", assets)

        if isinstance(self.input_option_requirements, (str, bytes)):
            raise TypeError("input_option_requirements must be a sequence")
        option_requirements = tuple(self.input_option_requirements)
        if not all(
            isinstance(requirement, WorkflowInputOptionRequirement)
            for requirement in option_requirements
        ):
            raise TypeError(
                "input_option_requirements must contain "
                "WorkflowInputOptionRequirement values"
            )
        keys = [
            (requirement.input_id, requirement.option_value)
            for requirement in option_requirements
        ]
        if len(set(keys)) != len(keys):
            raise ValueError("input option requirements must target unique options")

        defaults = default_input_values(self)
        if any(
            defaults.get(requirement.input_id, object())
            == requirement.option_value
            for requirement in option_requirements
        ):
            raise ValueError(
                "input option requirements must not target a workflow default"
            )
        object.__setattr__(self, "input_option_requirements", option_requirements)

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


# Author-facing vocabulary.  Keep the original class names as exact aliases so
# existing declarations, isinstance checks, persistence, and embedders remain
# compatible while new catalogue code can say what the definitions actually are.
WorkflowBlockNode = WorkflowNode
WorkflowOrchestraNode = WorkflowSequenceNode
# endregion

# region Registry
class WorkflowRegistry:
    def __init__(self) -> None:
        self._definitions: Dict[str, WorkflowNode | WorkflowSequenceNode] = {}
        self._provenance: Dict[str, tuple[str, str]] = {}

    @staticmethod
    def _ports(
        definition: WorkflowNode,
        input_output: str,
        *,
        workflow_id: str,
    ) -> dict[str, WorkflowCell]:
        raw_cells = definition.inputs if input_output == "inputs" else definition.outputs
        try:
            cells = tuple(raw_cells)
        except TypeError as exc:
            raise ValueError(
                f"Referenced workflow '{workflow_id}' has invalid {input_output}."
            ) from exc
        if not all(isinstance(cell, WorkflowCell) for cell in cells):
            raise TypeError(
                f"Referenced workflow '{workflow_id}' has non-WorkflowCell "
                f"{input_output}."
            )
        ids = [cell.id for cell in cells]
        if len(set(ids)) != len(ids):
            raise ValueError(
                f"Referenced workflow '{workflow_id}' has duplicate "
                f"{input_output} ports."
            )
        return {cell.id: cell for cell in cells}

    @classmethod
    def _validate_sequence(
        cls,
        sequence: WorkflowSequenceNode,
        definitions: Mapping[str, WorkflowNode | WorkflowSequenceNode],
    ) -> None:
        public_inputs = {cell.id: cell for cell in sequence.inputs}
        stage_ids = [stage.id for stage in sequence.stages]
        blocks: list[WorkflowNode] = []

        for stage in sequence.stages:
            block = definitions.get(stage.workflow_id)
            if block is None:
                raise ValueError(
                    f"Sequence stage '{stage.id}' references unregistered workflow "
                    f"'{stage.workflow_id}'."
                )
            if not isinstance(block, WorkflowNode):
                raise ValueError(
                    f"Sequence stage '{stage.id}' must reference an ordinary "
                    "WorkflowNode; sequence nesting is not supported."
                )
            if not callable(block.configure_download):
                raise ValueError(
                    f"Sequence stage '{stage.id}' references workflow "
                    f"'{stage.workflow_id}' without a portable configure_download "
                    "callback required for preflight."
                )
            blocks.append(block)

        for index, (stage, block) in enumerate(zip(sequence.stages, blocks)):
            target_inputs = cls._ports(
                block,
                "inputs",
                workflow_id=stage.workflow_id,
            )
            bound_target_ids = {
                binding.target_input_id for binding in stage.bindings
            }

            for binding in stage.bindings:
                target = target_inputs.get(binding.target_input_id)
                if target is None:
                    raise ValueError(
                        f"Sequence stage '{stage.id}' binds unknown input port "
                        f"'{binding.target_input_id}'."
                    )
                if isinstance(binding, WorkflowSequencePublicInputBinding):
                    if binding.public_input_id not in public_inputs:
                        raise ValueError(
                            f"Sequence stage '{stage.id}' references unknown public "
                            f"input '{binding.public_input_id}'."
                        )
                elif isinstance(binding, (WorkflowSequenceArtifactBinding, WorkflowSequenceTextBinding)):
                    kind = "text" if isinstance(binding, WorkflowSequenceTextBinding) else "artifact"
                    if index == 0:
                        raise ValueError(
                            f"The first sequence stage cannot bind a previous {kind}."
                        )
                    source_stage_id = binding.source_stage_id
                    if source_stage_id is None:
                        source_index = index - 1
                        source_description = "the immediately previous workflow"
                    else:
                        try:
                            source_index = stage_ids.index(source_stage_id)
                        except ValueError as exc:
                            raise ValueError(
                                f"Sequence stage '{stage.id}' references unknown source "
                                f"stage '{source_stage_id}'."
                            ) from exc
                        if source_index == index:
                            raise ValueError(
                                f"Sequence stage '{stage.id}' cannot consume an "
                                f"{kind} from itself."
                            )
                        if source_index > index:
                            raise ValueError(
                                f"Sequence stage '{stage.id}' references future source "
                                f"stage '{source_stage_id}'; only earlier stages may "
                                f"provide {kind} outputs."
                            )
                        source_description = f"source stage '{source_stage_id}'"

                    source_outputs = cls._ports(
                        blocks[source_index],
                        "outputs",
                        workflow_id=sequence.stages[source_index].workflow_id,
                    )
                    if binding.output_id not in source_outputs:
                        raise ValueError(
                            f"Sequence stage '{stage.id}' references unknown output "
                            f"port '{binding.output_id}' on {source_description}."
                        )
                    if kind == "text":
                        if target.shape not in {"textarea", "textfield"}:
                            raise ValueError(
                                f"Sequence text target '{stage.id}.{binding.target_input_id}' "
                                "must be a textarea or textfield input."
                            )
                        if source_outputs[binding.output_id].shape not in {"code", "textarea", "textfield"}:
                            raise ValueError(
                                f"Sequence text output '{binding.output_id}' on "
                                f"{source_description} must be a text display."
                            )
                    elif target.shape != "upload":
                        raise ValueError(
                            f"Sequence artifact target '{stage.id}."
                            f"{binding.target_input_id}' must be an upload input."
                        )

            unresolved_required_inputs = [
                input_id
                for input_id, cell in target_inputs.items()
                if cell.required
                and input_id not in bound_target_ids
                and not (
                    isinstance(cell.props, Mapping)
                    and "lfValue" in cell.props
                )
            ]
            if unresolved_required_inputs:
                raise ValueError(
                    f"Sequence stage '{stage.id}' must bind required input(s) "
                    "without declaration defaults: "
                    f"{', '.join(unresolved_required_inputs)}."
                )

        final_outputs = cls._ports(
            blocks[-1],
            "outputs",
            workflow_id=sequence.stages[-1].workflow_id,
        )
        missing_outputs = [
            output_id
            for output_id in sequence.final_output_ids
            if output_id not in final_outputs
        ]
        if missing_outputs:
            raise ValueError(
                "Sequence final outputs must exist on the final workflow; unknown "
                f"port(s): {', '.join(missing_outputs)}."
            )

    def _sequence_output_cells(
        self,
        sequence: WorkflowSequenceNode,
    ) -> Dict[str, Any]:
        final_stage = sequence.stages[-1]
        final_block = self._definitions[final_stage.workflow_id]
        if not isinstance(final_block, WorkflowNode):
            # Registration validation makes this unreachable unless internal
            # state was mutated behind the registry's API.
            raise RuntimeError("A workflow sequence no longer has an ordinary final block.")
        block_outputs = final_block.cells_as_dict("outputs")
        return {
            output_id: block_outputs[output_id]
            for output_id in sequence.final_output_ids
        }

    def _sequence_public_option_requirements(
        self,
        sequence: WorkflowSequenceNode,
    ) -> dict[
        str,
        dict[str | int, tuple[tuple[str, WorkflowInputOptionRequirement], ...]],
    ]:
        """Project block option gates onto their sequence-level controls.

        A public input may intentionally feed more than one narrow block.  Keep
        every matching requirement so catalogue filtering is an intersection:
        an option is advertised only when *all* of its bound targets can run.
        This avoids the unsafe last-binding-wins behaviour that a flattened
        mapping would introduce while preserving useful shared controls such as
        aspect ratio and seed.
        """

        projected: dict[
            str,
            dict[str | int, list[tuple[str, WorkflowInputOptionRequirement]]],
        ] = {}
        for stage in sequence.stages:
            block = self._definitions[stage.workflow_id]
            if not isinstance(block, WorkflowNode):
                raise RuntimeError("A workflow sequence contains a nested sequence.")
            requirements_by_input: dict[
                str,
                list[WorkflowInputOptionRequirement],
            ] = {}
            for requirement in block.input_option_requirements:
                requirements_by_input.setdefault(requirement.input_id, []).append(
                    requirement
                )

            for binding in stage.bindings:
                if not isinstance(binding, WorkflowSequencePublicInputBinding):
                    continue
                for requirement in requirements_by_input.get(
                    binding.target_input_id,
                    (),
                ):
                    projected.setdefault(binding.public_input_id, {}).setdefault(
                        requirement.option_value,
                        [],
                    ).append((stage.id, requirement))

        return {
            public_input_id: {
                option_value: tuple(requirements)
                for option_value, requirements in options.items()
            }
            for public_input_id, options in projected.items()
        }

    @classmethod
    def _sequence_public_defaults(
        cls,
        sequence: WorkflowSequenceNode,
    ) -> dict[str, Any]:
        """Resolve public defaults with the same select semantics as execution."""

        return default_input_values(sequence)

    def _sequence_input_cells(
        self,
        sequence: WorkflowSequenceNode,
        *,
        scanner: WorkflowReadinessScanner,
    ) -> Dict[str, Any]:
        """Serialize sequence inputs while hiding unavailable block options."""

        input_cells = sequence.cells_as_dict("inputs")
        projected = self._sequence_public_option_requirements(sequence)
        for public_input_id, options in projected.items():
            cell = input_cells.get(public_input_id)
            if not isinstance(cell, dict):
                continue
            props = cell.get("props")
            dataset = props.get("lfDataset") if isinstance(props, dict) else None
            nodes = dataset.get("nodes") if isinstance(dataset, dict) else None
            if not isinstance(nodes, list):
                continue

            available_nodes: list[Any] = []
            for option in nodes:
                if not isinstance(option, Mapping):
                    available_nodes.append(option)
                    continue
                option_value = select_option_value(option)
                requirements = options.get(option_value, ())
                if any(
                    evaluate_input_option_requirement(
                        requirement,
                        scanner=scanner,
                    ).get("status")
                    == READINESS_SETUP_REQUIRED
                    for _stage_id, requirement in requirements
                ):
                    continue
                available_nodes.append(option)
            dataset["nodes"] = available_nodes
        return input_cells

    def _sequence_readiness(
        self,
        sequence: WorkflowSequenceNode,
        *,
        scanner: WorkflowReadinessScanner,
    ) -> Dict[str, Any]:
        blocking_issues: list[dict[str, str]] = []
        warning_issues: list[dict[str, str]] = []
        public_defaults = self._sequence_public_defaults(sequence)

        for stage in sequence.stages:
            block = self._definitions[stage.workflow_id]
            if not isinstance(block, WorkflowNode):
                raise RuntimeError("A workflow sequence contains a nested sequence.")

            configured_stage_inputs = default_input_values(block)
            configured_stage_inputs.update({
                binding.target_input_id: binding.value
                for binding in stage.bindings
                if isinstance(binding, WorkflowSequenceLiteralBinding)
            })
            configured_stage_inputs.update(
                {
                    binding.target_input_id: public_defaults[binding.public_input_id]
                    for binding in stage.bindings
                    if isinstance(binding, WorkflowSequencePublicInputBinding)
                    and binding.public_input_id in public_defaults
                }
            )
            replaceable_stage_input_ids = {
                binding.target_input_id
                for binding in stage.bindings
                if isinstance(binding, WorkflowSequencePublicInputBinding)
            }
            results = [
                evaluate_workflow_readiness(
                    block,
                    inputs=configured_stage_inputs,
                    replaceable_input_ids=replaceable_stage_input_ids,
                    scanner=scanner,
                )
            ]
            for requirement in selected_input_option_requirements(
                block,
                configured_stage_inputs,
            ):
                results.append(
                    evaluate_input_option_requirement(requirement, scanner=scanner)
                )

            for result in results:
                target = (
                    blocking_issues
                    if result.get("status") == READINESS_SETUP_REQUIRED
                    else warning_issues
                )
                raw_issues = result.get("issues", [])
                if not isinstance(raw_issues, list):
                    continue
                for issue in raw_issues:
                    if not isinstance(issue, Mapping):
                        continue
                    code = issue.get("code")
                    message = issue.get("message")
                    if not isinstance(code, str) or not isinstance(message, str):
                        continue
                    target.append(
                        {
                            "code": code,
                            "message": f"Stage {stage.id}: {message}",
                        }
                    )

        status = (
            READINESS_SETUP_REQUIRED
            if blocking_issues
            else READINESS_WARNING
            if warning_issues
            else READINESS_READY
        )
        issues = blocking_issues + warning_issues
        if len(issues) > MAX_READINESS_ISSUES:
            omitted = len(issues) - (MAX_READINESS_ISSUES - 1)
            issues = issues[: MAX_READINESS_ISSUES - 1] + [
                {
                    "code": "readiness_issues_truncated",
                    "message": f"{omitted} additional readiness issue(s) were omitted.",
                }
            ]
        return {"status": status, "issues": issues}

    def register(
        self,
        definition: WorkflowNode | WorkflowSequenceNode,
        *,
        origin: str | None = None,
        collection: str | None = None,
    ) -> None:
        # The packaged workflow loader attaches trusted provenance by wrapping
        # immutable definitions. Recover only an exact sequence payload here;
        # ordinary mutable WorkflowNode registrations keep their legacy path.
        wrapped_definition = getattr(definition, "_definition", None)
        if isinstance(wrapped_definition, WorkflowSequenceNode):
            definition = wrapped_definition

        previous = self._definitions.get(definition.id)
        if previous is not None and previous is not definition:
            _LOG.warning(
                "Workflow definition %r replaces an existing registration",
                definition.id,
            )

        candidate_definitions = dict(self._definitions)
        candidate_definitions[definition.id] = definition
        for candidate in candidate_definitions.values():
            if isinstance(candidate, WorkflowSequenceNode):
                self._validate_sequence(candidate, candidate_definitions)

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
            if isinstance(definition, WorkflowSequenceNode):
                input_cells = self._sequence_input_cells(
                    definition,
                    scanner=readiness_scanner,
                )
                output_cells = self._sequence_output_cells(definition)
                readiness = self._sequence_readiness(
                    definition,
                    scanner=readiness_scanner,
                )
            else:
                input_cells = filter_unavailable_input_options(
                    definition,
                    definition.cells_as_dict("inputs"),
                    scanner=readiness_scanner,
                )
                output_cells = definition.cells_as_dict("outputs")
                readiness = evaluate_workflow_readiness(
                    definition,
                    scanner=readiness_scanner,
                )
            workflow_node = {
                "id": definition.id,
                "value": definition.value,
                "description": definition.description,
                "category": definition.category,
                "kind": (
                    "orchestra"
                    if isinstance(definition, WorkflowSequenceNode)
                    else "block"
                ),
                "origin": origin,
                "collection": collection,
                "readiness": readiness,
                "children": [{
                    "id": f"{definition.id}:inputs",
                    "value": "Inputs",
                    "description": "Workflow inputs",
                    "cells": input_cells,
                    },{
                    "id": f"{definition.id}:outputs",
                    "value": "Outputs",
                    "description": "Workflow outputs",
                    "cells": output_cells,
                    },
                ],
            }
            card = getattr(definition, "card", None)
            if isinstance(card, WorkflowCardPresentation):
                card_payload: Dict[str, Any] = {"summary": card.summary}
                # A curated shipped result no longer demonstrates an overridden block.
                suppress_hero = (
                    origin == "shipped"
                    and isinstance(definition, WorkflowSequenceNode)
                    and any(
                        self._provenance.get(stage.workflow_id, ("custom", "Custom"))[0]
                        != "shipped"
                        for stage in definition.stages
                    )
                )
                if card.hero is not None and not suppress_hero:
                    card_payload["hero"] = {
                        "asset": card.hero.asset,
                        "alt": card.hero.alt,
                    }
                workflow_node["card"] = card_payload
            if isinstance(definition, WorkflowSequenceNode):
                workflow_node.update(
                    {
                        "downloadable": False,
                        "stages": [
                            {"id": stage.id, "workflowId": stage.workflow_id}
                            for stage in definition.stages
                        ],
                    }
                )
            nodes.append(workflow_node)

        return {
            "columns": [],
            "nodes": nodes,
        }
    
    def get(self, id: str) -> WorkflowNode | WorkflowSequenceNode | None:
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
    wrapped_definition = getattr(definition, "_definition", None)
    if isinstance(
        wrapped_definition,
        (WorkflowNode, WorkflowSequenceNode),
    ):
        return True
    if isinstance(definition, (WorkflowNode, WorkflowSequenceNode)):
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

    definitions: list[tuple[object, str, str]] = []
    for definition in iter_workflow_definitions():
        origin = getattr(definition, "origin", "custom")
        collection = getattr(definition, "collection", "Custom")
        definitions.append((definition, origin, collection))

    blocks: list[tuple[object, str, str]] = []
    orchestras: list[tuple[object, str, str]] = []
    for definition, origin, collection in definitions:
        if not _is_workflow_definition(definition):
            raise TypeError(
                f"Workflow definition '{definition!r}' is not compatible with WorkflowNode."
            )

        wrapped_definition = getattr(definition, "_definition", None)
        payload = (
            wrapped_definition
            if isinstance(wrapped_definition, WorkflowSequenceNode)
            else definition
        )
        target = orchestras if isinstance(payload, WorkflowSequenceNode) else blocks
        target.append((definition, origin, collection))

    # Custom modules are discovered by filename, not dependency order. Register
    # every ordinary block first so an orchestra can safely reference a block
    # exported by any later module without authors maintaining a load-order list.
    # Order within each role remains discovery order, preserving the supported
    # last-registration-wins extension contract. This also ensures an orchestra
    # validates against the final block override rather than an earlier authority.
    for definition, origin, collection in (*blocks, *orchestras):
        REGISTRY.register(  # type: ignore[arg-type]
            definition,
            origin=origin,
            collection=collection,
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

def get_workflow(id: str) -> WorkflowNode | WorkflowSequenceNode | None:
    _ensure_registered()
    return REGISTRY.get(id)

def get_workflow_submission_policy(id: str) -> WorkflowSubmissionPolicy | None:
    """Return trusted admission metadata for a registered workflow, if any."""

    _ensure_registered()
    return REGISTRY.get_submission_policy(id)
# endregion
