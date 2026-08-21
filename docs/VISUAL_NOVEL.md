# LF Visual Novel Nodes

The visual-novel node suite is a CPU-only, target-neutral authoring and
preview contract. It builds a symbolic narrative graph, validates and
compiles that graph deterministically, and previews one fixture state. It
does not own a renderer, live application state, persistence, networking, or
an engine adapter.

All four nodes are in the `✨ LF Nodes/Visual Novel` category. The public
contract uses typed LF sockets and one JSON document widget per declaration;
the older collection of separate JSON widgets is not supported.

## Nodes and public inputs

### VN State (`LF_VNState`)

Required inputs:

- `fixture_id` (`LF_ID`, kind `fixture`): persistent fixture identity.
- `state_body` (`LF_TEXTAREA`): one strict-JSON object containing fixture
  values. The default is `{ "markers": [] }`.

Optional input:

- `profile_ref` (`LF_REF`, kind `profile`): an optional consumer-owned profile
  reference.

Outputs are `state` (`LF_VN_STATE`), `state_object` (`JSON`), and
`canonical_json` (`STRING`). The state envelope is `lf.vn.state.v1` and has
`fixtureId`, `values`, and `appliedEffectIds`, with an optional `profileId`.

### Scene Spec (`LF_SceneSpec`)

Required inputs:

- `scene_id` (`LF_ID`, kind `scene`): persistent scene identity.
- `title` (`STRING`): author-facing title (also used as the reference label).
- `scene_body` (`LF_TEXTAREA`): one strict-JSON object with exactly these root
  fields: `participants`, `entryPredicate`, `beats`, `choices`, and
  `artRequests`.

`scene_body` is the complete declaration document. A beat needs an `id` and
either `text` or `localizationKey`; a choice needs an `id` and either `label`
or `localizationKey`, and may contain `visibilityPredicate`,
`availabilityPredicate`, `effects`, and `nextSceneId`; an effect needs `id`,
`type`, and object `payload`; an art request needs `id` and may contain
`slots`, `direction`, and `metadata`. Participants are semantic IDs. Optional
`metadata` fields are objects. Declaration `source` fields are produced by
the node and are not author inputs.

Optional input:

- `graph` (`LF_VN_GRAPH`): an existing declaration chain. Leave it empty for
  the first declaration, then connect each preceding `graph` output.

Outputs are `graph` (`LF_VN_GRAPH`), `scene` (`JSON`), and `scene_ref`
(`LF_REF`, kind `scene`).

### VN Switch (`LF_VNSwitch`)

Required inputs:

- `state` (`LF_VN_STATE`): fixture state used only for route preview.
- `switch_id` (`LF_ID`, kind `switch`): persistent switch identity.
- `switch_body` (`LF_TEXTAREA`): one strict-JSON object with exactly
  `cases` and `fallback`.

Each case has `id`, `when`, and `targetSceneId`. `fallback` is either `null`
or an object with `id` and `targetSceneId`; it has no `when` predicate. Cases
are evaluated in order and the first matching case is selected. Every case
and the fallback remain in the authored graph.

Optional input:

- `graph` (`LF_VN_GRAPH`): the existing declaration chain.

Outputs are `graph` (`LF_VN_GRAPH`), `selected_case` (`JSON`),
`target_scene_id` (`LF_REF`, kind `scene`), and `preview_report` (`JSON`).

### Compile VN (`LF_VNCompile`)

Required inputs:

- `graph` (`LF_VN_GRAPH`): the completed declaration chain.
- `state` (`LF_VN_STATE`): fixture state for preview; it is not embedded in
  the authored bundle.
- `workflow_id` (`LF_ID`, kind `workflow`): persistent workflow identity.
- `entry_scene_id` (`LF_REF`, kind `scene`): bundle-local entry scene.
- `selected_choice_id` (`LF_REF`, kind `choice`): optional choice to replay
  once against the fixture; an empty value means no replay.

Optional input:

- `ui_widget` (`LF_CODE`): the node's optional UI/diagnostic widget value.

