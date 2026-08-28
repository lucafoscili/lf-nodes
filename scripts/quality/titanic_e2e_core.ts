export type GateOutcome = 'PASS' | 'FAIL' | 'BLOCKED' | 'SKIPPED' | 'ABORTED';
export type HistoryClassification = 'success' | 'failure' | 'incomplete' | 'missing';
export type PostCancellationDisposition =
  | 'late-success'
  | 'late-failure'
  | 'cancelled'
  | 'wait';

export interface QueueSnapshot {
  running: Set<string>;
  pending: Set<string>;
  malformed: string[];
}

export interface ManifestCase {
  id: string;
  title: string;
  resourceClass: string;
  targets: number[];
  timeoutSeconds: number;
  interaction?: string;
  interactionNodeId?: number;
  execution?: {
    requiredNodeIds?: number[];
    forbiddenCachedNodeIds?: number[];
    requiredAfterInteractionNodeIds?: number[];
    committedEditIngressNodeId?: number;
    committedEditOutputNodeId?: number;
  };
  expect?: Record<
    string,
    {
      receiptSchema?: string;
      minimumPreviewCount?: number;
      previewStorageType?: 'input' | 'output' | 'temp';
      forbidTopLevelJsonKeys?: string[];
      minimumStringLength?: number;
      forbiddenStringPrefixes?: string[];
    }
  >;
}

export interface ExecutionTrace {
  promptId: string;
  started: boolean;
  terminalEvent: string | null;
  executedNodeIds: string[];
  uiExecutedNodeIds: string[];
  cachedNodeIds: string[];
  executingEvents: Array<{ nodeId: string; timestampMs: number }>;
  executedPreviewUrlsByNode: Record<string, string[]>;
}

export interface EditorClientBindingEvidence {
  callerClientId: unknown;
  contextId: unknown;
  pendingOwnerClientId: unknown;
  recoveredOwnerClientId: unknown;
  completedOwnerClientId: unknown;
  processCallerClientId: unknown;
  processContextId: unknown;
  updateCallerClientId: unknown;
  updateContextId: unknown;
  completedContextId: unknown;
  wrongOwnerRecoveryData: unknown;
}

export type TitanicRequestedMode = 'hydrate' | 'smoke' | 'full';
export type TitanicEffectiveMode = TitanicRequestedMode | 'targeted';
export type TitanicAchievedGate =
  | 'none'
  | 'inventory'
  | 'hydration'
  | 'targeted-branch-coverage'
  | 'targeted-branch-execution'
  | 'full-workflow-coverage'
  | 'full-workflow-execution';

export interface TitanicGateScope {
  requestedMode: TitanicRequestedMode;
  mode: TitanicEffectiveMode;
  caseIds: string[];
  selectedCoverageCaseIds: string[];
  allCoverageCasesSelected: boolean;
}

export interface TitanicManifest {
  schema: string;
  workflow: {
    id: string;
    expectedSha256: string;
    expectedNodeCount: number;
    expectedLinkCount: number;
  };
  smokeCases: ManifestCase[];
  coverageCases: ManifestCase[];
  dormantNodeIds: number[];
  disabledNodes: Array<{ id: number; type: string; reason: string }>;
}

const asRecord = (value: unknown): Record<string, unknown> | null =>
  value !== null && typeof value === 'object' && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : null;

export const comfyArtifactKey = (value: unknown): string => {
  const raw = String(value ?? '');
  try {
    const url = new URL(raw, 'http://127.0.0.1');
    if (url.pathname !== '/view') return `${url.pathname}${url.search}`;
    const params = new URLSearchParams();
    for (const key of ['filename', 'type', 'subfolder']) {
      params.set(key, url.searchParams.get(key) ?? '');
    }
    return `${url.pathname}?${params.toString()}`;
  } catch {
    return raw;
  }
};

