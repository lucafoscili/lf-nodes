import math
from copy import deepcopy
import logging
import torch

from typing import Any, Dict, Tuple

from ...filters._common import apply_gaussian_blur
from ..logic.normalize_json_input import normalize_json_input
from ..logic.normalize_output_mask import normalize_output_mask

TEXT_REGION_MASK_SCHEMA = 'lf.text-region-masks.v1'


def _text_regions(value):
    """Retain the semantic row array while removing Comfy's list wrapper."""
    value = normalize_json_input(value)
    while isinstance(value, (list, tuple)) and len(value) == 1 and isinstance(value[0], (list, tuple)):
        value = value[0]
    if not isinstance(value, list) or not value:
        raise ValueError('regions must be a non-empty JSON array of {id,prompt,priority}.')
    rows, identifiers = [], set()
    for row in value:
        if not isinstance(row, dict):
            raise ValueError('Each region must be an object with id, prompt and priority.')
        identifier, prompt, priority = row.get('id'), row.get('prompt'), row.get('priority')
        if not isinstance(identifier, str) or not identifier.strip() or identifier in identifiers:
            raise ValueError('Region IDs must be non-empty and unique.')
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError('Each region prompt must be non-empty text.')
        if isinstance(priority, bool) or not isinstance(priority, (int, float)) or not math.isfinite(priority):
            raise ValueError('Each region priority must be a finite number.')
        identifiers.add(identifier)
        rows.append({'id': identifier, 'prompt': prompt, 'priority': priority})
    return rows


def _region_mask_items(value, *, binary=False):
    candidates = []

    def collect(item):
        if isinstance(item, (list, tuple)):
            for child in item:
                collect(child)
        elif torch.is_tensor(item):
            if item.is_complex() or not torch.isfinite(item).all():
                raise ValueError('Region masks must contain finite real values in 0..1.')
            if item.numel() == 0 or item.min() < 0 or item.max() > 1:
                raise ValueError('Region masks must contain non-empty values in 0..1.')
            if binary and not ((item == 0) | (item == 1)).all():
                raise ValueError('Region metadata requires binary masks containing only 0 and 1.')
            # Threshold in the original dtype before normalization casts to
            # float32: values just below 0.5 must not round up into the region.
            candidates.append(item if binary else item >= 0.5)
        else:
            raise ValueError('Region masks must be MASK tensors.')

    collect(value)
    _, items = normalize_output_mask(candidates)
    shapes = {tuple(item.shape[1:]) for item in items}
    if len(shapes) != 1:
        raise ValueError('Region masks must all have the same spatial size.')
    return [item.detach().to(device='cpu', dtype=torch.float32) for item in items]


def resolve_region_overlaps(masks, regions):
    """Resolve one ordered region set; attribute losses to the final pixel owner."""
    regions = _text_regions(regions)
    items = _region_mask_items(masks)
    if len(items) != len(regions):
        raise ValueError('Expected exactly one mask per region.')
    raw = torch.cat(items, dim=0) >= 0.5
    owner = torch.full(raw.shape[1:], -1, dtype=torch.int64)
    for index in sorted(range(len(regions)), key=lambda i: (-regions[i]['priority'], i)):
        owner[raw[index] & (owner < 0)] = index
    resolved = torch.stack([owner == i for i in range(len(regions))])
    records = []
    for index, region in enumerate(regions):
        area, raw_area = int(resolved[index].sum()), int(raw[index].sum())
        record = {'id': region['id'], 'area': area, 'raw_area': raw_area, 'empty': area == 0,
                  'overlap_lost': []}
        for winner, winner_region in enumerate(regions):
            lost = int((raw[index] & resolved[winner]).sum()) if winner != index else 0
            if lost:
                record['overlap_lost'].append({'id': winner_region['id'], 'area': lost})
        if not area:
            record['warning'] = ('No pixels detected for this region.' if not raw_area
                                 else 'Region is empty after overlap resolution.')
        records.append(record)
    return resolved.to(dtype=torch.float32), records


