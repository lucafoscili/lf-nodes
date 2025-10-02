import re
from typing import Callable, Dict, List, Optional, Tuple

import torch
import torch.nn.functional as F

from server import PromptServer

from ...helpers.api import get_resource_url
from ...helpers.comfy import resolve_filepath
from ...helpers.conversion import tensor_to_pil
from .create_compare_node import create_compare_node

# region prepare_preview_destination
def prepare_preview_destination(
    node_id: Optional[str],
    index: int,
    image: torch.Tensor,
    *,
    label: str = "preview",
    filename_prefix: str = "preview",
) -> Dict[str, str]:
    """
    Create a deterministic filesystem destination for a preview image.

    This function builds a safe, human-readable filename prefix from the
    provided node identifier, label, and index, then resolves a final file
    path using the project's resolve_filepath utility.

    Parameters
    - node_id (Optional[str]): Identifier for the node producing the preview.
        If falsy, the literal string "node" is used. Any characters outside
        [0-9A-Za-z_-] are replaced with underscores to form a filesystem-safe
        token.
    - index (int): Zero-based index of the preview. Note that the produced
        filename uses index + 1 (i.e., 1-based numbering) for readability.
    - image (torch.Tensor): Image tensor passed through to resolve_filepath;
        used by that helper to determine file extension/format or other image-
        dependent logic.
    - label (str, optional): Short label inserted into the filename (default "preview").
    - filename_prefix (str, optional): Top-level prefix for the generated filename
        (default "preview").

    Behavior
    - Constructs a prefix of the form:
            "{filename_prefix}_{label}_{safe_node}_{index + 1}"
        where safe_node is the sanitized node_id (or "node" if node_id is falsy).
    - Calls resolve_filepath(filename_prefix=prefix, image=image, add_counter=False)
        and returns the resulting file, subfolder, and filename values.

    Returns
    - Dict[str, str]: A mapping with keys:
            - "file": full resolved output path
            - "subfolder": subfolder component chosen by resolve_filepath
            - "filename": final filename (without subfolder)

    Notes
    - Deterministic: identical inputs will produce the same prefix and, subject
        to resolve_filepath behavior, the same resolved destination.
    - Any errors from resolve_filepath are propagated to the caller.
    """
    safe_node = re.sub(r"[^0-9A-Za-z_-]", "_", str(node_id) if node_id else "node")
    prefix = f"{filename_prefix}_{label}_{safe_node}_{index + 1}"
    output_file, subfolder, filename = resolve_filepath(
        filename_prefix=prefix,
        image=image,
        add_counter=False,
    )
    return {
        "file": output_file,
        "subfolder": subfolder,
        "filename": filename,
    }
# endregion

