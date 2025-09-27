import {
  ImageEditorBrightnessIds,
  ImageEditorClarityIds,
  ImageEditorContrastIds,
  ImageEditorControls,
  ImageEditorDesaturateIds,
  ImageEditorFilters,
  ImageEditorSaturationIds,
  ImageEditorSliderIds,
  ImageEditorToggleIds,
  ImageEditorUnsharpMaskIds,
} from '../../../types/widgets/imageEditor';

export const BASIC_ADJUSTMENT_SETTINGS: Pick<
  ImageEditorFilters,
  'brightness' | 'clarity' | 'contrast' | 'desaturate' | 'saturation' | 'unsharpMask'
> = {
  //#region Brightness
  brightness: {
    controlIds: ImageEditorBrightnessIds,
    settings: {
      strength: 0,
      gamma: 0,
      localized: false,
      midpoint: 0.5,
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Brightness Strength',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Strength,
          isMandatory: true,
          max: '1',
          min: '-1',
          step: '0.05',
          title:
            'Adjust the brightness of the image. Negative values darken, positive values brighten.',
        },
        {
          ariaLabel: 'Gamma',
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.Gamma,
          max: '3',
          min: '0.1',
          step: '0.1',
          title: 'Adjust the gamma correction. Values < 1 brighten shadows, > 1 darken highlights.',
        },
        {
          ariaLabel: 'Midpoint',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.5,
          id: ImageEditorSliderIds.Midpoint,
          max: '1',
          min: '0',
          step: '0.05',
          title: 'Defines the tonal midpoint for brightness scaling.',
        },
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: 'Localized Brightness',
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Localized,
          off: 'false',
          on: 'true',
          title: 'Enhance brightness locally in darker regions.',
        },
      ],
    },
  },
  //#endregion
  //#region Clarity
  clarity: {
    controlIds: ImageEditorClarityIds,
    settings: {
      strength: 0,
      sharpen_amount: 0,
      blur_kernel_size: 1,
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Clarity Strength',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Strength,
          isMandatory: true,
          max: '5',
          min: '0',
          step: '0.1',
          title: 'Controls the amount of contrast enhancement in midtones.',
        },
        {
          ariaLabel: 'Sharpen Amount',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.SharpenAmount,
          max: '5',
          min: '0',
          step: '0.1',
          title: 'Controls how much sharpening is applied to the image.',
        },
        {
          ariaLabel: 'Blur Kernel Size',
          controlType: ImageEditorControls.Slider,
          defaultValue: 7,
          id: ImageEditorSliderIds.BlurKernelSize,
          max: '15',
          min: '1',
          step: '2',
          title:
            'Controls the size of the Gaussian blur kernel. Higher values mean more smoothing.',
        },
      ],
    },
  },
  //#endregion
  //#region Contrast
  contrast: {
    controlIds: ImageEditorContrastIds,
    settings: {
      strength: 0,
      localized: false,
      midpoint: 0,
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Contrast Strength',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Strength,
          isMandatory: true,
          max: '1',
          min: '-1',
          step: '0.05',
          title:
            'Controls the intensity of the contrast adjustment. 1.0 is no change, below 1 reduces contrast, above 1 increases contrast.',
        },
        {
          ariaLabel: 'Midpoint',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.5,
          id: ImageEditorSliderIds.Midpoint,
          max: '1',
          min: '0',
          step: '0.05',
          title: 'Defines the tonal midpoint for contrast scaling.',
        },
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: 'Localized Contrast',
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Localized,
          off: 'false',
          on: 'true',
          title: 'Apply contrast enhancement locally to edges and textures.',
        },
      ],
    },
  },
  //#endregion
  //#region Desaturate
  desaturate: {
    controlIds: ImageEditorDesaturateIds,
    settings: {
      r_channel: 1,
      g_channel: 1,
      b_channel: 1,
      strength: 0,
    },
    configs: {
      slider: [
        {
          ariaLabel: 'Desaturation strength',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Strength,
          isMandatory: true,
          max: '1',
          min: '0',
          step: '0.05',
          title:
            'Controls the intensity of the desaturation. 0 is no effect, 1 is fully desaturated.',
        },
        {
          ariaLabel: 'Red channel level',
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.RedChannel,
          max: '1',
          min: '0',
          step: '0.05',
          title:
            'Controls the intensity of the red channel desaturation relative to the total strength of the filter.',
        },
        {
          ariaLabel: 'Green channel level',
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.GreenChannel,
          max: '1',
          min: '0',
          step: '0.05',
          title:
            'Controls the intensity of the green channel desaturation relative to the total strength of the filter.',
        },
        {
          ariaLabel: 'Blue channel level',
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.BlueChannel,
          max: '1',
          min: '0',
          step: '0.05',
          title:
            'Controls the intensity of the blue channel desaturation relative to the total strength of the filter.',
        },
      ],
    },
  },
  //#endregion
  //#region Saturation
  saturation: {
    controlIds: ImageEditorSaturationIds,
    settings: {
      intensity: 1,
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Saturation Intensity',
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: '5',
          min: '0',
          step: '0.1',
          title:
            'Controls the intensity of the saturation adjustment. 1.0 is no change, below 1 reduces saturation, above 1 increases saturation.',
        },
      ],
    },
  },
  //#endregion
  //#region Unsharp Mask
  unsharpMask: {
    controlIds: ImageEditorUnsharpMaskIds,
    settings: {
      amount: 0.5,
      radius: 5,
      sigma: 1.0,
      threshold: 0,
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Sharpen Amount',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.5,
          id: ImageEditorSliderIds.Amount,
          isMandatory: true,
          max: '5',
          min: '0',
          step: '0.05',
          title: 'Overall strength applied to the high-frequency detail mask.',
        },
        {
          ariaLabel: 'Radius',
          controlType: ImageEditorControls.Slider,
          defaultValue: 5,
          id: ImageEditorSliderIds.Radius,
          isMandatory: true,
          max: '31',
          min: '1',
          step: '2',
          title: 'Gaussian blur kernel size (odd numbers give the best results).',
        },
        {
          ariaLabel: 'Sigma',
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.Sigma,
          isMandatory: true,
          max: '5',
          min: '0.1',
          step: '0.1',
          title: 'Gaussian blur sigma controlling feather softness around edges.',
        },
        {
          ariaLabel: 'Threshold',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Threshold,
          isMandatory: true,
          max: '1',
          min: '0',
          step: '0.01',
          title: 'Skip sharpening for pixels below this normalized contrast level.',
        },
      ],
    },
    //#endregion
  },
};
