import { getLfFramework } from '@lf-widgets/framework';

export type DebugCategory = 'informational' | 'warning' | 'error' | 'success';

const formatContext = (context: unknown): string | null => {
  if (context === undefined || context === null) {
    return null;
  }

  if (typeof context === 'string') {
    return context;
  }

  try {
    const serialized = JSON.stringify(context, null, 2);
    return serialized ? serialized : null;
  } catch {
    return String(context);
  }
};

export const debugLog = (
  message: string,
  category: DebugCategory = 'informational',
  context?: unknown,
): void => {
  try {
    const framework = getLfFramework();
    const debug = framework?.debug;
    const logs = debug?.logs;

    if (!debug || !logs) {
      return;
    }

    const formattedContext = formatContext(context);
    const payload = formattedContext ? `${message}\n\n${formattedContext}` : message;

    // Use the debug manager as the source so messages appear in the debug card console.
    void logs.new(debug, payload, category);
  } catch {
    // Intentionally swallow debug errors to avoid interfering with user flows.
  }
};
