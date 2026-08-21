import { describe, expect, it } from 'vitest';
import {
  enumerateIdentities,
  enumerateIdentitiesAndLabels,
  materializeMissingIds,
  rewriteReferencesAtPaths,
  transformVnClipboard,
} from './visualNovel';

const generator = () => {
  let index = 0;
  return (kind: string) => `lf:${kind}:test-${++index}`;
};

const scenePaths = [
  { path: '/beats/*', kind: 'beat' },
  { path: '/choices/*', kind: 'choice', label: 'label' },
  { path: '/choices/*/effects/*', kind: 'effect' },
  { path: '/artRequests/*', kind: 'art-request' },
] as const;

describe('VN JSON identity helpers', () => {
  it('materializes configured paths and enumerates IDs with labels without mutating input', () => {
    const body = {
      beats: [{ text: 'A beat' }],
      choices: [{ label: 'Continue' }],
      effects: [],
      artRequests: [],
    };

    const materialized = materializeMissingIds(body, scenePaths, generator());

    expect(materialized).toEqual({
      beats: [{ text: 'A beat', id: 'lf:beat:test-1' }],
      choices: [{ label: 'Continue', id: 'lf:choice:test-2' }],
      effects: [],
      artRequests: [],
    });
    expect(Object.prototype.hasOwnProperty.call(body.beats[0], 'id')).toBe(false);
    expect(enumerateIdentities(materialized, scenePaths)).toEqual([
      { id: 'lf:beat:test-1', kind: 'beat', path: '/beats/0' },
      { id: 'lf:choice:test-2', kind: 'choice', path: '/choices/0', label: 'Continue' },
    ]);
    expect(enumerateIdentitiesAndLabels(materialized, scenePaths)).toEqual(
      enumerateIdentities(materialized, scenePaths),
    );
  });

  it('rewrites only explicitly configured narrative reference paths', () => {
    const value = {
      choices: [{
        nextSceneId: 'scene.old',
        effects: [{ payload: { nextSceneId: 'scene.old' } }],
      }],
      metadata: { targetSceneId: 'scene.old' },
      label: 'scene.old',
    };

    expect(rewriteReferencesAtPaths(
      value,
      new Map([['scene.old', 'scene.new']]),
      ['/choices/*/nextSceneId'],
    )).toEqual({
      choices: [{
        nextSceneId: 'scene.new',
        effects: [{ payload: { nextSceneId: 'scene.old' } }],
      }],
      metadata: { targetSceneId: 'scene.old' },
      label: 'scene.old',
    });
    expect(value.choices[0].nextSceneId).toBe('scene.old');
  });
});

