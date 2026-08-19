const INLINE_IMAGE_DATA_URL = /^data:image\/[^,]*;base64,/i;

type SerializedRecord = Record<string, unknown>;

/**
 * Return whether a string is an inline, base64 encoded image data URL.
 *
 * This deliberately only covers image data URLs. Hashes, paths, ordinary
 * strings, and other data URL types are workflow data and must be preserved.
 */
export const isInlineImageDataUrl = (value: string): boolean =>
  INLINE_IMAGE_DATA_URL.test(value);

const isPlainObject = (value: object): boolean => {
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
};

/**
 * Clone a serialized widget value while removing only inline image payloads.
 *
 * The clone is intentionally cycle-safe. If a host object or accessor cannot
 * be cloned, the original value is returned so serialization fails open and
 * never leaves a partially modified live widget value behind.
 */
export const sanitizeSerializedValue = <T>(value: T): T => {
  const seen = new WeakMap<object, unknown>();

  const clone = (current: unknown): unknown => {
    if (typeof current === 'string') {
      return isInlineImageDataUrl(current) ? '' : current;
    }

    if (current === null || typeof current !== 'object') {
      return current;
    }

    const existing = seen.get(current);
    if (existing !== undefined) {
      return existing;
    }

    // Serialized LF values are arrays and plain records. Leave host objects
    // such as Date, Blob, and DOM nodes untouched rather than producing a
    // misleading shallow facsimile of them.
    if (!Array.isArray(current) && !isPlainObject(current)) {
      return current;
    }

    const copy: unknown[] | SerializedRecord = Array.isArray(current)
      ? new Array(current.length)
      : Object.create(Object.getPrototypeOf(current));
    seen.set(current, copy);

    for (const key of Object.keys(current)) {
      // Assignment would invoke Object.prototype.__proto__'s setter instead
      // of preserving a serialized "__proto__" key as data.
      Object.defineProperty(copy, key, {
        configurable: true,
        enumerable: true,
        value: clone((current as SerializedRecord)[key]),
        writable: true,
      });
    }

    return copy;
  };

  try {
    return clone(value) as T;
  } catch {
    // Sanitization is a best-effort boundary around host-provided values.
    return value;
  }
};

type DOMWidgetSerializationState = {
  widgets: Set<Widget<any>>;
  wrapper?: NodeType['onSerialize'];
};

const SERIALIZATION_STATES = new WeakMap<NodeType, DOMWidgetSerializationState>();

const sanitizeSerializedResult = <T>(value: T): T => {
  if (value !== null && (typeof value === 'object' || typeof value === 'function')) {
    try {
      if (typeof (value as { then?: unknown }).then === 'function') {
        // Keep synchronous serializers synchronous, but sanitize async widget
        // results after the host Promise/thenable resolves.
        return Promise.resolve(value).then((resolved) => sanitizeSerializedValue(resolved)) as T;
      }
    } catch {
      // A hostile thenable should retain the host's original result.
      return value;
    }
  }

  return sanitizeSerializedValue(value);
};

const rewriteWidgetSerialization = (node: NodeType, data: unknown, widget: Widget<any>) => {
  try {
    if (!data || typeof data !== 'object') return;

    const serialized = data as {
      widgets_values?: unknown[];
      widgets_values_named?: Record<string, unknown>;
    };
    const index = node.widgets?.indexOf(widget) ?? -1;
    if (index < 0) return;

    if (
      Array.isArray(serialized.widgets_values) &&
      Object.prototype.hasOwnProperty.call(serialized.widgets_values, index)
    ) {
      serialized.widgets_values[index] = sanitizeSerializedValue(serialized.widgets_values[index]);
    }

    const name = widget.name;
    const named = serialized.widgets_values_named;
    if (
      name &&
      named &&
      typeof named === 'object' &&
      Object.prototype.hasOwnProperty.call(named, name)
    ) {
      named[name] = sanitizeSerializedValue(named[name]);
    }
  } catch {
    // Host serialization objects may be frozen or proxied. Leave them intact.
  }
};

/**
 * Attach LF-only serialization behavior to one custom DOM widget.
 *
 * Prompt serialization uses serializeValue when available. Workflow
 * serialization uses live widget values and invokes node.onSerialize after
 * constructing its output, so both boundaries are covered here.
 */
export const hookDOMWidgetSerialization = (node: NodeType, widget: Widget<any>): Widget<any> => {
  try {
    const originalSerializeValue = widget.serializeValue;
    widget.serializeValue = function (this: Widget<any>, ...args: any[]) {
      const value = originalSerializeValue
        ? originalSerializeValue.apply(this, args)
        : this.value;
      return sanitizeSerializedResult(value);
    };

    const state = SERIALIZATION_STATES.get(node);
    if (state) {
      state.widgets.add(widget);

      // A later node/extension callback may replace our wrapper. Re-chain the
      // current callback so every LF widget remains covered without wrapping
      // the same callback twice.
      if (node.onSerialize !== state.wrapper) {
        const previous = node.onSerialize;
        const onSerialize = function (this: NodeType, data: Record<string, any>, ...args: any[]) {
          if (previous) {
            previous.apply(this, [data, ...args]);
          }
          for (const customWidget of state.widgets) {
            rewriteWidgetSerialization(node, data, customWidget);
          }
        };
        state.wrapper = onSerialize as NodeType['onSerialize'];
        node.onSerialize = state.wrapper;
      }

      return widget;
    }

    const previous = node.onSerialize;
    const nextState: DOMWidgetSerializationState = { widgets: new Set([widget]) };
    const onSerialize = function (this: NodeType, data: Record<string, any>, ...args: any[]) {
      // Comfy invokes onSerialize after it has assembled positional and named
      // values. Preserve the existing callback before applying LF's exact
      // widget rewrite.
      if (previous) {
        previous.apply(this, [data, ...args]);
      }
      for (const customWidget of nextState.widgets) {
        rewriteWidgetSerialization(node, data, customWidget);
      }
    };

    SERIALIZATION_STATES.set(node, nextState);
    nextState.wrapper = onSerialize as NodeType['onSerialize'];
    node.onSerialize = nextState.wrapper;
  } catch {
    // Host widgets may be sealed or proxied. Keep the original Comfy behavior.
  }

  return widget;
};
