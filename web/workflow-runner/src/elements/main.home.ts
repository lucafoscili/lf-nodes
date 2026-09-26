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
  custom: theme.bemClass(ROOT_CLASS, 'custom'),
  customCatalogue: theme.bemClass(ROOT_CLASS, 'custom-catalogue'),
  description: theme.bemClass(ROOT_CLASS, 'description'),
  h1: theme.bemClass(ROOT_CLASS, 'title-h1'),
  jump: theme.bemClass(ROOT_CLASS, 'jump'),
  jumpCustom: theme.bemClass(ROOT_CLASS, 'jump-custom'),
  jumpNavigation: theme.bemClass(ROOT_CLASS, 'jump-navigation'),
  jumpShipped: theme.bemClass(ROOT_CLASS, 'jump-shipped'),
  orchestraMasonry: theme.bemClass(ROOT_CLASS, 'orchestra-masonry'),
  orchestraRail: theme.bemClass(ROOT_CLASS, 'orchestra-rail'),
  shipped: theme.bemClass(ROOT_CLASS, 'shipped'),
  title: theme.bemClass(ROOT_CLASS, 'title'),
} as const;
//#endregion

//#region Helpers
type CatalogueKind = WorkflowAPIKind;
type CatalogueOwner = 'shipped' | 'custom';

const OWNER_SECTION_IDS: Record<CatalogueOwner, string> = {
  shipped: 'workflow-catalogue-lf-nodes',
  custom: 'workflow-catalogue-custom',
};

const ORCHESTRA_CARD_ACCENT = [
  '.material-layout {',
  '  border-inline-start: 4px double rgb(var(--lf-card-color-primary, var(--lf-color-secondary)));',
  '}',
].join('\n');
const CARD_STYLE = [
  // LF's adopted base stylesheet follows lfStyle; :host makes these overrides
  // win without relying on insertion order or changing the shared widget.
  ':host .material-layout { height: auto; overflow: hidden; }',
  ':host .material-layout__text-section { height: auto; min-width: 0; overflow: hidden; }',
  ':host .material-layout .text-content__description {',
  '  display: -webkit-box; overflow: hidden; white-space: pre-line;',
  '  -webkit-box-orient: vertical; -webkit-line-clamp: 4;',
  '}',
  ':host .material-layout--has-actions { padding-bottom: 0; }',
  ':host .material-layout__actions-section { position: static; height: auto; padding: 0 .5em .35em; }',
].join('\n');
const HERO_CARD_STYLE = [
  ':host .material-layout__cover-section {',
  '  aspect-ratio: 16 / 9; flex: none; height: auto; overflow: hidden;',
  '  --lf-image-object-fit: contain;',
  '}',
].join('\n');

const _kind = (node: WorkflowAPIItem): CatalogueKind => normalizeWorkflowKind(node.kind);

const _isShipped = (node: WorkflowAPIItem) => node.origin === 'shipped';

const _deduplicateNodes = (nodes: WorkflowAPIItem[]) => {
  const unique = new Map<string, WorkflowAPIItem>();
  nodes.forEach((node) => {
    const current = unique.get(node.id);
    // Custom registrations are authoritative overrides. Once one has claimed
    // an id, a stale shipped record cannot make the same workflow appear twice.
    if (!current || !_isShipped(node) || _isShipped(current)) {
      unique.set(node.id, node);
    }
  });
  return [...unique.values()];
};

const _collectionName = (node: WorkflowAPIItem) => node.collection?.trim() || 'Custom';

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
          dataset: {
            workflowCollection: _collectionName(node),
            workflowKind: kind,
            workflowOrigin: _isShipped(node) ? 'shipped' : 'custom',
          },
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
        lfSizeY: 'auto',
        lfStyle: [
          CARD_STYLE,
          hero ? HERO_CARD_STYLE : '',
          kind === 'orchestra' ? ORCHESTRA_CARD_ACCENT : '',
        ].join('\n'),
        ...(kind === 'orchestra' ? { lfUiState: 'secondary' as const } : {}),
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
  p.textContent = 'Browse LF Nodes workflows and your registered custom collections.';

  return p;
};

