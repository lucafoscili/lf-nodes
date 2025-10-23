import { LfDebugCategory } from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { WorkflowStatus } from '../types/state';

//#region Helpers
const _formatContext = (context: unknown): string | null => {
  if (context === undefined || context === null) {
    return null;
  }

  if (typeof context === 'string') {
    return context;
  }

  try {
    const serialized = JSON.stringify(context);
    return serialized ? serialized : null;
  } catch {
    return String(context);
  }
};
const _getLogLevel = (category: WorkflowStatus | LfDebugCategory) => {
  let level: LfDebugCategory;

  switch (category) {
    case 'error':
      level = 'error';
      break;
    default:
      level = 'informational';
  }

  return level;
};
//#endregion

//#region Logging
export const debugLog = (
  message: string,
  category: WorkflowStatus | LfDebugCategory = 'idle',
  context?: unknown,
): void => {
  try {
    const { debug } = getLfFramework();
    const { logs } = debug;

    const formattedContext = _formatContext(context);
    const payload = formattedContext ? `${message}\n\n${formattedContext}` : message;

    logs.new(debug, payload, _getLogLevel(category));
  } catch {
    // Intentionally swallow debug errors to avoid interfering with user flows.
  }
};
//#endregion
