//#region Debug
export const DEBUG_MESSAGES = {
  WORKFLOWS_LOAD_FAILED: 'Failed to load workflows.',
  WORKFLOWS_LOADED: 'Workflow definitions loaded.',
  WORKFLOW_SELECTED: 'Workflow selected.',
  STATUS_UPDATED: 'Workflow status updated.',
  INPUTS_COLLECTED: 'Collected workflow inputs.',
  INPUTS_FAILED: 'Failed to collect workflow inputs.',
  WORKFLOW_DISPATCHING: 'Dispatching workflow execution.',
  WORKFLOW_COMPLETED: 'Workflow execution completed.',
  WORKFLOW_FAILED: 'Workflow execution failed.',
  WORKFLOW_FAILED_UNEXPECTED: 'Workflow execution failed unexpectedly.',
  UPLOAD_COMPLETED: 'Upload completed.',
  UPLOAD_FAILED: 'Upload failed.',
  UPLOAD_FAILED_UNEXPECTED: 'Upload failed unexpectedly.',
  DRAWER_MOUNTED: 'Drawer section mounted.',
  DRAWER_UPDATED: 'Drawer dataset refreshed.',
  DRAWER_DESTROYED: 'Drawer section destroyed.',
  MAIN_MOUNTED: 'Main content mounted.',
  MAIN_DESTROYED: 'Main content destroyed.',
  WORKFLOW_LAYOUT_MOUNTED: 'Workflow layout mounted.',
  WORKFLOW_LAYOUT_DESTROYED: 'Workflow layout destroyed.',
  WORKFLOW_INPUTS_RENDERED: 'Workflow inputs rendered.',
  WORKFLOW_INPUTS_CLEARED: 'Workflow inputs cleared.',
  WORKFLOW_RESULTS_RENDERED: 'Workflow results rendered.',
  WORKFLOW_RESULTS_CLEARED: 'Workflow results cleared.',
  WORKFLOW_INPUT_FLAGGED: 'Workflow input flagged.',
} as const;
//#endregion

//#region Status
export const STATUS_MESSAGES = {
  LOADING_WORKFLOWS: 'Loading workflows...',
  WORKFLOWS_LOADED: 'Workflows loaded.',
  SUBMITTING_WORKFLOW: 'Submitting workflow...',
  UPLOADING_FILE: 'Uploading file...',
  FILE_PROCESSING: 'File uploaded, processing...',
} as const;
//#endregion
