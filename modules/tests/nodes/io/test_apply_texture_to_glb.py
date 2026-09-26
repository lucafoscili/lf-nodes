"""CPU-only GLB texture replacement, with no asset copies or renderer."""
import copy
import json
import struct
import sys
import types
from io import BytesIO

import pytest
import torch
from PIL import Image

from modules.utils.glb_texture import apply_texture_to_glb, read_glb


def source_document():
    # A second material deliberately shares the original texture.
    return {'asset': {'version': '2.0'}, 'buffers': [{'byteLength': 8}],
            'bufferViews': [{'buffer': 0, 'byteOffset': 0, 'byteLength': 8}],
            'images': [{'bufferView': 0, 'mimeType': 'image/png'}],
            'samplers': [{'wrapS': 33071, 'wrapT': 10497, 'minFilter': 9729}],
            'textures': [{'source': 0, 'sampler': 0, 'extras': {'retained': True}}],
            'materials': [{'alphaMode': 'MASK', 'alphaCutoff': 0.4,
                           'pbrMetallicRoughness': {'roughnessFactor': 0.9,
                             'baseColorFactor': [1, 0.5, 1, 0.8],
                             'baseColorTexture': {'index': 0, 'texCoord': 1,
                               'extensions': {'KHR_texture_transform': {'offset': [0.2, 0]}}}}},
                          {'pbrMetallicRoughness': {'baseColorTexture': {'index': 0}}}],
            'meshes': [{'primitives': [{'material': 0, 'attributes': {'POSITION': 0, 'TEXCOORD_0': 1}},
                                       {'material': 1, 'attributes': {'POSITION': 0}}]}],
            'accessors': [], 'skins': [{'joints': [1], 'inverseBindMatrices': 0}],
            'animations': [{'name': 'idle', 'channels': [], 'samplers': []}],
            'nodes': [{'mesh': 0, 'skin': 0, 'rotation': [0, 0, 0, 1]}],
            'scenes': [{'nodes': [0]}], 'scene': 0,
            'extensionsUsed': ['KHR_texture_transform']}


def pack(document=None, binary=b'ORIGINAL'):
    document = source_document() if document is None else document
    encoded = json.dumps(document).encode()
    encoded += b' ' * (-len(encoded) % 4)
    return (struct.pack('<4sII', b'glTF', 2, 28 + len(encoded) + len(binary))
            + struct.pack('<II', len(encoded), 0x4E4F534A) + encoded
            + struct.pack('<II', len(binary), 0x004E4942) + binary)


@pytest.mark.parametrize('mode,pixel', [('RGB', (13, 27, 41)), ('RGBA', (13, 27, 41, 63))])
@pytest.mark.parametrize('target', [0, 1])
def test_preserves_scene_binary_shared_map_and_alpha(mode, pixel, target):
    original = source_document()
    blob = pack(original)
    result = apply_texture_to_glb(blob, Image.new(mode, (3, 2), pixel), target)
    document, binary = read_glb(result)
    expected = copy.deepcopy(original)
    expected['materials'][target]['pbrMetallicRoughness']['baseColorTexture']['index'] = 1
    for key in original:
        if key not in ('buffers', 'bufferViews', 'images', 'textures'):
            assert document[key] == expected[key]
    assert binary[:8] == b'ORIGINAL'
    assert document['bufferViews'][:-1] == original['bufferViews']
    assert document['images'][:-1] == original['images']
    assert document['textures'][0] == original['textures'][0]
    assert document['textures'][1] == {**original['textures'][0], 'source': 1}
    view = document['bufferViews'][-1]
    png = binary[view['byteOffset']:view['byteOffset'] + view['byteLength']]
    with Image.open(BytesIO(png)) as image:
        assert image.mode == mode
        assert image.size == (3, 2)
        assert image.getpixel((0, 0)) == pixel
    assert blob == pack(original)


