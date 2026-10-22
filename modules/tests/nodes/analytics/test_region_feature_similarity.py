"""Deterministic CPU features; no model weights or Comfy GPU imports.

Core Output is an attribute bag in comfy/clip_vision.py, whose module imports
the GPU stack. SimpleNamespace carries exactly the fields read here:
last_hidden_state, image_sizes, image_embeds.
"""
from types import SimpleNamespace

import pytest
import torch

from modules.nodes.analytics.region_feature_similarity import LF_RegionFeatureSimilarity
from modules.nodes.regions.text_region_masks import LF_TextRegionMasks
from modules.utils.helpers.torch.region_feature_similarity import pool_region_patches


def _regions(masks=None):
    if masks is None:
        masks = torch.zeros(2, 4, 4)
        masks[0, :, :2] = 1
        masks[1, :, 2:] = 1
    table = [{'id': f'part-{i}', 'prompt': f'part {i}', 'priority': 0}
             for i in range(len(masks))]
    image = torch.zeros(1, *masks.shape[1:], 3)
    return LF_TextRegionMasks().on_exec(image, masks, table)[:2]


def _patches(values=None):
    if values is None:
        values = [[1., 0.], [0., 1.], [1., 0.], [0., 1.]]
    # Giant prefix tokens make accidental CLS/register pooling observable.
    return SimpleNamespace(
        last_hidden_state=torch.cat([torch.full((5, 2), 900.), torch.tensor(values)]).unsqueeze(0),
        image_sizes=[torch.Size([3, 32, 32])], image_embeds=torch.tensor([[900., 900.]]))


def _compare(a=None, b=None, masks=None, metadata=None, **kwargs):
    if masks is None:
        masks, metadata = _regions()
    return LF_RegionFeatureSimilarity().on_exec(
        features_a=_patches() if a is None else a,
        features_b=_patches() if b is None else b,
        masks=masks, metadata=metadata, **kwargs)[0]


def test_identical_outputs_give_one_and_name_actual_method():
    masks, metadata = _regions()
    result = _compare(a=[_patches()], b=[_patches()], masks=[masks], metadata=[metadata],
                      model_file=['dino_v3_vit_h.safetensors'], crop=['none'])
    assert result['schema'] == 'lf.region-feature-similarity.v1'
    assert result['model_file'] == 'dino_v3_vit_h.safetensors'
    assert result['model_file_source'] == 'workflow_input'
    assert result['method'] == 'coverage_weighted_patch_mean_cosine'
    assert result['patch_grid'] == [2, 2]
    assert result['prefix_tokens'] == 5
    assert [row['similarity'] for row in result['regions']] == pytest.approx([1., 1.])


def test_changed_region_lowers_only_its_score_and_prefix_tokens_are_ignored():
    b = _patches([[0., 1.], [0., 1.], [0., 1.], [0., 1.]])
    b.last_hidden_state[:, :5] = -900.
    result = _compare(b=b)
    assert [row['similarity'] for row in result['regions']] == pytest.approx([0., 1.])


def test_pooling_weights_fractional_patch_coverage_before_cosine():
    masks = torch.zeros(1, 4, 4)
    masks[0, 0, 0] = 1  # quarter of the top-left patch
    masks[0, :2, 2:] = 1  # all of the top-right patch
    features = torch.tensor([[1., 0.], [0., 1.], [10., 10.], [10., 10.]], dtype=torch.float64)
    means, weights = pool_region_patches(features, masks, (2, 2), (32, 32), 'none')
    torch.testing.assert_close(means, torch.tensor([[.2, .8]], dtype=torch.float64))
    assert weights.tolist() == [1.25]
    resolved, metadata = _regions(masks)
    b = _patches([[0., 1.]] * 4)
    result = _compare(b=b, masks=resolved, metadata=metadata)
    assert result['regions'][0]['similarity'] == pytest.approx(.8 / (.2**2 + .8**2)**.5)


