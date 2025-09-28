import {
  ImageEditorBackgroundRemoverIds,
  ImageEditorControls,
  ImageEditorFilters,
  ImageEditorTextfieldIds,
  ImageEditorToggleIds,
} from '../../../types/widgets/imageEditor';

export const BACKGROUND_SETTINGS: Pick<ImageEditorFilters, 'backgroundRemover'> = {
  backgroundRemover: {
    controlIds: ImageEditorBackgroundRemoverIds,
    settings: {
      color: '#000000',
      transparent_background: true,
    },
    configs: {
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: 'Background color',
          controlType: ImageEditorControls.Textfield,
          defaultValue: '#000000',
          id: ImageEditorTextfieldIds.Color,
          isMandatory: true,
          title: 'Used to fill the removed background when transparency is disabled.',
          type: 'color',
        },
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: 'Transparent background',
          controlType: ImageEditorControls.Toggle,
          defaultValue: true,
          id: ImageEditorToggleIds.TransparentBackground,
          off: 'false',
          on: 'true',
          title: 'Keep an alpha channel instead of filling the background with the selected color.',
        },
      ],
    },
  },
};
