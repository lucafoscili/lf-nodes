import { MasonryAudioFile, MasonryCSS, MasonryState } from '../types/widgets/masonry';

const normalizeAudioFiles = (value: unknown[]): MasonryAudioFile[] =>
  value.flatMap((item) => {
    if (!item || typeof item !== 'object') return [];
    const file = item as Partial<MasonryAudioFile>;
    if (
      typeof file.filename !== 'string' ||
      !file.filename ||
      typeof file.subfolder !== 'string' ||
      file.type !== 'output'
    ) {
      return [];
    }
    return [{ filename: file.filename, subfolder: file.subfolder, type: 'output' as const }];
  });

export const releaseAudioPreview = (masonry: HTMLLfMasonryElement): void => {
  masonry.querySelectorAll('audio').forEach((audio) => {
    audio.pause();
    audio.removeAttribute('src');
    audio.load();
  });
};

/** Render output references as native controls, never as backend-supplied HTML or media bytes. */
export const setMasonryAudio = (state: MasonryState, value: unknown[]): void => {
  const files = normalizeAudioFiles(value);
  // Live LF events and Comfy's executed event carry the same final payload.
  // Reusing the controls prevents a second delivery from resetting playback.
  if (
    JSON.stringify(files) === JSON.stringify(state.audio) &&
    state.masonry.querySelectorAll('audio[src]').length === files.length
  ) {
    return;
  }

  const { masonry } = state;
  releaseAudioPreview(masonry);
  masonry.replaceChildren();
  state.audio = files;
  masonry.lfShape = 'slot';
  masonry.lfDataset = {
    nodes: files.map((file, index) => {
      const slotName = `lf-audio-${index}`;
      const reference = [file.subfolder, file.filename].filter(Boolean).join('/');
      const url = `/view?${new URLSearchParams({ ...file })}`;
      const slot = document.createElement('div');
      slot.slot = slotName;
      slot.classList.add(MasonryCSS.Slot);
      slot.style.padding = '8px';
      slot.style.boxSizing = 'border-box';

      const label = document.createElement('a');
      label.textContent = reference;
      label.href = url;
      label.download = file.filename;
      label.title = `Download ${reference}`;
      label.style.display = 'block';
      label.style.overflowWrap = 'anywhere';
      label.style.marginBottom = '6px';
      label.style.color = 'inherit';

      const audio = document.createElement('audio');
      audio.controls = true;
      audio.preload = 'metadata';
      audio.src = url;
      audio.setAttribute('aria-label', reference);
      audio.style.display = 'block';
      audio.style.width = '100%';
      audio.style.minWidth = '0';
      slot.append(label, audio);
      masonry.appendChild(slot);

      return {
        id: slotName,
        value: reference,
        cells: { lfSlot: { shape: 'slot' as const, value: slotName } },
      };
    }),
  };
};

type AudioOutputNode = NodeType & {
  onExecuted?: (output: unknown, ...args: unknown[]) => unknown;
};

/** Comfy invokes onExecuted for both fresh execution and restored history outputs. */
export const installAudioPreviewHistory = (
  node: AudioOutputNode,
  apply: (audio: unknown[]) => void,
): void => {
  const previous = node.onExecuted;
  node.onExecuted = function (output, ...args) {
    const result = previous?.apply(this, [output, ...args]);
    if (!output || typeof output !== 'object') return result;

    const payload = output as { lf_output?: Array<{ audio?: unknown[] }>; audio?: unknown[] };
    const entries = Array.isArray(payload.lf_output)
      ? payload.lf_output.filter((entry) => entry && Array.isArray(entry.audio))
      : [];
    if (entries.length) {
      apply(entries.flatMap((entry) => entry.audio));
    } else if (Array.isArray(payload.audio)) {
      apply(payload.audio);
    }
    return result;
  };
};
