# Comfy ecosystem update — 2026-10-01

This host maintenance pass follows the completed LF consolidation. It updates
the existing Comfy/extension channels, preserves local work, and does not
publish or change LF Nodes' release version.

## Installed changes

| Component | Previous | Updated |
| --- | --- | --- |
| Comfy Core, existing `master` | `79be670e` / 0.37.0 | `651ca296` / 0.38.0 |
| Comfy frontend | 1.53.6 | 1.53.10 |
| Kitchen | 0.2.35 | 0.2.36 |
| Workflow templates | 0.11.70 | 0.11.73 |
| Embedded docs | 0.5.12 | 0.5.13 |
| Manager | `9c29dc68` | `2a6cb164` |
| ControlNet Aux | `59b1fc41` / 1.1.5 | `0cd29047` / 1.1.6 |
| Ultimate SD Upscale | `c48d60df` / 1.6.0 | `a5547db9` / 1.7.2 |

Core's exact revision is newer than the 0.38.0 release tag. All four Git
updates were fast-forwards with submodule recursion disabled. Existing Core
storage edits and untracked files are unchanged. Ultimate's nested gitlink is
unchanged; its untracked Python cache was preserved, not deleted or stashed.

The two Krea extensions, H3 Turbo/Spectrum/Latent-Upres, See-through and AI
GameDev already match their configured upstreams. The four registry packages
(Inpaint 1.4.3, Tooling 3.3.0, IPAdapter 2.0.0, SeedVR2 2.5.24) already match
their latest published registry versions. AI GameDev's nested changes remain
untouched. LF's local candidate was not replaced by its published remote.

VNCCS upstream still needs the local `b843cc0` decoder repair. It remains
installed and clean, one commit ahead of upstream; no reset or replacement
was performed. This fix was not published upstream. **Subsequent 2026-10-02
change:** shipped LF sprite/turnaround workflows now use
[native RMBG-2.0](BACKGROUND_REMOVER.md), so this external repair is relevant
only to older/custom consumers. The evidence below records the original update.

## Dependency boundaries

Seven distributions changed: the four Core pins above and three template
subpackages. The resolver plan was checked before exact-version installation.
`pip check` passed. PyTorch/torchvision/torchaudio remain
2.11.0+cu130 / 0.26.0+cu130 / 2.11.0+cu130; Transformers 5.10.1, Tokenizers
0.22.2, AIMDO 0.5.5 and Pillow 12.2.0 remain unchanged. No models were downloaded.

Aux's new requirements file names `albumentationsx`, while its pyproject still
names `albumentations`. Both supply the same import namespace. The working
`albumentations==2.0.8` provider was retained rather than overlaying conflicting
distributions. The other newly listed dependency, `rtree`, was already present.
Optional ONNX GPU acceleration was not added. This is a reviewed code update,
not a claim that every optional extension requirement is installed.

## Compatibility and verification

- Managed JOC stop/start succeeded with an idle queue. No manual process kill,
  launch, global interrupt or cache clear was used.
- Startup inventory changed from 1,334 to 1,339 node types. All 154 LF schemas
  are identical before/after. The only removed type is upstream's deprecated
  `OpenAIVideoSora2`; new provider nodes and `UltimateSDUpscaleGuider` account
  for the additions. No checked LF workflow uses that removed type.
- Ultimate appends required `batch_size`, default 1. Disposable old-format
  browser hydration retained all 20 existing widget values and serialized the
  added 21st value as 1. Existing raw API prompts must explicitly include this
  new input; the Python function default does not bypass Core validation.
- The canonical Titanic passed hydration and actual execution of
  `cpu.image-regions-layers` and `cpu.glb-texture-scale`. Its 390 nodes / 515
  links and fixture bytes stayed unchanged. This is **targeted execution**, not
  exhaustive Titanic or third-party extension coverage.
- Static LF contracts passed for 154 mappings. Focused fixture/release/schema/
  HD wiring checks passed: 15 tests and four subtests. The external VNCCS
  decoder regression passed three tests.
- The fresh HD sprite orchestra passed in 439 seconds observed, parent
  `lf-sequence:51cd4e1c12544b489393ac708766cbe9`. H3 plus four-step HD refinement
  (`0e82547c-21ad-4e18-8ccc-d0d7c4dd5ac0`) took 407.46 seconds; VNCCS sprite
  cutting (`ae275635-d4a3-4784-9444-2f5385c8d63e`) took 26.25 seconds. Both Core
  histories report no cached nodes. The MP4 decodes all 124 frames at
  **1920×1088 / 24 fps**, with a stereo 32 kHz AAC stream. This verifies the
  audio stream, not listening-based sound quality.
- All 24 exported RGBA sprite frames have real transparency, nonempty content,
  no clipping, and the expected baseline at row 235. The atlas and five video
  sample frames were inspected: subject, outfit and wave remain recognizable.
  Fine sprite edge fringes and loop smoothness remain creative acceptance
  questions; no new showcase cover or quality improvement is claimed.
- Ultimate's two-tile/two-step refinement and Aux Canny both actually executed
  in `e98ef2e3-31f0-4e16-bebe-c0bf638e95e5` (51.88 seconds; no cached nodes).
  The 256×384 refinement and edge map were inspected. This is a bounded
  compatibility specimen, not a quality render or coverage of every Aux model.
- Playwright desktop and 390-pixel mobile checks passed: curated and custom
  collections remain usable, all 35 accepted covers load, and there is no
  horizontal overflow. Existing optional CSS/subgraph and AI GameDev import
  404s remain; this is not a clean-console claim. The diagnostic browser was
  closed. Comfy/proxy remain available with an idle queue.

The HD video is under Comfy output at
`LF_Nodes/MiniMaxH3/ReferenceRestage/kitchen_quality/seed-260926-refs1-f124-hd4_00001_.mp4`;
its sprite atlas is
`LF_Nodes/SpriteLoopCut/256px-content-144px-bottom-20px-f24/atlas-6x4_00003_.png`.
Ultimate/Aux specimens are in `LF_Nodes/Compatibility/20261001/`.

**Keep:** the updated host combination and its named live passes. **Defer:**
exhaustive provider/model/editor execution, optional dependency changes, new
art acceptance and LF release publication. Remaining local VNCCS and upstream
Ultimate/Sora compatibility requirements stay explicit.

## Recovery and evidence

Each updated Git repository retains its previous HEAD at local branch
`checkpoint/ecosystem-20261001`. Recovery is an explicit coordinated operation:
stop the idle managed stack, return the four repos to those matching refs while
preserving unrelated edits, restore the seven previous package versions from
the inventory, then start and verify. Do not use a broad reset/clean or erase
the nested repositories. No new Core database migration was introduced; its
revision remains `0008_drop_asset_meta`.

Ignored local evidence lives in `output/ecosystem-update-20261001/`: exact
Git/upstream inventories, applied revisions, before/after package and node
inventories, dependency plan/install reports, and runtime comparison.
Titanic receipts are in `output/titanic-e2e/ecosystem-update-20261001/`;
browser evidence is under `output/playwright/ecosystem-update-20261001/`.
The one-shot maintenance driver hit Windows' default text encoding after the
Git phase; no dependency install had started. Reading its report as UTF-8 and
running the reviewed exact package set completed the dependency phase without
reapplying Git changes.

Earlier maintenance: [September H3 ecosystem update](llm/h3-ecosystem-update.md).
