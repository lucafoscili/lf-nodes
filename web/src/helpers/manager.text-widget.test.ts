import { describe, expect, it } from 'vitest';
import { CustomWidgetName, NodeName } from '../types/widgets/widgets';
import { NODE_WIDGET_MAP, normalizeTextWidgetValue } from './manager';

describe('normalizeTextWidgetValue', () => {
  it('keeps strings unchanged for Comfy text replacement', () => {
    const value = 'portrait [seed]';

    expect(normalizeTextWidgetValue(value)).toBe(value);
  });

  it('coerces legacy scalar values instead of passing them to replace', () => {
    expect(normalizeTextWidgetValue(42)).toBe('42');
    expect(normalizeTextWidgetValue(true)).toBe('true');
    expect(normalizeTextWidgetValue(null)).toBe('');
  });

  it('drops structured spillover from legacy widget hydration', () => {
    expect(normalizeTextWidgetValue(['a', 'b'])).toBe('');
    expect(normalizeTextWidgetValue({ props: [{ lfDataset: {} }] })).toBe('');
  });
});

describe('External intake widget contracts', () => {
  it('renders the YouTube reference receipt with the LF code widget', () => {
    expect(NODE_WIDGET_MAP[NodeName.youtubeReference]).toEqual([CustomWidgetName.code]);
  });
});

describe('Generic output widget contracts', () => {
  it('uses native Comfy audio UI for ACE-Step Remix', () => {
    expect(NODE_WIDGET_MAP[NodeName.aceStepRemix]).toEqual([]);
  });

  it('renders DDS save receipts with the LF tree widget', () => {
    expect(NODE_WIDGET_MAP[NodeName.saveDds]).toEqual([CustomWidgetName.tree]);
  });

  it('renders registered output receipts with the LF tree widget', () => {
    expect(NODE_WIDGET_MAP[NodeName.registerOutputFile]).toEqual([CustomWidgetName.tree]);
  });

  it('renders comparison grids with the LF masonry widget', () => {
    expect(NODE_WIDGET_MAP[NodeName.imageGrid]).toEqual([CustomWidgetName.masonry]);
  });

  it('renders ordered image lists with the LF masonry widget', () => {
    expect(NODE_WIDGET_MAP[NodeName.imageList]).toEqual([CustomWidgetName.masonry]);
  });

  it('renders periodic image samples with the LF masonry widget', () => {
    expect(NODE_WIDGET_MAP[NodeName.periodicImageBatchSampler]).toEqual([
      CustomWidgetName.masonry,
    ]);
  });

  it('renders normalized sprite batches with the LF masonry widget', () => {
    expect(NODE_WIDGET_MAP[NodeName.normalizeSpriteBatch]).toEqual([
      CustomWidgetName.masonry,
    ]);
  });

  it('renders side-by-side composites with the LF masonry widget', () => {
    expect(NODE_WIDGET_MAP[NodeName.sideBySide]).toEqual([CustomWidgetName.masonry]);
  });

  it('renders unsharp-mask comparisons with the LF compare widget', () => {
    expect(NODE_WIDGET_MAP[NodeName.unsharpMask]).toEqual([CustomWidgetName.compare]);
  });

  it('renders region extraction history with the LF history widget', () => {
    expect(NODE_WIDGET_MAP[NodeName.regionExtractor]).toEqual([CustomWidgetName.history]);
  });

  it('does not retain mappings for nodes that no longer exist', () => {
    expect(Object.values(NodeName).includes('LF_Brush' as NodeName)).toBe(false);
    expect(Object.values(NodeName).includes('LF_ExtractFaceEmbedding' as NodeName)).toBe(false);
    expect(Object.prototype.hasOwnProperty.call(NODE_WIDGET_MAP, 'LF_Brush')).toBe(false);
    expect(Object.prototype.hasOwnProperty.call(NODE_WIDGET_MAP, 'LF_ExtractFaceEmbedding')).toBe(
      false,
    );
  });
});

describe('Visual novel widget contracts', () => {
  it('keeps LF_CODE exclusively on compile diagnostics', () => {
    expect(NODE_WIDGET_MAP[NodeName.vnCompile]).toEqual([
      CustomWidgetName.id,
      CustomWidgetName.ref,
      CustomWidgetName.code,
    ]);
  });

  it('uses one LF_TEXTAREA body and persistent identity controls per declaration', () => {
    expect(NODE_WIDGET_MAP[NodeName.vnState]).toEqual([
      CustomWidgetName.id,
      CustomWidgetName.textarea,
      CustomWidgetName.ref,
    ]);
    expect(NODE_WIDGET_MAP[NodeName.vnSceneSpec]).toEqual([
      CustomWidgetName.id,
      CustomWidgetName.textarea,
    ]);
    expect(NODE_WIDGET_MAP[NodeName.vnSwitch]).toEqual([
      CustomWidgetName.id,
      CustomWidgetName.textarea,
    ]);
  });
});
