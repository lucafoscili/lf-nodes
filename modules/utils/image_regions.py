"""Ordered, reversible image-region editing with local RGB delta composition."""
import torch
import torch.nn.functional as F

from .helpers.logic import normalize_input_image, normalize_json_input

SCHEMA = 'lf.image-regions.v1'
# PNG editor transport quantizes to eight bits; do not turn that noise into edits.
PNG_TOLERANCE = 1.0 / 255.0 + 1e-6


def single_value(value, name):
    while isinstance(value, (list, tuple)):
        if len(value) != 1:
            raise ValueError(f'{name} requires exactly one value.')
        value = value[0]
    return value


def image_items(value, name):
    images = normalize_input_image(value)
    for image in images:
        if not image.is_floating_point() or not torch.isfinite(image).all():
            raise ValueError(f'{name} requires finite floating-point RGB/RGBA images.')
        if image.min() < 0 or image.max() > 1:
            raise ValueError(f'{name} pixels must be in 0..1.')
    return images


def single_image(value, name):
    images = image_items(value, name)
    if len(images) != 1:
        raise ValueError(f'{name} requires exactly one image.')
    return images[0]


def _document(value, name):
    result = normalize_json_input(single_value(value, name))
    if not isinstance(result, dict):
        raise ValueError(f'{name} must be a JSON object.')
    return result


def _rect(value, width, height, name):
    if (not isinstance(value, (list, tuple)) or len(value) != 4
            or any(type(v) is not int for v in value)):
        raise ValueError(f'{name} must be integer [x,y,width,height].')
    x, y, w, h = value
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > width or y + h > height:
        raise ValueError(f'{name} must be positive and inside the image bounds.')
    return [x, y, w, h]


def _regions(document, width, height):
    rows = document.get('regions')
    if not isinstance(rows, list) or not rows:
        raise ValueError('regions must be a non-empty array.')
    result, ids = [], set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Each region must be an object with id, label and rect.')
        identifier, label = row.get('id'), row.get('label')
        if not isinstance(identifier, str) or not identifier.strip() or identifier in ids:
            raise ValueError('Region IDs must be non-empty and unique.')
        if not isinstance(label, str) or not label.strip():
            raise ValueError('Each region label must be non-empty text.')
        rect = _rect(row.get('rect'), width, height, 'Region rect')
        x, y, w, h = rect
        for previous in result:
            px, py, pw, ph = previous['rect']
            if x < px + pw and px < x + w and y < py + ph and py < y + h:
                raise ValueError('Overlapping image regions are not supported.')
        result.append({'id': identifier, 'label': label, 'rect': rect})
        ids.add(identifier)
    return result


def _canvas_size(value):
    value = single_value(value, 'canvas_size')
    if type(value) is not int or not 1 <= value <= 4096:
        raise ValueError('canvas_size must be an integer in 1..4096.')
    return value


