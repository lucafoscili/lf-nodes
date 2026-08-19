import { describe, expect, it } from 'vitest';
import { normalizeTextWidgetValue } from './manager';

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
