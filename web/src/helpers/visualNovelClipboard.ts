import { transformVnClipboard, VnClipboardItems } from './visualNovel';

const PATCH_FLAG = Symbol.for('lf.vn.clipboard-remap.v1');

type ClipboardDeserializer = (
  parsed: VnClipboardItems,
  options?: unknown,
) => unknown;

type CanvasWithClipboard = {
  _deserializeItems?: ClipboardDeserializer;
  [PATCH_FLAG]?: boolean;
};

export type ClipboardRemapLogger = (
  message: string,
  details?: Record<string, unknown>,
) => void;

/**
 * Install the current Comfy/LiteGraph clipboard compatibility adapter.
 *
 * Frontend 1.49.6 exposes no extension hook around a complete paste
 * transaction. `_deserializeItems` is the narrowest atomic seam: the full
 * payload is available before any node, link, group, or subgraph is added.
 * The adapter is feature-detected and refuses to claim support when that seam
 * is absent.
 */
export const installVnClipboardIdentityRemap = (
  canvas: unknown,
  logger?: ClipboardRemapLogger,
): boolean => {
  if (!canvas || typeof canvas !== 'object') {
    const message = 'VN identity remapping unavailable: Comfy canvas was not initialized.';
    logger?.(message);
    console.error(message);
    return false;
  }

  const instance = canvas as CanvasWithClipboard;
  const prototype = Object.getPrototypeOf(instance) as CanvasWithClipboard | null;
  const owner = prototype && typeof prototype._deserializeItems === 'function'
    ? prototype
    : instance;

  if (owner[PATCH_FLAG]) return true;
  const original = owner._deserializeItems;
  if (typeof original !== 'function') {
    const message =
      'VN identity remapping unavailable: this Comfy frontend has no compatible paste transaction.';
    logger?.(message, { canvas });
    console.error(message, canvas);
    return false;
  }

  owner._deserializeItems = function (
    this: CanvasWithClipboard,
    parsed: VnClipboardItems,
    options?: unknown,
  ) {
    try {
      // The pure transformer clones first. If it cannot complete, the native
      // deserializer is never entered, so a partial graph cannot be created.
      const remapped = transformVnClipboard(parsed);
      return original.call(this, remapped, options);
    } catch (error) {
      const message = 'VN paste blocked because semantic identities could not be remapped safely.';
      logger?.(message, { error });
      console.error(message, error);
      throw error;
    }
  };
  Object.defineProperty(owner, PATCH_FLAG, {
    configurable: false,
    enumerable: false,
    value: true,
  });
  return true;
};
