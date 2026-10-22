"""Coverage-weighted DINOv3 patch comparison of already encoded images."""
import logging

import torch
import torch.nn.functional as F

from ..detection.region_masks import region_mask_sets
from ...image_regions import single_value


def _vision_outputs(value, name):
    # Core list mode wraps the output objects; a batch lives inside each object.
    values = list(value) if isinstance(value, (list, tuple)) else [value]
    if not values or any(item is None for item in values):
        raise ValueError(f'{name} requires CLIP_VISION_OUTPUT from CLIPVisionEncode.')
    return values


def _feature_tensor(value, name, ndim):
    if (not isinstance(value, torch.Tensor) or value.ndim != ndim
            or any(size < 1 for size in value.shape)
            or not value.is_floating_point() or not torch.isfinite(value).all()):
        raise ValueError(f'{name} must be a finite floating-point {ndim}D feature tensor.')
    return value.detach().to(device='cpu', dtype=torch.float64)


def _patch_features(output, name):
    features = _feature_tensor(getattr(output, 'last_hidden_state', None),
                               f'{name}.last_hidden_state', 3)
    if features.shape[0] != 1:
        raise ValueError(f'{name}.last_hidden_state must encode exactly one full image.')
    sizes = getattr(output, 'image_sizes', None)
    if (not isinstance(sizes, (list, tuple)) or len(sizes) != 1
            or not isinstance(sizes[0], (list, tuple, torch.Size)) or len(sizes[0]) != 3):
        raise ValueError(f'{name}.image_sizes must contain one encoded [C,H,W] size.')
    channels, height, width = sizes[0]
    if (any(type(size) is not int or size <= 0 for size in sizes[0]) or channels != 3
            or height != width or height % 16 or width % 16):
        raise ValueError(f'{name}.image_sizes must describe the square DINOv3 /16 input.')
    grid = (height // 16, width // 16)
    # Core DINOv3 orders CLS, four register tokens, then row-major patches.
    if features.shape[1] != 5 + grid[0] * grid[1]:
        raise ValueError(f'{name}.last_hidden_state does not match the DINOv3 patch grid '
                         'plus CLS and four register tokens.')
    return features[0, 5:], grid, (height, width)


def pool_region_patches(features, masks, grid, encoded_size, crop):
    """Return region means and coverage sums, excluding all prefix tokens.

    Geometry follows Core clip_preprocess: stretch for ``none``; resize the
    shorter side then floor-centre crop for ``center``. Area resampling keeps
    fractional coverage rather than selecting patches at their centres.
    """
    coverage = masks.to(dtype=torch.float64).unsqueeze(1)
    if crop == 'center':
        height, width = coverage.shape[-2:]
        size = encoded_size[0]
        scale = size / min(height, width)
        scaled = (round(scale * height), round(scale * width))
        coverage = F.interpolate(coverage, size=scaled, mode='area')
        top, left = (scaled[0] - size) // 2, (scaled[1] - size) // 2
        coverage = coverage[:, :, top:top + size, left:left + size]
    elif crop != 'none':
        raise ValueError("crop must match CLIPVisionEncode: 'center' or 'none'.")
    weights = F.interpolate(coverage, size=grid, mode='area').flatten(1)
    totals = weights.sum(dim=1)
    means = weights @ features / totals.clamp_min(torch.finfo(torch.float64).tiny)[:, None]
    return means, totals


def _pooled_features(outputs, count, name):
    embeddings = [_feature_tensor(getattr(output, 'image_embeds', None),
                                  f'{name}.image_embeds', 2) for output in outputs]
    if len({item.shape[1] for item in embeddings}) != 1:
        raise ValueError(f'{name}.image_embeds feature dimensions must match.')
    result = torch.cat(embeddings, dim=0)
    if result.shape[0] != count:
        raise ValueError(f'{name} pooled-only output requires exactly one encoded crop '
                         'per region, in metadata order; no full-image broadcast.')
    return result


def compare_region_features(features_a, features_b, masks, region_metadata,
                            model_file, crop):
    """Compare two full-image patch outputs or two ordered sets of pooled crops."""
    sets, metadata = region_mask_sets(masks, region_metadata)
    if sets.shape[0] not in (1, 2):
        raise ValueError('Region feature comparison requires one shared mask set or two A/B sets.')
    model_file = single_value(model_file, 'model_file')
    if not isinstance(model_file, str) or not model_file.strip():
        raise ValueError('model_file must name the file selected in CLIPVisionLoader.')
    crop = single_value(crop, 'crop')
    if crop not in ('center', 'none'):
        raise ValueError("crop must match CLIPVisionEncode: 'center' or 'none'.")
    outputs_a = _vision_outputs(features_a, 'features_a')
    outputs_b = _vision_outputs(features_b, 'features_b')
    has_patches = [getattr(output, 'last_hidden_state', None) is not None
                   for output in outputs_a + outputs_b]
    mask_a, mask_b = sets[0], sets[-1]
    if all(has_patches):
        if len(outputs_a) != 1 or len(outputs_b) != 1:
            raise ValueError('Patch comparison needs exactly one full-image output for A and B.')
        patches_a, grid_a, size_a = _patch_features(outputs_a[0], 'features_a')
        patches_b, grid_b, size_b = _patch_features(outputs_b[0], 'features_b')
        if grid_a != grid_b or patches_a.shape[1] != patches_b.shape[1]:
            raise ValueError('features_a and features_b must have matching patch grids and feature dimensions.')
        means_a, coverage_a = pool_region_patches(patches_a, mask_a, grid_a, size_a, crop)
        means_b, coverage_b = pool_region_patches(patches_b, mask_b, grid_b, size_b, crop)
        method = 'coverage_weighted_patch_mean_cosine'
        geometry = {'patch_grid': list(grid_a), 'patch_size': 16, 'prefix_tokens': 5,
                    'crop': crop, 'mask_resampling': 'area'}
    elif any(has_patches):
        raise ValueError('features_a and features_b must both carry patch tokens or both carry pooled-only crops.')
    else:
        means_a = _pooled_features(outputs_a, len(metadata['regions']), 'features_a')
        means_b = _pooled_features(outputs_b, len(metadata['regions']), 'features_b')
        if means_a.shape != means_b.shape:
            raise ValueError('features_a and features_b pooled feature dimensions must match.')
        coverage_a, coverage_b = mask_a.sum((1, 2)), mask_b.sum((1, 2))
        method = 'per_region_crop_pooled_cosine'
        geometry = {'crop': crop, 'crop_order': 'region_table',
                    'note': 'Workflow supplies one independently encoded crop per region and image.'}

    rows = []
    for index, region in enumerate(metadata['regions']):
        row = {'id': region['id'], 'area_a': int(mask_a[index].sum(dtype=torch.int64)),
               'area_b': int(mask_b[index].sum(dtype=torch.int64)), 'similarity': None}
        row['empty'] = row['area_a'] == 0 or row['area_b'] == 0
        if coverage_a[index] == 0 or coverage_b[index] == 0:
            warning = f"Region '{region['id']}' has no mask coverage in A or B after {crop} preprocessing."
            row['warning'] = warning
            logging.warning(warning)
        else:
            norm_a, norm_b = means_a[index].norm(), means_b[index].norm()
            if norm_a == 0 or norm_b == 0:
                raise ValueError(f"Region '{region['id']}' has a zero-norm mean feature in A or B.")
            similarity = torch.dot(means_a[index] / norm_a, means_b[index] / norm_b)
            row['similarity'] = float(similarity.clamp(-1, 1))
        rows.append(row)
    return {'schema': 'lf.region-feature-similarity.v1', 'model_file': model_file,
            'model_file_source': 'workflow_input', 'method': method, **geometry,
            'mask_sets': int(sets.shape[0]), 'regions': rows}
