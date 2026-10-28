"""Deterministic CPU encoder stand-in; no model weights or Comfy GPU imports.

The clip_vision stand-in carries exactly the fields the helper reads: model,
patcher, load_device, image_size, image_mean, image_std, model_type and
return_all_hidden_states. Its model mimics DINOv3's forward, returning
(sequence, None, pooled, None) with CLS, four registers, then 16-px patches.
Core's comfy.clip_vision, comfy.clip_model and comfy.model_management import
the GPU stack, so host modules are stubbed: Output as core's attribute bag,
a recording load_model_gpu, and a geometry-compatible stand-in for clip_preprocess
(the real preprocessing implementation and model loading run only live).
"""
import sys
import types
from types import SimpleNamespace

import pytest
import torch

from modules.nodes.analytics.vision_patch_encode import LF_VisionPatchEncode
from modules.nodes.analytics import vision_patch_encode as node_module
from modules.nodes.regions.text_region_masks import LF_TextRegionMasks
from modules.utils.helpers.torch.region_feature_similarity import compare_region_features
from modules.utils.helpers.torch.vision_patch_encode import vision_output_from_pixel_values
from modules.utils.helpers.ui import generated_preview


@pytest.fixture(autouse=True)
def preview_root(monkeypatch, tmp_path):
    monkeypatch.setattr(generated_preview, 'get_comfy_dir', lambda _kind: str(tmp_path / 'input'))


class _Output:  # mirror of comfy.clip_vision.Output
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, item):
        setattr(self, key, item)


class _TinyDino(torch.nn.Module):
    def __init__(self, result=None):
        super().__init__()
        self.result = result
        self.patch_size = 16
        self.kwargs = None
        self.register_buffer('projection', torch.arange(12, dtype=torch.float32).reshape(3, 4) / 10)

    def forward(self, pixel_values, **kwargs):
        self.kwargs = kwargs
        if self.result is not None:
            return self.result
        b, _, h, w = pixel_values.shape
        patches = pixel_values.unfold(2, 16, 16).unfold(3, 16, 16).mean((-1, -2))
        patches = patches.flatten(2).transpose(1, 2) @ self.projection + 1.
        cls = patches.mean(1, keepdim=True)
        registers = torch.full((b, 4, 4), 900.)
        sequence = torch.cat([cls, registers, patches], dim=1)
        return sequence, None, sequence[:, 0], None


@pytest.fixture(autouse=True)
def _host(monkeypatch):
    calls = []
    clip_vision = types.ModuleType('comfy.clip_vision')
    clip_vision.Output = _Output
    clip_model = types.ModuleType('comfy.clip_model')

    def clip_preprocess(image, size, mean, std, crop):
        calls.append(('preprocess', size, crop))
        image = image[..., :3].movedim(-1, 1)
        if image.shape[-2:] != (size, size):
            height, width = image.shape[-2:]
            scale = size / min(height, width)
            scaled = (round(scale * height), round(scale * width)) if crop else (size, size)
            image = torch.nn.functional.interpolate(image, size=scaled, mode='bicubic', antialias=True)
            top, left = (image.shape[2] - size) // 2, (image.shape[3] - size) // 2
            image = image[:, :, top:top + size, left:left + size]
        image = (image * 255).clamp(0, 255).round() / 255.
        return (image - torch.tensor(mean).view(3, 1, 1)) / torch.tensor(std).view(3, 1, 1)

    clip_model.clip_preprocess = clip_preprocess
    management = types.ModuleType('comfy.model_management')
    management.load_model_gpu = lambda patcher: calls.append(('load', patcher))
    management.intermediate_device = lambda: torch.device('cpu')
    for name, module in (('clip_vision', clip_vision), ('clip_model', clip_model),
                         ('model_management', management)):
        monkeypatch.setitem(sys.modules, f'comfy.{name}', module)
    return calls


def _clip_vision(model=None):
    return SimpleNamespace(model=model or _TinyDino(), patcher=object(), load_device='cpu',
                           image_size=32, image_mean=[.5, .5, .5], image_std=[.25, .25, .25],
                           model_type='dinov3', return_all_hidden_states=False)


