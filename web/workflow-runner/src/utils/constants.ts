//#region Debug messages
export const DEBUG_MESSAGES = {
  DRAWER_DESTROYED: 'Drawer section destroyed.',
  DRAWER_MOUNTED: 'Drawer section mounted.',
  DRAWER_UPDATED: 'Drawer dataset refreshed.',
  INPUTS_COLLECTED: 'Collected workflow inputs.',
  INPUTS_FAILED: 'Failed to collect workflow inputs.',
  MAIN_DESTROYED: 'Main content destroyed.',
  MAIN_MOUNTED: 'Main content mounted.',
  STATUS_UPDATED: 'Workflow status updated.',
  UPLOAD_COMPLETED: 'Upload completed.',
  UPLOAD_FAILED: 'Upload failed.',
  UPLOAD_FAILED_UNEXPECTED: 'Upload failed unexpectedly.',
  WORKFLOW_COMPLETED: 'Workflow execution completed.',
  WORKFLOW_DISPATCHING: 'Dispatching workflow execution.',
  WORKFLOW_FAILED: 'Workflow execution failed.',
  WORKFLOW_FAILED_UNEXPECTED: 'Workflow execution failed unexpectedly.',
  WORKFLOW_LAYOUT_DESTROYED: 'Workflow layout destroyed.',
  WORKFLOW_LAYOUT_MOUNTED: 'Workflow layout mounted.',
  WORKFLOW_INPUT_FLAGGED: 'Workflow input flagged.',
  WORKFLOW_INPUTS_CLEARED: 'Workflow inputs cleared.',
  WORKFLOW_INPUTS_RENDERED: 'Workflow inputs rendered.',
  WORKFLOW_NOT_SELECTED: 'No workflow selected.',
  WORKFLOW_RESULTS_CLEARED: 'Workflow results cleared.',
  WORKFLOW_RESULTS_RENDERED: 'Workflow results rendered.',
  WORKFLOW_SELECTED: 'Workflow selected.',
  WORKFLOWS_LOAD_FAILED: 'Failed to load workflows.',
  WORKFLOWS_LOADED: 'Workflow definitions loaded.',
} as const;
//#endregion

//#region Error messages
export const ERROR_MESSAGES = {
  RUN_GENERIC: 'Workflow execution failed.',
  UPLOAD_GENERIC: 'Upload failed.',
  UPLOAD_INVALID_RESPONSE: 'Invalid response shape from upload API.',
  UPLOAD_MISSING_FILE: 'Missing file to upload.',
} as const;
//#endregion

//#region Status messages
export const STATUS_MESSAGES = {
  FILE_PROCESSING: 'File uploaded, processing...',
  LOADING_WORKFLOWS: 'Loading workflows...',
  SUBMITTING_WORKFLOW: 'Submitting workflow...',
  UPLOAD_COMPLETED: 'Upload completed successfully.',
  UPLOADING_FILE: 'Uploading file...',
  WORKFLOW_COMPLETED: 'Workflow execution completed successfully.',
  WORKFLOWS_LOADED: 'Workflows loaded.',
} as const;
//#endregion
