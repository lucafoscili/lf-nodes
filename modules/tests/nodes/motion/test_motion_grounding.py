"""CPU synthetic contracts for the grounding steps' pure parts; the app-backed steps run in acceptance."""

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from modules.utils.helpers.motion import motion_grounding as grounding


def test_a_camera_moving_along_its_view_reads_as_a_push_in():
    n = 60
    view = np.tile([0.0, 0.0, -1.0], (n, 1))
    pushed = np.stack([np.zeros(n), np.linspace(0.0, -0.4, n)], axis=1)  # 40 cm toward where it looks
    aside = np.stack([np.linspace(0.0, 0.4, n), np.zeros(n)], axis=1)  # 40 cm across its view
    assert grounding.push_in_reading(pushed, view) == pytest.approx(0.4)
    assert grounding.push_in_reading(aside, view) == pytest.approx(0.0)
    assert grounding.push_in_reading(pushed, view) > grounding.DEFAULTS["push_in_metres"]


def test_view_is_the_camera_z_row_on_the_floor():
    world = Rotation.from_rotvec([0.0, 0.7, 0.0])
    to_camera = Rotation.from_rotvec([np.pi, 0.0, 0.0])  # OpenCV: y down, looking along +z
    camera = to_camera * world
    view = grounding.view_directions(camera.as_rotvec()[None], world.as_rotvec()[None])
    np.testing.assert_allclose(view[0], [0.0, 0.0, -1.0], atol=1e-12)


def test_planted_seconds_become_frames_and_refuse_outside_the_clip():
    mask = grounding.planted_frames([[0.5, 1.0]], 30.0, 60)
    assert mask.sum() == 15 and mask[15] and not mask[30]
    with pytest.raises(ValueError, match="outside"):
        grounding.planted_frames([[1.5, 2.5]], 30.0, 60)


def test_parameters_and_solver_arrays_round_trip():
    rng = np.random.default_rng(3)
    params = dict(global_orient=rng.normal(0, 0.3, (5, 3)), body_pose=rng.normal(0, 0.3, (5, 63)),
                  transl=rng.normal(0, 1, (5, 3)), left_hand_pose=np.zeros((5, 45)),
                  right_hand_pose=np.zeros((5, 45)))
    pelvis = np.array([0.0, -0.35, 0.01])
    root, quat = grounding.arrays_from_params(params, pelvis)
    world = grounding.to_world(params, root, quat, pelvis)
    np.testing.assert_allclose(world["transl"], params["transl"])
    np.testing.assert_allclose(Rotation.from_rotvec(world["body_pose"].reshape(-1, 3)).as_matrix(),
                               Rotation.from_rotvec(params["body_pose"].reshape(-1, 3)).as_matrix(), atol=1e-9)
    assert set(world) == {"global_orient", "body_pose", "transl", "left_hand_pose", "right_hand_pose"}


def test_rotation_between_takes_each_direction_onto_the_other():
    a = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    b = np.array([[0.0, 0.0, 2.0], [0.0, 1.0, 0.0]])
    turned = np.einsum("tij,tj->ti", grounding.rotation_between(a, b), a)
    np.testing.assert_allclose(turned, [[0.0, 0.0, 1.0], [0.0, 1.0, 0.0]], atol=1e-12)
