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
from .iso_ground_tiles import WORKFLOW as iso_ground_tiles
from .krea2 import character_restage, generate as krea2_generate, identity_edit
from .minimax_h3 import directed_view, reference_restage
from .sprite_loop_cut import WORKFLOW as sprite_loop_cut


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


_SPRITE_LOOP_DIRECTION_DEFAULT = (
    "A classic 2D game sprite shot of the subject performing one continuous, evenly "
    "timed action cycle in place: stroke after stroke with no pause and no resting "
    "pose, full body, strict side view facing the viewer's right, centered, whole body "
    "and every extremity inside the frame with a clear margin on every side. Torso "
    "stays level, no root translation, no drift. Clean flat colors and crisp outlines, "
    "same design and palette as the reference. Flat, uniform, solid light grey studio "
    "background with no gradient, props or shadow. Locked camera, no pan, zoom, cut, "
    "turn or text."
)
_SPRITE_LOOP_DIRECTION_HELPER = (
    "Describe the one action to loop (swim, walk, idle sway, wing beat). Ask for a "
    "continuous cycle with no resting pose, a locked camera, a plain background, "
    "and margin around the whole body; the loop cut needs motion everywhere."
)
_SPRITE_LOOP_SOURCE_HELPER = (
    "Upload one still of the subject in a clean side pose on a plain background. "
    "The reference card invents the motion from it; the loop cut then keeps the "
    "best self-closing cycle."
)
_GROUND_TEXTURE_PROMPT_DEFAULT = (
    "Seamless top-down painterly ground texture, straight-down orthographic view, "
    "even soft daylight with no directional shadows, no horizon, no objects, no text, "
    "uniform fine detail across the whole image, natural mottled variation, hand-painted "
    "game-art finish. Subject: short meadow grass with small clover patches."
)
_GROUND_TEXTURE_PROMPT_HELPER = (
    "Describe the ground seen straight from above with even light and no objects; "
    "swap the last sentence for sand, shallow sea, stone or forest floor. The next "
    "block makes it wrap and cuts the diamonds."
)


def _sprite_loop_source_input() -> WorkflowCell:
    cell = _renamed_input(
        reference_restage,
        "reference_image",
        public_id="source_image",
        label="Subject still",
    )
    cell.description = _SPRITE_LOOP_SOURCE_HELPER
    return cell


def _sprite_loop_direction_input() -> WorkflowCell:
    cell = _renamed_input(
        reference_restage,
        "direction",
        public_id="direction",
        label="Loop action",
    )
    cell.description = _SPRITE_LOOP_DIRECTION_HELPER
    cell.props["lfValue"] = _SPRITE_LOOP_DIRECTION_DEFAULT
    helper = cell.props.get("lfHelper")
    if isinstance(helper, dict):
        helper["value"] = _SPRITE_LOOP_DIRECTION_HELPER
    return cell


def _ground_texture_prompt_input() -> WorkflowCell:
    cell = _renamed_input(
        krea2_generate,
        "prompt",
        public_id="texture_prompt",
        label="Ground texture",
    )
    cell.description = _GROUND_TEXTURE_PROMPT_HELPER
    cell.props["lfValue"] = _GROUND_TEXTURE_PROMPT_DEFAULT
    helper = cell.props.get("lfHelper")
    if isinstance(helper, dict):
        helper["value"] = _GROUND_TEXTURE_PROMPT_HELPER
    return cell


