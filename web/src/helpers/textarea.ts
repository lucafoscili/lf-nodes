import { LogSeverity } from '../types/manager/manager';
import { TextareaCSS } from '../types/widgets/textarea';
import { getLfManager } from '../utils/common';
import { parseStrictJson } from './strictJson';

export { parseStrictJson } from './strictJson';

export type TextareaJsonNormalizer = (value: unknown) => unknown;
export type TextareaValidCallback = (value: unknown) => void;

const VALIDATION_TIMEOUTS = new WeakMap<
  HTMLTextAreaElement,
  ReturnType<typeof setTimeout>
>();

const reportInvalidJson = (textarea: HTMLTextAreaElement, error: unknown) => {
  textarea.classList.add(TextareaCSS.WidgetError);
  textarea.title = error instanceof Error ? error.message : String(error);
  getLfManager()?.log?.('Error parsing JSON', { error }, LogSeverity.Warning);
};

/**
 * Validate, normalize, and persist one LF_TEXTAREA document.
 *
 * The optional normalizer is deliberately invoked only after strict JSON
 * succeeded. VN declarations use that author-time boundary to materialize
 * missing LF-owned child IDs; queue serialization never calls this function.
 */
export const validateAndFormatTextarea = (
  textarea: HTMLTextAreaElement,
  normalize?: TextareaJsonNormalizer,
  onValid?: TextareaValidCallback,
): boolean => {
  try {
    const parsed = parseStrictJson(textarea.value);
    const normalized = normalize ? normalize(parsed) : parsed;
    const formatted = JSON.stringify(normalized, null, 2);

    textarea.value = formatted === undefined ? 'null' : formatted;
    textarea.title = '';
    textarea.classList.remove(TextareaCSS.WidgetError);
    onValid?.(normalized);
    return true;
  } catch (error) {
    reportInvalidJson(textarea, error);
    return false;
  }
};

/** Schedule validation independently per textarea, so editing one node cannot cancel another. */
export const scheduleTextareaValidation = (
  textarea: HTMLTextAreaElement,
  normalize?: TextareaJsonNormalizer,
  onValid?: TextareaValidCallback,
  delay = 650,
) => {
  const pending = VALIDATION_TIMEOUTS.get(textarea);
  if (pending) clearTimeout(pending);

  const timeout = setTimeout(() => {
    VALIDATION_TIMEOUTS.delete(textarea);
    validateAndFormatTextarea(textarea, normalize, onValid);
  }, delay);
  VALIDATION_TIMEOUTS.set(textarea, timeout);
};

export const cancelTextareaValidation = (textarea: HTMLTextAreaElement) => {
  const pending = VALIDATION_TIMEOUTS.get(textarea);
  if (pending) clearTimeout(pending);
  VALIDATION_TIMEOUTS.delete(textarea);
};

export const EV_HANDLERS = {
  input: (event: Event) => {
    scheduleTextareaValidation(event.currentTarget as HTMLTextAreaElement);
  },
};
