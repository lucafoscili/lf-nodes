---
name: lf-node-authoring
description: Build, change, or audit public LF Nodes against the suite's established ComfyUI contracts. Use for node schemas, list/batch and mask/latent behavior, frontend widgets, events, persistent previews, durable UI history, saver receipts, tests, and Titanic acceptance. Do not use for Runner-only workflow catalogue changes unless they also change a public node contract.
---

# LF Node Authoring

Build LF Nodes as a public, domain-neutral suite. Preserve published workflows while making new behavior headless, testable, and consistent.

## Required context

1. Read [references/contracts.md](references/contracts.md) completely.
2. In the target repository, read `AGENTS.md`, `docs/ARCHITECTURE.md`, and `docs/NODE_TEMPLATE.md` completely when present.
3. Inspect the closest sibling nodes and their focused tests. Treat existing code as evidence, not automatically as authority; compare it with the contracts reference.
4. Inspect `git status --short` before editing. Preserve unrelated user and agent changes.

## Delivery workflow

### 1. Classify the node

Choose the smallest applicable family:

- scalar or JSON transform;
- image or mask transform;
- heterogeneous list seam;
- latent transform;
- viewer/output node;
- file saver;
- authoring widget whose serialized value is semantic input;
- external/provider node.

State the input cardinality, output forms, frontend role, final UI/history needs, and failure behavior before editing.

### 2. Protect the public contract

- Check whether the class name is already in `NODE_CLASS_MAPPINGS`.
- Before editing a published node, snapshot its input types, keys, defaults,
  required/optional placement, output indices/types/names, and every existing
  `OUTPUT_IS_LIST` flag. Keep an exact regression assertion: the static checker
  validates today's internal alignment but cannot detect drift from a prior
  release.
- For published nodes, keep every existing output index, type, name, and list
  flag. Append missing companions; never reorder or prepend them.
- Keep class names, input schemas, and consumed receipt keys stable unless the
  user explicitly approves a migration.
- Keep public API, examples, labels, and defaults domain-neutral.

### 3. Implement through shared helpers

- Keep node files lean. Put reusable normalization, preview, path, encoding, or event behavior under `modules/utils`.
- Use one node-wide boolean `INPUT_IS_LIST`; never use a tuple. Leave it
  disabled for unary mapped transforms. Enable it when one invocation must see
  true cardinality, validate exact pairing, or implement singleton broadcast,
  because Core maps and may repeat shorter inputs before `on_exec` otherwise.
- Normalize by semantic role. Do not blindly unwrap all inputs.
- Define and validate exact pairing or singleton broadcast for parallel inputs.
- Return the lossless list form alongside a compatible batch form for image/mask transforms, subject to published socket order.
- Use `safe_send_sync` only when the node actually emits UI state. Use stable
  generated previews for final widget state and temp resources only for
  in-flight transactions.
- Return `ui.lf_output` when final state must survive history or cached
  execution. Nodes with no useful final observational state need neither an
  event nor history payload. Replace progressive temp URLs before publishing a
  shared final payload.
- Make observational widgets optional and keep core execution headless.

### 4. Verify the contract

Run the smallest relevant checks first, then the repository gates:

```powershell
python -m compileall -q modules scripts tests
python -I scripts/quality/check_node_contracts.py
```

Add focused behavior tests for success, cardinality, list/batch order, stable errors, headless execution, and final UI/preview behavior. When frontend code changes, run its focused tests plus TypeScript/build checks.

Every new node must also pass
`modules/tests/test_frontend_widget_registry.py` and
`modules/tests/nodes/test_output_metadata_contract.py`. Run CPU-only tests via
`python -I scripts/quality/run_pytests.py -q ...`; it installs Comfy host stubs
before pytest collection. Do not accept Windows xformers/flash-attn ABI noise
from a direct pytest import as a meaningful test boundary.

For release-bound backend/frontend changes, use the checked-in canonical
Titanic authority at `scripts/quality/fixtures/E2E.json`. Refresh it from the
maintainer's user-owned projection only through `corepack yarn
sanitize:titanic`, review the sanitized diff, and commit its pinned manifest
hash. Never save over the external projection without permission. Perform live
experience checks only after inspecting the Comfy queue and coordinating
ownership; do not start GPU/provider branches merely to prove hydration.

Name the achieved Titanic level explicitly: inventory, hydration, targeted
branch execution, or full workflow execution. Never report the first three as
a full E2E pass. Full execution requires every active branch and all model,
provider, interaction, and dependency prerequisites.

Public node authoring does not add a Workflow Runner catalogue entry unless the
user separately requests one. Runner compatibility normally means generic
history/output consumption.

### 5. Report honestly

Report:

- the exact public schema and whether sockets were appended;
- batch/list and broadcast semantics;
- event, history, preview, and widget behavior;
- focused and static test evidence;
- Titanic status and the exact achieved gate level;
- any deliberate compatibility exception or deferred migration.

End exploratory work with **keep**, **defer**, or **drop**, plus the smallest next action.

## Stop conditions

Pause and ask before:

- changing an existing output index/type/name;
- renaming a serialized input used by published workflows;
- moving consumer-owned vocabulary or compatibility decisions into LF Nodes;
- starting or restarting Comfy when another task may own the queue;
- inventing a new abstraction when one verified vertical slice has not yet passed.
