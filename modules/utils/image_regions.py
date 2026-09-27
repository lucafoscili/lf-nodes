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


def _canvas(image, row, size):
    x, y, w, h = row['rect']
    cx, cy, cw, ch = row['content_rect']
    fitted = _resize(image[:, y:y+h, x:x+w].to(dtype=torch.float32), ch, cw).clamp(0, 1)
    return F.pad(fitted.permute(0, 3, 1, 2), (cx, size-cw-cx, cy, size-ch-cy),
                 mode='replicate').permute(0, 2, 3, 1).contiguous()


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
        if (baseline - expected).abs().max() > PNG_TOLERANCE:
            raise ValueError('original_regions does not match extraction order/source; use the editor original image list.')
        cx, cy, cw, ch = row['content_rect']
        delta = edited_image[:, cy:cy+ch, cx:cx+cw, :3] - baseline[:, cy:cy+ch, cx:cx+cw, :3]
        # Zero each unchanged channel before interpolation so PNG noise cannot
        # bleed into neighbouring edited pixels. Alpha is never composed.
        delta = torch.where(delta.abs() > PNG_TOLERANCE, delta, 0)
        if not torch.count_nonzero(delta):
            continue
        x, y, w, h = row['rect']
        projected = _resize(delta, h, w)
        target = result[:, y:y+h, x:x+w, :3]
        changed = projected != 0
        candidate = (target.to(dtype=torch.float32) + projected).clamp(0, 1).to(dtype=target.dtype)
        target.copy_(torch.where(changed, candidate, target))
    return result
