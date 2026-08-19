type WidthMutableWidget = {
  width?: number;
};

/**
 * Keep LF DOM widgets bound to the canvas node width.
 *
 * ComfyUI frontend 1.49.6 renders a selected legacy widget in the narrow
 * Workflow Overview sidebar and writes that preview width back to the shared
 * widget instance. The canvas DOM renderer then reuses the leaked width and
 * leaves the widget permanently shrunken. LF DOM widgets are full-node-width,
 * so foreign width assignments are intentionally ignored.
 */
export const protectDOMWidgetWidth = <T extends WidthMutableWidget>(widget: T): T => {
  try {
    const descriptor = Object.getOwnPropertyDescriptor(widget, 'width');

    if (descriptor && !descriptor.configurable) {
      return widget;
    }

    Object.defineProperty(widget, 'width', {
      configurable: true,
      enumerable: descriptor?.enumerable ?? false,
      get: () => undefined,
      set: () => undefined,
    });
  } catch {
    // Fail open for sealed objects or host-provided proxies.
  }

  return widget;
};