# region save_preview_image
def save_preview_image(
    tensor: torch.Tensor,
    destination: Dict[str, str],
    *,
    target_size: Optional[Tuple[int, int]] = None,
    max_long_edge: int = 512,
    resource_type: str = "temp",
) -> str:
    """
    Persist a preview image tensor to disk (PNG) and return a resource URL.
    This function accepts a torch.Tensor representing an image (or a batch of images),
    normalizes and sanitizes it, optionally resizes it, converts it to a PIL image,
    saves it to the path specified in `destination["file"]`, and returns a resource
    URL constructed from `destination["subfolder"]` and `destination["filename"]`.

    Behavior details:
    - Accepted tensor shapes:
        - Single image: (H, W, C)
        - Batch: (B, H, W, C)
        If a 3-D tensor is provided it is treated as a single image and a batch
        dimension is added.
    - The tensor is detached and converted to float32. NaNs are set to 0.0,
        positive infinities to 1.0 and negative infinities to 0.0.
    - If `target_size` is provided as (target_h, target_w) and both dims > 0,
        the image is resized to that exact size using bicubic interpolation
        (antialiasing enabled).
    - After clamping values to [0.0, 1.0] and moving to CPU, if either image
        dimension exceeds `max_long_edge` the image is downscaled (preserving
        aspect ratio) so the longest edge equals `max_long_edge`.
    - The processed image is converted to a PIL Image via `tensor_to_pil` and
        saved as a PNG to `destination["file"]`.
    - The function returns the value of `get_resource_url(destination["subfolder"], destination["filename"], resource_type)`.

    Parameters:
            tensor (torch.Tensor): Image tensor in HWC or BHWC layout. Values are
                    expected in a 0.0-1.0 range but out-of-range values, NaNs and infinities
                    are handled.
            destination (Dict[str, str]): Destination metadata and path. Required keys:
                    - "file": filesystem path where the PNG will be written.
                    - "subfolder": subfolder identifier used to build the returned resource URL.
                    - "filename": filename identifier used to build the returned resource URL.
            target_size (Optional[Tuple[int, int]]): Optional (height, width) to resize
                    the image to before enforcing `max_long_edge`. If None or contains
                    non-positive values, no explicit target-size resize is performed.
            max_long_edge (int): Maximum allowed length (in pixels) of the image's
                    longer edge. If the image is larger, it is downscaled while preserving
                    aspect ratio. Set to a non-positive value to disable this behavior.
            resource_type (str): A string passed through to `get_resource_url` to
                    indicate the resource category/type (defaults to "temp").

    Returns:
            str: A resource URL returned by `get_resource_url(subfolder, filename, resource_type)`.

    Raises:
            KeyError: If `destination` is missing required keys ("file", "subfolder", "filename").
            OSError: If saving the image to the filesystem fails.
            TypeError: If `tensor` is not a torch.Tensor or has an unsupported shape.
            (Other exceptions may be raised by the underlying helpers `tensor_to_pil`,
             `F.interpolate`, or `get_resource_url`.)

    Notes:
            - If a batch (B, H, W, C) is provided, only a single image will be saved
                (the helper `tensor_to_pil` is expected to return a single PIL Image).
            - The function will overwrite any existing file at `destination["file"]`.
            - This function depends on the availability of torch, torchvision/F.interpolate,
                tensor_to_pil, and get_resource_url in the runtime.
    """
    if tensor.dim() == 3:
        tensor = tensor.unsqueeze(0)

    preview = tensor.detach().to(torch.float32)
    preview = torch.nan_to_num(preview, nan=0.0, posinf=1.0, neginf=0.0)

    if target_size and all(dim > 0 for dim in target_size):
        target_h, target_w = target_size
        if preview.shape[1] != target_h or preview.shape[2] != target_w:
            preview = F.interpolate(
                preview.permute(0, 3, 1, 2),
                size=(target_h, target_w),
                mode="bicubic",
                align_corners=False,
                antialias=True,
            ).permute(0, 2, 3, 1)

    preview = preview.clamp(0.0, 1.0).to("cpu")
    _, height, width, _ = preview.shape

    if max_long_edge and max(height, width) > max_long_edge:
        scale_factor = max_long_edge / max(height, width)
        new_h = max(1, int(round(height * scale_factor)))
        new_w = max(1, int(round(width * scale_factor)))
        preview = F.interpolate(
            preview.permute(0, 3, 1, 2),
            size=(new_h, new_w),
            mode="bicubic",
            align_corners=False,
            antialias=True,
        ).permute(0, 2, 3, 1)

    preview_pil = tensor_to_pil(preview)
    preview_pil.save(destination["file"], format="PNG")

    return get_resource_url(destination["subfolder"], destination["filename"], resource_type)
# endregion

