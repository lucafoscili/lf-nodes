# LF Nodes architecture

This document defines the public node contract shared by the Python suite, its
LF Widgets frontend, and headless ComfyUI clients. Published node sockets and
serialized inputs are APIs: improve them without invalidating saved workflows.

## Repository layout

```text
modules/
  nodes/<domain>/        # Lean public node declarations and orchestration
  utils/
    filters/             # Reusable image operations
    helpers/
      comfy/             # Comfy boundaries and safe event delivery
      logic/             # IMAGE, MASK, LATENT, list, and JSON normalization
      ui/                # Dataset builders and generated-preview storage
web/src/                 # LF Widget hydration and exhaustive node mapping
modules/workflow_runner/ # Local workflow catalogue and execution app
```

Keep reusable transformations and normalization in `modules/utils`; keep node
sources focused on declaring their public inputs/outputs and composing helpers.

## Execution and input normalization

Image transforms typically flatten incoming containers into ordered
`[1, H, W, C]` tensors, process them per image, and reassemble only
stack-compatible outputs. List-seam and batch-native nodes may intentionally
preserve lists or operate on a coherent batch directly.

Normalize every input by its meaning:

- `normalize_input_image` flattens IMAGE tensors/containers into ordered
  `[1,H,W,C]` items.
- `normalize_input_image_batches` flattens containers while preserving each
  coherent `[B,H,W,C]` batch for temporal or batch-sensitive models.
- `normalize_input_list` preserves an intentional sequence.
- `normalize_list_to_value` unwraps a scalar control.
- `normalize_parallel_list` applies explicit singleton broadcast or rejects a
  cardinality mismatch before work begins.
- `normalize_conditioning` preserves CONDITIONING as `[tensor, metadata]`
  pairs. Never scalar-unwrap CONDITIONING.
- The MASK and LATENT helpers preserve order and slice per-item metadata.

`INPUT_IS_LIST` is one node-wide boolean, never a per-input tuple. When it is
`True`, Comfy invokes the node once and list-wraps every supplied required,
optional, and hidden input, including scalar controls and `UNIQUE_ID`. Normalize
each one explicitly. Omit it or set it to `False` for Comfy's normal mapped
execution. In mapped execution Core may invoke the node before `on_exec` sees
the original collections and repeat the last item of a shorter input. Use
`INPUT_IS_LIST = True` whenever the node itself must inspect true cardinality,
validate exact pairing, or implement singleton broadcasting; unary mapped
transforms normally leave it disabled.

When two collections meet, declare the policy in code and tests. Use exact
pairing, singleton broadcast, or a clear mismatch error; never silently reuse
or discard items.

## Output contracts and socket compatibility

`OUTPUT_IS_LIST` is per socket. It must be a literal boolean tuple aligned with
`RETURN_TYPES`, `RETURN_NAMES`, `OUTPUT_TOOLTIPS`, and every return path. A slot
marked `True` must return a real list of logical items—returning a string or
tensor makes Comfy extend it into characters or slices.

For image-producing nodes, expose both forms:

```python
RETURN_TYPES = (Input.IMAGE, Input.IMAGE)
RETURN_NAMES = ("image", "image_list")
OUTPUT_IS_LIST = (False, True)

batch_groups, image_list = normalize_output_image(outputs)
primary_batch = batch_groups[0]
return (primary_batch, image_list)
```

`normalize_output_image` groups by height, width, channels, dtype, and device.
`primary_batch` is only the first encountered stack-compatible signature;
`image_list` is the authoritative, lossless heterogeneous form. For an
interleaved `A, B, A` result, the list stays `A, B, A` and the primary batch
contains both `A` items. Every image node must explicitly choose this
compatibility projection, reject heterogeneous geometry, or derive one shared
geometry. Deliberate list constructors such as `LF_ImageList` and non-image
nodes can expose only the form their semantics require.

Published socket index, type, and name are workflow compatibility surface.
Never reorder, prepend, or retag an existing output. Append a missing companion
or new datum, even when a brand-new node would place it adjacent to its batch.

MASK follows `[B,H,W]` plus `[1,H,W]` item-list conventions. LATENT item lists
must slice `samples`, `noise_mask`, and `batch_index` consistently instead of
copying batch-wide metadata into each sample.

LATENT normalization has two deliberate seams. Use
`normalize_input_latent_list` when heterogeneous shapes or complete item order
must survive, `normalize_input_latent_batches` when a model must receive each
source batch intact, `normalize_output_latent` to split one coherent batch, and
`normalize_output_latents` to produce the first-signature compatibility batch
plus the authoritative item list. Merging latents with
`normalize_input_latent` requires `noise_mask` and `batch_index` to be present
on every entry or omitted from every entry; partial batch-coupled metadata
fails closed instead of being silently dropped.

## Frontend events and durable history

Node UI events go through the shared boundary:

```python
from ...utils.helpers.comfy import safe_send_sync

payload = {"value": "Downloading..."}
safe_send_sync("loadclipsegmodel", payload, node_id)
```

Pass the lowercase unprefixed suffix. `safe_send_sync` adds `lf-`, copies the
payload, unwraps list-mode node IDs, supplies the canonical `node` key when an
ID is provided, and is a no-op when WebSocket infrastructure is unavailable.
Direct `PromptServer` use is for routes and infrastructure, not published node
UI emission.

