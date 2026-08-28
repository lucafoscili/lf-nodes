import { createHash, randomUUID } from 'node:crypto';
import { mkdir, readFile, stat, writeFile } from 'node:fs/promises';
import { basename, dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import playwright from 'playwright';
import type { Browser, Page } from 'playwright';

import {
  classifyHistoryEntry,
  classifyPostCancellation,
  collectPreviewUrls,
  comfyArtifactKey,
  createJUnitXml,
  describeGateScope,
  determineAchievedGate,
  extractDatasetCellPreviewUrl,
  extractHistoryExecutionTargets,
  extractHistoryPrompt,
  normalizeExecutionTargetIds,
  parseQueueSnapshot,
  queueIds,
  requiredFlagsForResourceClass,
  selectOwnedSubmissionPromptId,
  timedOutTerminalClassification,
  unwrapHistoryEntry,
  validateCaseOutputs,
  validateCoverage,
  validateExecutionTrace,
  validateEditorClientBinding,
  validateLoadedModelFixture,
  type ExecutionTrace,
  type GateOutcome,
  type ManifestCase,
  type TitanicManifest,
} from './titanic_e2e_core.ts';

type JsonRecord = Record<string, any>;

const { chromium } = playwright;

interface CliOptions {
  workflowPath: string;
  comfyUrl: string;
  lmStudioUrl: string;
  localModelId?: string;
  localInstanceId?: string;
  outputDir: string;
  browserChannel?: string;
  headed: boolean;
  mode: 'hydrate' | 'smoke' | 'full';
  caseIds: string[];
  allowGpu: boolean;
  allowModels: boolean;
  allowWrites: boolean;
  allowUnpinnedInputs: boolean;
  allowLocalLlm: boolean;
  allowInteraction: boolean;
  acceptWarmCache: boolean;
}

interface CaseResult {
  id: string;
  title: string;
  outcome: GateOutcome;
  durationSeconds: number;
  message?: string;
  promptId?: string;
  assertions?: string[];
  blockers?: string[];
  interaction?: JsonRecord;
  terminal?: JsonRecord;
  promptEvidence?: JsonRecord;
  executionTrace?: ExecutionTrace;
  downstreamArtifact?: JsonRecord;
  foreignWorkDetected?: boolean;
}

const scriptDir = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(scriptDir, '..', '..');
const defaultWorkflow = resolve(scriptDir, 'fixtures', 'E2E.json');
const defaultManifest = resolve(scriptDir, 'titanic_cases.json');

const timestamp = () => new Date().toISOString().replaceAll(':', '-').replaceAll('.', '-');

const usage = `
LF Titanic E2E gate

Usage:
  corepack yarn test:titanic -- [--workflow <E2E.json>] [--execute-smoke | --full]

Default mode hydrates the real workflow in Comfy's frontend, compiles it with
app.graphToPrompt(), audits LF widgets, and never queues work.

The reviewed case manifest is repository-fixed. A --workflow override is
accepted only when its bytes match that manifest's canonical workflow hash.

Execution authority is explicit:
  --execute-smoke          Run only the bounded CPU widget specimen.
  --full                   Evaluate every active manifest case.
  --case <id>              Restrict --full; reports a targeted gate, never full.
  --allow-gpu              Permit GPU-class cases.
  --allow-models           Permit local model-loading cases (never downloads).
  --allow-writes           Permit declared durable-output cases.
  --allow-unpinned-inputs  Permit workstation-owned input fixtures.
  --allow-local-llm        Permit localhost:5001 cases.
  --local-model-id <key>   Require exactly this LM Studio model key.
  --local-instance-id <id> Optionally require this loaded instance ID.
  --allow-interaction      Permit browser-driven editing transactions.
  --accept-warm-cache      Allow full execution without Comfy --cache-none.

Service lifecycle is deliberately out of scope: this command never starts,
stops, restarts, clears, or globally interrupts Comfy or LM Studio.
`;

const parseArgs = (argv: string[]): CliOptions => {
  const options: CliOptions = {
    workflowPath: process.env.LF_TITANIC_WORKFLOW || defaultWorkflow,
    comfyUrl: process.env.LF_COMFY_URL || 'http://127.0.0.1:8188',
    lmStudioUrl: process.env.LF_LM_STUDIO_URL || 'http://127.0.0.1:5001',
    localModelId: process.env.LF_TITANIC_LOCAL_MODEL_ID,
    localInstanceId: process.env.LF_TITANIC_LOCAL_INSTANCE_ID,
    outputDir: resolve(repoRoot, 'output', 'titanic-e2e', timestamp()),
    browserChannel: process.env.LF_TITANIC_BROWSER_CHANNEL || 'chrome',
    headed: false,
    mode: 'hydrate',
    caseIds: [],
    allowGpu: false,
    allowModels: false,
    allowWrites: false,
    allowUnpinnedInputs: false,
    allowLocalLlm: false,
    allowInteraction: false,
    acceptWarmCache: false,
  };
  const takeValue = (index: number, name: string): string => {
    const value = argv[index + 1];
    if (!value || value.startsWith('--')) throw new Error(`${name} requires a value`);
    return value;
  };
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    switch (arg) {
      case '--':
        break;
      case '--help':
      case '-h':
        console.log(usage.trim());
        process.exit(0);
      case '--workflow':
        options.workflowPath = resolve(takeValue(index, arg));
        index += 1;
        break;
      case '--comfy-url':
        options.comfyUrl = takeValue(index, arg).replace(/\/$/, '');
        index += 1;
        break;
      case '--lm-studio-url':
        options.lmStudioUrl = takeValue(index, arg).replace(/\/$/, '');
        index += 1;
        break;
      case '--local-model-id':
        options.localModelId = takeValue(index, arg);
        index += 1;
        break;
      case '--local-instance-id':
        options.localInstanceId = takeValue(index, arg);
        index += 1;
        break;
      case '--output-dir':
        options.outputDir = resolve(takeValue(index, arg));
        index += 1;
        break;
      case '--browser-channel':
        options.browserChannel = takeValue(index, arg);
        index += 1;
        break;
      case '--headed':
        options.headed = true;
        break;
      case '--execute-smoke':
        options.mode = 'smoke';
        break;
      case '--full':
        options.mode = 'full';
        break;
      case '--case':
        options.caseIds.push(takeValue(index, arg));
        index += 1;
        break;
      case '--allow-gpu':
        options.allowGpu = true;
        break;
      case '--allow-models':
        options.allowModels = true;
        break;
      case '--allow-writes':
        options.allowWrites = true;
        break;
      case '--allow-unpinned-inputs':
        options.allowUnpinnedInputs = true;
        break;
      case '--allow-local-llm':
        options.allowLocalLlm = true;
        break;
      case '--allow-interaction':
        options.allowInteraction = true;
        break;
      case '--accept-warm-cache':
        options.acceptWarmCache = true;
        break;
      default:
        throw new Error(`unknown argument: ${arg}`);
    }
  }
  if (options.caseIds.length > 0 && options.mode !== 'full') {
    throw new Error('--case is only valid with --full');
  }
  return options;
};

const sha256 = (value: string | Buffer): string =>
  createHash('sha256').update(value).digest('hex');

const jsonFetch = async (
  url: string,
  init: RequestInit = {},
  timeoutMs = 10_000,
): Promise<any> => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, { ...init, signal: controller.signal });
    const text = await response.text();
    if (!response.ok) {
      throw new Error(`${response.status} ${response.statusText}: ${text.slice(0, 500)}`);
    }
    return text ? JSON.parse(text) : {};
  } finally {
    clearTimeout(timeout);
  }
};

const validatePreviewAssets = async (
  comfyUrl: string,
  manifestCase: ManifestCase,
  historyEntry: JsonRecord,
): Promise<string[]> => {
  const errors: string[] = [];
  const outputs = historyEntry.outputs ?? {};
  for (const [nodeId, expectation] of Object.entries(manifestCase.expect ?? {})) {
    if (expectation.minimumPreviewCount === undefined) continue;
    for (const previewUrl of collectPreviewUrls(outputs[nodeId])) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 10_000);
      try {
        const response = await fetch(new URL(previewUrl, comfyUrl), {
          signal: controller.signal,
        });
        if (!response.ok) {
          errors.push(
            `node ${nodeId} preview returned ${response.status}: ${previewUrl}`,
          );
          continue;
        }
        const contentType = response.headers.get('content-type') ?? '';
        const bytes = await response.arrayBuffer();
        if (!contentType.startsWith('image/')) {
          errors.push(
            `node ${nodeId} preview is not an image (${contentType || 'missing content-type'}): ${previewUrl}`,
          );
        }
        if (bytes.byteLength === 0) {
          errors.push(`node ${nodeId} preview is empty: ${previewUrl}`);
        }
      } catch (error) {
        errors.push(`node ${nodeId} preview did not resolve: ${previewUrl} (${String(error)})`);
      } finally {
        clearTimeout(timeout);
      }
    }
  }
  return errors;
};

const findArgv = (value: unknown): string[] | null => {
  if (Array.isArray(value)) {
    if (value.every((item) => typeof item === 'string') && value.includes('main.py')) {
      return value as string[];
    }
    for (const item of value) {
      const found = findArgv(item);
      if (found) return found;
    }
    return null;
  }
  if (value && typeof value === 'object') {
    for (const item of Object.values(value)) {
      const found = findArgv(item);
      if (found) return found;
    }
  }
  return null;
};

const launchBrowser = async (options: CliOptions): Promise<Browser> => {
  try {
    return await chromium.launch({
      channel: options.browserChannel,
      headless: !options.headed,
    });
  } catch (channelError) {
    if (!options.browserChannel) throw channelError;
    try {
      return await chromium.launch({ headless: !options.headed });
    } catch (bundledError) {
      throw new Error(
        `browser launch failed for channel ${options.browserChannel} and bundled Chromium. ` +
          `Install a browser with "corepack yarn playwright install chromium" or pass --browser-channel. ` +
          `Channel error: ${String(channelError)}; bundled error: ${String(bundledError)}`,
      );
    }
  }
};