describe('transformVnClipboard', () => {
  it('freshens all copied VN identities and rewrites forward/internal refs', () => {
    const payload = {
      nodes: [
        {
          type: 'LF_VNState',
          widgets_values_named: {
            fixture_id: 'fixture.old',
            state_body: '{"markers":[]}',
            profile_ref: 'profile.external',
          },
        },
        {
          type: 'LF_SceneSpec',
          widgets_values_named: {
            scene_id: 'scene.opening',
            title: 'Opening',
            scene_body: JSON.stringify({
              beats: [{ text: 'Start' }],
              choices: [{
                label: 'Continue',
                effects: [{ payload: { nextSceneId: 'scene.opening' } }],
                nextSceneId: 'scene.follow-up',
              }],
              effects: [],
              artRequests: [{ description: 'A ridge' }],
              metadata: { targetSceneId: 'scene.opening' },
            }),
          },
        },
        {
          type: 'LF_VNSwitch',
          widgets_values_named: {
            switch_id: 'switch.route',
            switch_body: JSON.stringify({
              cases: [{ targetSceneId: 'scene.opening' }],
              fallback: { targetSceneId: 'scene.external' },
            }),
          },
        },
        {
          type: 'LF_VNCompile',
          widgets_values_named: {
            workflow_id: 'workflow.old',
            entry_scene_id: 'scene.opening',
            selected_choice_id: 'choice.old',
            ui_widget: 'keep this output',
          },
        },
      ],
      untouched: { text: 'scene.opening' },
    };

    const result = transformVnClipboard(payload, { generateId: generator() });
    const state = result.nodes?.[0];
    const scene = result.nodes?.[1];
    const route = result.nodes?.[2];
    const compile = result.nodes?.[3];
    const sceneBody = JSON.parse(scene?.widgets_values_named?.scene_body as string) as Record<string, any>;
    const switchBody = JSON.parse(route?.widgets_values_named?.switch_body as string) as Record<string, any>;

    expect(state?.widgets_values_named?.fixture_id).toBe('lf:fixture:test-1');
    expect(state?.widgets_values_named?.profile_ref).toBe('profile.external');
    expect(scene?.widgets_values_named?.scene_id).toBe('lf:scene:test-2');
    expect(sceneBody.beats[0].id).toBe('lf:beat:test-5');
    expect(sceneBody.choices[0].id).toBe('lf:choice:test-6');
    expect(sceneBody.choices[0].nextSceneId).toBe('scene.follow-up');
    expect(sceneBody.choices[0].effects[0].id).toBe('lf:effect:test-7');
    expect(sceneBody.choices[0].effects[0].payload.nextSceneId).toBe('scene.opening');
    expect(sceneBody.metadata.targetSceneId).toBe('scene.opening');
    expect(sceneBody.artRequests[0].id).toBe('lf:art-request:test-8');
    expect(route?.widgets_values_named?.switch_id).toBe('lf:switch:test-3');
    expect(switchBody.cases[0].id).toBe('lf:switch-case:test-9');
    expect(switchBody.cases[0].targetSceneId).toBe('lf:scene:test-2');
    expect(switchBody.fallback.targetSceneId).toBe('scene.external');
    expect(compile?.widgets_values_named).toMatchObject({
      workflow_id: 'lf:workflow:test-4',
      entry_scene_id: 'lf:scene:test-2',
      selected_choice_id: 'choice.old',
      ui_widget: 'keep this output',
    });
    expect(result.untouched).toEqual({ text: 'scene.opening' });
    expect(payload.nodes?.[1].widgets_values_named?.scene_id).toBe('scene.opening');
  });

  it('rewrites selected choices when the copied scene contains that choice', () => {
    const payload = {
      nodes: [
        {
          type: 'LF_SceneSpec',
          widgets_values: [
            'scene.old',
            'Opening',
            JSON.stringify({
              beats: [],
              choices: [{ id: 'choice.old', label: 'Go', nextSceneId: 'scene.next' }],
              effects: [],
              artRequests: [],
            }),
          ],
        },
        {
          type: 'LF_SceneSpec',
          widgets_values: ['scene.next', 'Next', JSON.stringify({ beats: [], choices: [], effects: [], artRequests: [] })],
        },
        {
          type: 'LF_VNCompile',
          widgets_values: ['workflow.old', 'scene.old', 'choice.old', 'ui'],
        },
      ],
    };

    const result = transformVnClipboard(payload, { generateId: generator() });
    expect(result.nodes?.[0].widgets_values).toEqual([
      'lf:scene:test-1',
      'Opening',
      JSON.stringify({
        beats: [],
        choices: [{ id: 'lf:choice:test-4', label: 'Go', nextSceneId: 'lf:scene:test-2' }],
        effects: [],
        artRequests: [],
      }),
    ]);
    expect(result.nodes?.[2].widgets_values).toEqual([
      'lf:workflow:test-3',
      'lf:scene:test-1',
      'lf:choice:test-4',
      'ui',
    ]);
  });

  it('transforms nodes inside copied subgraphs and preserves external refs', () => {
    const payload = {
      nodes: [],
      subgraphs: [
        {
          nodes: [
            {
              type: 'LF_SceneSpec',
              widgets_values_named: {
                scene_id: 'scene.nested',
                title: 'Nested',
                scene_body: JSON.stringify({
                  beats: [],
                  choices: [{ id: 'choice.nested', nextSceneId: 'scene.not-copied' }],
                  effects: [],
                  artRequests: [],
                }),
              },
            },
          ],
        },
      ],
    };

    const result = transformVnClipboard(payload, { generateId: generator() });
    const nested = result.subgraphs?.[0].nodes?.[0];
    const body = JSON.parse(nested?.widgets_values_named?.scene_body as string) as Record<string, any>;
    expect(nested?.widgets_values_named?.scene_id).toBe('lf:scene:test-1');
    expect(body.choices[0].id).toBe('lf:choice:test-2');
    expect(body.choices[0].nextSceneId).toBe('scene.not-copied');
  });

  it('preserves duplicate identity evidence for structured compiler diagnostics', () => {
    const payload = {
      nodes: [
        {
          type: 'LF_SceneSpec',
          widgets_values: ['scene.duplicate', 'First', '{"beats":[],"choices":[],"artRequests":[]}'],
        },
        {
          type: 'LF_SceneSpec',
          widgets_values: ['scene.duplicate', 'Second', '{"beats":[],"choices":[],"artRequests":[]}'],
        },
      ],
    };

    const result = transformVnClipboard(payload, { generateId: generator() });
    expect(result.nodes?.[0].widgets_values?.[0]).toBe('lf:scene:test-1');
    expect(result.nodes?.[1].widgets_values?.[0]).toBe('lf:scene:test-1');
  });
});
