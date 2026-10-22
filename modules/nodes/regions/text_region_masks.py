"""Label precomputed detector masks without owning model execution."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.detection.region_masks import text_region_masks


class LF_TextRegionMasks:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'image': (Input.IMAGE, {'tooltip': 'Source image(s), all with the same spatial size.'}),
            'masks': (Input.MASK, {'tooltip': 'Exactly N images × R regions, region-major: all images for each table row. SAM3 Detect: individual_masks=false.'}),
            'regions': (Input.JSON, {'tooltip': 'Ordered JSON array [{id,prompt,priority}]. Higher priority wins; ties retain earlier rows.'}),
        }}

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    RETURN_TYPES = (Input.MASK, Input.JSON, Input.MASK)
    RETURN_NAMES = ('masks', 'metadata', 'mask_list')
    OUTPUT_IS_LIST = (False, False, True)
    OUTPUT_TOOLTIPS = ('Disjoint binary masks in image-major, then original region-table order.',
                       'Source size, region rows, image sets, areas, overlap losses and empty warnings.',
                       'All masks as ordered [1,H,W] list items, including empty regions.')

    def on_exec(self, image=None, masks=None, regions=None):
        return text_region_masks(image, masks, regions)


NODE_CLASS_MAPPINGS = {'LF_TextRegionMasks': LF_TextRegionMasks}
NODE_DISPLAY_NAME_MAPPINGS = {'LF_TextRegionMasks': 'Text Region Masks'}
