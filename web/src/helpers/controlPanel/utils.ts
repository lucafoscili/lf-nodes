import { LfArticleElement, LfArticleNode } from '@lf-widgets/foundations';
import { ControlPanelSection } from '../../types/widgets/controlPanel';

//#region setArticleDataset
export const setArticleDataset = (article: LfArticleElement, node: LfArticleNode) => {
  article.lfDataset = {
    nodes: [{ children: [node], id: ControlPanelSection.Root }],
  };
};
//#endregion
