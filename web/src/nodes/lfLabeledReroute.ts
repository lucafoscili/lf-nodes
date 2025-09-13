/* Frontend-only Labeled Reroute Node for LF Nodes
 * Inspired by native ComfyUI reroute implementation.
 * Provides: user label + dynamic type propagation + display modes.
 * This file purposefully avoids importing internal ComfyUI modules and instead
 * relies on runtime globals (LiteGraph, LGraphCanvas, app, helper fns) to stay
 * resilient to upstream path/layout changes.
 */

// Declare globals to satisfy TypeScript (these are provided by ComfyUI at runtime)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const LiteGraph: any;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const LGraphCanvas: any;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const app: any; // provided by ComfyUI core frontend
// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const LGraphNode: any; // base LiteGraph node class

// Helper access wrappers (gracefully degrade if missing)
const widgetHelpers = (() => {
  const g: any = window as any;
  return {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    mergeIfValid: g.mergeIfValid || ((..._args: any[]) => null),
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    getWidgetConfig: g.getWidgetConfig || ((..._args: any[]) => null),
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    setWidgetConfig: g.setWidgetConfig || ((..._args: any[]) => {}),
  };
})();

interface LFLabeledRerouteNode /* extends LGraphNode (untyped global) */ {
  __outputType?: string;
  properties: {
    horizontal: boolean;
    label: string;
    mode: 'label' | 'type' | 'label+type';
    showType: boolean;
    showIcon?: boolean;
    [k: string]: any;
  };
  inputs?: Array<{
    name?: string;
    type?: string;
    link?: number | null;
    links?: number[];
    pos?: [number, number];
    [k: string]: any;
  }>;
  outputs?: Array<{
    name?: string;
    type?: string;
    links?: number[];
    [k: string]: any;
  }>;
  size: [number, number];
  graph?: any;
  makeOutputName: (displayType: string) => string;
  refreshLabel: () => void;
  applyOrientation: () => void;
  computeSize: () => [number, number];
}

const EXTENSION_NAME = 'LF.LabeledReroute';
const NODE_TYPE = 'LF/LabeledReroute'; // Category prefix shown in UI

