"""A linear probe on encoded patch tokens: what tells two kinds of image apart, and where a new image reads as each.

Teaching images carry a label, 0 or 1, and a group (a scene, a pair of shots of it). The probe is a class-balanced
logistic regression with an L2 penalty on standardized patch tokens. Each group is held out once while the others
teach, so the report says whether the probe reads a scene it never saw; the probe taught by every group then reads
the frames, and a frame naming a teaching group is read by the probe that held that group out. The tokens come from a
CLIP_VISION_OUTPUT of a ViT encode with square patches (Vision Patch Encode with DINOv3): prefix tokens (CLS,
registers) first, then row-major patches. A frame's score is its patches' mean logit, the probe applied to its
mean-pooled tokens: the probabilities saturate where a frame reads far to one side, the logits keep counting.
Nothing here loads a model or imports ComfyUI.
"""
from __future__ import annotations

import torch
import torch.nn.functional as F

SCHEMA = 'lf.patch-probe.v1'
CROPS = ('none', 'center')
PATCH_SIZE = 16
# Painted colours: label 1 orange, label 0 blue, over the frame's grey luma; undecided patches stay grey.
POSITIVE = (1.0, 0.55, 0.10)
NEGATIVE = (0.15, 0.45, 1.0)
PAINT_STRENGTH = 0.65
MAX_ITER = 200


def patch_tokens(output, name, patch_size=PATCH_SIZE):
    """[B, P, D] float32 patch tokens of one encode, its (rows, cols) grid and its encoded (height, width)."""
    sequence = getattr(output, 'last_hidden_state', None)
    if (not isinstance(sequence, torch.Tensor) or sequence.ndim != 3 or 0 in sequence.shape
            or not sequence.is_floating_point()):
        raise ValueError(f'{name} needs a CLIP_VISION_OUTPUT whose last_hidden_state is a [B,T,D] tensor '
                         '(Vision Patch Encode keeps the patch tokens).')
    sizes = getattr(output, 'image_sizes', None)
    if not isinstance(sizes, (list, tuple)) or len(sizes) != sequence.shape[0]:
        raise ValueError(f'{name}.image_sizes must hold one encoded [C,H,W] size per image.')
    shapes = {tuple(int(value) for value in size) for size in sizes}
    if len(shapes) != 1 or len(next(iter(shapes))) != 3:
        raise ValueError(f'{name}.image_sizes must be one [C,H,W] size shared by the batch.')
    _, height, width = next(iter(shapes))
    if height <= 0 or width <= 0 or height % patch_size or width % patch_size:
        raise ValueError(f'{name} was encoded at {width}x{height}, not a whole number of {patch_size}-pixel patches.')
    rows, cols = height // patch_size, width // patch_size
    prefix = sequence.shape[1] - rows * cols
    if prefix < 0:
        raise ValueError(f'{name} holds {sequence.shape[1]} tokens, fewer than its {rows}x{cols} patch grid.')
    tokens = sequence[:, prefix:].detach().to(device='cpu', dtype=torch.float32)
    if not torch.isfinite(tokens).all():
        raise ValueError(f'{name} holds non-finite patch tokens.')
    return tokens, (rows, cols), (height, width)


def _items(text):
    return [item.strip() for item in str(text or '').split(',')]


def parse_labels(text, count):
    """One 0 or 1 per teaching image; both must occur."""
    items = [item for item in _items(text) if item]
    if len(items) != count:
        raise ValueError(f'labels names {len(items)} images; the teaching batch holds {count}.')
    if any(item not in ('0', '1') for item in items):
        raise ValueError('labels must be 0 or 1 per teaching image, comma-separated.')
    labels = [int(item) for item in items]
    if set(labels) != {0, 1}:
        raise ValueError('labels need both 0 and 1 among the teaching images.')
    return labels


def parse_groups(text, count):
    """One group name per teaching image, at least two groups, each holding out leaving both labels to teach."""
    groups = _items(text)
    if len(groups) != count or any(not group for group in groups):
        raise ValueError(f'groups must name one group per teaching image ({count}), comma-separated.')
    if len(set(groups)) < 2:
        raise ValueError('groups need at least two names: each is held out once while the others teach.')
    return groups


