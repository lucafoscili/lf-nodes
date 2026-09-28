"""Ordered, source-owned RGBA layer editing and Pillow-compatible composition."""
from __future__ import annotations

from io import BytesIO
import hashlib
import os
from pathlib import Path
import re

import numpy as np
from PIL import Image
import torch

from .helpers.conversion import pil_to_tensor
from .helpers.logic import normalize_json_input, normalize_masks_for_images
from .image_regions import (
    aspect_fit_canvas,
    aspect_fit_content_rect,
    compose_image_regions,
    extract_image_regions,
    image_items,
    restore_rgb_canvas_edit,
    single_image,
    single_value,
)


SCHEMA = 'lf.image-layers.v1'
_SHA256 = re.compile(r'^[0-9a-fA-F]{64}$')


def _document(value, name):
    result = normalize_json_input(single_value(value, name))
    if not isinstance(result, dict):
        raise ValueError(f'{name} must be a JSON object.')
    return result


def _canvas_size(value):
    value = single_value(value, 'canvas_size')
    if type(value) is not int or not 1 <= value <= 4096:
        raise ValueError('canvas_size must be an integer in 1..4096.')
    return value


def _rect(value, name):
    if (not isinstance(value, (list, tuple)) or len(value) != 4
            or any(type(item) is not int for item in value)):
        raise ValueError(f'{name} must be integer [x,y,width,height].')
    x, y, width, height = value
    if x < 0 or y < 0 or width <= 0 or height <= 0:
        raise ValueError(f'{name} must have a non-negative origin and positive size.')
    return [x, y, width, height]


def _identity(row, identifiers):
    identifier, label = row.get('id'), row.get('label')
    if not isinstance(identifier, str) or not identifier.strip() or identifier in identifiers:
        raise ValueError('Layer IDs must be non-empty and unique.')
    if not isinstance(label, str) or not label.strip():
        raise ValueError('Each layer label must be non-empty text.')
    identifiers.add(identifier)
    return identifier, label


