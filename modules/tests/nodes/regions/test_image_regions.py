"""Pixel-preserving region editing without editor/server/GPU dependencies."""
from copy import deepcopy
import json

import pytest
import torch

from modules.utils.image_regions import extract_image_regions, compose_image_regions
from modules.nodes.regions.image_regions import LF_ExtractImageRegions, LF_ComposeImageRegions


def source(channels=3, dtype=torch.float32):
    return torch.rand((1, 24, 40, channels), generator=torch.Generator().manual_seed(8), dtype=dtype)


def regions():
    return {'regions': [{'id': f'part-{i}', 'label': f'Part {i}', 'rect': [i*4, 0, 4, i+2]}
                        for i in range(8)]}


def quantize(image):
    return torch.floor(image * 255) / 255


@pytest.mark.parametrize('channels', [3, 4])
@pytest.mark.parametrize('size', [4, 16, 32])
@pytest.mark.parametrize('dtype', [torch.float32, torch.float64])
def test_no_edit_roundtrip_is_exact_despite_resizing_and_png_quantization(channels, size, dtype):
    original = source(channels, dtype)
    before = original.clone()
    images, layout, config = extract_image_regions(original, regions(), size)
    assert all(tuple(image.shape) == (1, size, size, channels) for image in images)
    assert all(image.dtype == torch.float32 for image in images)
    assert config == {'image_entries': [{'id': f'part-{i}', 'label': f'Part {i}'} for i in range(8)]}
    result = compose_image_regions(original, [quantize(i) for i in images], images, layout)
    assert torch.equal(result, original)
    assert result.data_ptr() != original.data_ptr()
    assert torch.equal(original, before)
    assert result.dtype == dtype


@pytest.mark.parametrize('channels', [3, 4])
def test_one_edited_region_preserves_seven_others_and_uncovered_pixels(channels):
    original = source(channels)
    images, layout, _ = extract_image_regions(original, regions(), 32)
    baselines = [quantize(i) for i in images]
    edits = [i.clone() for i in baselines]
    edits[3][..., :3] = 1 - edits[3][..., :3]
    result = compose_image_regions(original, edits, baselines, layout)
    x, y, w, h = layout['regions'][3]['rect']
    protected = torch.ones(original.shape[1:3], dtype=torch.bool)
    protected[y:y+h, x:x+w] = False
    assert torch.equal(result[:, protected], original[:, protected])
    assert not torch.equal(result[:, y:y+h, x:x+w, :3], original[:, y:y+h, x:x+w, :3])
    if channels == 4:
        assert torch.equal(result[..., 3], original[..., 3])


def test_internal_unpainted_pixels_and_channels_remain_exact():
    original = source(4, torch.float64)
    definition = {'regions': [{'id': 'detail', 'label': 'Detail', 'rect': [7, 5, 8, 8]}]}
    images, layout, _ = extract_image_regions(original, definition, 8)
    edits = [quantize(images[0])]
    edits[0][0, 3, 4, 0] = 0 if images[0][0, 3, 4, 0] > .5 else 1
    edits[0][..., 3] = 0  # Alpha edits must never leak into source alpha.
    result = compose_image_regions(original, edits, images, layout)
    changed = result != original
    assert changed.sum().item() == 1
    assert changed[0, 8, 11, 0]
    assert torch.equal(result[..., 3], original[..., 3])


