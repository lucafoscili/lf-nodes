# LF Nodes contributor guide

## Public node contracts

- Python nodes live in `modules/nodes/<domain>`, import their package
  `CATEGORY`, use `FUNCTION = "on_exec"`, and declare local class/display maps.
- Normalize by semantic type. IMAGE usually becomes ordered `[1,H,W,C]` items;
  list seams and batch-native algorithms are explicit exceptions. Use
  `normalize_input_list` for sequences, `normalize_list_to_value` for scalars,
  and `normalize_conditioning` for CONDITIONING.
- `INPUT_IS_LIST` is one boolean for the whole node, never a per-input tuple.
  With `True`, required, optional, hidden, and scalar inputs are list-wrapped.
  With `False`, Core maps first and may repeat the final shorter input. Enable
  list mode when the node itself must validate cardinality or broadcasting.
- Parallel collections require an explicit exact-pair, singleton-broadcast, or
  mismatch policy.
- Image products normally expose batch plus list. `OUTPUT_IS_LIST` is per
  socket and must align with names, types, tooltips, and all return paths. The
  item list is authoritative; a heterogeneous primary batch is only the first
  encountered stack-compatible signature.
- Published input type/key/default/required placement and output
  index/type/name/list flag are API. Snapshot the prior schema, append missing
  outputs, and never reorder, prepend, or silently retag existing sockets.

## UI, previews, and headless behavior

- When a node has useful UI state, emit it through
  `safe_send_sync("foobar", payload, node_id)`;
  `LF_FooBar` maps to `lf-foobar`. Do not call `PromptServer` directly from a
  published node for UI feedback.
- Live events are transient. Return final history/Runner state through
  `ui.lf_output` and reuse the final live payload. Nodes with no useful final
  observational state need neither an event nor a history payload.
- Observational widgets are optional and must not control execution. Required
  authoring widgets serialize the real input and need an equivalent raw
  prompt/API value.
- Final previews use `cache_generated_preview` or cached masonry/compare
  builders. `TempFileCache` is only for in-flight editing/progress state; its
  URLs and base64 previews do not belong in durable history.
- Add every node to the exhaustive frontend `NodeName` and `NODE_WIDGET_MAP`;
  use `[]` intentionally when native Comfy UI is sufficient.

## Shared implementation

- Keep node declarations lean. Put repeated transforms, validation, tensor
  geometry, filesystem safety, receipts, and dataset builders under
  `modules/utils`.
- Keep Comfy core untouched and heavy dependencies lazy where possible.
- Keep public names, defaults, docs, and examples consumer-agnostic.
- Workflow Runner controllers handle HTTP, services own behavior, models define
  schemas, and adapters isolate external systems.
- Public node work does not add a Runner catalogue entry unless separately
  requested; normal compatibility is generic history/output consumption.

## Verification

- Run `python -I scripts/quality/check_node_contracts.py`.
- Run CPU-only pytest through
  `python -I scripts/quality/run_pytests.py -q ...`; add coverage for order,
  shape, pair/broadcast policy, failure paths, event payloads, durable history,
  and receipts.
- Include `modules/tests/test_frontend_widget_registry.py` and
  `modules/tests/nodes/test_output_metadata_contract.py` for new nodes.
- Run `corepack yarn test`, TypeScript checks, and a full build for frontend
  changes.
- Finish release-bound backend/frontend contract changes against the audited repository authority at
  `scripts/quality/fixtures/E2E.json`: hydrate the real workflow, confirm
  sockets, and execute only the in-scope branch. Refresh it from the maintainer
  working projection with `corepack yarn sanitize:titanic`; the sanitizer must
  preserve topology and fail closed on credentials, private paths, volatile
  sessions/previews, and adult-content vocabulary. Coordinate queue ownership
  before live execution and verify durable preview hydration after reload.

## References

- `docs/ARCHITECTURE.md`
- `docs/NODE_TEMPLATE.md`
- `docs/WORKFLOW_RUNNER.md`
- `modules/utils/helpers/comfy/safe_send_sync.py`
- `modules/utils/helpers/logic/`
- `modules/utils/helpers/ui/generated_preview.py`
- `web/src/helpers/manager.ts`
