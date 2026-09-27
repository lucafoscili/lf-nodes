interface ComfyFileUrlApi {
  fileURL(route: string): string;
}

interface ExtensionUrlOptions {
  api?: Partial<ComfyFileUrlApi>;
  href?: string;
}

const LF_EXTENSION_PATH = 'extensions/lf-nodes';

/** Resolve an LF extension file without inheriting the active tab's query or hash. */
export const resolveLfExtensionUrl = (
  relativePath: string,
  options: ExtensionUrlOptions = {},
): string => {
  const href = options.href ?? window.location.href;
  const suffix = relativePath.replace(/^\/+/, '');
  const extensionPath = `${LF_EXTENSION_PATH}/${suffix}`;
  const route = `/${extensionPath}`;
  const resolved = options.api?.fileURL?.(route) ?? extensionPath;

  return new URL(resolved, href).href;
};