export const validateEditorClientBinding = (
  evidence: EditorClientBindingEvidence,
): string[] => {
  const callerClientId =
    typeof evidence.callerClientId === 'string'
      ? evidence.callerClientId.trim()
      : '';
  if (!callerClientId) {
    return ['image editor has no connected Comfy caller client id'];
  }
  const contextId =
    typeof evidence.contextId === 'string' ? evidence.contextId.trim() : '';
  if (!contextId) {
    return ['image editor has no exact editing context id'];
  }

  const errors: string[] = [];
  for (const [label, value] of [
    ['pending dataset owner', evidence.pendingOwnerClientId],
    ['recovered dataset owner', evidence.recoveredOwnerClientId],
    ['completed dataset owner', evidence.completedOwnerClientId],
    ['process-image caller', evidence.processCallerClientId],
    ['update-json caller', evidence.updateCallerClientId],
  ] as const) {
    if (value !== callerClientId) {
      errors.push(
        `${label} ${JSON.stringify(value)} does not match connected client ${JSON.stringify(callerClientId)}`,
      );
    }
  }
  if (evidence.wrongOwnerRecoveryData !== null) {
    errors.push('wrong-owner edit-dataset recovery returned session data');
  }
  for (const [label, value] of [
    ['process-image context', evidence.processContextId],
    ['update-json context', evidence.updateContextId],
    ['completed dataset context', evidence.completedContextId],
  ] as const) {
    if (value !== contextId) {
      errors.push(
        `${label} ${JSON.stringify(value)} does not match exact context ${JSON.stringify(contextId)}`,
      );
    }
  }
  return errors;
};

export const executionEventNodeId = (
  eventType: string,
  detail: unknown,
): string | null => {
  if (
    eventType === 'executing' &&
    (typeof detail === 'string' || typeof detail === 'number')
  ) {
    return String(detail);
  }
  const record = asRecord(detail);
  const node = record?.node ?? record?.display_node;
  return typeof node === 'string' || typeof node === 'number'
    ? String(node)
    : null;
};

export const describeGateScope = (
  requestedMode: TitanicRequestedMode,
  caseIds: string[],
  coverageCaseIds: string[],
): TitanicGateScope => {
  const selectedCoverageCaseIds =
    requestedMode === 'full'
      ? caseIds.length
        ? coverageCaseIds.filter((id) => caseIds.includes(id))
        : [...coverageCaseIds]
      : [];
  const allCoverageCasesSelected =
    requestedMode === 'full' &&
    caseIds.length === 0 &&
    selectedCoverageCaseIds.length === coverageCaseIds.length;
  return {
    requestedMode,
    mode: requestedMode === 'full' && caseIds.length > 0 ? 'targeted' : requestedMode,
    caseIds: [...caseIds],
    selectedCoverageCaseIds,
    allCoverageCasesSelected,
  };
};

export const determineAchievedGate = (
  scope: TitanicGateScope,
  results: Array<{ id: string; outcome: GateOutcome }>,
  executionProven = false,
): TitanicAchievedGate => {
  const byId = new Map(results.map((result) => [result.id, result.outcome]));
  if (byId.get('inventory') !== 'PASS') return 'none';
  if (byId.get('hydration') !== 'PASS') return 'inventory';

  const selectedCaseIds =
    scope.requestedMode === 'smoke'
      ? results
          .filter(
            (result) =>
              !['inventory', 'hydration', 'workflow-immutability', 'cold-cache'].includes(
                result.id,
              ) &&
              !result.id.startsWith('disabled.'),
          )
          .map((result) => result.id)
      : scope.selectedCoverageCaseIds;
  if (!selectedCaseIds.length) return 'hydration';
  if (!selectedCaseIds.every((id) => byId.get(id) === 'PASS')) return 'hydration';
  if (byId.get('workflow-immutability') !== 'PASS') return 'hydration';
  if (scope.allCoverageCasesSelected) {
    return executionProven ? 'full-workflow-execution' : 'full-workflow-coverage';
  }
  return executionProven ? 'targeted-branch-execution' : 'targeted-branch-coverage';
};

export const extractHistoryPrompt = (
  historyEntry: Record<string, unknown>,
  promptId: string,
): Record<string, unknown> | null => {
  const promptTuple = historyEntry.prompt;
  if (!Array.isArray(promptTuple) || promptTuple[1] !== promptId) return null;
  return asRecord(promptTuple[2]);
};

