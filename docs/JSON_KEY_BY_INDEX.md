# Get Key From JSON by Index

`LF_GetKeyFromJSONByIndex` selects a key deliberately, unlike the seeded random
selection node. Required inputs are `json_input` (JSON object) and `index`
(integer, default 0). Output socket 0 is `string` (STRING, not a list).

Keys follow object insertion order: index 0 selects the first key. Values are
ignored. Empty objects, non-string keys, non-integer indices, and out-of-range
indices fail clearly; indices never wrap. Normal Comfy mapped execution applies;
this is not a batch-pairing node. Existing random-node sockets are unchanged.

The optional code widget shows the selected key. Its live LF event is mirrored
in `ui.lf_output`; the frontend restores the preview from execution history.
Headless callers may omit the widget and node ID.

## Titanic checkpoint

Nodes 595 → 596 → 597 form an isolated CPU example beside the JSON group:
`{"Zebra":"","Alpha":"","Middle":""}` → index 1 → `Alpha`.
This deliberately distinguishes insertion order from alphabetical order.
The manifest case is `cpu.json-key-index`.

2026-09-07: keep. User confirmed live node use. Focused Python checks passed
(25 tests, 5 subtests), frontend suite passed (585 tests), TypeScript and Vite
builds passed, and Titanic sanitizer/gate unit checks passed (24 tests).
Canonical Titanic inventory and real frontend hydration passed. Targeted
execution was deferred because another generation batch occupied the queue;
this is not a full Titanic execution pass.

Next: when the queue is idle, run `corepack yarn test:titanic --full --case
cpu.json-key-index --accept-warm-cache` and inspect the Alpha preview.