def parse_frame_groups(text, count, teaching):
    """A teaching group per frame, or an empty entry for a frame the probe never saw; empty text for none."""
    if not str(text or '').strip():
        return [''] * count
    groups = _items(text)
    if len(groups) != count:
        raise ValueError(f'frame_groups names {len(groups)} frames; the frames batch holds {count}.')
    unknown = sorted({group for group in groups if group and group not in teaching})
    if unknown:
        raise ValueError(f'frame_groups names {", ".join(unknown)}, not among the teaching groups.')
    return groups


def parse_names(text):
    names = [item for item in _items(text) if item]
    if len(names) != 2:
        raise ValueError('names must be two words, label 0 then label 1, comma-separated.')
    return names


def fit_probe(features, labels, l2, max_iter=MAX_ITER):
    """Class-balanced L2 logistic regression on standardized [N, D] features with 0/1 [N] labels."""
    # ComfyUI runs nodes under inference mode, and an encoder's tokens are inference tensors, which autograd can
    # neither track nor save: learn with grad on, from normal copies.
    with torch.inference_mode(False), torch.enable_grad():
        return _fit(features.clone(), labels.clone(), l2, max_iter)


def _fit(features, labels, l2, max_iter):
    mean = features.mean(0)
    scale = features.std(0).clamp_min(1e-6)
    standard = (features - mean) / scale
    positives = float(labels.sum())
    negatives = float(labels.numel()) - positives
    sample = torch.where(labels > 0.5, 0.5 / positives, 0.5 / negatives)
    weight = torch.zeros(features.shape[1], requires_grad=True)
    bias = torch.zeros((), requires_grad=True)
    max_eval = max_iter * 5 // 4
    optimizer = torch.optim.LBFGS([weight, bias], lr=1.0, max_iter=max_iter, max_eval=max_eval, history_size=20,
                                  tolerance_grad=1e-7, tolerance_change=1e-10, line_search_fn='strong_wolfe')

    def closure():
        optimizer.zero_grad()
        logits = standard @ weight + bias
        loss = (F.binary_cross_entropy_with_logits(logits, labels, reduction='none') * sample).sum()
        loss = loss + l2 * weight.dot(weight)
        loss.backward()
        return loss

    optimizer.step(closure)
    # LBFGS stops at a tolerance (converged) or at a cap on its iterations or evaluations (not converged).
    state = optimizer.state[weight]
    iterations, evaluations = int(state.get('n_iter', 0)), int(state.get('func_evals', 0))
    return {'mean': mean, 'scale': scale, 'weight': weight.detach(), 'bias': bias.detach(), 'iterations': iterations,
            'converged': iterations < max_iter and evaluations < max_eval}


def probe_logits(probe, features):
    return ((features - probe['mean']) / probe['scale']) @ probe['weight'] + probe['bias']


def roc_auc(scores, labels):
    """Area under the ROC curve by ranks, ties averaged; None without both labels."""
    positive = labels > 0.5
    count_positive = int(positive.sum())
    count_negative = int(labels.numel()) - count_positive
    if not count_positive or not count_negative:
        return None
    order = scores.argsort()
    _, inverse, counts = torch.unique_consecutive(scores[order], return_inverse=True, return_counts=True)
    ends = counts.cumsum(0).to(torch.float64)
    average = ends - (counts.to(torch.float64) - 1.0) / 2.0
    ranks = torch.empty(scores.numel(), dtype=torch.float64)
    ranks[order] = average[inverse]
    found = ranks[positive].sum() - count_positive * (count_positive + 1) / 2.0
    return float(found / (count_positive * count_negative))


def _balanced(values, labels):
    """The mean of each present label's mean."""
    means = [values[labels == label].mean() for label in (0.0, 1.0) if bool((labels == label).any())]
    return float(sum(means) / len(means))


def _patch_labels(labels, patches):
    return torch.tensor(labels, dtype=torch.float32).repeat_interleave(patches)


