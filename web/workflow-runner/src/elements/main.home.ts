import {
  LfCardEventPayload,
  LfDataDataset,
  LfDataNode,
  LfImageEventPayload,
  LfMasonryEventPayload,
} from '@lf-widgets/foundations/dist';
import { getLfFramework } from '@lf-widgets/framework';
import { masonryHandler } from '../handlers/masonry';
import { WorkflowAPIDataset, WorkflowAPIItem, WorkflowAPIKind } from '../types/api';
import { WorkflowSectionController } from '../types/section';
import { WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES, UI_CONSTANTS } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { workflowCardPresentation } from '../utils/workflow-card';
import { isWorkflowOrchestra, normalizeWorkflowKind } from '../utils/workflow-kind';
import { MAIN_CLASSES } from './layout.main';

//#region CSS Classes
const { theme } = getLfFramework();
const ROOT_CLASS = 'home-section';
export const HOME_MASONRY_CLASS = theme.bemClass(ROOT_CLASS, 'masonry');
export const HOME_CARD_OPEN_ID = 'workflow-card-open';
export const HOME_CLASSES = {
  _: theme.bemClass(ROOT_CLASS),
  blockMasonry: theme.bemClass(ROOT_CLASS, 'block-masonry'),
  blockRail: theme.bemClass(ROOT_CLASS, 'block-rail'),
  catalogue: theme.bemClass(ROOT_CLASS, 'catalogue'),
  description: theme.bemClass(ROOT_CLASS, 'description'),
  h1: theme.bemClass(ROOT_CLASS, 'title-h1'),
  orchestraMasonry: theme.bemClass(ROOT_CLASS, 'orchestra-masonry'),
  orchestraRail: theme.bemClass(ROOT_CLASS, 'orchestra-rail'),
  title: theme.bemClass(ROOT_CLASS, 'title'),
} as const;
//#endregion

//#region Helpers
type CatalogueKind = WorkflowAPIKind;

const ORCHESTRA_CARD_ACCENT = [
  '.material-layout {',
  '  border-inline-start: 4px double rgb(var(--lf-card-color-primary, var(--lf-color-secondary)));',
  '}',
].join('\n');
const ORCHESTRA_CARD_STYLE = `${ORCHESTRA_CARD_ACCENT}\n.material-layout__text-section { height: 100%; }`;
const HERO_CARD_STYLE = [
  // LF's adopted base stylesheet follows lfStyle; :host makes these overrides
  // win without relying on insertion order or changing the shared widget.
  ':host .material-layout { height: auto; overflow: hidden; }',
  ':host .material-layout__cover-section {',
  '  aspect-ratio: 16 / 9; flex: none; height: auto; overflow: hidden;',
  '  --lf-image-object-fit: contain;',
  '}',
  ':host .material-layout__text-section { height: auto; min-width: 0; overflow: hidden; }',
  ':host .material-layout .text-content__description { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }',
  ':host .material-layout--has-actions { padding-bottom: 0; }',
  ':host .material-layout__actions-section { position: static; height: auto; padding: 0 .5em .35em; }',
].join('\n');

const _kind = (node: WorkflowAPIItem): CatalogueKind => normalizeWorkflowKind(node.kind);

const _fallbackStageLabel = (value: string) =>
  value
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());

const _stageTrail = (node: WorkflowAPIItem, labels: Map<string, string>) => {
  if (!isWorkflowOrchestra(node) || !node.stages?.length) {
    return '';
  }
  const workflowCounts = node.stages.reduce<Map<string, number>>((counts, stage) => {
    counts.set(stage.workflowId, (counts.get(stage.workflowId) || 0) + 1);
    return counts;
  }, new Map());
  return node.stages
    .map((stage) => {
      const blockLabel = labels.get(stage.workflowId);
      if (!blockLabel) {
        return _fallbackStageLabel(stage.id);
      }
      return (workflowCounts.get(stage.workflowId) || 0) > 1
        ? `${_fallbackStageLabel(stage.id)} · ${blockLabel}`
        : blockLabel;
    })
    .join(' → ');
};

