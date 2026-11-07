"""Generated GLB rigs exercise scene TRS, append-only clips and CPU LBS."""
import copy
import importlib
import sys
import types
from pathlib import Path

import numpy as np
import pytest

# Import the pure adapter without helpers/__init__.py eagerly importing every
# optional provider/model package. A private namespace avoids altering other
# tests' public package imports.
_ROOT = Path(__file__).resolve().parents[3]
for _suffix, _directory in [('', _ROOT), ('.utils', _ROOT / 'utils'),
                            ('.utils.helpers', _ROOT / 'utils/helpers'),
                            ('.utils.helpers.motion', _ROOT / 'utils/helpers/motion')]:
    _package = types.ModuleType('_lf_glb_test' + _suffix)
    _package.__path__ = [str(_directory)]
    sys.modules[_package.__name__] = _package
_codec = importlib.import_module('_lf_glb_test.utils.glb_texture')
_core = importlib.import_module('_lf_glb_test.utils.helpers.motion.retarget')
_glb = importlib.import_module('_lf_glb_test.utils.helpers.motion.retarget_glb')
pack_glb, read_glb = _codec.pack_glb, _codec.read_glb
_accessor = _glb._accessor
append_glb_animation, glb_meshes = _glb.append_glb_animation, _glb.glb_meshes
load_glb_target, validate_glb_axes = _glb.load_glb_target, _glb.validate_glb_axes


PAIRS = [('pelvis', 'Hips'), ('head', 'Head'), ('left_hip', 'LeftHip')]


def rig(turn=0, tilt=0, skin_mesh=True):
    """Nonidentity local bone rests, scene transform, mesh transform, two sets."""
    binary = bytearray(b'OLD!')
    document = {
        'asset': {'version': '2.0'}, 'buffers': [{'byteLength': 4}],
        'bufferViews': [], 'accessors': [],
        'nodes': [
            {'name': 'Scene', 'translation': [3, 2, 5],
             'rotation': [np.sin(tilt / 2), np.sin(turn / 2), 0, np.cos((turn + tilt) / 2)], 'children': [1, 4]},
            {'name': 'Hips', 'translation': [0, 1, 0],
             'rotation': [0, 0, np.sin(0.15), np.cos(0.15)], 'children': [2, 3]},
            {'name': 'Head', 'translation': [0, 1.5, 0]},
            {'name': 'LeftHip', 'translation': [0.4, -0.1, 0]},
            {'name': 'Mesh', 'translation': [7, 0, 0], 'mesh': 0},
        ],
        'skins': [{'joints': [1, 2, 3]}],
        'meshes': [{'primitives': [{'attributes': {}}]}],
        'scenes': [{'nodes': [0]}], 'scene': 0,
        'materials': [{'name': 'unchanged'}],
        'animations': [{'name': 'original', 'channels': [], 'samplers': [], 'extras': {'original': True}}],
    }
    def accessor(values, kind, dtype='<f4', component=5126):
        values = np.asarray(values, dtype=dtype)
        offset = len(binary)
        binary.extend(values.tobytes())
        document['bufferViews'].append({'buffer': 0, 'byteOffset': offset, 'byteLength': values.nbytes})
        document['accessors'].append({'bufferView': len(document['bufferViews']) - 1,
                                     'componentType': component, 'count': len(values), 'type': kind})
        return len(document['accessors']) - 1
    primitive = document['meshes'][0]['primitives'][0]
    attrs = primitive['attributes']
    attrs['POSITION'] = accessor([[0, 0, 0], [1, 0, 0], [0, 1, 0]], 'VEC3')
    primitive['indices'] = accessor([0, 1, 2], 'SCALAR', '<u2', 5123)
    # Alignment before the next float accessor.
    binary.extend(b'\0' * (-len(binary) % 4))
    if skin_mesh:
        document['nodes'][4]['skin'] = 0
        for index in range(2):
            attrs[f'JOINTS_{index}'] = accessor([[index, 0, 0, 0]] * 3, 'VEC4', 'u1', 5121)
            # The unnormalized sum is 4 per vertex across both sets.
            attrs[f'WEIGHTS_{index}'] = accessor([[1 if index == 0 else 3, 0, 0, 0]] * 3, 'VEC4')
    # IBM deliberately differs from rest inverse: only skinning may read it.
    inverse = np.repeat(np.eye(4)[None], 3, axis=0)
    inverse[1, 0, 3] = 2
    document['skins'][0]['inverseBindMatrices'] = accessor(inverse.transpose(0, 2, 1).reshape(3, 16), 'MAT4')
    document['buffers'][0]['byteLength'] = len(binary)
    return pack_glb(document, binary)


