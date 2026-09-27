"""CPU contracts and transform mathematics; no renderer or GPU imports needed."""
import copy
import importlib.util
import math
import struct
import sys
import types
from io import BytesIO
from pathlib import Path

import numpy as np
import pytest

from modules.utils.glb_texture import pack_glb, read_glb
from modules.utils.glb_transform import scale_glb_nodes, transform_document


def scene():
    # Two channels share a cubic sampler deliberately. Its values and tangents
    # must stay exact, as must all binary data including the embedded image.
    binary = struct.pack('<20f', *range(20)) + b'IMAGEPNG'
    return {
        'asset': {'version': '2.0'}, 'buffers': [{'byteLength': len(binary)}],
        'bufferViews': [{'buffer': 0, 'byteOffset': 0, 'byteLength': 80},
                        {'buffer': 0, 'byteOffset': 80, 'byteLength': 8}],
        'accessors': [{'bufferView': 0, 'componentType': 5126, 'count': 2, 'type': 'SCALAR'},
                      {'bufferView': 0, 'byteOffset': 8, 'componentType': 5126, 'count': 6, 'type': 'VEC3'}],
        'images': [{'bufferView': 1, 'mimeType': 'image/png'}],
        'textures': [{'source': 0}],
        'materials': [{'pbrMetallicRoughness': {'baseColorTexture': {'index': 0}}}],
        'nodes': [
            {'name': 'scene', 'children': [1, 3, 4]},
            {'name': 'selected', 'translation': [2, 3, -1],
             'rotation': [0, 0, math.sin(0.4), math.cos(0.4)],
             'scale': [1.2, 0.8, 1.6], 'children': [2]},
            {'name': 'child', 'translation': [0.2, 0.4, -0.1]},
            {'name': 'other', 'scale': [0.9, 1.1, 1.2]},
            {'name': 'mesh', 'mesh': 0, 'skin': 0}],
        'skins': [{'joints': [1, 2, 3], 'skeleton': 0}, {'joints': [1, 2], 'skeleton': 0}],
        'meshes': [{'primitives': [{'attributes': {'POSITION': 0}, 'material': 0}]}],
        'animations': [{'name': 'motion', 'samplers': [
            {'input': 0, 'output': 1, 'interpolation': 'CUBICSPLINE'}], 'channels': [
            {'sampler': 0, 'target': {'node': 1, 'path': 'scale'}},
            {'sampler': 0, 'target': {'node': 3, 'path': 'scale'}}]}],
        'scene': 0, 'scenes': [{'nodes': [0]}],
    }, binary


def recipe(anchor=None):
    row = {'nodeIndex': 1, 'nodeName': 'selected'}
    if anchor is not None:
        row['anchorLocal'] = anchor
    return {'nodes': [row], 'minPercent': 65, 'maxPercent': 115}


def test_preserves_binary_scene_original_trs_and_every_animation_record():
    document, binary = scene()
    original = copy.deepcopy(document)
    anchor = [0.2, -0.8, 0.1]
    result = scale_glb_nodes(pack_glb(document, binary), recipe(anchor), 75)
    changed, payload = read_glb(result)
    assert payload == binary
    for key in document.keys() - {'nodes', 'skins'}:
        assert changed[key] == original[key]
    assert changed['nodes'][1] == dict(original['nodes'][1], children=[5])
    assert changed['nodes'][5] == {'name': 'selected scale', 'translation': [0.25 * v for v in anchor],
                                  'scale': [0.75] * 3, 'children': [2]}
    assert changed['skins'] == [dict(original['skins'][0], joints=[5, 2, 3]),
                               dict(original['skins'][1], joints=[5, 2])]
    assert document == original


