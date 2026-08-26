import { ComfyFileArtifact } from '../types/api';

/** Return a same-origin Comfy `/view` URL derived only from its descriptor. */
export const artifactViewUrl = (artifact: ComfyFileArtifact): string => {
  const params = new URLSearchParams({
    filename: artifact.filename,
    subfolder: (artifact.subfolder || '').replaceAll('\\', '/'),
    type: artifact.type || 'output',
  });
  return `/view?${params.toString()}`;
};