const _createDataset = (
  nodes: WorkflowAPIItem[],
  labels: Map<string, string>,
  kind: CatalogueKind,
  failedHeroes: Set<string>,
) => {
  const root: LfDataNode = {
    cells: {},
    id: 'root',
    value: kind === 'orchestra' ? 'Orchestras' : 'Blocks',
  };

  nodes
    .filter((node) => _kind(node) === kind)
    .forEach((node) => {
      const id = node.id;
      const blockCount = node.stages?.length || 0;
      const subtitle =
        kind === 'orchestra'
          ? blockCount
            ? `ORCHESTRA · ${blockCount} ${blockCount === 1 ? 'BLOCK' : 'BLOCKS'}`
            : 'ORCHESTRA'
          : node.category;
      const trail = _stageTrail(node, labels);
      const presentation = workflowCardPresentation(node.card);
      const hero = presentation?.hero;
      const description =
        presentation?.summary || [trail, node.description].filter(Boolean).join('\n');
      root.cells[id] = {
        htmlProps: {
          dataset: { workflowKind: kind },
        },
        lfDataset: {
          nodes: [
            {
              cells: {
                '1': {
                  value: String(node.value),
                },
                '2': {
                  value: subtitle,
                },
                '3': {
                  value: description,
                },
                ...(hero && !failedHeroes.has(hero.url)
                  ? {
                      hero: {
                        shape: 'image' as const,
                        value: hero.url,
                        lfHtmlAttributes: { alt: hero.alt },
                      },
                    }
                  : {}),
                open: {
                  shape: 'button' as const,
                  value: '',
                  htmlProps: { id: HOME_CARD_OPEN_ID },
                  lfLabel: 'Open',
                  lfAriaLabel: `Open ${String(node.value)}`,
                  lfStyling: 'flat' as const,
                  lfUiSize: 'small' as const,
                  lfUiState:
                    kind === 'orchestra' ? ('secondary' as const) : ('primary' as const),
                },
              },
              id,
            },
          ],
        },
        ...(presentation
          ? {
              lfSizeY: 'auto',
              lfStyle: [
                HERO_CARD_STYLE,
                kind === 'orchestra' ? ORCHESTRA_CARD_ACCENT : '',
              ].join('\n'),
              ...(kind === 'orchestra' ? { lfUiState: 'secondary' as const } : {}),
            }
          : kind === 'orchestra'
          ? {
              lfStyle: ORCHESTRA_CARD_STYLE,
              lfUiState: 'secondary' as const,
            }
          : {}),
        shape: 'card',
        value: '',
      };
    });

  return {
    count: Object.keys(root.cells).length,
    dataset: { nodes: [root] } satisfies LfDataDataset,
  };
};

// LF forwards image errors through card and masonry custom events. Replace the
// dataset as well as the live card so a later masonry resize cannot restore it.
const _recoverHero = (e: CustomEvent<LfMasonryEventPayload>, failedHeroes: Set<string>) => {
  const masonry = e.detail.comp;
  const cardEvent = e.detail.originalEvent as CustomEvent<LfCardEventPayload>;
  const imageEvent = cardEvent?.detail?.originalEvent as CustomEvent<LfImageEventPayload>;
  const card = cardEvent?.detail?.comp;
  const image = imageEvent?.detail?.comp;
  if (
    cardEvent?.detail?.eventType !== 'lf-event' ||
    card?.rootElement?.tagName.toLowerCase() !== 'lf-card' ||
    imageEvent?.detail?.eventType !== 'error' ||
    image?.rootElement?.tagName.toLowerCase() !== 'lf-image'
  ) {
    return;
  }
  const id = card.lfDataset?.nodes?.[0]?.id;
  const root = masonry.lfDataset?.nodes?.[0];
  const cell = root?.cells?.[id];
  if (cell?.shape !== 'card') {
    return;
  }
  const node = cell?.lfDataset?.nodes?.[0];
  const hero = node?.cells?.hero;
  if (hero?.shape !== 'image' || hero.value !== image.lfValue) {
    return;
  }

  failedHeroes.add(String(hero.value));
  const cells = { ...node.cells };
  delete cells.hero;
  const dataset = { ...cell.lfDataset, nodes: [{ ...node, cells }] };
  card.lfDataset = dataset;
  masonry.lfDataset = {
    ...masonry.lfDataset,
    nodes: [{ ...root, cells: { ...root.cells, [id]: { ...cell, lfDataset: dataset } } }],
  };
};