@pytest.mark.parametrize('anchor', [[0, 0, 0], [0.2, -0.8, 0.1]])
@pytest.mark.parametrize('factor', [0.65, 1.15])
def test_wrapper_math_preserves_anchor_under_original_and_animated_trs(anchor, factor):
    document, binary = scene()
    result, _ = transform_document(document, [{'nodeIndex': 1, 'factor': factor, 'anchorLocal': anchor}])
    wrapper = result['nodes'][-1]
    anchor = np.array(anchor)
    point = np.array([0.7, -1.1, 0.4])
    # Evaluate a cubic scale curve from the actual retained sampler payload.
    samples = np.array(struct.unpack('<18f', binary[8:80])).reshape(6, 3)
    for t in [0, 0.23, 0.8, 1]:
        animated_scale = ((2*t**3-3*t**2+1)*samples[1] + (t**3-2*t**2+t)*samples[2]
                          + (-2*t**3+3*t**2)*samples[4] + (t**3-t**2)*samples[3])
        for scale in [document['nodes'][1]['scale'], animated_scale]:
            angle = 0.8 + t
            rotation = np.array([[math.cos(angle), -math.sin(angle), 0],
                                 [math.sin(angle), math.cos(angle), 0], [0, 0, 1]])
            linear = rotation @ np.diag(scale)
            translation = np.array(document['nodes'][1]['translation']) + t
            offset = np.array(wrapper['translation'])
            wrapper_scale = np.array(wrapper['scale'])
            assert np.allclose(translation + linear @ (offset + wrapper_scale * anchor),
                               translation + linear @ anchor)
            assert np.allclose(translation + linear @ (offset + wrapper_scale * point),
                               translation + linear @ (anchor + factor * (point - anchor)))


def test_independent_groups_and_document_report_do_not_alias():
    document, _ = scene()
    controls = [{'nodeIndex': 1, 'factor': 0.75}, {'nodeIndex': 3, 'factor': 1.1}]
    result, report = transform_document(document, controls)
    assert [row['deformNodeIndex'] for row in report['anchoredRoots']] == [5, 6]
    assert result['skins'][0]['joints'] == [5, 2, 6]
    assert report['changedScaleChannels'] == 0
    assert report['clipCount'] == 1
    result['animations'][0]['name'] = 'changed'
    report['controls'][0]['nodeIndex'] = 99
    assert document['animations'][0]['name'] == 'motion'
    assert controls[0]['nodeIndex'] == 1


@pytest.mark.parametrize('targets', [None, {}, {'nodes': []}, recipe()])
def test_identity_is_byte_exact(targets):
    document, binary = scene()
    blob = pack_glb(document, binary)
    assert scale_glb_nodes(blob, targets, 100) is blob
    result, report = transform_document(document, [{'nodeIndex': 1, 'factor': 1}])
    assert result == document and result is not document
    assert report['anchoredRoots'] == []


@pytest.mark.parametrize('targets,percent,match', [
    (None, 99, 'No configured nodes'), ({}, 99, 'No configured nodes'),
    ([], 100, 'JSON object'), ({'nodes': {}}, 100, 'array'),
    ({'nodes': [1]}, 100, 'objects'), (recipe(), float('nan'), 'finite'),
    (recipe(), float('inf'), 'finite'), (recipe(), True, 'finite'),
    (recipe(), 0, 'between'), (recipe(), 201, 'between'), (recipe(), 60, 'recipe range'),
    ({'minPercent': 101, 'maxPercent': 80}, 100, 'range'),
    ({'minPercent': float('nan')}, 100, 'finite'),
    ({'maxPercent': 201}, 100, 'range'),
])
def test_recipe_and_percent_errors(targets, percent, match):
    document, binary = scene()
    with pytest.raises(ValueError, match=match):
        scale_glb_nodes(pack_glb(document, binary), targets, percent)


@pytest.mark.parametrize('controls,match', [
    ([{'nodeIndex': 99, 'factor': 1}], 'existing'),
    ([{'nodeIndex': True, 'factor': 1}], 'existing'),
    ([{'nodeIndex': 0, 'factor': 1}], 'skin joint'),
    ([{'nodeIndex': 1, 'nodeName': 'wrong', 'factor': 1}], 'nodeName'),
    ([{'nodeIndex': 1, 'factor': 1}, {'nodeIndex': 1, 'factor': 0.8}], 'distinct'),
    ([{'nodeIndex': 1, 'factor': 1}, {'nodeIndex': 2, 'factor': 0.8}], 'nonoverlapping'),
    ([{'nodeIndex': 1, 'factor': 0}], 'between'),
    ([{'nodeIndex': 1, 'factor': float('nan')}], 'finite'),
    ([{'nodeIndex': 1, 'factor': 1, 'anchorLocal': [0, 0]}], 'three'),
    ([{'nodeIndex': 1, 'factor': 1, 'anchorLocal': [0, 0, float('inf')]}], 'finite'),
])
def test_control_errors(controls, match):
    document, _ = scene()
    with pytest.raises(ValueError, match=match):
        transform_document(document, controls)


