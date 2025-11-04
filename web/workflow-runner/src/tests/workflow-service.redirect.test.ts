import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';

// Mock getLfFramework to satisfy imports in the service module
vi.mock('@lf-widgets/framework', () => ({
  getLfFramework: () => ({
    syntax: { json: { parse: async () => null } },
  }),
}));

import { fetchWorkflowDefinitions } from '../services/workflow-service';
import { API_BASE } from '../config';

// Narrowly-typed test alias for globalThis to avoid `as any` in tests.
const G = globalThis as unknown as {
  location?: { href?: string; origin?: string };
  window?: unknown;
  fetch?: unknown;
};

describe('workflow-service redirect on 401', () => {
  const realFetch = globalThis.fetch;
  let origHref = '';

  beforeEach(() => {
    // Preserve original href if present and ensure a mutable location for node env
    origHref = G.location?.href ?? '';
    if (!G.location) {
      // Provide a minimal location object for non-jsdom environments
      G.location = {
        href: `${'http://localhost'}/app/`,
        origin: 'http://localhost',
      };
    } else {
      G.location.href = `${G.location.origin}/app/`;
    }
    // Provide a window alias for modules that reference window directly
    if (!G.window) {
      G.window = globalThis;
    }
  });

  afterEach(() => {
    globalThis.fetch = realFetch;
    try {
      if (G.location) G.location.href = origHref;
    } catch (e) {
      // ignore
    }
    try {
      delete (G as unknown as Record<string, unknown>).window;
    } catch (e) {}
    vi.restoreAllMocks();
  });

  it('navigates to controller login page when server returns 401', async () => {
    // mock fetch to return an object with status 401
    globalThis.fetch = vi.fn().mockResolvedValue({ status: 401 });

    await expect(fetchWorkflowDefinitions()).rejects.toThrow();

    const expected = `${G.location?.origin}${API_BASE}/workflow-runner`;
    expect(G.location?.href).toBe(expected);
  });
});
