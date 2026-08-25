import {
  addNotification,
  clearResults,
  ensureActiveRun,
  setStatus,
  upsertRun,
} from '../app/store-actions';
import { INPUTS_CLASSES } from '../elements/main.inputs';
import {
  getWorkflowSubmission,
  runWorkflow,
  uploadWorkflowFiles,
  WorkflowApiError,
} from '../services/workflow-service';
import {
  WorkflowRunRequestPayload,
  WorkflowRunResponse,
  WorkflowRunStatus,
  WorkflowSubmissionSnapshot,
} from '../types/api';
import { WorkflowCellStatus, WorkflowUICells } from '../types/section';
import { WorkflowStore } from '../types/state';
import { DEBUG_MESSAGES, NOTIFICATION_MESSAGES, STATUS_MESSAGES } from '../utils/constants';
import { debugLog } from '../utils/debug';
import { getRetainedUploadPrefill, WorkflowUploadPrefill } from '../utils/input-prefill';

const SUBMISSIONS_IN_FLIGHT = new WeakSet<WorkflowStore>();
/**
 * One materialized request is retained per mounted store.
 *
 * - Transport errors, timeouts, 5xx, and invalid success bodies retain the
 *   exact envelope and submission id (`ambiguous`).
 * - Explicit 4xx responses retain materialized uploads but force a fresh id
 *   on the next unchanged attempt (`authoritative-rejection`).
 * - A changed raw-form fingerprint discards both identity and materialization.
 * - A valid POST response or successful GET reconciliation clears everything.
 *
 * This cache is deliberately local: GET reconciliation helps when available,
 * but retry correctness never depends on the backend's process-local index.
 */
const RETRYABLE_SUBMISSIONS = new WeakMap<WorkflowStore, RetryableSubmission>();
let fallbackSubmissionCounter = 0;

type InputIntent =
  | {
      id: string;
      kind: 'upload';
      files: File[];
      required: boolean;
      retained?: WorkflowUploadPrefill;
    }
  | {
      id: string;
      kind: 'value';
      tagName: string;
      value: unknown;
    };

type RetryableSubmission = {
  envelope: WorkflowRunRequestPayload;
  intentFingerprint: string;
  outcome: 'ambiguous' | 'authoritative-rejection';
  startedAt: number;
};

export const createWorkflowSubmissionId = (): string => {
  const browserCrypto = globalThis.crypto;
  if (typeof browserCrypto?.randomUUID === 'function') {
    return `lf-web:${browserCrypto.randomUUID()}`;
  }

  if (typeof browserCrypto?.getRandomValues === 'function') {
    const bytes = new Uint8Array(16);
    browserCrypto.getRandomValues(bytes);
    const entropy = Array.from(bytes, (value) => value.toString(16).padStart(2, '0')).join('');
    return `lf-web:${entropy}`;
  }

  // Extremely old/non-browser embeddings may expose neither Web Crypto API.
  // The module counter prevents same-realm, same-millisecond collisions; the
  // random suffix reduces cross-tab collisions without claiming cryptographic
  // identity in an environment that has no cryptographic source.
  fallbackSubmissionCounter += 1;
  return `lf-web:${Date.now().toString(36)}:${fallbackSubmissionCounter.toString(36)}:${Math.random().toString(36).slice(2)}`;
};