def text_region_masks(image, masks, regions):
    """Turn region-major detector masks into image-major, disjoint mask sets."""
    # Lazy import avoids the helpers package's image_regions import cycle.
    from ...image_regions import image_items

    images = image_items(image, 'image')
    if not images:
        raise ValueError('image requires at least one image.')
    sizes = {tuple(item.shape[1:3]) for item in images}
    if len(sizes) != 1:
        raise ValueError('image must use one shared spatial size.')
    height, width = images[0].shape[1:3]
    rows = _text_regions(regions)
    items = _region_mask_items(masks)
    if len(items) != len(images) * len(rows):
        raise ValueError('Expected exactly image_count * region_count masks in region-major order.')
    if tuple(items[0].shape[1:]) != (height, width):
        raise ValueError('Region mask size must match the source image size.')
    outputs, mask_sets = [], []
    for image_index in range(len(images)):
        result, records = resolve_region_overlaps(
            [items[region_index * len(images) + image_index] for region_index in range(len(rows))], rows)
        outputs.append(result)
        mask_sets.append({'image_index': image_index, 'regions': records})
        for record in records:
            if 'warning' in record:
                logging.getLogger(__name__).warning('Image %s region %s: %s', image_index,
                                                    record['id'], record['warning'])
    document = {'schema': TEXT_REGION_MASK_SCHEMA, 'source_size': [width, height],
                'image_count': len(images), 'regions': rows, 'ordering': 'image-major',
                'mask_sets': mask_sets}
    batches, mask_list = normalize_output_mask(outputs)
    return batches[0], document, mask_list


def region_mask_sets(masks, metadata):
    """Validate region mask sets and return CPU [N,R,H,W].

    Accept either a single document or two single-image documents. Flat masks
    always follow image-major order, then the original region table order.
    Recorded areas establish structural consistency, not source-image identity.
    """
    metadata = normalize_json_input(metadata)
    while isinstance(metadata, (list, tuple)) and len(metadata) == 1:
        metadata = normalize_json_input(metadata[0])
    documents = metadata if isinstance(metadata, list) else [metadata]
    if not 1 <= len(documents) <= 2 or not all(isinstance(doc, dict) for doc in documents):
        raise ValueError('metadata requires one document or two single-image documents.')
    items = _region_mask_items(masks, binary=True)
    combined = None
    sets = []
    for document in documents:
        if document.get('schema') != TEXT_REGION_MASK_SCHEMA:
            raise ValueError('metadata schema must be lf.text-region-masks.v1.')
        size = document.get('source_size')
        if (not isinstance(size, list) or len(size) != 2
                or any(type(v) is not int or v <= 0 for v in size)):
            raise ValueError('metadata source_size must be positive integer [width,height].')
        rows = _text_regions(document.get('regions'))
        count, entries = document.get('image_count'), document.get('mask_sets')
        if (type(count) is not int or count < 1 or not isinstance(entries, list)
                or len(entries) != count or (len(documents) == 2 and count != 1)):
            raise ValueError('metadata image_count and mask_sets must agree; paired documents require one set each.')
        if document.get('ordering') != 'image-major':
            raise ValueError('metadata ordering must be image-major.')
        if combined is None:
            combined = deepcopy(document)
            combined['regions'] = rows
        elif (size != combined['source_size']
              or [row['id'] for row in rows] != [row['id'] for row in combined['regions']]):
            raise ValueError('metadata documents must share source_size and identical ordered region IDs.')
        for image_index, entry in enumerate(entries):
            if (not isinstance(entry, dict) or type(entry.get('image_index')) is not int
                    or entry['image_index'] != image_index):
                raise ValueError('metadata mask_sets must retain image_index order.')
            records = entry.get('regions')
            if not isinstance(records, list) or len(records) != len(rows):
                raise ValueError('metadata mask_sets must contain one record per region.')
            if any(not isinstance(record, dict) or record.get('id') != row['id']
                   for record, row in zip(records, rows)):
                raise ValueError('metadata mask set region IDs/order do not match the region table.')
            copied = deepcopy(entry)
            copied['image_index'] = len(sets)
            sets.append(copied)
    expected_count = len(sets) * len(combined['regions'])
    if len(items) != expected_count:
        raise ValueError('Mask count does not match metadata image_count * region_count.')
    width, height = combined['source_size']
    if tuple(items[0].shape[1:]) != (height, width):
        raise ValueError('Mask size does not match metadata source_size.')
    tensor = torch.cat(items).reshape(len(sets), len(combined['regions']), height, width)
    if (tensor.sum(dim=1) > 1).any():
        raise ValueError('Region masks must be disjoint within each image set.')
    identifiers = {row['id'] for row in combined['regions']}
    for set_index, entry in enumerate(sets):
        for region_index, record in enumerate(entry['regions']):
            area = int(tensor[set_index, region_index].sum(dtype=torch.int64))
            if type(record.get('area')) is not int or record['area'] != area:
                raise ValueError('metadata region area does not match the actual mask.')
            if type(record.get('empty')) is not bool or record['empty'] != (area == 0):
                raise ValueError('metadata region empty does not match the actual mask.')
            raw_area, losses = record.get('raw_area'), record.get('overlap_lost')
            if (type(raw_area) is not int or not area <= raw_area <= width * height
                    or not isinstance(losses, list)):
                raise ValueError('metadata raw_area/overlap_lost must describe valid region areas.')
            lost_ids, lost_area = set(), 0
            for loss in losses:
                if (not isinstance(loss, dict) or loss.get('id') not in identifiers
                        or loss['id'] == record['id'] or loss['id'] in lost_ids
                        or type(loss.get('area')) is not int or loss['area'] <= 0):
                    raise ValueError('metadata overlap_lost must contain unique winning region IDs and positive areas.')
                lost_ids.add(loss['id'])
                lost_area += loss['area']
            if raw_area - area != lost_area:
                raise ValueError('metadata raw_area must equal area plus overlap_lost areas.')
    combined['mask_sets'], combined['image_count'] = sets, len(sets)
    return tensor, combined

