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