def _content_rect(rect, size):
    _, _, width, height = rect
    scale = size / max(width, height)
    w, h = max(1, round(width * scale)), max(1, round(height * scale))
    return [(size - w) // 2, (size - h) // 2, w, h]


def _resize(image, height, width):
    if image.shape[1:3] == (height, width):
        return image
    return F.interpolate(image.permute(0, 3, 1, 2), size=(height, width), mode='bilinear',
                         align_corners=False, antialias=True).permute(0, 2, 3, 1)


def aspect_fit_content_rect(width, height, size):
    """Return the centred content rectangle for an aspect-fit square canvas."""
    return _content_rect([0, 0, width, height], size)


def aspect_fit_canvas(image, size, *, padding='replicate'):
    """Fit one image into a square editing canvas without stretching it."""
    if image.ndim != 4 or image.shape[0] != 1:
        raise ValueError('aspect_fit_canvas requires one [1,H,W,C] image.')
    _, height, width, _ = image.shape
    content_rect = aspect_fit_content_rect(width, height, size)
    cx, cy, cw, ch = content_rect
    fitted = _resize(image.to(dtype=torch.float32), ch, cw).clamp(0, 1)
    channels_first = fitted.permute(0, 3, 1, 2)
    padding_values = (cx, size-cw-cx, cy, size-ch-cy)
    if padding == 'replicate':
        canvas = F.pad(channels_first, padding_values, mode='replicate')
    elif padding == 'transparent':
        canvas = F.pad(channels_first, padding_values, mode='constant', value=0)
    else:
        raise ValueError("padding must be 'replicate' or 'transparent'.")
    return canvas.permute(0, 2, 3, 1).contiguous(), content_rect


def restore_rgb_canvas_edit(source, edited, baseline, expected_canvas, content_rect, *, name):
    """Project an editor RGB delta onto native pixels while preserving alpha."""
    if source.ndim != 4 or source.shape[0] != 1 or source.shape[-1] not in (3, 4):
        raise ValueError(f'{name} source must be one RGB/RGBA image.')
    if expected_canvas.ndim != 4 or expected_canvas.shape[0] != 1:
        raise ValueError(f'{name} expected canvas must be one image.')
    if tuple(baseline.shape) != tuple(expected_canvas.shape):
        raise ValueError(f'{name} original canvas dimensions/channels do not match the layout.')
    if (edited.ndim != 4 or edited.shape[0] != 1
            or edited.shape[1:3] != expected_canvas.shape[1:3]
            or edited.shape[-1] not in (3, 4)):
        raise ValueError(f'{name} edited canvas must match the layout dimensions and use RGB/RGBA.')

    device = source.device
    baseline = baseline.to(device=device, dtype=torch.float32)
    expected_canvas = expected_canvas.to(device=device, dtype=torch.float32)
    if (baseline - expected_canvas).abs().max() > PNG_TOLERANCE:
        raise ValueError(f'{name} original canvas does not match extraction order/source.')

    edited = edited.to(device=device, dtype=torch.float32)
    cx, cy, cw, ch = content_rect
    delta = (edited[:, cy:cy+ch, cx:cx+cw, :3]
             - baseline[:, cy:cy+ch, cx:cx+cw, :3])
    # Zero each unchanged channel before interpolation so PNG noise cannot
    # bleed into neighbouring edited pixels. Alpha is never composed.
    delta = torch.where(delta.abs() > PNG_TOLERANCE, delta, 0)
    result = source.clone()
    if not torch.count_nonzero(delta):
        return result

    _, height, width, _ = source.shape
    projected = _resize(delta, height, width)
    target = result[..., :3]
    changed = projected != 0
    candidate = (target.to(dtype=torch.float32) + projected).clamp(0, 1).to(dtype=target.dtype)
    target.copy_(torch.where(changed, candidate, target))
    return result


def _canvas(image, row, size):
    x, y, w, h = row['rect']
    canvas, _ = aspect_fit_canvas(image[:, y:y+h, x:x+w], size, padding='replicate')
    return canvas


def extract_image_regions(image, regions, canvas_size):
    source = single_image(image, 'image')
    _, height, width, channels = source.shape
    size = _canvas_size(canvas_size)
    rows = _regions(_document(regions, 'regions'), width, height)
    for row in rows:
        row['content_rect'] = _content_rect(row['rect'], size)
    images = [_canvas(source, row, size) for row in rows]
    layout = {'schema': SCHEMA, 'source_size': [width, height], 'channels': channels,
              'canvas_size': size, 'regions': rows}
    config = {'image_entries': [{'id': row['id'], 'label': row['label']} for row in rows]}
    return images, layout, config


def compose_image_regions(original, edited, original_regions, layout):
    source = single_image(original, 'original')
    document = _document(layout, 'layout')
    _, height, width, channels = source.shape
    if (document.get('schema') != SCHEMA or document.get('source_size') != [width, height]
            or document.get('channels') != channels):
        raise ValueError('layout must match the original image dimensions/channels and schema.')
    size = _canvas_size(document.get('canvas_size'))
    rows = _regions(document, width, height)
    for row, stored in zip(rows, document['regions']):
        expected = _content_rect(row['rect'], size)
        if stored.get('content_rect') != expected:
            raise ValueError('layout content_rect does not match the aspect-fit geometry.')
        row['content_rect'] = expected
    edits = image_items(edited, 'edited')
    baselines = image_items(original_regions, 'original_regions')
    if len(edits) != len(rows) or len(baselines) != len(rows):
        raise ValueError('edited and original_regions must match layout cardinality exactly; no broadcast.')
    result = source.clone()
    for row, edited_image, baseline in zip(rows, edits, baselines):
        if tuple(edited_image.shape) != (1, size, size, channels) or tuple(baseline.shape) != (1, size, size, channels):
            raise ValueError('Region image dimensions/channels must match the layout canvas.')
        edited_image = edited_image.to(device=source.device, dtype=torch.float32)
        baseline = baseline.to(device=source.device, dtype=torch.float32)
        expected = _canvas(source, row, size)
        x, y, w, h = row['rect']
        restored = restore_rgb_canvas_edit(
            source[:, y:y+h, x:x+w], edited_image, baseline, expected,
            row['content_rect'], name='Region')
        result[:, y:y+h, x:x+w].copy_(restored)
    return result
