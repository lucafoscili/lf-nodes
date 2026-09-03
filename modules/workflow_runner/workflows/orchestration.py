"""Declaration-only Workflow Runner assemblies.

The workflows in this module own no Comfy graph or model policy. They compose
narrow blocks declared by other workflow modules; packaged registration admits
all blocks before resolving any orchestra.
"""

from __future__ import annotations

from copy import deepcopy

from ..services.registry import (
    WorkflowCardPresentation,
    WorkflowCell,
    WorkflowHeroImage,
    WorkflowOrchestraNode,
    WorkflowSequenceArtifactBinding,
    WorkflowSequenceLiteralBinding,
    WorkflowSequencePublicInputBinding,
    WorkflowSequenceStage,
)
from .cardinal_turnaround import WORKFLOW as assemble_cardinal_turnaround
from .krea2 import character_restage, identity_edit
from .minimax_h3 import directed_view


_IDENTITY_CLEANUP_DEFAULT = (
    "Create a polished, faithful waist-up portrait from the supplied character "
    "reference. Preserve the exact facial identity, hair, skin tone, and defining "
    "features. Keep the person alone in a simple neutral setting with soft even "
    "lighting, natural anatomy, and coherent skin, hair, and fabric texture. Correct "
    "minor image artifacts without changing who they are; do not redesign the face, "
    "hairstyle, or body."
)
_IDENTITY_CLEANUP_HELPER = (
    "Describe how to clean and stabilize the supplied character reference before the "
    "next block restages it. Ask for identity-preserving cleanup, framing, or "
    "presentation only; put the new pose, outfit, and environment in Restage scene and "
    "pose. Do not type Picture or image tags—the reference is injected automatically."
)
_FRONT_CLEANUP_DEFAULT = (
    "Create a faithful full-body technical front view of the supplied character. "
    "Preserve the exact recognizable identity, face, hairstyle, anatomy, body "
    "proportions, outfit, materials, colors, accessories, equipment, and left-right "
    "asymmetry. Place the character alone in a relaxed A-pose, facing the camera "
    "straight-on, with arms slightly away from the torso, hands and fingers visible, "
    "feet fully visible, and no crossed or hidden limbs. Use a locked eye-level camera, "
    "plain neutral light-gray studio background, even diffuse lighting, and roughly "
    "eight percent clear margin around the complete silhouette. Correct minor image "
    "artifacts without redesigning the character or changing the outfit."
)
_FRONT_CLEANUP_HELPER = (
    "Describe the faithful front-view cleanup that will anchor all later angles. A "
    "neutral A-pose, visible hands and feet, plain background, even light, and clear "
    "silhouette make the following camera turns and 3D reconstruction easier."
)


def _input_cell(workflow: object, input_id: str) -> WorkflowCell:
    """Clone one block input so an assembly never mutates block authority."""

    matches = [
        cell
        for cell in getattr(workflow, "inputs", ())
        if isinstance(cell, WorkflowCell) and cell.id == input_id
    ]
    if len(matches) != 1:
        workflow_id = getattr(workflow, "id", "unknown")
        raise RuntimeError(
            f"Workflow '{workflow_id}' must expose exactly one '{input_id}' input."
        )
    return deepcopy(matches[0])


def _renamed_input(
    workflow: object,
    input_id: str,
    *,
    public_id: str,
    label: str,
) -> WorkflowCell:
    """Clone and relabel a block control without copying its knob contract."""

    cell = _input_cell(workflow, input_id)
    cell.id = public_id
    cell.value = label
    cell.props["lfLabel"] = label
    html_attributes = cell.props.get("lfHtmlAttributes")
    if isinstance(html_attributes, dict) and "name" in html_attributes:
        html_attributes["name"] = public_id
    return cell


def _identity_cleanup_prompt() -> WorkflowCell:
    """Specialize Identity Edit for its reference-only orchestra stage."""

    cell = _renamed_input(
        identity_edit,
        "prompt",
        public_id="identity_prompt",
        label="Identity cleanup",
    )
    cell.description = _IDENTITY_CLEANUP_HELPER
    cell.props["lfValue"] = _IDENTITY_CLEANUP_DEFAULT
    cell.props["lfHelper"]["value"] = _IDENTITY_CLEANUP_HELPER
    return cell