sprite_loop_orchestra = WorkflowOrchestraNode(
    id="sprite_loop_orchestra",
    value="Sprite Loop from One Still",
    description=(
        "Invent one continuous action from a single character still with the H3 "
        "reference card, then keep its best self-closing cycle, cut it out, register "
        "it on one transparent canvas and pack a zero-gap atlas with receipts."
    ),
    category="Image Processing",
    inputs=(
        _sprite_loop_source_input(),
        _sprite_loop_direction_input(),
        _input_cell(reference_restage, "aspect_ratio"),
        _input_cell(reference_restage, "duration_frames"),
        _input_cell(reference_restage, "seed"),
        _input_cell(sprite_loop_cut, "frame_count"),
        _input_cell(sprite_loop_cut, "columns"),
        _input_cell(sprite_loop_cut, "min_period_frames"),
        _input_cell(sprite_loop_cut, "max_period_frames"),
        _input_cell(sprite_loop_cut, "motion_floor"),
        _input_cell(sprite_loop_cut, "canvas_size"),
        _input_cell(sprite_loop_cut, "content_height"),
        _input_cell(sprite_loop_cut, "bottom_padding"),
    ),
    stages=(
        WorkflowSequenceStage(
            id="restage",
            workflow_id=reference_restage.id,
            bindings=(
                WorkflowSequencePublicInputBinding(
                    target_input_id="reference_image",
                    public_input_id="source_image",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="direction",
                    public_input_id="direction",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="aspect_ratio",
                    public_input_id="aspect_ratio",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="duration_frames",
                    public_input_id="duration_frames",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="seed",
                    public_input_id="seed",
                ),
            ),
        ),
        WorkflowSequenceStage(
            id="cut",
            workflow_id=sprite_loop_cut.id,
            bindings=(
                WorkflowSequenceArtifactBinding(
                    target_input_id="source_video",
                    output_id="video",
                ),
                *(
                    WorkflowSequencePublicInputBinding(
                        target_input_id=field_id,
                        public_input_id=field_id,
                    )
                    for field_id in (
                        "frame_count",
                        "columns",
                        "min_period_frames",
                        "max_period_frames",
                        "motion_floor",
                        "canvas_size",
                        "content_height",
                        "bottom_padding",
                    )
                ),
            ),
        ),
    ),
    final_output_ids=("frames", "atlas", "loop_receipt", "normalization_receipt"),
)


iso_ground_tiles_orchestra = WorkflowOrchestraNode(
    id="iso_ground_tiles_orchestra",
    value="Iso Ground Tiles from a Prompt",
    description=(
        "Generate one top-down ground texture from text, make it wrap seamlessly, "
        "and cut a set of isometric diamond tiles at seeded offsets."
    ),
    category="Image Processing",
    inputs=(
        _ground_texture_prompt_input(),
        _input_cell(krea2_generate, "aspect_ratio"),
        _input_cell(krea2_generate, "seed"),
        _input_cell(iso_ground_tiles, "blend_fraction"),
        _input_cell(iso_ground_tiles, "tile_width"),
        _input_cell(iso_ground_tiles, "tile_height"),
        _input_cell(iso_ground_tiles, "variants"),
        _input_cell(iso_ground_tiles, "texture_scale"),
    ),
    stages=(
        WorkflowSequenceStage(
            id="generate",
            workflow_id=krea2_generate.id,
            bindings=(
                WorkflowSequencePublicInputBinding(
                    target_input_id="prompt",
                    public_input_id="texture_prompt",
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
            id="tiles",
            workflow_id=iso_ground_tiles.id,
            bindings=(
                WorkflowSequenceArtifactBinding(
                    target_input_id="source_texture",
                    output_id="image",
                ),
                WorkflowSequencePublicInputBinding(
                    target_input_id="seed",
                    public_input_id="seed",
                ),
                *(
                    WorkflowSequencePublicInputBinding(
                        target_input_id=field_id,
                        public_input_id=field_id,
                    )
                    for field_id in (
                        "blend_fraction",
                        "tile_width",
                        "tile_height",
                        "variants",
                        "texture_scale",
                    )
                ),
            ),
        ),
    ),
    final_output_ids=("tiles", "texture", "receipt"),
)


WORKFLOWS = (
    identity_cleanup_restage,
    character_turnaround_orchestra,
    sprite_loop_orchestra,
    iso_ground_tiles_orchestra,
)
WORKFLOW_BY_ID = {workflow.id: workflow for workflow in WORKFLOWS}