@pytest.mark.parametrize('mutation,match', [
    (lambda d: d['nodes'][1].update(children=[99]), 'existing'),
    (lambda d: d['nodes'][1].update(children=[2, 2]), 'repeat'),
    (lambda d: d['nodes'][3].update(children=[2]), 'share'),
    (lambda d: d['nodes'][2].update(children=[0]), 'cycle'),
    (lambda d: d['skins'][0].update(joints=[1, 99]), 'existing'),
    (lambda d: d['skins'][0].update(joints=[1, 1]), 'distinct'),
    (lambda d: d['skins'][0].update(joints=[]), 'empty'),
])
def test_malformed_graph_and_skin_errors(mutation, match):
    document, _ = scene()
    mutation(document)
    with pytest.raises(ValueError, match=match):
        transform_document(document, [{'nodeIndex': 1, 'factor': 0.75}])


def test_pure_document_helper_loads_without_package_or_comfy():
    path = Path(__file__).resolve().parents[3] / 'utils' / 'glb_transform.py'
    spec = importlib.util.spec_from_file_location('standalone_glb_transform', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    document, _ = scene()
    result, _ = module.transform_document(document, [{'nodeIndex': 1, 'factor': 0.75}])
    assert result['nodes'][-1]['scale'] == [0.75] * 3


@pytest.fixture
def node(monkeypatch):
    class File3D:
        def __init__(self, source, file_format='glb'):
            self.source, self.format = source, file_format

        def get_bytes(self):
            return Path(self.source).read_bytes() if isinstance(self.source, str) else self.source.getvalue()

    latest = types.ModuleType('comfy_api.latest')
    latest.Types = types.SimpleNamespace(File3D=File3D)
    monkeypatch.setitem(sys.modules, 'comfy_api.latest', latest)
    from modules.nodes.io.scale_glb_nodes import LF_ScaleGLBNodes
    return LF_ScaleGLBNodes(), File3D


@pytest.mark.parametrize('list_mode', [False, True])
def test_node_headless_and_disk_source_never_written(node, tmp_path, list_mode):
    transform, File3D = node
    document, binary = scene()
    blob = pack_glb(document, binary)
    path = tmp_path / 'source.glb'
    path.write_bytes(blob)
    values = [File3D(str(path)), recipe(), 75]
    if list_mode:
        values = [[value] for value in values]
    output, = transform.on_exec(*values)
    assert output.format == 'glb' and isinstance(output.source, BytesIO)
    assert read_glb(output.get_bytes())[1] == binary
    assert path.read_bytes() == blob
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize('input_index', [0, 1, 2])
@pytest.mark.parametrize('count', [0, 2])
def test_exact_input_cardinality(node, input_index, count):
    transform, _ = node
    values = [None, None, 100]
    values[input_index] = [None] * count
    with pytest.raises(ValueError, match='exactly one'):
        transform.on_exec(*values)


def test_file3d_contract_and_schema(node):
    transform, File3D = node
    for source in ['source.glb', File3D(BytesIO(), 'obj')]:
        with pytest.raises(ValueError, match='FILE_3D_GLB'):
            transform.on_exec(source, None)
    required = transform.INPUT_TYPES()['required']
    assert list(required) == ['glb', 'targets', 'percent']
    assert [required[key][0] for key in required] == ['FILE_3D_GLB', 'JSON', 'FLOAT']
    assert {k: v for k, v in required['percent'][1].items() if k != 'tooltip'} == {
        'default': 100.0, 'min': 1.0, 'max': 200.0, 'step': 1.0}
    assert transform.INPUT_IS_LIST is True
    assert transform.RETURN_TYPES == ('FILE_3D_GLB',)
    assert transform.RETURN_NAMES == ('glb',)
    assert transform.OUTPUT_IS_LIST == (False,)
