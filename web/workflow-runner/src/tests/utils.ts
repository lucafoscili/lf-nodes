export class EventSourceMock {
  onopen: ((ev: any) => any) | null = null;
  onerror: ((ev: any) => any) | null = null;
  onmessage: ((ev: any) => any) | null = null;
  private listeners = new Map<string, Set<(e: any) => void>>();
  closed = false;

  constructor(public url: string) {}

  addEventListener(type: string, cb: (e: any) => void) {
    if (!this.listeners.has(type)) this.listeners.set(type, new Set());
    this.listeners.get(type)!.add(cb);
  }
  removeEventListener(type: string, cb: (e: any) => void) {
    this.listeners.get(type)?.delete(cb);
  }
  close() {
    this.closed = true;
  }

  emit(type: string, data: any) {
    const payload = { data: typeof data === 'string' ? data : JSON.stringify(data) };
    if ((type === 'message' || type === 'message') && this.onmessage)
      this.onmessage(payload as any);
    this.listeners.get(type)?.forEach((cb) => cb(payload as any));
  }
  open() {
    this.onopen?.({});
  }
  error() {
    this.onerror?.({});
  }
}