def _image(seed=0):
    return torch.rand(1, 40, 40, 3, generator=torch.Generator().manual_seed(seed))


def _regions():
    masks = torch.zeros(2, 4, 4)
    masks[0, :, :2] = 1
    masks[1, :, 2:] = 1
    table = [{'id': f'part-{i}', 'prompt': f'part {i}', 'priority': 0} for i in range(2)]
    return LF_TextRegionMasks().on_exec(torch.zeros(1, 4, 4, 3), masks, table)['result'][:2]


def test_dinov3_tuple_gives_core_output_fields_and_shapes():
    pixels = torch.rand(2, 3, 32, 32, generator=torch.Generator().manual_seed(1))
    output = vision_output_from_pixel_values(_TinyDino(), pixels, torch.device('cpu'))
    assert output.last_hidden_state.shape == (2, 9, 4)
    assert output.image_embeds.shape == (2, 4)
    assert output.image_sizes == [torch.Size([3, 32, 32])] * 2
    assert output['mm_projected'] is None
    assert not hasattr(output, 'penultimate_hidden_states')


def test_hidden_state_tensor_is_kept_when_the_model_returns_one():
    sequence = torch.ones(1, 9, 4)
    model = _TinyDino((sequence, sequence * 2, sequence[:, 0], None))
    output = vision_output_from_pixel_values(model, torch.zeros(1, 3, 32, 32), 'cpu')
    torch.testing.assert_close(output.penultimate_hidden_states, sequence * 2)
    assert model.kwargs == {'intermediate_output': -2}


def test_node_encodes_through_loaded_model_and_matches_core_crop(_host):
    clip_vision = _clip_vision()
    output = LF_VisionPatchEncode().on_exec(clip_vision, _image(), 'none')['result'][0]
    assert _host == [('load', clip_vision.patcher), ('preprocess', 32, False)]
    assert output.last_hidden_state.shape == (1, 9, 4)
    LF_VisionPatchEncode().on_exec(clip_vision, _image(), 'center')
    assert _host[-1] == ('preprocess', 32, True)


def test_identical_images_compare_at_one_in_region_feature_similarity():
    clip_vision = _clip_vision()
    a = LF_VisionPatchEncode().on_exec(clip_vision, _image(), 'none')['result'][0]
    b = LF_VisionPatchEncode().on_exec(clip_vision, _image(), 'none')['result'][0]
    masks, metadata = _regions()
    result = compare_region_features(a, b, masks, metadata, 'dino_v3_vit_h.safetensors', 'none')
    assert result['method'] == 'coverage_weighted_patch_mean_cosine'
    assert result['patch_grid'] == [2, 2]
    assert [row['similarity'] for row in result['regions']] == pytest.approx([1., 1.])
    changed = LF_VisionPatchEncode().on_exec(clip_vision, _image(seed=5), 'none')['result'][0]
    result = compare_region_features(a, changed, masks, metadata, 'dino_v3_vit_h.safetensors', 'none')
    assert all(row['similarity'] < 1. for row in result['regions'])


@pytest.mark.parametrize('result,message', [
    ((None, None, torch.ones(1, 4), None), 'sequence tensor at index 0'),
    ((torch.ones(1, 9, 4), None, None, None), 'pooled tensor at index 2'),
    (torch.ones(1, 9, 4), 'must be a tuple'),
    ((torch.ones(1, 9, 4),), 'must be a tuple'),
    ((torch.ones(2, 9, 4), None, torch.ones(2, 4), None), 'batch does not match'),
])
def test_bad_model_output_is_refused_with_reason(result, message):
    with pytest.raises(ValueError, match=message):
        vision_output_from_pixel_values(_TinyDino(result), torch.zeros(1, 3, 32, 32), 'cpu')