const _masonry = (store: WorkflowStore, className: string, failedHeroes: Set<string>) => {
  const masonry = document.createElement('lf-masonry');
  masonry.className = `${HOME_MASONRY_CLASS} ${className}`;
  masonry.lfShape = 'card';
  masonry.lfStyle = UI_CONSTANTS.MASONRY_STYLE;
  masonry.addEventListener('lf-masonry-event', (e) => {
    _recoverHero(e, failedHeroes);
    masonryHandler(e, store);
  });

  return masonry;
};

const _description = () => {
  const p = document.createElement('p');
  p.className = HOME_CLASSES.description;
  p.textContent = 'Choose a focused block or a ready-made orchestra.';

  return p;
};

const _rail = (
  store: WorkflowStore,
  kind: CatalogueKind,
  titleText: string,
  descriptionText: string,
  railClass: string,
  masonryClass: string,
  failedHeroes: Set<string>,
) => {
  const rail = document.createElement('section');
  const header = document.createElement('header');
  const headingRow = document.createElement('div');
  const heading = document.createElement('h2');
  const count = document.createElement('span');
  const description = document.createElement('p');
  const masonry = _masonry(store, masonryClass, failedHeroes);

  rail.className = `${theme.bemClass(ROOT_CLASS, 'rail')} ${railClass}`;
  rail.dataset.workflowKind = kind;
  header.className = theme.bemClass(ROOT_CLASS, 'rail-header');
  headingRow.className = theme.bemClass(ROOT_CLASS, 'rail-heading');
  heading.className = theme.bemClass(ROOT_CLASS, 'rail-title');
  count.className = theme.bemClass(ROOT_CLASS, 'rail-count');
  description.className = theme.bemClass(ROOT_CLASS, 'rail-description');

  heading.textContent = titleText;
  count.textContent = '0';
  count.setAttribute('aria-label', `0 ${titleText.toLowerCase()}`);
  count.dataset.railCount = kind;
  description.textContent = descriptionText;

  headingRow.append(heading, count);
  header.append(headingRow, description);
  rail.append(header, masonry);

  return { masonry, rail };
};

const _title = () => {
  const title = document.createElement('div');
  const h1 = document.createElement('h1');

  title.className = HOME_CLASSES.title;

  h1.className = HOME_CLASSES.h1;
  h1.textContent = 'Workflow Runner';

  title.appendChild(h1);

  return { h1, title };
};
//#endregion

