/**
 * Parse JSON while rejecting duplicate keys within the same object.
 *
 * JSON.parse accepts duplicate names and keeps only the last value. That is
 * dangerous at an authoring boundary because a typo can silently discard a
 * declaration. We let the native parser validate all JSON syntax and then
 * walk the original token stream to check object names without reserializing
 * the input.
 */
export const parseStrictJson = <T = unknown>(text: string): T => {
  const parsed = JSON.parse(text) as T;
  let index = 0;

  const syntaxError = (message: string): never => {
    throw new SyntaxError(`${message} at position ${index}`);
  };

  const skipWhitespace = () => {
    while (index < text.length && /\s/.test(text[index])) index += 1;
  };

  const parseString = (): string => {
    if (text[index] !== '"') syntaxError('Expected a JSON string');
    const start = index;
    index += 1;
    while (index < text.length) {
      const character = text[index];
      if (character === '\\') {
        index += 2;
        continue;
      }
      index += 1;
      if (character === '"') {
        return JSON.parse(text.slice(start, index)) as string;
      }
    }
    return syntaxError('Unterminated JSON string');
  };

  const parseValue = (): void => {
    skipWhitespace();
    const character = text[index];
    if (character === '{') {
      parseObject();
      return;
    }
    if (character === '[') {
      parseArray();
      return;
    }
    if (character === '"') {
      parseString();
      return;
    }

    // Native JSON.parse has already validated literals and numbers. Advance
    // to the next structural delimiter so nested containers can be scanned.
    while (
      index < text.length &&
      !/\s/.test(text[index]) &&
      !',]}'.includes(text[index])
    ) {
      index += 1;
    }
  };

  const parseObject = (): void => {
    index += 1; // {
    skipWhitespace();
    const keys = new Set<string>();
    if (text[index] === '}') {
      index += 1;
      return;
    }

    while (index < text.length) {
      skipWhitespace();
      const key = parseString();
      if (keys.has(key)) syntaxError(`Duplicate JSON key ${JSON.stringify(key)}`);
      keys.add(key);
      skipWhitespace();
      if (text[index] !== ':') syntaxError('Expected : after JSON object key');
      index += 1;
      parseValue();
      skipWhitespace();
      if (text[index] === '}') {
        index += 1;
        return;
      }
      if (text[index] !== ',') syntaxError('Expected , or } in JSON object');
      index += 1;
    }
    syntaxError('Unterminated JSON object');
  };

  const parseArray = (): void => {
    index += 1; // [
    skipWhitespace();
    if (text[index] === ']') {
      index += 1;
      return;
    }

    while (index < text.length) {
      parseValue();
      skipWhitespace();
      if (text[index] === ']') {
        index += 1;
        return;
      }
      if (text[index] !== ',') syntaxError('Expected , or ] in JSON array');
      index += 1;
    }
    syntaxError('Unterminated JSON array');
  };

  parseValue();
  skipWhitespace();
  if (index !== text.length) syntaxError('Unexpected JSON content');
  return parsed;
};
