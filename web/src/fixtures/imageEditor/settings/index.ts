import { ImageEditorFilters } from '../../../types/widgets/imageEditor';
import { BASIC_ADJUSTMENT_SETTINGS } from './basicAdjustments';
import { CREATIVE_EFFECT_SETTINGS } from './creativeEffects';
import { DIFFUSION_SETTINGS, INPAINT_ADV } from './diffusion';
import { DRAWING_SETTINGS } from './drawing';

export const SETTINGS: ImageEditorFilters = {
  ...BASIC_ADJUSTMENT_SETTINGS,
  ...CREATIVE_EFFECT_SETTINGS,
  ...DRAWING_SETTINGS,
  ...DIFFUSION_SETTINGS,
};

export { INPAINT_ADV };
