import { ComfyWidget, ComfyWidgetMap } from '../widgets/widgets';

//#region Class Definition
export interface Reroute {
  __labelWidget?: ComfyWidgetMap['TEXT'] | undefined;
  __outputType?: string;
  properties: {
    horizontal: boolean;
    label: string;
    mode: 'label' | 'type' | 'label+type';
    showType: boolean;
    showIcon?: boolean;
    [k: string]: unknown;
  };
  inputs?: GraphSlot[];
  outputs?: GraphSlot[];
  size: [number, number];
  graph?: LiteGraphGraph;
  applyOrientation: () => void;
  computeSize: () => [number, number];
  makeOutputName: (displayType: string) => string;
  onAfterGraphConfigured?: () => void;
  refreshLabel: () => void;
}
//#endregion
