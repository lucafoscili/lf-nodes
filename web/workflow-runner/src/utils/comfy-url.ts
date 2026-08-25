import {
  API_ROOT,
  DEFAULT_COMFY_UI_PORT,
  DEFAULT_COMFY_UI_PROTOCOL,
  DEFAULT_FRONTEND_PROXY_PORT,
} from '../config';

const WORKFLOW_RUNNER_PATH = `${API_ROOT}/workflow-runner`;

/**
 * Resolve the browser URL for ComfyUI's root interface.
 *
 * The runner can be served directly by ComfyUI or through the optional local
 * frontend proxy. The proxy forwards the runner/API paths but deliberately
 * does not expose ComfyUI's root page, so its port must not be used as the
 * destination for the drawer link.
 *
 * The input is explicit to keep this pure and easy to test. The current page's
 * deployment prefix (if any) is retained, while the runner route, query, and
 * fragment are removed from the destination.
 */
export const resolveComfyUrl = (
  href: string = window.location.href,
  proxyPort: string = DEFAULT_FRONTEND_PROXY_PORT,
  comfyPort: string = DEFAULT_COMFY_UI_PORT,
  comfyProtocol: string = DEFAULT_COMFY_UI_PROTOCOL,
): string => {
  const current = new URL(href);

  if (current.port === proxyPort) {
    // The local frontend proxy may terminate TLS while ComfyUI itself remains
    // HTTP. Resolve the complete backend origin instead of retaining either
    // proxy component.
    current.protocol = comfyProtocol;
    current.port = comfyPort;
  }

  const runnerIndex = current.pathname.indexOf(WORKFLOW_RUNNER_PATH);
  const runnerEnd = runnerIndex + WORKFLOW_RUNNER_PATH.length;
  if (
    runnerIndex >= 0 &&
    (runnerEnd === current.pathname.length || current.pathname[runnerEnd] === '/')
  ) {
    const deploymentPrefix = current.pathname.slice(0, runnerIndex);
    current.pathname = deploymentPrefix || '/';
  } else {
    current.pathname = '/';
  }
  current.search = '';
  current.hash = '';

  return current.toString();
};
