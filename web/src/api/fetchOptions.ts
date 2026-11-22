/**
 * fetchApi options for a call that can outlast the ComfyUI frontend's default abort: since
 * frontend 1.59 every call is aborted after 60 s unless `timeoutMs` is null (a caller's own
 * `signal` is combined with that timeout, not a replacement for it). Older frontends ignore the key.
 */
export const UNBOUNDED_FETCH = { timeoutMs: null } as const;