const hydrateWorkflow = async (
  page: Page,
  comfyUrl: string,
  workflow: JsonRecord,
  objectInfo: JsonRecord,
) => {
  const expectedWidgetTypes = [
    ...new Set(
      workflow.nodes.flatMap((savedNode: any) =>
        (savedNode.inputs ?? [])
          .filter((input: any) => Boolean(input?.widget?.name))
          .map((input: any) => input.type)
          .filter(
            (inputType: unknown): inputType is string =>
              typeof inputType === 'string' && inputType.startsWith('LF_'),
          ),
      ),
    ),
  ].sort();
  const expectedNodeTypes = [
    ...new Set(
      workflow.nodes
        .map((savedNode: any) => savedNode?.type)
        .filter((nodeType: unknown): nodeType is string => typeof nodeType === 'string'),
    ),
  ].sort();
  const consoleErrors: string[] = [];
  const pageErrors: string[] = [];
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  page.on('pageerror', (error) => pageErrors.push(String(error)));

  await page.goto(`${comfyUrl}/?lf-titanic-e2e=${randomUUID()}`, {
    waitUntil: 'domcontentloaded',
    timeout: 60_000,
  });
  await page.waitForFunction(
    () =>
      Boolean(
        (window as any).comfyAPI?.app?.app?.loadGraphData &&
          (window as any).comfyAPI?.api?.api,
      ),
    undefined,
    { timeout: 60_000 },
  );
  await page.waitForFunction(
    () => {
      const app = (window as any).comfyAPI?.app?.app;
      return Boolean(
        (window as any).app === app &&
          app?.canvas?.graph &&
          document.getElementById('splash-loader') === null,
      );
    },
    undefined,
    { timeout: 60_000 },
  );
  try {
    await page.waitForFunction(
      ({ widgetTypes, nodeTypes }) => {
        try {
          const manager = (window as any)[Symbol.for('__LfManager__')];
          const app = (window as any).comfyAPI?.app?.app;
          const registeredNodeTypes = (window as any).LiteGraph?.registered_node_types;
          return Boolean(
            manager?.getManagers?.().lfFramework &&
              customElements.get('lf-masonry') &&
              customElements.get('lf-tree') &&
              (widgetTypes as string[]).every(
                (widgetType) => typeof app?.widgets?.[widgetType] === 'function',
              ) &&
              (nodeTypes as string[]).every(
                (nodeType) => registeredNodeTypes?.[nodeType],
              ),
          );
        } catch {
          return false;
        }
      },
      { widgetTypes: expectedWidgetTypes, nodeTypes: expectedNodeTypes },
      { timeout: 60_000 },
    );
  } catch (error) {
    const missing = await page.evaluate(
      ({ widgetTypes, nodeTypes }) => {
        const app = (window as any).comfyAPI?.app?.app;
        const registeredNodeTypes =
          (window as any).LiteGraph?.registered_node_types ?? {};
        let widgets: Record<string, unknown> = {};
        try {
          widgets = app?.widgets ?? {};
        } catch {}
        return {
          widgetTypes: (widgetTypes as string[]).filter(
            (widgetType) => typeof widgets[widgetType] !== 'function',
          ),
          nodeTypes: (nodeTypes as string[]).filter(
            (nodeType) => !registeredNodeTypes[nodeType],
          ),
        };
      },
      { widgetTypes: expectedWidgetTypes, nodeTypes: expectedNodeTypes },
    );
    throw new Error(
      `FRONTEND_REGISTRY_NOT_READY: missing widgets=${JSON.stringify(missing.widgetTypes)}, missing node types=${JSON.stringify(missing.nodeTypes)}; ${String(error)}`,
    );
  }
  // tsx annotates nested functions with this helper. A string evaluation keeps
  // the helper itself free of transpiler decoration inside the browser realm.
  await page.evaluate('globalThis.__name ??= (value) => value');

  const hydrated = await page.evaluate(
    async ({ workflowData, nodeInfo }) => {
      const comfy = (window as any).comfyAPI;
      const app = comfy.app.app;
      await app.loadGraphData(workflowData, true, true, null, {
        deferWarnings: true,
        skipAssetScans: true,
        silentAssetErrors: true,
      });

      await new Promise<void>((resolvePromise) =>
        requestAnimationFrame(() => requestAnimationFrame(() => resolvePromise())),
      );
      const loadedNodes = app.rootGraph?._nodes ?? app.graph?._nodes ?? [];
      const byId = new Map(loadedNodes.map((node: any) => [String(node.id), node]));
      const customWidgetInputs = workflowData.nodes.flatMap((savedNode: any) =>
        (savedNode.inputs ?? [])
          .filter(
            (input: any) =>
              input?.widget?.name &&
              typeof input.type === 'string' &&
              input.type.startsWith('LF_'),
          )
          .map((input: any) => ({
            nodeId: String(savedNode.id),
            nodeType: savedNode.type,
            name: input.widget.name,
            expectedType: input.type,
          })),
      );

      const inspectWidgets = () =>
        customWidgetInputs.map((expected: any) => {
          const loadedNode: any = byId.get(expected.nodeId);
          const widget = loadedNode?.widgets?.find(
            (candidate: any) => candidate.name === expected.name,
          );
          const element = widget?.element;
          const customElement =
            element?.tagName?.toLowerCase?.().startsWith('lf-')
              ? element
              : element?.querySelector?.('lf-article,lf-button,lf-code,lf-list,lf-masonry,lf-messenger,lf-textarea,lf-tree');
          return {
            ...expected,
            found: Boolean(widget),
            hasElement: Boolean(element),
            connected: Boolean(element?.isConnected),
            customElementTag: customElement?.tagName?.toLowerCase?.() ?? null,
          };
        });

      // Widget construction is synchronous: structural absence cannot heal by
      // polling. Only DOM connection may settle for a few frames after this
      // very large graph is configured.
      let widgetChecks = inspectWidgets();
      const hasStructuralWidgetFailure = () =>
        widgetChecks.some((widget: any) => !widget.found || !widget.hasElement);
      const widgetDeadline = performance.now() + 5_000;
      while (
        !hasStructuralWidgetFailure() &&
        widgetChecks.some((widget: any) => !widget.connected) &&
        performance.now() < widgetDeadline
      ) {
        await new Promise((resolvePromise) => setTimeout(resolvePromise, 100));
        widgetChecks = inspectWidgets();
      }

      const promptBundle = await app.graphToPrompt(app.rootGraph);
      widgetChecks = inspectWidgets();

      const activeOutputIds = workflowData.nodes
        .filter(
          (node: any) =>
            Number(node.mode ?? 0) === 0 && nodeInfo[node.type]?.output_node === true,
        )
        .map((node: any) => Number(node.id))
        .sort((a: number, b: number) => a - b);
      return {
        promptBundle,
        loadedNodeCount: loadedNodes.length,
        loadedLinkCount: Object.keys(app.rootGraph?.links ?? app.graph?.links ?? {}).length,
        activeOutputIds,
        mode2NodeIds: workflowData.nodes
          .filter((node: any) => Number(node.mode ?? 0) === 2)
          .map((node: any) => Number(node.id))
          .sort((a: number, b: number) => a - b),
        widgetChecks,
        widgetDebug: ['2', '590', '592'].map((nodeId) => {
          const node: any = byId.get(nodeId);
          return {
            nodeId,
            nodeKeys: node ? Object.keys(node).sort() : [],
            widgets: (node?.widgets ?? []).map((widget: any) => ({
              name: widget.name,
              type: widget.type,
              hasElement: Boolean(widget.element),
            })),
            inputs: (node?.inputs ?? []).map((input: any) => ({
              name: input.name,
              type: input.type,
              widget: input.widget,
            })),
          };
        }),
        clientId: String(comfy.api.api.clientId ?? ''),
      };
    },
    { workflowData: workflow, nodeInfo: objectInfo },
  );
  return { ...hydrated, consoleErrors, pageErrors };
};

const collectAncestors = (prompt: JsonRecord, targets: number[]): Set<string> => {
  const seen = new Set<string>();
  const visit = (id: string) => {
    if (seen.has(id)) return;
    seen.add(id);
    const node = prompt[id];
    if (!node || typeof node !== 'object') return;
    for (const value of Object.values(node.inputs ?? {})) {
      if (Array.isArray(value) && value.length >= 2 && prompt[String(value[0])]) {
        visit(String(value[0]));
      }
    }
  };
  targets.forEach((target) => visit(String(target)));
  return seen;
};

const validateCombos = (
  prompt: JsonRecord,
  objectInfo: JsonRecord,
  targets: number[],
): string[] => {
  const blockers: string[] = [];
  for (const nodeId of collectAncestors(prompt, targets)) {
    const node = prompt[nodeId];
    const classType = node?.class_type;
    const definition = objectInfo[classType];
    if (!definition) {
      blockers.push(`node ${nodeId} uses unavailable class ${String(classType)}`);
      continue;
    }
    const definitions = {
      ...(definition.input?.required ?? {}),
      ...(definition.input?.optional ?? {}),
    };
    for (const [name, value] of Object.entries(node.inputs ?? {})) {
      const spec = definitions[name];
      const choices = Array.isArray(spec) && Array.isArray(spec[0]) ? spec[0] : null;
      const isLink = Array.isArray(value) && value.length >= 2;
      if (choices && !isLink && !choices.includes(value)) {
        blockers.push(
          `node ${nodeId} (${classType}) input ${name} selects unavailable value ${JSON.stringify(value)}`,
        );
      }
    }
  }
  return blockers;
};

const queueIsEmpty = async (comfyUrl: string) => {
  const raw = await jsonFetch(`${comfyUrl}/queue`);
  const parsed = parseQueueSnapshot(raw);
  return { raw, parsed, ids: queueIds(parsed) };
};

const queueCaseThroughFrontend = async (
  page: Page,
  targets: number[],
  requestedPromptId: string,
) =>
  page.evaluate(async ({ targetIds, ownedPromptId }) => {
    const comfy = (window as any).comfyAPI;
    const app = comfy.app.app;
    const api = comfy.api.api;
    let captured: any = null;
    let submittedPrompt: any = null;
    let submittedPartialExecutionTargets: any = null;
    let promptIdInjected = false;
    const original = api.queuePrompt;
    const originalFetchApi = api.fetchApi;
    api.fetchApi = async function (route: string, options?: RequestInit) {
      if (
        !promptIdInjected &&
        route === '/prompt' &&
        options?.method === 'POST' &&
        typeof options.body === 'string'
      ) {
        const body = JSON.parse(options.body);
        body.prompt_id = ownedPromptId;
        options = { ...options, body: JSON.stringify(body) };
        promptIdInjected = true;
      }
      return originalFetchApi.call(this, route, options);
    };
    api.queuePrompt = async function (...args: any[]) {
      submittedPrompt = JSON.parse(JSON.stringify(args[1]?.output ?? null));
      submittedPartialExecutionTargets = JSON.parse(
        JSON.stringify(args[2]?.partialExecutionTargets ?? null),
      );
      try {
        const response = await original.apply(this, args);
        captured = response;
        return response;
      } catch (error: any) {
        captured = {
          thrown: String(error),
          response: error?.response ?? null,
        };
        throw error;
      }
    };
    try {
      // Core's NodeExecutionId is a string (and may eventually carry a
      // subgraph path), even though root-graph workflow IDs serialize as
      // numbers. Numeric IDs silently match no partial-execution outputs.
      const accepted = await app.queuePrompt(0, 1, targetIds.map(String));
      return {
        accepted,
        captured,
        submittedPrompt,
        submittedPartialExecutionTargets,
        requestedPromptId: ownedPromptId,
        promptIdInjected,
      };
    } finally {
      api.queuePrompt = original;
      api.fetchApi = originalFetchApi;
    }
  }, { targetIds: targets, ownedPromptId: requestedPromptId });

const installExecutionRecorder = async (page: Page): Promise<string> => {
  const token = randomUUID();
  await page.evaluate((recorderToken) => {
    const api = (window as any).comfyAPI.api.api;
    const globalRecorders = ((globalThis as any).__lfTitanicExecutionRecorders ??= {});
    const recorder: any = {
      activePromptId: null,
      events: [],
      handlers: {},
    };
    const collectPreviewUrls = (value: unknown): string[] => {
      const urls = new Set<string>();
      const visit = (candidate: unknown) => {
        if (Array.isArray(candidate)) {
          candidate.forEach(visit);
          return;
        }
        if (!candidate || typeof candidate !== 'object') return;
        for (const nested of Object.values(candidate as Record<string, unknown>)) {
          if (typeof nested === 'string' && nested.startsWith('/view?')) urls.add(nested);
          else visit(nested);
        }
      };
      visit(value);
      return [...urls].sort();
    };
    for (const type of [
      'execution_start',
      'execution_cached',
      'executing',
      'executed',
      'execution_success',
      'execution_error',
      'execution_interrupted',
    ]) {
      const handler = (event: Event) => {
        const rawDetail = (event as CustomEvent).detail;
        const detail =
          rawDetail !== null && typeof rawDetail === 'object' ? rawDetail : {};
        const explicitPromptId =
          typeof detail.prompt_id === 'string' ? detail.prompt_id : null;
        if (type === 'execution_start' && explicitPromptId) {
          recorder.activePromptId = explicitPromptId;
        }
        const promptId = explicitPromptId ?? recorder.activePromptId;
        const primitiveExecutingNode =
          type === 'executing' &&
          (typeof rawDetail === 'string' || typeof rawDetail === 'number')
            ? String(rawDetail)
            : null;
        recorder.events.push({
          type,
          promptId,
          nodeId:
            primitiveExecutingNode ??
            (detail.node === null || detail.node === undefined
              ? null
              : String(detail.node)),
          nodes: Array.isArray(detail.nodes) ? detail.nodes.map(String) : [],
          previewUrls:
            type === 'executed' ? collectPreviewUrls(detail.output) : [],
          timestampMs: Date.now(),
        });
        if (
          explicitPromptId &&
          explicitPromptId === recorder.activePromptId &&
          ['execution_success', 'execution_error', 'execution_interrupted'].includes(type)
        ) {
          recorder.activePromptId = null;
        }
      };
      recorder.handlers[type] = handler;
      api.addEventListener(type, handler);
    }
    globalRecorders[recorderToken] = recorder;
  }, token);
  return token;
};

const stopExecutionRecorder = async (
  page: Page,
  token: string,
  promptId: string,
): Promise<ExecutionTrace> =>
  page.evaluate(
    ({ recorderToken, ownedPromptId }) => {
      const api = (window as any).comfyAPI.api.api;
      const globalRecorders = (globalThis as any).__lfTitanicExecutionRecorders ?? {};
      const recorder = globalRecorders[recorderToken];
      if (!recorder) {
        return {
          promptId: ownedPromptId,
          started: false,
          terminalEvent: null,
          executedNodeIds: [],
          uiExecutedNodeIds: [],
          cachedNodeIds: [],
          executingEvents: [],
          executedPreviewUrlsByNode: {},
        };
      }
      for (const [type, handler] of Object.entries(recorder.handlers)) {
        api.removeEventListener(type, handler as EventListener);
      }
      delete globalRecorders[recorderToken];
      const events = recorder.events.filter(
        (event: any) => event.promptId === ownedPromptId,
      );
      const unique = (values: string[]) => [...new Set(values)];
      const terminal = events
        .filter((event: any) =>
          ['execution_success', 'execution_error', 'execution_interrupted'].includes(
            event.type,
          ),
        )
        .at(-1);
      const executedPreviewUrlsByNode: Record<string, string[]> = {};
      for (const event of events) {
        if (event.type !== 'executed' || !event.nodeId) continue;
        executedPreviewUrlsByNode[event.nodeId] = unique([
          ...(executedPreviewUrlsByNode[event.nodeId] ?? []),
          ...event.previewUrls,
        ]).sort();
      }
      return {
        promptId: ownedPromptId,
        started: events.some((event: any) => event.type === 'execution_start'),
        terminalEvent: terminal?.type ?? null,
        // `executing` is Core's actual-work event. The frontend may omit its
        // prompt_id, so the recorder assigns it only while bracketed by this
        // prompt's exact start and terminal events.
        executedNodeIds: unique(
          events
            .filter((event: any) => event.type === 'executing' && event.nodeId)
            .map((event: any) => event.nodeId),
        ),
        uiExecutedNodeIds: unique(
          events
            .filter((event: any) => event.type === 'executed' && event.nodeId)
            .map((event: any) => event.nodeId),
        ),
        cachedNodeIds: unique(
          events
            .filter((event: any) => event.type === 'execution_cached')
            .flatMap((event: any) => event.nodes),
        ),
        executingEvents: events
          .filter((event: any) => event.type === 'executing' && event.nodeId)
          .map((event: any) => ({
            nodeId: event.nodeId,
            timestampMs: event.timestampMs,
          })),
        executedPreviewUrlsByNode,
      };
    },
    { recorderToken: token, ownedPromptId: promptId },
  );

const executionRecorderPromptIds = async (
  page: Page,
  token: string,
): Promise<string[]> =>
  page.evaluate((recorderToken) => {
    const recorder = (globalThis as any).__lfTitanicExecutionRecorders?.[recorderToken];
    if (!recorder) return [];
    const promptIds = (recorder.events ?? [])
      .map((event: any) => event.promptId)
      .filter(
        (promptId: unknown): promptId is string =>
          typeof promptId === 'string' && promptId.length > 0,
      );
    return [...new Set<string>(promptIds)].sort();
  }, token);

