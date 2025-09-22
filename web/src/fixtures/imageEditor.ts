import { LfDataDataset } from '@lf-widgets/foundations';
import {
  ImageEditorBlendIds,
  ImageEditorBloomIds,
  ImageEditorBrightnessIds,
  ImageEditorBrushIds,
  ImageEditorClarityIds,
  ImageEditorContrastIds,
  ImageEditorControls,
  ImageEditorDesaturateIds,
  ImageEditorFilmGrainIds,
  ImageEditorFilters,
  ImageEditorGaussianBlurIds,
  ImageEditorInpaintIds,
  ImageEditorLineIds,
  ImageEditorSaturationIds,
  ImageEditorSepiaIds,
  ImageEditorSliderIds,
  ImageEditorSplitToneIds,
  ImageEditorTextfieldIds,
  ImageEditorTiltShiftIds,
  ImageEditorToggleIds,
  ImageEditorVibranceIds,
  ImageEditorVignetteIds,
} from '../types/widgets/imageEditor';

export const SETTINGS: ImageEditorFilters = {
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

  //#region Brush
  brush: {
    controlIds: ImageEditorBrushIds,
    hasCanvasAction: true,
    settings: { b64_canvas: '', color: '#FF0000', opacity: 1, size: 10 },
    configs: {
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
            'Controls the total intensity of the desaturation. 0 is no effect, 1 is fully desaturated.',
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

  //#region Film grain
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

  //#region Gaussian blur
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

  //#region Inpaint
  inpaint: {
    controlIds: ImageEditorInpaintIds,
    hasCanvasAction: true,
    requiresManualApply: true,
    settings: {
      b64_canvas: '',
      denoise_percentage: 40,
      steps: 16,
      positive_prompt: '',
      negative_prompt: '',
    },
    configs: {
      [ImageEditorControls.Slider]: [
        {
          ariaLabel: 'Denoise percentage',
          controlType: ImageEditorControls.Slider,
          defaultValue: 40,
          id: ImageEditorSliderIds.DenoisePercentage,
          isMandatory: true,
          max: '100',
          min: '0',
          step: '1',
          title: 'Noise applied during inpaint. 0 keeps original pixels, 100 fully regenerates.',
        },
        {
          ariaLabel: 'Steps',
          controlType: ImageEditorControls.Slider,
          defaultValue: 16,
          id: ImageEditorSliderIds.Steps,
          isMandatory: true,
          max: '30',
          min: '1',
          step: '1',
          title: 'Diffusion steps used for the inpaint sampler.',
        },
      ],
      [ImageEditorControls.Textfield]: [
        {
          ariaLabel: 'Positive prompt',
          controlType: ImageEditorControls.Textfield,
          defaultValue: '',
          id: ImageEditorTextfieldIds.PositivePrompt,
          isMandatory: false,
          title: 'Prompt applied to masked pixels.',
          type: 'text',
        },
        {
          ariaLabel: 'Negative prompt',
          controlType: ImageEditorControls.Textfield,
          defaultValue: '',
          id: ImageEditorTextfieldIds.NegativePrompt,
          isMandatory: false,
          title: 'Negative prompt applied to masked pixels.',
          type: 'text',
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

  //#region Split tone
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

  //#region Tilt-shift
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

export const TREE_DATA: LfDataDataset = {
  nodes: [
    {
      description: 'Tool configuration.',
      id: 'settings',
      icon: 'brush',
      value: 'Settings',
      children: [
        //#region Brush
        {
          description: 'Brush configuration.',
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.brush),
            },
          },
          id: 'brush',
          value: 'Brush',
        },
        //#endregion
      ],
    },
    {
      description: 'Diffusion-based retouching tools.',
      id: 'diffusion_tools',
      value: 'Diffusion Tools',
      icon: 'wand',
      children: [
        //#region Inpaint
        {
          description: 'Inpaint masked areas using the connected diffusion model.',
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.inpaint),
            },
          },
          id: 'inpaint',
          value: 'Inpaint',
        },
        //#endregion
      ],
    },
    {
      description: 'Basic adjustments such as sharpening and color tuning.',
      id: 'basic_adjustments',
      value: 'Basic Adjustments',
      icon: 'settings',
      children: [
        //#region Brightness
        {
          description: 'Adjusts the brightness.',
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.brightness),
            },
          },
          id: 'brightness',
          value: 'Brightness',
        },
        //#endregion

        //#region Clarity
        {
          description: 'Simulates the Lightroom clarity effect.',
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.clarity),
            },
          },
          id: 'clarity',
          value: 'Clarity',
        },
        //#endregion

        //#region Contrast
        {
          description: 'Adjusts the contrast.',
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.contrast),
            },
          },
          id: 'contrast',
          value: 'Contrast',
        },
        //#endregion

        //#region Desaturate
        {
          description: 'Reduces the saturation.',
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.desaturate),
            },
          },
          id: 'desaturate',
          value: 'Desaturate',
        },
        //#endregion

        //#region Saturation
        {
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.saturation),
            },
          },
          description: 'Adjusts the saturation.',
          id: 'saturation',
          value: 'Saturation',
        },
        //#endregion
      ],
    },
    {
      description: 'Artistic filters, such as vignette effect and gaussian blur.',
      id: 'creative_effects',
      icon: 'palette',
      value: 'Creative Effects',
      children: [
        //#region Blend
        {
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.blend),
            },
          },
          description: 'Blends a color layer onto the image.',
          id: 'blend',
          value: 'Blend',
        },
        //#endregion

        //#region Bloom
        {
          description: 'Applies a bloom effect.',
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.bloom),
            },
          },
          id: 'bloom',
          value: 'Bloom',
        },
        //#endregion

        //#region Film grain
        {
          description: 'Applies a film grain effect.',
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.filmGrain),
            },
          },
          id: 'film_grain',
          value: 'Film grain',
        },
        //#endregion

        //#region Gaussian blur
        {
          description: 'Blurs the image.',
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.gaussianBlur),
            },
          },
          id: 'gaussian_blur',
          value: 'Gaussian blur',
        },
        //#endregion

        //#region Line
        {
          description: 'Draws a line.',
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.line),
            },
          },
          id: 'line',
          value: 'Line',
        },
        //#endregion

        //#region Sepia
        {
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.sepia),
            },
          },
          description: 'Applies a sepia effect to the image.',
          id: 'sepia',
          value: 'Sepia',
        },
        //#endregion

        //#region Split tone
        {
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.splitTone),
            },
          },
          description: 'Applies a split tone effect to the image.',
          id: 'split_tone',
          value: 'Split tone',
        },
        //#endregion

        //#region Tilt-shift
        {
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.tiltShift),
            },
          },
          description: 'Applies a tilt-shift effect to the image.',
          id: 'tilt_shift',
          value: 'Tilt-shift',
        },
        //#endregion

        //#region Vibrance
        {
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.vibrance),
            },
          },
          description: 'Applies a vibrance effect to the image.',
          id: 'vibrance',
          value: 'Vibrance',
        },
        //#endregion

        //#region Vignette
        {
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.vignette),
            },
          },
          description: 'Applies a vignetting effect to the image.',
          id: 'vignette',
          value: 'Vignette',
        },
        //#endregion
      ],
    },
  ],
};