Outputs are `bundle` (`LF_VN_BUNDLE`), `preview` (`JSON`), `validation`
(`JSON`), `derived_state` (`LF_VN_STATE`), and `canonical_bundle` (`STRING`).
Compilation exposes `lf.vn.bundle.v1`, `lf.vn.preview.v1`, and
`lf.vn.validation.v1` documents.

## Authoring identity and one-body textarea contract

`LF_ID` is an LF-owned persistent identity, not a free-form label. The
authoring UI generates a value once when the widget has an empty default and
keeps that value in the node. `lf_id_kind` identifies the namespace (`fixture`,
`scene`, `switch`, or `workflow`); the scene ID uses `title` as its friendly
label. Regenerating an ID requires confirmation and remaps matching typed
references in the current graph. Semantic IDs must start with a letter or
digit, use only ASCII letters, digits, `.`, `_`, `:`, `/`, and `-`, and be at
most 200 characters.

`LF_REF` controls show friendly labels but store the immutable ID. Candidates
come from matching `LF_ID` widgets and from IDs found at the configured paths
inside LF VN textareas. Typed connections are also valid. A reference that is
not currently available is shown as unresolved; the control does not invent a
replacement ID.

Each body is exactly one `LF_TEXTAREA` value serialized as JSON text:

- Scene paths materialized by the UI are `/beats/*` (`beat`), `/choices/*`
  (`choice`, labeled by `label`), `/choices/*/effects/*` (`effect`), and
  `/artRequests/*` (`art-request`). Its reference picker covers
  `/choices/*/nextSceneId` (`scene`).
- Switch paths materialized by the UI are `/cases/*` (`switch-case`) and
  `/fallback` (`switch-fallback`). Its reference pickers cover
  `/cases/*/targetSceneId` and `/fallback/targetSceneId` (`scene`).
- VN State has no child-ID paths: `state_body` is opaque fixture values.

The UI parses and formats a body only after valid JSON is entered. On valid
JSON it clones the document and fills only missing configured child `id`
fields; authored IDs are preserved. Invalid raw text remains visible and is
marked as an error. Queue/workflow serialization does not call this
normalizer, so IDs are not silently created at execution time.

## Headless and fail-closed behavior

The Python nodes do not generate identities. Headless prompts, exported
workflow JSON, and API clients must provide every top-level `LF_ID` value and
every nested ID required by the body validators (beats, choices, effects, art
requests, switch cases, and non-null fallback). They must also provide
`workflow_id`, `entry_scene_id`, and any selected/reference values explicitly.
Missing or malformed IDs fail closed with a contract diagnostic; there is no
index-based or title-based fallback. The state body and declaration bodies
must be strict JSON objects with their required root fields.

Strict parsing rejects malformed JSON, duplicate object keys, `NaN`,
`Infinity`, `-Infinity`, unsupported fields, invalid root types, and non-finite
or non-JSON values. A semantic reference must point to a declared target:
the entry scene must exist, choice `nextSceneId` values must name scenes, and
switch targets must name scenes.

## Copying and remapping

The VN clipboard adapter transforms the complete clipboard payload before the
native paste transaction:

- copied top-level fixture, scene, switch, and workflow IDs receive fresh IDs;
- valid scene/switch bodies get missing configured child IDs and fresh IDs for
  copied child identities;
- known scene references (`nextSceneId`, `targetSceneId`) and compile
  `entry_scene_id`/`selected_choice_id` values are rewritten only when their
  target was copied in the same payload;
- references to external targets, `profile_ref`, unknown strings, and
  consumer-specific fields are preserved.

The transformer handles nodes in copied subgraphs and leaves the original
payload untouched. It intentionally rewrites only the known identity fields;
it cannot infer relationships encoded in arbitrary strings or remap a target
that is not part of the copied payload. If the frontend has no compatible
paste transaction hook, remapping is unavailable. If safe remapping throws,
the paste is blocked before native deserialization so a partial graph is not
created.

## Predicates and effects

Predicates are objects with one operator; `{}` is unconditional. Supported
operators are `eq`, `in`, `gte`, `lte`, `has-marker`, `all`, `any`, and `not`.
Path predicates use non-root RFC 6901 JSON Pointers relative to
`state.values`. A missing path is a non-match and is included in the
evaluation trace.