def held_out(tokens, labels, groups, l2):
    """Each group held out once: its images read by the probe the other groups taught. Returns folds and probes."""
    _, patches, features = tokens.shape
    folds, probes = [], {}
    for group in dict.fromkeys(groups):
        held = [index for index, name in enumerate(groups) if name == group]
        teach = [index for index, name in enumerate(groups) if name != group]
        if {labels[index] for index in teach} != {0, 1}:
            raise ValueError(f'holding out group {group!r} leaves teaching images of one label only.')
        probe = fit_probe(tokens[teach].reshape(-1, features), _patch_labels([labels[i] for i in teach], patches), l2)
        probes[group] = probe
        logits = probe_logits(probe, tokens[held].reshape(-1, features))
        truth = _patch_labels([labels[i] for i in held], patches)
        probability = torch.sigmoid(logits)
        loss = F.binary_cross_entropy_with_logits(logits, truth, reduction='none')
        per_image = probability.reshape(len(held), patches)
        per_logit = logits.reshape(len(held), patches)
        images = [{'index': index, 'label': labels[index], 'mean_probability': round(float(per_image[k].mean()), 4),
                   'mean_logit': round(float(per_logit[k].mean()), 3),
                   'positive_share': round(float((per_image[k] > 0.5).float().mean()), 4)}
                  for k, index in enumerate(held)]
        # the order of the group's images by their mean logits, which keep counting where probabilities saturate
        means = [float(value) for value in per_logit.mean(1)]
        ones = [mean for mean, index in zip(means, held) if labels[index] == 1]
        zeros = [mean for mean, index in zip(means, held) if labels[index] == 0]
        # per patch, over the held-out group's images
        auc = roc_auc(probability, truth)
        folds.append({
            'group': group, 'images': images,
            'accuracy': round(_balanced(((probability > 0.5).float() == truth).float(), truth), 4),
            'auc': None if auc is None else round(auc, 4),
            'log_loss': round(_balanced(loss, truth), 4),
            # every label-1 image reads above every label-0 image of the group (a pair's on above its off)
            'ordered': (min(ones) > max(zeros)) if ones and zeros else None,
            'converged': probe['converged'],
        })
    return folds, probes


def probability_map(logits, grid, size, crop):
    """[H, W] probability at an image's size from its patch grid's logits, and where the grid covers it.

    Geometry follows core clip_preprocess: ``none`` stretches the whole image onto the square, ``center`` scales
    the shorter side to it and keeps the centred square, so the sides outside it are not read (0.5, uncovered).
    """
    height, width = size
    square = logits.reshape(1, 1, *grid)
    if crop == 'none':
        up = F.interpolate(square, size=(height, width), mode='bilinear', align_corners=False)[0, 0]
        return torch.sigmoid(up), torch.ones(height, width)
    side = min(height, width)
    up = F.interpolate(square, size=(side, side), mode='bilinear', align_corners=False)[0, 0]
    top, left = (height - side) // 2, (width - side) // 2
    probability = torch.full((height, width), 0.5)
    covered = torch.zeros(height, width)
    probability[top:top + side, left:left + side] = torch.sigmoid(up)
    covered[top:top + side, left:left + side] = 1.0
    return probability, covered


def paint(image, probability, covered):
    """The frame's grey luma, orange where it reads as label 1 and blue as label 0, by how sure the probe is."""
    rgb = image[..., :3].detach().to(device='cpu', dtype=torch.float32).clamp(0.0, 1.0)
    grey = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]) * 0.8 + 0.1
    base = grey[..., None].expand(*grey.shape, 3)
    colour = torch.where(probability[..., None] >= 0.5, torch.tensor(POSITIVE), torch.tensor(NEGATIVE))
    alpha = ((probability - 0.5).abs() * 2.0 * covered * PAINT_STRENGTH)[..., None]
    return base * (1.0 - alpha) + colour * alpha


def _masks(value, count, size):
    if value is None:
        return None
    masks = value.detach().to(device='cpu', dtype=torch.float32)
    if masks.ndim == 2:
        masks = masks[None]
    if masks.ndim != 3 or masks.shape[0] not in (1, count):
        raise ValueError(f'frame_masks must be one mask or one per frame ({count}), as [B,H,W].')
    if tuple(masks.shape[-2:]) != tuple(size):
        raise ValueError(f'frame_masks are {masks.shape[-1]}x{masks.shape[-2]}; the frames are {size[1]}x{size[0]}.')
    return masks.expand(count, *size) if masks.shape[0] == 1 else masks


