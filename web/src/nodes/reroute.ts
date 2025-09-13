import { COMFY_API } from '../api/comfy';
import { onAfterGraphConfigured } from '../helpers/manager';
import { LogSeverity } from '../types/manager/manager';
import { Reroute } from '../types/nodes/reroute';
import { ComfyWidgetMap } from '../types/widgets/widgets';
import { getLfManager } from '../utils/common';

//#region Constants
const CATEGORY = '✨ LF Nodes';
const DESCRIPTION = 'Virtual reroute node that propagates upstream type and optional label.';
const DISPLAY_NAME = 'Reroute';
const EXTENSION_NAME = `lf.virtual.${DISPLAY_NAME}`;
const NODE_PATH = '✨ LF Nodes/Reroute';
const SERIALIZED_KEYS = ['label', 'showIcon', 'showType', 'mode', 'horizontal'] as const;
//#endregion

export const lfReroute = {
  name: EXTENSION_NAME,
  registerCustomNodes(appInstance: GraphAppLike) {
    class LFReroute extends LGraphNode implements Reroute {
      __labelWidget?: ComfyWidgetMap['TEXT'];
      __outputType?: string;
      __autoLabel?: string;

      horizontal: boolean;
      isVirtualNode = true;
      properties: Reroute['properties'] = {
        horizontal: false,
        label: '',
        mode: 'label+type',
        showType: true,
        showIcon: true,
      };
      size: [number, number];

      override onConnectionsChange?: () => void;

      constructor() {
        super();

        this.title = this.properties.label || 'Label';
        this.addProperty?.('label', this.properties.label, 'string');
        this.addProperty?.('mode', this.properties.mode, 'string');
        this.addProperty?.('showType', this.properties.showType, 'boolean');
        this.addProperty?.('showIcon', this.properties.showIcon, 'boolean');
        this.addProperty?.('horizontal', this.properties.horizontal, 'boolean');

        this.addInput('', '*');
        this.addOutput(this.makeOutputName('*'), '*');

        this.__labelWidget = this.addWidget?.(
          'text',
          'Label',
          this.properties.label,
          (v: string) => {
            // When user edits the label, persist it. Empty string re-enables auto label.
            this.properties.label = v;
            // If user cleared the label, allow auto label to show.
            this.refreshLabel();
          },
          { multiline: false },
        );

        if (this.__labelWidget) {
          this.__labelWidget.serializeValue = () => this.properties.label;
        }

        this.onConnectionsChange = () => {
          try {
            reroutePropagationLogic.call(this as unknown as LFReroute, appInstance);
          } catch (error) {
            getLfManager()?.log?.(
              '[LFReroute] onConnectionsChange error',
              { error },
              LogSeverity.Warning,
            );
          }
        };
      }

      snapToGrid(size?: number) {
        const proto = LGraphNode.prototype;
        if (proto?.snapToGrid) {
          return proto.snapToGrid.call(this, size);
        }

        const grid = size || LiteGraph.CANVAS_GRID_SIZE || 10;

        if (this.pos) {
          this.pos[0] = grid * Math.round(this.pos[0] / grid);
          this.pos[1] = grid * Math.round(this.pos[1] / grid);
        }
      }

      getExtraMenuOptions(
        _ignored: unknown,
        options: Array<{ content: string; callback: () => void }>,
      ) {
        options.unshift(
          {
            content: 'Cycle Label/Type Mode',
            callback: () => {
              const order = ['label+type', 'label', 'type'] as const;
              const i = order.indexOf(this.properties.mode as (typeof order)[number]);
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
              COMFY_API.scheduleRedraw();
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

      makeOutputName(displayType: string, labelOverride?: string): string {
        const label = (
          labelOverride !== undefined ? labelOverride : this.properties.label || ''
        ).trim();
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

        const effectiveLabel = (this.properties.label || '').trim() || this.__autoLabel || '';
        const displayType = this.__outputType || this.outputs[0].type || '*';
        this.outputs[0].name = this.makeOutputName(displayType, effectiveLabel);
        this.title = effectiveLabel || 'Label';
        this.size = this.computeSize();
        this.applyOrientation();
        COMFY_API.scheduleRedraw();
        const w = this.__labelWidget;
        // Keep widget value in sync only with the user label (not auto label)
        if (w && 'value' in w && w.value !== this.properties.label) {
          w.value = this.properties.label;
        }
      }

      onSerialize(raw: unknown) {
        const o = raw as { properties?: Record<string, unknown>; widgets_values?: unknown[] };

        if (o?.properties) {
          const target = o.properties;
          for (const key of SERIALIZED_KEYS) {
            target[key] = this.properties[key];
          }
        }

        if (Array.isArray(o?.widgets_values) && this.__labelWidget && this.widgets) {
          const idx = this.widgets.indexOf(this.__labelWidget);
          if (idx >= 0) {
            o.widgets_values[idx] = this.properties.label;
          }
        }
      }

      onConfigure(raw: unknown) {
        const o = raw as { properties?: Record<string, unknown>; widgets_values?: unknown[] };
        const props = (o?.properties || {}) as Record<string, unknown>;

        for (const key of SERIALIZED_KEYS) {
          const incoming = props[key];
          if (incoming === undefined) continue;
          if (key === 'mode') {
            if (
              typeof incoming === 'string' &&
              ['label', 'type', 'label+type'].includes(incoming)
            ) {
              this.properties.mode = incoming as 'label' | 'type' | 'label+type';
            }
            continue;
          }
          if (key === 'label') {
            if (typeof incoming === 'string') {
              this.properties.label = incoming;
            } else if (Array.isArray(o?.widgets_values) && this.__labelWidget && this.widgets) {
              const idx = this.widgets.indexOf(this.__labelWidget);
              const wv = o.widgets_values[idx];
              if (idx >= 0 && typeof wv === 'string') {
                this.properties.label = wv;
              }
            }
            continue;
          }
          if (key === 'horizontal' || key === 'showIcon' || key === 'showType') {
            if (typeof incoming === 'boolean') {
              this.properties[key] = incoming;
            }
            continue;
          }
        }

        if (this.__labelWidget && this.widgets) {
          const idx = this.widgets.indexOf(this.__labelWidget);
          if (idx >= 0 && 'value' in this.__labelWidget) {
            this.__labelWidget.value = this.properties.label;
          }
        }

        this.refreshLabel();
      }

      applyOrientation() {
        if (this.properties.horizontal) {
          if (this.inputs?.[0]) {
            this.inputs[0].pos = [this.size[0] / 2, 0];
          }
          if (this.outputs?.[0]) {
            this.outputs[0].pos = [this.size[0] / 2, this.size[1]];
          }
        } else {
          if (this.inputs?.[0]) {
            delete this.inputs[0].pos;
          }
          if (this.outputs?.[0]) {
            delete this.outputs[0].pos;
          }
        }

        COMFY_API.scheduleRedraw();
      }

      override computeSize(): [number, number] {
        const base = this.title || '';
        const slotName = this.outputs?.[0]?.name || '';
        const longest = base.length > slotName.length ? base : slotName;
        const textSize = LiteGraph.NODE_TEXT_SIZE || 14;
        const w = Math.max(120, textSize * longest.length * 0.6 + 50);
        const collapsed = this.flags?.collapsed;
        const h = collapsed ? 28 : 50;
        return [w, h];
      }

      onDrawForeground(ctx: CanvasRenderingContext2D) {
        try {
          if (!this.properties.showIcon || !ctx) {
            return;
          }

          const headerH = (LiteGraph && LiteGraph.NODE_TITLE_HEIGHT) || 24;
          const radius = 6;
          const cx = 10 + radius; // horizontal padding
          const cy = -headerH / 2; // center within header (negative coordinate)
          ctx.save();
          ctx.fillStyle = '#3a3a3a';
          ctx.beginPath();
          ctx.arc(cx, cy, radius, 0, Math.PI * 2);
          ctx.fill();
          ctx.fillStyle = '#d4d4d4';
          ctx.beginPath();
          ctx.arc(cx, cy, radius * 0.4, 0, Math.PI * 2);
          ctx.fill();
          ctx.restore();
        } catch (err) {
          getLfManager()?.log?.('[LFReroute] onDrawForeground error', { err }, LogSeverity.Info);
        }
      }
    }

    function reroutePropagationLogic(this: LFReroute, appInstance: GraphAppLike) {
      const isLabeled = (n: unknown): n is LFReroute => (n as any)?.constructor?.type === NODE_PATH;

      let inputType: string | null = null;
      let upstream: LFReroute | (LFReroute & { inputs?: GraphSlot[] }) = this;
      let originNode: LFReroute | null = null;

      while ((upstream as { inputs?: GraphSlot[] })?.inputs?.[0]?.link != null) {
        const linkId = (upstream as { inputs: GraphSlot[] }).inputs[0].link;
        const link = appInstance.graph.links[linkId];
        if (!link) break;
        const origin = appInstance.graph.getNodeById(link.origin_id);
        if (!origin) break;
        if (isLabeled(origin)) {
          if (origin === this) {
            (
              upstream as LFReroute & { disconnectInput?: (slot: number) => void }
            ).disconnectInput?.(link.target_slot);
            break;
          }
          upstream = origin;
          continue;
        }
        inputType = (origin as { outputs?: GraphSlot[] }).outputs?.[link.origin_slot]?.type || null;
        originNode = origin as typeof originNode;
        break;
      }

      let downstreamType: string | null = null;
      const firstLinks = this.outputs?.[0]?.links || [];
      for (const l of firstLinks) {
        const link: GraphLink = appInstance.graph.links[l];
        if (!link) {
          continue;
        }

        const target = appInstance.graph.getNodeById(link.target_id);
        if (!target || isLabeled(target)) {
          continue;
        }

        downstreamType = target.inputs?.[link.target_slot]?.type || null;
        if (downstreamType) {
          break;
        }
      }

      const finalType = inputType || downstreamType || '*';

      // Auto-label logic: only compute auto label when user label empty
      if (!(this.properties.label || '').trim()) {
        if (originNode) {
          const candidateTitle = (originNode.title || '').trim();
          const candidateSlotName = ((): string => {
            if (!originNode.outputs) return '';
            const slotIdx = ((): number => {
              if ((upstream as { inputs?: GraphSlot[] })?.inputs?.[0]?.link != null) {
                const linkId = (upstream as { inputs: GraphSlot[] }).inputs[0].link;
                const link = appInstance.graph.links[linkId];
                if (link) return link.origin_slot ?? 0;
              }
              return 0;
            })();
            return (
              originNode.outputs?.[slotIdx]?.label ||
              originNode.outputs?.[slotIdx]?.name ||
              ''
            ).trim();
          })();
          const effectiveSlotName =
            candidateSlotName && candidateSlotName !== '*' ? candidateSlotName : '';
          const chosen = effectiveSlotName || candidateTitle;
          if (chosen) {
            this.__autoLabel = chosen; // store separately; do not overwrite user label
          }
        } else {
          this.__autoLabel = undefined; // no origin -> clear auto label
        }
      } else {
        // User provided a label -> freeze auto label until cleared
        this.__autoLabel = undefined;
      }

      this.__outputType = finalType;
      if (this.outputs?.[0]) {
        this.outputs[0].type = inputType || '*';
        this.outputs[0].name = this.makeOutputName(finalType);
      }

      this.size = this.computeSize();
      this.applyOrientation();
      // Update title using refreshLabel to respect auto label logic
      this.refreshLabel();

      const color = LGraphCanvas.link_type_colors?.[finalType];
      if (color && this.outputs?.[0]?.links) {
        for (const l of this.outputs[0].links) {
          const link: GraphLink = appInstance.graph.links[l];
          if (link) link.color = color;
        }
      }
      COMFY_API.scheduleRedraw();
    }

    LiteGraph.registerNodeType(
      NODE_PATH,
      Object.assign(LFReroute, {
        title_mode: LiteGraph.NORMAL_TITLE,
        title: 'Reroute',
        collapsable: true,
        category: 'LF Nodes',
        description: 'Label + type aware reroute (frontend virtual)',
      }),
    );

    onAfterGraphConfigured(LFReroute, (node) => {
      requestAnimationFrame(() => {
        try {
          node.onConnectionsChange?.();
        } catch (err) {
          getLfManager()?.log?.(
            '[LFReroute] onAfterGraphConfigured error',
            { err },
            LogSeverity.Warning,
          );
        }
      });
    });

    getLfManager()?.log?.(
      `Virtual node registered (UI compliant): ${NODE_PATH}`,
      {},
      LogSeverity.Success,
    );
  },

  beforeRegisterVueAppNodeDefs(defs: any[]) {
    const def = defs.find((d) => d.name === NODE_PATH);
    if (def) {
      def.display_name = DISPLAY_NAME;
      def.category = CATEGORY;
      def.description = DESCRIPTION;
      if (def.python_module === 'custom_nodes.frontend_only') {
        def.python_module = 'lf_nodes.virtual';
      }
    }
  },
};
