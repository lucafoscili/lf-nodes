import { buildAssetsUrl } from '../config';

export interface WorkflowCardPresentation {
  summary: string;
  hero?: { url: string; alt: string };
}

const visibleLine = (value: unknown, limit: number): string | undefined => {
  if (
    typeof value !== 'string' ||
    value.length > limit ||
    /[\u0000-\u001f\u007f-\u009f\u2028\u2029]/u.test(value)
  ) {
    return undefined;
  }
  return value.trim().replace(/\s+/gu, ' ') || undefined;
};

/** Catalogue heroes are local raster assets, not arbitrary image or output URLs. */
export const resolveWorkflowHeroUrl = (asset: unknown): string | undefined => {
  if (
    typeof asset !== 'string' ||
    !asset ||
    asset.length > 240 ||
    asset.includes('..') ||
    !/\.(?:avif|jpe?g|png|webp)$/i.test(asset) ||
    !asset
      .split('/')
      .every((part) => /^[a-z0-9][a-z0-9._-]*$/i.test(part) && !part.endsWith('.'))
  ) {
    return undefined;
  }

  try {
    const base = new URL(`${buildAssetsUrl().replace(/\/+$/, '')}/workflow-runner/heroes/`);
    const url = new URL(asset, base);
    if (url.origin !== window.location.origin || !url.pathname.startsWith(base.pathname)) {
      return undefined;
    }
    return url.href;
  } catch {
    return undefined;
  }
};

/** A malformed hero may disappear without discarding an otherwise useful summary. */
export const workflowCardPresentation = (value: unknown): WorkflowCardPresentation | undefined => {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return undefined;
  }
  const card = value as Record<string, unknown>;
  const summary = visibleLine(card.summary, 180);
  if (!summary) {
    return undefined;
  }

  const presentation: WorkflowCardPresentation = { summary };
  if (card.hero && typeof card.hero === 'object' && !Array.isArray(card.hero)) {
    const hero = card.hero as Record<string, unknown>;
    const url = resolveWorkflowHeroUrl(hero.asset);
    const alt = visibleLine(hero.alt, 500);
    if (url && alt) {
      presentation.hero = { url, alt };
    }
  }
  return presentation;
};
