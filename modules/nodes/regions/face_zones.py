"""Facial zones (forehead, under-eyes, cheeks, folds, chin) at the source size, for shading reads."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.detection.build_overlay import outline_region_masks, region_mask_preview
from ...utils.helpers.face.face_align import SELECT_POLICIES
from ...utils.helpers.face.face_zones import face_zones
from ...utils.helpers.face.insightface_onnx import available_packs
from ...utils.helpers.logic import normalize_output_image
from ...utils.helpers.ui import create_cached_compare_node
from ...utils.image_regions import single_image


class LF_FaceZones:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'image': (Input.IMAGE, {'tooltip': 'Exactly one image; one face in it is zoned.'}),
            'model_pack': (available_packs(), {
                'tooltip': 'InsightFace pack folder under models/insightface (detector and 1k3d68 landmarks).'}),
            'select': (list(SELECT_POLICIES), {
                'default': 'largest', 'tooltip': 'Which face when several are found: largest, nearest the centre or most confident.'}),
            'det_size': (Input.INTEGER, {'default': 1280, 'min': 160, 'max': 2048, 'step': 32,
                                         'tooltip': 'Detector canvas; raise it for small faces in large frames.'}),
            'score_threshold': (Input.FLOAT, {'default': 0.5, 'min': 0.05, 'max': 0.99, 'step': 0.01,
                                              'tooltip': 'Minimum detector confidence.'}),
        }, 'optional': {'ui_widget': (Input.LF_COMPARE, {'default': {}})},
            'hidden': {'node_id': 'UNIQUE_ID'}}

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    RETURN_TYPES = (Input.MASK, Input.JSON, Input.IMAGE)
    RETURN_NAMES = ('masks', 'metadata', 'overlay')
    OUTPUT_IS_LIST = (False, False, False)
    OUTPUT_TOOLTIPS = ('Disjoint zone masks at the source size: under_eyes, cheeks, folds, forehead, chin.',
                       'lf.text-region-masks.v1 document with a face_zones block (box, score, landmarks).',
                       'The image with the zones outlined.')

    def on_exec(self, image=None, model_pack=None, select='largest', det_size=1280, score_threshold=0.5, **kwargs):
        source = single_image(image, 'image')
        masks, document = face_zones(source, model_pack, select=select, det_size=int(det_size),
                                     score_threshold=float(score_threshold))
        overlay = outline_region_masks(source, masks)
        nodes = [create_cached_compare_node(source, overlay, index=0,
                                            title=f"{document['face_zones']['faces_found']} face(s) found | "
                                                  f"score {document['face_zones']['score']:.3f}")]
        for index, record in enumerate(document['mask_sets'][0]['regions']):
            nodes.append(create_cached_compare_node(region_mask_preview(source, masks[index]), source,
                                                    index=index + 1, title=f"{record['id']} | {record['area']} px"))
        payload = {'dataset': {'nodes': nodes}, 'metadata': document}
        safe_send_sync('facezones', payload, kwargs.get('node_id'))
        return {'ui': {'lf_output': [payload]},
                'result': (masks, document, normalize_output_image([overlay])[0][0])}


NODE_CLASS_MAPPINGS = {'LF_FaceZones': LF_FaceZones}
NODE_DISPLAY_NAME_MAPPINGS = {'LF_FaceZones': 'Face Zones'}
