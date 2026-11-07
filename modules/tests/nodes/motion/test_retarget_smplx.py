"""Model-free adapter checks with a generated rig and shape-dependent fake joints."""
from __future__ import annotations

from contextlib import nullcontext
from copy import deepcopy
import importlib
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest


# Import the actual motion modules under a lightweight package. The public
# helpers/__init__.py eagerly imports unrelated optional model dependencies.
MODULES = Path(__file__).resolve().parents[3]
NAMESPACE = "_lf_motion_adapter_tests"
for suffix, directory in (("", MODULES), (".utils", MODULES / "utils"),
                          (".utils.helpers", MODULES / "utils/helpers"),
                          (".utils.helpers.motion", MODULES / "utils/helpers/motion")):
    package = ModuleType(NAMESPACE + suffix)
    package.__path__ = [str(directory)]
    sys.modules[package.__name__] = package
adapter = importlib.import_module(NAMESPACE + ".utils.helpers.motion.retarget_smplx")
core = importlib.import_module(NAMESPACE + ".utils.helpers.motion.retarget")
format_module = importlib.import_module(NAMESPACE + ".utils.helpers.motion.format")
glb = importlib.import_module(NAMESPACE + ".utils.helpers.motion.retarget_glb")
codec = importlib.import_module(NAMESPACE + ".utils.glb_texture")


MODEL_PARENTS = np.array([
    -1, 0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 12, 13, 14, 16, 17, 18, 19, 15, 15, 15,
    20, 25, 26, 20, 28, 29, 20, 31, 32, 20, 34, 35, 20, 37, 38,
    21, 40, 41, 21, 43, 44, 21, 46, 47, 21, 49, 50, 21, 52, 53,
])


class Tensor(np.ndarray):
    def cpu(self):
        return self

    def numpy(self):
        return np.asarray(self)


def tensor(value, dtype=None):
    return np.asarray(value, dtype=dtype).view(Tensor)


def base_positions():
    positions = np.zeros((55, 3))
    positions[0] = [0, 1, 0]
    for index in range(1, 55):
        delta = [0, .2, 0]
        if index in (1, 2):
            delta = [.2 if index == 1 else -.2, -.1, 0]
        elif index in (4, 5, 7, 8):
            delta = [0, -.4, 0]
        elif index in (10, 11):
            delta = [0, 0, .15]
        elif index in (13, 14, 16, 17, 18, 19, 20, 21):
            delta = [.2 if index % 2 == 0 else -.2, .05, 0]
        elif index >= 25:
            delta = [.05 if index < 40 else -.05, 0, .01]
        positions[index] = positions[MODEL_PARENTS[index]] + delta
    return positions


class FakeModel:
    def __init__(self):
        self.parents = tensor(MODEL_PARENTS)
        self.calls = []

    def __call__(self, **kwargs):
        betas = np.asarray(kwargs["betas"])
        self.calls.append({key: np.array(value, copy=True) for key, value in kwargs.items()})
        scale = 1 + betas[:, 1, None, None] * .1
        offset = betas[:, 0, None, None] * np.array([.5, .2, .3])[None, None]
        return SimpleNamespace(joints=tensor(base_positions()[None] * scale + offset))


@pytest.fixture
def model(monkeypatch):
    fake_torch = ModuleType("torch")
    fake_torch.float32 = np.float32
    fake_torch.as_tensor = tensor
    fake_torch.zeros = lambda *shape: tensor(np.zeros(shape))
    fake_torch.inference_mode = nullcontext
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    return FakeModel()


def motion(count=3):
    params = {name: np.zeros((count, width)).tolist() for name, width in format_module.POSE_WIDTHS.items()}
    return {"schema": "lf.motion.v1", "fps": 24., "joint_names": deepcopy(format_module.JOINT_NAMES),
            "world": deepcopy(params), "camera": deepcopy(params), "betas": [[0.] * 10]}


def bone_map():
    return {"schema": "lf.bone-map.v1", "source": "smplx", "unmapped": "rest",
            "bones": {name: "Rig_" + name for name in adapter.SOURCE_NAMES[:22]}}


def write_map(tmp_path, document):
    path = tmp_path / "map.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