# region Helpers
def _gaussian_blur_2d(tensor: torch.Tensor, kernel_size: Tuple[int, int], sigma: float) -> torch.Tensor:
    """
    Applies a 2D Gaussian blur to the input tensor.

    Args:
        tensor (torch.Tensor): Input tensor of shape (1, 1, H, W) or (1, H, W).
        kernel_size (Tuple[int, int]): Size of the Gaussian kernel (height, width).
        sigma (float): Standard deviation of the Gaussian kernel. If sigma <= 0, no blur is applied.

    Returns:
        torch.Tensor: The blurred tensor with the same shape and device as the input.
    """
    if sigma <= 0:
        return tensor
    _, kw = kernel_size
    array = tensor.squeeze(0).squeeze(0).detach().cpu().numpy().astype("float32")
    blurred = apply_gaussian_blur(array, max(1, kw), sigma)
    result = torch.from_numpy(blurred).to(tensor.device, tensor.dtype)

    return result.unsqueeze(0).unsqueeze(0)

def _ensure_bbox(region: Dict[str, Any], image_height: int, image_width: int) -> Tuple[float, float, float, float]:
    """
    Ensures that the region's bounding box is valid and clamped within image dimensions.

    Args:
        region (Dict[str, Any]): A dictionary containing region metadata, expected to have either "bbox_float" or "bbox" keys with a list of four values [x1, y1, x2, y2].
        image_height (int): The height of the image.
        image_width (int): The width of the image.

    Returns:
        Tuple[float, float, float, float]: The clamped bounding box coordinates (x1, y1, x2, y2) as floats.

    Raises:
        ValueError: If the region metadata does not contain valid bounding box information.
    """
    bbox = region.get("bbox_float") or region.get("bbox")
    if bbox is None or len(bbox) != 4:
        raise ValueError("Region metadata missing bbox information")
    x1, y1, x2, y2 = [float(v) for v in bbox]
    if region.get("bbox") is not None:
        # incoming bbox assumed inclusive pixel indices; treat as floats but clamp within image
        pass
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1

    return (
        max(0.0, min(x1, image_width - 1.0)),
        max(0.0, min(y1, image_height - 1.0)),
        max(0.0, min(x2, image_width - 1.0)),
        max(0.0, min(y2, image_height - 1.0)),
    )
# endregion

