"""Headless source-owned layer editing; the existing editor owns the UI."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.logic import normalize_output_image
from ...utils.image_layers import load_image_layers, compose_image_layers


class LF_LoadImageLayers:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'manifest': (Input.JSON, {
                'tooltip': 'Object with root and ordered layers: [{id,label,file,sha256?,rect:[x,y,width,height]}].',
            }),
            'canvas_size': (Input.INTEGER, {
                'default': 512, 'min': 1, 'max': 4096,
                'tooltip': 'Square RGBA editing canvas; each native layer fits without stretching.',
            }),
        }, 'optional': {
            'include_masks': (Input.BOOLEAN, {
                'default': False, 'tooltip': 'Add cut-mask canvases: white keeps coverage, black cuts, gray partially keeps.',
            }),
            'base': (Input.IMAGE, {'tooltip': 'One base image; supply together with base_regions to edit it in the same session.'}),
            'base_regions': (Input.JSON, {'tooltip': 'Non-overlapping base regions: {regions:[{id,label,rect:[x,y,width,height]}]}.'}),
        }}

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.JSON, Input.JSON, Input.IMAGE)
    RETURN_NAMES = ('images', 'image_list', 'layout', 'editor_config', 'source_layers')
    OUTPUT_IS_LIST = (False, True, False, False, True)
    OUTPUT_TOOLTIPS = (
        'All ordered RGBA editing canvases in one compatible batch.',
        'Ordered individual RGBA editing canvases.',
        'Layer order, target rectangles, native sizes and content rectangles for composition.',
        'Named image_entries configuration for the image editing breakpoint.',
        'Authoritative ordered native-size RGBA sources; connect directly to Compose Image Layers.',
    )

    def on_exec(self, manifest, canvas_size=512, include_masks=False, base=None, base_regions=None):
        images, layout, config, sources = load_image_layers(
            manifest, canvas_size, include_masks, base, base_regions)
        batches, image_list = normalize_output_image(images)
        return (batches[0], image_list, layout, config, sources)


class LF_ComposeImageLayers:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'base': (Input.IMAGE, {'tooltip': 'Exactly one RGB/RGBA base atlas.'}),
            'edited': (Input.IMAGE, {'tooltip': 'Edited canvases in validated original entry order.'}),
            'original_layers': (Input.IMAGE, {
                'tooltip': 'Breakpoint orig_image_list, in the same order; required for local edit deltas.',
            }),
            'source_layers': (Input.IMAGE, {
                'tooltip': 'Native RGBA source_layers returned by Load Image Layers.',
            }),
            'layout': (Input.JSON, {'tooltip': 'Layout returned by Load Image Layers.'}),
        }, 'optional': {
            'base_mask': (Input.MASK, {'tooltip': 'Base-region RGB edit coverage: white permits edits, black preserves the original base.'}),
        }}

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.IMAGE)
    RETURN_NAMES = ('atlas', 'atlas_list', 'layer_images')
    OUTPUT_IS_LIST = (False, True, True)
    OUTPUT_TOOLTIPS = (
        'Pillow-compatible RGBA atlas with restored layers alpha-composited in manifest order.',
        'Single-item list containing the composed atlas.',
        'Ordered native-size RGBA layer images with RGB edits and original coverage, optionally reduced by cut masks.',
    )

    def on_exec(self, base, edited, original_layers, source_layers, layout, base_mask=None):
        atlas, layers = compose_image_layers(
            base, edited, original_layers, source_layers, layout, base_mask)
        batches, atlas_list = normalize_output_image([atlas])
        return (batches[0], atlas_list, layers)


NODE_CLASS_MAPPINGS = {
    'LF_LoadImageLayers': LF_LoadImageLayers,
    'LF_ComposeImageLayers': LF_ComposeImageLayers,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    'LF_LoadImageLayers': 'Load Image Layers',
    'LF_ComposeImageLayers': 'Compose Image Layers',
}