export const normalizeExecutionTargetIds = (value: unknown): string[] | null => {
  if (!Array.isArray(value)) return null;
  const normalized: string[] = [];
  const seen = new Set<string>();
  for (const candidate of value) {
    if (typeof candidate !== 'string' && typeof candidate !== 'number') return null;
    const id = String(candidate);
    if (!id || seen.has(id)) return null;
    seen.add(id);
    normalized.push(id);
  }
  return normalized.sort((left, right) => left.localeCompare(right, undefined, { numeric: true }));
};

export const selectOwnedSubmissionPromptId = (
  capturedPromptId: unknown,
  contentBoundPromptIds: string[],
): string | null => {
  if (typeof capturedPromptId === 'string' && capturedPromptId.length > 0) {
    return capturedPromptId;
  }
  return contentBoundPromptIds.length === 1 ? contentBoundPromptIds[0] : null;
};

export const extractHistoryExecutionTargets = (
  historyEntry: Record<string, unknown>,
  promptId: string,
): string[] | null => {
  const promptTuple = historyEntry.prompt;
  if (!Array.isArray(promptTuple) || promptTuple[1] !== promptId) return null;
  return normalizeExecutionTargetIds(promptTuple[4]);
};

export const extractDatasetCellPreviewUrl = (
  nodeOutput: unknown,
  rowIndex: number,
  cellId: string,
): string | null => {
  const output = asRecord(nodeOutput);
  const lfOutput = output?.lf_output;
  if (!Array.isArray(lfOutput) || lfOutput.length !== 1) return null;
  const payload = asRecord(lfOutput[0]);
  const dataset = asRecord(payload?.dataset);
  const nodes = dataset?.nodes;
  if (!Array.isArray(nodes) || !Number.isInteger(rowIndex) || rowIndex < 0) return null;
  const row = asRecord(nodes[rowIndex]);
  const cells = asRecord(row?.cells);
  const cell = asRecord(cells?.[cellId]);
  for (const key of ['lfValue', 'value']) {
    const candidate = cell?.[key];
    if (typeof candidate === 'string' && candidate.startsWith('/view?')) return candidate;
  }
  return null;
};

export const validateExecutionTrace = (
  manifestCase: ManifestCase,
  trace: ExecutionTrace,
  interactionResumedAt?: number,
): string[] => {
  const errors: string[] = [];
  const executed = new Set(trace.executedNodeIds);
  const cached = new Set(trace.cachedNodeIds);
  for (const nodeId of manifestCase.execution?.requiredNodeIds ?? []) {
    const id = String(nodeId);
    if (!executed.has(id)) {
      errors.push(`node ${id} was not observed executing for prompt ${trace.promptId}`);
    }
  }
  for (const nodeId of manifestCase.execution?.forbiddenCachedNodeIds ?? []) {
    const id = String(nodeId);
    if (cached.has(id)) {
      errors.push(`node ${id} was served from cache for prompt ${trace.promptId}`);
    }
  }
  if (
    (manifestCase.execution?.requiredAfterInteractionNodeIds?.length ?? 0) > 0 &&
    (!Number.isFinite(interactionResumedAt) || Number(interactionResumedAt) <= 0)
  ) {
    errors.push('interaction resume timestamp is absent from execution evidence');
  } else {
    for (const nodeId of manifestCase.execution?.requiredAfterInteractionNodeIds ?? []) {
      const event = trace.executingEvents.find(
        (candidate) =>
          candidate.nodeId === String(nodeId) &&
          candidate.timestampMs >= Number(interactionResumedAt),
      );
      if (!event) {
        errors.push(`node ${nodeId} was not observed executing after interaction resume`);
      }
    }
  }
  if (!trace.started) {
    errors.push(`execution_start was not observed for prompt ${trace.promptId}`);
  }
  if (trace.terminalEvent !== 'execution_success') {
    errors.push(
      `execution_success was not observed for prompt ${trace.promptId} (saw ${trace.terminalEvent ?? 'no terminal event'})`,
    );
  }
  return errors;
};

const promptIdFromQueueEntry = (value: unknown): string | null => {
  if (Array.isArray(value)) {
    return typeof value[1] === 'string' && value[1].length > 0
      ? value[1]
      : null;
  }
  const record = asRecord(value);
  if (!record) return null;
  for (const key of ['prompt_id', 'promptId', 'id']) {
    if (typeof record[key] === 'string' && record[key].length > 0) {
      return record[key] as string;
    }
  }
  return null;
};

