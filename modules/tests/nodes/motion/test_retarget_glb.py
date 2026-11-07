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
