import {
  attachMockLocalStorage,
  createMockLocalStorage,
  restoreGlobalEventSourceMock,
  setGlobalEventSourceMock,
} from './_utils';

setGlobalEventSourceMock();

attachMockLocalStorage(createMockLocalStorage());

if (
  typeof (globalThis as unknown as { requestAnimationFrame?: unknown }).requestAnimationFrame ===
  'undefined'
) {
  Object.defineProperty(globalThis, 'requestAnimationFrame', {
    configurable: true,
    writable: true,
    value: (cb: FrameRequestCallback) => {
      return setTimeout(() => cb(Date.now()), 0) as unknown as number;
    },
  });
}

export function teardownTestGlobals() {
  restoreGlobalEventSourceMock();
}

export * from './_utils';