const observeSubmissionDelta = async (
  page: Page,
  comfyUrl: string,
  recorderToken: string,
  historyBefore: Set<string>,
  expectedPromptIds: string[] = [],
) => {
  const candidateIds = new Set<string>();
  const boundPromptIds = new Set<string>();
  const queuePromptIds = new Set<string>();
  const historyDeltaIds = new Set<string>();
  const recorderPromptIds = new Set<string>();
  const errors = new Set<string>();
  const expectedIds = new Set(expectedPromptIds);
  const deadline = Date.now() + 3_000;
  do {
    try {
      const queue = await queueIsEmpty(comfyUrl);
      queue.parsed.malformed.forEach((diagnostic) => errors.add(diagnostic));
      for (const id of queue.ids) {
        queuePromptIds.add(id);
        candidateIds.add(id);
        if (expectedIds.has(id)) boundPromptIds.add(id);
      }
    } catch (error) {
      errors.add(`submission queue audit failed: ${String(error)}`);
    }
    try {
      const history = (await jsonFetch(`${comfyUrl}/history`)) as JsonRecord;
      for (const [id, entry] of Object.entries(history ?? {})) {
        if (historyBefore.has(id)) continue;
        historyDeltaIds.add(id);
        candidateIds.add(id);
        if (expectedIds.has(id)) boundPromptIds.add(id);
      }
    } catch (error) {
      errors.add(`submission history audit failed: ${String(error)}`);
    }
    try {
      for (const id of await executionRecorderPromptIds(page, recorderToken)) {
        recorderPromptIds.add(id);
        candidateIds.add(id);
        if (expectedIds.has(id)) boundPromptIds.add(id);
      }
    } catch (error) {
      errors.add(`submission event audit failed: ${String(error)}`);
    }
    if (
      boundPromptIds.size > 0 ||
      (expectedIds.size === 0 && candidateIds.size > 0)
    ) break;
    await new Promise((resolvePromise) => setTimeout(resolvePromise, 250));
  } while (Date.now() < deadline);

  return {
    candidateIds: [...candidateIds].sort(),
    boundPromptIds: [...boundPromptIds].sort(),
    queuePromptIds: [...queuePromptIds].sort(),
    historyPromptIds: [...historyDeltaIds].sort(),
    recorderPromptIds: [...recorderPromptIds].sort(),
    errors: [...errors].sort(),
  };
};

const readLiveWidgets = async (page: Page, nodeIds: number[]) =>
  page.evaluate((ids) => {
    const app = (window as any).comfyAPI.app.app;
    const graph = app.rootGraph ?? app.graph;
    return ids.map((nodeId) => {
      const node = graph.getNodeById(nodeId);
      const widget = node?.widgets?.find((candidate: any) => candidate.name === 'ui_widget');
      const value = widget?.value;
      const dataset = value?.dataset ?? value;
      return {
        nodeId,
        found: Boolean(widget),
        hasElement: Boolean(widget?.element),
        previewCount: Array.isArray(dataset?.nodes) ? dataset.nodes.length : 0,
      };
    });
  }, nodeIds);

const requireComfyClientId = async (page: Page, timeoutMs: number): Promise<string> => {
  await page.waitForFunction(
    () => {
      const clientId = (window as any).comfyAPI?.api?.api?.clientId;
      return typeof clientId === 'string' && clientId.trim().length > 0;
    },
    undefined,
    { timeout: timeoutMs },
  );
  const clientId = await page.evaluate(() => {
    const value = (window as any).comfyAPI?.api?.api?.clientId;
    return typeof value === 'string' ? value.trim() : '';
  });
  if (!clientId) throw new Error('Comfy frontend has no connected client id');
  return clientId;
};

