"""Ordered text-region masks and the metadata boundary shared by consumers."""
from copy import deepcopy
import json

import pytest
import torch

from modules.nodes.regions.text_region_masks import LF_TextRegionMasks
from modules.utils.helpers.detection.region_masks import (
    TEXT_REGION_MASK_SCHEMA, region_mask_sets, resolve_region_overlaps,
)


def rows():
    return [{'id': 'first', 'prompt': 'first item', 'priority': 1},
            {'id': 'second', 'prompt': 'second item', 'priority': 2},
            {'id': 'third', 'prompt': 'third item', 'priority': 2}]


def image(count=1):
    return torch.zeros(count, 2, 3, 3)


def execute(masks=None, regions=None, count=1):
    if masks is None:
        masks = torch.tensor([[[1, 1, 0], [0, 0, 0]],
                              [[0, 1, 1], [0, 0, 0]],
                              [[0, 1, 0], [0, 1, 0]]], dtype=torch.float32)
    return LF_TextRegionMasks().on_exec([image(count)], [masks], [json.dumps(regions or rows())])


def test_priority_ties_and_triple_overlap_attribute_final_winner_once():
    batch, document, mask_list = execute()
    assert torch.equal(batch, torch.tensor([[[1, 0, 0], [0, 0, 0]],
                                           [[0, 1, 1], [0, 0, 0]],
                                           [[0, 0, 0], [0, 1, 0]]], dtype=torch.float32))
    records = document['mask_sets'][0]['regions']
    assert records[0] == {'id': 'first', 'area': 1, 'raw_area': 2, 'empty': False,
                          'overlap_lost': [{'id': 'second', 'area': 1}]}
    assert records[2]['overlap_lost'] == [{'id': 'second', 'area': 1}]
    assert document == {'schema': TEXT_REGION_MASK_SCHEMA, 'source_size': [3, 2],
                        'image_count': 1, 'regions': rows(), 'ordering': 'image-major',
                        'mask_sets': [{'image_index': 0, 'regions': records}]}
    assert len(mask_list) == 3
    assert all(tuple(item.shape) == (1, 2, 3) for item in mask_list)
    assert torch.equal(torch.cat(mask_list), batch)


def test_empty_raw_and_overlap_empties_are_preserved_with_warnings(caplog):
    masks = torch.ones(3, 2, 3)
    masks[2] = 0
    batch, doc, mask_list = execute(masks)
    first, second, third = doc['mask_sets'][0]['regions']
    assert first['empty'] and first['area'] == 0 and first['raw_area'] == 6
    assert first['overlap_lost'] == [{'id': 'second', 'area': 6}]
    assert second['area'] == 6
    assert third['empty'] and third['raw_area'] == 0
    assert 'overlap resolution' in first['warning']
    assert 'No pixels detected' in third['warning']
    assert len(mask_list) == 3 and batch.shape[0] == 3
    assert len(caplog.records) == 2
    assert 'first' in caplog.text and 'third' in caplog.text
    region_mask_sets(batch, doc)


@pytest.mark.parametrize('as_list', [False, True])
def test_multiple_image_region_major_input_becomes_image_major_output(as_list):
    region_rows = rows()[:2]
    # A0, A1, B0, B1: each detector contributes the complete image batch.
    masks = torch.zeros(4, 2, 3)
    masks[0, 0, 0] = 1
    masks[1, 0, 1] = 1
    masks[2, 1, 0] = 1
    masks[3, 1, 1] = 1
    incoming = [masks[:2], masks[2:]] if as_list else masks
    batch, doc, mask_list = execute(incoming, region_rows, count=2)
    assert torch.equal(batch, masks[[0, 2, 1, 3]])
    assert torch.equal(torch.cat(mask_list), batch)
    assert [entry['image_index'] for entry in doc['mask_sets']] == [0, 1]
    normalized, returned = region_mask_sets(mask_list, [doc])
    assert tuple(normalized.shape) == (2, 2, 2, 3)
    assert normalized.dtype == torch.float32 and normalized.device.type == 'cpu'
    assert returned == doc and returned is not doc


