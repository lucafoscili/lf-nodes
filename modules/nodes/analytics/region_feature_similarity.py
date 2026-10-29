"""Region comparison of core CLIPVisionEncode outputs; never loads a model."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
from ...utils.helpers.comfy import safe_send_sync
from ...utils.helpers.torch.region_feature_similarity import compare_region_features


class LF_RegionFeatureSimilarity:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'features_a': (Input.CLIP_VISION_OUTPUT, {
                'tooltip': 'Core CLIPVisionEncode output for A; pooled-only outputs must encode ordered region crops.'}),
            'features_b': (Input.CLIP_VISION_OUTPUT, {
                'tooltip': 'Core CLIPVisionEncode output for B using the same model and crop setting.'}),
            'masks': (Input.MASK, {
                'tooltip': 'Text Region Masks batch/list: one shared set or two sets in A/B order.'}),
            'metadata': (Input.JSON, {
                'tooltip': 'Matching lf.text-region-masks.v1 metadata, in the same order as masks.'}),
            'model_file': (Input.STRING, {
                'default': 'dino_v3_vit_h.safetensors',
                'tooltip': 'Filename selected by CLIPVisionLoader, recorded as supplied by the workflow.'}),
            'crop': (['none', 'center'], {
                'default': 'none', 'tooltip': 'Must match both CLIPVisionEncode crop controls; none retains the full image.'}),
        }, 'optional': {'ui_widget': (Input.LF_TREE, {'default': {}})},
            'hidden': {'node_id': 'UNIQUE_ID'}}

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    RETURN_TYPES = (Input.JSON,)
    RETURN_NAMES = ('similarity',)
    OUTPUT_IS_LIST = (False,)
    OUTPUT_TOOLTIPS = ('Per-region feature cosine similarity, model filename and pooling method.',)

    def on_exec(self, features_a=None, features_b=None, masks=None, metadata=None,
                model_file='dino_v3_vit_h.safetensors', crop='none', **kwargs):
        similarity = compare_region_features(features_a, features_b, masks, metadata,
                                             model_file, crop)
        details = []
        for index, row in enumerate(similarity['regions']):
            score = row['similarity']
            label = f"{row['id']}: cosine {score:.4f}" if score is not None else f"{row['id']}: N/A"
            if row.get('warning'):
                label += f" | {row['warning']}"
            details.append({'id': str(index), 'value': label, 'children': [
                {'id': f'{index}_{key}', 'value': f'{key}: {value}'}
                for key, value in row.items()]})
        payload = {'similarity': similarity, 'dataset': {'nodes': details}}
        safe_send_sync('regionfeaturesimilarity', payload, kwargs.get('node_id'))
        return {'ui': {'lf_output': [payload]}, 'result': (similarity,)}


NODE_CLASS_MAPPINGS = {'LF_RegionFeatureSimilarity': LF_RegionFeatureSimilarity}
NODE_DISPLAY_NAME_MAPPINGS = {'LF_RegionFeatureSimilarity': 'Region Feature Similarity'}