const inpaintImageEditor = async (
  page: Page,
  nodeId: number,
  timeoutMs: number,
): Promise<JsonRecord> => {
  const editorSelector = `lf-imageviewer[data-e2e-editor="${nodeId}"]`;
  const processPath = '/lf-nodes/process-image';
  const updatePath = '/lf-nodes/update-json';
  const callerClientId = await requireComfyClientId(page, timeoutMs);
  let processExpected = false;
  let processStarted = false;
  let processSettled = false;
  let resumed = false;
  let cleanupAction: string | null = null;
  let liveContextId: string | null = null;
  let interactionFailure: unknown;
  let failureCleanup: JsonRecord | null = null;
  const markPhase = (phase: string) =>
    console.error(`[Titanic image editor ${nodeId}] ${phase}`);
  const restoreApiCapture = async () => {
    try {
      await page.evaluate(() => {
        const restore = (globalThis as any).__lfTitanicRestoreEditorApi;
        if (typeof restore === 'function') restore();
      });
    } catch {
      // The browser may already be closing during global abort cleanup.
    }
  };

  const clickTreeNode = async (label: string): Promise<boolean> =>
    page.evaluate(
      ({ id, exactLabel }) => {
        const app = (window as any).comfyAPI.app.app;
        const graph = app.rootGraph ?? app.graph;
        const node = graph.getNodeById(id);
        const widget = node?.widgets?.find((candidate: any) => candidate.name === 'ui_widget');
        const state = widget?.options?.getState?.();
        const tree = state?.elements?.imageviewer?.shadowRoot?.querySelector('#details-tree');
        const nodes = [...(tree?.shadowRoot?.querySelectorAll('.node') ?? [])] as HTMLElement[];
        const target = nodes.find(
          (element) =>
            element.querySelector('.node__value')?.textContent?.trim() === exactLabel,
        );
        const content = target?.querySelector('.node__content') as HTMLElement | null;
        content?.click();
        return Boolean(content);
      },
      { id: nodeId, exactLabel: label },
    );

  const readCapturedProcessState = async () => {
    let capturedProcessStarted = processStarted;
    let capturedProcessSettled = processSettled;
    try {
      const captureState = await page.evaluate(() => {
        const record = (globalThis as any).__lfTitanicEditorApiCapture?.process?.[0];
        return {
          started: Boolean(record),
          settled: Boolean(record?.finishedAt || record?.error),
        };
      });
      capturedProcessStarted ||= captureState.started;
      capturedProcessSettled ||= captureState.settled;
    } catch {
      // Fall back to the Node-side state when the browser is already unavailable.
    }
    processStarted = capturedProcessStarted;
    processSettled = capturedProcessSettled;
    return {
      started: capturedProcessStarted,
      settled: capturedProcessSettled,
    };
  };

  const recoverPendingContextId = async (): Promise<string | null> => {
    try {
      return await page.evaluate(async ({ id, callerClientId }) => {
        const body = new FormData();
        body.append('node_id', String(id));
        body.append('caller_client_id', callerClientId);
        const response = await fetch('/lf-nodes/recover-edit-dataset', {
          method: 'POST',
          body,
        });
        if (!response.ok) return null;
        const contextId = (await response.json())?.data?.context_id;
        return typeof contextId === 'string' && contextId ? contextId : null;
      }, { id: nodeId, callerClientId });
    } catch {
      return null;
    }
  };

  const safeResume = async (): Promise<JsonRecord> => {
    if (resumed) {
      return {
        state: 'release-requested',
        action: cleanupAction ?? 'normal-save-and-resume',
        contextId: liveContextId,
        processExpected,
        processStarted,
        processSettled,
      };
    }

    let captureState = await readCapturedProcessState();
    let drainAttempted = false;
    if (processExpected && !captureState.settled) {
      drainAttempted = true;
      try {
        await page.waitForFunction(
          () => {
            const record = (globalThis as any).__lfTitanicEditorApiCapture?.process?.[0];
            return Boolean(record?.finishedAt || record?.error);
          },
          undefined,
          { timeout: 5_000 },
        );
      } catch {
        // A processing request has no exact cancellation seam. Preserve the
        // session instead of resuming through work that may still commit.
      }
      captureState = await readCapturedProcessState();
    }
    if (captureState.started && !captureState.settled) {
      cleanupAction = 'preserved-exact-session-while-processing-remained-in-flight';
      return {
        state: 'residue-preserved',
        action: cleanupAction,
        contextId: liveContextId,
        processExpected,
        processStarted: true,
        processSettled: false,
        drainMilliseconds: 5_000,
      };
    }

    try {
      const button = page
        .locator(`div:has(> ${editorSelector})`)
        .locator('lf-button[title*="resume the workflow"] [part="button"]')
        .first();
      if (await button.isVisible({ timeout: 2_000 })) {
        await button.click({ force: true, timeout: 5_000 });
        cleanupAction = 'resumed-without-committing-after-interaction-failure';
        resumed = true;
      }
    } catch {
      // Fall through to the exact pending-session release below.
    }
    if (!resumed && liveContextId) {
      try {
        const released = await page.evaluate(
          async ({ id, contextId, callerClientId }) => {
            const recoverBody = new FormData();
            recoverBody.append('node_id', String(id));
            recoverBody.append('context_id', contextId);
            recoverBody.append('caller_client_id', callerClientId);
            const recovery = await fetch('/lf-nodes/recover-edit-dataset', {
              method: 'POST',
              body: recoverBody,
            });
            const recovered = recovery.ok ? (await recovery.json())?.data : null;
            if (recovered?.context_id !== contextId) return false;
            if (recovered?.owner_client_id !== callerClientId) return false;
            const status = recovered.columns?.find((column: any) => column?.id === 'status');
            if (!status || status.title !== 'pending') return false;
            status.title = 'completed';
            const updateBody = new FormData();
            updateBody.append('file_path', contextId);
            updateBody.append('dataset', JSON.stringify(recovered));
            updateBody.append('caller_client_id', callerClientId);
            const updated = await fetch('/lf-nodes/update-json', {
              method: 'POST',
              body: updateBody,
            });
            return updated.ok;
          },
          { id: nodeId, contextId: liveContextId, callerClientId },
        );
        if (released) {
          cleanupAction = 'released-exact-pending-session-after-interaction-failure';
          resumed = true;
        }
      } catch {
        // The exact prompt timeout/cancellation path remains authoritative.
      }
    }
    const observedContextId = liveContextId ?? (await recoverPendingContextId());
    if (!resumed && observedContextId && !cleanupAction) {
      cleanupAction = 'preserved-pending-session-observed-by-node-recovery';
    }
    return {
      state: resumed ? 'release-requested' : observedContextId ? 'residue-preserved' : 'no-context',
      action: cleanupAction,
      contextId: observedContextId,
      contextIdSource: liveContextId ? 'live-widget' : observedContextId ? 'node-recovery-probe' : null,
      processExpected,
      processStarted: captureState.started,
      processSettled: captureState.settled,
      drainMilliseconds: drainAttempted ? 5_000 : 0,
    };
  };

  try {
    await page.waitForFunction(
      (id) => {
        const app = (window as any).comfyAPI?.app?.app;
        const graph = app?.rootGraph ?? app?.graph;
        const node = graph?.getNodeById?.(id);
        const widget = node?.widgets?.find((candidate: any) => candidate.name === 'ui_widget');
        const state = widget?.options?.getState?.();
        const dataset = state?.elements?.imageviewer?.lfDataset;
        const status = dataset?.columns?.find((column: any) => column?.id === 'status')?.title;
        return (
          state?.status === 'ready' &&
          status === 'pending' &&
          typeof dataset?.context_id === 'string' &&
          dataset.context_id.length > 0 &&
          Array.isArray(dataset?.nodes) &&
          dataset.nodes.length > 0
        );
      },
      nodeId,
      { timeout: timeoutMs },
    );

    const pending = await page.evaluate((id) => {
      const app = (window as any).comfyAPI.app.app;
      const graph = app.rootGraph ?? app.graph;
      const node = graph.getNodeById(id);
      const widget = node.widgets.find((candidate: any) => candidate.name === 'ui_widget');
      const state = widget.options.getState();
      const imageviewer = state.elements.imageviewer;
      const dataset = imageviewer.lfDataset;
      imageviewer.dataset.e2eEditor = String(id);
      if (app.canvas?.ds) app.canvas.ds.scale = 0.8;
      app.canvas?.centerOnNode?.(node);
      app.canvas?.setDirty?.(true, true);
      const firstCell = dataset.nodes[0]?.cells?.lfImage ?? {};
      return {
        contextId: dataset.context_id,
        ownerClientId: dataset.owner_client_id,
        sourceUrl: firstCell.lfValue ?? firstCell.value,
        status: dataset.columns?.find((column: any) => column?.id === 'status')?.title,
      };
    }, nodeId);
    if (!pending.contextId || !pending.sourceUrl || pending.status !== 'pending') {
      throw new Error('image editor did not expose a live pending source');
    }
    liveContextId = pending.contextId;
    markPhase('pending session ready');

    const recovered = await page.evaluate(
      async ({ id, contextId, callerClientId }) => {
        const recover = async (caller: string) => {
          const body = new FormData();
          body.append('node_id', String(id));
          body.append('context_id', contextId);
          body.append('caller_client_id', caller);
          const response = await fetch('/lf-nodes/recover-edit-dataset', {
            method: 'POST',
            body,
          });
          return { status: response.status, payload: await response.json() };
        };
        return {
          wrongOwner: await recover(`${callerClientId}:wrong-owner-probe`),
          correctOwner: await recover(callerClientId),
        };
      },
      { id: nodeId, contextId: pending.contextId, callerClientId },
    );
    if (
      recovered.wrongOwner.status !== 200 ||
      recovered.wrongOwner.payload?.data !== null
    ) {
      throw new Error('pending image editor context leaked to a wrong-owner recovery probe');
    }
    if (
      recovered.correctOwner.status !== 200 ||
      recovered.correctOwner.payload?.data?.context_id !== pending.contextId
    ) {
      throw new Error('pending image editor context was not recoverable by exact owner and context');
    }
    const recoveredDataset = recovered.correctOwner.payload.data as JsonRecord;
    if (
      pending.ownerClientId !== callerClientId ||
      recoveredDataset.owner_client_id !== callerClientId
    ) {
      throw new Error('pending image editor owner changed across exact recovery');
    }

    const sourceProbe = await page.evaluate(async (url) => {
      const response = await fetch(url);
      const bytes = await response.arrayBuffer();
      return {
        ok: response.ok,
        status: response.status,
        byteLength: bytes.byteLength,
        contentType: response.headers.get('content-type'),
      };
    }, pending.sourceUrl);
    if (!sourceProbe.ok || sourceProbe.byteLength < 100) {
      throw new Error(`editor source preview does not resolve: ${JSON.stringify(sourceProbe)}`);
    }

    await page.waitForTimeout(250);
    const firstImage = page.locator(`${editorSelector} #navigation-masonry lf-image [part="image"]`).first();
    await firstImage.waitFor({ state: 'visible', timeout: timeoutMs });
    await firstImage.click();
    await page.waitForFunction(
      async (id) => {
        const app = (window as any).comfyAPI.app.app;
        const graph = app.rootGraph ?? app.graph;
        const node = graph.getNodeById(id);
        const widget = node.widgets.find((candidate: any) => candidate.name === 'ui_widget');
        const imageviewer = widget.options.getState().elements.imageviewer;
        const snapshot = await imageviewer.getCurrentSnapshot();
        return snapshot?.shape?.index === 0;
      },
      nodeId,
      { timeout: 30_000 },
    );
    markPhase('source image selected');

    let inpaintFound = await clickTreeNode('Inpaint');
    if (!inpaintFound) {
      if (!(await clickTreeNode('Diffusion Tools'))) {
        throw new Error('image editor Diffusion Tools group is missing');
      }
      await page.waitForTimeout(150);
      inpaintFound = await clickTreeNode('Inpaint');
    }
    if (!inpaintFound) {
      throw new Error('image editor Inpaint tool is missing after expanding Diffusion Tools');
    }
    await page.waitForFunction(
      (id) => {
        const app = (window as any).comfyAPI.app.app;
        const graph = app.rootGraph ?? app.graph;
        const node = graph.getNodeById(id);
        const widget = node.widgets.find((candidate: any) => candidate.name === 'ui_widget');
        const state = widget.options.getState();
        return state.filterType === 'inpaint' && state.filterNodeId === 'inpaint';
      },
      nodeId,
      { timeout: 30_000 },
    );
    markPhase('Inpaint tool selected');

    const controlValues = await page.evaluate(async (id) => {
      const app = (window as any).comfyAPI.app.app;
      const graph = app.rootGraph ?? app.graph;
      const node = graph.getNodeById(id);
      const widget = node.widgets.find((candidate: any) => candidate.name === 'ui_widget');
      const state = widget.options.getState();
      const controls = state.elements.controls;
      const desired: Record<string, string | number> = {
        positive_prompt: 'Replace only the masked patch with a vivid red painted texture.',
        negative_prompt: '',
        conditioning_mix: 1,
        denoise_percentage: 100,
        cfg: 7,
        steps: 4,
        upsample_target: 0,
        roi_padding: 8,
        roi_align: 8,
        roi_min_size: 64,
        dilate: 0,
        feather: 0,
        seed: '42',
        sampler: 'euler',
        scheduler: 'normal',
        roi_align_auto: 'off',
        apply_unsharp_mask: 'off',
        wd14_tagging: 'off',
      };
      for (const [controlId, value] of Object.entries(desired)) {
        const control = controls[controlId];
        if (!control?.setValue) throw new Error(`missing image editor control ${controlId}`);
        await control.setValue(value);
        await control.refresh?.();
      }
      const observed: Record<string, unknown> = {};
      for (const controlId of Object.keys(desired)) {
        observed[controlId] = await controls[controlId].getValue();
      }
      return observed;
    }, nodeId);
    markPhase('deterministic controls applied');

    await page.evaluate(
      ({ processEndpoint, updateEndpoint }) => {
        const target = (window as any).comfyAPI.api.api;
        const previousRestore = (globalThis as any).__lfTitanicRestoreEditorApi;
        if (typeof previousRestore === 'function') previousRestore();
        const original = target.fetchApi;
        const capture = {
          process: [] as any[],
          update: [] as any[],
        };
        (globalThis as any).__lfTitanicEditorApiCapture = capture;
        const wrapper = async function (this: unknown, route: string, init: RequestInit = {}) {
          const path = new URL(String(route), window.location.href).pathname;
          const bucket =
            path === processEndpoint
              ? capture.process
              : path === updateEndpoint
                ? capture.update
                : null;
          if (!bucket) return original.call(this, route, init);
          const fields: Record<string, string> = {};
          if (init.body instanceof FormData) {
            for (const [key, value] of init.body.entries()) {
              fields[key] = typeof value === 'string' ? value : `[file:${value.name}]`;
            }
          }
          const record: any = { fields, path, startedAt: Date.now() };
          bucket.push(record);
          try {
            const response = await original.call(this, route, init);
            record.status = response.status;
            const text = await response.clone().text();
            try {
              record.payload = text ? JSON.parse(text) : {};
            } catch {
              record.payload = { raw: text.slice(0, 1_000) };
            }
            record.finishedAt = Date.now();
            return response;
          } catch (error) {
            record.error = String(error);
            record.finishedAt = Date.now();
            throw error;
          }
        };
        target.fetchApi = wrapper;
        (globalThis as any).__lfTitanicRestoreEditorApi = () => {
          if (target.fetchApi === wrapper) target.fetchApi = original;
          delete (globalThis as any).__lfTitanicRestoreEditorApi;
        };
      },
      { processEndpoint: processPath, updateEndpoint: updatePath },
    );

    const board = page.locator(`${editorSelector} #details-canvas canvas.canvas__board`).first();
    await board.waitFor({ state: 'visible', timeout: 30_000 });
    const box = await board.boundingBox();
    if (!box || box.width < 32 || box.height < 32) {
      throw new Error(`image editor drawing board is not interactable: ${JSON.stringify(box)}`);
    }

    const points = [
      [0.40, 0.48],
      [0.44, 0.44],
      [0.49, 0.48],
      [0.54, 0.44],
      [0.60, 0.48],
      [0.56, 0.54],
      [0.50, 0.50],
      [0.44, 0.54],
      [0.40, 0.48],
    ];
    processExpected = true;
    await page.mouse.move(box.x + box.width * points[0][0], box.y + box.height * points[0][1]);
    await page.mouse.down();
    for (const [x, y] of points.slice(1)) {
      await page.mouse.move(box.x + box.width * x, box.y + box.height * y, { steps: 3 });
    }
    await page.mouse.up();
    markPhase('brush stroke submitted');
    await page.waitForFunction(
      () => ((globalThis as any).__lfTitanicEditorApiCapture?.process?.length ?? 0) > 0,
      undefined,
      { timeout: timeoutMs },
    );
    processStarted = true;
    markPhase('inpaint request captured');
    await page.waitForFunction(
      () => {
        const records = (globalThis as any).__lfTitanicEditorApiCapture?.process ?? [];
        const record = records[0];
        return Boolean(record?.finishedAt || record?.error);
      },
      undefined,
      { timeout: timeoutMs },
    );
    const processCapture = await page.evaluate(() =>
      JSON.parse(JSON.stringify((globalThis as any).__lfTitanicEditorApiCapture?.process ?? [])),
    );
    if (processCapture.length !== 1) {
      throw new Error(`expected one inpaint request, observed ${processCapture.length}`);
    }
    const processRecord = processCapture[0] as JsonRecord;
    processSettled = true;
    markPhase('inpaint response received');
    if (processRecord.error || processRecord.status !== 200) {
      throw new Error(
        `inpaint request failed with ${processRecord.status}: ${JSON.stringify(processRecord.payload ?? processRecord.error).slice(0, 500)}`,
      );
    }

    const fields = processRecord.fields as Record<string, string>;
    const settings = JSON.parse(fields.settings ?? '{}') as JsonRecord;
    if (fields.type !== 'inpaint') throw new Error(`unexpected editor filter ${fields.type}`);
    if (fields.url !== pending.sourceUrl) throw new Error('inpaint source URL changed before submit');
    if (fields.caller_client_id !== callerClientId) {
      throw new Error('inpaint request was not bound to the connected Comfy client');
    }
    if (fields.context_id !== pending.contextId) {
      throw new Error('inpaint request was not bound to the exact editing context');
    }
    if (settings.context_id !== pending.contextId) throw new Error('inpaint context id mismatch');
    const expectedSettings: Record<string, string | number> = {
      conditioning_mix: 1,
      denoise_percentage: 100,
      cfg: 7,
      steps: 4,
      upsample_target: 0,
      roi_padding: 8,
      roi_align: 8,
      roi_min_size: 64,
      dilate: 0,
      feather: 0,
      seed: 42,
      sampler: 'euler',
      scheduler: 'normal',
    };
    for (const [key, expected] of Object.entries(expectedSettings)) {
      if (settings[key] !== expected) {
        throw new Error(`inpaint setting ${key} was ${JSON.stringify(settings[key])}, expected ${JSON.stringify(expected)}`);
      }
    }
    for (const key of ['roi_align_auto', 'apply_unsharp_mask', 'wd14_tagging']) {
      if (String(settings[key]) !== 'false') {
        throw new Error(`inpaint setting ${key} was not disabled`);
      }
    }
    if (!String(settings.positive_prompt ?? '').includes('vivid red painted texture')) {
      throw new Error('inpaint positive prompt was not submitted');
    }
    const canvasMatch = /^data:image\/png;base64,([A-Za-z0-9+/=]+)$/.exec(
      String(settings.b64_canvas ?? ''),
    );
    if (!canvasMatch) throw new Error('inpaint request has no PNG brush canvas');
    const brushPng = Buffer.from(canvasMatch[1], 'base64');
    if (
      brushPng.length < 100 ||
      brushPng.subarray(0, 8).toString('hex') !== '89504e470d0a1a0a'
    ) {
      throw new Error('inpaint brush canvas is not a valid nonempty PNG payload');
    }

    const responsePayload = processRecord.payload as JsonRecord;
    if (
      responsePayload.status !== 'success' ||
      typeof responsePayload.data !== 'string' ||
      typeof responsePayload.mask !== 'string'
    ) {
      throw new Error(`invalid inpaint response: ${JSON.stringify(responsePayload).slice(0, 500)}`);
    }

      const pixelProof = await page.evaluate(
        async ({ sourceUrl, resultUrl, maskUrl }) => {
          const decode = async (url: string) => {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`${url} returned ${response.status}`);
            const bitmap = await createImageBitmap(await response.blob());
            const canvas = new OffscreenCanvas(bitmap.width, bitmap.height);
            const context = canvas.getContext('2d', { willReadFrequently: true });
            if (!context) throw new Error('2D canvas context is unavailable');
            context.drawImage(bitmap, 0, 0);
            const pixels = context.getImageData(0, 0, bitmap.width, bitmap.height).data;
            const digest = await crypto.subtle.digest('SHA-256', pixels);
            const sha256 = [...new Uint8Array(digest)]
              .map((value) => value.toString(16).padStart(2, '0'))
              .join('');
            return { width: bitmap.width, height: bitmap.height, pixels, sha256 };
          };
          const [source, result, mask] = await Promise.all([
            decode(sourceUrl),
            decode(resultUrl),
            decode(maskUrl),
          ]);
          if (
            source.width !== result.width ||
            source.height !== result.height ||
            source.width !== mask.width ||
            source.height !== mask.height
          ) {
            throw new Error('source, result, and mask dimensions differ');
          }
          let maskPixels = 0;
          let insideDiff = 0;
          let outsideMaxDiff = 0;
          let outsideChangedPixels = 0;
          let minX = source.width;
          let minY = source.height;
          let maxX = -1;
          let maxY = -1;
          for (let y = 0; y < source.height; y += 1) {
            for (let x = 0; x < source.width; x += 1) {
              const offset = (y * source.width + x) * 4;
              const masked =
                (mask.pixels[offset] + mask.pixels[offset + 1] + mask.pixels[offset + 2]) /
                  3 >
                127;
              let pixelMaxDiff = 0;
              for (let channel = 0; channel < 3; channel += 1) {
                const difference = Math.abs(
                  source.pixels[offset + channel] - result.pixels[offset + channel],
                );
                pixelMaxDiff = Math.max(pixelMaxDiff, difference);
                if (masked) insideDiff += difference;
              }
              if (masked) {
                maskPixels += 1;
                minX = Math.min(minX, x);
                minY = Math.min(minY, y);
                maxX = Math.max(maxX, x);
                maxY = Math.max(maxY, y);
              } else {
                outsideMaxDiff = Math.max(outsideMaxDiff, pixelMaxDiff);
                if (pixelMaxDiff > 1) outsideChangedPixels += 1;
              }
            }
          }
          return {
            width: source.width,
            height: source.height,
            sourceSha256: source.sha256,
            resultSha256: result.sha256,
            maskPixels,
            maskCoverage: maskPixels / (source.width * source.height),
            maskBounds: { minX, minY, maxX, maxY },
            insideMeanAbsoluteDifference: maskPixels ? insideDiff / (maskPixels * 3) : 0,
            outsideMaxDiff,
            outsideChangedPixels,
          };
        },
        {
          sourceUrl: pending.sourceUrl,
          resultUrl: responsePayload.data,
          maskUrl: responsePayload.mask,
        },
      );
      const bounds = pixelProof.maskBounds;
      if (pixelProof.maskPixels < 1 || pixelProof.maskCoverage >= 0.5) {
        throw new Error(`inpaint mask coverage is not bounded: ${JSON.stringify(pixelProof)}`);
      }
      if (
        bounds.minX > pixelProof.width * 0.7 ||
        bounds.maxX < pixelProof.width * 0.3 ||
        bounds.minY > pixelProof.height * 0.7 ||
        bounds.maxY < pixelProof.height * 0.3
      ) {
        throw new Error(`inpaint mask missed the central gesture: ${JSON.stringify(bounds)}`);
      }
      if (
        pixelProof.sourceSha256 === pixelProof.resultSha256 ||
        pixelProof.insideMeanAbsoluteDifference <= 0.5
      ) {
        throw new Error(`inpaint result did not materially change masked pixels: ${JSON.stringify(pixelProof)}`);
      }
      if (pixelProof.outsideMaxDiff > 1 || pixelProof.outsideChangedPixels > 0) {
        throw new Error(`inpaint modified pixels outside the binary mask: ${JSON.stringify(pixelProof)}`);
      }
      markPhase('mask and pixel proof passed');

      await page.waitForFunction(
        async ({ id, resultUrl }) => {
          const app = (window as any).comfyAPI.app.app;
          const graph = app.rootGraph ?? app.graph;
          const node = graph.getNodeById(id);
          const widget = node.widgets.find((candidate: any) => candidate.name === 'ui_widget');
          const imageviewer = widget.options.getState().elements.imageviewer;
          const snapshot = await imageviewer.getCurrentSnapshot();
          const index = imageviewer.currentShape?.index;
          return snapshot?.value === resultUrl && imageviewer.history?.[index]?.length > 1;
        },
        { id: nodeId, resultUrl: responsePayload.data },
        { timeout: 30_000 },
      );

      const saveButton = page
        .locator(`${editorSelector} #details-save [part="button"]`)
        .first();
      await saveButton.waitFor({ state: 'visible', timeout: 30_000 });
      await page.waitForFunction(
        async (id) => {
          const app = (window as any).comfyAPI.app.app;
          const graph = app.rootGraph ?? app.graph;
          const node = graph.getNodeById(id);
          const widget = node.widgets.find((candidate: any) => candidate.name === 'ui_widget');
          const imageviewer = widget.options.getState().elements.imageviewer;
          const details = (await imageviewer.getComponents()).details;
          const save = imageviewer.shadowRoot?.querySelector('#details-save');
          return details?.save?.lfUiState === 'success' || (save as any)?.lfUiState === 'success';
        },
        nodeId,
        { timeout: 30_000 },
      );
      await saveButton.click({ timeout: 30_000 });
      markPhase('save control activated');
      const committed = await page.evaluate(async ({ id, resultUrl }) => {
        const artifactKey = (value: unknown) => {
          const raw = String(value ?? '');
          const url = new URL(raw, window.location.href);
          if (url.pathname !== '/view') return `${url.pathname}${url.search}`;
          const params = new URLSearchParams();
          for (const key of ['filename', 'type', 'subfolder']) {
            params.set(key, url.searchParams.get(key) ?? '');
          }
          return `${url.pathname}?${params.toString()}`;
        };
        const resultArtifact = artifactKey(resultUrl);
        const app = (window as any).comfyAPI.app.app;
        const graph = app.rootGraph ?? app.graph;
        const node = graph.getNodeById(id);
        const widget = node.widgets.find((candidate: any) => candidate.name === 'ui_widget');
        const state = widget.options.getState();
        const imageviewer = state.elements.imageviewer;
        const deadline = Date.now() + 30_000;
        while (Date.now() < deadline) {
          const dataset = imageviewer.lfDataset;
          const selectedIndex = dataset?.selection?.index ?? imageviewer.currentShape?.index ?? 0;
          const imageCell = dataset?.nodes?.[selectedIndex]?.cells?.lfImage ?? {};
          const committedUrl = imageCell.lfValue ?? imageCell.value;
          const historyLength = imageviewer.history?.[selectedIndex]?.length ?? 0;
          const snapshot = await imageviewer.getCurrentSnapshot();
          const snapshotMatches = !snapshot || artifactKey(snapshot.value) === resultArtifact;
          if (
            artifactKey(committedUrl) === resultArtifact &&
            historyLength <= 1 &&
            snapshotMatches
          ) {
            let nonemptyMaskPixels = 0;
            const canvasComponent = (await imageviewer.getComponents()).details.canvas;
            if (canvasComponent) {
              const board = await canvasComponent.getCanvas('board');
              const pixels = board
                .getContext('2d', { willReadFrequently: true })
                .getImageData(0, 0, board.width, board.height).data;
              for (let offset = 3; offset < pixels.length; offset += 4) {
                if (pixels[offset] > 0) nonemptyMaskPixels += 1;
              }
            }
            return { committedUrl, historyLength, nonemptyMaskPixels, selectedIndex };
          }
          await new Promise((resolvePromise) => setTimeout(resolvePromise, 100));
        }
        const dataset = imageviewer.lfDataset;
        const selectedIndex = dataset?.selection?.index ?? imageviewer.currentShape?.index ?? 0;
        const urls = (dataset?.nodes ?? []).map((entry: any) => {
          const cell = entry?.cells?.lfImage ?? {};
          return cell.lfValue ?? cell.value ?? null;
        });
        const historyLengths = Object.fromEntries(
          Object.entries(imageviewer.history ?? {}).map(([key, value]) => [
            key,
            Array.isArray(value) ? value.length : null,
          ]),
        );
        throw new Error(
          `edited snapshot was not committed to the dataset: ${JSON.stringify({ selectedIndex, urls, historyLengths })}`,
        );
      }, { id: nodeId, resultUrl: responsePayload.data });
      if (committed.nonemptyMaskPixels !== 0) {
        throw new Error('image editor brush canvas was not cleared after commit');
      }
      markPhase('edited snapshot committed');

      const resumeButton = page
        .locator(`div:has(> ${editorSelector})`)
        .locator('lf-button[title*="resume the workflow"] [part="button"]')
        .first();
      await resumeButton.waitFor({ state: 'visible', timeout: 30_000 });
      const updateCountBefore = await page.evaluate(
        () => (globalThis as any).__lfTitanicEditorApiCapture?.update?.length ?? 0,
      );
      await resumeButton.click({ timeout: 30_000 });
      await page.waitForFunction(
        (previousCount) => {
          const records = (globalThis as any).__lfTitanicEditorApiCapture?.update ?? [];
          const record = records[previousCount];
          return records.length > previousCount && Boolean(record?.finishedAt || record?.error);
        },
        updateCountBefore,
        { timeout: 30_000 },
      );
      const updateRecord = await page.evaluate((index) => {
        const record = (globalThis as any).__lfTitanicEditorApiCapture?.update?.[index];
        return record ? JSON.parse(JSON.stringify(record)) : null;
      }, updateCountBefore);
      if (!updateRecord || updateRecord.error || updateRecord.status !== 200) {
        throw new Error(
          `editing session completion update failed: ${JSON.stringify(updateRecord).slice(0, 500)}`,
        );
      }
      const updateFields = updateRecord.fields as Record<string, string>;
      const completedDataset = JSON.parse(updateFields.dataset ?? '{}') as JsonRecord;
      const completedStatus = completedDataset.columns?.find(
        (column: JsonRecord) => column?.id === 'status',
      )?.title;
      const completedCell = completedDataset.nodes?.[committed.selectedIndex]?.cells?.lfImage ?? {};
      const completedUrl = completedCell.lfValue ?? completedCell.value;
      if (
        updateFields.file_path !== pending.contextId ||
        updateFields.caller_client_id !== callerClientId ||
        completedDataset.context_id !== pending.contextId ||
        completedStatus !== 'completed' ||
        comfyArtifactKey(completedUrl) !== comfyArtifactKey(responsePayload.data)
      ) {
        throw new Error('completed editing dataset did not retain the committed inpaint result');
      }
      const clientBindingErrors = validateEditorClientBinding({
        callerClientId,
        contextId: pending.contextId,
        pendingOwnerClientId: pending.ownerClientId,
        recoveredOwnerClientId: recoveredDataset.owner_client_id,
        completedOwnerClientId: completedDataset.owner_client_id,
        processCallerClientId: fields.caller_client_id,
        processContextId: fields.context_id,
        updateCallerClientId: updateFields.caller_client_id,
        updateContextId: updateFields.file_path,
        completedContextId: completedDataset.context_id,
        wrongOwnerRecoveryData: recovered.wrongOwner.payload?.data,
      });
      if (clientBindingErrors.length) {
        throw new Error(clientBindingErrors.join('; '));
      }
      const resumedAt = Number(updateRecord.finishedAt ?? Date.now());
      resumed = true;
      markPhase('workflow resumed with committed edit');

      const { b64_canvas: _brushCanvas, ...submittedSettings } = settings;
      return {
        action: 'inpaint-save-resume',
        nodeId,
        callerClientId,
        ownerClientId: completedDataset.owner_client_id,
        contextId: pending.contextId,
        sourceUrl: pending.sourceUrl,
        resultUrl: responsePayload.data,
        maskUrl: responsePayload.mask,
        sourceProbe,
        controlValues,
        submittedSettings,
        brushPngBytes: brushPng.length,
        pixelProof,
        committed,
        completedStatus,
        clientBinding: {
          pendingOwnerClientId: pending.ownerClientId,
          recoveredOwnerClientId: recoveredDataset.owner_client_id,
          completedOwnerClientId: completedDataset.owner_client_id,
          processCallerClientId: fields.caller_client_id,
          processContextId: fields.context_id,
          updateCallerClientId: updateFields.caller_client_id,
          updateContextId: updateFields.file_path,
          completedContextId: completedDataset.context_id,
          wrongOwnerRecoveryDenied: recovered.wrongOwner.payload?.data === null,
        },
        processRequestCount: processCapture.length,
        resumedAt,
        cleanupAction,
      };
  } catch (error) {
    interactionFailure = error;
  } finally {
    failureCleanup = await safeResume();
    await restoreApiCapture();
  }

  return {
    action: 'inpaint-interaction-failed',
    error: String(interactionFailure ?? 'unknown image editor failure'),
    nodeId,
    contextId: liveContextId ?? failureCleanup?.contextId ?? null,
    cleanup: failureCleanup,
  };
};