def test_threshold_includes_half_and_excludes_values_below_half():
    result, records = resolve_region_overlaps(
        torch.tensor([[[.5 - 1e-10, .5, .9]]], dtype=torch.float64), rows()[:1])
    assert torch.equal(result, torch.tensor([[[0., 1., 1.]]]))
    assert records[0]['area'] == 2


@pytest.mark.parametrize('bad', [[], {}, [{'id': 'x', 'priority': 1}],
    [{'id': '', 'prompt': 'x', 'priority': 1}],
    [{'id': 'x', 'prompt': ' ', 'priority': 1}],
    [{'id': 'x', 'prompt': 'x', 'priority': True}],
    [{'id': 'x', 'prompt': 'x', 'priority': float('nan')}],
    [{'id': 'x', 'prompt': 'x', 'priority': '1'}],
    [{'id': 'x', 'prompt': 'x', 'priority': 1}] * 2])
def test_malformed_region_table_fails(bad):
    with pytest.raises(ValueError, match='region|Region'):
        LF_TextRegionMasks().on_exec(image(), torch.zeros(1, 2, 3), bad)


@pytest.mark.parametrize('bad', [torch.zeros(2, 2, 3), torch.zeros(3, 3, 3),
    [torch.zeros(1, 2, 3), torch.zeros(1, 3, 3), torch.zeros(1, 2, 3)],
    torch.full((3, 2, 3), float('nan')), torch.full((3, 2, 3), float('inf')),
    torch.full((3, 2, 3), -0.01), torch.full((3, 2, 3), 1.01),
    torch.zeros(3, 2, 3, 2)])
def test_mask_count_size_values_and_channels_fail(bad):
    with pytest.raises(ValueError):
        execute(bad)


def test_heterogeneous_source_sizes_fail():
    with pytest.raises(ValueError, match='spatial size'):
        LF_TextRegionMasks().on_exec([image(), torch.zeros(1, 3, 3, 3)],
                                     torch.zeros(6, 2, 3), rows())


@pytest.mark.parametrize('missing', ['image', 'masks', 'regions'])
def test_missing_required_input_has_a_named_error(missing):
    kwargs = {'image': image(), 'masks': torch.zeros(3, 2, 3), 'regions': rows()}
    del kwargs[missing]
    with pytest.raises(ValueError, match=missing):
        LF_TextRegionMasks().on_exec(**kwargs)


def test_empty_mask_dimensions_have_a_named_error():
    with pytest.raises(ValueError, match='Region masks'):
        execute(torch.zeros(3, 2, 0))


def test_direct_raw_table_single_row_and_singleton_mask_channel_forms():
    node = LF_TextRegionMasks()
    for masks in [torch.ones(2, 3), torch.ones(1, 1, 2, 3), torch.ones(1, 2, 3, 1)]:
        batch, doc, _ = node.on_exec(image(), masks, rows()[:1])
        assert batch.shape == (1, 2, 3) and doc['regions'] == rows()[:1]


@pytest.mark.parametrize('serialized', [False, True])
def test_two_separate_metadata_documents_combine_without_mutation(serialized):
    first, first_doc, _ = execute()
    second, second_doc, _ = execute(torch.zeros(3, 2, 3))
    documents = [first_doc, second_doc]
    before = deepcopy(documents)
    if serialized:
        documents = [json.dumps(doc) for doc in documents]
    masks, combined = region_mask_sets([first, second], documents)
    assert masks.shape == (2, 3, 2, 3)
    assert torch.equal(masks[0], first) and torch.equal(masks[1], second)
    assert combined['image_count'] == 2
    assert [entry['image_index'] for entry in combined['mask_sets']] == [0, 1]
    assert [first_doc, second_doc] == before