class ComparePreviewStream:
    """
    Manage progressive "before / after" compare previews for LF widgets.
    This class centralizes the lifecycle of a progressive preview for a single
    item: preparing file destinations, saving the original input image, producing
    and saving intermediate/after previews, creating or updating the compare node
    dictionary used by the UI, and optionally emitting an event (via a sender
    function) to notify a front-end or server about dataset changes.

    Parameters
    - node_id (Optional[str]):
        Identifier of the node that will receive/update the compare preview.
        May be None for contexts where a node id is not available.
    - index (int):
        Index of this preview within the node's dataset (used to prepare
        unique file destinations and to populate the created compare node).
    - input_image (torch.Tensor):
        Tensor representing the input image. This is saved immediately (using
        save_preview_image) to the prepared input destination and its URL is
        stored on construction as input_url.
    - dataset (Dict[str, List[dict]]):
        The dataset structure that will hold compare node entries. The created
        or updated compare node dict is appended here when first created.
    - compare_nodes (List[dict]):
        A list reference used to collect/append the compare node dict created for
        this preview (useful for assembling a combined UI payload).
    - event (str):
        Event name to use when emitting updates via the sender function.
    - input_target_size (Tuple[int, int]):
        Target size (width, height) used when saving the input image.
    - filename_prefix (str, optional):
        Prefix to use when preparing filenames for preview and input images.
        Defaults to "preview".
    - resource_type (str, optional):
        Type/category of resource used when saving images (defaults to "temp").
    - max_long_edge (int, optional):
        Maximum allowed long edge used when saving preview images (defaults to 512).
    - send_fn (Optional[Callable[[str, dict], None]], optional):
        Optional function used to emit update events. If not provided, the class
        attempts to use PromptServer.instance.send_sync; if that is unavailable
        (e.g. in test environments), no sending will occur and emit() is a no-op.
    Attributes (not exhaustive)
    - node_id, index, dataset, compare_nodes, event, resource_type, max_long_edge:
        Mirrors of the constructor parameters.
    - _compare_node (Optional[dict]):
        The compare node dictionary once created. Remains None until update_compare
        is called the first time.
    - _preview_destination, _input_destination:
        Prepared file destinations (via prepare_preview_destination) used when
        saving preview and input images.
    - input_url (str):
        URL/path returned by saving the input image on initialization.
    - _send_fn:
        Resolved sender function (either the provided send_fn or the default).

    Key methods
    - save_preview(tensor: torch.Tensor, target_size: Optional[Tuple[int, int]] = None) -> str
        Save a tensor to the prepared preview destination and return its URL.
        Respects max_long_edge and resource_type provided at construction.
    - update_compare(after_url: str, debug_url: Optional[str] = None, title: Optional[str] = None) -> dict
        Create a compare node dictionary on first call (appending it to
        compare_nodes) or update the existing one. Updates the "before" (input)
        image URL, the "after" image URL, an optional debug image cell, and an
        optional title. Returns the compare node dict.
    - emit() -> None
        If a sender function is available, call it with the configured event
        name and a payload containing {"node": node_id, "dataset": dataset}.
    - finalize(after_url: str, debug_url: Optional[str] = None, title: Optional[str] = None, emit: bool = True) -> dict
        Convenience combining update_compare and an optional emit. Returns the
        (created or updated) compare node dict.

    Notes
    - The class depends on external helpers: prepare_preview_destination and
      save_preview_image (for file/URL handling) and optionally PromptServer for
      a default sender. Those are not implemented here.
    - If no sender function is available, emit() will silently do nothing.
    - The compare node structure conforms to the UI expected schema: cells
      containing "lfImage", "lfImage_after", and optionally "lfImage_debug".
    - Thread-safety is not guaranteed; if multiple threads/processes may update
      the same compare_nodes or dataset, external synchronization is required.

    Example (conceptual)
        cps = ComparePreviewStream(
            node_id="node-123",
            index=0,
            input_image=tensor_img,
            dataset=dataset_obj,
            compare_nodes=[],
            event="dataset_update",
            input_target_size=(640, 480),
        preview_url = cps.save_preview(some_tensor)
        cps.finalize(preview_url, title="Denoised")
    """
    def __init__(
        self,
        *,
        node_id: Optional[str],
        index: int,
        input_image: torch.Tensor,
        dataset: Dict[str, List[dict]],
        compare_nodes: List[dict],
        event: str,
        input_target_size: Tuple[int, int],
        filename_prefix: str = "preview",
        resource_type: str = "temp",
        max_long_edge: int = 512,
        send_fn: Optional[Callable[[str, dict], None]] = None,
    ) -> None:
        self.node_id = node_id
        self.index = index
        self.dataset = dataset
        self.compare_nodes = compare_nodes
        self.event = event
        self.resource_type = resource_type
        self.max_long_edge = max_long_edge
        self._compare_node: Optional[dict] = None

        self._preview_destination = prepare_preview_destination(
            node_id,
            index,
            input_image,
            label="preview",
            filename_prefix=filename_prefix,
        )
        self._input_destination = prepare_preview_destination(
            node_id,
            index,
            input_image,
            label="input",
            filename_prefix=filename_prefix,
        )

        self.input_url = save_preview_image(
            input_image,
            self._input_destination,
            target_size=input_target_size,
            max_long_edge=max_long_edge,
            resource_type=resource_type,
        )

        self._send_fn = send_fn or self._get_default_sender()

# region _get_default_sender
    @staticmethod
    def _get_default_sender() -> Optional[Callable[[str, dict], None]]:
        """
        Return the default sender callable from the PromptServer singleton, if available.

        This helper attempts to retrieve PromptServer.instance.send_sync and return it
        as the default synchronous sender function used by the UI. If any exception
        occurs (for example, PromptServer is not initialized in test or headless
        environments), the function returns None to provide a safe fallback.

        Returns:
            Optional[Callable[[str, dict], None]]: The synchronous send callable that
            accepts a prompt string and a metadata dict, or None if unavailable.

        Notes:
            - All exceptions are intentionally suppressed to avoid breaking callers in
              environments where the PromptServer is not present.
            - Intended for use as a safe default supplier for UI components that may
              run outside of the full application context.
        """
        try:
            return PromptServer.instance.send_sync
        except Exception:  # pragma: no cover - safety for test environments
            return None
