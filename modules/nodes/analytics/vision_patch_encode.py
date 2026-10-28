"""CLIPVisionEncode drop-in for DINOv3, whose core encode path raises; never loads a model."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.torch.vision_patch_encode import CROPS, encode_vision_patches, vision_encoding_preview


class LF_VisionPatchEncode:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'clip_vision': (Input.CLIP_VISION, {
                'tooltip': 'Model from core CLIPVisionLoader, e.g. dino_v3_vit_h.safetensors.'}),
            'image': (Input.IMAGE, {'tooltip': 'Image or batch to encode.'}),
            'crop': (list(CROPS), {
                'tooltip': 'As core CLIPVisionEncode: center crops the square, none stretches the full image.'}),
        }, 'optional': {'ui_widget': (Input.LF_COMPARE, {'default': {}})},
            'hidden': {'node_id': 'UNIQUE_ID'}}

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = (Input.CLIP_VISION_OUTPUT,)
    RETURN_NAMES = ('clip_vision_output',)
    OUTPUT_IS_LIST = (False,)
    OUTPUT_TOOLTIPS = ('Core CLIP_VISION_OUTPUT with patch tokens (last_hidden_state), image_embeds and image_sizes.',)

    def on_exec(self, clip_vision=None, image=None, crop='center', **kwargs):
        output, encoded = encode_vision_patches(clip_vision, image, crop, return_preview=True)
        payload = vision_encoding_preview(clip_vision, image, crop, output, encoded)
        safe_send_sync('visionpatchencode', payload, kwargs.get('node_id'))
        return {'ui': {'lf_output': [payload]}, 'result': (output,)}


NODE_CLASS_MAPPINGS = {'LF_VisionPatchEncode': LF_VisionPatchEncode}
NODE_DISPLAY_NAME_MAPPINGS = {'LF_VisionPatchEncode': 'Vision Patch Encode'}