@pytest.mark.parametrize("edit,field,reason", [
    (lambda doc: doc["bones"].update(unknown="Rig_pelvis"), "bones", "unknown source"),
    (lambda doc: doc["bones"].update(pelvis="Missing"), "bones", "unknown target"),
    (lambda doc: doc["bones"].update(right_hip="Rig_left_hip"), "bones", "duplicate target"),
    (lambda doc: doc["bones"].pop("left_knee"), "bones", "missing core"),
    (lambda doc: doc.pop("unmapped"), "unmapped", "equal rest"),
    (lambda doc: doc.update(chains=[{"source": ["unknown"], "target": ["Rig_spine1"]}]), "chains", "unknown joint"),
    (lambda doc: doc.update(chains=[{"source": ["spine1"], "target": ["Missing"]}]), "chains", "unknown joint"),
])
def test_map_errors_name_path_field_and_offending_contract(tmp_path, edit, field, reason):
    document = bone_map()
    edit(document)
    path = write_map(tmp_path, document)
    with pytest.raises(ValueError) as caught:
        adapter.read_bone_map(path, ["Rig_" + name for name in adapter.SOURCE_NAMES])
    assert str(path) in str(caught.value)
    assert field in str(caught.value)
    assert reason in str(caught.value)


def test_source_joint_indices_parents_world_composition_and_selected_shape(model):
    clip = motion()
    clip["world"]["global_orient"] = [[0, .4, 0]] * 3
    clip["world"]["body_pose"][1][0:3] = [.3, 0, 0]
    clip["world"]["left_hand_pose"][1][0:3] = [0, 0, .5]
    clip["world"]["transl"] = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
    betas = np.array([2, 1] + [0] * 8)
    skeleton, world, roots = adapter.source_skeleton(clip, model, betas)
    assert skeleton["names"] == [name for names in format_module.JOINT_NAMES.values() for name in names]
    assert adapter.MODEL_JOINTS == list(range(22)) + list(range(25, 55))
    for name, model_joint in (("left_index1", 25), ("left_thumb3", 39), ("right_index1", 40), ("right_thumb3", 54)):
        index = skeleton["names"].index(name)
        expected = base_positions()[model_joint] * 1.1 + [1, .4, .6]
        np.testing.assert_allclose(skeleton["rest_positions"][index], expected, atol=1e-6)
        parent_model = MODEL_PARENTS[model_joint]
        assert adapter.MODEL_JOINTS[skeleton["parents"][index]] == parent_model
    np.testing.assert_allclose(roots, np.asarray(clip["world"]["transl"]) + [1, 1.5, .6], atol=1e-6)
    index = skeleton["names"].index("left_index1")
    expected = core.quaternion_multiply(core.axis_angle_to_quaternion([0, .4, 0]),
                                        core.axis_angle_to_quaternion([0, 0, .5]))
    np.testing.assert_allclose(core.quaternion_to_matrix(world[1, index]), core.quaternion_to_matrix(expected), atol=1e-7)
    assert all(np.count_nonzero(call[key]) == 0 for call in model.calls
               for key in ("global_orient", "transl", "body_pose", "left_hand_pose", "right_hand_pose"))


def test_required_anatomical_anchor_cannot_be_replaced_by_a_chain(tmp_path):
    document = bone_map()
    target = document["bones"].pop("pelvis")
    document["chains"] = [{"source": ["pelvis"], "target": [target]}]
    path = write_map(tmp_path, document)
    with pytest.raises(ValueError, match="map.json.*bones.*missing core joint 'pelvis'"):
        adapter.read_bone_map(path, ["Rig_" + name for name in adapter.SOURCE_NAMES])


def test_chain_can_share_source_controls_with_an_ordinary_pair(tmp_path):
    document = bone_map()
    del document["bones"]["spine1"], document["bones"]["spine2"]
    document["chains"] = [{"source": ["spine1", "spine2", "spine3"],
                           "target": ["Rig_spine1", "Rig_spine2"]}]
    # spine3 drives the chain and keeps its ordinary pair onto a bone outside the run.
    assert adapter.read_bone_map(write_map(tmp_path, document),
                                 ["Rig_" + name for name in adapter.SOURCE_NAMES]) == document


