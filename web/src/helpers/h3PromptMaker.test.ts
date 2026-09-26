import { describe, expect, it, vi } from 'vitest';
import { H3ReferenceNode, installH3References, refreshH3References } from './h3PromptMaker';

function fixture(names: string[] = ['image', ...Array.from({ length: 8 }, (_, i) => `image_${i + 2}`)]) {
  const node: H3ReferenceNode = {
    inputs: names.map((name) => ({ name, link: null })),
    addInput(name) { this.inputs!.push({ name, link: null }); },
    removeInput(index) { this.inputs!.splice(index, 1); },
  };
  return node;
}

describe('H3 reference sockets', () => {
  it('starts compact and exposes a spare when the first reference connects', () => {
    const node = fixture();
    refreshH3References(node);
    expect(node.inputs!.map((i) => i.name)).toEqual(['image']);
    node.inputs![0].link = 0;
    refreshH3References(node);
    expect(node.inputs!.map((i) => i.name)).toEqual(['image', 'image_2']);
  });

  it('preserves saved gaps, linked slots, and converted control sockets', () => {
    const node = fixture(['image', 'model', 'image_2', 'image_3', 'image_4']);
    node.inputs![1].link = 10;
    node.inputs![3].link = 12;
    refreshH3References(node);
    expect(node.inputs!.map((i) => i.name)).toEqual(['image', 'model', 'image_2', 'image_3', 'image_4']);
    expect(node.inputs![3].link).toBe(12);
    node.inputs![3].link = null;
    refreshH3References(node);
    expect(node.inputs!.map((i) => i.name)).toEqual(['image', 'model']);
  });

  it('does not exceed the nine-image socket contract', () => {
    const node = fixture();
    node.inputs![8].link = 1;
    refreshH3References(node);
    expect(node.inputs).toHaveLength(9);
  });

  it('reconciles after configure and preserves existing callbacks', async () => {
    const node = fixture();
    const callback = vi.fn();
    node.onConfigure = callback;
    installH3References(node);
    node.inputs![2].link = 42;
    node.onConfigure!('saved');
    await Promise.resolve();
    expect(callback).toHaveBeenCalledWith('saved');
    expect(node.inputs!.map((i) => i.name)).toEqual(['image', 'image_2', 'image_3', 'image_4']);
    node.inputs![2].link = null;
    node.onConnectionsChange!();
    await Promise.resolve();
    expect(node.inputs!.map((i) => i.name)).toEqual(['image']);
  });
});
