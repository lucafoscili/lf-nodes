"""Region comparison of core CLIPVisionEncode outputs; never loads a model."""
from . import CATEGORY
from ...utils.constants import FUNCTION, Input
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
        }}

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    INPUT_IS_LIST = True
    RETURN_TYPES = (Input.JSON,)
    RETURN_NAMES = ('similarity',)
    OUTPUT_IS_LIST = (False,)
    OUTPUT_TOOLTIPS = ('Per-region feature cosine similarity, model filename and pooling method.',)

    def on_exec(self, features_a=None, features_b=None, masks=None, metadata=None,
                model_file='dino_v3_vit_h.safetensors', crop='none'):
        return (compare_region_features(features_a, features_b, masks, metadata,
                                        model_file, crop),)


NODE_CLASS_MAPPINGS = {'LF_RegionFeatureSimilarity': LF_RegionFeatureSimilarity}
NODE_DISPLAY_NAME_MAPPINGS = {'LF_RegionFeatureSimilarity': 'Region Feature Similarity'}