def test_center_crop_uses_core_resize_then_floor_center_geometry():
    masks = torch.zeros(1, 4, 8)
    masks[:, :, :2] = 1  # outside the square centre crop
    features = torch.ones(4, 2, dtype=torch.float64)
    _, total_none = pool_region_patches(features, masks, (2, 2), (32, 32), 'none')
    _, total_center = pool_region_patches(features, masks, (2, 2), (32, 32), 'center')
    assert total_none.item() == 1
    assert total_center.item() == 0
    resolved, metadata = _regions(masks)
    result = _compare(masks=resolved, metadata=metadata, crop='center')
    assert result['regions'][0]['similarity'] is None
    assert result['regions'][0]['empty'] is False
    assert 'after center preprocessing' in result['regions'][0]['warning']


def test_two_independent_mask_sets_pool_independently():
    masks_a, meta_a = _regions()
    masks_b, meta_b = _regions(masks_a.flip(0))
    result = _compare(masks=[masks_a, masks_b], metadata=[meta_a, meta_b])
    assert result['mask_sets'] == 2
    assert [row['similarity'] for row in result['regions']] == pytest.approx([0., 0.])


def test_empty_region_keeps_null_score_and_loud_warning(caplog):
    masks, metadata = _regions(torch.zeros(1, 4, 4))
    result = _compare(masks=masks, metadata=metadata)
    assert result['regions'][0]['empty'] is True
    assert result['regions'][0]['similarity'] is None
    assert 'no mask coverage' in caplog.text


def test_pooled_only_requires_one_crop_per_region_and_reports_method():
    a = SimpleNamespace(last_hidden_state=None, image_embeds=torch.tensor([[1., 0.], [0., 1.]]))
    b = [SimpleNamespace(image_embeds=torch.tensor([[1., 0.]])),
         SimpleNamespace(image_embeds=torch.tensor([[1., 0.]]))]
    result = _compare(a=a, b=b)
    assert result['method'] == 'per_region_crop_pooled_cosine'
    assert [row['similarity'] for row in result['regions']] == pytest.approx([1., 0.])
    with pytest.raises(ValueError, match='exactly one encoded crop per region'):
        _compare(a=b[0], b=b)


@pytest.mark.parametrize('change,message', [
    (lambda x: setattr(x, 'last_hidden_state', torch.ones(1, 4, 2)), 'CLS and four register'),
    (lambda x: setattr(x, 'last_hidden_state', torch.ones(2, 9, 2)), 'exactly one full image'),
    (lambda x: setattr(x, 'last_hidden_state', torch.full((1, 9, 2), float('nan'))), 'finite'),
    (lambda x: setattr(x, 'image_sizes', None), 'image_sizes'),
    (lambda x: setattr(x, 'image_sizes', [(3, 30, 32)]), 'square DINOv3'),
    (lambda x: setattr(x, 'last_hidden_state', torch.zeros(1, 9, 2)), 'zero-norm'),
])
def test_invalid_patch_outputs_fail_with_reason(change, message):
    output = _patches()
    change(output)
    with pytest.raises(ValueError, match=message):
        _compare(b=output)


def test_no_missing_or_mixed_feature_fallback():
    masks, metadata = _regions()
    node = LF_RegionFeatureSimilarity()
    with pytest.raises(ValueError, match='features_a requires'):
        node.on_exec(features_b=_patches(), masks=masks, metadata=metadata)
    with pytest.raises(ValueError, match='both carry'):
        _compare(b=SimpleNamespace(image_embeds=torch.ones(2, 2)))
    with pytest.raises(ValueError, match='model_file'):
        _compare(model_file='')
    with pytest.raises(ValueError, match='crop must match'):
        _compare(crop='unknown')


def test_metadata_and_feature_shape_mismatches_fail():
    masks, metadata = _regions()
    with pytest.raises(ValueError, match='Mask count'):
        _compare(masks=masks[:1], metadata=metadata)
    b = _patches()
    b.last_hidden_state = torch.ones(1, 9, 3)
    with pytest.raises(ValueError, match='feature dimensions'):
        _compare(b=b)


def test_public_contract():
    node = LF_RegionFeatureSimilarity
    required = node.INPUT_TYPES()['required']
    assert required['features_a'][0] == required['features_b'][0] == 'CLIP_VISION_OUTPUT'
    assert node.INPUT_IS_LIST is True
    assert node.RETURN_TYPES == ('JSON',)
    assert node.RETURN_NAMES == ('similarity',)
    assert node.OUTPUT_IS_LIST == (False,)
