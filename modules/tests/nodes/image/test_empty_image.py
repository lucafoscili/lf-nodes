from __future__ import annotations

from modules.nodes.image.empty_image import LF_EmptyImage
from modules.utils.constants import Input


def test_empty_image_declares_both_returned_image_outputs() -> None:
    assert LF_EmptyImage.RETURN_NAMES == ("image", "image_list")
    assert LF_EmptyImage.RETURN_TYPES == (Input.IMAGE, Input.IMAGE)
    assert LF_EmptyImage.OUTPUT_IS_LIST == (False, True)