@pytest.mark.parametrize('mutation,match', [
    (lambda d: d['buffers'][0].update(uri='outside.bin'), 'self-contained'),
    (lambda d: d['images'][0].update(uri='outside.png'), 'embedded'),
    (lambda d: d['bufferViews'][0].update(byteLength=999), 'buffer view'),
    (lambda d: d['textures'][0].update(source=99), 'source index'),
    (lambda d: d['textures'][0].update(extensions={'KHR_texture_basisu': {'source': 0}}), 'extensions'),
    (lambda d: d['materials'][0].pop('pbrMetallicRoughness'), 'base-color'),
    (lambda d: d['asset'].update(version='1.0'), 'version'),
])
def test_rejects_unsupported_resources_and_bindings(mutation, match):
    document = source_document()
    mutation(document)
    with pytest.raises(ValueError, match=match):
        apply_texture_to_glb(pack(document), Image.new('RGB', (1, 1)))


@pytest.mark.parametrize('blob', [b'', b'not a glb', pack()[:-1]])
def test_rejects_truncated_glb(blob):
    with pytest.raises(ValueError, match='GLB'):
        apply_texture_to_glb(blob, Image.new('RGB', (1, 1)))


def test_rejects_material_and_image_mode():
    with pytest.raises(ValueError, match='material index'):
        apply_texture_to_glb(pack(), Image.new('RGB', (1, 1)), 2)
    with pytest.raises(ValueError, match='RGB'):
        apply_texture_to_glb(pack(), Image.new('L', (1, 1)))


@pytest.fixture
def node(monkeypatch):
    # File3D is a host boundary; no Comfy GPU stack is needed to exercise bytes.
    class File3D:
        def __init__(self, source, file_format):
            self.source, self.format = source, file_format

        def get_bytes(self):
            return self.source.getvalue()

    latest = types.ModuleType('comfy_api.latest')
    latest.Types = types.SimpleNamespace(File3D=File3D)
    monkeypatch.setitem(sys.modules, 'comfy_api.latest', latest)
    from modules.nodes.io.apply_texture_to_glb import LF_ApplyTextureToGLB
    return LF_ApplyTextureToGLB()


def test_node_headless_in_memory_and_no_source_write(node, tmp_path):
    source = tmp_path / 'source.glb'
    source.write_bytes(pack())
    before = source.read_bytes()
    image = torch.tensor([[[[1., 0., 0., 0.5]]]])
    result, = node.on_exec([str(source)], [image], [1])
    assert result.format == 'glb'
    document, _ = read_glb(result.get_bytes())
    assert document['materials'][1]['pbrMetallicRoughness']['baseColorTexture']['index'] == 1
    assert source.read_bytes() == before
    assert list(tmp_path.iterdir()) == [source]


@pytest.mark.parametrize('source,image,material,match', [
    (['a', 'b'], torch.zeros(1, 2, 2, 3), 0, 'exactly one'),
    ('a', torch.zeros(2, 2, 2, 3), 0, 'exactly one image'),
    ('a', [torch.zeros(1, 2, 2, 3), torch.zeros(1, 2, 2, 4)], 0, 'exactly one image'),
    ('a', torch.zeros(1, 2, 2, 3), [0, 1], 'exactly one'),
    ('a', torch.zeros(1, 2, 2, 3), -1, 'non-negative'),
])
def test_node_cardinality_fails_before_file_access(node, source, image, material, match):
    with pytest.raises(ValueError, match=match):
        node.on_exec(source, image, material)


def test_public_schema(node):
    assert set(node.INPUT_TYPES()['required']) == {'source_glb', 'texture', 'material_index'}
    assert node.INPUT_IS_LIST is True
    assert node.RETURN_TYPES == ('FILE_3D_GLB',)
    assert node.RETURN_NAMES == ('glb',)
    assert node.OUTPUT_IS_LIST == (False,)


def test_source_changes_invalidate_cache(node, tmp_path):
    source = tmp_path / 'source.glb'
    source.write_bytes(pack())
    old = node.IS_CHANGED([str(source)])
    document = source_document()
    document['extras'] = {'new_revision': True}
    source.write_bytes(pack(document))
    assert node.IS_CHANGED([str(source)]) != old


def test_relative_source_uses_core_annotated_resolver(node, tmp_path, monkeypatch):
    import folder_paths
    source = tmp_path / 'source.glb'
    source.write_bytes(pack())
    seen = []
    def resolve(value):
        seen.append(value)
        return str(source)
    monkeypatch.setattr(folder_paths, 'get_annotated_filepath', resolve, raising=False)
    node.on_exec('source.glb [input]', torch.zeros(1, 2, 2, 3))
    assert seen == ['source.glb [input]']
