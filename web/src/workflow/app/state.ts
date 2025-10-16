import { WorkflowState } from '../../types/workflow/state';

export const initState = (): WorkflowState => ({
  ui: {
    buttons: {
      run: null as HTMLLfButtonElement | null,
    },
    fields: {
      workflow: null as HTMLSelectElement | null,
    },
    labels: {
      workflow: null as HTMLLabelElement | null,
    },
    sections: {
      fields: null as HTMLElement | null,
      result: null as HTMLElement | null,
      status: null as HTMLElement | null,
      workflow: null as HTMLElement | null,
    },
    title: null as HTMLHeadingElement | null,
  },
  workflows: [] as any[],
});
