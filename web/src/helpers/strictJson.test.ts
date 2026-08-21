import { describe, expect, it } from 'vitest';
import { parseStrictJson } from './strictJson';

describe('parseStrictJson', () => {
  it('rejects duplicate keys in the same object, including nested objects', () => {
    expect(() => parseStrictJson('{"outer":{"value":1,"value":2}}'))
      .toThrow(/Duplicate JSON key/);
  });

  it('allows the same key in separate objects', () => {
    expect(parseStrictJson('[{"value":1},{"value":2}]')).toEqual([
      { value: 1 },
      { value: 2 },
    ]);
  });

  it('compares decoded keys while ignoring escaped strings in values', () => {
    expect(() => parseStrictJson(
      '{"label":"a \\"value\\" with } and {","\\u006cabel":"duplicate"}',
    )).toThrow(/Duplicate JSON key/);
    expect(parseStrictJson('{"label":"a \\"value\\" with } and {"}'))
      .toEqual({ label: 'a "value" with } and {' });
  });

  it('retains native syntax errors', () => {
    expect(() => parseStrictJson('{"broken":}')).toThrow(SyntaxError);
    expect(() => parseStrictJson('{"broken":1')).toThrow(SyntaxError);
  });
});