const inspectEditingSessionCleanup = async (
  page: Page,
  interaction: JsonRecord,
): Promise<JsonRecord | null> => {
  const nodeId = interaction.nodeId;
  if (typeof nodeId !== 'number') return null;
  let callerClientId: string;
  try {
    callerClientId = await requireComfyClientId(page, 10_000);
  } catch (error) {
    return {
      cleanupProven: false,
      residue: true,
      contextId: interaction.contextId ?? null,
      nodeId,
      pathValid: null,
      error: `editing-session caller identity could not be proven: ${String(error)}`,
    };
  }
  let contextId = interaction.contextId;
  let contextIdSource = 'interaction';
  if (typeof contextId !== 'string' || !contextId) {
    try {
      contextId = await page.evaluate(async ({ id, callerClientId }) => {
        const body = new FormData();
        body.append('node_id', String(id));
        body.append('caller_client_id', callerClientId);
        const response = await fetch('/lf-nodes/recover-edit-dataset', {
          method: 'POST',
          body,
        });
        if (!response.ok) throw new Error(`recover-edit-dataset returned ${response.status}`);
        return (await response.json())?.data?.context_id ?? null;
      }, { id: nodeId, callerClientId });
      contextIdSource = 'post-terminal-node-recovery';
    } catch (error) {
      return {
        cleanupProven: false,
        residue: true,
        contextId: null,
        nodeId,
        pathValid: null,
        error: `editing-session absence could not be proven: ${String(error)}`,
      };
    }
  }
  if (typeof contextId !== 'string' || !contextId) return null;
  const tempRoot = resolve(repoRoot, '..', '..', 'temp');
  const contextPath = resolve(contextId);
  const relativePath = relative(tempRoot, contextPath);
  const expectedName = new RegExp(`^${nodeId}_[0-9a-f]{32}_edit_dataset\\.json$`, 'i');
  if (
    !relativePath ||
    relativePath.startsWith('..') ||
    resolve(tempRoot, relativePath) !== contextPath ||
    !expectedName.test(basename(contextPath))
  ) {
    return {
      cleanupProven: false,
      residue: true,
      contextId,
      nodeId,
      contextIdSource,
      pathValid: false,
      error: `image editor returned an invalid context path: ${contextId}`,
    };
  }

  let fileExists = false;
  let fileStatus: string | null = null;
  let fileOwnerClientId: string | null = null;
  let filesystemError: string | null = null;
  try {
    await stat(contextPath);
    fileExists = true;
    try {
      const dataset = JSON.parse(await readFile(contextPath, 'utf8')) as JsonRecord;
      fileStatus =
        dataset.columns?.find((column: JsonRecord) => column?.id === 'status')?.title ?? null;
      fileOwnerClientId =
        typeof dataset.owner_client_id === 'string' ? dataset.owner_client_id : null;
    } catch (error: any) {
      if (error?.code === 'ENOENT') {
        fileExists = false;
      } else {
        filesystemError = `editing session JSON could not be read: ${String(error)}`;
      }
    }
  } catch (error: any) {
    if (error?.code !== 'ENOENT') {
      filesystemError = `editing session cleanup could not be proven: ${String(error)}`;
    }
  }

  let recoveredContextId: string | null = null;
  let recoveryProbed = false;
  let recoveryError: string | null = null;
  try {
    const recovered = await page.evaluate(async ({ id, contextId, callerClientId }) => {
      const body = new FormData();
      body.append('node_id', String(id));
      body.append('context_id', contextId);
      body.append('caller_client_id', callerClientId);
      const response = await fetch('/lf-nodes/recover-edit-dataset', { method: 'POST', body });
      if (!response.ok) throw new Error(`recover-edit-dataset returned ${response.status}`);
      return (await response.json())?.data?.context_id ?? null;
    }, { id: nodeId, contextId, callerClientId });
    recoveryProbed = true;
    recoveredContextId = typeof recovered === 'string' ? recovered : null;
  } catch (error) {
    recoveryError = String(error);
  }

  const recoverable = recoveredContextId === contextId;
  const cleanupProven =
    !fileExists && !filesystemError && recoveryProbed && !recoveryError && !recoverable;
  return {
    cleanupProven,
    residue: fileExists || recoverable || !cleanupProven,
    contextId,
    nodeId,
    contextIdSource,
    pathValid: true,
    fileExists,
    fileStatus,
    fileOwnerClientId,
    callerClientId,
    ownerUnchanged:
      fileOwnerClientId === null || fileOwnerClientId === interaction.ownerClientId,
    recoverable,
    recoveredContextId,
    filesystemError,
    recoveryError,
  };
};

