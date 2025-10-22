import { LfDebugCategory } from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';

//#region Logging
/**
 * Formats an unknown context value into a string representation.
 * Returns null if the context is null or undefined.
 * If the context is already a string, returns it as-is.
 * Attempts to serialize the context using JSON.stringify with indentation.
 * If serialization fails or results in an empty string, falls back to String(context).
 *
 * @param context - The value to format, of any type.
 * @returns A formatted string representation of the context, or null if the context is null or undefined.
 */
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
/**
 * Logs a debug message with an optional category and context.
 *
 * @param message - The debug message to log.
 * @param category - The category of the debug log. Defaults to 'informational'.
 * @param context - Optional additional context to include in the log.
 */
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
//#endregion
