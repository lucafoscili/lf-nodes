/** Keep one spare reference socket without touching saved/connected inputs. */
export interface H3ReferenceNode {
  inputs?: { name?: string; link?: unknown }[];
  addInput?: (name: string, type: string) => unknown;
  removeInput?: (index: number) => unknown;
  onConnectionsChange?: (...args: any[]) => unknown;
  onConfigure?: (...args: any[]) => unknown;
}

const ordinal = (name = ''): number =>
  name === 'image' ? 1 : /^image_[2-9]$/.test(name) ? Number(name.slice(6)) : 0;

export function refreshH3References(node: H3ReferenceNode): void {
  if (!node.addInput || !node.removeInput) return;
  const inputs = node.inputs ?? [];
  const connected = inputs.filter((input) => input.link != null).map((input) => ordinal(input.name));
  const last = Math.max(0, ...connected);
  const needed = Math.min(9, last + 1);
  // Remove only trailing, disconnected reference sockets. Core updates link indices.
  for (let index = inputs.length - 1; index >= 0; index--) {
    if (ordinal(inputs[index].name) > needed && inputs[index].link == null) {
      node.removeInput(index);
    }
  }
  for (let index = 2; index <= needed; index++) {
    const name = `image_${index}`;
    if (!node.inputs?.some((input) => input.name === name)) node.addInput(name, 'IMAGE');
  }
}

export function installH3References(node: H3ReferenceNode): void {
  let pending = false;
  const schedule = () => {
    if (pending) return;
    pending = true;
    queueMicrotask(() => {
      // Hold the flag through mutations: removeInput itself can emit a connection event.
      refreshH3References(node);
      pending = false;
    });
  };
  const onConnectionsChange = node.onConnectionsChange;
  node.onConnectionsChange = function (...args) {
    const result = onConnectionsChange?.apply(this, args);
    schedule();
    return result;
  };
  const onConfigure = node.onConfigure;
  node.onConfigure = function (...args) {
    const result = onConfigure?.apply(this, args);
    schedule();
    return result;
  };
  schedule();
}