const exactCancel = async (
  comfyUrl: string,
  promptId: string,
): Promise<{
  requested: boolean;
  fallback: string | null;
  acknowledged?: 'cancelled' | 'no-op';
  error?: string;
}> => {
  // Core's single-job endpoint atomically targets only this prompt ID. The
  // compatibility fallback may remove only this ID while it is still pending;
  // there is deliberately no global /interrupt or queue-clear fallback.
  try {
    const response = (await jsonFetch(
      `${comfyUrl}/api/jobs/${encodeURIComponent(promptId)}/cancel`,
      { method: 'POST' },
      10_000,
    )) as JsonRecord;
    const cancelled = response?.cancelled === true;
    return {
      requested: cancelled,
      fallback: null,
      acknowledged: cancelled ? 'cancelled' : 'no-op',
    };
  } catch (primaryError) {
    try {
      const queue = await queueIsEmpty(comfyUrl);
      if (queue.parsed.pending.has(promptId)) {
        await jsonFetch(`${comfyUrl}/queue`, {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ delete: [promptId] }),
        });
        return {
          requested: true,
          fallback: 'delete-pending-by-id',
          acknowledged: 'cancelled',
        };
      }
      return {
        requested: false,
        fallback: null,
        error: `exact cancellation was rejected: ${String(primaryError)}`,
      };
    } catch (fallbackError) {
      return {
        requested: false,
        fallback: null,
        error: `exact cancellation failed: ${String(primaryError)}; exact pending fallback failed: ${String(fallbackError)}`,
      };
    }
  }
};

const waitForTerminal = async (
  comfyUrl: string,
  promptId: string,
  timeoutSeconds: number,
) => {
  const deadline = Date.now() + timeoutSeconds * 1000;
  const foreignIds = new Set<string>();
  const queueDiagnostics = new Set<string>();
  while (Date.now() < deadline) {
    let historyRaw: unknown;
    let queue: Awaited<ReturnType<typeof queueIsEmpty>>;
    try {
      [historyRaw, queue] = await Promise.all([
        jsonFetch(`${comfyUrl}/history/${encodeURIComponent(promptId)}`),
        queueIsEmpty(comfyUrl),
      ]);
    } catch (error) {
      queueDiagnostics.add(`terminal poll failed: ${String(error)}`);
      await new Promise((resolvePromise) => setTimeout(resolvePromise, 750));
      continue;
    }
    for (const diagnostic of queue.parsed.malformed) queueDiagnostics.add(diagnostic);
    for (const id of queue.ids) if (id !== promptId) foreignIds.add(id);
    const entry = unwrapHistoryEntry(historyRaw, promptId);
    const classification = classifyHistoryEntry(entry);
    if (
      queue.parsed.malformed.length === 0 &&
      (classification === 'success' || classification === 'failure')
    ) {
      if (queue.ids.has(promptId)) {
        await new Promise((resolvePromise) => setTimeout(resolvePromise, 250));
        continue;
      }
      return {
        classification,
        entry,
        foreignIds: [...foreignIds].sort(),
        queueDiagnostics: [...queueDiagnostics].sort(),
        postCancellationDisposition: null,
      };
    }
    await new Promise((resolvePromise) => setTimeout(resolvePromise, 750));
  }
  const cancellation = await exactCancel(comfyUrl, promptId);
  const cleanupDeadline = Date.now() + 30_000;
  let lastEntry: JsonRecord | null = null;
  while (Date.now() < cleanupDeadline) {
    let queue: Awaited<ReturnType<typeof queueIsEmpty>>;
    let historyRaw: unknown;
    try {
      [queue, historyRaw] = await Promise.all([
        queueIsEmpty(comfyUrl),
        jsonFetch(`${comfyUrl}/history/${encodeURIComponent(promptId)}`),
      ]);
    } catch (error) {
      queueDiagnostics.add(`post-cancellation poll failed: ${String(error)}`);
      await new Promise((resolvePromise) => setTimeout(resolvePromise, 750));
      continue;
    }
    for (const diagnostic of queue.parsed.malformed) queueDiagnostics.add(diagnostic);
    for (const id of queue.ids) if (id !== promptId) foreignIds.add(id);
    const entry = unwrapHistoryEntry(historyRaw, promptId);
    lastEntry = entry;
    const postCancellation = classifyPostCancellation(
      classifyHistoryEntry(entry),
      queue.ids.has(promptId),
      queue.parsed.malformed.length > 0,
      cancellation.acknowledged === 'cancelled' && cancellation.requested,
    );
    const timedOutClassification = timedOutTerminalClassification(postCancellation);
    if (timedOutClassification !== null) {
      return {
        classification: timedOutClassification,
        entry,
        foreignIds: [...foreignIds].sort(),
        queueDiagnostics: [...queueDiagnostics].sort(),
        cancellation,
        cleanupProven: true,
        postCancellationDisposition: postCancellation,
      };
    }
    await new Promise((resolvePromise) => setTimeout(resolvePromise, 750));
  }
  return {
    classification: 'orphaned',
    entry: lastEntry,
    foreignIds: [...foreignIds].sort(),
    queueDiagnostics: [...queueDiagnostics].sort(),
    cancellation,
    cleanupProven: false,
    postCancellationDisposition: null,
  };
};

const localModelBlockers = async (options: CliOptions): Promise<string[]> => {
  if (!options.localModelId) {
    return ['--local-model-id is required because Titanic LLM requests omit model'];
  }
  let response: any;
  try {
    response = await jsonFetch(`${options.lmStudioUrl}/api/v1/models`, {}, 10_000);
  } catch (error) {
    return [`local model endpoint is unavailable: ${String(error)}`];
  }
  return validateLoadedModelFixture(
    response,
    options.localModelId,
    options.localInstanceId,
  );
};

const historyPromptIds = async (comfyUrl: string): Promise<Set<string>> => {
  const history = await jsonFetch(`${comfyUrl}/history`);
  return new Set(Object.keys(history ?? {}));
};

const validateCommittedEditPropagation = async (
  page: Page,
  manifestCase: ManifestCase,
  historyEntry: JsonRecord,
  interaction: JsonRecord | undefined,
  executionTrace: ExecutionTrace,
): Promise<{ errors: string[]; evidence: JsonRecord | null }> => {
  const outputNodeId = manifestCase.execution?.committedEditOutputNodeId;
  if (outputNodeId === undefined) return { errors: [], evidence: null };
  const ingressNodeId =
    manifestCase.execution?.committedEditIngressNodeId ?? outputNodeId;
  const errors: string[] = [];
  const sourceUrl = interaction?.sourceUrl;
  const resultUrl = interaction?.resultUrl;
  const sourceSha256 = interaction?.pixelProof?.sourceSha256;
  const resultSha256 = interaction?.pixelProof?.resultSha256;
  const selectedIndex = interaction?.committed?.selectedIndex;
  if (
    typeof sourceUrl !== 'string' ||
    typeof resultUrl !== 'string' ||
    typeof sourceSha256 !== 'string' ||
    typeof resultSha256 !== 'string' ||
    !Number.isInteger(selectedIndex) ||
    selectedIndex < 0
  ) {
    return {
      errors: [
        'committed edit has no source/result URL, pixel digests, and selected-index evidence',
      ],
      evidence: null,
    };
  }
  const historyUrls = collectPreviewUrls(historyEntry.outputs?.[String(outputNodeId)]);
  const ingressHistoryUrl = extractDatasetCellPreviewUrl(
    historyEntry.outputs?.[String(ingressNodeId)],
    selectedIndex,
    'lfImage',
  );
  const eventUrls = executionTrace.executedPreviewUrlsByNode[String(outputNodeId)] ?? [];
  const eventKeys = new Set(eventUrls.map(comfyArtifactKey));
  const historyEventMatches = historyUrls.filter((url) =>
    eventKeys.has(comfyArtifactKey(url)),
  );
  if (!historyEventMatches.length) {
    errors.push(
      `node ${outputNodeId} executed-event previews do not match its exact terminal-history artifacts`,
    );
  }
  if (!historyUrls.length) {
    return {
      errors: [...errors, `node ${outputNodeId} has no terminal-history preview artifacts`],
      evidence: {
        outputNodeId,
        committedResultSha256: resultSha256,
        historyUrls: [],
        eventUrls,
        ingressNodeId,
        ingressHistoryUrl,
        selectedIndex,
      },
    };
  }
  if (!ingressHistoryUrl) {
    return {
      errors: [
        ...errors,
        `node ${ingressNodeId} has no exact lfImage cell at committed index ${selectedIndex}`,
      ],
      evidence: {
        outputNodeId,
        ingressNodeId,
        selectedIndex,
        committedResultSha256: resultSha256,
        historyUrls,
        eventUrls,
        ingressHistoryUrl: null,
      },
    };
  }

  const fingerprints = await page.evaluate(
    async ({ sourceUrl, referenceUrl, candidateUrl }) => {
      const decode = async (url: string) => {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`${url} returned ${response.status}`);
        const bitmap = await createImageBitmap(await response.blob());
        const sourceCanvas = new OffscreenCanvas(bitmap.width, bitmap.height);
        const sourceContext = sourceCanvas.getContext('2d', {
          willReadFrequently: true,
        });
        if (!sourceContext) throw new Error('2D canvas context is unavailable');
        sourceContext.drawImage(bitmap, 0, 0);
        const sourcePixels = sourceContext.getImageData(
          0,
          0,
          bitmap.width,
          bitmap.height,
        ).data;
        const digest = await crypto.subtle.digest('SHA-256', sourcePixels);
        const sha256 = [...new Uint8Array(digest)]
          .map((value) => value.toString(16).padStart(2, '0'))
          .join('');
        const normalizedCanvas = new OffscreenCanvas(32, 32);
        const normalizedContext = normalizedCanvas.getContext('2d', {
          willReadFrequently: true,
        });
        if (!normalizedContext) throw new Error('normalized canvas is unavailable');
        normalizedContext.imageSmoothingEnabled = true;
        normalizedContext.imageSmoothingQuality = 'high';
        normalizedContext.drawImage(bitmap, 0, 0, 32, 32);
        const normalized = Array.from(
          normalizedContext.getImageData(0, 0, 32, 32).data,
        );
        bitmap.close();
        return {
          url,
          width: sourceCanvas.width,
          height: sourceCanvas.height,
          sha256,
          normalized,
        };
      };
      const [source, reference, candidate] = await Promise.all([
        decode(sourceUrl),
        decode(referenceUrl),
        decode(candidateUrl),
      ]);
      const difference = (left: number[], right: number[]) => {
        let total = 0;
        for (let index = 0; index < left.length; index += 1) {
          total += Math.abs(left[index] - right[index]);
        }
        return total / left.length;
      };
      return {
        source,
        reference,
        candidate: {
          url: candidate.url,
          width: candidate.width,
          height: candidate.height,
          sha256: candidate.sha256,
          committedMeanAbsoluteDifference: difference(
            reference.normalized,
            candidate.normalized,
          ),
          sourceMeanAbsoluteDifference: difference(
            source.normalized,
            candidate.normalized,
          ),
          committedAspectRatioDifference: Math.abs(
            reference.width / reference.height - candidate.width / candidate.height,
          ),
        },
        sourceToCommittedMeanAbsoluteDifference: difference(
          source.normalized,
          reference.normalized,
        ),
      };
    },
    { sourceUrl, referenceUrl: resultUrl, candidateUrl: ingressHistoryUrl },
  );
  if (fingerprints.source.sha256 !== sourceSha256) {
    errors.push('original editor source artifact changed after its inpaint pixel proof');
  }
  if (fingerprints.reference.sha256 !== resultSha256) {
    errors.push('committed edit artifact changed after its inpaint pixel proof');
  }
  const candidate = fingerprints.candidate;
  const contentMatch =
    candidate.sha256 === resultSha256 ||
    (candidate.sha256 !== sourceSha256 &&
      candidate.committedAspectRatioDifference < 0.001 &&
      candidate.committedMeanAbsoluteDifference <= 6 &&
      candidate.committedMeanAbsoluteDifference + 0.05 <
        candidate.sourceMeanAbsoluteDifference);
  if (!contentMatch) {
    errors.push(
      `node ${ingressNodeId} exact lfImage cell at index ${selectedIndex} does not carry the committed edit rather than the unchanged source`,
    );
  }
  if (candidate.sha256 === sourceSha256) {
    errors.push(
      `node ${ingressNodeId} exact lfImage cell at index ${selectedIndex} still carries the pre-edit source`,
    );
  }
  if (fingerprints.sourceToCommittedMeanAbsoluteDifference <= 0.05) {
    errors.push('source and committed edit are not materially distinct in normalized comparison');
  }
  return {
    errors,
    evidence: {
      outputNodeId,
      ingressNodeId,
      committedResultSha256: resultSha256,
      decodedCommittedResultSha256: fingerprints.reference.sha256,
      historyArtifactCount: historyUrls.length,
      ingressHistoryUrl,
      selectedIndex,
      executedEventArtifactCount: eventUrls.length,
      historyEventMatchCount: historyEventMatches.length,
      contentMatch,
      candidate,
      sourceToCommittedMeanAbsoluteDifference:
        fingerprints.sourceToCommittedMeanAbsoluteDifference,
    },
  };
};