def test_a_target_bone_named_by_a_pair_and_a_chain_is_refused(tmp_path):
    document = bone_map()
    document["chains"] = [{"source": ["spine1", "spine2", "spine3"],
                           "target": ["Rig_spine1", "Rig_spine2"]}]
    path = write_map(tmp_path, document)
    with pytest.raises(ValueError, match="map.json.*chains.*'Rig_spine1' is also a bones target"):
        adapter.read_bone_map(path, ["Rig_" + name for name in adapter.SOURCE_NAMES])


def test_spine_may_come_only_through_a_chain(tmp_path):
    document = bone_map()
    for name in ("spine1", "spine2", "spine3"):
        del document["bones"][name]
    document["chains"] = [{"source": ["spine1", "spine2", "spine3"],
                           "target": ["Rig_spine1", "Rig_spine2"]}]
    names = ["Rig_" + name for name in adapter.SOURCE_NAMES]
    assert adapter.read_bone_map(write_map(tmp_path, document), names) == document
    del document["chains"]
    with pytest.raises(ValueError, match="at least one of spine1, spine2, spine3"):
        adapter.read_bone_map(write_map(tmp_path, document), names)


def test_rest_joint_evaluation_batches_shape_without_pose(model):
    betas = np.zeros((18, 10))
    betas[:, 0] = np.arange(18)
    positions = adapter.rest_joints(model, betas)
    assert positions.shape == (18, 52, 3)
    assert [len(call["betas"]) for call in model.calls] == [16, 2]
    np.testing.assert_allclose(positions[-1, 0], base_positions()[0] + 17 * np.array([.5, .2, .3]))


def test_camera_transform_uses_clip_shape_per_frame_j0_and_preserves_target_placement(model):
    clip = motion()
    clip["betas"] = [[value, 0] + [0] * 8 for value in [1, 3, 5]]
    clip["world"]["global_orient"] = [[0, .1, 0], [0, .2, 0], [0, .3, 0]]
    clip["camera"]["global_orient"] = [[0, .5, 0], [0, .7, 0], [0, .9, 0]]
    clip["world"]["transl"] = [[1, 2, 3], [2, 3, 4], [3, 4, 5]]
    clip["camera"]["transl"] = [[4, 3, 2], [5, 4, 3], [6, 5, 4]]
    rotation, translation, camera_root = adapter.camera_from_world(clip, model)
    clip_pelvis = base_positions()[0] + np.asarray([1, 3, 5])[:, None] * [.5, .2, .3]
    expected_camera_root = np.asarray(clip["camera"]["transl"]) + clip_pelvis
    expected_world_root = np.asarray(clip["world"]["transl"]) + clip_pelvis
    np.testing.assert_allclose(camera_root, expected_camera_root, atol=1e-6)
    np.testing.assert_allclose(np.einsum("fij,fj->fi", rotation, expected_world_root) + translation, camera_root, atol=1e-6)
    expected_rotation = core.quaternion_to_matrix(core.axis_angle_to_quaternion([[0, .4, 0], [0, .5, 0], [0, .6, 0]]))
    np.testing.assert_allclose(rotation, expected_rotation, atol=1e-7)
    # A receiver/selected shape offset remains a real transformed offset. The
    # shared camera is recovered from the clip's J0, never fitted to this root.
    placement = np.array([2., .7, -1.])
    transformed = np.einsum("fij,fj->fi", rotation, expected_world_root + placement) + translation
    np.testing.assert_allclose(transformed-camera_root, np.einsum("fij,j->fi", rotation, placement), atol=1e-6)
    assert not np.allclose(transformed, camera_root)


