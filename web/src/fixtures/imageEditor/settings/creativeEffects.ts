import {
  ImageEditorBlendIds,
  ImageEditorBloomIds,
  ImageEditorControls,
  ImageEditorFilmGrainIds,
  ImageEditorFilters,
  ImageEditorGaussianBlurIds,
  ImageEditorSepiaIds,
  ImageEditorSliderIds,
  ImageEditorSplitToneIds,
  ImageEditorTextfieldIds,
  ImageEditorTiltShiftIds,
  ImageEditorToggleIds,
  ImageEditorVibranceIds,
  ImageEditorVignetteIds,
} from '../../../types/widgets/imageEditor';

export const CREATIVE_EFFECT_SETTINGS: Pick<
  ImageEditorFilters,
  | 'blend'
  | 'bloom'
  | 'filmGrain'
  | 'gaussianBlur'
  | 'sepia'
  | 'splitTone'
  | 'tiltShift'
  | 'vibrance'
  | 'vignette'
> = {
  //#region Blend
  blend: {
    controlIds: ImageEditorBlendIds,
    settings: {
      color: '#FF0000',
      opacity: 0.5,
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Opacity',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Opacity,
          isMandatory: true,
          max: '1',
          min: '0',
          step: '0.01',
          title: 'Adjust the opacity of the blended layer.',
        },
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: 'Color',
          controlType: ImageEditorControls.Textfield,
          defaultValue: '#FF0000',
          id: ImageEditorTextfieldIds.Color,
          isMandatory: true,
          title: 'Sets the solid color that will be blended onto the image.',
          type: 'color',
        },
      ],
    },
  },
  //#endregion
  //#region Bloom
  bloom: {
    controlIds: ImageEditorBloomIds,
    settings: {
      intensity: 0.6,
      radius: 15,
      threshold: 0.8,
      tint: '#FFFFFF',
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Bloom Intensity',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.6,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: '2',
          min: '0',
          step: '0.05',
          title:
            'How strong the bloom reads after compositing. 1.0 = add the blurred highlights at full strength.',
        },
        {
          ariaLabel: 'Bloom Radius',
          controlType: ImageEditorControls.Slider,
          defaultValue: 15,
          id: ImageEditorSliderIds.Radius,
          isMandatory: true,
          max: '127',
          min: '3',
          step: '2',
          title:
            'Blur radius in pixels (odd numbers only). Bigger radius → softer, more cinematic glow.',
        },
        {
          ariaLabel: 'Threshold',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.8,
          id: ImageEditorSliderIds.Threshold,
          isMandatory: true,
          max: '1',
          min: '0',
          step: '0.01',
          title:
            'Bright-pass cutoff. 0 = everything glows, 1 = nothing glows. For dim scenes start around 0.15-0.35.',
        },
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: 'Tint Color',
          controlType: ImageEditorControls.Textfield,
          defaultValue: '#FFFFFF',
          id: ImageEditorTextfieldIds.Color,
          title: 'Hex color for the glow (e.g., FFCCAA). Pure white FFFFFF keeps original hue.',
          type: 'color',
        },
      ],
    },
  },
  //#endregion
  //#region Film Grain
  filmGrain: {
    controlIds: ImageEditorFilmGrainIds,
    settings: { intensity: 0, size: 1, soft_blend: false, tint: '#FFFFFF' },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Intensity',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: '1',
          min: '0',
          step: '0.05',
          title: 'Sets the strength of the filter.',
        },
        {
          ariaLabel: 'Size',
          controlType: ImageEditorControls.Slider,
          defaultValue: 1,
          id: ImageEditorSliderIds.Size,
          isMandatory: true,
          max: '5',
          min: '0.5',
          step: '0.1',
          title: "Sets the size of the noise's granularity.",
        },
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: 'Tint',
          controlType: ImageEditorControls.Textfield,
          defaultValue: '#FFFFFF',
          id: ImageEditorTextfieldIds.Tint,
          isMandatory: true,
          title: 'Hexadecimal color (default is FFFFFF for no tint).',
          type: 'color',
        },
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: 'Soft blend',
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.SoftBlend,
          title: 'If True, uses a soft blending mode for the grain.',
          off: 'false',
          on: 'true',
        },
      ],
    },
  },
  //#endregion
  //#region Gaussian Blur
  gaussianBlur: {
    controlIds: ImageEditorGaussianBlurIds,
    settings: {
      blur_kernel_size: 1,
      blur_sigma: 0,
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Blur Sigma',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.BlurSigma,
          max: '10',
          min: '0.1',
          step: '0.1',
          title: 'Standard deviation for the Gaussian kernel. Controls blur intensity.',
        },
        {
          ariaLabel: 'Blur Kernel Size',
          controlType: ImageEditorControls.Slider,
          defaultValue: 7,
          id: ImageEditorSliderIds.BlurKernelSize,
          max: '51',
          min: '1',
          step: '2',
          title:
            'Controls the size of the Gaussian blur kernel. Higher values mean more smoothing.',
        },
      ],
    },
  },
  //#endregion
  //#region Sepia
  sepia: {
    controlIds: ImageEditorSepiaIds,
    settings: {
      intensity: 0,
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Sepia Intensity',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: '1',
          min: '0',
          step: '0.01',
          title: 'Controls the intensity of the sepia effect.',
        },
      ],
    },
  },
  //#endregion
  //#region Split Tone
  splitTone: {
    controlIds: ImageEditorSplitToneIds,
    settings: {
      balance: 0.5,
      highlights: '#FFAA55',
      intensity: 0.6,
      shadows: '#0066FF',
      softness: 0.25,
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Intensity',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.6,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: '2',
          min: '0',
          step: '0.05',
          title: 'Strength of the tint applied.',
        },
        {
          ariaLabel: 'Balance',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.5,
          id: ImageEditorSliderIds.Balance,
          isMandatory: true,
          max: '1',
          min: '0',
          step: '0.01',
          title: 'Luminance pivot. 0 = lift even deep blacks; 1 = tint only the brightest pixels.',
        },
        {
          ariaLabel: 'Softness',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.25,
          id: ImageEditorSliderIds.Softness,
          isMandatory: true,
          max: '0.5',
          min: '0.01',
          step: '0.01',
          title: 'Width of the transition band around the balance value.',
        },
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: 'Highlights',
          controlType: ImageEditorControls.Textfield,
          defaultValue: '#FFAA55',
          id: ImageEditorTextfieldIds.Highlights,
          title: 'Hex colour applied to highlights (e.g. FFAA55).',
          type: 'color',
        },
        {
          ariaLabel: 'Shadows',
          controlType: ImageEditorControls.Textfield,
          defaultValue: '#0066FF',
          id: ImageEditorTextfieldIds.Shadows,
          title: 'Hex colour applied to shadows (e.g. 0066FF).',
          type: 'color',
        },
      ],
    },
  },
  //#endregion
  //#region Tilt Shift
  tiltShift: {
    controlIds: ImageEditorTiltShiftIds,
    settings: {
      focus_position: 0.5,
      focus_size: 0.25,
      radius: 25,
      smooth: false,
      vertical: false,
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Focus Position',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.5,
          id: ImageEditorSliderIds.FocusPosition,
          isMandatory: true,
          max: '1',
          min: '0',
          step: '0.01',
          title: 'Vertical center of the sharp band (0 = top, 1 = bottom).',
        },
        {
          ariaLabel: 'Focus Size',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0.25,
          id: ImageEditorSliderIds.FocusSize,
          isMandatory: true,
          max: '0.9',
          min: '0.05',
          step: '0.01',
          title: 'Height of the sharp zone as a fraction of the image.',
        },
        {
          ariaLabel: 'Blur Radius',
          controlType: ImageEditorControls.Slider,
          defaultValue: 25,
          id: ImageEditorSliderIds.Radius,
          isMandatory: true,
          max: '151',
          min: '3',
          step: '2',
          title:
            'Gaussian radius for out-of-focus areas. Higher values mean more blur and less detail.',
        },
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: 'Smooth Fall-off Curve',
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Smooth,
          off: 'linear',
          on: 'smooth',
          title:
            'Fall-off curve of blur vs distance. Linear means a constant fall-off, smooth means a gradual transition.',
        },
        {
          ariaLabel: 'Vertical Orientation',
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Vertical,
          off: 'horizontal',
          on: 'vertical',
          title:
            'Direction of the focus band. Horizontal means the focus band is horizontal, vertical means it is vertical.',
        },
      ],
    },
  },
  //#endregion
  //#region Vibrance
  vibrance: {
    controlIds: ImageEditorVibranceIds,
    settings: {
      intensity: 0,
      protect_skin: true,
      clip_soft: true,
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Vibrance Intensity',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: '2',
          min: '-1',
          step: '0.05',
          title:
            'Controls the intensity of the vibrance adjustment. Negative values reduce vibrance, positive values increase it.',
        },
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: 'Protect Skin Tones',
          controlType: ImageEditorControls.Toggle,
          defaultValue: true,
          id: ImageEditorToggleIds.ProtectSkin,
          off: 'false',
          on: 'true',
          title: 'If true, skin tones are less affected by the vibrance adjustment.',
        },
        {
          ariaLabel: 'Clip Softly',
          controlType: ImageEditorControls.Toggle,
          defaultValue: true,
          id: ImageEditorToggleIds.ClipSoft,
          off: 'false',
          on: 'true',
          title: 'If true, saturation is rolled off near maximum to avoid clipping.',
        },
      ],
    },
  },
  //#endregion
  //#region Vignette
  vignette: {
    controlIds: ImageEditorVignetteIds,
    settings: {
      intensity: 0,
      radius: 0,
      shape: false,
      color: '000000',
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Vignette Intensity',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Intensity,
          isMandatory: true,
          max: '1',
          min: '0',
          step: '0.05',
          title: 'Controls the darkness of the vignette effect. Higher values mean darker edges.',
        },
        {
          ariaLabel: 'Vignette Radius',
          controlType: ImageEditorControls.Slider,
          defaultValue: 0,
          id: ImageEditorSliderIds.Radius,
          isMandatory: true,
          max: '1',
          min: '0',
          step: '0.05',
          title: 'Controls the size of the vignette effect. Lower values mean a smaller vignette.',
        },
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: 'Color',
          controlType: ImageEditorControls.Textfield,
          defaultValue: '#000000',
          id: ImageEditorTextfieldIds.Color,
          title: 'Sets the color of the vignette.',
          type: 'color',
        },
      ],
      [ImageEditorControls.Toggle]: [
        {
          ariaLabel: 'Circular',
          controlType: ImageEditorControls.Toggle,
          defaultValue: false,
          id: ImageEditorToggleIds.Shape,
          off: 'elliptical',
          on: 'circular',
          title: 'Selects the shape of the vignette effect, defaults to elliptical.',
        },
      ],
    },
  },
  //#endregion
};
