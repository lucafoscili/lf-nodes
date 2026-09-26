# LM Studio model lifecycle

`LMS Load Model` (`LF_LMSLoadModel`) loads one already-downloaded LLM using its
exact LM Studio model key. If that key has one loaded instance, it reuses it.
It fails on multiple instances, missing keys, or embedding models. Loading uses
LM Studio's configured defaults; these nodes do not download models.

Connect `instance_id` to both the prompt-maker's `model` input and
`LMS Unload Model`'s `instance_id` input. Connect the completed prompt to Unload's
`prompt` input, then connect Unload's `prompt` output to downstream generation:

```text
LMS Load Model.instance_id -> Prompt Maker.model
LMS Load Model.instance_id -> LMS Unload Model.instance_id
Prompt Maker.prompt       -> LMS Unload Model.prompt
LMS Unload Model.prompt    -> downstream generation prompt
```

The prompt passes through unchanged only after the exact instance is unloaded
or confirmed absent. An unload error stops that downstream branch. Placing an
unload node on the canvas alone does not sequence execution; the connected
prompt path creates the dependency. Independent branches can still run in
parallel, so every consumer of this model must finish before this unload, and
any downstream model-loading branch that must wait also needs a dependency on
the released prompt.

Both nodes accept `url` (default `http://127.0.0.1:1234/api/v1/chat`) and optional
`timeout` (120 seconds). Use the same server URL as the prompt maker; the nodes
derive its native model-management routes. Authentication, if enabled, reads
`LM_API_TOKEN` or `LM_API_TOKEN_FILE` on the Comfy server. Native chat, automatic
model discovery, and lifecycle operations all use this authentication, so the
whole connected chain works with an authenticated LM Studio server. The token
is not sent to generic OpenAI-compatible endpoints or saved in node widgets.

Each node consumes one scalar value per input, including Comfy's singleton
list envelopes; multi-item inputs fail before a lifecycle request. Both nodes
recheck external residency on every queued execution, even if their inputs are
unchanged. Unload deliberately has no standalone output-node behavior: connect
its prompt output to the generation/output branch. Native Comfy widgets suffice;
there are no custom UI events, previews, or saved history receipts.

A failed or cancelled prompt-maker branch does not execute downstream unload.
The model may remain loaded and can be reused on the next run. A request timeout
can occur after a server-side operation completes; retry checks the inventory.
An externally shared instance is also released when selected through this graph;
use these nodes when this workflow owns that model's residency.

Implementation: `modules/nodes/llm/lm_studio_models.py`; transport:
`modules/utils/helpers/api/lm_studio_lifecycle.py`; focused checks:

```powershell
python -I scripts/quality/run_pytests.py -q modules/tests/nodes/llm/test_lm_studio_models.py
```

The transport follows LM Studio's native [model list](https://lmstudio.ai/docs/developer/rest/list),
[load](https://lmstudio.ai/docs/developer/rest/load), and
[unload](https://lmstudio.ai/docs/developer/rest/unload) contracts. CPU mocks cover
reuse, exact-instance release, ordering, errors, authentication, and repeated
runs. Live loading/unloading needs a separately coordinated model session.
