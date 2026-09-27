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
