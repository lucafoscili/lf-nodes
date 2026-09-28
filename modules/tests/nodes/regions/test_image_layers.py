"""Source-safe image-layer editing without editor/server/GPU dependencies."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
import pytest
import torch

from modules.nodes.regions.image_layers import LF_LoadImageLayers, LF_ComposeImageLayers
from modules.utils.helpers.conversion import pil_to_tensor
from modules.utils.image_layers import load_image_layers, compose_image_layers
from modules.utils.constants import Input


def save_rgba(path: Path, size, seed, *, opaque=False):
    generator = np.random.default_rng(seed)
    pixels = generator.integers(0, 256, (size[1], size[0], 4), dtype=np.uint8)
    if opaque:
        pixels[..., 3] = 255
    Image.fromarray(pixels, 'RGBA').save(path)
    return pixels


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tensor_bytes(image):
    return image.detach().clamp(0, 1).mul(255).round().to(torch.uint8).cpu().numpy()[0].tobytes()


def fixture(tmp_path, *, overlap=False):
    root = tmp_path / 'layers'
    nested = root / 'nested'
    nested.mkdir(parents=True)
    first = root / 'first.png'
    second = nested / 'second.png'
    save_rgba(first, (4, 2), 3)
    save_rgba(second, (2, 1), 5, opaque=True)
    manifest = {
        'root': str(root),
        'layers': [
            {'id': 'lower', 'label': 'Lower cloth', 'file': 'first.png',
             'sha256': digest(first), 'rect': [1, 2, 4, 2]},
            {'id': 'upper', 'label': 'Upper cloth', 'file': 'nested/second.png',
             'sha256': digest(second), 'rect': [1 if overlap else 4, 2, 4, 2]},
        ],
    }
    return root, manifest


def base_image(size=(8, 8)):
    image = Image.new('RGB', size, (11, 22, 33))
    return image, pil_to_tensor(image)


def pillow_reference(base, manifest):
    atlas = base.convert('RGBA')
    root = Path(manifest['root'])
    for row in manifest['layers']:
        with Image.open(root / row['file']) as source:
            layer = source.convert('RGBA')
        x, y, width, height = row['rect']
        atlas.alpha_composite(layer.resize((width, height), Image.Resampling.LANCZOS), (x, y))
    return atlas


def test_loads_ordered_relative_rgba_sources_once_with_named_canvases(tmp_path, monkeypatch):
    root, manifest = fixture(tmp_path)
    reads = []
    real_read_bytes = Path.read_bytes

    def track(path):
        reads.append(Path(path).resolve())
        return real_read_bytes(path)

    monkeypatch.setattr(Path, 'read_bytes', track)
    images, layout, config, sources = load_image_layers(json.dumps(manifest), [16])
    assert len(images) == len(sources) == 2
    assert all(tuple(image.shape) == (1, 16, 16, 4) for image in images)
    assert [tuple(source.shape) for source in sources] == [(1, 2, 4, 4), (1, 1, 2, 4)]
    assert layout['schema'] == 'lf.image-layers.v1'
    assert [row['id'] for row in layout['layers']] == ['lower', 'upper']
    assert layout['layers'][0]['content_rect'] == [0, 4, 16, 8]
    assert config == {'image_entries': [
        {'id': 'lower', 'label': 'Lower cloth'},
        {'id': 'upper', 'label': 'Upper cloth'},
    ]}
    assert reads == [(root / 'first.png').resolve(), (root / 'nested/second.png').resolve()]
    assert all(source.shape[-1] == 4 for source in sources)


def test_no_edit_matches_existing_pillow_native_resize_and_alpha_composite_exactly(tmp_path):
    root, manifest = fixture(tmp_path, overlap=True)
    source_hashes = {path: digest(path) for path in (root / 'first.png', root / 'nested/second.png')}
    base_pil, base = base_image()
    canvases, layout, _, sources = load_image_layers(manifest, 16)
    before = [source.clone() for source in sources]
    atlas, restored = compose_image_layers(base, canvases, canvases, sources, layout)
    expected = pillow_reference(base_pil, manifest)
    assert tensor_bytes(atlas) == expected.tobytes()
    assert [tensor_bytes(layer) for layer in restored] == [tensor_bytes(layer) for layer in sources]
    assert all(torch.equal(actual, original) for actual, original in zip(sources, before))
    assert {path: digest(path) for path in source_hashes} == source_hashes


@pytest.mark.parametrize('edited_channels', [3, 4])
def test_rgb_or_rgba_edits_restore_native_layers_preserving_alpha_and_padding(tmp_path, edited_channels):
    _, manifest = fixture(tmp_path)
    _, base = base_image()
    canvases, layout, _, sources = load_image_layers(manifest, 16)
    edits = [canvas.clone() for canvas in canvases]
    edits[0][:, :4, :, :3] = 1  # Transparent square padding must not become an edit.
    edits[0][:, 5:11, 4:12, 0] = 1 - edits[0][:, 5:11, 4:12, 0]
    if edited_channels == 3:
        edits[0] = edits[0][..., :3]
    else:
        edits[0][..., 3] = 0  # Editor alpha changes are deliberately ignored.

    atlas, restored = compose_image_layers(base, edits, canvases, sources, layout)
    assert atlas.shape[-1] == 4
    assert not torch.equal(restored[0][..., :3], sources[0][..., :3])
    assert torch.equal(restored[0][..., 3], sources[0][..., 3])
    assert torch.equal(restored[1], sources[1])


def test_editing_invisible_lower_rgb_keeps_opaque_upper_layer_visible(tmp_path):
    root, manifest = fixture(tmp_path, overlap=True)
    Image.new('RGBA', (2, 1), (200, 180, 160, 255)).save(root / 'nested/second.png')
    manifest['layers'][1]['sha256'] = digest(root / 'nested/second.png')
    _, base = base_image()
    canvases, layout, _, sources = load_image_layers(manifest, 16)
    edits = [canvas.clone() for canvas in canvases]
    edits[0][..., :3] = torch.tensor([0.0, 1.0, 0.0])
    atlas, restored = compose_image_layers(base, edits, canvases, sources, layout)
    expected_upper = torch.tensor([200, 180, 160, 255], dtype=torch.uint8)
    actual = atlas[0, 2:4, 1:5].mul(255).round().to(torch.uint8)
    assert torch.all(actual == expected_upper)
    assert not torch.equal(restored[0][..., :3], sources[0][..., :3])
    assert torch.equal(restored[0][..., 3], sources[0][..., 3])


def test_png_transport_noise_is_not_promoted_to_an_edit(tmp_path):
    _, manifest = fixture(tmp_path)
    base_pil, base = base_image()
    canvases, layout, _, sources = load_image_layers(manifest, 16)
    edits = [(canvas + .001).clamp(0, 1) for canvas in canvases]
    atlas, restored = compose_image_layers(base, edits, canvases, sources, layout)
    assert tensor_bytes(atlas) == pillow_reference(base_pil, manifest).tobytes()
    assert all(torch.equal(actual, original) for actual, original in zip(restored, sources))


@pytest.mark.parametrize('relative,message', [
    ('../outside.png', 'inside manifest root'),
    ('', 'non-empty relative'),
])
def test_layer_paths_must_be_nonempty_relative_and_contained(tmp_path, relative, message):
    _, manifest = fixture(tmp_path)
    (tmp_path / 'outside.png').write_bytes(b'outside')
    manifest['layers'][0]['file'] = relative
    manifest['layers'][0].pop('sha256', None)
    with pytest.raises(ValueError, match=message):
        load_image_layers(manifest, 16)


def test_absolute_layer_path_and_sha_mismatch_fail(tmp_path):
    root, manifest = fixture(tmp_path)
    manifest['layers'][0]['file'] = str((root / 'first.png').resolve())
    with pytest.raises(ValueError, match='relative'):
        load_image_layers(manifest, 16)
    manifest['layers'][0]['file'] = 'first.png'
    manifest['layers'][0]['sha256'] = '0' * 64
    with pytest.raises(ValueError, match='does not match'):
        load_image_layers(manifest, 16)


@pytest.mark.parametrize('mutation,message', [
    (lambda manifest: manifest.update(layers=[]), 'non-empty'),
    (lambda manifest: manifest['layers'][1].update(id='lower'), 'unique'),
    (lambda manifest: manifest['layers'][0].update(label=''), 'label'),
    (lambda manifest: manifest['layers'][0].update(rect=[0, 0, 0, 2]), 'positive'),
    (lambda manifest: manifest['layers'][0].update(rect=[0, 0, 3, 2]), 'aspect'),
    (lambda manifest: manifest['layers'][0].update(sha256='bad'), '64 hexadecimal'),
])
def test_invalid_manifest_contracts_fail_before_editing(tmp_path, mutation, message):
    _, manifest = fixture(tmp_path)
    mutation(manifest)
    with pytest.raises(ValueError, match=message):
        load_image_layers(manifest, 16)


@pytest.mark.parametrize('edit_count,baseline_count,source_count', [
    (1, 2, 2), (2, 1, 2), (2, 2, 1), (3, 2, 2),
])
def test_compose_requires_exact_cardinality_without_broadcast(
        tmp_path, edit_count, baseline_count, source_count):
    _, manifest = fixture(tmp_path)
    _, base = base_image()
    canvases, layout, _, sources = load_image_layers(manifest, 16)
    expanded_canvases = canvases + canvases
    expanded_sources = sources + sources
    with pytest.raises(ValueError, match='cardinality'):
        compose_image_layers(
            base, expanded_canvases[:edit_count], expanded_canvases[:baseline_count],
            expanded_sources[:source_count], layout)


def test_compose_rejects_wrong_baseline_source_layout_and_base_bounds(tmp_path):
    _, manifest = fixture(tmp_path)
    _, base = base_image()
    canvases, layout, _, sources = load_image_layers(manifest, 16)
    with pytest.raises(ValueError, match='order/source'):
        compose_image_layers(base, canvases, list(reversed(canvases)), sources, layout)
    wrong_sources = [source.clone() for source in sources]
    wrong_sources[0][0, 0, 0, 0] = 1 - wrong_sources[0][0, 0, 0, 0]
    with pytest.raises(ValueError, match='order/source'):
        compose_image_layers(base, canvases, canvases, wrong_sources, layout)
    bad = deepcopy(layout)
    bad['layers'][0]['content_rect'][0] += 1
    with pytest.raises(ValueError, match='content_rect'):
        compose_image_layers(base, canvases, canvases, sources, bad)
    bad = deepcopy(layout)
    bad['layers'][0]['rect'] = [7, 7, 4, 2]
    with pytest.raises(ValueError, match='bounds'):
        compose_image_layers(base, canvases, canvases, sources, bad)


def test_headless_nodes_accept_list_wrapped_controls_and_publish_list_metadata(tmp_path):
    _, manifest = fixture(tmp_path)
    _, base = base_image()
    batch, images, layout, config, sources = LF_LoadImageLayers().on_exec(
        [json.dumps(manifest)], [16])
    assert tuple(batch.shape) == (2, 16, 16, 4)
    assert len(images) == len(sources) == 2
    assert config['image_entries'][0]['id'] == 'lower'
    atlas, atlas_list, layers = LF_ComposeImageLayers().on_exec(
        [base], [batch], images, sources, [layout])
    assert tuple(atlas.shape) == (1, 8, 8, 4)
    assert len(atlas_list) == 1 and torch.equal(atlas_list[0], atlas)
    assert len(layers) == 2
    assert LF_LoadImageLayers.RETURN_NAMES == (
        'images', 'image_list', 'layout', 'editor_config', 'source_layers')
    assert LF_LoadImageLayers.OUTPUT_IS_LIST == (False, True, False, False, True)
    assert LF_ComposeImageLayers.RETURN_NAMES == ('atlas', 'atlas_list', 'layer_images')
    assert LF_ComposeImageLayers.OUTPUT_IS_LIST == (False, True, True)
    assert LF_LoadImageLayers.INPUT_IS_LIST is True
    assert LF_ComposeImageLayers.INPUT_IS_LIST is True


def test_published_schema_is_unchanged_except_additive_optional_inputs():
    loader = LF_LoadImageLayers.INPUT_TYPES()
    assert loader['required'] == {
        'manifest': (Input.JSON, {'tooltip': 'Object with root and ordered layers: [{id,label,file,sha256?,rect:[x,y,width,height]}].'}),
        'canvas_size': (Input.INTEGER, {'default': 512, 'min': 1, 'max': 4096,
            'tooltip': 'Square RGBA editing canvas; each native layer fits without stretching.'}),
    }
    assert list(loader['optional']) == ['include_masks', 'base', 'base_regions']
    assert loader['optional']['include_masks'][0] == Input.BOOLEAN
    assert loader['optional']['include_masks'][1]['default'] is False
    assert loader['optional']['base'][0] == Input.IMAGE
    assert loader['optional']['base_regions'][0] == Input.JSON
    composer = LF_ComposeImageLayers.INPUT_TYPES()
    assert composer['required'] == {
        'base': (Input.IMAGE, {'tooltip': 'Exactly one RGB/RGBA base atlas.'}),
        'edited': (Input.IMAGE, {'tooltip': 'Edited canvases in validated original entry order.'}),
        'original_layers': (Input.IMAGE, {'tooltip': 'Breakpoint orig_image_list, in the same order; required for local edit deltas.'}),
        'source_layers': (Input.IMAGE, {'tooltip': 'Native RGBA source_layers returned by Load Image Layers.'}),
        'layout': (Input.JSON, {'tooltip': 'Layout returned by Load Image Layers.'}),
    }
    assert list(composer['optional']) == ['base_mask']
    assert composer['optional']['base_mask'][0] == Input.MASK
    assert LF_LoadImageLayers.RETURN_TYPES == (Input.IMAGE, Input.IMAGE, Input.JSON, Input.JSON, Input.IMAGE)
    assert LF_ComposeImageLayers.RETURN_TYPES == (Input.IMAGE, Input.IMAGE, Input.IMAGE)


def combined_fixture(tmp_path, *, include_masks=True):
    root, manifest = fixture(tmp_path, overlap=True)
    _, base = base_image()
    regions = {'regions': [{'id': 'body', 'label': 'Body', 'rect': [1, 2, 4, 2]}]}
    result = LF_LoadImageLayers().on_exec(
        [manifest], [16], [include_masks], [base], [regions])
    return root, manifest, base, result


@pytest.mark.parametrize('include_masks', [False, True])
def test_combined_noop_and_white_masks_match_baseline_and_preserve_sources(tmp_path, include_masks):
    root, manifest, base, (batch, canvases, layout, config, sources) = combined_fixture(
        tmp_path, include_masks=include_masks)
    count = 5 if include_masks else 3
    assert batch.shape == (count, 16, 16, 4)
    assert len(sources) == 2
    ids = ['base:body', 'layer:lower', 'mask:lower', 'layer:upper', 'mask:upper'] if include_masks else [
        'base:body', 'layer:lower', 'layer:upper']
    assert [row['id'] for row in config['image_entries']] == ids
    source_before = [source.clone() for source in sources]
    hashes = {path: digest(path) for path in root.rglob('*.png')}
    base_pil, _ = base_image()
    for transport in ('exact', 'png', 'white'):
        edits = [canvas.clone() for canvas in canvases]
        baselines = [canvas.clone() for canvas in canvases]
        if transport == 'png':
            edits = [canvas.mul(255).round().div(255) for canvas in edits]
            baselines = [canvas.mul(255).round().div(255) for canvas in baselines]
        if transport == 'white' and include_masks:
            for index in (2, 4):
                edits[index][..., :3] = 1
                edits[index][..., 3] = 0  # Editor alpha does not control retention.
        atlas, layers = compose_image_layers(base, edits, baselines, sources, layout)
        assert tensor_bytes(atlas) == pillow_reference(base_pil, manifest).tobytes()
        assert all(torch.equal(actual, original) for actual, original in zip(layers, sources))
    assert all(torch.equal(actual, original) for actual, original in zip(sources, source_before))
    assert {path: digest(path) for path in hashes} == hashes


def test_black_cut_masks_reveal_edited_base_and_lower_layer_and_white_restores(tmp_path):
    _, _, base, (_, canvases, layout, _, sources) = combined_fixture(tmp_path)
    edits = [canvas.clone() for canvas in canvases]
    edits[0][..., :3] = torch.tensor([1., 0., 0.])
    edits[4][..., :3] = 0
    atlas, layers = compose_image_layers(base, edits, canvases, sources, layout)
    assert torch.count_nonzero(layers[1][..., 3]) == 0
    assert torch.equal(layers[0], sources[0])
    expected = Image.new('RGBA', (8, 8), (11, 22, 33, 255))
    expected.paste((255, 0, 0, 255), (1, 2, 5, 4))
    lower = Image.frombytes('RGBA', (4, 2), tensor_bytes(sources[0]))
    expected.alpha_composite(lower, (1, 2))
    assert tensor_bytes(atlas) == expected.tobytes()
    edits[2][..., :3] = 0
    atlas, layers = compose_image_layers(base, edits, canvases, sources, layout)
    assert torch.all(atlas[0, 2:4, 1:5] == torch.tensor([1., 0., 0., 1.]))
    for index in (2, 4):
        edits[index][..., :3] = 1
    _, restored = compose_image_layers(base, edits, canvases, sources, layout)
    assert all(torch.equal(actual, source) for actual, source in zip(restored, sources))


def test_gray_masks_multiply_native_alpha_and_ignore_padding(tmp_path):
    _, manifest = fixture(tmp_path)
    _, base = base_image()
    canvases, layout, _, sources = load_image_layers(manifest, 16, include_masks=True)
    edits = [canvas.clone() for canvas in canvases]
    edits[1][:, 4:12, :, :3] = .5
    edits[3][:, :4, :, :3] = 1  # Padding cannot add coverage.
    edits[3][:, 12:, :, :3] = 1
    atlas, layers = compose_image_layers(base, edits, canvases, sources, layout)
    assert torch.allclose(layers[0][..., 3], sources[0][..., 3] * .5, atol=1e-7, rtol=0)
    assert torch.equal(layers[0][..., :3], sources[0][..., :3])
    assert torch.equal(layers[1], sources[1])
    assert torch.all(atlas[..., 3] == 1)


def test_uv_mask_protects_base_edits_and_preserves_original_alpha(tmp_path):
    _, _, base, (_, canvases, layout, _, sources) = combined_fixture(tmp_path)
    edits = [canvas.clone() for canvas in canvases]
    edits[0][..., :3] = 1
    edits[2][..., :3] = edits[4][..., :3] = 0
    mask = torch.zeros((1, 8, 8))
    mask[:, 2:4, 1:3] = 1
    atlas, _, _ = LF_ComposeImageLayers().on_exec(
        [base], edits, canvases, sources, [layout], [mask])
    assert torch.all(atlas[:, 2:4, 1:3, :3] == 1)
    assert torch.equal(atlas[:, 2:4, 3:5, :3], base[:, 2:4, 3:5])
    assert torch.all(atlas[..., 3] == 1)


@pytest.mark.parametrize('bad_input', ['count', 'source_count', 'order', 'mask_baseline', 'base', 'layout_order'])
def test_combined_rejects_misaligned_baselines_and_layout(tmp_path, bad_input):
    _, _, base, (_, canvases, layout, _, sources) = combined_fixture(tmp_path)
    edits = [canvas.clone() for canvas in canvases]
    baselines = [canvas.clone() for canvas in canvases]
    message = 'cardinality'
    if bad_input == 'count':
        edits.pop()
    elif bad_input == 'source_count':
        sources.pop()
    elif bad_input == 'order':
        baselines[1], baselines[3] = baselines[3], baselines[1]
        message = 'order/source'
    elif bad_input == 'mask_baseline':
        baselines[2][..., :3] = 0
        message = 'order/source'
    elif bad_input == 'base':
        base = base.clone()
        base[..., 0] = 1
        message = 'extraction source'
    else:
        layout['editor_entries'].reverse()
        message = 'extraction order'
    with pytest.raises(ValueError, match=message):
        compose_image_layers(base, edits, baselines, sources, layout)


def test_optional_inputs_fail_clearly_when_incomplete(tmp_path):
    _, manifest = fixture(tmp_path)
    _, base = base_image()
    with pytest.raises(ValueError, match='supplied together'):
        load_image_layers(manifest, 16, base=base)
    canvases, layout, _, sources = load_image_layers(manifest, 16)
    assert set(layout) == {'schema', 'canvas_size', 'layers'}
    with pytest.raises(ValueError, match='editable base regions'):
        compose_image_layers(base, canvases, canvases, sources, layout, torch.ones((1, 8, 8)))


def test_cut_masks_cannot_expand_transparent_source_and_base_alpha_is_retained(tmp_path):
    root, manifest = fixture(tmp_path)
    Image.new('RGBA', (4, 2), (200, 100, 50, 0)).save(root / 'first.png')
    manifest['layers'] = [manifest['layers'][0]]
    manifest['layers'][0]['sha256'] = digest(root / 'first.png')
    base = pil_to_tensor(Image.new('RGBA', (8, 8), (11, 22, 33, 123)))
    before = base.clone()
    regions = {'regions': [{'id': 'panel', 'label': 'Panel', 'rect': [1, 2, 4, 2]}]}
    canvases, layout, _, sources = load_image_layers(manifest, 16, True, base, regions)
    edits = [canvas.clone() for canvas in canvases]
    edits[0][..., :3] = 1
    edits[0][..., 3] = 0
    edits[2][...] = 1
    atlas, layers = compose_image_layers(base, edits, canvases, sources, layout)
    assert torch.count_nonzero(layers[0][..., 3]) == 0
    assert torch.equal(atlas[..., 3], base[..., 3])
    assert torch.equal(base, before)
    assert torch.equal(atlas[:, :2], base[:, :2])


@pytest.mark.parametrize('mask,message', [
    (torch.ones((2, 8, 8)), 'count mismatch'),
    (torch.ones((1, 4, 4)), 'dimensions'),
    (torch.full((1, 8, 8), float('nan')), 'finite'),
])
def test_base_mask_requires_one_matching_finite_mask(tmp_path, mask, message):
    _, _, base, (_, canvases, layout, _, sources) = combined_fixture(tmp_path)
    with pytest.raises(ValueError, match=message):
        compose_image_layers(base, canvases, canvases, sources, layout, mask)