export const parseQueueSnapshot = (value: unknown): QueueSnapshot => {
  const snapshot: QueueSnapshot = {
    running: new Set<string>(),
    pending: new Set<string>(),
    malformed: [],
  };
  const record = asRecord(value);
  if (!record) {
    snapshot.malformed.push('queue response is not an object');
    return snapshot;
  }

  for (const [key, target] of [
    ['queue_running', snapshot.running],
    ['queue_pending', snapshot.pending],
  ] as const) {
    const entries = record[key];
    if (!Array.isArray(entries)) {
      snapshot.malformed.push(`${key} is not an array`);
      continue;
    }
    entries.forEach((entry, index) => {
      const promptId = promptIdFromQueueEntry(entry);
      if (promptId) target.add(promptId);
      else snapshot.malformed.push(`${key}[${index}] has no prompt id`);
    });
  }
  return snapshot;
};

export const queueIds = (snapshot: QueueSnapshot): Set<string> =>
  new Set([...snapshot.running, ...snapshot.pending]);

export const unwrapHistoryEntry = (
  value: unknown,
  promptId: string,
): Record<string, unknown> | null => {
  const record = asRecord(value);
  if (!record) return null;
  const nested = asRecord(record[promptId]);
  if (nested) return nested;
  return 'status' in record || 'outputs' in record ? record : null;
};

export const classifyHistoryEntry = (
  entry: Record<string, unknown> | null,
): HistoryClassification => {
  if (!entry) return 'missing';
  const status = asRecord(entry.status);
  if (!status) return 'incomplete';
  const statusString = String(status.status_str ?? '').toLowerCase();
  const completed = status.completed === true;
  if (completed && ['success', 'completed'].includes(statusString)) {
    return 'success';
  }
  if (
    completed ||
    ['error', 'failed', 'failure', 'interrupted', 'cancelled', 'canceled'].includes(
      statusString,
    )
  ) {
    return 'failure';
  }
  return 'incomplete';
};

export const classifyPostCancellation = (
  history: HistoryClassification,
  queueHasOwnedPrompt: boolean,
  queueMalformed: boolean,
  cancellationAcknowledged: boolean,
): PostCancellationDisposition => {
  if (queueMalformed || queueHasOwnedPrompt) return 'wait';
  if (history === 'success') return 'late-success';
  if (history === 'failure') return 'late-failure';
  return cancellationAcknowledged ? 'cancelled' : 'wait';
};

export const timedOutTerminalClassification = (
  disposition: PostCancellationDisposition,
): 'timeout' | null => (disposition === 'wait' ? null : 'timeout');

export const validateCoverage = (
  manifest: TitanicManifest,
  activeOutputIds: Array<number | string>,
): string[] => {
  const errors: string[] = [];
  const active = new Set(activeOutputIds.map(String));
  const seen = new Map<string, string>();
  for (const manifestCase of manifest.coverageCases) {
    for (const target of manifestCase.targets) {
      const key = String(target);
      const previous = seen.get(key);
      if (previous) {
        errors.push(`output ${key} is assigned to both ${previous} and ${manifestCase.id}`);
      } else {
        seen.set(key, manifestCase.id);
      }
    }
  }
  for (const target of seen.keys()) {
    if (!active.has(target)) errors.push(`manifest output ${target} is not active`);
  }
  for (const target of active) {
    if (!seen.has(target)) errors.push(`active output ${target} is unclassified`);
  }
  return errors.sort();
};

const visit = (value: unknown, visitor: (record: Record<string, unknown>) => void) => {
  if (Array.isArray(value)) {
    value.forEach((item) => visit(item, visitor));
    return;
  }
  const record = asRecord(value);
  if (!record) return;
  visitor(record);
  Object.values(record).forEach((item) => visit(item, visitor));
};

export const collectReceiptSchemas = (value: unknown): Set<string> => {
  const schemas = new Set<string>();
  visit(value, (record) => {
    if (typeof record.schema === 'string' && record.schema.startsWith('lf.')) {
      schemas.add(record.schema);
    }
  });
  return schemas;
};

