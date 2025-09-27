import { LfDataColumn, LfDataDataset } from '@lf-widgets/foundations';
import { ImageEditorColumnId, ImageEditorControlConfig } from '../../types/widgets/imageEditor';

//#region Path
export function getPathColumn(dataset: LfDataDataset): LfDataColumn | null {
  return dataset?.columns?.find((c) => c.id === ImageEditorColumnId.Path) || null;
}
//#endregion

//#region Status
export function getStatusColumn(dataset: LfDataDataset): LfDataColumn | null {
  return dataset?.columns?.find((c) => c.id === ImageEditorColumnId.Status) || null;
}
//#endregion

//#region Label
export function parseLabel(data: ImageEditorControlConfig) {
  return data.isMandatory ? `${data.ariaLabel}*` : data.ariaLabel;
}
//#endregion
