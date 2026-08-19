export type InputPrefillCell = HTMLElement & {
  getHistory?: () => Promise<unknown>;
  setHistory?: (...args: any[]) => Promise<void> | void;
  setValue?: (...args: any[]) => Promise<void> | void;
  lfDataset?: {
    nodes?: InputPrefillNode[];
  };
  lfValue?: unknown;
};

type InputPrefillNode = {
  id: string;
  value?: string | number;
  workflowValue?: string | number;
  children?: InputPrefillNode[];
};

const findSelectNodeId = (
  nodes: InputPrefillNode[] | undefined,
  workflowValue: unknown,
): string | undefined => {
  let displayFallback: string | undefined;
  const visit = (items: InputPrefillNode[] | undefined): string | undefined => {
    for (const node of items || []) {
      if (node.workflowValue === workflowValue) {
        return node.id;
      }
      if (
        displayFallback === undefined &&
        (node.value === workflowValue || node.id === String(workflowValue))
      ) {
        displayFallback = node.id;
      }
      const childMatch = visit(node.children);
      if (childMatch) {
        return childMatch;
      }
    }
    return undefined;
  };

  return visit(nodes) ?? displayFallback;
};

/** Restore replayable controls from a prior run without replaying uploads. */
export const applyInputPrefill = async (
  cells: InputPrefillCell[],
  inputs: Record<string, unknown>,
): Promise<void> => {
  for (const cell of cells) {
    const id = cell.id;
    if (!id || !Object.prototype.hasOwnProperty.call(inputs, id)) {
      continue;
    }

    const value = inputs[id];
    try {
      switch (cell.tagName.toLowerCase()) {
        case 'lf-upload':
          continue;
        case 'lf-chat': {
          const history = typeof value === 'string' ? value : JSON.stringify(value ?? []);
          if (typeof cell.setHistory === 'function') {
            await cell.setHistory(history);
          }
          break;
        }
        case 'lf-select': {
          // Runs store the semantic workflowValue, while lf-select restores by
          // its UI node id. Resolve the current definition so friendly option
          // ids may evolve independently from the submitted value.
          const selectedId = findSelectNodeId(cell.lfDataset?.nodes, value) ?? String(value ?? '');
          if (typeof cell.setValue === 'function') {
            await cell.setValue(selectedId);
          } else {
            cell.lfValue = selectedId;
          }
          break;
        }
        case 'lf-toggle': {
          const enabled = value === true || value === 'on' || value === 1;
          if (typeof cell.setValue === 'function') {
            await cell.setValue(enabled ? 'on' : 'off');
          } else {
            cell.lfValue = enabled;
          }
          break;
        }
        default: {
          const text = value === null || value === undefined ? '' : String(value);
          if (typeof cell.setValue === 'function') {
            await cell.setValue(text);
          } else {
            cell.lfValue = text;
          }
        }
      }
    } catch {
      // A retired/malformed input must not prevent the rest of the form from
      // being restored. The normal form defaults remain available to the user.
    }
  }
};