The supported core effects are:

- `lf.marker.set` / `lf.marker.clear` with `{ "id": "marker.id" }`;
- `lf.state.set` with `{ "path": "/value", "value": ... }`;
- `lf.state.unset` with `{ "path": "/value" }`.

Effect IDs are retained in `appliedEffectIds`, so replaying an already applied
core effect is reported as skipped. Consumer-namespaced effects are retained
but not executed; compilation emits a `deferred_effect_capability` warning
and preview returns them in `deferredEffects`. Unknown effects in the reserved
`lf.*` namespace fail closed.

## Compile diagnostics and deterministic output

The validation report has schema `lf.vn.validation.v1`, status `complete` or
`blocked`, declaration/scene/switch counts, and `errors`/`warnings` arrays.
Each diagnostic has `code`, `message`, and `path`, with optional
`semanticId` and `sourceNodeId`. Typical blocking codes include
`missing_semantic_id`, `invalid_json`, `unsupported_field`,
`duplicate_semantic_id`, `missing_entry_scene`, `dangling_transition`, and
`dangling_switch_target`. A switch without a fallback is a warning; it is
explicitly allowed.

`LF_VNCompile` raises a machine-readable blocked contract error and sends a
diagnostic summary to the UI when validation fails, so no bundle or preview
outputs are returned for an invalid graph. An invalid selected choice (not in
the active scene or unavailable in the fixture) similarly blocks preview.
On success, the bundle contains all authored scenes and switches regardless of
the selected preview choice. The preview reports eligibility, available
choices, predicate traces, switch traces, and before/after fixture snapshots;
the derived state reflects one optional choice replay.

Canonical JSON is compact, UTF-8, finite, and key-sorted. The bundle source
contains the workflow ID, semantic version `1`, and a `sha256:` graph receipt.
Every compiled declaration and child carries its owning Comfy node ID. The
receipt therefore records graph/node provenance in addition to stable semantic
IDs.

## Domain-neutral example

The checked-in `Visual novel - Signal at Dusk` workflow is the runnable
example. For a fresh UI-authored version, create these nodes in the
`✨ LF Nodes/Visual Novel` category. Keep every generated `LF_ID`; the body
examples deliberately omit LF-owned child IDs so the authoring UI can
materialize them after successful JSON validation.

1. **VN State**

   - `state_body`:

     ```json
     {"markers":[],"trust":0}
     ```

2. **Scene Spec** (leave `graph` empty)

   - `title`: `Start`
   - `scene_body`:

     ```json
     {
       "participants": ["narrator"],
       "entryPredicate": {},
       "beats": [{"speaker":"narrator","text":"A path begins."}],
       "choices": [{
         "label":"Go forward",
         "effects":[{"type":"lf.marker.set","payload":{"id":"path.ready"}}]
       }],
       "artRequests": []
     }
     ```

3. **Scene Spec** (connect the first scene's `graph` to this node)

   - `title`: `End`
   - `scene_body`:

     ```json
     {
       "participants": ["narrator"],
       "entryPredicate": {"has-marker":"path.ready"},
       "beats": [{"speaker":"narrator","text":"The way is open."}],
       "choices": [],
       "artRequests": []
     }
     ```

   After both scenes exist, use the first scene's inline choice picker to set
   `nextSceneId` to **End**. The JSON stores End's immutable scene ID.

4. **Compile VN**

   Connect the second scene's `graph` and the state's `state` output. Keep the
   generated `workflow_id`, choose **Start** as `entry_scene_id`, and leave
   `selected_choice_id` empty for the initial preview. Choose **Go forward**
   to preview the marker effect and transition.

The authored bundle always contains both scenes. Selecting a choice changes
only the fixture preview and derived state. A headless/API client must provide
the generated top-level and child IDs, plus their references, explicitly; it
cannot rely on this authoring-time materialization.

## Non-goals

LF Nodes does not provide lore, character canon, live game state, save files,
rendering, audio playback, localization runtime, networking, or target-engine
adapters. Consumers own those layers and may interpret the neutral bundle and
deferred effects under their own contracts.