# region build_region_mask
def build_region_mask(
    image: torch.Tensor,
    region: Dict[str, Any],
    *,
    padding: float = 0.0,
    padding_px: float = 0.0,
    feather: float = 0.0,
    shape: str = "rectangle",
    invert: bool = False,
) -> torch.Tensor:
    """
    Builds a region mask for a given image tensor and region specification.

    Args:
        image (torch.Tensor): Input image tensor of shape [B, H, W, C].
        region (Dict[str, Any]): Dictionary specifying the region (bounding box) in the image.
        padding (float, optional): Fractional padding to apply to the region size (relative to width/height). Default is 0.0.
        padding_px (float, optional): Absolute padding in pixels to apply to the region size. Default is 0.0.
        feather (float, optional): Amount of feathering (Gaussian blur) to apply to the mask edges. Default is 0.0.
        shape (str, optional): Shape of the region mask, either "rectangle" or "ellipse". Default is "rectangle".
        invert (bool, optional): If True, inverts the mask (region becomes background). Default is False.

    Returns:
        torch.Tensor: Region mask tensor of shape [1, H, W, 1] with values in [0.0, 1.0].

    Raises:
        ValueError: If the input image tensor does not have shape [B, H, W, C].
    """
    if image.dim() != 4:
        raise ValueError("image tensor must be [B,H,W,C]")
    device = image.device
    dtype = torch.float32
    _, H, W, _ = image.shape
    x1, y1, x2, y2 = _ensure_bbox(region, H, W)
    # ensure coordinates inclusive/exclusive ordering
    if x2 <= x1 or y2 <= y1:
        return torch.zeros((1, H, W, 1), device=device, dtype=dtype)

    width = x2 - x1
    height = y2 - y1
    padding = max(0.0, float(padding))
    padding_px = max(0.0, float(padding_px))
    pad_w = padding * width + padding_px
    pad_h = padding * height + padding_px

    x1 = max(0.0, x1 - pad_w)
    x2 = min(float(W), x2 + pad_w)
    y1 = max(0.0, y1 - pad_h)
    y2 = min(float(H), y2 + pad_h)

    if x2 <= x1 or y2 <= y1:
        return torch.zeros((1, H, W, 1), device=device, dtype=dtype)

    mask = torch.zeros((H, W), device=device, dtype=dtype)
    if shape == "ellipse":
        yy = torch.arange(H, device=device, dtype=dtype).unsqueeze(1)
        xx = torch.arange(W, device=device, dtype=dtype).unsqueeze(0)
        cx = (x1 + x2) * 0.5
        cy = (y1 + y2) * 0.5
        rx = max((x2 - x1) * 0.5, 1.0)
        ry = max((y2 - y1) * 0.5, 1.0)
        mask_inner = (((xx + 0.5 - cx) / rx) ** 2 + ((yy + 0.5 - cy) / ry) ** 2) <= 1.0
        mask = mask_inner.to(dtype)
    else:
        xi1 = int(math.floor(x1))
        yi1 = int(math.floor(y1))
        xi2 = int(math.ceil(x2))
        yi2 = int(math.ceil(y2))
        xi1 = max(0, min(xi1, W))
        yi1 = max(0, min(yi1, H))
        xi2 = max(0, min(xi2, W))
        yi2 = max(0, min(yi2, H))
        if xi2 > xi1 and yi2 > yi1:
            mask[yi1:yi2, xi1:xi2] = 1.0

    feather = max(0.0, float(feather))
    if feather > 0.0:
        sigma = feather * max(width, height, 1.0)
        if sigma > 0.0:
            kernel = max(3, int(math.ceil(sigma * 6.0)))
            if kernel % 2 == 0:
                kernel += 1
            mask = mask.unsqueeze(0).unsqueeze(0)
            mask = _gaussian_blur_2d(mask, (kernel, kernel), sigma)
            mask = mask.squeeze(0).squeeze(0)
            max_val = mask.max()
            if max_val > 0:
                mask = mask / max_val
    if invert:
        mask = 1.0 - mask
    mask = mask.clamp(0.0, 1.0)

    return mask.unsqueeze(0).unsqueeze(-1)
# endregion
