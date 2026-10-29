import { describe, expect, it, vi } from 'vitest';

import { parseArgs, resetExecutionCache } from '../titanic_e2e.mts';

import {
  classifyHistoryEntry,
  buildCasePayloads,
  buildCpuFixturePromptBindings,
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
  findComfyArgv,
  normalizeExecutionTargetIds,
  parseQueueSnapshot,
  requiredFlagsForResourceClass,
  selectOwnedSubmissionPromptId,
  timedOutTerminalClassification,
  unwrapHistoryEntry,
  validateCaseOutputs,
  validatePreviewAssetBytes,
  validateLivePreviewWidget,
  validateCoverage,
  validateExecutionTrace,
  validateEditorClientBinding,
  validateLifecycleModelFixture,
  validateLoadedModelFixture,
  type TitanicManifest,
} from '../titanic_e2e_core.ts';

describe('Titanic E2E pure contracts', () => {
  it('keeps cache reset explicit and independent of warm-cache acceptance', () => {
    expect(parseArgs([])).toMatchObject({ resetCache: false, acceptWarmCache: false });
    expect(parseArgs(['--full', '--accept-warm-cache'])).toMatchObject({ resetCache: false, acceptWarmCache: true });
    expect(parseArgs(['--full', '--reset-cache'])).toMatchObject({ resetCache: true, acceptWarmCache: false });
  });

  it.each([
    { cached: [false, true, false], succeeds: true },
    { cached: [false, true, true, false], succeeds: true },
    { cached: [false, true, true, true, true], succeeds: false },
  ])('waits for the warmed probe to become uncached: $cached', async ({ cached, succeeds }) => {
    const requests: string[] = [];
    const prompts: unknown[] = [];
    let promptIndex = -1;
    let value: string;
    vi.stubGlobal('fetch', vi.fn(async (url: string, init?: RequestInit) => {
      const path = new URL(url).pathname;
      requests.push(path);
      let response: unknown = {};
      if (path === '/queue') response = { queue_running: [], queue_pending: [] };
      else if (path === '/prompt') {
        const { prompt } = JSON.parse(String(init?.body));
        prompts.push(prompt);
        value = prompt.lf_cache_probe.inputs.string;
        promptIndex += 1;
        response = { prompt_id: `probe-${promptIndex}` };
      } else if (path.startsWith('/history/')) {
        const promptId = `probe-${promptIndex}`;
        response = { [promptId]: {
          outputs: { lf_cache_probe: { lf_output: [{ string: value }] } },
          status: { status_str: 'success', completed: true, messages: [
            ['execution_cached', { prompt_id: promptId, nodes: cached[promptIndex] ? ['lf_cache_probe'] : [] }],
          ] },
        } };
      } else if (path === '/free') {
        expect(init?.method).toBe('POST');
        expect(JSON.parse(String(init?.body))).toEqual({ free_memory: true });
        expect(prompts).toHaveLength(2);
      } else throw new Error(`unexpected request ${path}`);
      return new Response(JSON.stringify(response), { status: 200 });
    }));
    try {
      const reset = resetExecutionCache('http://comfy.test');
      if (succeeds) {
        const result = await reset;
        expect(result.probes.map((probe) => probe.cached)).toEqual(cached);
        expect(result.unloadsModels).toBe(true);
      } else {
        await expect(reset).rejects.toThrow('remained cached after /free');
      }
      expect(requests.filter((path) => path === '/free')).toHaveLength(1);
      expect(prompts).toHaveLength(cached.length);
      expect(prompts.every((prompt) => JSON.stringify(prompt) === JSON.stringify(prompts[0]))).toBe(true);
    } finally {
      vi.unstubAllGlobals();
    }
  });

  it('captures only declared final UI with node types from the submitted prompt', () => {
    const manifestCase = { id: 'cpu.payloads', execution: { requiredNodeIds: [12, 10, 12] } } as any;
    const ui = { lf_output: [{ value: 'résultat', dataset: { nodes: [] } }] };
    const nativeUi = { result: ['model.glb [temp]', null, []] };
    const submittedPrompt = {
      '10': { class_type: 'LF_DisplayJSON', inputs: { text: 'input-only' } },
      '12': { class_type: 'Preview3DAdvanced', inputs: { model_file: 'input.glb' } },
      '99': { class_type: 'LF_WriteJSON', inputs: { text: 'unrelated-input' } },
    };
    const history = {
      prompt: [0, 'owned', { '10': { class_type: 'different-history-type' } }],
      outputs: { '10': ui, '12': nativeUi, '99': { lf_output: ['unrelated-output'] } },
      workflow: { nodes: ['workflow-only'] },
      status: { completed: true, status_str: 'success' },
    };
    const before = structuredClone({ submittedPrompt, history });
    const captured = buildCasePayloads(manifestCase, submittedPrompt, history);
    expect(captured).toEqual({
      schema: 'lf.titanic-payloads.v1', caseId: 'cpu.payloads',
      nodes: [
        { nodeId: '12', nodeType: 'Preview3DAdvanced', ui: nativeUi },
        { nodeId: '10', nodeType: 'LF_DisplayJSON', ui },
      ],
    });
    expect(JSON.parse(JSON.stringify(captured))).toEqual(captured);
    expect({ submittedPrompt, history }).toEqual(before);
  });

  it('keeps terminal UI available when cached execution is rejected', () => {
    const manifestCase = { id: 'cpu.cached', execution: {
      requiredNodeIds: [10], forbiddenCachedNodeIds: [10],
    } } as any;
    const history = { outputs: { '10': { lf_output: [{ value: 'cached result' }] } } };
    expect(validateExecutionTrace(manifestCase, {
      promptId: 'owned', started: true, terminalEvent: 'execution_success',
      executedNodeIds: [], uiExecutedNodeIds: [], cachedNodeIds: ['10'],
      executingEvents: [], executedPreviewUrlsByNode: {},
    })).toEqual([
      'node 10 was not observed executing for prompt owned',
      'node 10 was served from cache for prompt owned',
    ]);
    expect(buildCasePayloads(manifestCase, { '10': { class_type: 'LF_DisplayJSON' } }, history).nodes)
      .toEqual([{ nodeId: '10', nodeType: 'LF_DisplayJSON', ui: history.outputs['10'] }]);
  });

  it('retains available UI when required headless nodes have no history UI', () => {
    const manifestCase = { id: 'cpu.missing', execution: { requiredNodeIds: [10, 12] } } as any;
    const prompt = { '10': { class_type: 'LF_DisplayJSON' }, '12': { class_type: 'LF_LoadSAM3Model' } };
    const ui = { lf_output: [{ value: 1 }] };
    for (const missing of [undefined, null, {}, [], 'not UI']) {
      expect(buildCasePayloads(manifestCase, prompt, {
        outputs: { '10': ui, '12': missing },
      }).nodes).toEqual([
        { nodeId: '10', nodeType: 'LF_DisplayJSON', ui },
        { nodeId: '12', nodeType: 'LF_LoadSAM3Model', ui: {} },
      ]);
    }
    expect(buildCasePayloads(manifestCase, prompt, undefined).nodes).toEqual([
      { nodeId: '10', nodeType: 'LF_DisplayJSON', ui: {} },
      { nodeId: '12', nodeType: 'LF_LoadSAM3Model', ui: {} },
    ]);
  });

  it('reports missing submitted node types without inventing a type', () => {
    const manifestCase = { id: 'cpu.missing', execution: { requiredNodeIds: [10, 12] } } as any;
    const prompt = { '10': { class_type: 'LF_DisplayJSON' }, '12': { class_type: 'LF_LoadSAM3Model' } };
    expect(() => buildCasePayloads(manifestCase, null, undefined)).toThrow(
      'payload capture for cpu.missing: node 10 has no submitted class_type; node 12 has no submitted class_type',
    );
    expect(() => buildCasePayloads(manifestCase, {
      ...prompt, '12': { class_type: ' ' },
    }, { outputs: { '10': { text: ['valid'] }, '12': { result: ['valid'] } } }))
      .toThrow('node 12 has no submitted class_type');
  });

  it('does not expand payload selection to expectations or targets', () => {
    expect(buildCasePayloads({ id: 'cpu.no-required', targets: [10], expect: { '10': {} } } as any,
      null, { outputs: { '10': { text: ['outside selection'] } } })).toEqual({
      schema: 'lf.titanic-payloads.v1', caseId: 'cpu.no-required', nodes: [],
    });
  });

  it('verifies the stock temporary GLB preview without treating arbitrary result strings as assets', () => {
    const output = { result: ['preview3d_advanced_aabb.glb [temp]', null, []] };
    expect(collectPreviewUrls(output)).toEqual(['/view?filename=preview3d_advanced_aabb.glb&type=temp']);
    expect(countPreviewReferences(output)).toBe(1);
    expect(validateCaseOutputs({ id: 'glb', expect: { '615': {
      minimumPreviewCount: 1, previewStorageType: 'temp',
    } } } as any, { outputs: { '615': output } })).toEqual([]);
    expect(collectPreviewUrls({ result: ['../../private.glb [temp]'] })).toEqual([]);
    const bytes = new Uint8Array(28);
    const header = new DataView(bytes.buffer);
    header.setUint32(0, 0x46546c67, true);
    header.setUint32(4, 2, true);
    header.setUint32(8, 28, true);
    expect(validatePreviewAssetBytes('model-3d', 'application/octet-stream', bytes)).toEqual([]);
    expect(validatePreviewAssetBytes('model-3d', 'model/gltf-binary', bytes.slice(0, 27))).toHaveLength(1);
    header.setUint32(8, 29, true);
    expect(validatePreviewAssetBytes('model-3d', 'model/gltf-binary', bytes)).toHaveLength(1);
    expect(validatePreviewAssetBytes('image', 'text/plain', new Uint8Array())).toHaveLength(2);
    const modelUrl = '/view?filename=preview3d_advanced_aabb.glb&type=temp';
    const live = { nodeId: 615, kind: 'model-3d' as const, found: true, hasElement: true, previewCount: 0,
      modelLoaded: true, modelUrl: '/api' + modelUrl + '&subfolder=&rand=0.25' };
    expect(validateLivePreviewWidget('615', { previewKind: 'model-3d', minimumPreviewCount: 1 }, live, [modelUrl])).toEqual([]);
    expect(validateLivePreviewWidget('615', { previewKind: 'model-3d' }, { ...live, found: false })).toEqual([
      'node 615 live native 3D viewport is not hydrated',
    ]);
    expect(validateLivePreviewWidget('615', { minimumPreviewCount: 1 }, live)).toEqual([
      'node 615 live ui_widget is not hydrated',
    ]);
    for (const missingModel of [{ ...live, modelLoaded: false }, { ...live, modelUrl: '/view?filename=other.glb&type=temp' }]) {
      expect(validateLivePreviewWidget('615', { previewKind: 'model-3d' }, missingModel, [modelUrl])).toEqual([
        'node 615 live native 3D viewport has not loaded its terminal-history model',
      ]);
    }
    expect(validateLivePreviewWidget('615', { previewKind: 'model-3d' }, { ...live, hasElement: false }, [modelUrl])).toEqual([
      'node 615 live native 3D viewport is not hydrated',
    ]);
  });
  it('counts Compare entries separately from their persistent asset references', () => {
    const url = '/view?filename=shared.png&type=input';
    const expectation = { minimumPreviewCount: 2, minimumLivePreviewCount: 1 };
    const live = { nodeId: 647, kind: 'image' as const, found: true, hasElement: true, previewCount: 1 };
    const history = { outputs: { '647': { lf_output: [{ dataset: { nodes: [{
      cells: { lfImage: { lfValue: url }, lfImage_after: { lfValue: url } },
    }] } }] } } };
    // Content-addressed storage can reuse one URL for both cells of an entry.
    expect(countPreviewReferences(history.outputs['647'])).toBe(2);
    expect(collectPreviewUrls(history.outputs['647'])).toEqual([url]);
    expect(validateCaseOutputs({ expect: { '647': expectation } } as any, history)).toEqual([]);
    expect(validateLivePreviewWidget('647', expectation, live)).toEqual([]);
    expect(validateLivePreviewWidget('647', expectation, { ...live, previewCount: 0 })).toEqual([
      'node 647 live widget has 0 previews; expected at least 1',
    ]);
    expect(validateLivePreviewWidget('647', { minimumPreviewCount: 2 }, live)).toEqual([
      'node 647 live widget has 1 previews; expected at least 2',
    ]);
    expect(validateCaseOutputs({ expect: { '647': expectation } } as any,
      { outputs: { '647': { lf_output: [{ lfValue: url }] } } })).toEqual([
      'node 647 exposed 1 preview references; expected at least 2',
    ]);
  });
  it('binds reviewed CPU fixture inputs without changing the portable prompt', () => {
    const layers = { root: 'scripts/quality/fixtures/titanic-cpu', layers: [{ file: 'lower.png' }] };
    const prompt = {
      '612': { class_type: 'LF_ApplyTextureToGLB', inputs: { source_glb: 'titanic-cpu/synthetic.glb' } },
      '622': { class_type: 'LF_WriteJSON', inputs: { ui_widget: JSON.stringify(layers) } },
    };
    const original = structuredClone(prompt);
    const bindings = { fixtureGlbSourceNodeIds: [612], fixtureLayerManifestNodeIds: [622] };
    const result = buildCpuFixturePromptBindings(prompt, bindings, '/checkout/lf-nodes/');
    expect(result).toEqual([
      { nodeId: '612', classType: 'LF_ApplyTextureToGLB', input: 'source_glb',
        value: '/checkout/lf-nodes/scripts/quality/fixtures/titanic-cpu/synthetic.glb' },
      { nodeId: '622', classType: 'LF_WriteJSON', input: 'ui_widget',
        value: JSON.stringify({ ...layers, root: '/checkout/lf-nodes/scripts/quality/fixtures/titanic-cpu' }) },
    ]);
    expect(prompt).toEqual(original);
    prompt['612'].inputs.source_glb = 'other.glb';
    expect(() => buildCpuFixturePromptBindings(prompt, bindings, '/checkout')).toThrow('GLB fixture binding node 612 drifted');
    prompt['612'].inputs.source_glb = original['612'].inputs.source_glb;
    prompt['622'].inputs.ui_widget = JSON.stringify({ ...layers, root: '/private' });
    expect(() => buildCpuFixturePromptBindings(prompt, bindings, '/checkout')).toThrow('root drifted');
    expect(buildCpuFixturePromptBindings({}, undefined, '/checkout')).toEqual([]);
  });
  it('binds the reviewed single-image SAM fixture to the selected checkout', () => {
    const prompt = { '654': { class_type: 'LF_LoadImages', inputs: {
      dir: 'scripts/quality/fixtures/titanic-sam3', load_cap: 1,
      subdir: false, dummy_output: false, copy_into_input_dir: false,
    } } };
    const original = structuredClone(prompt);
    const bindings = { fixtureImageSourceNodeIds: [654] };
    expect(buildCpuFixturePromptBindings(prompt, bindings, 'C:\\checkout\\lf-nodes\\')).toEqual([
      { nodeId: '654', classType: 'LF_LoadImages', input: 'dir',
        value: 'C:\\checkout\\lf-nodes/scripts/quality/fixtures/titanic-sam3' },
    ]);
    expect(prompt).toEqual(original);
    for (const inputs of [{ dir: '/private' }, { load_cap: 0 }, { dummy_output: true },
      { subdir: true }, { copy_into_input_dir: true }]) {
      expect(() => buildCpuFixturePromptBindings({ '654': {
        ...prompt['654'], inputs: { ...prompt['654'].inputs, ...inputs },
      } }, bindings, '/checkout')).toThrow('image fixture binding node 654 drifted');
    }
    expect(() => buildCpuFixturePromptBindings({ '654': {
      ...prompt['654'], class_type: 'LF_LoadFileOnce',
    } }, bindings, '/checkout')).toThrow('image fixture binding node 654 drifted');
  });
  it('finds only a named Comfy argv with relative, Windows, or POSIX main.py paths', () => {
    expect(findComfyArgv({ system: { argv: ['main.py', '--cache-none'] } })).toEqual([
      'main.py',
      '--cache-none',
    ]);
    expect(
      findComfyArgv({ system: { argv: ['F:\\GitHub\\ComfyUI\\main.py', '--cache-none'] } }),
    ).toEqual(['F:\\GitHub\\ComfyUI\\main.py', '--cache-none']);
    expect(
      findComfyArgv({ system: { argv: ['/opt/comfyui/main.py', '--cache-none'] } }),
    ).toEqual(['/opt/comfyui/main.py', '--cache-none']);

    expect(findComfyArgv({ values: ['main.py', '--cache-none'] })).toBeNull();
    expect(findComfyArgv({ argv: ['not-main.py', '--cache-none'] })).toBeNull();
    expect(findComfyArgv({ argv: ['main.py', 42] })).toBeNull();
  });

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

  it('asserts nested authoring state by exact named values', () => {
    const manifestCase = {
      id: 'h3',
      expect: {
        '10': {
          requiredNamedValues: {
            referenceImageCount: 2,
            method: 'prose',
            enabled: true,
            status: 'completed',
          },
        },
      },
    } as any;
    const history = {
      outputs: {
        '10': {
          lf_output: [{
            validation_report: {
              referenceImageCount: 2,
              review: { enabled: true, status: 'completed' },
              authoring: { method: 'prose' },
            },
          }],
        },
      },
    };
    expect(validateCaseOutputs(manifestCase, history)).toEqual([]);
    history.outputs['10'].lf_output[0].validation_report.review.enabled = false;
    expect(validateCaseOutputs(manifestCase, history)).toEqual([
      'node 10 exposed no "enabled" value equal to true',
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
    expect(requiredFlagsForResourceClass('local-llm-lifecycle-gpu-write')).toEqual([
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

  it('permits a downloaded lifecycle model only when instance ownership is explicit', () => {
    const unloaded = {
      models: [{
        key: 'fixture',
        type: 'llm',
        capabilities: { vision: true },
        loaded_instances: [],
      }],
    };
    expect(validateLifecycleModelFixture(unloaded, 'fixture')).toEqual([]);
    expect(
      validateLifecycleModelFixture(unloaded, 'fixture', 'already-loaded'),
    ).toEqual([
      'local instance "already-loaded" was required but the lifecycle model is unloaded',
    ]);

    const loaded = {
      models: [{
        ...unloaded.models[0],
        loaded_instances: [{ id: 'exact-instance' }],
      }],
    };
    expect(validateLifecycleModelFixture(loaded, 'fixture')).toEqual([
      'an already-loaded lifecycle model requires --local-instance-id so the exact reusable instance is explicit',
    ]);
    expect(
      validateLifecycleModelFixture(loaded, 'fixture', 'exact-instance'),
    ).toEqual([]);
    expect(
      validateLifecycleModelFixture(loaded, 'fixture', 'other-instance'),
    ).toEqual([
      'loaded instance "exact-instance" does not match "other-instance"',
    ]);
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
