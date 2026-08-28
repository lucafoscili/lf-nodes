import type { LfDataDataset } from '@lf-widgets/foundations/dist';

export const hydrateSamplingSelectDataset = async (
  select: HTMLLfSelectElement,
  dataset: LfDataDataset,
  defaultValue: string,
): Promise<void> => {
  let selectedValue = '';
  try {
    const selectedNode = await select.getValue();
    selectedValue = String(selectedNode?.id ?? '');
  } catch {
    // A not-yet-upgraded custom element has no readable selection. The
    // declared filter default remains the safe fallback below.
  }

  select.lfDataset = dataset;

  const availableValues = new Set(
    (dataset.nodes ?? []).map((node) => String(node?.id ?? '')),
  );
  const targetValue = availableValues.has(selectedValue) ? selectedValue : defaultValue;
  if (targetValue) {
    await select.setValue(targetValue);
  }
};