//#region Helpers
const _readInputIntent = async (store: WorkflowStore): Promise<InputIntent[]> => {
  const state = store.getState();
  const { uiRegistry } = state.manager;

  const elements = uiRegistry.get();
  const cells = (elements?.[INPUTS_CLASSES.cells] as WorkflowUICells) || [];

  const intent: InputIntent[] = [];

  for (const cell of cells) {
    const id = cell.id || '';
    _setCellStatus(store, id);

    const tagName = cell.tagName.toLowerCase();
    try {
      switch (tagName) {
        case 'lf-chat': {
          const value = await (cell as HTMLLfChatElement).getHistory();
          intent.push({ id, kind: 'value', tagName, value });
          break;
        }
        case 'lf-select': {
          const selected = (await (cell as HTMLLfSelectElement).getValue()) as {
            id?: string;
            value?: string | number;
            workflowValue?: string | number;
          } | null;
          intent.push({
            id,
            kind: 'value',
            tagName,
            value: selected?.workflowValue ?? selected?.value ?? selected?.id ?? null,
          });
          break;
        }
        case 'lf-toggle': {
          const value = await (cell as HTMLLfToggleElement).getValue();
          intent.push({ id, kind: 'value', tagName, value: value !== 'off' });
          break;
        }
        case 'lf-upload': {
          const value = await (cell as HTMLLfUploadElement).getValue();
          intent.push({
            files: Array.isArray(value) ? value : (value as File[] | undefined) || [],
            id,
            kind: 'upload',
            required: cell.dataset.required !== 'false',
            retained: getRetainedUploadPrefill(cell),
          });
          break;
        }
        default: {
          const value = await (cell as HTMLLfTextfieldElement).getValue();
          intent.push({ id, kind: 'value', tagName, value });
        }
      }
    } catch (error) {
      if (tagName === 'lf-upload') {
        _setCellStatus(store, id, 'error');
      }
      throw error;
    }
  }

  return intent;
};

const _canonicalizeIntentValue = (value: unknown, ancestors = new WeakSet<object>()): unknown => {
  if (value === null || typeof value === 'string' || typeof value === 'boolean') {
    return value;
  }
  if (typeof value === 'number') {
    if (Number.isNaN(value)) return { $number: 'NaN' };
    if (value === Infinity) return { $number: 'Infinity' };
    if (value === -Infinity) return { $number: '-Infinity' };
    if (Object.is(value, -0)) return { $number: '-0' };
    return value;
  }
  if (typeof value === 'undefined') return { $type: 'undefined' };
  if (typeof value === 'bigint') return { $bigint: value.toString() };
  if (typeof value === 'symbol') return { $symbol: value.description ?? '' };
  if (typeof value === 'function') return { $function: value.name || '' };
  if (typeof value !== 'object') return { $type: typeof value };

  if (ancestors.has(value)) {
    throw new Error('An input contains a circular value and cannot be submitted.');
  }
  ancestors.add(value);
  try {
    if (Array.isArray(value)) {
      return value.map((item) => _canonicalizeIntentValue(item, ancestors));
    }
    if (value instanceof Date) {
      return { $date: value.toISOString() };
    }
    const normalized: Record<string, unknown> = {};
    for (const key of Object.keys(value).sort()) {
      normalized[key] = _canonicalizeIntentValue(
        (value as Record<string, unknown>)[key],
        ancestors,
      );
    }
    return normalized;
  } finally {
    ancestors.delete(value);
  }
};

const _intentFingerprint = (workflowId: string, intent: InputIntent[]): string =>
  JSON.stringify({
    workflowId,
    inputs: intent.map((entry) => {
      if (entry.kind === 'value') {
        return {
          id: entry.id,
          kind: entry.kind,
          tagName: entry.tagName,
          value: _canonicalizeIntentValue(entry.value),
        };
      }

      if (entry.files.length > 0) {
        return {
          files: entry.files.map((file) => ({
            lastModified: file.lastModified,
            name: file.name,
            relativePath: file.webkitRelativePath || '',
            size: file.size,
            type: file.type,
          })),
          id: entry.id,
          kind: entry.kind,
          required: entry.required,
        };
      }

      return {
        id: entry.id,
        kind: entry.kind,
        required: entry.required,
        retainedReference: entry.retained
          ? _canonicalizeIntentValue(entry.retained.reference)
          : null,
      };
    }),
  });

const _materializeInputs = async (
  store: WorkflowStore,
  intent: InputIntent[],
): Promise<Record<string, unknown>> => {
  const inputs: Record<string, unknown> = {};
  for (const entry of intent) {
    if (entry.kind === 'value') {
      inputs[entry.id] = entry.value;
      continue;
    }

    try {
      const uploaded = await _handleUploadCell(
        store,
        entry.files,
        entry.required,
        entry.retained,
      );
      if (uploaded !== undefined) {
        inputs[entry.id] = uploaded;
      }
    } catch (error) {
      _setCellStatus(store, entry.id, 'error');
      throw error;
    }
  }
  return inputs;
};