def _root(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('manifest root must be a non-empty directory path.')
    try:
        resolved = Path(value).resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ValueError('manifest root must resolve to an existing directory.') from error
    if not resolved.is_dir():
        raise ValueError('manifest root must resolve to an existing directory.')
    return resolved


def _source_path(root, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Each layer file must be a non-empty relative path.')
    relative = Path(value)
    if relative.is_absolute() or relative.anchor or relative.drive:
        raise ValueError('Layer files must be relative to manifest root.')
    try:
        candidate = (root / relative).resolve(strict=True)
        root_key = os.path.normcase(os.fspath(root))
        candidate_key = os.path.normcase(os.fspath(candidate))
        contained = os.path.commonpath((root_key, candidate_key)) == root_key
    except (OSError, RuntimeError, ValueError) as error:
        raise ValueError('Layer file must resolve inside manifest root.') from error
    if not contained:
        raise ValueError('Layer file must resolve inside manifest root.')
    if not candidate.is_file():
        raise ValueError('Layer file must resolve to an existing file.')
    return candidate


def _tensor_bytes(image):
    pixels = image.detach().clamp(0, 1).mul(255).round().to(torch.uint8).cpu().numpy()[0]
    return np.ascontiguousarray(pixels).tobytes()


def _rgba_digest(image):
    return hashlib.sha256(_tensor_bytes(image)).hexdigest()


def _tensor_to_pil(image):
    pixels = image.detach().clamp(0, 1).mul(255).round().to(torch.uint8).cpu().numpy()[0]
    if pixels.shape[-1] == 3:
        return Image.fromarray(pixels, mode='RGB')
    if pixels.shape[-1] == 4:
        return Image.fromarray(pixels, mode='RGBA')
    raise ValueError('Image must use RGB or RGBA channels.')


def _load_rgba(path, expected_sha256):
    if expected_sha256 is not None:
        if not isinstance(expected_sha256, str) or not _SHA256.fullmatch(expected_sha256):
            raise ValueError('Layer sha256 must be 64 hexadecimal characters.')
    try:
        data = path.read_bytes()
    except OSError as error:
        raise ValueError(f'Layer file could not be read: {path.name}.') from error
    digest = hashlib.sha256(data).hexdigest()
    if expected_sha256 is not None:
        if digest != expected_sha256.lower():
            raise ValueError(f'Layer sha256 does not match {path.name}.')
    try:
        with Image.open(BytesIO(data)) as source:
            image = source.convert('RGBA').copy()
    except (OSError, ValueError) as error:
        raise ValueError(f'Layer file is not a readable image: {path.name}.') from error
    return image, digest


def _as_rgba(image):
    if image.shape[-1] == 4:
        return image
    return torch.cat((image, torch.ones_like(image[..., :1])), dim=-1)


def _retention_source(source):
    return torch.cat((torch.ones_like(source[..., :3]), source[..., 3:4]), dim=-1)


def _editor_entries(rows, base_layout, include_masks):
    entries = []
    if base_layout is not None:
        for index, row in enumerate(base_layout['regions']):
            entries.append({'kind': 'base', 'index': index, 'id': f"base:{row['id']}",
                            'label': f"Base · {row['label']}"})
    for index, row in enumerate(rows):
        entries.append({'kind': 'layer', 'index': index, 'id': f"layer:{row['id']}",
                        'label': f"Fabric · {row['label']}"})
        if include_masks:
            entries.append({'kind': 'mask', 'index': index, 'id': f"mask:{row['id']}",
                            'label': f"Cut · {row['label']}"})
    return entries


def load_image_layers(manifest, canvas_size, include_masks=False, base=None, base_regions=None):
    document = _document(manifest, 'manifest')
    root = _root(document.get('root'))
    rows = document.get('layers')
    if not isinstance(rows, list) or not rows:
        raise ValueError('manifest layers must be a non-empty array.')
    size = _canvas_size(canvas_size)
    include_masks = single_value(include_masks, 'include_masks')
    if type(include_masks) is not bool:
        raise ValueError('include_masks must be a boolean.')
    if (base is None) != (base_regions is None):
        raise ValueError('base and base_regions must be supplied together.')

    identifiers = set()
    canvases, sources, layout_rows = [], [], []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Each layer must be an object with id, label, file and rect.')
        identifier, label = _identity(row, identifiers)
        rect = _rect(row.get('rect'), 'Layer rect')
        path = _source_path(root, row.get('file'))
        pil_image, file_sha256 = _load_rgba(path, row.get('sha256'))
        width, height = pil_image.size
        if width * rect[3] != height * rect[2]:
            raise ValueError(
                f'Layer {identifier!r} has aspect {width}:{height}; '
                f'expected {rect[2]}:{rect[3]} from rect.')

        source = pil_to_tensor(pil_image)
        canvas, content_rect = aspect_fit_canvas(source, size, padding='transparent')
        sources.append(source)
        canvases.append(canvas)
        layout_rows.append({
            'id': identifier,
            'label': label,
            'rect': rect,
            'source_size': [width, height],
            'content_rect': content_rect,
            'file_sha256': file_sha256,
            'rgba_sha256': _rgba_digest(source),
        })

    layout = {'schema': SCHEMA, 'canvas_size': size, 'layers': layout_rows}
    config = {'image_entries': [
        {'id': row['id'], 'label': row['label']} for row in layout_rows
    ]}
    if include_masks or base is not None:
        base_canvases, base_layout = [], None
        if base is not None:
            base_image = _as_rgba(single_image(base, 'base'))
            base_canvases, base_layout, _ = extract_image_regions(base_image, base_regions, size)
            layout['base_layout'] = base_layout
            layout['base_rgba_sha256'] = _rgba_digest(base_image)
        entries = _editor_entries(layout_rows, base_layout, include_masks)
        expanded = list(base_canvases)
        for canvas, source in zip(canvases, sources):
            expanded.append(canvas)
            if include_masks:
                mask_canvas, _ = aspect_fit_canvas(_retention_source(source), size, padding='transparent')
                expanded.append(mask_canvas)
        canvases = expanded
        layout['include_masks'] = include_masks
        layout['editor_entries'] = entries
        config = {'image_entries': [{'id': entry['id'], 'label': entry['label']} for entry in entries]}
    return canvases, layout, config, sources


def _layout(value):
    document = _document(value, 'layout')
    if document.get('schema') != SCHEMA:
        raise ValueError(f'layout schema must be {SCHEMA}.')
    size = _canvas_size(document.get('canvas_size'))
    rows = document.get('layers')
    if not isinstance(rows, list) or not rows:
        raise ValueError('layout layers must be a non-empty array.')

    identifiers = set()
    result = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Each layout layer must be an object.')
        identifier, label = _identity(row, identifiers)
        rect = _rect(row.get('rect'), 'Layer rect')
        source_size = row.get('source_size')
        if (not isinstance(source_size, (list, tuple)) or len(source_size) != 2
                or any(type(item) is not int or item <= 0 for item in source_size)):
            raise ValueError('Layer source_size must be positive integer [width,height].')
        width, height = source_size
        if width * rect[3] != height * rect[2]:
            raise ValueError('Layer source_size aspect must match its target rect.')
        expected_content = aspect_fit_content_rect(width, height, size)
        if row.get('content_rect') != expected_content:
            raise ValueError('Layer content_rect does not match the aspect-fit geometry.')
        rgba_sha256 = row.get('rgba_sha256')
        if not isinstance(rgba_sha256, str) or not _SHA256.fullmatch(rgba_sha256):
            raise ValueError('Layer rgba_sha256 must be 64 hexadecimal characters.')
        result.append({
            'id': identifier,
            'label': label,
            'rect': rect,
            'source_size': [width, height],
            'content_rect': expected_content,
            'rgba_sha256': rgba_sha256.lower(),
        })
    return size, result


def compose_image_layers(base, edited, original_layers, source_layers, layout, base_mask=None):
    base_image = single_image(base, 'base')
    size, rows = _layout(layout)
    edits = image_items(edited, 'edited')
    baselines = image_items(original_layers, 'original_layers')
    sources = image_items(source_layers, 'source_layers')
    document = _document(layout, 'layout')
    include_masks = document.get('include_masks', False)
    if type(include_masks) is not bool:
        raise ValueError('layout include_masks must be a boolean.')
    base_layout = document.get('base_layout')
    base_count = 0
    if base_layout is not None:
        base_image = _as_rgba(base_image)
        if _rgba_digest(base_image) != document.get('base_rgba_sha256'):
            raise ValueError('base does not match extraction source.')
        _, expected_layout, _ = extract_image_regions(base_image, base_layout, size)
        if expected_layout != base_layout:
            raise ValueError('base_layout does not match extraction geometry.')
        base_count = len(base_layout['regions'])
    if base_mask is not None and base_layout is None:
        raise ValueError('base_mask requires editable base regions in layout.')
    if 'editor_entries' in document or include_masks or base_layout is not None:
        if document.get('editor_entries') != _editor_entries(rows, base_layout, include_masks):
            raise ValueError('layout editor_entries do not match extraction order.')
    entry_count = base_count + len(rows) * (2 if include_masks else 1)
    if len(edits) != entry_count or len(baselines) != entry_count or len(sources) != len(rows):
        raise ValueError(
            'edited, original_layers and source_layers must match layout cardinality exactly; '
            'no broadcast.')

    if base_layout is not None:
        edited_base = compose_image_regions(
            base_image, [_as_rgba(item) for item in edits[:base_count]],
            baselines[:base_count], base_layout)
        if base_mask is not None:
            mask = normalize_masks_for_images(base_mask, 1)[0].to(
                device=base_image.device, dtype=base_image.dtype)
            if tuple(mask.shape) != tuple(base_image.shape[:3]):
                raise ValueError('base_mask dimensions must match the base image.')
            if not torch.isfinite(mask).all() or mask.min() < 0 or mask.max() > 1:
                raise ValueError('base_mask requires finite pixels in 0..1.')
            edited_base[..., :3] = base_image[..., :3] + (
                edited_base[..., :3] - base_image[..., :3]) * mask.unsqueeze(-1)
        base_image = edited_base

    _, base_height, base_width, _ = base_image.shape
    restored_layers = []
    for index, (row, source) in enumerate(zip(rows, sources)):
        entry_index = base_count + index * (2 if include_masks else 1)
        edited_image, baseline = edits[entry_index], baselines[entry_index]
        x, y, width, height = row['rect']
        if x + width > base_width or y + height > base_height:
            raise ValueError('Layer rect must fit inside the base image bounds.')
        source_width, source_height = row['source_size']
        if tuple(source.shape) != (1, source_height, source_width, 4):
            raise ValueError('source_layers dimensions/channels must match layout source_size as RGBA.')
        if _rgba_digest(source) != row['rgba_sha256']:
            raise ValueError('source_layers does not match extraction order/source.')
        if tuple(baseline.shape) != (1, size, size, 4):
            raise ValueError('original_layers dimensions/channels must match the RGBA editing canvas.')
        if (edited_image.ndim != 4 or edited_image.shape[0] != 1
                or tuple(edited_image.shape[1:3]) != (size, size)
                or edited_image.shape[-1] not in (3, 4)):
            raise ValueError('edited layer dimensions must match the RGB/RGBA editing canvas.')

        expected, _ = aspect_fit_canvas(source, size, padding='transparent')
        restored = restore_rgb_canvas_edit(
            source, edited_image, baseline, expected, row['content_rect'], name='Layer')
        if include_masks:
            retention_source = _retention_source(source)
            expected_mask, _ = aspect_fit_canvas(retention_source, size, padding='transparent')
            retention = restore_rgb_canvas_edit(
                retention_source, edits[entry_index + 1], baselines[entry_index + 1],
                expected_mask, row['content_rect'], name='Cut mask')
            restored[..., 3:4] = source[..., 3:4] * retention[..., :3].mean(dim=-1, keepdim=True)
        restored_layers.append(restored)

    atlas = _tensor_to_pil(base_image).convert('RGBA')
    for row, layer in zip(rows, restored_layers):
        x, y, width, height = row['rect']
        resized = _tensor_to_pil(layer).convert('RGBA').resize(
            (width, height), Image.Resampling.LANCZOS)
        atlas.alpha_composite(resized, (x, y))
    return pil_to_tensor(atlas), restored_layers