def solved_rest(target, count=2):
    world_to_local_rotations = _core.world_to_local_rotations
    skeleton = target['skeleton']
    local = world_to_local_rotations(skeleton['rest_rotations'], skeleton['parents'])
    root = skeleton['names'].index('Hips')
    positions = np.repeat(skeleton['rest_positions'][root][None], count, axis=0)
    positions[:, 0] += np.arange(count)
    return {'local_rotations': np.repeat(local[None], count, axis=0), 'root_positions': positions, 'scale': 1.25}


def test_world_rest_comes_from_node_trs_including_scene_ancestor_not_ibm():
    target = load_glb_target(rig(), PAIRS)
    skeleton = target['skeleton']
    np.testing.assert_allclose(skeleton['rest_positions'][skeleton['names'].index('Hips')], [3, 3, 5])
    np.testing.assert_allclose(skeleton['rest_rotations'][skeleton['names'].index('Hips')],
                               [0, 0, np.sin(0.15), np.cos(0.15)])
    assert skeleton['parents'].tolist() == [-1, 0, 1, 1]
    assert target['axis_report']['forward'] == '+Z'


@pytest.mark.parametrize('turn,tilt,message', [(np.pi, 0, 'left hip'), (0, np.pi / 2, 'pelvis-to-head')])
def test_measured_axes_reject_backwards_and_z_up_even_with_familiar_names(turn, tilt, message):
    with pytest.raises(ValueError, match=message):
        load_glb_target(rig(turn, tilt), PAIRS)


def test_nonjoint_ancestor_turn_is_in_world_rest():
    target = load_glb_target(rig(turn=0.4))
    quaternion_to_matrix = _core.quaternion_to_matrix
    expected = quaternion_to_matrix(np.array([0, np.sin(0.2), 0, np.cos(0.2)]))
    base = load_glb_target(rig())
    left = target['skeleton']['rest_positions'][3] - [3, 2, 5]
    original = base['skeleton']['rest_positions'][3] - [3, 2, 5]
    np.testing.assert_allclose(left, expected @ original, atol=1e-7)


def test_append_preserves_whole_document_except_allowed_arrays_and_bin_prefix():
    blob = rig()
    target = load_glb_target(blob, PAIRS)
    original = copy.deepcopy(target['document'])
    output = append_glb_animation(target, solved_rest(target), 24, 'Hips', {'accepted': True})
    changed, binary = read_glb(output)
    assert binary.startswith(target['binary'])
    for key in original.keys() - {'animations', 'accessors', 'bufferViews', 'buffers'}:
        assert changed[key] == original[key]
    for key in ('animations', 'accessors', 'bufferViews'):
        assert changed[key][:len(original[key])] == original[key]
    assert changed['buffers'][0].keys() == original['buffers'][0].keys()
    assert target['document'] == original
    clip = changed['animations'][-1]
    assert len(clip['channels']) == 4
    assert {row['target']['node'] for row in clip['channels'] if row['target']['path'] == 'rotation'} == {1, 2, 3}
    translation = next(row for row in clip['channels'] if row['target']['path'] == 'translation')
    assert translation['target']['node'] == 1
    sampler = clip['samplers'][translation['sampler']]
    np.testing.assert_allclose(_accessor(changed, binary, sampler['output']), [[0, 1, 0], [1, 1, 0]], atol=1e-6)
    assert all(row['interpolation'] == 'LINEAR' for row in clip['samplers'])
    assert clip['extras']['lf_motion_retarget']['fps'] == 24


def test_skinning_uses_both_weight_sets_ibm_columns_and_scene_world_without_double_mesh_transform():
    quaternion_to_matrix = _core.quaternion_to_matrix
    target = load_glb_target(rig())
    solved = solved_rest(target)
    output = append_glb_animation(target, solved, 30, 'Hips')
    batches, faces, metadata = glb_meshes(output, batch_size=1)
    vertices = np.concatenate(list(batches()))
    positions = np.array([[0, 0, 0, 1], [1, 0, 0, 1], [0, 1, 0, 1]])
    world = target['world_matrices']
    inverse = np.eye(4)
    inverse[0, 3] = 2
    expected = 0.25 * (positions @ world[1].T) + 0.75 * (positions @ (world[2] @ inverse).T)
    np.testing.assert_allclose(vertices[0], expected[:, :3], atol=1e-6)
    np.testing.assert_allclose(vertices[1] - vertices[0], np.repeat([[1, 0, 0]], 3, axis=0), atol=1e-6)
    np.testing.assert_array_equal(faces, [[0, 1, 2]])
    assert metadata['frame_count'] == 2 and metadata['scale'] == 1.25
    np.testing.assert_allclose(batches.root_positions, solved['root_positions'], atol=1e-6)
    np.testing.assert_allclose(np.concatenate(list(batches())), vertices)


