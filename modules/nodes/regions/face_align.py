"""Landmark-aligned face crops with region masks; InsightFace ONNX packs from ComfyUI's models."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.detection.build_overlay import outline_region_masks
from ...utils.helpers.face.face_align import SELECT_POLICIES, align_faces, mask_items
from ...utils.helpers.face.insightface_onnx import available_packs
from ...utils.helpers.logic import normalize_input_image, normalize_list_to_value, normalize_output_image
from ...utils.helpers.ui import create_cached_compare_node


class LF_FaceAlign:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'image': (Input.IMAGE, {'tooltip': 'One or more images; one face is aligned from each.'}),
            'model_pack': (available_packs(), {
                'tooltip': 'InsightFace pack folder under models/insightface (detector, 1k3d68 landmarks, ArcFace).'}),
            'select': (list(SELECT_POLICIES), {
                'default': 'center', 'tooltip': 'Which face when several are found: nearest the centre, largest or most confident.'}),
            'crop_size': (Input.INTEGER, {'default': 512, 'min': 64, 'max': 4096, 'step': 16,
                                          'tooltip': 'Side of the square aligned crop.'}),
            'face_scale': (Input.FLOAT, {'default': 0.5, 'min': 0.1, 'max': 1.0, 'step': 0.01,
                                         'tooltip': "ArcFace's 112 template as a share of the crop; lower keeps more hair."}),
            'det_size': (Input.INTEGER, {'default': 640, 'min': 160, 'max': 2048, 'step': 32,
                                         'tooltip': 'Detector canvas; raise it for small faces in large frames.'}),
            'score_threshold': (Input.FLOAT, {'default': 0.5, 'min': 0.05, 'max': 0.99, 'step': 0.01,
                                              'tooltip': 'Minimum detector confidence.'}),
        }, 'optional': {
            'extra_masks': (Input.MASK, {
                'tooltip': 'Workflow masks at source size, region-major (all images for region 0, then 1...), warped with the face.'}),
            'extra_ids': (Input.STRING, {'default': 'hair', 'tooltip': 'Comma-separated IDs, one per extra mask region.'}),
            'extra_priority': (Input.FLOAT, {'default': 35, 'min': -1000, 'max': 1000, 'step': 1,
                                             'tooltip': 'Overlap priority of extra regions: skin 0, brows 30, eyes and lips 40.'}),
            'ui_widget': (Input.LF_COMPARE, {'default': {}}),
        }, 'hidden': {'node_id': 'UNIQUE_ID'}}

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    RETURN_TYPES = (Input.IMAGE, Input.MASK, Input.JSON, Input.IMAGE, Input.MASK)
    RETURN_NAMES = ('image', 'masks', 'metadata', 'image_list', 'mask_list')
    OUTPUT_IS_LIST = (False, False, False, True, True)
    OUTPUT_TOOLTIPS = ('Aligned square crops, one per input image.',
                       'Disjoint region masks on the crops, image-major then region-table order.',
                       'lf.text-region-masks.v1 document with a face_alignment block (boxes, points, transforms).',
                       'Aligned crops as an ordered list.',
                       'Region masks as ordered [1,H,W] items.')

    def on_exec(self, image=None, model_pack=None, select='center', crop_size=512, face_scale=0.5, det_size=640,
                score_threshold=0.5, extra_masks=None, extra_ids='hair', extra_priority=35, **kwargs):
        images = normalize_input_image(image)
        if not images:
            raise ValueError('Face Align requires at least one image.')
        extras = mask_items(extra_masks)
        crops, masks, metadata, mask_list = align_faces(
            images, normalize_list_to_value(model_pack),
            crop_size=int(normalize_list_to_value(crop_size)), face_scale=float(normalize_list_to_value(face_scale)),
            select=normalize_list_to_value(select), det_size=int(normalize_list_to_value(det_size)),
            score_threshold=float(normalize_list_to_value(score_threshold)), extra_masks=extras,
            extra_ids=normalize_list_to_value(extra_ids) or '', extra_priority=float(normalize_list_to_value(extra_priority)))
        regions = len(metadata['regions'])
        nodes = []
        for index, crop in enumerate(crops):
            face = metadata['face_alignment']['faces'][index]
            outlined = outline_region_masks(crop, masks[index * regions:(index + 1) * regions])
            nodes.append(create_cached_compare_node(
                crop, outlined, index=index,
                title=f"image {index} | score {face['score']:.3f} | {face['faces_found']} face(s) found"))
        payload = {'dataset': {'nodes': nodes}, 'metadata': metadata}
        safe_send_sync('facealign', payload, kwargs.get('node_id'))
        batches, image_list = normalize_output_image(crops)
        return {'ui': {'lf_output': [payload]}, 'result': (batches[0], masks, metadata, image_list, mask_list)}


NODE_CLASS_MAPPINGS = {'LF_FaceAlign': LF_FaceAlign}
NODE_DISPLAY_NAME_MAPPINGS = {'LF_FaceAlign': 'Face Align'}