# endregion        

    @property
    def compare_node(self) -> Optional[dict]:
        return self._compare_node

    def save_preview(
        self,
        tensor: torch.Tensor,
        *,
        target_size: Optional[Tuple[int, int]] = None,
    ) -> str:
        """
        Save a preview image from a torch Tensor to the node's configured preview destination.

        This method wraps the underlying save_preview_image utility, writing the provided
        tensor to self._preview_destination and applying any configured sizing behavior
        (self.max_long_edge and self.resource_type).

        Parameters
        - tensor (torch.Tensor): Image data to save. Expected to be a 2D or 3D image tensor,
            commonly in shape (C, H, W) or (H, W, C). Typical value types are floats in
            [0, 1] or uint8 in [0, 255]; the underlying saver will convert as needed.
        - target_size (Optional[Tuple[int, int]]): Exact output size as (width, height).
            If provided, the saved image will be resized to these dimensions. If None,
            resizing (if any) is governed by self.max_long_edge; if both are unspecified,
            the image is saved at its native resolution.

        Returns
        - str: Filesystem path to the saved preview image.

        Raises
        - Any exceptions raised by the underlying save_preview_image call (e.g. ValueError
            for invalid tensor shapes or OSError for filesystem errors).

        Example
        - saved_path = self.save_preview(tensor, target_size=(512, 512))
        """
        return save_preview_image(
            tensor,
            self._preview_destination,
            target_size=target_size,
            max_long_edge=self.max_long_edge,
            resource_type=self.resource_type,
        )

# region update_compare
    def update_compare(
        self,
        after_url: str,
        *,
        debug_url: Optional[str] = None,
        title: Optional[str] = None,
    ) -> dict:
        """
        Update or create a "compare" node representing a before/after image comparison.
        This method ensures that a compare node exists for the current instance and
        updates its image cells with the provided URLs. If a compare node does not
        already exist, a new one will be created via create_compare_node and appended
        to self.compare_nodes.

        Parameters:
        after_url : str
            URL (or identifier) of the "after" image to set on the compare node.
        debug_url : Optional[str], optional
            If provided, a debug image URL to set on the compare node. When creating a
            new node this value is passed to create_compare_node; when updating an
            existing node the "lfImage_debug" cell is created or overwritten only if
            debug_url is not None. If omitted (None) an existing debug cell is left
            unchanged.
        title : Optional[str], optional
            If provided, sets/overwrites the compare node's title/value on the existing
            node (or initial title when creating a new node).

        Behavior / Side effects:
        - If self._compare_node is None:
            - Calls create_compare_node(self.input_url, after_url, self.index,
              debug=debug_url, title=title) to create a new compare node.
            - Appends the newly created node to self.compare_nodes and stores it in
              self._compare_node.
        - If self._compare_node already exists:
            - Updates the "lfImage" cell to reference self.input_url (the "before"
              image).
            - Updates the "lfImage_after" cell to reference after_url.
            - If debug_url is provided, sets (or overwrites) the "lfImage_debug" cell to
              the debug URL.
            - If title is provided, updates the node's "value" to the title.
        - The method does not remove an existing "lfImage_debug" cell when debug_url
          is None; it only creates or overwrites when a value is provided.

        Returns:
        dict
            The compare node dictionary that was created or updated.

        Raises:
        Any exception raised by create_compare_node or by mutating the node structure
        may propagate (e.g., KeyError or whatever create_compare_node may raise).
        """
        if self._compare_node is None:
            self._compare_node = create_compare_node(
                self.input_url,
                after_url,
                self.index,
                debug=debug_url,
                title=title,
            )
            self.compare_nodes.append(self._compare_node)
        else:
            cells = self._compare_node["cells"]
            if "lfImage" in cells:
                cells["lfImage"]["lfValue"] = self.input_url
            cells["lfImage_after"]["lfValue"] = after_url
            if debug_url is not None:
                cells["lfImage_debug"] = {
                    "shape": "image",
                    "lfValue": debug_url,
                    "value": "",
                }
            if title:
                self._compare_node["value"] = title

        return self._compare_node

    def emit(self) -> None:
        if self._send_fn:
            self._send_fn(
                self.event,
                {
                    "node": self.node_id,
                    "dataset": self.dataset,
                },
            )
# endregion

# region finalize
    def finalize(
        self,
        after_url: str,
        *,
        debug_url: Optional[str] = None,
        title: Optional[str] = None,
        emit: bool = True,
    ) -> dict:
        """
        Finalize the progressive preview state and optionally emit an update.

        Parameters:
        after_url : str
            The URL of the "after" image to set in the comparison.
        debug_url : Optional[str], optional
            An optional debugging image URL to include in the comparison update.
        title : Optional[str], optional
            An optional title to associate with the updated node.
        emit : bool, optional
            If True (default), call self.emit() after updating the comparison; if False, do not emit.

        Returns:
        dict
            The node dictionary returned by self.update_compare(...) representing the updated node state.

        Notes:
        This method delegates the update work to self.update_compare(...) and, depending on the
        emit flag, triggers an emission side effect via self.emit(). It does not perform validation
        of the provided URLs; callers should ensure they are well-formed if necessary.
        """
        node = self.update_compare(after_url, debug_url=debug_url, title=title)
        if emit:
            self.emit()
        return node
# endregion