@pytest.mark.parametrize('field,value,match', [
    ('schema', 'other', 'schema'), ('source_size', [2, 3], 'size'),
    ('source_size', [True, 2], 'source_size'), ('image_count', 2, 'image_count'),
    ('ordering', 'region-major', 'ordering'), ('mask_sets', [], 'image_count')])
def test_consumer_rejects_invalid_document(field, value, match):
    masks, doc, _ = execute()
    doc[field] = value
    with pytest.raises(ValueError, match=match):
        region_mask_sets(masks, doc)


@pytest.mark.parametrize('field,value,match', [
    ('area', 0, 'area'), ('empty', True, 'empty'), ('raw_area', 99, 'raw_area'),
    ('overlap_lost', [], 'raw_area'), ('id', 'second', 'IDs/order')])
def test_consumer_rejects_false_record_metadata(field, value, match):
    masks, doc, _ = execute()
    doc['mask_sets'][0]['regions'][0][field] = value
    with pytest.raises(ValueError, match=match):
        region_mask_sets(masks, doc)


def test_consumer_rejects_reordered_masks_rows_and_image_sets():
    masks, doc, _ = execute()
    with pytest.raises(ValueError, match='area'):
        region_mask_sets(masks[[1, 0, 2]], doc)
    doc['regions'].reverse()
    with pytest.raises(ValueError, match='IDs/order'):
        region_mask_sets(masks, doc)
    _, doc, _ = execute()
    doc['mask_sets'][0]['image_index'] = 1
    with pytest.raises(ValueError, match='image_index'):
        region_mask_sets(masks, doc)


def test_consumer_rejects_document_pair_geometry_or_table_mismatch():
    masks, doc, _ = execute()
    other = deepcopy(doc)
    other['regions'].reverse()
    with pytest.raises(ValueError, match='identical ordered'):
        region_mask_sets([masks, masks], [doc, other])
    other = deepcopy(doc)
    other['regions'][0]['id'] = 'different-id'
    with pytest.raises(ValueError, match='identical ordered'):
        region_mask_sets([masks, masks], [doc, other])
    other = deepcopy(doc)
    other['source_size'] = [6, 1]
    with pytest.raises(ValueError, match='source_size'):
        region_mask_sets([masks, masks], [doc, other])


def test_document_pair_matches_ids_despite_different_detector_prompts_and_priorities():
    masks, doc, _ = execute()
    other = deepcopy(doc)
    other['regions'][0]['prompt'] = 'alternate wording for the other view'
    other['regions'][0]['priority'] = 10
    normalized, combined = region_mask_sets([masks, masks], [doc, other])
    assert normalized.shape == (2, 3, 2, 3)
    assert combined['regions'] == doc['regions']


def test_consumer_rejects_nonbinary_overlapping_and_incorrect_count_masks():
    masks, doc, _ = execute()
    with pytest.raises(ValueError, match='count'):
        region_mask_sets(masks[:2], doc)
    with pytest.raises(ValueError, match='binary'):
        region_mask_sets(masks * .5, doc)
    masks[0, 0, 1] = 1
    with pytest.raises(ValueError, match='disjoint'):
        region_mask_sets(masks, doc)


def test_helper_accepts_general_n_and_node_metadata_is_aligned():
    batch, doc, _ = execute(torch.zeros(9, 2, 3), count=3)
    masks, _ = region_mask_sets(batch, doc)
    assert masks.shape == (3, 3, 2, 3)
    node = LF_TextRegionMasks
    assert node.INPUT_IS_LIST is True
    assert node.RETURN_NAMES == ('masks', 'metadata', 'mask_list')
    assert node.OUTPUT_IS_LIST == (False, False, True)
    assert len(node.RETURN_TYPES) == len(node.RETURN_NAMES) == len(node.OUTPUT_TOOLTIPS)