def test_bad_inputs_fail_before_any_model_load(_host):
    node = LF_VisionPatchEncode()
    with pytest.raises(ValueError, match='clip_vision requires'):
        node.on_exec(None, _image(), 'none')
    with pytest.raises(ValueError, match='image must be an IMAGE'):
        node.on_exec(_clip_vision(), torch.ones(40, 40, 3), 'none')
    with pytest.raises(ValueError, match='image must be an IMAGE'):
        node.on_exec(_clip_vision(), 'not an image', 'none')
    with pytest.raises(ValueError, match="crop must be 'center' or 'none'"):
        node.on_exec(_clip_vision(), _image(), 'stretch')
    siglip2 = _clip_vision()
    siglip2.model_type = 'siglip2_vision_model'
    with pytest.raises(ValueError, match='siglip2'):
        node.on_exec(siglip2, _image(), 'none')
    assert _host == []


def test_public_contract_matches_core_clip_vision_encode():
    required = LF_VisionPatchEncode.INPUT_TYPES()['required']
    assert list(required) == ['clip_vision', 'image', 'crop']
    assert required['clip_vision'][0] == 'CLIP_VISION'
    assert required['image'][0] == 'IMAGE'
    assert required['crop'][0] == ['center', 'none']
    assert LF_VisionPatchEncode.RETURN_TYPES == ('CLIP_VISION_OUTPUT',)
    assert LF_VisionPatchEncode.OUTPUT_IS_LIST == (False,)
    assert not getattr(LF_VisionPatchEncode, 'INPUT_IS_LIST', False)
    assert LF_VisionPatchEncode.RETURN_NAMES == ('clip_vision_output',)
    assert LF_VisionPatchEncode.INPUT_TYPES()['optional']['ui_widget'] == ('LF_COMPARE', {'default': {}})
    assert LF_VisionPatchEncode.INPUT_TYPES()['hidden'] == {'node_id': 'UNIQUE_ID'}


def test_batch_geometry_payload_and_history_are_same_and_stable(monkeypatch):
    sent = []
    monkeypatch.setattr(node_module, 'safe_send_sync', lambda *args: sent.append(args))
    image = torch.cat([_image(1), _image(2)])
    clip = _clip_vision()
    response = LF_VisionPatchEncode().on_exec(clip, image, 'none', node_id='20')
    payload = response['ui']['lf_output'][0]
    assert sent == [('visionpatchencode', payload, '20')]
    assert payload['encoding'] == {
        'schema': 'lf.vision-patch-encode.v1', 'crop': 'none', 'source_size': [40, 40],
        'encoded_size': [32, 32], 'image_count': 2, 'sequence_shape': [2, 9, 4],
        'pooled_shape': [2, 4], 'token_count': 9, 'feature_dimension': 4,
        'patch_grid': [2, 2], 'patch_size': 16, 'prefix_tokens': 5, 'model_identity': None}
    assert len(payload['dataset']['nodes']) == 2
    assert 'pooled [2, 4]' in payload['dataset']['nodes'][1]['value']
    assert all(node['cells']['lfImage']['value'] == node['value'] + ' (before)'
               and node['cells']['lfImage_after']['value'] == node['value'] + ' (after)'
               for node in payload['dataset']['nodes'])
    assert LF_VisionPatchEncode().on_exec(clip, image, 'none')['ui']['lf_output'][0] == payload


def test_unknown_model_does_not_invent_grid_or_prefix():
    clip = _clip_vision()
    clip.model_type = 'other'
    del clip.model.patch_size
    payload = LF_VisionPatchEncode().on_exec(clip, _image(), 'center')['ui']['lf_output'][0]
    assert payload['encoding']['patch_grid'] is None and payload['encoding']['prefix_tokens'] is None
    assert 'unavailable' in payload['encoding']['warning']
    assert 'grid N/A' in payload['dataset']['nodes'][0]['value']


def test_clip_config_geometry_reports_its_grid_and_single_prefix():
    sequence = torch.ones(1, 5, 4)
    clip = _clip_vision(_TinyDino((sequence, sequence, sequence[:, 0], None)))
    clip.model_type, clip.image_size, clip.config = 'clip_vision_model', 28, {'patch_size': 14}
    del clip.model.patch_size
    payload = LF_VisionPatchEncode().on_exec(clip, _image(), 'center')['ui']['lf_output'][0]
    assert payload['encoding']['patch_grid'] == [2, 2]
    assert payload['encoding']['patch_size'] == 14
    assert payload['encoding']['prefix_tokens'] == 1