@pytest.mark.parametrize('canvas', [4, 24])
def test_resized_local_edit_has_bounded_footprint_and_preserves_unpainted_interior(canvas):
    original = torch.full((1, 32, 32, 3), .25)
    definition = {'regions': [{'id': 'center', 'label': 'Center', 'rect': [8, 8, 16, 16]}]}
    images, layout, _ = extract_image_regions(original, definition, canvas)
    edits = [images[0].clone()]
    edits[0][:, canvas//2:canvas//2+1, canvas//2:canvas//2+1, 0] = .75
    result = compose_image_regions(original, edits, images, layout)
    assert not torch.equal(result, original)
    assert torch.equal(result[:, :8], original[:, :8])
    assert torch.equal(result[:, 24:], original[:, 24:])
    assert torch.equal(result[:, :, :8], original[:, :, :8])
    assert torch.equal(result[:, :, 24:], original[:, :, 24:])
    assert torch.equal(result[:, 8:10, 8:10], original[:, 8:10, 8:10])
    assert torch.equal(result[..., 1:], original[..., 1:])


def test_aspect_fit_edge_padding_is_unlabelled_and_padding_edits_ignored():
    original = torch.zeros(1, 4, 8, 3)
    original[..., 0] = .25
    original[..., 1] = .5
    original[..., 2] = .75
    images, layout, _ = extract_image_regions(original,
        {'regions': [{'id': 'wide', 'label': 'Do not burn this label', 'rect': [0, 0, 8, 4]}]}, 8)
    assert layout['regions'][0]['content_rect'] == [0, 2, 8, 4]
    assert torch.equal(images[0], original[:, :1, :1].expand(1, 8, 8, 3))
    edited = images[0].clone()
    edited[:, :2] = 0
    edited[:, 6:] = 1
    assert torch.equal(compose_image_regions(original, edited, images, layout), original)


def test_opaque_rgba_and_white_survive_noninteger_resize_with_finite_unit_range():
    original = torch.ones(1, 7, 3, 4)
    definition = {'regions': [{'id': 'whole', 'label': 'Whole', 'rect': [0, 0, 3, 7]}]}
    images, layout, _ = extract_image_regions(original, definition, 32)
    assert images[0].min() >= 0 and images[0].max() <= 1
    result = compose_image_regions(original, [quantize(images[0])], images, layout)
    assert torch.equal(result, original)


@pytest.mark.parametrize('definition,message', [
    ({'regions': []}, 'non-empty'),
    ({'regions': [{'id': 'a', 'label': 'A', 'rect': [-1, 0, 2, 2]}]}, 'bounds'),
    ({'regions': [{'id': 'a', 'label': 'A', 'rect': [39, 0, 2, 2]}]}, 'bounds'),
    ({'regions': [{'id': 'a', 'label': 'A', 'rect': [0, 0, 0, 2]}]}, 'positive'),
    ({'regions': [{'id': 'a', 'label': 'A', 'rect': [0., 0, 2, 2]}]}, 'integer'),
    ({'regions': [{'id': '', 'label': 'A', 'rect': [0, 0, 2, 2]}]}, 'IDs'),
    ({'regions': [{'id': 'a', 'label': '', 'rect': [0, 0, 2, 2]}]}, 'label'),
    ({'regions': [{'id': 'a', 'label': 'A', 'rect': [0, 0, 2, 2]},
                  {'id': 'a', 'label': 'B', 'rect': [4, 0, 2, 2]}]}, 'unique'),
    ({'regions': [{'id': 'a', 'label': 'A', 'rect': [0, 0, 2, 2]},
                  {'id': 'b', 'label': 'B', 'rect': [1, 1, 2, 2]}]}, 'Overlapping'),
])
def test_invalid_region_definitions_fail(definition, message):
    with pytest.raises(ValueError, match=message):
        extract_image_regions(source(), definition, 16)


@pytest.mark.parametrize('count,baseline_count', [(7, 8), (8, 7), (1, 8), (8, 9)])
def test_compose_rejects_cardinality_without_broadcast(count, baseline_count):
    original = source()
    images, layout, _ = extract_image_regions(original, regions(), 16)
    with pytest.raises(ValueError, match='cardinality'):
        compose_image_regions(original, (images + images)[:count], (images + images)[:baseline_count], layout)


def test_compose_rejects_wrong_order_source_canvas_and_layout():
    original = source()
    images, layout, _ = extract_image_regions(original, regions(), 16)
    with pytest.raises(ValueError, match='order/source'):
        compose_image_regions(original, images, list(reversed(images)), layout)
    with pytest.raises(ValueError, match='order/source'):
        compose_image_regions(1-original, images, images, layout)
    wrong_shape = list(images)
    wrong_shape[0] = images[0][:, :-1]
    with pytest.raises(ValueError, match='dimensions/channels'):
        compose_image_regions(original, wrong_shape, images, layout)
    wrong_channels = list(images)
    wrong_channels[0] = torch.cat([images[0], images[0][..., :1]], dim=-1)
    with pytest.raises(ValueError, match='dimensions/channels'):
        compose_image_regions(original, wrong_channels, images, layout)
    bad_layout = deepcopy(layout)
    bad_layout['regions'][0]['content_rect'][0] += 1
    with pytest.raises(ValueError, match='content_rect'):
        compose_image_regions(original, images, images, bad_layout)
    bad_layout = deepcopy(layout)
    bad_layout['source_size'] = [1, 1]
    with pytest.raises(ValueError, match='dimensions/channels'):
        compose_image_regions(original, images, images, bad_layout)


def test_exact_single_source_and_finite_pixels_required():
    with pytest.raises(ValueError, match='exactly one image'):
        extract_image_regions(torch.cat([source(), source()]), regions(), 16)
    with pytest.raises(ValueError, match='exactly one value'):
        extract_image_regions(source(), regions(), [16, 32])
    invalid = source()
    invalid[0, 0, 0, 0] = float('nan')
    with pytest.raises(ValueError, match='finite'):
        extract_image_regions(invalid, regions(), 16)
    with pytest.raises(ValueError, match='canvas_size'):
        extract_image_regions(source(), regions(), 0)


def test_headless_nodes_accept_list_wrapped_controls_and_preserve_output_order():
    original = source()
    extracted = LF_ExtractImageRegions().on_exec([original], [json.dumps(regions())], [16])
    batch, items, layout, config = extracted
    assert tuple(batch.shape) == (8, 16, 16, 3)
    assert isinstance(items, list) and len(items) == 8
    for index in range(8):
        assert torch.equal(items[index], batch[index:index+1])
    image, image_list = LF_ComposeImageRegions().on_exec([original], [batch], items, [layout])
    assert torch.equal(image, original)
    assert len(image_list) == 1 and torch.equal(image_list[0], original)
    assert LF_ExtractImageRegions.RETURN_NAMES == ('images', 'image_list', 'layout', 'editor_config')
    assert LF_ExtractImageRegions.OUTPUT_IS_LIST == (False, True, False, False)
    assert LF_ComposeImageRegions.RETURN_NAMES == ('image', 'image_list')
    assert LF_ComposeImageRegions.OUTPUT_IS_LIST == (False, True)
    assert LF_ExtractImageRegions.INPUT_IS_LIST is True
    assert LF_ComposeImageRegions.INPUT_IS_LIST is True