def generated_target():
    lookup = {model: index for index, model in enumerate(adapter.MODEL_JOINTS)}
    parents = [lookup.get(int(MODEL_PARENTS[index]), -1) for index in adapter.MODEL_JOINTS]
    positions = base_positions()[adapter.MODEL_JOINTS] * 2 + [5, .4, -4]
    nodes = []
    finger_rotation = core.axis_angle_to_quaternion([0, 0, .2]).tolist()
    for index, (name, parent) in enumerate(zip(adapter.SOURCE_NAMES, parents)):
        offset = positions[index] if parent < 0 else positions[index]-positions[parent]
        node = {"name": "Rig_" + name, "translation": offset.tolist()}
        children = [child for child, ancestor in enumerate(parents) if ancestor == index]
        if children:
            node["children"] = children
        if index >= 22:
            node["rotation"] = finger_rotation
        nodes.append(node)
    document = {"asset": {"version": "2.0"}, "buffers": [{"byteLength": 0}],
                "nodes": nodes, "skins": [{"joints": list(range(len(nodes)))}],
                "scenes": [{"nodes": [0]}], "scene": 0}
    return codec.pack_glb(document, b""), finger_rotation


def test_full_adapter_scales_root_without_pinning_and_keeps_unmapped_finger_rests(tmp_path, model, monkeypatch):
    render = importlib.import_module(NAMESPACE + ".utils.helpers.motion.render")
    monkeypatch.setattr(render, "load_body_model", lambda *_args: model)
    clip = motion()
    clip["betas"] = [[value, 0] + [0] * 8 for value in [1, 3, 5]]
    clip["world"]["transl"] = [[.6, .1, -.2], [.8, .2, -.3], [1.2, .1, -.1]]
    path = tmp_path / "clip.json"
    format_module.write_motion(path, clip)
    blob, finger_rotation = generated_target()
    target_path = tmp_path / "target.glb"
    target_path.write_bytes(blob)
    map_path = write_map(tmp_path, bone_map())
    output, report = adapter.retarget_motion(path, tmp_path / "unused.npz", "neutral", "4,2", target_path, map_path)
    document, binary = codec.read_glb(output)
    expected_scale = 2 / 1.2
    assert report["s"] == pytest.approx(expected_scale, abs=1e-6)
    assert report["fingers"] == {"left": "rest", "right": "rest"}
    assert report["source_rest_pelvis"] == pytest.approx([2, 2, 1.2])
    assert report["target_rest_pelvis"] == pytest.approx([5, 2.4, -4])
    latest = document["animations"][-1]
    translation = next(row for row in latest["channels"] if row["target"]["path"] == "translation")
    values = glb._accessor(document, binary, latest["samplers"][translation["sampler"]]["output"])
    expected = np.array([5, 2.4, -4]) + np.asarray(clip["world"]["transl"]) * expected_scale
    np.testing.assert_allclose(values, expected, atol=1e-6)
    assert not np.allclose(values[0], report["target_rest_pelvis"])
    for index in range(22, 52):
        channel = next(row for row in latest["channels"] if row["target"] == {"node": index, "path": "rotation"})
        values = glb._accessor(document, binary, latest["samplers"][channel["sampler"]]["output"])
        np.testing.assert_allclose(values, [finger_rotation] * 3, atol=1e-6)
    assert set(report["held_target_bones"]) == {"Rig_" + name for name in adapter.SOURCE_NAMES[22:]}


def test_fully_mapped_fingers_are_animated_with_no_held_or_dropped_bones(tmp_path, model, monkeypatch):
    render = importlib.import_module(NAMESPACE + ".utils.helpers.motion.render")
    monkeypatch.setattr(render, "load_body_model", lambda *_args: model)
    clip = motion()
    clip["world"]["left_hand_pose"][1][:3] = [.3, .1, 0]
    path = tmp_path / "fingers.json"
    format_module.write_motion(path, clip)
    target_path = tmp_path / "target.glb"
    target_path.write_bytes(generated_target()[0])
    mapping = bone_map()
    mapping["bones"] = {name: "Rig_" + name for name in adapter.SOURCE_NAMES}
    output, report = adapter.retarget_motion(path, tmp_path / "unused.npz", "neutral", "0",
                                             target_path, write_map(tmp_path, mapping))
    assert report["held_target_bones"] == report["dropped_source_joints"] == []
    assert report["fingers"] == {}
    document, binary = codec.read_glb(output)
    clip = document["animations"][-1]
    index = adapter.SOURCE_NAMES.index("left_index1")
    channel = next(row for row in clip["channels"] if row["target"] == {"node": index, "path": "rotation"})
    values = glb._accessor(document, binary, clip["samplers"][channel["sampler"]]["output"])
    assert not np.allclose(values[0], values[1])
