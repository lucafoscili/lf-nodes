import torch

# region normalize_output_mask
def normalize_output_mask(mask_input):
    """
    Normalize mask tensors into grouped batch and list formats.

    Accepts single tensors, batched tensors, or iterables of tensors and
    returns:
      - batch_list: list of tensors grouped by spatial resolution, each with
        shape [B, H, W].
      - mask_list: list of tensors each with shape [1, H, W].
    """
    if isinstance(mask_input, (list, tuple)):
        if not mask_input:
            raise ValueError("Mask input is empty.")
        candidates = list(mask_input)
    elif torch.is_tensor(mask_input):
        candidates = [mask_input]
    else:
        raise TypeError("Unsupported input type for mask normalization.")

    mask_list = []
    for mask in candidates:
        if not torch.is_tensor(mask):
            raise TypeError("Mask entries must be tensors.")

        if mask.dim() == 4:
            # Interpret as batched [B, C, H, W] or [B, H, W, C].
            if mask.shape[1] == 1 or mask.shape[-1] == 1:
                if (
                    mask.shape[1] == 1
                    and mask.shape[-1] == 1
                    and mask.shape[2] != 1
                ):
                    raise ValueError(
                        "A 4D mask with singleton dimensions at both channel "
                        "positions is ambiguous; provide explicit [B,1,H,W] "
                        "or [B,H,W,1] geometry."
                    )
                if mask.shape[1] == 1:
                    batches = mask[:, 0]
                else:
                    batches = mask[..., 0]
                for item in batches:
                    mask_list.append(item.unsqueeze(0).contiguous().float())
            else:
                raise ValueError(
                    "A 4D mask must use a singleton channel dimension in "
                    f"[B,1,H,W] or [B,H,W,1] layout; got {tuple(mask.shape)}."
                )
        elif mask.dim() == 3:
            if mask.shape[0] != 1:
                for item in mask:
                    mask_list.append(item.unsqueeze(0).contiguous().float())
            else:
                mask_list.append(mask.contiguous().float())
        elif mask.dim() == 2:
            mask_list.append(mask.unsqueeze(0).contiguous().float())
        else:
            raise ValueError(f"Unsupported mask tensor shape: {mask.shape}")

    if not mask_list:
        raise ValueError("Mask input did not contain any masks.")

    resolution_groups = {}
    for mask in mask_list:
        h, w = mask.shape[1:]
        key = (h, w, mask.dtype, str(mask.device))
        resolution_groups.setdefault(key, []).append(mask)

    batch_list = []
    for masks in resolution_groups.values():
        if len(masks) > 1:
            batch_list.append(torch.cat(masks, dim=0))
        else:
            batch_list.append(masks[0])

    return batch_list, mask_list
# endregion
