/**
 * LEGACY INGESTION PATH - REMOVED
 *
 * This module has been replaced by WorkflowRunnerClient (client.ts).
 * WorkflowRunnerClient is now the single source of truth for run state ingestion.
 *
 * If you see imports of this module, they should be removed and replaced with
 * WorkflowRunnerClient instantiation at the manager level.
 *
 * See: WORKFLOW_RUNNER_CLIENT_ANALYSIS.md for migration details.
 */

// Stub exports to prevent breaking existing imports during migration
export const createRealtimeController = () => {
  console.warn(
    '[DEPRECATED] createRealtimeController is deprecated. Use WorkflowRunnerClient instead.',
  );
  return {
    startRealtimeUpdates: () => {},
    stopRealtimeUpdates: () => {},
  };
};
