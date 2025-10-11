export const BUTTON_STYLE = ':host { margin: auto; padding: 1em 0; width: max-content; }';

export const STYLES = {
  customization: () => ({
    margin: '0',
  }),
  debugGrid: () => ({
    display: 'grid',
    gridTemplateRows: 'repeat(5, max-content) 1fr',
    height: '100%',
    margin: '0',
  }),
  debugLogs: () => ({
    display: 'grid',
    gridGap: '0.75em',
    gridTemplateRows: '320px 480px',
  }),
  logsArea: () => ({
    backgroundColor: 'rgba(var(--lf-color-on-bg), 0.075)',
    borderRadius: '0.5em',
    display: 'block',
    height: '100%',
    marginBottom: '1em',
    overflow: 'auto',
  }),
  separator: () => ({
    border: '1px solid rgb(var(--lf-color-border))',
    display: 'block',
    margin: '0.75em auto 1.25em',
    opacity: '0.25',
    width: '50%',
  }),
} as const;