const executeCase = async (
  manifestCase: ManifestCase,
  page: Page,
  prompt: JsonRecord,
  objectInfo: JsonRecord,
  options: CliOptions,
): Promise<CaseResult> => {
  const started = performance.now();
  const blockers: string[] = [];
  const optionRecord = options as unknown as Record<string, unknown>;
  for (const flag of requiredFlagsForResourceClass(manifestCase.resourceClass)) {
    if (optionRecord[flag] !== true) blockers.push(`requires --${flag.replace(/[A-Z]/g, (m) => `-${m.toLowerCase()}`)}`);
  }
  blockers.push(...validateCombos(prompt, objectInfo, manifestCase.targets));
  if (manifestCase.resourceClass === 'local-llm-gpu-write' && options.allowLocalLlm) {
    blockers.push(...(await localModelBlockers(options)));
  }
  if (blockers.length) {
    return {
      id: manifestCase.id,
      title: manifestCase.title,
      outcome: 'BLOCKED',
      durationSeconds: (performance.now() - started) / 1000,
      message: blockers.join('; '),
      blockers,
    };
  }

  const queueBefore = await queueIsEmpty(options.comfyUrl);
  if (queueBefore.parsed.malformed.length || queueBefore.ids.size > 0) {
    const queueBlockers = [
      ...queueBefore.parsed.malformed,
      ...(queueBefore.ids.size ? [`queue is not empty: ${[...queueBefore.ids].join(', ')}`] : []),
    ];
    return {
      id: manifestCase.id,
      title: manifestCase.title,
      outcome: 'BLOCKED',
      durationSeconds: (performance.now() - started) / 1000,
      message: queueBlockers.join('; '),
      blockers: queueBlockers,
    };
  }

  const historyBefore = await historyPromptIds(options.comfyUrl);
  const recorderToken = await installExecutionRecorder(page);
  const requestedPromptId = randomUUID();
  let queued: Awaited<ReturnType<typeof queueCaseThroughFrontend>> | null = null;
  let submissionError: string | null = null;
  try {
    queued = await queueCaseThroughFrontend(
      page,
      manifestCase.targets,
      requestedPromptId,
    );
  } catch (error) {
    submissionError = String(error);
  }
  const promptId = queued?.captured?.prompt_id;
  if (!queued?.accepted || typeof promptId !== 'string' || !promptId) {
    const capturedPromptId =
      typeof promptId === 'string' && promptId
        ? promptId
        : typeof queued?.captured?.response?.prompt_id === 'string'
          ? queued.captured.response.prompt_id
          : undefined;
    const exactExpectedPromptIds = [requestedPromptId, capturedPromptId].filter(
      (id): id is string => typeof id === 'string' && id.length > 0,
    );
    const submissionDelta = await observeSubmissionDelta(
      page,
      options.comfyUrl,
      recorderToken,
      historyBefore,
      exactExpectedPromptIds,
    );
    const recoveredPromptId = selectOwnedSubmissionPromptId(
      capturedPromptId,
      submissionDelta.boundPromptIds,
    );
    if (recoveredPromptId) {
      const recoveredTerminal = await waitForTerminal(
        options.comfyUrl,
        recoveredPromptId,
        0,
      );
      const recoveredTrace = await stopExecutionRecorder(
        page,
        recorderToken,
        recoveredPromptId,
      );
      return {
        id: manifestCase.id,
        title: manifestCase.title,
        outcome: 'ABORTED',
        durationSeconds: (performance.now() - started) / 1000,
        promptId: recoveredPromptId,
        terminal: {
          classification: recoveredTerminal.classification,
          cancellation: recoveredTerminal.cancellation ?? null,
          exactPromptCleanupProven: recoveredTerminal.cleanupProven ?? null,
          postCancellationDisposition:
            recoveredTerminal.postCancellationDisposition ?? null,
        },
        executionTrace: recoveredTrace,
        foreignWorkDetected:
          submissionDelta.errors.length > 0 ||
          submissionDelta.candidateIds.some((id) => id !== recoveredPromptId),
        message: `frontend submission was uncertain; recovered exact prompt ${recoveredPromptId} and forced truthful terminal cleanup (${submissionError ?? JSON.stringify(queued?.captured)})`,
      };
    }
    const uncertainTrace = await stopExecutionRecorder(page, recorderToken, '');
    const noNewWorkProven =
      submissionDelta.candidateIds.length === 0 &&
      submissionDelta.errors.length === 0;
    return {
      id: manifestCase.id,
      title: manifestCase.title,
      outcome: noNewWorkProven ? 'FAIL' : 'ABORTED',
      durationSeconds: (performance.now() - started) / 1000,
      executionTrace: uncertainTrace,
      foreignWorkDetected: !noNewWorkProven,
      message: noNewWorkProven
        ? `frontend submission was rejected and no new Core work appeared: ${submissionError ?? JSON.stringify(queued?.captured)}`
        : `frontend submission ownership is ambiguous; no global cancellation was attempted: ${JSON.stringify({ submissionError, captured: queued?.captured, submissionDelta })}`,
    };
  }

  const submittedPrompt = queued.submittedPrompt as JsonRecord | null;
  const submittedTargets = normalizeExecutionTargetIds(
    queued.submittedPartialExecutionTargets,
  );
  const expectedTargets = normalizeExecutionTargetIds(manifestCase.targets);
  const promptEvidence: JsonRecord = {
    source: 'frontend-api-queuePrompt-request',
    requestedPromptId: queued.requestedPromptId,
    promptIdInjected: queued.promptIdInjected === true,
    responsePromptIdMatchesRequested:
      queued.promptIdInjected === true && queued.requestedPromptId === promptId,
    submittedPromptSha256: submittedPrompt
      ? sha256(JSON.stringify(submittedPrompt))
      : null,
    submittedPromptNodeCount: submittedPrompt
      ? Object.keys(submittedPrompt).length
      : null,
    submittedPartialExecutionTargets: submittedTargets,
    expectedPartialExecutionTargets: expectedTargets,
    submittedTargetsMatchManifest:
      submittedTargets !== null &&
      expectedTargets !== null &&
      JSON.stringify(submittedTargets) === JSON.stringify(expectedTargets),
  };

  let interaction: JsonRecord | undefined;
  let interactionPromise: Promise<JsonRecord> | undefined;
  if (manifestCase.interaction === 'inpaint-image-editor') {
    if (typeof manifestCase.interactionNodeId !== 'number') {
      interactionPromise = Promise.reject(
        new Error('inpaint-image-editor requires interactionNodeId'),
      );
    } else {
      interactionPromise = inpaintImageEditor(
        page,
        manifestCase.interactionNodeId,
        manifestCase.timeoutSeconds * 1000,
      ).catch((error) => ({ error: String(error) }));
    }
  }
  let terminal: Awaited<ReturnType<typeof waitForTerminal>>;
  let executionTrace: ExecutionTrace;
  try {
    terminal = await waitForTerminal(
      options.comfyUrl,
      promptId,
      manifestCase.timeoutSeconds,
    );
    if (interactionPromise) {
      try {
        interaction = await interactionPromise;
      } catch (error) {
        interaction = { error: String(error) };
      }
    }
  } finally {
    executionTrace = await stopExecutionRecorder(page, recorderToken, promptId);
  }
  let historyAfter = new Set<string>();
  let historyAfterError: string | null = null;
  try {
    historyAfter = await historyPromptIds(options.comfyUrl);
  } catch (error) {
    historyAfterError = String(error);
  }
  const foreignHistoryIds = [...historyAfter]
    .filter((id) => !historyBefore.has(id) && id !== promptId)
    .sort();
  const foreignWorkDetected =
    Boolean(terminal.foreignIds?.length) ||
    foreignHistoryIds.length > 0 ||
    historyAfterError !== null;
  if (terminal.entry) {
    const exactHistoryPrompt = extractHistoryPrompt(terminal.entry, promptId);
    const exactHistoryTargets = extractHistoryExecutionTargets(
      terminal.entry,
      promptId,
    );
    promptEvidence.historyPromptSha256 = exactHistoryPrompt
      ? sha256(JSON.stringify(exactHistoryPrompt))
      : null;
    promptEvidence.historyPromptNodeCount = exactHistoryPrompt
      ? Object.keys(exactHistoryPrompt).length
      : null;
    promptEvidence.submissionMatchesHistory =
      promptEvidence.submittedPromptSha256 !== null &&
      promptEvidence.submittedPromptSha256 === promptEvidence.historyPromptSha256;
    promptEvidence.historyExecutionTargets = exactHistoryTargets;
    promptEvidence.submittedTargetsMatchHistory =
      submittedTargets !== null &&
      exactHistoryTargets !== null &&
      JSON.stringify(submittedTargets) === JSON.stringify(exactHistoryTargets);
  }
  promptEvidence.foreignHistoryDetection = historyAfterError
    ? { available: false, error: historyAfterError }
    : { available: true, foreignPromptIds: foreignHistoryIds };
  let editingSessionCleanup: JsonRecord | null = null;
  if (manifestCase.interaction === 'inpaint-image-editor' && interaction) {
    editingSessionCleanup = await inspectEditingSessionCleanup(page, interaction);
    if (editingSessionCleanup) {
      interaction = { ...interaction, sessionCleanup: editingSessionCleanup };
    }
  }
  const durationSeconds = (performance.now() - started) / 1000;
  const terminalEvidence = {
    classification: terminal.classification,
    cancellation: terminal.cancellation ?? null,
    exactPromptCleanupProven: terminal.cleanupProven ?? null,
    postCancellationDisposition: terminal.postCancellationDisposition ?? null,
    queueDiagnostics: terminal.queueDiagnostics ?? [],
  };
  const editingSessionResidue =
    interaction?.cleanup?.state === 'residue-preserved' ||
    (editingSessionCleanup !== null && editingSessionCleanup.cleanupProven !== true);
  if (terminal.classification !== 'success' || !terminal.entry) {
    const aborted = terminal.classification === 'orphaned' || editingSessionResidue;
    return {
      id: manifestCase.id,
      title: manifestCase.title,
      outcome: aborted ? 'ABORTED' : 'FAIL',
      durationSeconds,
      promptId,
      interaction,
      terminal: terminalEvidence,
      promptEvidence,
      executionTrace,
      foreignWorkDetected,
      message: editingSessionResidue
        ? `terminal state: ${terminal.classification}; exact editing-session cleanup is unproven and residue was preserved`
        : `terminal state: ${terminal.classification}`,
    };
  }
  if (editingSessionResidue) {
    return {
      id: manifestCase.id,
      title: manifestCase.title,
      outcome: 'ABORTED',
      durationSeconds,
      promptId,
      interaction,
      terminal: terminalEvidence,
      promptEvidence,
      executionTrace,
      foreignWorkDetected,
      message: 'Core reported success, but exact editing-session cleanup is unproven and residue was preserved',
    };
  }
  const assertions = validateCaseOutputs(manifestCase, terminal.entry);
  if (historyAfterError) {
    assertions.push(`post-terminal foreign-history snapshot failed: ${historyAfterError}`);
  }
  if (!submittedPrompt) {
    assertions.push('frontend submission prompt was not captured');
  }
  if (!extractHistoryPrompt(terminal.entry, promptId)) {
    assertions.push('terminal history is not bound to the exact owned prompt tuple');
  } else if (promptEvidence.submissionMatchesHistory !== true) {
    assertions.push('submitted prompt hash does not match the exact terminal-history prompt');
  }
  if (promptEvidence.submittedTargetsMatchManifest !== true) {
    assertions.push('frontend submission did not carry exactly the declared partial-execution targets');
  }
  if (promptEvidence.submittedTargetsMatchHistory !== true) {
    assertions.push(
      'submitted partial-execution targets do not match the exact terminal-history outputs-to-execute tuple',
    );
  }
  if (manifestCase.execution) {
    assertions.push(
      ...validateExecutionTrace(
        manifestCase,
        executionTrace,
        typeof interaction?.resumedAt === 'number' ? interaction.resumedAt : undefined,
      ),
    );
  }
  assertions.push(
    ...(await validatePreviewAssets(
      options.comfyUrl,
      manifestCase,
      terminal.entry,
    )),
  );
  const liveWidgets = await readLiveWidgets(page, manifestCase.targets);
  for (const [nodeId, expectation] of Object.entries(manifestCase.expect ?? {}) as Array<
    [
      string,
      {
        receiptSchema?: string;
        minimumPreviewCount?: number;
        previewStorageType?: 'input' | 'output' | 'temp';
      },
    ]
  >) {
    const live = liveWidgets.find((item) => String(item.nodeId) === nodeId);
    if (!live?.found || !live.hasElement) {
      assertions.push(`node ${nodeId} live ui_widget is not hydrated`);
    } else if (
      expectation.minimumPreviewCount !== undefined &&
      live.previewCount < expectation.minimumPreviewCount
    ) {
      assertions.push(
        `node ${nodeId} live widget has ${live.previewCount} previews; expected at least ${expectation.minimumPreviewCount}`,
      );
    }
  }
  if (interaction?.error) assertions.push(`interaction failed: ${interaction.error}`);
  if (terminal.foreignIds?.length) {
    assertions.push(`foreign queue work appeared during the case: ${terminal.foreignIds.join(', ')}`);
  }
  if (foreignHistoryIds.length) {
    assertions.push(
      `foreign prompt history appeared during the case: ${foreignHistoryIds.join(', ')}`,
    );
  }
  const downstream = await validateCommittedEditPropagation(
    page,
    manifestCase,
    terminal.entry,
    interaction,
    executionTrace,
  );
  assertions.push(...downstream.errors);
  return {
    id: manifestCase.id,
    title: manifestCase.title,
    outcome: assertions.length ? 'FAIL' : 'PASS',
    durationSeconds,
    promptId,
    interaction,
    terminal: terminalEvidence,
    promptEvidence,
    executionTrace,
    downstreamArtifact: downstream.evidence ?? undefined,
    foreignWorkDetected:
      foreignWorkDetected,
    assertions,
    message: assertions.length ? assertions.join('; ') : 'terminal success with declared assertions',
  };
};

