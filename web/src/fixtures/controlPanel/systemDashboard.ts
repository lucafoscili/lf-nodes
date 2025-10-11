import { LfArticleNode } from '@lf-widgets/foundations';
import {
  ControlPanelFixture,
  ControlPanelIcons,
  ControlPanelLabels,
  ControlPanelSection,
} from '../../types/widgets/controlPanel';
import {
  clampPercent,
  formatBytes,
  getLfManager,
  percentLabel,
  toNumber,
} from '../../utils/common';
import { BUTTON_STYLE, STYLES } from './styles';

//#region Build system dashboard section
export const buildSystemDashboardSection: ControlPanelFixture['system-dashboard'] = (stats?) => {
  const { theme } = getLfManager().getManagers().lfFramework;
  const { '--lf-icon-refresh': refreshIcon } = theme.get.current().variables;
  const { progress } = theme.get.icons();
  const refreshTimeout = getLfManager().getSystemTimeout() || 0;

  const gpus = stats?.gpus ?? [];
  const disks = stats?.disks ?? [];
  const cpu = stats?.cpu;
  const ram = stats?.ram;
  const errors = stats?.errors ?? [];
  const timestamp = stats?.timestamp ? new Date(stats.timestamp) : null;
  const lastUpdated = timestamp ? timestamp.toLocaleString() : 'Waiting for data';

  const gpuNodes: LfArticleNode[] = gpus.length
    ? gpus.map((gpu) => {
        const vramPercent = gpu.vram_total
          ? clampPercent((gpu.vram_used / gpu.vram_total) * 100)
          : 0;
        const utilPercent = clampPercent(gpu.utilization);
        return {
          id: `gpu-${gpu.index}`,
          value: '',
          cssStyle: { marginBottom: '1em' },
          children: [
            {
              id: `gpu-${gpu.index}-title`,
              value: `${gpu.name} (GPU ${gpu.index})`,
              tagName: 'strong',
            },
            buildProgressNode(
              progress,
              `gpu-${gpu.index}-vram`,
              `VRAM ${formatBytes(gpu.vram_used)} / ${formatBytes(gpu.vram_total)} (${percentLabel(
                vramPercent,
              )})`,
              vramPercent,
            ),
            buildProgressNode(
              progress,
              `gpu-${gpu.index}-util`,
              `Utilization ${percentLabel(utilPercent)}`,
              utilPercent,
            ),
          ],
        };
      })
    : [
        {
          id: 'gpu-none',
          value: 'No GPUs detected.',
          cssStyle: { opacity: '0.7' },
        },
      ];

  const cpuNodes: LfArticleNode[] = cpu
    ? [
        buildProgressNode(
          progress,
          'cpu-average',
          `Average usage ${percentLabel(cpu.average)}`,
          clampPercent(cpu.average),
        ),
        {
          id: 'cpu-meta',
          value: `Logical cores: ${cpu.count} • Physical cores: ${cpu.physical_count}`,
          cssStyle: { fontSize: '0.9em', opacity: '0.8' },
        },
        {
          id: 'cpu-cores',
          value: '',
          cssStyle: {
            display: 'grid',
            gap: '0.75em',
            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
          },
          children: cpu.cores.map((core) =>
            buildProgressNode(
              progress,
              `cpu-core-${core.index}`,
              `Core ${core.index} ${percentLabel(core.usage)}`,
              clampPercent(core.usage),
            ),
          ),
        },
      ]
    : [
        {
          id: 'cpu-none',
          value: 'CPU statistics unavailable.',
          cssStyle: { opacity: '0.7' },
        },
      ];

  const ramNodes: LfArticleNode[] = ram
    ? [
        buildProgressNode(
          progress,
          'ram-usage',
          `RAM ${formatBytes(ram.used)} / ${formatBytes(ram.total)} (${percentLabel(ram.percent)})`,
          clampPercent(ram.percent),
        ),
        {
          id: 'ram-available',
          value: `Available: ${formatBytes(ram.available)}`,
          cssStyle: { fontSize: '0.9em', opacity: '0.8' },
        },
        ...(ram.swap_total
          ? [
              buildProgressNode(
                progress,
                'swap-usage',
                `Swap ${formatBytes(ram.swap_used)} / ${formatBytes(
                  ram.swap_total,
                )} (${percentLabel((ram.swap_used / ram.swap_total) * 100)})`,
                clampPercent((ram.swap_used / ram.swap_total) * 100),
              ),
            ]
          : []),
      ]
    : [
        {
          id: 'ram-none',
          value: 'RAM statistics unavailable.',
          cssStyle: { opacity: '0.7' },
        },
      ];

  const diskNodes: LfArticleNode[] = disks.length
    ? disks.map((disk, index) => {
        const used = toNumber(disk.used);
        const total = toNumber(disk.total);
        const percent = total ? clampPercent((used / total) * 100) : clampPercent(disk.percent);
        const descriptor = [disk.device || disk.mountpoint, disk.label].filter(Boolean).join(' ');

        return {
          id: `disk-${index}`,
          value: '',
          cssStyle: { marginBottom: '1em' },
          children: [
            {
              id: `disk-${index}-title`,
              value: descriptor || disk.mountpoint,
              tagName: 'strong',
            },
            {
              id: `disk-${index}-mount`,
              value: `Mount: ${disk.mountpoint}`,
              cssStyle: { fontSize: '0.9em', opacity: '0.8', marginBottom: '0.25em' },
            },
            buildProgressNode(
              progress,
              `disk-${index}-usage`,
              `${formatBytes(disk.used)} / ${formatBytes(disk.total)} (${percentLabel(percent)})`,
              percent,
            ),
          ],
        };
      })
    : [
        {
          id: 'disk-none',
          value: 'No disks detected.',
          cssStyle: { opacity: '0.7' },
        },
      ];

  const overviewChildren: LfArticleNode[] = [
    {
      id: ControlPanelSection.Content,
      value: 'Monitor real-time hardware usage for GPUs, CPU, memory, and storage.',
    },
    {
      id: ControlPanelSection.Content,
      value: `Last updated: ${lastUpdated}`,
      cssStyle: { fontSize: '0.85em', opacity: '0.75' },
    },
    {
      id: ControlPanelSection.Content,
      value:
        refreshTimeout > 0 ? `Auto refresh every ${refreshTimeout}s` : 'Auto refresh disabled.',
      cssStyle: { fontSize: '0.85em', opacity: '0.75', marginTop: '0.3em' },
    },
    {
      id: ControlPanelSection.Content,
      value: '',
      cells: {
        lfTextfield: {
          lfHelper: { showWhenFocused: false, value: 'Set to 0 to disable auto refresh' },
          lfHtmlAttributes: { type: 'number', min: '0', step: 'any' },
          lfLabel: ControlPanelLabels.SystemAutoRefresh,
          lfStyle: ':host { display: block; margin: 0.75em auto; max-width: 240px; }',
          lfValue: refreshTimeout > 0 ? refreshTimeout.toString() : '',
          shape: 'textfield',
          value: '',
        },
      },
    },
  ];

  if (errors.length) {
    overviewChildren.push({
      id: 'system-errors',
      value: '',
      children: errors.map((message, index) => ({
        id: `system-error-${index}`,
        value: message,
        cssStyle: {
          color: 'rgb(var(--lf-color-danger))',
          fontSize: '0.85em',
        },
      })),
    });
  }

  overviewChildren.push({
    id: ControlPanelSection.Content,
    value: '',
    cells: {
      lfButton: {
        lfIcon: refreshIcon,
        lfLabel: ControlPanelLabels.RefreshSystemStats,
        lfStyle: BUTTON_STYLE,
        lfStyling: 'flat',
        shape: 'button',
        value: '',
      },
    },
  });

  return {
    icon: ControlPanelIcons.SystemDashboard,
    id: ControlPanelSection.Section,
    value: 'System monitor',
    children: [
      {
        id: ControlPanelSection.Paragraph,
        value: 'Overview',
        children: overviewChildren,
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: '',
      },
      {
        id: ControlPanelSection.Paragraph,
        value: 'GPU usage',
        children: gpuNodes,
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: '',
      },
      {
        id: ControlPanelSection.Paragraph,
        value: 'CPU usage',
        children: cpuNodes,
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: '',
      },
      {
        id: ControlPanelSection.Paragraph,
        value: 'Memory',
        children: ramNodes,
      },
      {
        cssStyle: STYLES.separator(),
        id: ControlPanelSection.ContentSeparator,
        value: '',
      },
      {
        id: ControlPanelSection.Paragraph,
        value: 'Disk usage',
        children: diskNodes,
      },
    ],
  };
};
//#endregion

// #region Helpers
const getUsageState = (percent: number | null | undefined) => {
  const value = clampPercent(percent);
  if (value >= 90) return 'danger';
  if (value >= 70) return 'warning';
  if (value === 0) return 'primary';
  return 'success';
};

const buildProgressNode = (
  icon: string,
  id: string,
  label: string,
  percent: number,
): LfArticleNode => ({
  id,
  value: '',
  cells: {
    lfProgressbar: {
      lfIcon: icon,
      lfLabel: label,
      lfUiState: getUsageState(percent),
      shape: 'progressbar',
      value: clampPercent(percent),
    },
  },
});
//#endregion
