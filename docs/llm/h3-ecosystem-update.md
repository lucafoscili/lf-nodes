# Comfy ecosystem update — 2026-09-26

This host update prepares the H3 learned latent-upscale experiment. It does not
change the accepted phone orchestra or its default renderer. LF Nodes baseline
was `66a5a95`; the offline experiment builder is `813a77f`.

## Updated environment

Comfy Core fast-forwarded on its existing master branch from
`3216c62e9962c3babd28a4dfea6e5aef50b8fe16` to
`79be670e2d9be63e238785af307369d2b9039ed1`. Core reports version 0.37.0;
the exact commit, not the latest release tag, identifies this installation.
Existing storage-related edits and untracked files were preserved without
stashing or resetting. The queue was empty before stopping the task-owned host.

| Component | Before | After |
| --- | --- | --- |
| Frontend | 1.51.9 | 1.53.6 |
| Kitchen | 0.2.31 | 0.2.35 |
| AIMDO | 0.4.15 | 0.5.5 |
| Workflow templates | 0.11.50 | 0.11.70 |
| Embedded docs | 0.5.10 | 0.5.12 |
| MiniMax H3 Turbo | 55fee86 | 4274783 |
| MiniMax H3 Spectrum | 9395bf9 | 5161f04 |
| Manager | dd3ab9cf | 9c29dc68 |
| ControlNet Aux | 12f3564 | 59b1fc4 |
| VNCCS | 7c3281f | 2206d17 |
| See-through | eb6fa6f | 98d754b |
| Inpaint | 1.0.4 | 1.4.3 |
| Tooling | 3.0.0 | 3.3.0 |
| SeedVR2 | 2.5.22 | 2.5.24 |

The two Krea repositories and IPAdapter were already current. LF Nodes' local
commits were not pulled over. Ultimate SD Upscale and AI GameDev were skipped
because their repositories contain local/nested changes.

The pinned Core requirements changed nine distributions, including template
subpackages. Manager's new `nh3==0.3.7` requirement was installed separately
without dependencies. PyTorch remains **2.11.0+cu130**; torchvision and torchaudio
remain **0.26.0+cu130 / 2.11.0+cu130**. No blanket pip upgrade was performed.
Optional new VNCCS features and ONNX GPU acceleration dependencies were not
installed: they are not needed for node registration or this H3 experiment.
`pip check` passed after the environment changes.

The three registry packages were updated through Manager's exact-version
package installer after complete directory backups and archive inspection.
Their dependencies were unchanged; no install.py, postinstall callback, or
package fixer was executed. All 110 tracked Python files parsed successfully.

## Installed experiment dependency

Only [ComfyUI-MinimaxH3-Latent-Upres](https://github.com/benjiyaya/ComfyUI-MinimaxH3-Latent-Upres)
was added, at `438e31e4846d2d4d52cbe51e0c8d1d857d1ffb43`. It embeds the learned
upscaler, so the LBH node package was not installed alongside it.

Checkpoint: `minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors`, 690,592,992
bytes, directly in `ComfyUI/models/latent_upscale_models/`. SHA-256 verified
against the publisher's Hugging Face LFS metadata:
`4f57821f5837f32f7142b67d815606dbd7550f194e5c769f7d6c3f83b146a5e6`.
Only safetensors weights were downloaded; no pickle checkpoint was loaded.

## Runtime and recovery

The first updated startup loaded all installed node packages, including LF and
the new upscaler. Core and the 390×844 phone orchestra form hydrated and were
visually inspected with Playwright. This is hydration, **not** full-suite E2E.
The focused existing renderer/orchestra tests passed (71), as did the offline
experiment wiring tests (3). The paired live H3 render subsequently succeeded in
391.46 seconds; see [the results](h3-latent-upscale-trial.md).

The final restart was rejected by execution policy before running. No alternate
shutdown/restart mechanism was attempted. Comfy remains running and its queue
was confirmed empty afterward. The three registry package updates are on disk
but require a normal user-initiated Comfy restart before their new code is
considered runtime-verified. The Core, Git updates and upscaler were already
active during the successful trial.

Core migrated its asset database from revision 0006 to 0008. A separate offline
backup was taken before startup. The old database had zero assets, references,
or reference metadata, and only 24 unreferenced built-in category tags; the new
catalog is empty. The migration warning therefore does not indicate loss of
user media or per-asset metadata on this host. Runner history is a separate
database and was not changed by this migration. Manager migrated its legacy
configuration with its own backup, retaining the normal security level.

The frontend still logs an AI GameDev extension import-path error; that dirty
package was deliberately not modified. Core's default graph and Runner remain
usable. Existing legacy-extension deprecation warnings are not a clean-console
pass. Optional H3 TAESD preview weights are absent, so this run has no TAESD live
preview; final rendering does not depend on those weights.

Local receipts and backups live under `output/h3-upscale-20260926/` (ignored,
not disposable): `core-before.txt`, `core-requirements-target.txt`,
`environment-before.txt`, `environment-after.txt`, `comfyui-before.db`,
`custom-git-updates.json`, `cnr-package-updates.json`, and `cnr-backup/`.
These contain the exact prior revisions, package versions, and backup paths.

Recovery is explicit, not automatic: stop an idle owned host, preserve its
current state, restore the matching code/package snapshot and dependencies,
and restore the pre-migration Core database only together with old Core.
Do not run a broad reset or merge older registry backups into newer directories.
The existing LAN proxy, TLS, access controls, reference images, model weights,
and accepted video were not replaced.

**Keep:** the reviewed updates and successful H3 execution. **Pending:** user
restart and import verification of the three registry packages. **Defer:**
unrelated optional dependency additions and dirty repositories.
See [the experiment](../../scripts/experiments/README.md) for the separate quality
question; successful imports alone do not establish upscaled video quality.