const _createEnvelope = (
  workflowId: string,
  inputs: Record<string, unknown>,
  submissionId: string,
): WorkflowRunRequestPayload => {
  const serialized = JSON.stringify({ workflowId, inputs, submissionId });
  if (!serialized) {
    throw new Error('Workflow inputs could not be serialized.');
  }
  return JSON.parse(serialized) as WorkflowRunRequestPayload;
};
const _handleUploadCell = async (
  store: WorkflowStore,
  rawValue: unknown,
  required: boolean,
  retainedValue?: WorkflowUploadPrefill,
) => {
  const { ERROR_UPLOADING_FILE, RUNNING_UPLOADING_FILE } = STATUS_MESSAGES;

  const files = Array.isArray(rawValue) ? rawValue : (rawValue as File[] | undefined);
  if (!files || files.length === 0) {
    if (retainedValue?.available) {
      return { ...retainedValue.reference };
    }
    if (retainedValue && !retainedValue.available) {
      throw new Error('The previous upload is no longer available. Choose the file again.');
    }
    if (!required) {
      return undefined;
    }
    throw new Error('No files selected for upload.');
  }

  try {
    setStatus(store, 'running', RUNNING_UPLOADING_FILE);
    const { payload } = await uploadWorkflowFiles(files);
    const paths = payload?.paths || [];
    return paths.length === 1 ? paths[0] : paths;
  } catch (error) {
    setStatus(store, 'error', ERROR_UPLOADING_FILE);

    if (error instanceof WorkflowApiError) {
      addNotification(store, {
        id: performance.now().toString(),
        message: `Upload failed: ${error.payload?.detail || error.message}`,
        status: 'danger',
      });
    }
    throw error;
  }
};
const _setCellStatus = (store: WorkflowStore, id: string, status: WorkflowCellStatus = '') => {
  const { WORKFLOW_INPUT_FLAGGED } = DEBUG_MESSAGES;
  const state = store.getState();
  const { current, manager, mutate } = state;
  const { uiRegistry } = manager;

  const elements = uiRegistry.get();
  const cells = (elements?.[INPUTS_CLASSES.cells] as WorkflowUICells) || [];

  const cell = cells.find((el) => el.id === id);
  const wrapper = cell?.parentElement;
  if (wrapper) {
    if (status) {
      wrapper.dataset.status = status;
    } else {
      delete wrapper.dataset.status;
    }
  }

  mutate.inputStatus(id, status);

  if (status) {
    debugLog(WORKFLOW_INPUT_FLAGGED, 'informational', {
      cell: id,
      id: current.id,
      status,
    });
  }
};

const _toRunStatus = (status: WorkflowSubmissionSnapshot['status']): WorkflowRunStatus =>
  status === 'accepted' || status === 'reconciling' ? 'pending' : status;

const _normalizeRunResponse = (
  response: WorkflowRunResponse | string,
  submissionId: string,
): WorkflowRunResponse => {
  if (typeof response === 'string') {
    return {
      idempotentReplay: false,
      runId: response,
      status: 'pending',
      submissionId,
    };
  }
  if (!response.runId || response.submissionId !== submissionId) {
    throw new WorkflowApiError('Workflow run failed. (invalid response)', { status: 200 });
  }
  return response;
};

const _recordRun = (
  store: WorkflowStore,
  response: WorkflowRunResponse,
  workflowId: string,
  workflowName: string,
  startedAt: number,
) => {
  const timestamp = Date.now();
  upsertRun(store, {
    cancelRequested: false,
    createdAt: startedAt,
    error: null,
    httpStatus: null,
    // Upload responses contain host paths for the immediate local request.
    // Do not copy them into browser state: the run-detail endpoint will
    // hydrate authoritative, opaque remix references after registration.
    inputs: {},
    outputs: null,
    resultPayload: null,
    runId: response.runId,
    submissionId: response.submissionId,
    status: _toRunStatus(response.status),
    updatedAt: timestamp,
    workflowId,
    workflowName,
  });
  ensureActiveRun(store, response.runId);
};

const _errorDetail = (error: unknown, fallback: string): string => {
  if (error instanceof WorkflowApiError) {
    const payload = error.payload as { detail?: string } | undefined;
    return payload?.detail || error.message;
  }
  return error instanceof Error ? error.message || fallback : fallback;
};