export const collectPreviewUrls = (value: unknown): string[] => {
  const urls = new Set<string>();
  visit(value, (record) => {
    for (const key of ['lfValue', 'value']) {
      const candidate = record[key];
      if (typeof candidate === 'string' && candidate.startsWith('/view?')) {
        urls.add(candidate);
      }
    }
  });
  return [...urls].sort();
};

export const countPreviewReferences = (value: unknown): number => {
  let count = 0;
  visit(value, (record) => {
    if (
      ['lfValue', 'value'].some(
        (key) =>
          typeof record[key] === 'string' &&
          (record[key] as string).startsWith('/view?'),
      )
    ) {
      count += 1;
    }
  });
  return count;
};

const collectNamedValues = (value: unknown, name: string): unknown[] => {
  const values: unknown[] = [];
  visit(value, (record) => {
    if (Object.prototype.hasOwnProperty.call(record, name)) {
      values.push(record[name]);
    }
  });
  return values;
};

export const validateCaseOutputs = (
  manifestCase: ManifestCase,
  historyEntry: Record<string, unknown>,
): string[] => {
  const errors: string[] = [];
  if (!manifestCase.expect) return errors;
  const outputs = asRecord(historyEntry.outputs) ?? {};
  for (const [nodeId, expectation] of Object.entries(manifestCase.expect)) {
    const output = outputs[nodeId];
    if (!output) {
      errors.push(`history has no output for node ${nodeId}`);
      continue;
    }
    if (expectation.receiptSchema) {
      const schemas = collectReceiptSchemas(output);
      if (!schemas.has(expectation.receiptSchema)) {
        errors.push(
          `node ${nodeId} is missing receipt schema ${expectation.receiptSchema}`,
        );
      }
    }
    if (expectation.minimumPreviewCount !== undefined) {
      const previewCount = countPreviewReferences(output);
      const urls = collectPreviewUrls(output);
      if (previewCount < expectation.minimumPreviewCount) {
        errors.push(
          `node ${nodeId} exposed ${previewCount} preview references; expected at least ${expectation.minimumPreviewCount}`,
        );
      }
      for (const url of urls) {
        const parsed = new URL(url, 'http://localhost');
        const expectedType = expectation.previewStorageType ?? 'input';
        if (parsed.searchParams.get('type') !== expectedType) {
          errors.push(
            `node ${nodeId} preview storage is not ${expectedType}: ${url}`,
          );
        }
      }
    }
    if (expectation.forbidTopLevelJsonKeys?.length) {
      const jsonValues = collectNamedValues(output, 'json')
        .map(asRecord)
        .filter((value): value is Record<string, unknown> => Boolean(value));
      if (!jsonValues.length) {
        errors.push(`node ${nodeId} exposed no JSON response value`);
      }
      for (const forbiddenKey of expectation.forbidTopLevelJsonKeys) {
        if (
          jsonValues.some((value) =>
            Object.prototype.hasOwnProperty.call(value, forbiddenKey),
          )
        ) {
          errors.push(
            `node ${nodeId} JSON response contains forbidden key ${JSON.stringify(forbiddenKey)}`,
          );
        }
      }
    }
    if (expectation.minimumStringLength !== undefined) {
      const strings = collectNamedValues(output, 'string').filter(
        (value): value is string => typeof value === 'string',
      );
      if (
        !strings.some(
          (value) => value.trim().length >= expectation.minimumStringLength!,
        )
      ) {
        errors.push(
          `node ${nodeId} exposed no string of at least ${expectation.minimumStringLength} characters`,
        );
      }
      for (const prefix of expectation.forbiddenStringPrefixes ?? []) {
        if (strings.some((value) => value.trimStart().startsWith(prefix))) {
          errors.push(
            `node ${nodeId} string begins with forbidden error prefix ${JSON.stringify(prefix)}`,
          );
        }
      }
    }
  }
  return errors;
};

const RESOURCE_CLASS_FLAGS: Readonly<Record<string, readonly string[]>> = Object.freeze({
  'browser-interactive-gpu-model': ['allowGpu', 'allowModels', 'allowInteraction'],
  cpu: [],
  'durable-write': ['allowWrites'],
  'filesystem-unpinned': ['allowUnpinnedInputs'],
  gpu: ['allowGpu', 'allowModels'],
  'gpu-unpinned': ['allowGpu', 'allowModels', 'allowUnpinnedInputs'],
  'local-llm-gpu-write': ['allowGpu', 'allowModels', 'allowWrites', 'allowLocalLlm'],
  'model-cpu': ['allowModels'],
  'model-gpu-write': ['allowGpu', 'allowModels', 'allowWrites'],
});

