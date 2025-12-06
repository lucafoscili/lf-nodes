import { ImageEditorFilters } from '../../../types/widgets/imageEditor';
import { BACKGROUND_SETTINGS } from './background';
import { BASIC_ADJUSTMENT_SETTINGS } from './basicAdjustments';
import { CREATIVE_EFFECT_SETTINGS } from './creativeEffects';
import { DIFFUSION_SETTINGS } from './diffusion';
import { DRAWING_SETTINGS } from './drawing';

export const SETTINGS: ImageEditorFilters = {
  ...BASIC_ADJUSTMENT_SETTINGS,
  ...BACKGROUND_SETTINGS,
  ...CREATIVE_EFFECT_SETTINGS,
  ...DRAWING_SETTINGS,
  ...DIFFUSION_SETTINGS,
};