const _isAuthoritativeRejection = (error: unknown): error is WorkflowApiError =>
  error instanceof WorkflowApiError &&
  typeof error.status === 'number' &&
  error.status >= 400 &&
  error.status < 500;

type ReconciliationResult =
  | { kind: 'recovered'; response: WorkflowRunResponse }
  | { detail: string; kind: 'rejected' }
  | { kind: 'unknown' };

const _reconcileSubmission = async (
  submissionId: string,
): Promise<ReconciliationResult> => {
  try {
    const snapshot = await getWorkflowSubmission(submissionId);
    if (!snapshot) {
      // The lifecycle index can restart independently from the browser. A 404
      // therefore does not prove that the original POST missed Comfy's queue.
      return { kind: 'unknown' };
    }
    if (snapshot.run_id) {
      return {
        kind: 'recovered',
        response: {
          idempotentReplay: true,
          runId: snapshot.run_id,
          status: snapshot.status,
          submissionId: snapshot.submission_id,
        },
      };
    }
    if (snapshot.status === 'failed' || snapshot.status === 'cancelled') {
      return {
        detail: snapshot.error || `Submission ${snapshot.status}.`,
        kind: 'rejected',
      };
    }
  } catch {
    // Reconciliation is opportunistic. The locally retained request remains
    // the safety authority when this process-local endpoint is unavailable.
  }
  return { kind: 'unknown' };
};
//#endregion