def read_patch_probe(teach, labels, groups, frames, frame_images, *, crop='none', l2=0.01, frame_groups='',
                     frame_masks=None, names='0,1'):
    """Teach, hold each group out, read the frames: (report, painted [M,H,W,3], probability [M,H,W])."""
    if crop not in CROPS:
        raise ValueError("crop must be 'none' or 'center', as the frames were encoded.")
    if not isinstance(l2, (int, float)) or l2 < 0:
        raise ValueError('l2 must be a number of zero or more.')
    teach_tokens, grid, encoded = patch_tokens(teach, 'teach')
    frame_tokens, frame_grid, frame_encoded = patch_tokens(frames, 'frames')
    if frame_grid != grid or teach_tokens.shape[2] != frame_tokens.shape[2]:
        raise ValueError(f'frames were encoded as a {frame_grid[0]}x{frame_grid[1]} grid of {frame_tokens.shape[2]} '
                         f'features, the teaching images as {grid[0]}x{grid[1]} of {teach_tokens.shape[2]}: '
                         'encode both with the same model and size.')
    if not isinstance(frame_images, torch.Tensor) or frame_images.ndim != 4 or frame_images.shape[-1] not in (3, 4):
        raise ValueError('frame_images must be one IMAGE batch [M,H,W,C] of the frames.')
    count = frame_tokens.shape[0]
    if frame_images.shape[0] != count:
        raise ValueError(f'frame_images holds {frame_images.shape[0]} images; the frames encode {count}.')
    label_list = parse_labels(labels, teach_tokens.shape[0])
    group_list = parse_groups(groups, teach_tokens.shape[0])
    by_frame = parse_frame_groups(frame_groups, count, set(group_list))
    label_names = parse_names(names)
    size = tuple(frame_images.shape[1:3])
    masks = _masks(frame_masks, count, size)

    folds, probes = held_out(teach_tokens, label_list, group_list, float(l2))
    patches, features = teach_tokens.shape[1], teach_tokens.shape[2]
    whole = fit_probe(teach_tokens.reshape(-1, features), _patch_labels(label_list, patches), float(l2))

    rows, painted, maps = [], [], []
    for index in range(count):
        group = by_frame[index]
        probe = probes[group] if group else whole
        logits = probe_logits(probe, frame_tokens[index])
        probability = torch.sigmoid(logits)
        row = {'index': index, 'group': group or None,
               'read_by': f'without {group}' if group else 'all groups',
               'mean_probability': round(float(probability.mean()), 4),
               'mean_logit': round(float(logits.mean()), 3),
               'positive_share': round(float((probability > 0.5).float().mean()), 4),
               # the probes that each held one group out, on a frame none of them saw: how much the reading leans
               # on any one teaching group
               'fold_range': None, 'mask_probability': None}
        if not group:
            means = [float(probe_logits(fold, frame_tokens[index]).mean()) for fold in probes.values()]
            row['fold_range'] = [round(min(means), 3), round(max(means), 3)]
        picture, covered = probability_map(logits, grid, size, crop)
        if masks is not None:
            weight = masks[index] * covered
            total = float(weight.sum())
            row['mask_probability'] = round(float((picture * weight).sum()) / total, 4) if total > 0 else None
        row['logits'] = [round(float(value), 2) for value in logits]
        rows.append(row)
        painted.append(paint(frame_images[index], picture, covered))
        maps.append(picture)

    aucs = [fold['auc'] for fold in folds if fold['auc'] is not None]
    ordered = [fold['ordered'] for fold in folds if fold['ordered'] is not None]
    report = {
        'schema': SCHEMA, 'names': label_names, 'l2': float(l2), 'crop': crop, 'grid': list(grid),
        'encoded_size': [encoded[1], encoded[0]], 'frame_size': [size[1], size[0]],
        'teaching': {'images': teach_tokens.shape[0], 'patches': teach_tokens.shape[0] * patches,
                     'features': features, 'groups': list(dict.fromkeys(group_list)), 'labels': label_list},
        'held_out': {'folds': folds,
                     'accuracy': round(sum(fold['accuracy'] for fold in folds) / len(folds), 4),
                     'auc': round(sum(aucs) / len(aucs), 4) if aucs else None,
                     'auc_min': min(aucs) if aucs else None,
                     'ordered': f'{sum(ordered)}/{len(ordered)}' if ordered else None},
        # each fit stopped at a tolerance; a fit stopped at its cap names it in the node's title
        'converged': {'held_out': f"{sum(fold['converged'] for fold in folds)}/{len(folds)}",
                      'all_groups': whole['converged']},
        'frames': rows,
    }
    return report, torch.stack(painted), torch.stack(maps)