// Exported extension consumed by LFManager instead of self-registering here.
// This avoids relying on global app during module evaluation and keeps a single
// registration pathway consistent with other LF extensions.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const lfLabeledRerouteExtension: any = {
  name: EXTENSION_NAME,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  registerCustomNodes(appInstance: any) {
    class LFLabeledReroute extends LGraphNode implements LFLabeledRerouteNode {
      static category: string | undefined = 'utils';
      static defaultVisibility = false;

      __outputType?: string;
      properties: LFLabeledRerouteNode['properties'];
      horizontal: boolean;
      size: [number, number];

      constructor() {
        super();
        if (!this.properties) this.properties = {} as any; // base LGraphNode sets this.properties
        this.properties.horizontal = false;
        this.properties.label = this.properties.label || '';
        this.properties.mode = this.properties.mode || 'label+type';
        this.properties.showType = this.properties.showType ?? true;
        this.properties.showIcon = this.properties.showIcon ?? true;
        this.title = this.properties.label || 'Label';
        this.addProperty?.('label', this.properties.label, 'string');

        // Base IO
        // input wildcard always; output wildcard initially (content decided after analysis)
        this.addInput('', '*');
        this.addOutput(this.makeOutputName('*'), '*');

        // Single Label editing widget (text) with persistence
        const labelWidget = this.addWidget?.(
          'text',
          'Label',
          this.properties.label,
          (v: string) => {
            this.properties.label = v;
            this.refreshLabel();
          },
          { multiline: false },
        );
        (this as any)._lf_labelWidget = labelWidget;
        if (labelWidget) {
          labelWidget.serializeValue = () => this.properties.label;
        }

        // Schedule initial type propagation after graph config
        (this as any).onAfterGraphConfigured = function () {
          requestAnimationFrame(() => {
            this.onConnectionsChange(LiteGraph.INPUT, null, true, null);
          });
        };

        (this as any).onConnectionsChange = function () {
          try {
            reroutePropagationLogic.call(this, appInstance);
          } catch (error) {
            console.warn('[LFLabeledReroute] onConnectionsChange error', error);
          }
        };

        (this as any).isVirtualNode = true; // Do not serialize into execution prompt
      }

      // Inherit snapToGrid from prototype chain if provided by patches; fallback if missing
      snapToGrid(size?: number) {
        if (typeof (LGraphNode as any).prototype.snapToGrid === 'function') {
          return (LGraphNode as any).prototype.snapToGrid.call(this, size);
        }
        const grid = size || LiteGraph.CANVAS_GRID_SIZE || 10;
        if (this.pos) {
          this.pos[0] = grid * Math.round(this.pos[0] / grid);
          this.pos[1] = grid * Math.round(this.pos[1] / grid);
        }
      }

      // Menu options
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      getExtraMenuOptions(_ignored: any, options: any[]) {
        options.unshift(
          {
            content: 'Cycle Label/Type Mode',
            callback: () => {
              const order = ['label+type', 'label', 'type'] as const;
              const i = order.indexOf(this.properties.mode as any);
              this.properties.mode = order[(i + 1) % order.length];
              this.refreshLabel();
            },
          },
          {
            content: (this.properties.showType ? 'Hide' : 'Show') + ' Type Part',
            callback: () => {
              this.properties.showType = !this.properties.showType;
              this.refreshLabel();
            },
          },
          {
            content: (this.properties.showIcon ? 'Hide' : 'Show') + ' Icon',
            callback: () => {
              this.properties.showIcon = !this.properties.showIcon;
              appInstance.graph.setDirtyCanvas(true, true);
            },
          },
          {
            content: 'Edit Label',
            callback: () => {
              const v = prompt('Set label', this.properties.label || '');
              if (v !== null) {
                this.properties.label = v;
                this.refreshLabel();
              }
            },
          },
          {
            content: 'Set ' + (this.properties.horizontal ? 'Horizontal' : 'Vertical'),
            callback: () => {
              this.properties.horizontal = !this.properties.horizontal;
              this.applyOrientation();
            },
          },
        );
      }

      makeOutputName(displayType: string): string {
        const label = (this.properties.label || '').trim();
        const typePart = this.properties.showType ? displayType : '';
        switch (this.properties.mode) {
          case 'label':
            return label || (this.properties.showType ? displayType : '');
          case 'type':
            return typePart;
          case 'label+type':
          default:
            if (label && typePart) return `${label}:${typePart}`;
            return label || typePart;
        }
      }

      refreshLabel() {
        if (!this.outputs?.length) return;
        this.outputs[0].name = this.makeOutputName(
          this.__outputType || this.outputs[0].type || '*',
        );
        // Update header title (independent from output name formatting)
        this.title = this.properties.label || 'Label';
        this.size = this.computeSize();
        this.applyOrientation();
        appInstance.graph.setDirtyCanvas(true, true);
        const w = (this as any)._lf_labelWidget;
        if (w && w.value !== this.properties.label) w.value = this.properties.label;
      }

      onSerialize(o: any) {
        if (o?.properties) o.properties.label = this.properties.label;
        if (o?.properties) o.properties.showIcon = this.properties.showIcon;
        // ensure widgets_values contains the label for backward compatibility if needed
        if (Array.isArray(o.widgets_values)) {
          const idx = this.widgets?.indexOf((this as any)._lf_labelWidget);
          if (idx != null && idx >= 0) {
            o.widgets_values[idx] = this.properties.label;
          }
        }
      }

      onConfigure(o: any) {
        if (o?.properties?.label !== undefined) {
          this.properties.label = o.properties.label;
        } else if (Array.isArray(o?.widgets_values)) {
          // fallback if old serialization stored it only in widgets_values
          const w = (this as any)._lf_labelWidget;
          const idx = w ? this.widgets?.indexOf(w) : -1;
          if (idx != null && idx >= 0 && o.widgets_values[idx] != null) {
            this.properties.label = o.widgets_values[idx];
          }
        }
        if (o?.properties?.showIcon !== undefined) {
          this.properties.showIcon = o.properties.showIcon;
        }
        const w = (this as any)._lf_labelWidget;
        if (w) w.value = this.properties.label;
        this.refreshLabel();
      }

      applyOrientation() {
        (this as any).horizontal = this.properties.horizontal;
        if (this.properties.horizontal) {
          // Center input at top
          if (this.inputs?.[0]) this.inputs[0].pos = [this.size[0] / 2, 0];
        } else if (this.inputs?.[0]) {
          delete this.inputs[0].pos;
        }
        appInstance.graph.setDirtyCanvas(true, true);
      }

      computeSize(): [number, number] {
        // Base width considers longest between title and output label but keeps a minimum
        const base = this.title || '';
        const slotName = this.outputs?.[0]?.name || '';
        const longest = base.length > slotName.length ? base : slotName;
        const w = Math.max(120, LiteGraph.NODE_TEXT_SIZE * longest.length * 0.6 + 50);
        // Height: header (approx 24) + body (widget row ~ 24) minimal; if collapsed rely on framework to shrink
        const collapsed = (this as any).flags?.collapsed;
        const h = collapsed ? 28 : 50;
        return [w, h];
      }

      // Optional decorative icon (reroute symbol) drawn in header space
      // Attempt to hook into LiteGraph drawing; guard for safety.
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      onDrawForeground(ctx: any) {
        try {
          if (!this.properties.showIcon) return;
          if (!ctx) return;
          // Draw inside the header area. In LiteGraph, node local (0,0) is the top-left of the content area (just below the title bar),
          // so the title bar spans from y = -NODE_TITLE_HEIGHT to y = 0. Center the icon vertically within that negative region.
          const headerH = (LiteGraph && LiteGraph.NODE_TITLE_HEIGHT) || 24;
          const radius = 6;
          const cx = 10 + radius; // horizontal padding
          const cy = -headerH / 2; // center within header (negative coordinate)
          ctx.save();
          // subtle background circle
          ctx.fillStyle = '#3a3a3a';
          ctx.beginPath();
          ctx.arc(cx, cy, radius, 0, Math.PI * 2);
          ctx.fill();
          // inner dot representing reroute point
          ctx.fillStyle = '#d4d4d4';
          ctx.beginPath();
          ctx.arc(cx, cy, radius * 0.4, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        } catch (err) {
          // ignore draw errors to avoid breaking graph rendering
        }
      }

      static setDefaultTextVisibility(v: boolean) {
        LFLabeledReroute.defaultVisibility = v;
      }
    }

    // Reroute propagation logic (adapted from native ComfyUI reroute)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    function reroutePropagationLogic(this: any, appInstance: any) {
      // Only operate on our custom labeled reroute chain. We don't mutate native reroutes.
      const isLabeled = (n: any) => (n?.constructor as any)?.type === 'LabeledReroute';

      // Upstream: climb only through other labeled reroutes until a non-labeled source found.
      let inputType: string | null = null;
      let upstream = this as any;
      let originNode: any = null; // first real producer encountered
      while (upstream?.inputs?.[0]?.link != null) {
        const linkId = upstream.inputs[0].link;
        const link = appInstance.graph.links[linkId];
        if (!link) break;
        const origin = appInstance.graph.getNodeById(link.origin_id);
        if (!origin) break;
        if (isLabeled(origin)) {
          // prevent cycles
          if (origin === this) {
            upstream.disconnectInput?.(link.target_slot);
            break;
          }
          upstream = origin;
          continue;
        }
        // Found a real producer
        inputType = origin.outputs?.[link.origin_slot]?.type || null;
        originNode = origin;
        break;
      }

      // If no upstream type, attempt a lightweight downstream peek (first non-labeled consumer)
      let downstreamType: string | null = null;
      const firstLinks = this.outputs?.[0]?.links || [];
      for (const l of firstLinks) {
        const link = appInstance.graph.links[l];
        if (!link) continue;
        const target = appInstance.graph.getNodeById(link.target_id);
        if (!target) continue;
        if (isLabeled(target)) continue; // skip our siblings
        downstreamType = target.inputs?.[link.target_slot]?.type || null;
        if (downstreamType) break;
      }

      const finalType = inputType || downstreamType || '*';
      // One-time auto-label initialization: if user hasn't provided a label yet,
      // adopt the upstream origin node's title (preferred) or its output slot name.
      if (!this.properties.label || !this.properties.label.trim()) {
        if (originNode) {
          const candidateTitle = (originNode.title || '').trim();
          const candidateSlotName = ((): string => {
            if (!originNode.outputs) return '';
            const slotIdx = ((): number => {
              // try to find the slot that fed us via upstream link
              if (upstream?.inputs?.[0]?.link != null) {
                const linkId = upstream.inputs[0].link;
                const link = appInstance.graph.links[linkId];
                if (link) return link.origin_slot ?? 0;
              }
              return 0;
            })();
            return (originNode.outputs?.[slotIdx]?.name || '').trim();
          })();
          // Prefer the explicit slot name over the node title when available and meaningful.
          const effectiveSlotName =
            candidateSlotName && candidateSlotName !== '*' ? candidateSlotName : '';
          const chosen = effectiveSlotName || candidateTitle;
          if (chosen) {
            this.properties.label = chosen;
          }
        }
      }
      this.__outputType = finalType;
      if (this.outputs?.[0]) {
        this.outputs[0].type = inputType || '*';
        this.outputs[0].name = this.makeOutputName(finalType);
      }
      this.size = this.computeSize();
      this.applyOrientation();
      // If we just auto-labeled, ensure header/title reflects it (avoid re-running full propagation)
      if (originNode && this.title !== this.properties.label) {
        this.title = this.properties.label || 'Label';
      }

      // Link coloring (only immediate outgoing links)
      const color = (LGraphCanvas as any).link_type_colors?.[finalType];
      if (color && this.outputs?.[0]?.links) {
        for (const l of this.outputs[0].links) {
          const link = appInstance.graph.links[l];
          if (link) link.color = color;
        }
      }
      appInstance.graph.setDirtyCanvas(true, true);
    }

    LiteGraph.registerNodeType(
      NODE_TYPE,
      Object.assign(LFLabeledReroute, {
        title_mode: LiteGraph.NORMAL_TITLE,
        title: 'Label',
        collapsable: true,
      }),
    );
  },
};

export {}; // ensure module scope (no default export)
