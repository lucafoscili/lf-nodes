import {
  ImageEditorBrushIds,
  ImageEditorControls,
  ImageEditorFilters,
  ImageEditorLineIds,
  ImageEditorSliderIds,
  ImageEditorTextfieldIds,
  ImageEditorToggleIds,
} from '../../../types/widgets/imageEditor';

export const DRAWING_SETTINGS: Pick<ImageEditorFilters, 'brush' | 'line'> = {
  //#region Brush
  brush: {
    controlIds: ImageEditorBrushIds,
    hasCanvasAction: true,
    settings: { b64_canvas: '', color: '#FF0000', opacity: 0.2, size: 150 },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Size',
          controlType: ImageEditorControls.Slider,
          defaultValue: 150,
          id: ImageEditorSliderIds.Size,
          isMandatory: true,
          max: '500',
          min: '1',
          step: '1',
          title: 'Sets the size of the brush.',
        },
        {
          ariaLabel: 'Opacity',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.2,
          id: ImageEditorSliderIds.Opacity,
          isMandatory: true,
          max: '1',
          min: '0.05',
          step: '0.05',
          title: 'Sets the opacity of the brush.',
        },
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: 'Color',
          controlType: ImageEditorControls.Textfield,
          defaultValue: '#FF0000',
          id: ImageEditorTextfieldIds.Color,
          isMandatory: true,
          title: 'Sets the color of the brush stroke.',
          type: 'color',
        },
      ],
    },
  },
  //#endregion
  //#region Line
  line: {
    controlIds: ImageEditorLineIds,
    hasCanvasAction: true,
    settings: { color: '#FF0000', opacity: 1, points: [], size: 10, smooth: false },
    configs: {
      [ImageEditorControls.Canvas]: [],
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Size',
          controlType: ImageEditorControls.Slider,
          defaultValue: 10,
          id: ImageEditorSliderIds.Size,
          isMandatory: true,
          max: '500',
          min: '1',
          step: '1',
          title: 'Sets the size of the brush.',
        },
        {
          ariaLabel: 'Opacity',
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.Opacity,
          isMandatory: true,
          max: '1',
          min: '0.05',
          step: '0.05',
          title: 'Sets the opacity of the brush.',
        },
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: 'Color',
          controlType: ImageEditorControls.Textfield,
          defaultValue: '#FF0000',
          id: ImageEditorTextfieldIds.Color,
          isMandatory: true,
          title: 'Sets the color of the brush stroke.',
          type: 'color',
        },
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: 'Smooth',
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Smooth,
          title: 'Draws a smooth line.',
          off: 'false',
          on: 'true',
        },
      ],
    },
  },
  //#endregion
};
