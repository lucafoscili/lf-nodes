"""Label precomputed detector masks without owning model execution."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.detection.build_overlay import region_mask_preview
from ...utils.helpers.detection.region_masks import text_region_masks
from ...utils.helpers.logic import normalize_input_image
from ...utils.helpers.ui import create_cached_compare_node


class LF_TextRegionMasks:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'image': (Input.IMAGE, {'tooltip': 'Source image(s), all with the same spatial size.'}),
            'masks': (Input.MASK, {'tooltip': 'Exactly N images × R regions, region-major: all images for each table row. SAM3 Detect: individual_masks=false.'}),
            'regions': (Input.JSON, {'tooltip': 'Ordered JSON array [{id,prompt,priority}]. Higher priority wins; ties retain earlier rows.'}),
        }, 'optional': {'ui_widget': (Input.LF_COMPARE, {'default': {}})},
            'hidden': {'node_id': 'UNIQUE_ID'}}

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    RETURN_TYPES = (Input.MASK, Input.JSON, Input.MASK)
    RETURN_NAMES = ('masks', 'metadata', 'mask_list')
    OUTPUT_IS_LIST = (False, False, True)
    OUTPUT_TOOLTIPS = ('Disjoint binary masks in image-major, then original region-table order.',
                       'Source size, region rows, image sets, areas, overlap losses and empty warnings.',
                       'All masks as ordered [1,H,W] list items, including empty regions.')

    def on_exec(self, image=None, masks=None, regions=None, **kwargs):
        result = text_region_masks(image, masks, regions)
        batch, metadata, _ = result
        images = normalize_input_image(image)
        nodes = []
        for entry in metadata['mask_sets']:
            source = images[entry['image_index']]
            for record in entry['regions']:
                index = len(nodes)
                label = f"{record['id']} | image {entry['image_index']} | area {record['area']} px"
                if record['empty']:
                    label += f" | N/A: {record['warning']}"
                nodes.append(create_cached_compare_node(
                    region_mask_preview(source, batch[index]), source,
                    index=index, title=label))
        payload = {'dataset': {'nodes': nodes}, 'metadata': metadata}
        safe_send_sync('textregionmasks', payload, kwargs.get('node_id'))
        return {'ui': {'lf_output': [payload]}, 'result': result}


NODE_CLASS_MAPPINGS = {'LF_TextRegionMasks': LF_TextRegionMasks}
NODE_DISPLAY_NAME_MAPPINGS = {'LF_TextRegionMasks': 'Text Region Masks'}