def _front_cleanup_prompt() -> WorkflowCell:
    """Specialize Identity Edit as the turnaround's authoritative front view."""

    cell = _renamed_input(
        identity_edit,
        "prompt",
        public_id="cleanup_prompt",
        label="Front-view cleanup",
    )
    cell.description = _FRONT_CLEANUP_HELPER
    cell.props["lfValue"] = _FRONT_CLEANUP_DEFAULT
    cell.props["lfHelper"]["value"] = _FRONT_CLEANUP_HELPER
    return cell


def _character_reference_input() -> WorkflowCell:
    """Describe the whole-character source expected by the turnaround orchestra."""

    helper = (
        "Upload one character reference. Cleanup can repair an imperfect "
        "source, but later views are most trustworthy when the complete silhouette, "
        "outfit, hands, and feet are visible."
    )
    cell = _renamed_input(
        identity_edit,
        "identity_image",
        public_id="source_image",
        label="Character reference",
    )
    cell.description = helper
    lf_helper = cell.props.get("lfHelper")
    if isinstance(lf_helper, dict):
        lf_helper["value"] = helper
    return cell


identity_cleanup_restage = WorkflowOrchestraNode(
    id="identity_cleanup_restage",
    value="Identity-Preserved Restage",
    description=(
        "Preserve one supplied identity, then place the retained character into a "
        "new pose, framing, outfit, and scene."
    ),
    category="Krea 2",
    card=WorkflowCardPresentation(
        summary="Preserve an identity, then restage it.",
        hero=WorkflowHeroImage(
            asset="krea2/identity-cleanup-restage.webp",
            alt=(
                "Before: the original generated traveler on a train. "
                "After: the orchestra's final greenhouse portrait, following "
                "Identity Edit and Character Restage."
            ),
        ),
    ),
    inputs=(
        _input_cell(identity_edit, "identity_image"),
        _identity_cleanup_prompt(),
        _renamed_input(
            character_restage,
            "prompt",
            public_id="restage_prompt",
            label="Restage scene and pose",
        ),
        _input_cell(identity_edit, "aspect_ratio"),
        _input_cell(identity_edit, "seed"),
    ),
    stages=(
        WorkflowSequenceStage(
            id="identity",
            workflow_id=identity_edit.id,
            bindings=(
                WorkflowSequencePublicInputBinding(
                    target_input_id="identity_image",
                    public_input_id="identity_image",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="prompt",
                    public_input_id="identity_prompt",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="aspect_ratio",
                    public_input_id="aspect_ratio",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="seed",
                    public_input_id="seed",
                ),
            ),
        ),
        WorkflowSequenceStage(
            id="restage",
            workflow_id=character_restage.id,
            bindings=(
                WorkflowSequenceArtifactBinding(
                    target_input_id="reference_image",
                    output_id="image",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="prompt",
                    public_input_id="restage_prompt",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="aspect_ratio",
                    public_input_id="aspect_ratio",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="seed",
                    public_input_id="seed",
                ),
            ),
        ),
    ),
    final_output_ids=("image",),
)


