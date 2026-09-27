"""Headless named crop editing; the existing editor owns the visual experience."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.logic import normalize_output_image
from ...utils.image_regions import extract_image_regions, compose_image_regions


class LF_ExtractImageRegions:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'image': (Input.IMAGE, {'tooltip': 'Exactly one RGB/RGBA source image.'}),
            'regions': (Input.JSON, {'tooltip': 'Object with ordered regions: [{id,label,rect:[x,y,width,height]}]. No overlaps.'}),
            'canvas_size': (Input.INTEGER, {'default': 512, 'min': 1, 'max': 4096,
                                          'tooltip': 'Square editing canvas; each crop fits without stretching, with edge padding.'}),
        }}

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE, Input.JSON, Input.JSON)
    RETURN_NAMES = ('images', 'image_list', 'layout', 'editor_config')
    OUTPUT_IS_LIST = (False, True, False, False)
    OUTPUT_TOOLTIPS = ('All ordered region canvases in one compatible batch.',
                       'Ordered individual region canvases.',
                       'Source rectangles and canvas content rectangles for composition.',
                       'Named image_entries configuration for the image editing breakpoint.')

    def on_exec(self, image, regions, canvas_size=512):
        images, layout, config = extract_image_regions(image, regions, canvas_size)
        batches, image_list = normalize_output_image(images)
        return (batches[0], image_list, layout, config)


class LF_ComposeImageRegions:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'original': (Input.IMAGE, {'tooltip': 'Exact single source image used for extraction; alpha is retained.'}),
            'edited': (Input.IMAGE, {'tooltip': 'Edited canvases in validated original entry order.'}),
            'original_regions': (Input.IMAGE, {'tooltip': 'Breakpoint orig_image_list, in the same order; required for local edit deltas.'}),
            'layout': (Input.JSON, {'tooltip': 'Layout returned by Extract Image Regions.'}),
        }}

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    RETURN_TYPES = (Input.IMAGE, Input.IMAGE)
    RETURN_NAMES = ('image', 'image_list')
    OUTPUT_IS_LIST = (False, True)
    OUTPUT_TOOLTIPS = ('Original image with region RGB edit deltas; alpha and untouched pixels retained.',
                       'Single-item list containing the composed image.')

    def on_exec(self, original, edited, original_regions, layout):
        result = compose_image_regions(original, edited, original_regions, layout)
        batches, image_list = normalize_output_image([result])
        return (batches[0], image_list)


NODE_CLASS_MAPPINGS = {'LF_ExtractImageRegions': LF_ExtractImageRegions,
                       'LF_ComposeImageRegions': LF_ComposeImageRegions}
NODE_DISPLAY_NAME_MAPPINGS = {'LF_ExtractImageRegions': 'Extract Image Regions',
                              'LF_ComposeImageRegions': 'Compose Image Regions'}
