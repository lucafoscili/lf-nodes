"""One existing GLB plus one texture, returned in memory for stock 3D viewers."""
from io import BytesIO
from pathlib import Path
import hashlib

import folder_paths
import torch

from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.glb_texture import apply_texture_to_glb
from ...utils.helpers.logic.normalize_input_image import normalize_input_image
from ...utils.helpers.conversion.tensor_to_pil import tensor_to_pil


def _single(value, name):
    while isinstance(value, (list, tuple)):
        if len(value) != 1:
            raise ValueError(f'{name} requires exactly one value; lists are not supported.')
        value = value[0]
    return value


def _source_path(source):
    source = _single(source, 'source_glb')
    if not isinstance(source, str) or not source.strip():
        raise ValueError('source_glb requires an existing GLB filepath.')
    # Explicit external paths are the read-only LF file-input seam; relative
    # names use Core annotation/containment rules without bypassing them.
    path = Path(source)
    if not path.is_absolute():
        path = Path(folder_paths.get_annotated_filepath(source))
    if path.suffix.lower() != '.glb' or not path.is_file():
        raise ValueError('source_glb must identify an existing .glb file.')
    return path


class LF_ApplyTextureToGLB:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'source_glb': (Input.STRING, {'default': '', 'tooltip': 'Existing absolute GLB filepath or Comfy input filename. Read only; no source copies.'}),
            'texture': (Input.IMAGE, {'tooltip': 'Exactly one RGB/RGBA texture. Preserves supplied alpha and material alpha mode.'}),
            'material_index': (Input.INTEGER, {'default': 0, 'min': 0, 'tooltip': 'Replace only this material base-color map; shared maps on other materials stay unchanged.'}),
        }}

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    RETURN_TYPES = (Input.FILE_3D_GLB,)
    RETURN_NAMES = ('glb',)
    OUTPUT_IS_LIST = (False,)
    OUTPUT_TOOLTIPS = ('In-memory GLB with the selected base-color texture; geometry, UVs, skins and animations retained.',)

    @classmethod
    def IS_CHANGED(cls, source_glb, **kwargs):
        return hashlib.sha256(_source_path(source_glb).read_bytes()).hexdigest()

    def on_exec(self, source_glb, texture, material_index=0):
        source = _single(source_glb, 'source_glb')
        material = _single(material_index, 'material_index')
        images = normalize_input_image(texture)
        if len(images) != 1:
            raise ValueError('texture requires exactly one image; batches/lists are not supported.')
        if type(material) is not int or material < 0:
            raise ValueError('material_index must be a non-negative integer.')
        path = _source_path(source)
        image = images[0].detach().to(dtype=torch.float32)
        if not torch.isfinite(image).all():
            raise ValueError('texture pixels must be finite.')
        result = apply_texture_to_glb(path.read_bytes(), tensor_to_pil(image), material)
        from comfy_api.latest import Types
        return (Types.File3D(BytesIO(result), file_format='glb'),)


NODE_CLASS_MAPPINGS = {'LF_ApplyTextureToGLB': LF_ApplyTextureToGLB}
NODE_DISPLAY_NAME_MAPPINGS = {'LF_ApplyTextureToGLB': 'Apply Texture to GLB'}