export const requiredFlagsForResourceClass = (resourceClass: string): string[] => {
  const required = RESOURCE_CLASS_FLAGS[resourceClass];
  if (!required) {
    throw new Error(`unknown Titanic resource class: ${JSON.stringify(resourceClass)}`);
  }
  return [...required];
};

export const validateLoadedModelFixture = (
  value: unknown,
  expectedModelKey: string,
  expectedInstanceId?: string,
): string[] => {
  const response = asRecord(value);
  if (!response || !Array.isArray(response.models)) {
    return ['LM Studio native model response has no models array'];
  }
  const loaded: Array<{
    modelKey: string;
    vision: boolean;
    instanceId: string;
  }> = [];
  for (const [modelIndex, candidate] of response.models.entries()) {
    const model = asRecord(candidate);
    if (!model || !Array.isArray(model.loaded_instances)) {
      return [`LM Studio model ${modelIndex} has malformed loaded_instances`];
    }
    for (const [instanceIndex, candidateInstance] of model.loaded_instances.entries()) {
      const instance = asRecord(candidateInstance);
      if (!instance || typeof instance.id !== 'string' || !instance.id) {
        return [
          `LM Studio loaded instance ${modelIndex}.${instanceIndex} has no id`,
        ];
      }
      const capabilities = asRecord(model.capabilities);
      loaded.push({
        modelKey: String(model.key ?? ''),
        vision: capabilities?.vision === true,
        instanceId: instance.id,
      });
    }
  }
  if (loaded.length !== 1) {
    return [`expected exactly one loaded local model instance, found ${loaded.length}`];
  }
  const [fixture] = loaded;
  const errors: string[] = [];
  if (fixture.modelKey !== expectedModelKey) {
    errors.push(
      `loaded model key ${JSON.stringify(fixture.modelKey)} does not match ${JSON.stringify(expectedModelKey)}`,
    );
  }
  if (expectedInstanceId && fixture.instanceId !== expectedInstanceId) {
    errors.push(
      `loaded instance ${JSON.stringify(fixture.instanceId)} does not match ${JSON.stringify(expectedInstanceId)}`,
    );
  }
  if (!fixture.vision) {
    errors.push('loaded local model does not advertise vision capability');
  }
  return errors;
};

const xmlEscape = (value: unknown): string =>
  String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&apos;');

export const createJUnitXml = (
  name: string,
  results: Array<{
    id: string;
    outcome: GateOutcome;
    durationSeconds?: number;
    message?: string;
  }>,
): string => {
  const failures = results.filter((item) => item.outcome === 'FAIL').length;
  const errors = results.filter((item) =>
    ['BLOCKED', 'ABORTED'].includes(item.outcome),
  ).length;
  const skipped = results.filter((item) => item.outcome === 'SKIPPED').length;
  const time = results.reduce((total, item) => total + (item.durationSeconds ?? 0), 0);
  const cases = results
    .map((item) => {
      const attrs = `name="${xmlEscape(item.id)}" time="${(
        item.durationSeconds ?? 0
      ).toFixed(3)}"`;
      const message = xmlEscape(item.message ?? item.outcome);
      if (item.outcome === 'FAIL') {
        return `  <testcase ${attrs}><failure message="${message}"/></testcase>`;
      }
      if (item.outcome === 'BLOCKED' || item.outcome === 'ABORTED') {
        return `  <testcase ${attrs}><error type="${item.outcome}" message="${message}"/></testcase>`;
      }
      if (item.outcome === 'SKIPPED') {
        return `  <testcase ${attrs}><skipped message="${message}"/></testcase>`;
      }
      return `  <testcase ${attrs}/>`;
    })
    .join('\n');
  return [
    '<?xml version="1.0" encoding="UTF-8"?>',
    `<testsuite name="${xmlEscape(name)}" tests="${results.length}" failures="${failures}" errors="${errors}" skipped="${skipped}" time="${time.toFixed(3)}">`,
    cases,
    '</testsuite>',
    '',
  ].join('\n');
};
