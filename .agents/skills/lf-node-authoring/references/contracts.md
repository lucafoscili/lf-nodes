# LF Nodes contract reference

Use this reference to distinguish established architecture from historical drift.

## Public compatibility

- A published node's class name, input keys, defaults, and output socket indices are API.
- Preserve every existing output index, type, and name. Append a missing batch/list companion at the end.
- Renaming labels may be harmless; renaming serialized keys is not.
- `UNIQUE_ID` is diagnostic routing metadata, never semantic identity.
- LF Nodes are provider- and consumer-neutral. Consumer catalogues own private IDs, domain semantics, compatibility, and promotion.

## Registration and metadata

Each node module exports matching entries in:

```python
NODE_CLASS_MAPPINGS = {"LF_Example": LF_Example}
NODE_DISPLAY_NAME_MAPPINGS = {"LF_Example": "Example"}
```

Keep these aligned:

- `RETURN_TYPES`
- `RETURN_NAMES`
- `OUTPUT_IS_LIST`
- `OUTPUT_TOOLTIPS`
- every return path from `FUNCTION`.

Run `python -I scripts/quality/check_node_contracts.py`; it is the lightweight standalone release gate and must not import Comfy's optional GPU stack.

## Comfy list execution

`INPUT_IS_LIST` is one boolean for the whole node.

- Omitted/`False`: Core may map normal inputs and invoke the node multiple times.
- `True`: Core invokes once and list-wraps every supplied required, optional, and hidden input, including scalars and `UNIQUE_ID`.
- Never declare a per-input tuple.

With list mode disabled, Core maps before `on_exec` sees the original
collections and may repeat the last item of a shorter input. Use
`INPUT_IS_LIST = True` whenever the node itself must validate exact pairing,
implement singleton broadcast, or inspect a true list in one invocation. Unary
mapped transforms normally leave it disabled.

Normalize by meaning:

- `normalize_input_image`: flatten image containers into ordered `[1,H,W,C]` tensors.
- `normalize_input_image_batches`: flatten containers but preserve each
  coherent `[B,H,W,C]` batch when model behavior depends on samples staying
  together.
- `normalize_list_to_value`: unwrap a true scalar control.
- `normalize_input_list`: retain an intentional parallel sequence.
- `normalize_parallel_list`: enforce exact cardinality with optional singleton
  broadcast; use it before any write or expensive processing.
- Never scalar-unwrap semantic lists such as conditioning.

For parallel inputs, choose one explicit policy:

- exact cardinality only;
- singleton broadcast on one or both sides;
- a documented list seam.

Reject incompatible cardinality with a stable, readable error. Preserve input order.

`OUTPUT_IS_LIST` is a per-output tuple. When an entry is `True`, return a real Python list for that socket because Comfy extends it. Keep it aligned with all metadata and return paths.

## Image contract

Canonical transform flow:

```python
images = normalize_input_image(kwargs["image"])
processed = [transform(image) for image in images]
batch_groups, image_list = normalize_output_image(processed)
```

- A list element is `[1,H,W,C]` with RGB or RGBA channels.
- The list is the lossless ordered form.
- `normalize_output_image` groups by height, width, channels, dtype, and device.
- `batch_groups[0]` is the first encountered stack-compatible signature, not a
  complete heterogeneous result. Name it `primary_batch` at the call site.
- For interleaved `A, B, A`, the authoritative list remains `A, B, A` and the
  primary batch contains both compatible `A` items.
- New stack-compatible transforms normally expose adjacent batch and list outputs `(False, True)`.
- A heterogeneous collector such as `LF_ImageList` may intentionally be list-only.
- Preserve alpha; promote RGB to RGBA when mixing with RGBA instead of discarding alpha.

Every image node must declare one policy: first-signature compatibility batch
plus authoritative list, rejection of heterogeneous output geometry, or one
explicit shared geometry. Test interleaved resolutions so ordering and the
projection are not confused.

Do not independently fit frames when shared registration matters. Derive shared geometry from the declared reference and document what the bounds mean.

## Mask contract

- Lossless mask list elements are `[1,H,W]`.
- Batch masks are `[B,H,W]`.
- Accept `[H,W]`, `[B,H,W]`, and unambiguous singleton-channel 4-D forms.
- Reject ambiguous multi-channel masks; do not silently slice a channel.
- Use `normalize_masks_for_images` for exact or singleton-broadcast image/mask pairing.

## Latent contract

- Require a dict with a non-empty 4-D tensor under `samples`.
- Preserve metadata without aliasing the caller's dict.
- When splitting a latent batch, slice batch-coupled metadata such as `noise_mask` and `batch_index` consistently.
- Validate metadata cardinality instead of silently misaligning it.

Canonical flows:

- `normalize_input_latent_list` preserves heterogeneous shapes and complete
  item order;
- `normalize_input_latent_batches` validates and preserves each coherent
  latent batch for temporal or batch-sensitive model calls;
- `normalize_output_latent` splits one coherent latent batch;
- `normalize_output_latents` returns the first-signature compatibility batch
  plus the authoritative ordered latent list;
- `normalize_input_latent` merges compatible entries and requires
  `noise_mask` and `batch_index` to be present everywhere or nowhere. Partial
  batch-coupled metadata fails with a stable error instead of being dropped.

## Events and final UI

Use:

```python
safe_send_sync("examplenode", payload, kwargs.get("node_id"))
```

