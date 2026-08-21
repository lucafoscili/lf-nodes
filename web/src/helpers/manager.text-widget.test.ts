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