def test_unskinned_mesh_scene_transform_is_applied():
    target = load_glb_target(rig(skin_mesh=False))
    output = append_glb_animation(target, solved_rest(target), 30, 'Hips')
    batches, _, _ = glb_meshes(output)
    vertices = next(batches())
    np.testing.assert_allclose(vertices[0], [[10, 2, 5], [11, 2, 5], [10, 3, 5]], atol=1e-6)
    np.testing.assert_allclose(vertices[1], vertices[0])


def test_world_pelvis_translation_converts_through_turned_scene_parent():
    target = load_glb_target(rig(turn=0.4))
    solved = solved_rest(target)
    output = append_glb_animation(target, solved, 30, 'Hips')
    document, binary = read_glb(output)
    clip = document['animations'][-1]
    translation = next(row for row in clip['channels'] if row['target']['path'] == 'translation')
    local = _accessor(document, binary, clip['samplers'][translation['sampler']]['output'])
    world = np.column_stack([local, np.ones(2)]) @ target['world_matrices'][0].T
    np.testing.assert_allclose(world[:, :3], solved['root_positions'], atol=1e-6)


@pytest.mark.parametrize('mutation,message', [
    (lambda doc: doc['skins'].append({'joints': [1]}), 'exactly one'),
    (lambda doc: doc['nodes'][2].update(name='Hips'), 'distinct'),
    (lambda doc: doc['nodes'][1].update(matrix=np.eye(4).ravel().tolist()), 'must use TRS'),
])
def test_unsupported_target_admission_is_actionable(mutation, message):
    document, binary = read_glb(rig())
    mutation(document)
    with pytest.raises(ValueError, match=message):
        load_glb_target(pack_glb(document, binary))


def test_nonuniform_scene_scale_keeps_node_rotation_chain_and_skins_exactly():
    document, binary = read_glb(rig())
    document['nodes'][0]['scale'] = [2, 3, 4]
    target = load_glb_target(pack_glb(document, binary), PAIRS)
    skeleton = target['skeleton']
    np.testing.assert_allclose(skeleton['rest_positions'][1], [3, 5, 5])
    np.testing.assert_allclose(skeleton['rest_rotations'][1], [0, 0, np.sin(0.15), np.cos(0.15)])
    output = append_glb_animation(target, solved_rest(target), 30, 'Hips')
    batches, _, _ = glb_meshes(output)
    vertices = next(batches())
    np.testing.assert_allclose(vertices[1] - vertices[0], np.repeat([[1, 0, 0]], 3, axis=0), atol=2e-6)


def test_static_morph_node_weights_override_mesh_weights_and_unrelated_extensions_survive():
    document, binary = read_glb(rig(skin_mesh=False))
    primitive = document['meshes'][0]['primitives'][0]
    primitive['targets'] = [{'POSITION': primitive['attributes']['POSITION']}]
    primitive['extensions'] = {'KHR_materials_variants': {'mappings': []}}
    document['meshes'][0]['weights'] = [0.25]
    document['nodes'][4]['weights'] = [0.5]
    target = load_glb_target(pack_glb(document, binary))
    output = append_glb_animation(target, solved_rest(target), 30, 'Hips')
    batches, _, _ = glb_meshes(output)
    np.testing.assert_allclose(next(batches())[0], [[10, 2, 5], [11.5, 2, 5], [10, 3.5, 5]], atol=1e-6)



@pytest.mark.parametrize('node,mirror', [
    (1, {'scale': [-1, 1, 1]}),
    (0, {'matrix': [-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 3, 2, 5, 1]}),
])
def test_a_mirrored_joint_or_ancestor_is_refused_by_name(node, mirror):
    document, binary = read_glb(rig())
    if 'matrix' in mirror:
        for key in ('translation', 'rotation'):
            document['nodes'][node].pop(key, None)
    document['nodes'][node].update(mirror)
    name = document['nodes'][node]['name']
    with pytest.raises(ValueError, match=f"'{name}' is mirrored"):
        load_glb_target(pack_glb(document, binary))