- Pass the lowercase unprefixed suffix. The helper adds `lf-`.
- The helper copies the payload, unwraps list-mode node IDs, adds the canonical `node` key, and fails safely without a WebSocket.
- Direct `PromptServer` calls are for route/infrastructure registration, not node UI emission.
- Live events are transient.

If a node has no useful final observational state, it needs neither an event nor
`ui.lf_output`. `safe_send_sync` is mandatory only for actual node UI emission.
Progressive temp URLs may appear in live events but must be replaced with
generated-preview URLs before the final shared payload.

When final state must be available from Comfy history or cached execution:

```python
return {
    "ui": {"lf_output": [final_payload]},
    "result": (batch, image_list, receipt),
}
```

Use the same final payload for the live event and `ui.lf_output`. Keep every UI value list-wrapped because Core flattens mapped UI results.

Set `OUTPUT_NODE = True` only when viewer/output behavior must execute without a downstream consumer.

## Preview lifecycle

Final preview URLs must survive restart and saved-widget hydration:

- use `cache_generated_preview`, `create_cached_masonry_node`, or `create_cached_compare_node`;
- store content-addressed PNGs under Comfy input;
- return `/view` URLs with `type=input` and no cache-busting nonce;
- bound preview resolution;
- preserve RGB/RGBA mode;
- never put base64 images or temp-file links into durable history/widget state.

Use `resolve_filepath`, `TempFileCache`, and progressive temp previews only for transactional/in-flight resources. Clean them at the transaction boundary. Do not retain dead cache plumbing after migrating a node to generated previews.

## Frontend and headless use

For every public class:

- add it to the `NodeName` enum;
- add exactly one `NODE_WIDGET_MAP` entry;
- use `[]` intentionally when native Comfy UI is sufficient;
- add/update the mapping test.

For `LF_FooBar`, the live event is `lf-foobar`; pass `foobar` to `safe_send_sync`.

Observational widget inputs are optional, ignored by core execution, and may be omitted from raw `/prompt` calls. A custom authoring widget may be required only when its serialized value is the actual domain input; give that input a meaningful name such as `document` or `body`.

Legacy compatibility exceptions currently use required semantic inputs named `ui_widget`:

- `LF_KeywordToggleFromJSON`
- `LF_WriteJSON`
- `LF_LLMChat`
- `LF_LLMMessenger`

Do not copy this pattern into new nodes. Renaming these fields requires an explicit workflow migration.

## Saver/output contract

- Resolve destinations against Comfy's authorized output root.
- Reject escapes before writing.
- Use the established extension and naming behavior; avoid timestamps unless the contract requests them.
- Prefer atomic writes where partial files would be misleading.
- Return relative artifact names and a deterministic machine-readable receipt through `ui.lf_output` when Runner/history consumes the result.
- Include only provenance and integrity fields that downstream recovery actually needs.

## Test matrix

Minimum focused tests, selected proportionately:

1. mapping/display metadata and headless schema;
2. raw single input and batch/list input;
3. output list and batch shapes/order;
4. alpha/mask/latent metadata preservation;
5. exact pairing, each supported singleton broadcast, and mismatch failure;
6. stable machine-readable or readable failures;
7. missing optional widget and list-wrapped `UNIQUE_ID`;
8. live event plus durable `ui.lf_output` where required;
9. restart-stable preview URL and RGB/RGBA file mode;
10. save/reload socket compatibility for published nodes.

For a published change, snapshot and assert the prior input types, input keys,
defaults, required/optional placement, output indices/types/names, and every
existing `OUTPUT_IS_LIST` flag. The static checker cannot infer release-to-
release schema compatibility.

Repository checks:

```powershell
python -m compileall -q modules scripts tests
python -I scripts/quality/check_node_contracts.py
python -I scripts/quality/run_pytests.py -q modules/tests/test_frontend_widget_registry.py
python -I scripts/quality/run_pytests.py -q modules/tests/nodes/test_output_metadata_contract.py
corepack yarn test
corepack yarn build:ts
```

Run focused Python tests through `scripts/quality/run_pytests.py`, which installs
host stubs before pytest can import the package. Fatal-looking Windows
xformers/flash-attn ABI output from a direct pytest command is not useful test
evidence. The standalone checker must remain independent of pytest.

## Titanic experience check

Canonical repository authority:

`scripts/quality/fixtures/E2E.json`

The maintainer's Comfy user workflow is a working projection, not the published
authority. Refresh the repository fixture deliberately with `corepack yarn
sanitize:titanic`; the sanitizer preserves topology, removes private/transient
state, and the fixed manifest pins its exact SHA-256. Review and commit both the
fixture and `scripts/quality/titanic_cases.json`.

For release-bound contract changes:

1. inspect the live queue and coordinate service ownership;
2. run the checked-in fixture through the programmatic gate rather than replacing user changes;
3. create/hydrate affected nodes and inspect widget state;
4. verify existing sockets did not shift;
5. execute only bounded CPU-safe branches unless GPU/provider execution is explicitly in scope;
6. ask before saving over the user-owned external projection; when authorized,
   refresh through the sanitizer, save/reload, and recheck final preview/state hydration.

Report inventory, hydration, targeted branch execution, and full workflow
execution as distinct gate levels. Do not say Titanic or E2E "passed" without
qualifying the level. Full workflow execution means every active branch ran
with its required models, providers, user interactions, and dependencies.

Unit tests establish mechanics; Titanic establishes the actual Comfy experience.

Node authoring does not add a Workflow Runner catalogue entry unless separately
requested. Runner compatibility normally means that its generic history/output
consumer can understand the node's durable result.
