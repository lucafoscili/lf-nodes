"""ArcFace identity cosine between Face Align crops; InsightFace ONNX packs from ComfyUI's models."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.face.face_align import face_identity
from ...utils.helpers.face.insightface_onnx import available_packs
from ...utils.helpers.logic import normalize_input_image, normalize_json_input, normalize_list_to_value


class LF_FaceIdentity:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'image': (Input.IMAGE, {'tooltip': 'Aligned crops from Face Align, in its order.'}),
            'metadata': (Input.JSON, {'tooltip': 'The metadata output of the same Face Align.'}),
            'model_pack': (available_packs(), {
                'tooltip': 'InsightFace pack whose ArcFace model embeds the faces (antelopev2: glintr100; buffalo_l: w600k_r50).'}),
            'reference_index': (Input.INTEGER, {'default': 0, 'min': 0, 'max': 4096,
                                                'tooltip': 'The face every other face is scored against.'}),
        }, 'optional': {'ui_widget': (Input.LF_TREE, {'default': {}})},
            'hidden': {'node_id': 'UNIQUE_ID'}}

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    RETURN_TYPES = (Input.JSON,)
    RETURN_NAMES = ('identity',)
    OUTPUT_IS_LIST = (False,)
    OUTPUT_TOOLTIPS = ('ArcFace cosine of each face against the reference (1 = same embedding), and the full matrix.',)

    def on_exec(self, image=None, metadata=None, model_pack=None, reference_index=0, **kwargs):
        images = normalize_input_image(image)
        document = normalize_json_input(normalize_list_to_value(metadata))
        identity = face_identity(images, document, normalize_list_to_value(model_pack),
                                 int(normalize_list_to_value(reference_index)))
        nodes = [{'id': str(pair['image']),
                  'value': f"image {pair['image']} vs {pair['reference']}: cosine {pair['cosine']:.4f}"}
                 for pair in identity['pairs']]
        payload = {'identity': identity, 'dataset': {'nodes': nodes}}
        safe_send_sync('faceidentity', payload, kwargs.get('node_id'))
        return {'ui': {'lf_output': [payload]}, 'result': (identity,)}


NODE_CLASS_MAPPINGS = {'LF_FaceIdentity': LF_FaceIdentity}
NODE_DISPLAY_NAME_MAPPINGS = {'LF_FaceIdentity': 'Face Identity'}