const main = async () => {
  let options: CliOptions;
  try {
    options = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(String(error));
    console.error(usage.trim());
    process.exitCode = 1;
    return;
  }

  await mkdir(options.outputDir, { recursive: true });
  const results: CaseResult[] = [];
  let gateScope = describeGateScope(options.mode, options.caseIds, []);
  const summary: JsonRecord = {
    schema: 'lf.titanic-e2e.v1',
    outcome: 'BLOCKED',
    requestedMode: options.mode,
    mode: gateScope.mode,
    caseIds: [...options.caseIds],
    authority: {
      allowGpu: options.allowGpu,
      allowModels: options.allowModels,
      allowWrites: options.allowWrites,
      allowUnpinnedInputs: options.allowUnpinnedInputs,
      allowLocalLlm: options.allowLocalLlm,
      allowInteraction: options.allowInteraction,
      acceptWarmCache: options.acceptWarmCache,
    },
    achievedGate: 'none',
    fullWorkflowPass: false,
    startedAt: new Date().toISOString(),
    workflow: { path: options.workflowPath },
    manifest: {
      authority: 'repository-fixed',
      path: defaultManifest,
    },
    environment: {
      comfyUrl: options.comfyUrl,
      lmStudioUrl: options.lmStudioUrl,
      browserChannel: options.browserChannel,
      headed: options.headed,
    },
    results,
  };
  let browser: Browser | undefined;
  let workflowBefore: Buffer | undefined;
  let executionProofNodesByCase = new Map<string, string[]>();
  const writeEvidence = async () => {
    const selectedExecutionProven =
      gateScope.selectedCoverageCaseIds.length > 0 &&
      gateScope.selectedCoverageCaseIds.every((caseId) => {
        const result = results.find((candidate) => candidate.id === caseId);
        const requiredNodes = executionProofNodesByCase.get(caseId) ?? [];
        const executed = new Set(result?.executionTrace?.executedNodeIds ?? []);
        return (
          result?.outcome === 'PASS' &&
          requiredNodes.length > 0 &&
          requiredNodes.every((nodeId) => executed.has(nodeId))
        );
      });
    const executionProven =
      summary.environment.coldCache === true ||
      (!gateScope.allCoverageCasesSelected && selectedExecutionProven);
    summary.executionProven = executionProven;
    summary.achievedGate = determineAchievedGate(gateScope, results, executionProven);
    summary.fullWorkflowPass =
      summary.outcome === 'PASS' &&
      summary.achievedGate === 'full-workflow-execution';
    summary.finishedAt = new Date().toISOString();
    summary.results = results;
    const summaryPath = resolve(options.outputDir, 'summary.json');
    const junitPath = resolve(options.outputDir, 'junit.xml');
    await writeFile(summaryPath, `${JSON.stringify(summary, null, 2)}\n`, 'utf8');
    await writeFile(
      junitPath,
      createJUnitXml(
        'LF Titanic E2E',
        results.map((result) => ({
          id: result.id,
          outcome: result.outcome,
          durationSeconds: result.durationSeconds,
          message: result.message,
        })),
      ),
      'utf8',
    );
    console.log(JSON.stringify({ outcome: summary.outcome, summaryPath, junitPath }, null, 2));
  };

  try {
    const [workflowBytes, manifestBytes] = await Promise.all([
      readFile(options.workflowPath),
      readFile(defaultManifest, 'utf8'),
    ]);
    workflowBefore = workflowBytes;
    const workflow = JSON.parse(workflowBytes.toString('utf8')) as JsonRecord;
    const manifest = JSON.parse(manifestBytes) as TitanicManifest;
    summary.manifest = {
      authority: 'repository-fixed',
      path: defaultManifest,
      sha256: sha256(manifestBytes),
      sizeBytes: Buffer.byteLength(manifestBytes, 'utf8'),
      schema: manifest.schema,
    };
    executionProofNodesByCase = new Map(
      manifest.coverageCases.map((manifestCase) => [
        manifestCase.id,
        (manifestCase.execution?.requiredNodeIds ?? []).map(String),
      ]),
    );
    gateScope = describeGateScope(
      options.mode,
      options.caseIds,
      manifest.coverageCases.map((manifestCase) => manifestCase.id),
    );
    summary.requestedMode = gateScope.requestedMode;
    summary.mode = gateScope.mode;
    summary.caseIds = gateScope.caseIds;
    summary.selection = {
      selectedCoverageCaseIds: gateScope.selectedCoverageCaseIds,
      allCoverageCasesSelected: gateScope.allCoverageCasesSelected,
      totalCoverageCaseCount: manifest.coverageCases.length,
    };
    const workflowInfo = await stat(options.workflowPath);
    summary.workflow = {
      authority:
        resolve(options.workflowPath) === defaultWorkflow
          ? 'repository-canonical'
          : 'hash-pinned-projection',
      path: options.workflowPath,
      sha256: sha256(workflowBytes),
      sizeBytes: workflowBytes.length,
      mtime: workflowInfo.mtime.toISOString(),
      id: workflow.id,
      nodeCount: workflow.nodes?.length,
      linkCount: workflow.links?.length,
    };

    const inventoryErrors: string[] = [];
    if (manifest.schema !== 'lf.titanic-e2e.manifest.v1') inventoryErrors.push('manifest schema mismatch');
    for (const manifestCase of [...manifest.smokeCases, ...manifest.coverageCases]) {
      try {
        requiredFlagsForResourceClass(manifestCase.resourceClass);
      } catch (error) {
        inventoryErrors.push(`${manifestCase.id}: ${String(error)}`);
      }
    }
    if (workflow.id !== manifest.workflow.id) inventoryErrors.push(`workflow id ${workflow.id} does not match manifest`);
    if (sha256(workflowBytes) !== String(manifest.workflow.expectedSha256).toLowerCase()) {
      inventoryErrors.push('workflow SHA-256 drift');
    }
    if (workflow.nodes?.length !== manifest.workflow.expectedNodeCount) inventoryErrors.push('workflow node count drift');
    if (workflow.links?.length !== manifest.workflow.expectedLinkCount) inventoryErrors.push('workflow link count drift');
    for (const disabled of manifest.disabledNodes) {
      const node = workflow.nodes?.find((candidate: any) => Number(candidate.id) === disabled.id);
      if (!node || Number(node.mode) !== 2 || node.type !== disabled.type) {
        inventoryErrors.push(`disabled-policy node ${disabled.id} drifted`);
      }
    }
    for (const dormantId of manifest.dormantNodeIds) {
      const node = workflow.nodes?.find((candidate: any) => Number(candidate.id) === dormantId);
      if (!node || Number(node.mode ?? 0) !== 0) inventoryErrors.push(`dormant node ${dormantId} drifted`);
    }
    results.push({
      id: 'inventory',
      title: 'Static workflow identity and policy inventory',
      outcome: inventoryErrors.length ? 'FAIL' : 'PASS',
      durationSeconds: 0,
      message: inventoryErrors.length ? inventoryErrors.join('; ') : 'workflow identity and policy nodes match',
      assertions: inventoryErrors,
    });
    if (inventoryErrors.length) throw new Error(`WORKFLOW_DRIFT: ${inventoryErrors.join('; ')}`);

    let systemStats: any;
    let objectInfo: any;
    try {
      [systemStats, objectInfo] = await Promise.all([
        jsonFetch(`${options.comfyUrl}/system_stats`),
        jsonFetch(`${options.comfyUrl}/object_info`, {}, 60_000),
      ]);
    } catch (error) {
      results.push({
        id: 'comfy-service',
        title: 'Comfy service availability',
        outcome: 'BLOCKED',
        durationSeconds: 0,
        message: String(error),
      });
      throw error;
    }
    const argv = findArgv(systemStats);
    summary.environment.comfyArgv = argv;
    summary.environment.coldCache = Boolean(argv?.includes('--cache-none'));

    browser = await launchBrowser(options);
    const context = await browser.newContext({ viewport: { width: 1600, height: 1000 } });
    const page = await context.newPage();
    const hydrated = await hydrateWorkflow(page, options.comfyUrl, workflow, objectInfo);
    const prompt = hydrated.promptBundle.output as JsonRecord;
    const promptHash = sha256(JSON.stringify(prompt));
    const widgetFailures = hydrated.widgetChecks.filter(
      (widget: any) => !widget.found || !widget.hasElement || !widget.connected,
    );
    const coverageErrors = validateCoverage(manifest, hydrated.activeOutputIds);
    const mode2Expected = manifest.disabledNodes.map((node) => node.id).sort((a, b) => a - b);
    if (JSON.stringify(hydrated.mode2NodeIds) !== JSON.stringify(mode2Expected)) {
      coverageErrors.push(
        `mode-2 set drifted: ${hydrated.mode2NodeIds.join(', ')} (expected ${mode2Expected.join(', ')})`,
      );
    }
    const hydrationErrors = [
      ...(hydrated.loadedNodeCount === manifest.workflow.expectedNodeCount
        ? []
        : [`loaded ${hydrated.loadedNodeCount} nodes`]),
      ...(hydrated.loadedLinkCount === manifest.workflow.expectedLinkCount
        ? []
        : [`loaded ${hydrated.loadedLinkCount} links`]),
      ...widgetFailures.map(
        (widget: any) =>
          `node ${widget.nodeId} ${widget.name} widget hydration: found=${widget.found}, element=${widget.hasElement}, connected=${widget.connected}`,
      ),
      ...hydrated.pageErrors.map((error: string) => `page error: ${error}`),
      ...coverageErrors,
    ];
    summary.hydration = {
      loadedNodeCount: hydrated.loadedNodeCount,
      loadedLinkCount: hydrated.loadedLinkCount,
      promptNodeCount: Object.keys(prompt).length,
      compiledPromptSha256: promptHash,
      compiledPromptAuthority: 'hydration-only',
      activeOutputCount: hydrated.activeOutputIds.length,
      activeOutputIds: hydrated.activeOutputIds,
      customWidgetCount: hydrated.widgetChecks.length,
      widgetFailures,
      widgetDebug: hydrated.widgetDebug,
      pageErrors: hydrated.pageErrors,
      consoleErrors: hydrated.consoleErrors,
      coverageErrors,
      clientId: hydrated.clientId,
    };
    results.push({
      id: 'hydration',
      title: 'Real frontend hydration and API prompt compilation',
      outcome: hydrationErrors.length ? 'FAIL' : 'PASS',
      durationSeconds: 0,
      message: hydrationErrors.length ? hydrationErrors.join('; ') : 'frontend hydration, widgets, and coverage manifest match',
      assertions: hydrationErrors,
    });
    if (hydrationErrors.length) throw new Error(`HYDRATION_FAILED: ${hydrationErrors.join('; ')}`);

    if (options.mode !== 'hydrate') {
      if (options.mode === 'full' && !options.acceptWarmCache && !argv?.includes('--cache-none')) {
        results.push({
          id: 'cold-cache',
          title: 'Cold execution boundary',
          outcome: 'BLOCKED',
          durationSeconds: 0,
          message: 'full execution requires Comfy --cache-none or explicit --accept-warm-cache',
        });
      } else {
        const cases =
          options.mode === 'smoke'
            ? manifest.smokeCases
            : manifest.coverageCases.filter(
                (manifestCase) =>
                  options.caseIds.length === 0 || options.caseIds.includes(manifestCase.id),
              );
        if (options.mode === 'full' && options.caseIds.some((id) => !manifest.coverageCases.some((item) => item.id === id))) {
          throw new Error('one or more --case values are absent from the manifest');
        }
        for (const manifestCase of cases) {
          const result = await executeCase(manifestCase, page, prompt, objectInfo, options);
          results.push(result);
          if (result.outcome === 'ABORTED') break;
          if (result.foreignWorkDetected) break;
        }
      }
      if (options.mode === 'full' && options.caseIds.length === 0) {
        for (const disabled of manifest.disabledNodes) {
          results.push({
            id: `disabled.${disabled.id}`,
            title: disabled.type,
            outcome: 'SKIPPED',
            durationSeconds: 0,
            message: disabled.reason,
          });
        }
      }
    }

    const workflowAfter = await readFile(options.workflowPath);
    summary.workflow.unchanged = workflowBefore.equals(workflowAfter);
    summary.workflow.sha256After = sha256(workflowAfter);
    if (!workflowBefore.equals(workflowAfter)) {
      results.push({
        id: 'workflow-immutability',
        title: 'Canonical workflow remains unchanged',
        outcome: 'FAIL',
        durationSeconds: 0,
        message: 'E2E.json changed on disk during the gate',
      });
    } else {
      results.push({
        id: 'workflow-immutability',
        title: 'Canonical workflow remains unchanged',
        outcome: 'PASS',
        durationSeconds: 0,
        message: 'workflow bytes are unchanged',
      });
    }

    const meaningful = results.filter((result) => result.outcome !== 'SKIPPED');
    summary.outcome = meaningful.some((result) => result.outcome === 'ABORTED')
      ? 'ABORTED'
      : meaningful.some((result) => result.outcome === 'FAIL')
        ? 'FAIL'
        : meaningful.some((result) => result.outcome === 'BLOCKED')
          ? 'BLOCKED'
          : 'PASS';
  } catch (error) {
    summary.error = String(error);
    if (results.some((result) => result.outcome === 'ABORTED')) {
      summary.outcome = 'ABORTED';
    } else if (!results.some((result) => result.outcome === 'FAIL')) {
      summary.outcome = 'BLOCKED';
    } else {
      summary.outcome = 'FAIL';
    }
  } finally {
    await browser?.close().catch(() => {});
    await writeEvidence();
  }

  process.exitCode =
    summary.outcome === 'PASS'
      ? 0
      : summary.outcome === 'BLOCKED'
        ? 2
        : summary.outcome === 'ABORTED'
          ? 130
          : 1;
};

await main();
