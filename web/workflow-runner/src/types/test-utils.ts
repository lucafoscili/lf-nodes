/**
 * Test-only types for the workflow-runner package.
 * These are convenience typings used by Vitest helpers and mocks.
 * Kept under `src/types` so both runtime code and tests can import them.
 */
import type { RunRecord } from './client';
import type { WorkflowRunStatus } from './api';

export type SSEPayload = { data: string };
export type SSEHandler = (e: SSEPayload) => void;

export interface ResponseLike {
  ok: boolean;
  status?: number;
  json?: () => Promise<unknown>;
}

export type FetchMock = (url: string, opts?: RequestInit) => ResponseLike | Promise<ResponseLike>;

export type SeedRunInput = {
  run_id?: string;
  runId?: string;
  workflow_id?: string | null;
  workflowId?: string | null;
  workflowName?: string | null;
  status: WorkflowRunStatus;
  created_at?: number;
  createdAt?: number;
  updated_at?: number;
  updatedAt?: number;
};

export interface ClientInternals {
  lastSeq: Map<string, number>;
  runs: Map<string, RunRecord>;
  inflightReconciles: Map<string, Promise<void>>;
  processingSnapshot: boolean;
  cacheKey: string;
  workflowNames?: Map<string, string>;
}

export interface ClientInternalsMethods {
  applyEvent: (ev: RunRecord) => void;
  upsertRun: (rec: RunRecord) => void;
  reconcileRun: (runId: string) => void;
  pollActiveRuns: () => Promise<void>;
  coldLoadRuns: () => Promise<void>;
  processSnapshotArray: (arr: RunRecord[]) => void;
  saveCache: () => void;
  loadCacheIds: () => string[];
  seedPlaceholders: (ids: string[]) => void;
  start: () => Promise<void>;
  stop: () => void;
  fetchWorkflowNames?: (ids: string[]) => Promise<void>;
  setWorkflowNames?: (names: Map<string, string>) => void;
}