character_turnaround_orchestra = WorkflowOrchestraNode(
    id="character_turnaround_orchestra",
    value="3D-Ready Character Turnaround",
    description=(
        "Clean one character reference into an authoritative front view, generate "
        "subject-right, back, and subject-left camera views, then register four "
        "transparent reconstruction inputs and a labeled review sheet."
    ),
    category="3D",
    card=WorkflowCardPresentation(
        summary="Clean a reference, generate three views, then align all four.",
        hero=WorkflowHeroImage(
            asset="orchestra/character-turnaround.webp",
            alt=(
                "Original generated adult explorer beside the orchestra's four actual "
                "saved views, labeled input, front, subject-right, back, and subject-left."
            ),
        ),
    ),
    inputs=(
        _character_reference_input(),
        _front_cleanup_prompt(),
        _input_cell(identity_edit, "identity_fidelity"),
        _input_cell(identity_edit, "grounding_px"),
        _input_cell(directed_view, "retention_details"),
        _input_cell(directed_view, "execution_profile"),
        _input_cell(directed_view, "duration_frames"),
        _input_cell(directed_view, "tail_fraction"),
        _input_cell(directed_view, "analysis_max_edge"),
        _input_cell(directed_view, "seed"),
        _input_cell(assemble_cardinal_turnaround, "canvas_size"),
        _input_cell(assemble_cardinal_turnaround, "content_height"),
        _input_cell(assemble_cardinal_turnaround, "bottom_padding"),
    ),
    stages=(
        WorkflowSequenceStage(
            id="cleanup",
            workflow_id=identity_edit.id,
            bindings=(
                WorkflowSequencePublicInputBinding(
                    target_input_id="identity_image",
                    public_input_id="source_image",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="prompt",
                    public_input_id="cleanup_prompt",
                ),
                WorkflowSequenceLiteralBinding(
                    target_input_id="aspect_ratio",
                    value="9:16 (Portrait Widescreen)",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="seed",
                    public_input_id="seed",
                ),
                WorkflowSequenceLiteralBinding(
                    target_input_id="steps",
                    value=10,
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="identity_fidelity",
                    public_input_id="identity_fidelity",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="grounding_px",
                    public_input_id="grounding_px",
                ),
            ),
        ),
        *(
            WorkflowSequenceStage(
                id=stage_id,
                workflow_id=directed_view.id,
                bindings=(
                    WorkflowSequenceArtifactBinding(
                        target_input_id="source_image",
                        output_id="image",
                        source_stage_id="cleanup",
                    ),
                    WorkflowSequenceLiteralBinding(
                        target_input_id="target_view",
                        value=target_view,
                    ),
                    WorkflowSequencePublicInputBinding(
                        target_input_id="retention_details",
                        public_input_id="retention_details",
                    ),
                    WorkflowSequencePublicInputBinding(
                        target_input_id="execution_profile",
                        public_input_id="execution_profile",
                    ),
                    WorkflowSequenceLiteralBinding(
                        target_input_id="aspect_ratio",
                        value="9:16",
                    ),
                    WorkflowSequencePublicInputBinding(
                        target_input_id="duration_frames",
                        public_input_id="duration_frames",
                    ),
                    WorkflowSequencePublicInputBinding(
                        target_input_id="tail_fraction",
                        public_input_id="tail_fraction",
                    ),
                    WorkflowSequencePublicInputBinding(
                        target_input_id="analysis_max_edge",
                        public_input_id="analysis_max_edge",
                    ),
                    WorkflowSequencePublicInputBinding(
                        target_input_id="seed",
                        public_input_id="seed",
                    ),
                ),
            )
            for stage_id, target_view in (
                ("subject_right", "subject_right"),
                ("back", "back"),
                ("subject_left", "subject_left"),
            )
        ),
        WorkflowSequenceStage(
            id="assemble",
            workflow_id=assemble_cardinal_turnaround.id,
            bindings=(
                WorkflowSequenceArtifactBinding(
                    target_input_id="front_image",
                    output_id="image",
                    source_stage_id="cleanup",
                ),
                WorkflowSequenceArtifactBinding(
                    target_input_id="right_image",
                    output_id="view",
                    source_stage_id="subject_right",
                ),
                WorkflowSequenceArtifactBinding(
                    target_input_id="back_image",
                    output_id="view",
                    source_stage_id="back",
                ),
                WorkflowSequenceArtifactBinding(
                    target_input_id="left_image",
                    output_id="view",
                    source_stage_id="subject_left",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="canvas_size",
                    public_input_id="canvas_size",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="content_height",
                    public_input_id="content_height",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="bottom_padding",
                    public_input_id="bottom_padding",
                ),
            ),
        ),
    ),
    final_output_ids=(
        "front",
        "right",
        "back",
        "left",
        "contact_sheet",
        "normalization_receipt",
    ),
)


WORKFLOWS = (identity_cleanup_restage, character_turnaround_orchestra)
WORKFLOW_BY_ID = {workflow.id: workflow for workflow in WORKFLOWS}
