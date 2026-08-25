import { describe, expect, it } from 'vitest';
import { resolveComfyUrl } from '../utils/comfy-url';

describe('resolveComfyUrl', () => {
  it('opens the direct ComfyUI origin on the current host', () => {
    expect(resolveComfyUrl('http://127.0.0.1:8188/api/lf-nodes/workflow-runner')).toBe(
      'http://127.0.0.1:8188/',
    );
  });

  it('maps the frontend proxy port to the ComfyUI backend port', () => {
    expect(resolveComfyUrl('http://127.0.0.1:9188/api/lf-nodes/workflow-runner')).toBe(
      'http://127.0.0.1:8188/',
    );
  });

  it('maps an HTTPS proxy to the configured HTTP ComfyUI origin', () => {
    expect(
      resolveComfyUrl('https://[2001:db8::7]:9188/instance/api/lf-nodes/workflow-runner'),
    ).toBe('http://[2001:db8::7]:8188/instance');
  });

  it('does not rewrite an unrelated custom port', () => {
    expect(resolveComfyUrl('https://runner.example.test:9443/api/lf-nodes/workflow-runner')).toBe(
      'https://runner.example.test:9443/',
    );
  });

  it('accepts runtime port overrides without changing URL semantics', () => {
    expect(
      resolveComfyUrl(
        'http://localhost:10088/prefix/api/lf-nodes/workflow-runner',
        '10088',
        '10080',
        'https:',
      ),
    ).toBe('https://localhost:10080/prefix');
  });
});
