import { describe, expect, it } from 'vitest';

import {
  classifyHistoryEntry,
  classifyPostCancellation,
  comfyArtifactKey,
  countPreviewReferences,
  collectPreviewUrls,
  collectReceiptSchemas,
  createJUnitXml,
  describeGateScope,
  determineAchievedGate,
  executionEventNodeId,
  extractDatasetCellPreviewUrl,
  extractHistoryExecutionTargets,
  extractHistoryPrompt,
  normalizeExecutionTargetIds,
  parseQueueSnapshot,
  requiredFlagsForResourceClass,
  selectOwnedSubmissionPromptId,
  timedOutTerminalClassification,
  unwrapHistoryEntry,
  validateCaseOutputs,
  validateCoverage,
  validateExecutionTrace,
  validateEditorClientBinding,
  validateLoadedModelFixture,
  type TitanicManifest,
} from '../titanic_e2e_core.ts';

describe('Titanic E2E pure contracts', () => {
  it('parses current Comfy queue tuples and fails closed on malformed entries', () => {
    const parsed = parseQueueSnapshot({
      queue_running: [[0, 'running-id', {}, {}]],
      queue_pending: [{ prompt_id: 'pending-id' }, ['bad']],
    });
    expect([...parsed.running]).toEqual(['running-id']);
    expect([...parsed.pending]).toEqual(['pending-id']);
    expect(parsed.malformed).toEqual(['queue_pending[1] has no prompt id']);
  });

  it('classifies exact history state without treating mere presence as success', () => {
    const response = {
      abc: { status: { completed: true, status_str: 'success' }, outputs: {} },
    };
    const entry = unwrapHistoryEntry(response, 'abc');
    expect(classifyHistoryEntry(entry)).toBe('success');
    expect(classifyHistoryEntry({ status: { completed: false, status_str: 'running' } })).toBe(
      'incomplete',
    );
    expect(classifyHistoryEntry(null)).toBe('missing');
  });

  it('does not call a vanished prompt cleaned up when cancellation was not acknowledged', () => {
    expect(classifyPostCancellation('missing', false, false, false)).toBe('wait');
    expect(classifyPostCancellation('missing', false, false, true)).toBe('cancelled');
    expect(classifyPostCancellation('success', false, false, false)).toBe('late-success');
    expect(classifyPostCancellation('failure', false, false, false)).toBe('late-failure');
    expect(classifyPostCancellation('missing', true, false, true)).toBe('wait');
    expect(classifyPostCancellation('missing', false, true, true)).toBe('wait');
    expect(timedOutTerminalClassification('late-success')).toBe('timeout');
    expect(timedOutTerminalClassification('late-failure')).toBe('timeout');
    expect(timedOutTerminalClassification('cancelled')).toBe('timeout');
    expect(timedOutTerminalClassification('wait')).toBeNull();
  });

  it('requires exhaustive and disjoint output classification', () => {
    const manifest = {
      coverageCases: [
        { id: 'a', targets: [1, 2] },
        { id: 'b', targets: [2, 3] },
      ],
    } as unknown as TitanicManifest;
    expect(validateCoverage(manifest, [1, 2, 4])).toEqual([
      'active output 4 is unclassified',
      'manifest output 3 is not active',
      'output 2 is assigned to both a and b',
    ]);
  });

  it('extracts receipt schemas and deduplicated preview URLs from LF history output', () => {
    const payload = {
      lf_output: [
        {
          receipt: { schema: 'lf.example.receipt.v1' },
          dataset: {
            nodes: [
              { cells: { image: { lfValue: '/view?filename=a.png&type=temp' } } },
              { cells: { image: { value: '/view?filename=a.png&type=temp' } } },
            ],
          },
        },
      ],
    };
    expect([...collectReceiptSchemas(payload)]).toEqual(['lf.example.receipt.v1']);
    expect(collectPreviewUrls(payload)).toEqual(['/view?filename=a.png&type=temp']);
    expect(countPreviewReferences(payload)).toBe(2);
  });

  it('compares Comfy artifacts without treating cache-busting nonces as identity', () => {
    expect(
      comfyArtifactKey('/view?filename=inpaint.png&type=temp&subfolder=edits&nonce=first'),
    ).toBe(
      comfyArtifactKey('/view?nonce=second&subfolder=edits&type=temp&filename=inpaint.png'),
    );
    expect(
      comfyArtifactKey('/view?filename=other.png&type=temp&subfolder=edits'),
    ).not.toBe(comfyArtifactKey('/view?filename=inpaint.png&type=temp&subfolder=edits'));
  });

  it('labels a selected full case as targeted and reserves full execution for exhaustive coverage', () => {
    const targeted = describeGateScope('full', ['browser.interactive'], [
      'cpu.headless',
      'browser.interactive',
    ]);
    expect(targeted).toEqual({
      requestedMode: 'full',
      mode: 'targeted',
      caseIds: ['browser.interactive'],
      selectedCoverageCaseIds: ['browser.interactive'],
      allCoverageCasesSelected: false,
    });
    expect(
      determineAchievedGate(targeted, [
        { id: 'inventory', outcome: 'PASS' },
        { id: 'hydration', outcome: 'PASS' },
        { id: 'browser.interactive', outcome: 'PASS' },
        { id: 'workflow-immutability', outcome: 'PASS' },
      ], true),
    ).toBe('targeted-branch-execution');
    expect(
      determineAchievedGate(targeted, [
        { id: 'inventory', outcome: 'PASS' },
        { id: 'hydration', outcome: 'PASS' },
        { id: 'browser.interactive', outcome: 'PASS' },
        { id: 'workflow-immutability', outcome: 'PASS' },
      ]),
    ).toBe('targeted-branch-coverage');

    const full = describeGateScope('full', [], ['a', 'b']);
    expect(
      determineAchievedGate(full, [
        { id: 'inventory', outcome: 'PASS' },
        { id: 'hydration', outcome: 'PASS' },
        { id: 'a', outcome: 'PASS' },
        { id: 'b', outcome: 'PASS' },
        { id: 'workflow-immutability', outcome: 'PASS' },
      ], true),
    ).toBe('full-workflow-execution');
    expect(
      determineAchievedGate(full, [
        { id: 'inventory', outcome: 'PASS' },
        { id: 'hydration', outcome: 'PASS' },
        { id: 'a', outcome: 'PASS' },
        { id: 'b', outcome: 'PASS' },
        { id: 'workflow-immutability', outcome: 'PASS' },
      ]),
    ).toBe('full-workflow-coverage');
    expect(
      determineAchievedGate(full, [
        { id: 'inventory', outcome: 'PASS' },
        { id: 'hydration', outcome: 'PASS' },
        { id: 'a', outcome: 'PASS' },
        { id: 'b', outcome: 'BLOCKED' },
        { id: 'workflow-immutability', outcome: 'PASS' },
      ]),
    ).toBe('hydration');

    expect(
      determineAchievedGate(full, [
        { id: 'inventory', outcome: 'PASS' },
        { id: 'hydration', outcome: 'PASS' },
        { id: 'a', outcome: 'PASS' },
        { id: 'b', outcome: 'PASS' },
        { id: 'workflow-immutability', outcome: 'FAIL' },
      ]),
    ).toBe('hydration');
  });

  it('binds evidence to the exact prompt tuple owned by the terminal history entry', () => {
    const prompt = { '418': { class_type: 'LF_ViewImages', inputs: {} } };
    expect(
      extractHistoryPrompt(
        { prompt: [7, 'owned-prompt', prompt, {}, ['418']] },
        'owned-prompt',
      ),
    ).toEqual(prompt);
    expect(
      extractHistoryPrompt(
        { prompt: [7, 'foreign-prompt', prompt, {}, ['418']] },
        'owned-prompt',
      ),
    ).toBeNull();
    expect(
      extractHistoryExecutionTargets(
        { prompt: [7, 'owned-prompt', prompt, {}, ['418', 441]] },
        'owned-prompt',
      ),
    ).toEqual(['418', '441']);
    expect(
      extractHistoryExecutionTargets(
        { prompt: [7, 'foreign-prompt', prompt, {}, ['418']] },
        'owned-prompt',
      ),
    ).toBeNull();
    expect(normalizeExecutionTargetIds(['418', 418])).toBeNull();
    expect(selectOwnedSubmissionPromptId('response-owned', ['foreign'])).toBe(
      'response-owned',
    );
    expect(selectOwnedSubmissionPromptId(null, ['exact-observed'])).toBe(
      'exact-observed',
    );
    expect(selectOwnedSubmissionPromptId(null, [])).toBeNull();
    expect(selectOwnedSubmissionPromptId(null, ['one', 'two'])).toBeNull();
  });

  it('extracts only the exact selected comparison cell from durable LF history', () => {
    const output = {
      lf_output: [
        {
          dataset: {
            nodes: [
              {
                cells: {
                  lfImage: { lfValue: '/view?filename=before-0.png&type=temp' },
                  lfImage_after: { lfValue: '/view?filename=after-0.png&type=temp' },
                },
              },
              {
                cells: {
                  lfImage: { lfValue: '/view?filename=before-1.png&type=temp' },
                  lfImage_after: { lfValue: '/view?filename=after-1.png&type=temp' },
                },
              },
            ],
          },
        },
      ],
    };
    expect(extractDatasetCellPreviewUrl(output, 1, 'lfImage')).toBe(
      '/view?filename=before-1.png&type=temp',
    );
    expect(extractDatasetCellPreviewUrl(output, 1, 'lfImage_after')).toBe(
      '/view?filename=after-1.png&type=temp',
    );
    expect(extractDatasetCellPreviewUrl(output, 2, 'lfImage')).toBeNull();
  });

  it('requires the declared editor rail to execute and forbids cache-only evidence', () => {
    const manifestCase = {
      id: 'browser.interactive',
      execution: {
        requiredNodeIds: [463, 441, 418],
        forbiddenCachedNodeIds: [463, 441, 418],
        requiredAfterInteractionNodeIds: [441, 418],
      },
    } as any;
    expect(
      validateExecutionTrace(manifestCase, {
        promptId: 'owned',
        started: true,
        terminalEvent: 'execution_success',
        executedNodeIds: ['463', '441', '418'],
        uiExecutedNodeIds: ['463', '418'],
        cachedNodeIds: [],
        executingEvents: [
          { nodeId: '463', timestampMs: 10 },
          { nodeId: '441', timestampMs: 30 },
          { nodeId: '418', timestampMs: 40 },
        ],
        executedPreviewUrlsByNode: {},
      }, 20),
    ).toEqual([]);
    expect(
      validateExecutionTrace(manifestCase, {
        promptId: 'owned',
        started: true,
        terminalEvent: 'execution_success',
        executedNodeIds: ['463', '418'],
        uiExecutedNodeIds: ['463', '418'],
        cachedNodeIds: ['441'],
        executingEvents: [
          { nodeId: '463', timestampMs: 10 },
          { nodeId: '418', timestampMs: 40 },
        ],
        executedPreviewUrlsByNode: {},
      }, 20),
    ).toEqual([
      'node 441 was not observed executing for prompt owned',
      'node 441 was served from cache for prompt owned',
      'node 441 was not observed executing after interaction resume',
    ]);
  });

  it('binds every editor mutation and recovery artifact to one immutable client owner', () => {
    const valid = {
      callerClientId: 'client-a',
      contextId: '463_deadbeef_edit_dataset.json',
      pendingOwnerClientId: 'client-a',
      recoveredOwnerClientId: 'client-a',
      completedOwnerClientId: 'client-a',
      processCallerClientId: 'client-a',
      processContextId: '463_deadbeef_edit_dataset.json',
      updateCallerClientId: 'client-a',
      updateContextId: '463_deadbeef_edit_dataset.json',
      completedContextId: '463_deadbeef_edit_dataset.json',
      wrongOwnerRecoveryData: null,
    };
    expect(validateEditorClientBinding(valid)).toEqual([]);
    expect(
      validateEditorClientBinding({
        ...valid,
        completedOwnerClientId: 'client-b',
        processCallerClientId: undefined,
        processContextId: 'other.json',
        wrongOwnerRecoveryData: { context_id: 'leaked' },
      }),
    ).toEqual([
      'completed dataset owner "client-b" does not match connected client "client-a"',
      'process-image caller undefined does not match connected client "client-a"',
      'wrong-owner edit-dataset recovery returned session data',
      'process-image context "other.json" does not match exact context "463_deadbeef_edit_dataset.json"',
    ]);
    expect(
      validateEditorClientBinding({ ...valid, callerClientId: '  ' }),
    ).toEqual(['image editor has no connected Comfy caller client id']);
  });

  it('recognizes the current frontend primitive executing-event detail', () => {
    expect(executionEventNodeId('executing', '441')).toBe('441');
    expect(executionEventNodeId('executing', 442)).toBe('442');
    expect(executionEventNodeId('executed', { node: '418' })).toBe('418');
    expect(executionEventNodeId('execution_start', { prompt_id: 'owned' })).toBeNull();
  });

  it('requires restart-stable input previews when declared', () => {
    const manifestCase = {
      id: 'preview',
      expect: {
        '10': {
          minimumPreviewCount: 1,
          previewStorageType: 'input',
        },
      },
    } as any;
    const history = {
      outputs: {
        '10': { lf_output: [{ dataset: { nodes: [{ value: '/view?filename=a.png&type=input' }] } }] },
      },
    };
    expect(validateCaseOutputs(manifestCase, history)).toEqual([]);
  });

  it('does not treat provider error payloads as successful LLM output', () => {
    const manifestCase = {
      id: 'llm',
      expect: {
        '10': { forbidTopLevelJsonKeys: ['error'] },
        '11': {
          minimumStringLength: 1,
          forbiddenStringPrefixes: ['Oops!'],
        },
      },
    } as any;
    const history = {
      outputs: {
        '10': { lf_output: [{ json: { error: 'model is not loaded' } }] },
        '11': { lf_output: [{ string: 'Oops! Request failed.' }] },
      },
    };
    expect(validateCaseOutputs(manifestCase, history)).toEqual([
      'node 10 JSON response contains forbidden key "error"',
      'node 11 string begins with forbidden error prefix "Oops!"',
    ]);
  });

  it('maps resource classes to explicit authority gates', () => {
    expect(requiredFlagsForResourceClass('cpu')).toEqual([]);
    expect(requiredFlagsForResourceClass('filesystem-unpinned')).toEqual([
      'allowUnpinnedInputs',
    ]);
    expect(requiredFlagsForResourceClass('durable-write')).toEqual([
      'allowWrites',
    ]);
    expect(requiredFlagsForResourceClass('model-cpu')).toEqual([
      'allowModels',
    ]);
    expect(requiredFlagsForResourceClass('model-gpu-write')).toEqual([
      'allowGpu',
      'allowModels',
      'allowWrites',
    ]);
    expect(requiredFlagsForResourceClass('gpu')).toEqual([
      'allowGpu',
      'allowModels',
    ]);
    expect(requiredFlagsForResourceClass('gpu-unpinned')).toEqual([
      'allowGpu',
      'allowModels',
      'allowUnpinnedInputs',
    ]);
    expect(requiredFlagsForResourceClass('local-llm-gpu-write')).toEqual([
      'allowGpu',
      'allowModels',
      'allowWrites',
      'allowLocalLlm',
    ]);
    expect(requiredFlagsForResourceClass('browser-interactive-gpu-model')).toEqual([
      'allowGpu',
      'allowModels',
      'allowInteraction',
    ]);
    expect(() => requiredFlagsForResourceClass('gpu-wirte')).toThrow(
      'unknown Titanic resource class: "gpu-wirte"',
    );
  });

  it('uses LM Studio loaded instances rather than the JIT download catalogue', () => {
    const catalogue = {
      models: [
        {
          key: 'fixture',
          capabilities: { vision: true },
          loaded_instances: [{ id: 'lf-titanic-fixture' }],
        },
        {
          key: 'downloaded-but-idle',
          capabilities: { vision: true },
          loaded_instances: [],
        },
      ],
    };
    expect(
      validateLoadedModelFixture(
        catalogue,
        'fixture',
        'lf-titanic-fixture',
      ),
    ).toEqual([]);
    expect(validateLoadedModelFixture(catalogue, 'other')).toEqual([
      'loaded model key "fixture" does not match "other"',
    ]);
    expect(
      validateLoadedModelFixture(
        {
          models: catalogue.models.map((model) => ({
            ...model,
            loaded_instances: [],
          })),
        },
        'fixture',
      ),
    ).toEqual(['expected exactly one loaded local model instance, found 0']);
  });

  it('keeps blocked results distinct from skipped policy branches in JUnit', () => {
    const xml = createJUnitXml('gate', [
      { id: 'pass', outcome: 'PASS' },
      { id: 'blocked', outcome: 'BLOCKED', message: 'model absent' },
      { id: 'disabled', outcome: 'SKIPPED', message: 'policy' },
    ]);
    expect(xml).toContain('errors="1"');
    expect(xml).toContain('skipped="1"');
    expect(xml).toContain('<error type="BLOCKED"');
    expect(xml).toContain('<skipped message="policy"');
  });
});
