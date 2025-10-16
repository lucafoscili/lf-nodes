export interface WorkflowState {
  ui: {
    buttons: {
      run: HTMLLfButtonElement | null;
    };
    fields: {
      workflow: HTMLSelectElement | null;
    };
    labels: {
      workflow: HTMLLabelElement | null;
    };
    sections: {
      fields: HTMLElement | null;
      result: HTMLElement | null;
      status: HTMLElement | null;
      workflow: HTMLElement | null;
    };
    title: HTMLHeadingElement | null;
  };
  workflows: any[];
}