def test_neck_measures_the_up_axis_when_the_map_has_no_head():
    target = load_glb_target(rig())
    report = validate_glb_axes(target, [('pelvis', 'Hips'), ('neck', 'Head'), ('left_hip', 'LeftHip')])
    assert report['up_joint'] == 'neck' and report['up'] == '+Y'
    assert 'pelvis_to_neck' in report


def test_matrix_nonjoint_ancestor_rest_is_preserved():
    document, binary = read_glb(rig())
    # Matrix ancestor is legal because only skin joints receive TRS channels.
    document['nodes'][0] = {'name': 'Scene', 'children': [1, 4],
                            'matrix': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 3, 2, 5, 1]}
    target = load_glb_target(pack_glb(document, binary))
    output = append_glb_animation(target, solved_rest(target), 30, 'Hips')
    batches, _, _ = glb_meshes(output)
    vertices = next(batches())
    expected = (0.25 * target['world_matrices'][1][:3, 3]
                + 0.75 * (target['world_matrices'][2] @ [2, 0, 0, 1])[:3])
    np.testing.assert_allclose(vertices[0, 0], expected, atol=1e-6)
    np.testing.assert_allclose(vertices[1] - vertices[0], [[1, 0, 0]] * 3, atol=1e-6)
    changed, _ = read_glb(output)
    assert changed['nodes'] == document['nodes']


def test_follower_translation_channel_places_it_in_world_after_the_translated_pelvis():
    target = load_glb_target(rig(turn=0.4), PAIRS)
    solved = solved_rest(target)
    placed = np.array([[3.5, 2.8, 5.2], [4.0, 3.1, 4.9]])
    solved['follower_positions'] = {'LeftHip': placed}
    document, binary = read_glb(append_glb_animation(target, solved, 30, 'Hips'))
    clip = document['animations'][-1]
    translations = [row for row in clip['channels'] if row['target']['path'] == 'translation']
    assert [row['target']['node'] for row in translations] == [1, 3]
    values = {row['target']['node']: _accessor(document, binary, clip['samplers'][row['sampler']]['output'])
              for row in translations}
    for frame in range(2):
        local = target['local_matrices'].copy()
        for node, value in values.items():
            local[node, :3, 3] = value[frame]
        world = _glb._world_matrices(local, target['parents'])
        np.testing.assert_allclose(world[1, :3, 3], solved['root_positions'][frame], atol=1e-6)
        np.testing.assert_allclose(world[3, :3, 3], placed[frame], atol=1e-6)
    without = read_glb(append_glb_animation(target, solved_rest(target), 30, 'Hips'))
    assert len([row for row in without[0]['animations'][-1]['channels']
                if row['target']['path'] == 'translation']) == 1
    with pytest.raises(ValueError, match="Follower 'Scene'"):
        append_glb_animation(target, dict(solved, follower_positions={'Scene': placed}), 30, 'Hips')


def test_a_posed_follower_rides_its_leader_rigidly_through_the_written_clip():
    """Core solve to GLB channels to posed node matrices: the follower's world is its leader's delta times its rest,
    with every parent away from rest (the turned scene, a rotated and translated pelvis)."""
    target = load_glb_target(rig(turn=0.4), PAIRS)
    skeleton = target['skeleton']
    source = dict(names=['root', 'pelvis', 'head', 'left_hip'], parents=skeleton['parents'],
                  rest_positions=skeleton['rest_positions'], rest_rotations=skeleton['rest_rotations'])
    rng = np.random.default_rng(3)
    frames = 3
    world = np.repeat(skeleton['rest_rotations'][None], frames, axis=0)
    turns = rng.normal(size=(frames - 1, len(source['names']) - 1, 4))
    world[1:, 1:] = turns / np.linalg.norm(turns, axis=-1, keepdims=True)
    roots = skeleton['rest_positions'][1] + rng.normal(size=(frames, 3))
    solved = _core.retarget_motion(world, roots, source, skeleton, [('pelvis', 'Hips'), ('left_hip', 'LeftHip')],
                                   follow={'Head': 'LeftHip'}, scale=1)
    document, binary = read_glb(append_glb_animation(target, solved, 30, 'Hips'))
    clip = document['animations'][-1]
    rest_world = _glb._world_matrices(target['local_matrices'].copy(), target['parents'])
    head, hip = 2, 3
    for frame in range(frames):
        local = target['local_matrices'].copy()
        for channel in clip['channels']:
            node, path = channel['target']['node'], channel['target']['path']
            value = _accessor(document, binary, clip['samplers'][channel['sampler']]['output'])[frame]
            if path == 'rotation':
                local[node, :3, :3] = _glb._rotations()[1](value)
            else:
                local[node, :3, 3] = value
        posed = _glb._world_matrices(local, target['parents'])
        assert not np.allclose(posed[hip, :3, :3], rest_world[hip, :3, :3]) or frame == 0
        np.testing.assert_allclose(posed[head], posed[hip] @ np.linalg.inv(rest_world[hip]) @ rest_world[head],
                                   atol=1e-5)


