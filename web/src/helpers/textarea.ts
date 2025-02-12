import { LogSeverity } from '../types/manager/manager';
import { TextareaCSS } from '../types/widgets/textarea';
import { getLfManager } from '../utils/common';

let VALIDATION_TIMEOUT: NodeJS.Timeout;

export const EV_HANDLERS = {
  //#region Input handler
  input: (e: Event) => {
    const textarea = e.currentTarget as HTMLTextAreaElement;

    const startValidationTimer = () => {
      const validateAndFormatJSON = async () => {
        try {
          const jsonObject = JSON.parse(textarea.value);
          const formattedJson = JSON.stringify(jsonObject, null, 2);
          if (formattedJson !== '{}') {
            textarea.title = '';
            textarea.value = formattedJson;
            textarea.classList.remove(TextareaCSS.WidgetError);
          }
        } catch (error) {
          getLfManager().log('Error parsing JSON', { error }, LogSeverity.Warning);
          textarea.classList.add(TextareaCSS.WidgetError);
          textarea.title = error;
        }
      };

      VALIDATION_TIMEOUT = setTimeout(validateAndFormatJSON, 2500);
    };

    clearTimeout(VALIDATION_TIMEOUT);
    startValidationTimer();
  },
  //#endregion
};
