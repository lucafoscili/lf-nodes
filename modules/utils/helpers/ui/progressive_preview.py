import re
from typing import Callable, Dict, List, Optional, Tuple

import torch
import torch.nn.functional as F

from server import PromptServer

from ...helpers.api import get_resource_url
from ...helpers.comfy import resolve_filepath
from ...helpers.conversion import tensor_to_pil
from .create_compare_node import create_compare_node


def prepare_preview_destination(
    node_id: Optional[str],
    index: int,
    image: torch.Tensor,
    *,
    label: str = "preview",
    filename_prefix: str = "preview",
) -> Dict[str, str]:
    """Create a deterministic destination for preview assets."""
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


def save_preview_image(
    tensor: torch.Tensor,
    destination: Dict[str, str],
    *,
    target_size: Optional[Tuple[int, int]] = None,
    max_long_edge: int = 512,
    resource_type: str = "temp",
) -> str:
    """Persist a preview tensor and return its resource URL."""
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


class ComparePreviewStream:
    """Utility to manage progressive compare previews for LF widgets."""

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

    @staticmethod
    def _get_default_sender() -> Optional[Callable[[str, dict], None]]:
        try:
            return PromptServer.instance.send_sync
        except Exception:  # pragma: no cover - safety for test environments
            return None

    @property
    def compare_node(self) -> Optional[dict]:
        return self._compare_node

    def save_preview(
        self,
        tensor: torch.Tensor,
        *,
        target_size: Optional[Tuple[int, int]] = None,
    ) -> str:
        return save_preview_image(
            tensor,
            self._preview_destination,
            target_size=target_size,
            max_long_edge=self.max_long_edge,
            resource_type=self.resource_type,
        )

    def update_compare(
        self,
        after_url: str,
        *,
        debug_url: Optional[str] = None,
        title: Optional[str] = None,
    ) -> dict:
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

    def finalize(
        self,
        after_url: str,
        *,
        debug_url: Optional[str] = None,
        title: Optional[str] = None,
        emit: bool = True,
    ) -> dict:
        node = self.update_compare(after_url, debug_url=debug_url, title=title)
        if emit:
            self.emit()
        return node