def _turn_angle(rotation):
    return np.degrees(np.arccos(np.clip((np.trace(rotation) - 1) / 2, -1, 1)))


@pytest.mark.parametrize('rule', [{'leader': 'LeftHip', 'weight': .5},
                                  {'leader': 'LeftHip', 'weight': 0, 'twist': .5, 'axis': ['Hips', 'LeftHip']}])
def test_a_posed_share_follower_through_the_written_clip(rule):
    """Core solve to GLB channels to posed node matrices, with the scene turned and the pelvis moving: a weighted
    follower turns halfway from its leader's parent to its leader about the leader's joint; a twist follower takes
    half the leader's twist about the axis and none of its swing."""
    target = load_glb_target(rig(turn=0.4), PAIRS)
    skeleton = target['skeleton']
    source = dict(names=['root', 'pelvis', 'head', 'left_hip'], parents=skeleton['parents'],
                  rest_positions=skeleton['rest_positions'], rest_rotations=skeleton['rest_rotations'])
    rng = np.random.default_rng(5)
    frames = 3
    world = np.repeat(skeleton['rest_rotations'][None], frames, axis=0)
    turns = rng.normal(size=(frames - 1, len(source['names']) - 1, 4))
    world[1:, 1:] = turns / np.linalg.norm(turns, axis=-1, keepdims=True)
    roots = skeleton['rest_positions'][1] + rng.normal(size=(frames, 3))
    solved = _core.retarget_motion(world, roots, source, skeleton, [('pelvis', 'Hips'), ('left_hip', 'LeftHip')],
                                   follow={'Head': rule}, scale=1)
    document, binary = read_glb(append_glb_animation(target, solved, 30, 'Hips'))
    clip = document['animations'][-1]
    assert {(row['target']['node'], row['target']['path']) for row in clip['channels']} >= {(2, 'translation')}
    rest_world = _glb._world_matrices(target['local_matrices'].copy(), target['parents'])
    hips, head, hip = 1, 2, 3
    axis = rest_world[hip, :3, 3] - rest_world[hips, :3, 3]
    axis /= np.linalg.norm(axis)
    for frame in range(1, frames):
        local = target['local_matrices'].copy()
        for channel in clip['channels']:
            node, path = channel['target']['node'], channel['target']['path']
            value = _accessor(document, binary, clip['samplers'][channel['sampler']]['output'])[frame]
            if path == 'rotation':
                local[node, :3, :3] = _glb._rotations()[1](value)
            else:
                local[node, :3, 3] = value
        posed = _glb._world_matrices(local, target['parents'])
        delta = {i: posed[i, :3, :3] @ rest_world[i, :3, :3].T for i in (hips, head, hip)}
        turn = delta[hips].T @ delta[hip]  # the leader's turn from its parent's, in rest axes
        own = delta[hips].T @ delta[head]
        if 'twist' in rule:
            # A pure twist about the axis, half the leader's twist (turn = swing * twist).
            np.testing.assert_allclose(own @ axis, axis, atol=1e-5)
            quaternion = _core.quaternion_from_matrix(turn)
            _, twist = _core.swing_twist(quaternion, axis)
            assert _turn_angle(own) == pytest.approx(_turn_angle(_core.quaternion_to_matrix(twist)) / 2, abs=1e-3)
        else:
            assert _turn_angle(turn) > 20
            assert _turn_angle(own) == pytest.approx(_turn_angle(turn) / 2, abs=1e-3)
            assert _turn_angle(own.T @ turn) == pytest.approx(_turn_angle(turn) / 2, abs=1e-3)
        # Its rest offset from the leader's joint turns by its own delta.
        np.testing.assert_allclose(posed[head, :3, 3], posed[hip, :3, 3] + delta[head] @ (
            rest_world[head, :3, 3] - rest_world[hip, :3, 3]), atol=1e-5)
