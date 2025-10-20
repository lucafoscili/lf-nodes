import { LfDebugCategory } from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';

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
  category: LfDebugCategory = 'informational',
  context?: unknown,
): void => {
  try {
    const { debug } = getLfFramework();
    const { logs } = debug;

    const formattedContext = formatContext(context);
    const payload = formattedContext ? `${message}\n\n${formattedContext}` : message;

    logs.new(debug, payload, category);
  } catch {
    // Intentionally swallow debug errors to avoid interfering with user flows.
  }
};
