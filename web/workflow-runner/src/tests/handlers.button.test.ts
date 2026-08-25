import type { LfButtonEventPayload } from '@lf-widgets/foundations/dist';
import { describe, expect, it, vi } from 'vitest';
import { DRAWER_CLASSES } from '../elements/layout.drawer';
import { ACTION_BUTTON_CLASSES } from '../elements/layout.action-button';
import { buttonHandler } from '../handlers/button';
import type { WorkflowStore } from '../types/state';

vi.mock('../utils/comfy-url', () => ({
  resolveComfyUrl: vi.fn(() => 'http://runner.example.test:8188/'),
}));

describe('buttonHandler', () => {
  it('routes the floating control to exact cancellation while a run is active', () => {
    const cancelWorkflow = vi.fn(async () => undefined);
    const runWorkflow = vi.fn(async () => undefined);
    const event = {
      detail: {
        eventType: 'click',
        comp: {
          rootElement: {
            className: ACTION_BUTTON_CLASSES._,
          },
        },
      },
    } as unknown as CustomEvent<LfButtonEventPayload>;
    const store = {
      getState: () => ({
        currentRunId: 'run-owned',
        manager: { getDispatchers: () => ({ cancelWorkflow, runWorkflow }) },
        runs: [{ runId: 'run-owned', status: 'running' }],
        submissionInFlightId: null,
        view: 'workflow',
      }),
    } as unknown as WorkflowStore;

    buttonHandler(event, store);

    expect(cancelWorkflow).toHaveBeenCalledOnce();
    expect(runWorkflow).toHaveBeenCalledTimes(0);
  });

  it('opens the resolved ComfyUI URL from the drawer without opener access', () => {
    const open = vi.spyOn(window, 'open').mockReturnValue(null);
    const event = {
      detail: {
        eventType: 'click',
        comp: {
          rootElement: { className: DRAWER_CLASSES.buttonComfyUi },
        },
      },
    } as unknown as CustomEvent<LfButtonEventPayload>;
    const store = {
      getState: () => ({ manager: {}, view: 'workflow' }),
    } as unknown as WorkflowStore;

    buttonHandler(event, store);

    expect(open).toHaveBeenCalledOnce();
    expect(open).toHaveBeenCalledWith(
      'http://runner.example.test:8188/',
      '_blank',
      'noopener,noreferrer',
    );
  });
});
