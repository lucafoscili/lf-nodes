import { LfDataDataset } from '@lf-widgets/foundations';
import { SETTINGS } from './settings';
import { INPAINT_ADV } from './settings/diffusion';

export const TREE_DATA: LfDataDataset = {
  nodes: [
    //#region Settings
    {
      description: 'Tool configuration.',
      id: 'settings',
      icon: 'brush',
      value: 'Settings',
      children: [
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
      ],
    },
    //#endregion
    //#region Diffusion Tools
    {
      description: 'Diffusion-based retouching tools.',
      id: 'diffusion_tools',
      value: 'Diffusion Tools',
      icon: 'wand',
      children: [
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
        {
          description: 'Inpaint with advanced ROI controls.',
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(INPAINT_ADV),
            },
          },
          id: 'inpaint_adv',
          value: 'Inpaint (adv.)',
        },
        {
          description:
            'Outpaint beyond the current canvas. Brush along edges to choose which sides expand.',
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.outpaint),
            },
          },
          id: 'outpaint',
          value: 'Outpaint',
        },
      ],
    },
    //#endregion
    //#region Cutouts
    {
      description: 'Background removal and matting tools.',
      id: 'cutouts',
      value: 'Cutouts',
      icon: 'replace',
      children: [
        {
          description: 'Remove the background using rembg with optional solid fill.',
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.backgroundRemover),
            },
          },
          id: 'background_remover',
          value: 'Background remover',
        },
      ],
    },
    //#endregion
    //#region Basic Adjustments
    {
      description: 'Basic adjustments such as sharpening and color tuning.',
      id: 'basic_adjustments',
      value: 'Basic Adjustments',
      icon: 'settings',
      children: [
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
        {
          description: 'Sharpens edges using a classic unsharp mask pipeline.',
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.unsharpMask),
            },
          },
          id: 'unsharp_mask',
          value: 'Unsharp Mask',
        },
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
        {
          description: 'Adjusts the saturation.',
          cells: {
            lfCode: {
              shape: 'code',
              value: JSON.stringify(SETTINGS.saturation),
            },
          },
          id: 'saturation',
          value: 'Saturation',
        },
      ],
    },
    //#endregion
    //#region Creative Effects
    {
      description: 'Artistic filters, such as vignette effect and gaussian blur.',
      id: 'creative_effects',
      icon: 'palette',
      value: 'Creative Effects',
      children: [
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
      ],
    },
    //#endregion
  ],
};
