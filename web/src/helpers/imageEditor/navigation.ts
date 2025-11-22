import { LogSeverity } from '../../types/manager/manager';
import { ImageEditorState } from '../../types/widgets/imageEditor';
import { getLfManager, normalizeDirectoryRequest } from '../../utils/common';

//#region syncNavigationDirectoryControl
/**
 * Synchronizes the navigation directory textfield of the image viewer to the provided directory value.
 *
 * The function:
 * - Normalizes the requested directory value using normalizeDirectoryRequest.
 * - Attempts to retrieve the image viewer components via imageviewer.getComponents().
 * - Locates the navigation textfield and uses its getValue and setValue methods (if available).
 * - Skips updating if the current textfield value equals the normalized target.
 * - Sets state.isSyncingDirectory to true while performing the update and ensures it is reset to false in a finally block.
 * - Handles missing components or missing getValue/setValue methods gracefully (no-op).
 * - Catches and logs any errors using getLfManager().log with Warning severity; errors are suppressed (not rethrown).
 *
 * @param state - The ImageEditorState containing UI element references and the isSyncingDirectory flag.
 * @param directoryValue - The desired directory value to synchronize into the navigation textfield (may be undefined).
 * @returns A Promise that resolves when synchronization completes.
 */
export const syncNavigationDirectoryControl = async (
  state: ImageEditorState,
  directoryValue: string | undefined,
): Promise<void> => {
  const { imageviewer } = state.elements;
  const { navigation } = await imageviewer.getComponents();
  const { textfield } = navigation;

  const current = await textfield.getValue();
  const target = normalizeDirectoryRequest(directoryValue);
  if ((current ?? '') === target) {
    return;
  }

  try {
    state.isSyncingDirectory = true;
    await textfield.setValue(target);
  } catch (error) {
    getLfManager().log('Failed to synchronize directory input.', { error }, LogSeverity.Warning);
  } finally {
    state.isSyncingDirectory = false;
  }
};
//#endregion
