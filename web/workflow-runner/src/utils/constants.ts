//#region Debug messages
export const DEBUG_MESSAGES = {
  ACTION_BUTTON_DESTROYED: 'Action button section destroyed.',
  ACTION_BUTTON_MOUNTED: 'Action button section mounted.',
  ACTION_BUTTON_UPDATED: 'Action button section refreshed.',
  DEV_SECTION_DESTROYED: 'Dev section destroyed.',
  DEV_SECTION_MOUNTED: 'Dev section mounted.',
  DEV_SECTION_UPDATED: 'Dev section refreshed.',
  DRAWER_DESTROYED: 'Drawer section destroyed.',
  DRAWER_MOUNTED: 'Drawer section mounted.',
  DRAWER_UPDATED: 'Drawer section refreshed.',
  HEADER_DESTROYED: 'Header section destroyed.',
  HEADER_MOUNTED: 'Header section mounted.',
  HEADER_UPDATED: 'Header section refreshed.',
  INPUTS_COLLECTED: 'Collected workflow inputs.',
  MAIN_DESTROYED: 'Main section destroyed.',
  MAIN_MOUNTED: 'Main section mounted.',
  MAIN_UPDATED: 'Main section refreshed.',
  NOTIFICATIONS_DESTROYED: 'Notifications section destroyed.',
  NOTIFICATIONS_MOUNTED: 'Notifications section mounted.',
  NOTIFICATIONS_UPDATED: 'Notifications section refreshed.',
  WORKFLOW_INPUT_FLAGGED: 'Workflow input flagged.',
  WORKFLOW_INPUTS_DESTROYED: 'Workflow inputs destroyed.',
  WORKFLOW_INPUTS_MOUNTED: 'Workflow inputs mounted.',
  WORKFLOW_INPUTS_UPDATED: 'Workflow inputs refreshed.',
  WORKFLOW_OUTPUTS_DESTROYED: 'Workflow outputs destroyed.',
  WORKFLOW_OUTPUTS_MOUNTED: 'Workflow outputs mounted.',
  WORKFLOW_OUTPUTS_UPDATED: 'Workflow outputs refreshed.',
  WORKFLOW_RESULTS_DESTROYED: 'Workflow results destroyed.',
  WORKFLOW_RESULTS_MOUNTED: 'Workflow results mounted.',
  WORKFLOW_RESULTS_UPDATED: 'Workflow results refreshed.',
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

//#region Notifications messages
export const NOTIFICATION_MESSAGES = {
  NO_WORKFLOWS_AVAILABLE: 'No workflows available from the API.',
  NO_WORKFLOW_SELECTED: 'No workflow selected.',
  WORKFLOW_CANCELLED: 'Workflow run cancelled.',
  WORKFLOW_COMPLETED: 'Workflow execution completed successfully.',
  WORKFLOW_STATUS_FAILED: 'Failed to fetch workflow status.',
  WORKFLOWS_LOAD_FAILED: 'Failed to load workflows.',
} as const;
//#endregion

//#region Status messages
export const STATUS_MESSAGES = {
  ERROR_FETCHING_WORKFLOW: 'Error fetching workflow!',
  ERROR_FETCHING_WORKFLOWS: 'Error fetching workflows!',
  ERROR_RUNNING_WORKFLOW: 'Error running workflow!',
  ERROR_UPLOADING_FILE: 'Error uploading file!',
  IDLE: 'Idle',
  IDLE_WORKFLOWS_LOADED: 'Workflows loaded',
  RUNNING_DISPATCHING_WORKFLOW: 'Dispatching workflow...',
  RUNNING_INITIALIZING: 'Initializing...',
  RUNNING_LOADING_WORKFLOWS: 'Loading workflows...',
  RUNNING_POLLING_WORKFLOW: 'Processing workflow...',
  RUNNING_SUBMITTING_WORKFLOW: 'Submitting workflow...',
  RUNNING_UPLOAD_COMPLETED: 'File uploaded...',
  RUNNING_UPLOADING_FILE: 'Uploading file...',
} as const;
//#endregion