const _jumpNavigation = (targets: Record<CatalogueOwner, HTMLElement>) => {
  const navigation = document.createElement('nav');
  const label = document.createElement('span');
  const links = {} as Record<CatalogueOwner, HTMLAnchorElement>;

  navigation.className = HOME_CLASSES.jumpNavigation;
  navigation.setAttribute('aria-label', 'Jump to workflow collection');
  navigation.hidden = true;
  label.className = theme.bemClass(ROOT_CLASS, 'jump-label');
  label.textContent = 'Jump to';
  navigation.append(label);

  (['shipped', 'custom'] as const).forEach((owner) => {
    const link = document.createElement('a');
    const target = targets[owner];
    const text = owner === 'shipped' ? 'LF Nodes' : 'Custom workflows';

    link.className = `${HOME_CLASSES.jump} ${
      owner === 'shipped' ? HOME_CLASSES.jumpShipped : HOME_CLASSES.jumpCustom
    }`;
    link.dataset.workflowOrigin = owner;
    link.hidden = true;
    link.href = `#${target.id}`;
    link.textContent = text;

    links[owner] = link;
    navigation.append(link);
  });

  return { links, navigation };
};

const _rail = (
  store: WorkflowStore,
  kind: CatalogueKind,
  titleText: string,
  descriptionText: string,
  railClass: string,
  masonryClass: string,
  failedHeroes: Set<string>,
  origin: 'shipped' | 'custom' = 'shipped',
  collection?: string,
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
  rail.dataset.workflowOrigin = origin;
  if (collection) {
    rail.dataset.workflowCollection = collection;
  }
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

const _owner = (
  owner: CatalogueOwner,
  titleText: string,
  descriptionText: string,
  className: string,
) => {
  const section = document.createElement('section');
  const header = document.createElement('header');
  const heading = document.createElement('h2');
  const description = document.createElement('p');
  const content = document.createElement('div');

  section.className = `${theme.bemClass(ROOT_CLASS, 'owner')} ${className}`;
  section.id = OWNER_SECTION_IDS[owner];
  section.dataset.workflowOrigin = owner;
  header.className = theme.bemClass(ROOT_CLASS, 'owner-header');
  heading.className = theme.bemClass(ROOT_CLASS, 'owner-title');
  description.className = theme.bemClass(ROOT_CLASS, 'owner-description');
  content.className = theme.bemClass(ROOT_CLASS, 'owner-content');
  heading.textContent = titleText;
  description.textContent = descriptionText;
  header.append(heading, description);
  section.append(header, content);

  return { content, section };
};

const _setRail = (
  rail: HTMLElement,
  masonry: HTMLLfMasonryElement,
  result: ReturnType<typeof _createDataset>,
  kind: CatalogueKind,
) => {
  masonry.lfDataset = result.dataset;
  rail.hidden = result.count === 0;
  const count = rail.querySelector<HTMLElement>(`[data-rail-count="${kind}"]`);
  if (!count) {
    return;
  }
  count.textContent = String(result.count);
  count.setAttribute(
    'aria-label',
    `${result.count} ${result.count === 1 ? kind : `${kind}s`}`,
  );
};

const _setJump = (
  navigation: HTMLElement,
  link: HTMLAnchorElement,
  available: boolean,
) => {
  link.hidden = !available;
  navigation.hidden = Array.from(navigation.querySelectorAll<HTMLAnchorElement>('a')).every(
    (candidate) => candidate.hidden,
  );
};

const _renderCustomCatalogue = (
  store: WorkflowStore,
  catalogue: HTMLElement,
  nodes: WorkflowAPIItem[],
  labels: Map<string, string>,
  failedHeroes: Set<string>,
) => {
  const groups = new Map<string, WorkflowAPIItem[]>();
  nodes.forEach((node) => {
    const name = _collectionName(node);
    groups.set(name, [...(groups.get(name) || []), node]);
  });

  const fragment = document.createDocumentFragment();
  [...groups.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .forEach(([name, collectionNodes]) => {
      const group = document.createElement('section');
      const heading = document.createElement('h3');
      const rails = document.createElement('div');
      const orchestra = _rail(
        store,
        'orchestra',
        'Orchestras',
        'Multi-block pipelines.',
        theme.bemClass(ROOT_CLASS, 'custom-orchestra-rail'),
        theme.bemClass(ROOT_CLASS, 'custom-orchestra-masonry'),
        failedHeroes,
        'custom',
        name,
      );
      const block = _rail(
        store,
        'block',
        'Blocks',
        'Single-purpose tools.',
        theme.bemClass(ROOT_CLASS, 'custom-block-rail'),
        theme.bemClass(ROOT_CLASS, 'custom-block-masonry'),
        failedHeroes,
        'custom',
        name,
      );

      group.className = theme.bemClass(ROOT_CLASS, 'collection');
      group.dataset.workflowCollection = name;
      heading.className = theme.bemClass(ROOT_CLASS, 'collection-title');
      heading.textContent = name;
      rails.className = theme.bemClass(ROOT_CLASS, 'collection-rails');

      const orchestras = _createDataset(
        collectionNodes,
        labels,
        'orchestra',
        failedHeroes,
      );
      const blocks = _createDataset(collectionNodes, labels, 'block', failedHeroes);
      _setRail(orchestra.rail, orchestra.masonry, orchestras, 'orchestra');
      _setRail(block.rail, block.masonry, blocks, 'block');

      rails.append(orchestra.rail, block.rail);
      group.append(heading, rails);
      fragment.append(group);
    });

  catalogue.replaceChildren(fragment);
  return groups.size;
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
  let renderedWorkflows: string | undefined;
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
    renderedWorkflows = undefined;

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
    const shipped = _owner(
      'shipped',
      'LF Nodes',
      'Curated workflows included with LF Nodes.',
      HOME_CLASSES.shipped,
    );
    const custom = _owner(
      'custom',
      'Custom workflows',
      'Workflows registered by your projects and local extensions.',
      HOME_CLASSES.custom,
    );
    custom.content.classList.add(HOME_CLASSES.customCatalogue);
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
    const jumps = _jumpNavigation({ shipped: shipped.section, custom: custom.section });
    const { h1, title } = _title();

    shipped.content.append(orchestra.rail, block.rail);
    catalogue.append(shipped.section, custom.section);
    _root.append(title, description, jumps.navigation, catalogue);

    elements[MAIN_CLASSES._].prepend(_root);

    uiRegistry.set(HOME_CLASSES._, _root);
    uiRegistry.set(HOME_CLASSES.blockMasonry, block.masonry);
    uiRegistry.set(HOME_CLASSES.blockRail, block.rail);
    uiRegistry.set(HOME_CLASSES.catalogue, catalogue);
    uiRegistry.set(HOME_CLASSES.custom, custom.section);
    uiRegistry.set(HOME_CLASSES.customCatalogue, custom.content);
    uiRegistry.set(HOME_CLASSES.description, description);
    uiRegistry.set(HOME_CLASSES.h1, h1);
    uiRegistry.set(HOME_CLASSES.jumpCustom, jumps.links.custom);
    uiRegistry.set(HOME_CLASSES.jumpNavigation, jumps.navigation);
    uiRegistry.set(HOME_CLASSES.jumpShipped, jumps.links.shipped);
    uiRegistry.set(HOME_CLASSES.orchestraMasonry, orchestra.masonry);
    uiRegistry.set(HOME_CLASSES.orchestraRail, orchestra.rail);
    uiRegistry.set(HOME_CLASSES.shipped, shipped.section);
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
    const custom = elements[HOME_CLASSES.custom] as HTMLElement;
    const customCatalogue = elements[HOME_CLASSES.customCatalogue] as HTMLElement;
    const jumpCustom = elements[HOME_CLASSES.jumpCustom] as HTMLAnchorElement;
    const jumpNavigation = elements[HOME_CLASSES.jumpNavigation] as HTMLElement;
    const jumpShipped = elements[HOME_CLASSES.jumpShipped] as HTMLAnchorElement;
    const shipped = elements[HOME_CLASSES.shipped] as HTMLElement;
    if (
      !orchestraMasonry ||
      !orchestraRail ||
      !blockMasonry ||
      !blockRail ||
      !custom ||
      !customCatalogue ||
      !jumpCustom ||
      !jumpNavigation ||
      !jumpShipped ||
      !shipped
    ) {
      return;
    }

    // Queue and run updates clone the workflow dataset too. Compare content so
    // unchanged cards keep their DOM, loaded images, and completed animations.
    const serializedWorkflows = JSON.stringify(state.workflows);
    if (serializedWorkflows === renderedWorkflows) {
      return;
    }
    const clone: WorkflowAPIDataset = JSON.parse(serializedWorkflows);
    const nodes = _deduplicateNodes(clone.nodes || []);
    const labels = new Map(nodes.map((node) => [node.id, String(node.value || node.id)]));
    const shippedNodes = nodes.filter(_isShipped);
    const customNodes = nodes.filter((node) => !_isShipped(node));
    const orchestras = _createDataset(shippedNodes, labels, 'orchestra', failedHeroes);
    const blocks = _createDataset(shippedNodes, labels, 'block', failedHeroes);

    _setRail(orchestraRail, orchestraMasonry, orchestras, 'orchestra');
    _setRail(blockRail, blockMasonry, blocks, 'block');
    shipped.hidden = orchestras.count + blocks.count === 0;
    custom.hidden =
      _renderCustomCatalogue(store, customCatalogue, customNodes, labels, failedHeroes) === 0;
    _setJump(jumpNavigation, jumpShipped, orchestras.count + blocks.count > 0);
    _setJump(jumpNavigation, jumpCustom, customNodes.length > 0);
    renderedWorkflows = serializedWorkflows;

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
