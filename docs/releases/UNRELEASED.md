# Next release

Changes after [LF Nodes 5.1.0](5.1.0.md):

- **Icon Framer** (`LF_IconFramer`, Image): fits a masked subject into a square icon at a chosen fill, over a
  flat or source backdrop, with an optional glow, a dark outline, darkened corners and a bevelled rim lit from
  the top left; writes a master size and a small display size. Compare widget: input against the framed icon.
  Its Titanic case is not written yet, so it is not release-ready.
- **Icon from Text** (`icon_from_text`, Runner): Krea 2 Turbo paints one object from a prompt, with up to three
  optional style images through the community style-reference adapter (removed when none is given); Background
  Remover (RMBG-2.0) finds the subject and Icon Framer frames it. Saves the painting, the master icon and the
  small icon; one submission per seed.