Live events are transient. If final UI state must survive cached execution or
be available in Comfy history and Workflow Runner, return the same final
payload through `ui.lf_output`:

```python
safe_send_sync("mynode", final_payload, node_id)
return {
    "ui": {"lf_output": [final_payload]},
    "result": (batch, image_list),
}
```

UI values are lists because Comfy combines results across mapped executions.
Use `OUTPUT_NODE = True` only for viewers/savers that must execute without a
downstream consumer, not as a default for transforms. Consumed `lf_output`
keys are public compatibility surface even when different features use
different payload shapes.

Nodes with no useful final observational state need neither a frontend event
nor `ui.lf_output`. Progressive temp URLs may drive live feedback, but replace
them with restart-stable generated-preview URLs before publishing the final
shared payload.

## Preview lifecycle

Final preview URLs serialized into widget state or `ui.lf_output` use
`cache_generated_preview`, `create_cached_masonry_node`, or
`create_cached_compare_node`. They are content-addressed under Comfy input,
survive restarts, deduplicate identical bytes, and remain disposable through
the preview-cache clear action.

`TempFileCache`, editing-session assets, and progressive preview resources are
transactional in-flight state. They may be replaced or removed, so never put
their URLs in durable final history or serialized widget state. Do not retain
base64 previews in history.

## Widgets and headless execution

Add every backend node class to the frontend `NodeName` enum and exactly one
entry in `NODE_WIDGET_MAP`; use `[]` intentionally when native Comfy UI is
sufficient. The map is exhaustive. `LF_FooBar` emits `lf-foobar`, so the suffix
passed to `safe_send_sync` is `foobar`.

Display/diagnostic `ui_widget` inputs are optional and observational. Raw
`/prompt` clients may omit them, and execution must tolerate a missing or
list-wrapped `UNIQUE_ID`. Custom authoring widgets whose serialized value is
the actual semantic input remain required; headless clients provide the same
raw string/JSON input. The legacy required `ui_widget` inputs on
`LF_KeywordToggleFromJSON`, `LF_WriteJSON`, `LF_LLMChat`, and `LF_LLMMessenger`
are compatibility exceptions, not a pattern for new nodes.

## Interactive editing

Editing flows intentionally use a transactional dataset and temporary assets
while a user is working. The editing session owns model components, prompts,
masks, and completion state. Once the operation finishes, only final outputs
and restart-safe previews cross the durable boundary.

## Verification

Run checks in proportion to the change:

1. `python -I scripts/quality/check_node_contracts.py`
2. Focused Python tests for normalization, ordering, broadcasting, failures,
   events, receipts, and history payloads.
3. `modules/tests/test_frontend_widget_registry.py` and
   `modules/tests/nodes/test_output_metadata_contract.py` for every new node.
4. `corepack yarn test`, `corepack yarn build:ts`, and a full frontend build
   when widget code or deploy assets change.
5. The canonical Titanic maintainer experience check at
   `scripts/quality/fixtures/E2E.json`.

Run CPU-only unit tests through the pre-collection host boundary:

```powershell
python -I scripts/quality/run_pytests.py -q <focused test paths>
```

It installs inert Comfy/server doubles before pytest can import the repository
package. If a direct pytest command emits optional CUDA/xformers/flash-attn ABI
noise, rerun it through this boundary rather than treating a fatal-looking DLL
trace as product evidence.

Titanic ships as an audited, recoverable fixture under
`scripts/quality/fixtures/E2E.json`. The maintainer's Comfy workflow is a
working projection, not the sole authority. Refresh the repository fixture with
`corepack yarn sanitize:titanic`: that deterministic projection preserves graph
topology while removing private filenames and paths, transient editor state,
history, preview URLs, credentials, and adult-content references. The gate pins
the resulting bytes in `scripts/quality/titanic_cases.json`.

After backend/frontend contract changes, load and hydrate Titanic, verify
existing sockets have not shifted, and execute only the in-scope CPU-safe
branches. Coordinate queue ownership before live execution. Confirm final
preview/state hydration after reload without unintentionally running
provider/GPU branches. A custom case manifest is deliberately unsupported by
the canonical gate; reviewed resource classes and grants come only from the
checked-in manifest.

Report the achieved Titanic gate precisely:

- **inventory**: the expected node types and links are present;
- **hydration**: the workflow loads and its frontend widgets mount correctly;
- **targeted execution**: named bounded branches execute successfully;
- **full workflow execution**: every active branch executes with all required
  models, providers, interactions, and dependencies available.

Never call inventory, hydration, or targeted execution a full E2E pass. A
workflow may hydrate perfectly while interactive, provider-backed, GPU, or
unloaded-model branches remain unexecuted.

Adding or changing a public node does not automatically add a Workflow Runner
catalogue entry. Runner compatibility means generic consumption of the node's
outputs/history unless a workflow declaration is separately requested.

## Extension rules

- Keep LF APIs, docs, examples, and defaults consumer-agnostic.
- Add abstractions after a demonstrated repeated need, not before the first
  working experience.
- Keep Comfy core untouched; normalize at LF's boundary.
- Reuse helpers for filesystem safety, previews, events, and tensor shapes.
- Test the actual experience. Types, hashes, and unit tests do not establish
  that a widget hydrates or an image looks correct.
