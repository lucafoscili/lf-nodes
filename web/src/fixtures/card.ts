export const DOWNLOAD_PLACEHOLDERS: Partial<HTMLLfCardElement> = {
  lfDataset: {
    nodes: [
      {
        cells: {
          lfImage: { shape: 'image', value: 'download' },
          lfText: { shape: 'text', value: 'Fetching metadata from CivitAI...' },
        },
        id: '0',
      },
    ],
  },
};
