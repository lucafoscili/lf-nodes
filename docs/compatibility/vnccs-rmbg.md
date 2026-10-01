# VNCCS / RMBG-2.0 compatibility

**Historical/custom-workflow compatibility.** Current shipped LF sprite and
turnaround cards use [native `LF_BackgroundRemover` support](../BACKGROUND_REMOVER.md)
and do not require VNCCS. Previously downloaded graphs and custom workflows
may still contain `VNCCS_RMBG2`; they are not automatically migrated.

LF Nodes does not bundle or automatically patch VNCCS. For those older/custom
graphs, installing VNCCS and its model files alone does not resolve the decoder
bug below.

## Affected source and symptom

Confirmed on upstream `AHEKOT/ComfyUI_VNCCS` commit
`2206d1743f7920a7b9a21f80f03777d9ddce74c3` (metadata version 3.1.2): model
construction fails with `NameError: name 'HierarAttDecBlk' is not defined`.
This is a source-code failure, not missing weights or insufficient VRAM.

In `nodes/_vendored_birefnet.py`, `Decoder.__init__` builds a dictionary that
eagerly references the missing class, even when selecting the supported default
`BasicDecBlk`. Removing that single unsupported entry fixes construction while
preserving the default, weights, preprocessing and existing error for unsupported
decoder configurations. Local owner commit
`b843cc0caf1671e917f4567605b21269a03fc9cc` contains the fix and three CPU regression
tests; that local commit is **not an upstream installation target**.

## Temporary repair

Prefer an upstream version containing the equivalent fix when available.
Until then, this package includes the exact
[one-line patch](vnccs-rmbg.patch), so the repair does not depend on access to a
developer's local commit. It is an explicit opt-in modification to VNCCS, never
an LF import-time monkeypatch. Git must be installed, but VNCCS itself may have
been installed from either Git or a ZIP.

Wait for the Comfy queue to become idle, then stop ComfyUI through your normal
service controls. From `ComfyUI/custom_nodes/ComfyUI_VNCCS`, preview the patch:

```powershell
git --work-tree=. apply --check --verbose ../lf-nodes/docs/compatibility/vnccs-rmbg.patch
```

Only if that check succeeds, apply it:

```powershell
git --work-tree=. apply --verbose ../lf-nodes/docs/compatibility/vnccs-rmbg.patch
```

The explicit work tree keeps paths relative to the VNCCS folder even when a
ZIP install sits inside ComfyUI's Git checkout. The preview must report
`Checking patch nodes/_vendored_birefnet.py`, not `Skipped patch`.

Restart ComfyUI to replace the already-imported Python module. Retry the failed
background-removal stage; no H3 regeneration or model re-download is necessary.
If the check fails, do not force it: the source may already be fixed, have local
edits, or differ from the affected revision. Inspect the decoder table first.
Manager updates may replace this manual repair; check whether the updated
VNCCS version contains the fix before using the affected cards.

To undo **only this patch**, stop ComfyUI when idle, then run from the same folder:

```powershell
git --work-tree=. apply --reverse --check --verbose ../lf-nodes/docs/compatibility/vnccs-rmbg.patch
git --work-tree=. apply --reverse --verbose ../lf-nodes/docs/compatibility/vnccs-rmbg.patch
```

Run the second command only if the reverse check succeeds. Restart afterward;
undoing the repair restores the bug on the affected source. Do not reset the
VNCCS checkout or discard unrelated edits.

## Evidence and boundary — 2026-10-01

An untouched archive of the affected upstream source fails the eager-lookup
regression; the repaired archive passes all three CPU checks. Applying this
bundled patch to the untouched source reproduces the exact repaired bytes,
and the reverse patch restores the upstream bytes.

The same repaired implementation passed fresh saved-video cutting and full H3
sprite orchestras, including the updated Comfy ecosystem's four-step HD run.
See [release readiness](../RELEASE_READINESS.md) and the
[ecosystem update](../COMFY_ECOSYSTEM_UPDATE.md) for exact execution scope.
This does not certify every VNCCS node or a future upstream revision.

RMBG-2.0 model assets and their license remain separate prerequisites. This
patch changes no model files. Runner's model-file readiness check does not
detect the decoder defect; a ready card is not proof that VNCCS has the repair.