export const createHomeSection = (store: WorkflowStore): WorkflowSectionController => {
  //#region Local variables
  const { HOME_DESTROYED, HOME_MOUNTED, HOME_UPDATED } = DEBUG_MESSAGES;
  const failedHeroes = new Set<string>();
  //#endregion

  //#region Destroy
  const destroy = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    for (const cls in HOME_CLASSES) {
      const element = HOME_CLASSES[cls];
      uiRegistry.remove(element);
    }
    failedHeroes.clear();

    debugLog(HOME_DESTROYED);
  };
  //#endregion

  //#region Mount
  const mount = () => {
    const { manager } = store.getState();
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (elements && elements[HOME_CLASSES._]) {
      return;
    }

    const _root = document.createElement('section');
    const catalogue = document.createElement('div');
    _root.className = HOME_CLASSES._;
    catalogue.className = HOME_CLASSES.catalogue;

    const description = _description();
    const orchestra = _rail(
      store,
      'orchestra',
      'Orchestras',
      'Multi-block pipelines.',
      HOME_CLASSES.orchestraRail,
      HOME_CLASSES.orchestraMasonry,
      failedHeroes,
    );
    const block = _rail(
      store,
      'block',
      'Blocks',
      'Single-purpose tools.',
      HOME_CLASSES.blockRail,
      HOME_CLASSES.blockMasonry,
      failedHeroes,
    );
    const { h1, title } = _title();

    catalogue.append(orchestra.rail, block.rail);
    _root.append(title, description, catalogue);

    elements[MAIN_CLASSES._].prepend(_root);

    uiRegistry.set(HOME_CLASSES._, _root);
    uiRegistry.set(HOME_CLASSES.blockMasonry, block.masonry);
    uiRegistry.set(HOME_CLASSES.blockRail, block.rail);
    uiRegistry.set(HOME_CLASSES.catalogue, catalogue);
    uiRegistry.set(HOME_CLASSES.description, description);
    uiRegistry.set(HOME_CLASSES.h1, h1);
    uiRegistry.set(HOME_CLASSES.orchestraMasonry, orchestra.masonry);
    uiRegistry.set(HOME_CLASSES.orchestraRail, orchestra.rail);
    uiRegistry.set(HOME_CLASSES.title, title);

    debugLog(HOME_MOUNTED);
  };
  //#endregion

  //#region Render
  const render = () => {
    const state = store.getState();
    const { manager } = state;
    const { uiRegistry } = manager;

    const elements = uiRegistry.get();
    if (!elements) {
      return;
    }

    const orchestraMasonry = elements[HOME_CLASSES.orchestraMasonry] as HTMLLfMasonryElement;
    const orchestraRail = elements[HOME_CLASSES.orchestraRail] as HTMLElement;
    const blockMasonry = elements[HOME_CLASSES.blockMasonry] as HTMLLfMasonryElement;
    const blockRail = elements[HOME_CLASSES.blockRail] as HTMLElement;
    if (!orchestraMasonry || !orchestraRail || !blockMasonry || !blockRail) {
      return;
    }

    const clone: WorkflowAPIDataset = JSON.parse(JSON.stringify(state.workflows));
    const nodes = clone.nodes || [];
    const labels = new Map(nodes.map((node) => [node.id, String(node.value || node.id)]));
    const orchestras = _createDataset(nodes, labels, 'orchestra', failedHeroes);
    const blocks = _createDataset(nodes, labels, 'block', failedHeroes);

    orchestraMasonry.lfDataset = orchestras.dataset;
    blockMasonry.lfDataset = blocks.dataset;
    orchestraRail.hidden = orchestras.count === 0;
    blockRail.hidden = blocks.count === 0;

    const orchestraCount = orchestraRail.querySelector<HTMLElement>(
      '[data-rail-count="orchestra"]',
    );
    const blockCount = blockRail.querySelector<HTMLElement>(
      '[data-rail-count="block"]',
    );
    if (orchestraCount) {
      orchestraCount.textContent = String(orchestras.count);
      orchestraCount.setAttribute(
        'aria-label',
        `${orchestras.count} ${orchestras.count === 1 ? 'orchestra' : 'orchestras'}`,
      );
    }
    if (blockCount) {
      blockCount.textContent = String(blocks.count);
      blockCount.setAttribute(
        'aria-label',
        `${blocks.count} ${blocks.count === 1 ? 'block' : 'blocks'}`,
      );
    }

    debugLog(HOME_UPDATED);
  };
  //#endregion

  return {
    destroy,
    mount,
    render,
  };
};
//#endregion
