"""Synthetic geometry tests; no body models, host, or external assets."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest


PATH = Path(__file__).resolve().parents[3] / "utils/helpers/motion/retarget.py"
SPEC = importlib.util.spec_from_file_location("standalone_retarget", PATH)
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)


def q(axis, degrees):
    return core.axis_angle_to_quaternion(np.asarray(axis) * np.deg2rad(degrees))


def skeleton(names, parents, positions, rotations=None):
    return {"names": names, "parents": parents, "rest_positions": np.asarray(positions, float),
            "rest_rotations": np.tile([0., 0., 0., 1.], (len(names), 1)) if rotations is None else rotations}


def same_rotation(actual, expected):
    np.testing.assert_allclose(core.quaternion_to_matrix(actual), core.quaternion_to_matrix(expected), atol=1e-8)


def test_core_loads_by_path_with_numpy_as_its_only_nonstdlib_import():
    code = ("import importlib.util, sys; "
            f"s=importlib.util.spec_from_file_location('isolated_core', {str(PATH)!r}); "
            "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
            "assert not any(n in sys.modules for n in ('torch','smplx','comfy','pygltflib'))")
    subprocess.run([sys.executable, "-B", "-I", "-c", code], check=True)


@pytest.mark.parametrize("degrees", [0, 25, 90, 179.999, 180, 270])
@pytest.mark.parametrize("axis", [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
def test_quaternion_matrix_round_trip(axis, degrees):
    quat = q(axis, degrees)
    same_rotation(core.quaternion_from_matrix(core.quaternion_to_matrix(quat)), quat)


def test_hamilton_active_order_and_shortest_arc_opposite_rays():
    a, b = q([0, 1, 0], 90), q([1, 0, 0], 90)
    np.testing.assert_allclose(core.quaternion_rotate(core.quaternion_multiply(a, b), [0, 1, 0]),
                               core.quaternion_rotate(a, core.quaternion_rotate(b, [0, 1, 0])), atol=1e-8)
    turn = core.shortest_arc_rotation([0, 1, 0], [0, -2, 0])
    np.testing.assert_allclose(core.quaternion_rotate(turn, [0, 1, 0]), [0, -1, 0], atol=1e-8)
    same_rotation(core.shortest_arc_rotation([0, 0, 0], [1, 0, 0]), [0, 0, 0, 1])


def test_unmapped_joint_holds_nonidentity_true_rest_local_beneath_animated_parent():
    source = skeleton(["pelvis", "spine1"], [-1, 0], [[0, 1, 0], [0, 2, 0]])
    rest_local = np.array([q([0, 1, 0], 30), q([1, 0, 0], 25), q([0, 0, 1], 40)])
    target = skeleton(["base", "hips", "ornament"], [-1, 0, 1], [[0, 0, 0], [0, 2, 0], [1, 2, 0]],
                      core.local_to_world_rotations(rest_local, [-1, 0, 1]))
    world = np.array([[q([0, 1, 0], 70), q([0, 1, 0], 70)]])
    result = core.retarget_motion(world, [[0, 1, 0]], source, target, [("pelvis", "hips")], scale=1)
    same_rotation(result["local_rotations"][0, 0], rest_local[0])
    same_rotation(result["local_rotations"][0, 2], rest_local[2])
    posed_world = core.local_to_world_rotations(result["local_rotations"], target["parents"])
    expected = core.quaternion_multiply(world[0, 0], target["rest_rotations"][1])
    same_rotation(posed_world[0, 1], expected)
    np.testing.assert_allclose(result["root_positions"], [[0, 2, 0]])


def test_nonidentity_source_rest_is_removed_before_target_alignment_and_rest():
    source = skeleton(["pelvis", "spine1"], [-1, 0], [[0, 0, 0], [0, 1, 0]],
                      np.array([q([1, 0, 0], 15)] * 2))
    target = skeleton(["hips", "torso"], [-1, 0], [[0, 0, 0], [1, 0, 0]],
                      np.array([q([0, 1, 0], 35)] * 2))
    pairs = [("pelvis", "hips"), ("spine1", "torso")]
    delta = q([0, 1, 0], 47)
    source_world = core.quaternion_multiply(delta, source["rest_rotations"])[None]
    result = core.retarget_motion(source_world, [[0, 0, 0]], source, target, pairs, scale=1)
    posed = core.local_to_world_rotations(result["local_rotations"], target["parents"])
    alignment = core.shortest_arc_rotation([1, 0, 0], [0, 1, 0])
    expected = core.quaternion_multiply(core.quaternion_multiply(delta, alignment), target["rest_rotations"][0])
    same_rotation(posed[0, 0], expected)
    same_rotation(posed[0, 1], expected)


def test_two_to_three_chain_resamples_cumulative_world_and_preserves_endpoints():
    source = skeleton(["pelvis", "a", "b"], [-1, 0, 1], [[0, 0, 0], [0, 1, 0], [0, 3, 0]])
    target = skeleton(["hips", "x", "y", "z"], [-1, 0, 1, 2], [[0, 0, 0], [0, 1, 0], [0, 2, 0], [0, 3, 0]])
    world = np.array([[q([0, 1, 0], 0), q([0, 1, 0], 20), q([0, 1, 0], 100)],
                      [q([0, 1, 0], 0), q([0, 1, 0], 40), -q([0, 1, 0], 140)]])
    result = core.retarget_motion(world, [[0, 0, 0]] * 2, source, target, [("pelvis", "hips")],
                                  chains=[{"source": ["a", "b"], "target": ["x", "y", "z"]}], scale=1)
    posed = core.local_to_world_rotations(result["local_rotations"], target["parents"])
    expected = np.array([[q([0, 1, 0], d) for d in [20, 60, 100]],
                         [q([0, 1, 0], d) for d in [40, 90, 140]]])
    same_rotation(posed[:, 1:], expected)


def test_equal_chain_counts_keep_order_even_with_different_bind_stations():
    world = np.array([[q([1, 0, 0], d) for d in [10, 20, 70]]])
    same_rotation(core.resample_chain_rotations(world, [0, .1, 1], [0, .9, 1]), world)


def test_chain_terminal_inherits_alignment_with_nonidentity_rest_frames():
    source = skeleton(["pelvis", "a", "b"], [-1, 0, 1], [[0, 0, 0], [0, 1, 0], [0, 3, 0]],
                      np.array([q([0, 0, 1], 10)] * 3))
    target = skeleton(["hips", "x", "y", "z"], [-1, 0, 1, 2], [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0]],
                      np.array([q([1, 0, 0], 25)] * 4))
    deltas = np.array([q([0, 1, 0], d) for d in [0, 20, 100]])
    world = core.quaternion_multiply(deltas, source["rest_rotations"])[None]
    result = core.retarget_motion(world, [[0, 0, 0]], source, target, [("pelvis", "hips")],
                                  chains=[{"source": ["a", "b"], "target": ["x", "y", "z"]}], scale=1)
    posed = core.local_to_world_rotations(result["local_rotations"], target["parents"])
    alignment = core.shortest_arc_rotation([1, 0, 0], [0, 1, 0])
    expected = core.quaternion_multiply(core.quaternion_multiply(
        np.array([q([0, 1, 0], d) for d in [20, 60, 100]]), alignment), target["rest_rotations"][1:])
    same_rotation(posed[0, 1:], expected)


def test_pelvis_alignment_sees_spine_supplied_only_as_chain():
    source = skeleton(["pelvis", "left_hip", "spine1", "spine2"], [-1, 0, 0, 2],
                      [[0, 0, 0], [-1, 0, 0], [0, 1, 0], [0, 2, 0]])
    target = skeleton(["hips", "leg", "lower", "upper"], [-1, 0, 0, 2],
                      [[0, 0, 0], [-1, 0, 0], [1, 0, 0], [2, 0, 0]])
    result = core.retarget_motion(source["rest_rotations"][None], [[0, 0, 0]], source, target,
                                  [("pelvis", "hips"), ("left_hip", "leg")],
                                  chains=[{"source": ["spine1", "spine2"], "target": ["lower", "upper"]}], scale=1)
    same_rotation(result["local_rotations"][0, 0], core.shortest_arc_rotation([1, 0, 0], [0, 1, 0]))


def test_target_bone_in_a_pair_and_a_chain_is_refused_by_name():
    source = skeleton(["pelvis", "a", "b"], [-1, 0, 1], [[0, 0, 0], [0, 1, 0], [0, 3, 0]])
    target = skeleton(["hips", "x", "y"], [-1, 0, 1], [[0, 0, 0], [0, 1, 0], [0, 2, 0]])
    with pytest.raises(ValueError, match="'x' is named by more than one pair or chain"):
        core.retarget_motion(source["rest_rotations"][None], [[0, 0, 0]], source, target,
                             [("pelvis", "hips"), ("a", "x")],
                             chains=[{"source": ["a", "b"], "target": ["x", "y"]}], scale=1)


def test_coincident_bind_joints_are_refused_not_given_identity_alignment():
    source = skeleton(["pelvis", "spine1"], [-1, 0], [[0, 0, 0], [0, 1, 0]])
    target = skeleton(["hips", "torso"], [-1, 0], [[0, 1, 0], [0, 1, 0]])
    with pytest.raises(ValueError, match="'hips' has zero length on its target side"):
        core.retarget_motion(source["rest_rotations"][None], [[0, 0, 0]], source, target,
                             [("pelvis", "hips"), ("spine1", "torso")], scale=1)


def test_chain_stations_measure_ancestral_arc_not_endpoint_distance():
    rig = skeleton(["a", "helper", "b"], [-1, 0, 1], [[0, 0, 0], [1, 0, 0], [1, 1, 0]])
    np.testing.assert_allclose(core.chain_stations(rig, [0, 1, 2]), [0, .5, 1])
    with pytest.raises(ValueError, match="ancestry"):
        core.chain_stations(rig, [2, 0])


def test_leaf_inherits_nearest_mapped_ancestor_alignment_through_unmapped_parent():
    source = skeleton(["pelvis", "branch", "tip"], [-1, 0, 1], [[0, 0, 0], [0, 1, 0], [0, 2, 0]])
    target = skeleton(["hips", "arm", "helper", "end"], [-1, 0, 1, 2],
                      [[0, 0, 0], [1, 0, 0], [1.5, 0, 0], [2, 0, 0]])
    pairs = [("tip", "end"), ("pelvis", "hips"), ("branch", "arm")]
    alignment = core.alignment_rotations(source, target, pairs)
    expected = core.shortest_arc_rotation([1, 0, 0], [0, 1, 0])
    same_rotation(alignment, np.tile(expected, (3, 1)))


def test_terminal_finger_uses_incoming_segment_instead_of_ancestor_alignment():
    source = skeleton(["pelvis", "left_index2", "left_index3"], [-1, 0, 1],
                      [[0, 0, 0], [0, 1, 0], [0, 2, 0]])
    target = skeleton(["hips", "digit2", "digit3"], [-1, 0, 1],
                      [[0, 0, 0], [1, 0, 0], [1, 1, 0]])
    pairs = list(zip(source["names"], target["names"]))
    alignment = core.alignment_rotations(source, target, pairs)
    same_rotation(alignment[0], core.shortest_arc_rotation([1, 0, 0], [0, 1, 0]))
    same_rotation(alignment[-1], [0, 0, 0, 1])


@pytest.mark.parametrize("omitted", [(), ("spine1", "neck")])
def test_pelvis_and_upper_spine_choose_anatomical_mapped_child(omitted):
    names = ["pelvis", "left_hip", "spine1", "spine3", "left_collar", "neck", "head"]
    source = skeleton(names, [-1, 0, 0, 2, 3, 3, 5], [[0, 0, 0], [-1, 0, 0], [0, 1, 0], [0, 2, 0], [-1, 2, 0], [0, 3, 0], [0, 4, 0]])
    target_names = ["target_" + name for name in names]
    target = skeleton(target_names, [-1, 0, 0, 2, 3, 3, 5], [[0, 0, 0], [-1, 0, 0], [1, 0, 0], [2, 0, 0], [2, 0, -1], [3, 0, 0], [4, 0, 0]])
    pairs = [(name, target) for name, target in zip(names, target_names) if name not in omitted]
    alignment = core.alignment_rotations(source, target, pairs)
    expected = core.shortest_arc_rotation([1, 0, 0], [0, 1, 0])
    same_rotation(alignment[0], expected)
    same_rotation(alignment[[name for name, _ in pairs].index("spine3")], expected)


def test_policies_change_only_bind_alignment_and_keep_animated_pitch():
    source = skeleton(["pelvis", "spine1"], [-1, 0], [[0, 0, 0], [0, 1, 1]])
    target = skeleton(["hips", "torso"], [-1, 0], [[0, 0, 0], [0, 0, 1]])
    pairs = [("pelvis", "hips"), ("spine1", "torso")]
    ordinary = core.alignment_rotations(source, target, pairs)
    flat = core.alignment_rotations(source, target, pairs, flatten_slope=["hips"])
    kept = core.alignment_rotations(source, target, pairs, keep_rest_facing=["hips"])
    assert not np.allclose(ordinary[0], [0, 0, 0, 1])
    same_rotation(flat[0], [0, 0, 0, 1])
    same_rotation(kept[0], [0, 0, 0, 1])
    pitched = np.tile(q([1, 0, 0], 27), (1, 2, 1))
    result = core.retarget_motion(pitched, [[0, 0, 0]], source, target, pairs, flatten_slope=["hips"], scale=1)
    same_rotation(result["local_rotations"][0, 0], pitched[0, 0])


def test_leg_scale_and_root_track_use_rest_pelvis_and_target_pelvis_pair():
    source = skeleton(["pelvis", "left_hip", "left_knee", "left_ankle"], [-1, 0, 1, 2],
                      [[2, 3, 4], [1, 3, 4], [1, 2, 4], [1, 1, 4]])
    target = skeleton(["scene", "hips", "thigh", "shin", "ankle"], [-1, 0, 1, 2, 3],
                      [[0, 0, 0], [10, 6, 7], [9, 6, 7], [9, 4, 7], [9, 2, 7]])
    pairs = list(zip(source["names"], target["names"][1:]))
    root = np.array([[2, 3, 4], [3, 3.5, 2]])
    result = core.retarget_motion(np.tile(source["rest_rotations"], (2, 1, 1)), root, source, target, pairs)
    assert result["scale"] == 2
    np.testing.assert_allclose(result["root_positions"], [[10, 6, 7], [12, 7, 3]])
    with pytest.raises(ValueError, match="left_hip"):
        core.retarget_motion(source["rest_rotations"][None], root[:1], source, target, pairs[:1])


def test_arbitrary_parent_order_and_rejection_of_cycle_unknown_bones_and_bad_frames():
    local = np.array([q([0, 1, 0], 20), q([1, 0, 0], 10)])
    parents = [1, -1]
    same_rotation(core.world_to_local_rotations(core.local_to_world_rotations(local, parents), parents), local)
    with pytest.raises(ValueError, match="cycle"):
        core.local_to_world_rotations(local, [1, 0])
    rig = skeleton(["pelvis"], [-1], [[0, 0, 0]])
    with pytest.raises(ValueError, match="Unknown skeleton bone"):
        core.retarget_motion(rig["rest_rotations"][None], [[0, 0, 0]], rig, rig, [("missing", "pelvis")], scale=1)
    with pytest.raises(ValueError, match="root positions"):
        core.retarget_motion(rig["rest_rotations"][None], [[np.nan, 0, 0]], rig, rig, [("pelvis", "pelvis")], scale=1)


def follow_rig():
    """A thigh driven by left_hip, a muscle sibling under its own offset joint, non-identity rests throughout."""
    source = skeleton(["pelvis", "left_hip", "left_knee"], [-1, 0, 1], [[0, 1, 0], [.1, .9, 0], [.1, .5, 0]])
    rests = np.array([q([0, 1, 0], 10), q([0, 0, 1], 25), q([1, 0, 0], -15), q([0, 1, 0], 40), q([1, 0, 0], 5)])
    target = skeleton(["hips", "thigh", "shin", "offset", "muscle"], [-1, 0, 1, 0, 3],
                      [[0, 1, 0], [.1, .9, 0], [.1, .5, 0], [.05, .95, .05], [.12, .82, .07]], rests)
    pairs = [("pelvis", "hips"), ("left_hip", "thigh"), ("left_knee", "shin")]
    world = np.tile(source["rest_rotations"], (2, 1, 1))
    world[1, 1] = world[1, 2] = q([1, 0, 0], 70)
    return source, target, pairs, world


def test_follower_rides_its_leader_rigidly_in_rotation_and_rest_offset():
    source, target, pairs, world = follow_rig()
    root = [[0, 1, 0], [0, 1.2, 0]]
    result = core.retarget_motion(world, root, source, target, pairs, follow={"muscle": "thigh"}, scale=1)
    posed = core.local_to_world_rotations(result["local_rotations"], target["parents"])
    rests, positions = target["rest_rotations"], target["rest_positions"]
    for frame in range(2):
        delta = core.quaternion_multiply(posed[frame, 1], core.quaternion_inverse(rests[1]))
        same_rotation(posed[frame, 4], core.quaternion_multiply(delta, rests[4]))
        thigh = np.asarray(root[frame]) + core.quaternion_rotate(
            core.quaternion_multiply(posed[frame, 0], core.quaternion_inverse(rests[0])), positions[1] - positions[0])
        np.testing.assert_allclose(result["follower_positions"]["muscle"][frame],
                                   thigh + core.quaternion_rotate(delta, positions[4] - positions[1]), atol=1e-9)
    # The thigh lifts 70 degrees: the muscle's offset turns with it, away from where its own parent holds it.
    assert np.linalg.norm(result["follower_positions"]["muscle"][1] - [.12, 1.02, .07]) > .05
    held = core.retarget_motion(world, root, source, target, pairs, scale=1)
    assert "follower_positions" not in held
    np.testing.assert_allclose(held["local_rotations"][:, :4], result["local_rotations"][:, :4], atol=1e-12)


@pytest.mark.parametrize("follow,message", [
    ({"thigh": "shin"}, "'thigh' is also driven"),
    ({"missing": "thigh"}, "unknown follower bone 'missing'"),
    ({"muscle": "missing"}, "unknown leader bone 'missing'"),
    ({"muscle": "offset", "offset": "thigh"}, "leader 'offset' of follower 'muscle' is itself a follower"),
    ({"muscle": "offset"}, "leader 'offset' of follower 'muscle' is held"),
    ([("muscle", "thigh"), ("muscle", "shin")], "'muscle' twice"),
])
def test_follow_refusals_name_the_bone(follow, message):
    source, target, pairs, world = follow_rig()
    with pytest.raises(ValueError, match=message):
        core.retarget_motion(world, [[0, 1, 0]] * 2, source, target, pairs, follow=follow, scale=1)


def test_a_follower_placed_by_its_own_descendant_is_refused():
    source = skeleton(["pelvis", "left_hip"], [-1, 0], [[0, 1, 0], [.1, .9, 0]])
    target = skeleton(["hips", "helper", "thigh"], [-1, 0, 1], [[0, 1, 0], [.1, .95, 0], [.1, .9, 0]])
    with pytest.raises(ValueError, match="'helper' and its leader place each other"):
        core.retarget_motion(source["rest_rotations"][None], [[0, 1, 0]], source, target,
                             [("pelvis", "hips"), ("left_hip", "thigh")], follow={"helper": "thigh"}, scale=1)