//#region Dispatcher
export const workflowDispatcher = async (store: WorkflowStore) => {
  const { INPUTS_COLLECTED } = DEBUG_MESSAGES;
  const { NO_WORKFLOW_SELECTED } = NOTIFICATION_MESSAGES;
  const { ERROR_RUNNING_WORKFLOW, RUNNING_DISPATCHING_WORKFLOW, RUNNING_SUBMITTING_WORKFLOW } =
    STATUS_MESSAGES;

  const state = store.getState();
  const { current } = state;
  const id = current.id;

  // A click owns one stable request identity. Ignore accidental re-entry until
  // that request has either bound to its Comfy prompt or failed visibly.
  if (SUBMISSIONS_IN_FLIGHT.has(store) || state.submissionInFlightId) {
    return;
  }

  if (!id) {
    addNotification(store, {
      id: performance.now().toString(),
      message: NO_WORKFLOW_SELECTED,
      status: 'warning',
    });
    return;
  }

  const cached = RETRYABLE_SUBMISSIONS.get(store);
  const provisionalSubmissionId =
    cached?.outcome === 'ambiguous'
      ? String(cached.envelope.submissionId)
      : createWorkflowSubmissionId();
  SUBMISSIONS_IN_FLIGHT.add(store);
  state.mutate.submissionInFlight?.(provisionalSubmissionId);

  try {
    setStatus(store, 'running', RUNNING_SUBMITTING_WORKFLOW);

    let attempt: RetryableSubmission;
    try {
      const intent = await _readInputIntent(store);
      const intentFingerprint = _intentFingerprint(id, intent);

      if (cached?.intentFingerprint === intentFingerprint) {
        if (cached.outcome === 'ambiguous') {
          // This is the one truly safe ambiguous retry: the same object is
          // passed back to the service, preserving the complete JSON envelope.
          attempt = cached;
        } else {
          attempt = {
            envelope: _createEnvelope(
              id,
              cached.envelope.inputs,
              provisionalSubmissionId,
            ),
            intentFingerprint,
            outcome: 'ambiguous',
            startedAt: Date.now(),
          };
        }
      } else {
        RETRYABLE_SUBMISSIONS.delete(store);
        const submissionId =
          cached?.outcome === 'ambiguous'
            ? createWorkflowSubmissionId()
            : provisionalSubmissionId;
        state.mutate.submissionInFlight?.(submissionId);
        const inputs = await _materializeInputs(store, intent);
        attempt = {
          envelope: _createEnvelope(id, inputs, submissionId),
          intentFingerprint,
          outcome: 'ambiguous',
          startedAt: Date.now(),
        };
      }

      state.mutate.submissionInFlight?.(String(attempt.envelope.submissionId));
      debugLog(INPUTS_COLLECTED, 'informational', {
        id,
        inputKeys: Object.keys(attempt.envelope.inputs),
      });
    } catch (error) {
      const detail = _errorDetail(error, 'Failed to collect inputs.');
      setStatus(store, 'error', ERROR_RUNNING_WORKFLOW);
      addNotification(store, {
        id: performance.now().toString(),
        message: `Failed to collect inputs: ${detail}`,
        status: 'danger',
      });
      return;
    }

    setStatus(store, 'running', RUNNING_DISPATCHING_WORKFLOW);
    clearResults(store);
    const workflowName = state.manager?.workflow.title() ?? id;

    // Install the retry record before crossing the network boundary. Success
    // and authoritative rejection below are the only paths that supersede it.
    RETRYABLE_SUBMISSIONS.set(store, attempt);
    try {
      const response = _normalizeRunResponse(
        await runWorkflow(attempt.envelope),
        String(attempt.envelope.submissionId),
      );
      RETRYABLE_SUBMISSIONS.delete(store);
      _recordRun(store, response, id, workflowName, attempt.startedAt);
    } catch (error) {
      setStatus(store, 'error', ERROR_RUNNING_WORKFLOW);
      const payload =
        error instanceof WorkflowApiError
          ? (error.payload as { detail?: string; error?: { input?: string } } | undefined)
          : undefined;
      const inputName = payload?.error?.input;
      if (inputName) {
        _setCellStatus(store, inputName, 'error');
      }

      if (_isAuthoritativeRejection(error)) {
        attempt.outcome = 'authoritative-rejection';
        RETRYABLE_SUBMISSIONS.set(store, attempt);
        addNotification(store, {
          id: performance.now().toString(),
          message: `Workflow run failed: ${payload?.detail || error.message}`,
          status: 'danger',
        });
        return;
      }

      attempt.outcome = 'ambiguous';
      RETRYABLE_SUBMISSIONS.set(store, attempt);
      const reconciliation = await _reconcileSubmission(
        String(attempt.envelope.submissionId),
      );
      if (reconciliation.kind === 'recovered') {
        RETRYABLE_SUBMISSIONS.delete(store);
        _recordRun(store, reconciliation.response, id, workflowName, attempt.startedAt);
        addNotification(store, {
          id: performance.now().toString(),
          message: 'Workflow submission recovered after the response was interrupted.',
          status: 'info',
        });
        return;
      }
      if (reconciliation.kind === 'rejected') {
        attempt.outcome = 'authoritative-rejection';
        RETRYABLE_SUBMISSIONS.set(store, attempt);
        addNotification(store, {
          id: performance.now().toString(),
          message: `Workflow run failed: ${reconciliation.detail}`,
          status: 'danger',
        });
        return;
      }

      addNotification(store, {
        id: performance.now().toString(),
        message:
          'Workflow outcome is unknown. Retry is safe: unchanged inputs will reuse the same submission and uploaded files.',
        status: 'warning',
      });
    }
  } finally {
    SUBMISSIONS_IN_FLIGHT.delete(store);
    store.getState().mutate.submissionInFlight?.(null);
  }
};

export const workflowCancellationDispatcher = async (store: WorkflowStore) => {
  const state = store.getState();
  const run = state.runs.find((entry) => entry.runId === state.currentRunId);
  if (
    !run ||
    !run.submissionId ||
    !['pending', 'running'].includes(run.status) ||
    run.cancelRequested ||
    state.cancelInFlightRunId === run.runId
  ) {
    return;
  }

  state.mutate.cancelInFlightRun(run.runId);
  setStatus(store, 'running', 'Stopping workflow...');
  try {
    if (!state.manager.runs.cancel) {
      throw new Error('Workflow cancellation is unavailable.');
    }
    await state.manager.runs.cancel(run.runId);
  } catch (error) {
    const detail = error instanceof Error ? error.message : 'Unable to stop workflow.';
    addNotification(store, {
      id: performance.now().toString(),
      message: detail,
      status: 'danger',
    });
    setStatus(store, 'error', detail);
  } finally {
    store.getState().mutate.cancelInFlightRun(null);
  }
};
//#endregion
