"""Deterministic, target-neutral contracts for LF visual-novel nodes.

The module deliberately models authored declarations and fixture previews only.
It does not own live game state, persistence, rendering, or target adapters.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re

from typing import Any


STATE_SCHEMA = "lf.vn.state.v1"
GRAPH_SCHEMA = "lf.vn.graph.v1"
BUNDLE_SCHEMA = "lf.vn.bundle.v1"
VALIDATION_SCHEMA = "lf.vn.validation.v1"
PREVIEW_SCHEMA = "lf.vn.preview.v1"
ERROR_SCHEMA = "lf.vn.error.v1"

_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}\Z")
_MISSING = object()
_CORE_EFFECT_TYPES = {
    "lf.marker.set",
    "lf.marker.clear",
    "lf.state.set",
    "lf.state.unset",
}


class _DuplicateJSONKey(ValueError):
    pass


class VNContractError(ValueError):
    """A JSON-serializable, machine-readable VN contract error."""

    def __init__(self, payload: dict[str, Any] | list[dict[str, Any]]):
        if isinstance(payload, list):
            payload = {
                "schema": ERROR_SCHEMA,
                "status": "blocked",
                "errors": payload,
            }
        self.payload = payload
        super().__init__(canonical_json(payload))


def canonical_json(value: Any) -> str:
    """Return canonical UTF-8-compatible JSON text for hashing and replay."""

    _ensure_json_value(value, "$")
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def strict_json_loads(
    value: Any,
    *,
    label: str,
    expected_type: type | tuple[type, ...] | None = None,
) -> Any:
    """Parse JSON without silent coercion, duplicate keys, or non-finite numbers."""

    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise _error("empty_json", f"{label} cannot be empty", path=label)

        def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            result: dict[str, Any] = {}
            for key, item in pairs:
                if key in result:
                    raise _DuplicateJSONKey(key)
                result[key] = item
            return result

        def reject_constant(constant: str) -> None:
            raise ValueError(f"Non-finite number {constant}")

        try:
            parsed = json.loads(
                text,
                object_pairs_hook=reject_duplicate_keys,
                parse_constant=reject_constant,
            )
        except _DuplicateJSONKey as error:
            raise _error(
                "duplicate_json_key",
                f"{label} contains duplicate object key {str(error)!r}",
                path=label,
            ) from error
        except (json.JSONDecodeError, ValueError) as error:
            details = str(error)
            if isinstance(error, json.JSONDecodeError):
                details = f"{error.msg} at line {error.lineno}, column {error.colno}"
            raise _error(
                "invalid_json",
                f"{label} is not valid strict JSON: {details}",
                path=label,
            ) from error
    else:
        _ensure_json_value(value, label)
        parsed = copy.deepcopy(value)

    if expected_type is not None and not isinstance(parsed, expected_type):
        expected_name = (
            "/".join(item.__name__ for item in expected_type)
            if isinstance(expected_type, tuple)
            else expected_type.__name__
        )
        raise _error(
            "invalid_json_root",
            f"{label} must be a JSON {expected_name}, got {type(parsed).__name__}",
            path=label,
        )
    _ensure_json_value(parsed, label)
    return parsed


def validate_semantic_id(value: Any, *, label: str, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise _error(
            "missing_semantic_id",
            f"{label} is required and must be authored before execution",
            path=path,
        )
    if not isinstance(value, str) or not _ID_PATTERN.fullmatch(value):
        raise _error(
            "invalid_semantic_id",
            f"{label} must be a stable ASCII ID using letters, digits, '.', '_', ':', '/', or '-'",
            path=path,
        )
    return value


def make_state(
    *,
    profile_id: Any,
    fixture_id: Any,
    values: dict[str, Any],
) -> dict[str, Any]:
    fixture_id = validate_semantic_id(fixture_id, label="fixture_id", path="/fixtureId")
    _ensure_json_value(values, "/values")
    if not isinstance(values, dict):
        raise _error("invalid_state_values", "State values must be a JSON object", path="/values")
    state = {
        "schema": STATE_SCHEMA,
        "fixtureId": fixture_id,
        "values": copy.deepcopy(values),
        "appliedEffectIds": [],
    }
    if profile_id != "":
        state["profileId"] = validate_semantic_id(
            profile_id,
            label="profile_id",
            path="/profileId",
        )
    return state


def normalize_state(value: Any) -> dict[str, Any]:
    state = strict_json_loads(value, label="state", expected_type=dict)
    _expect_keys(
        state,
        allowed={"schema", "profileId", "fixtureId", "values", "appliedEffectIds", "metadata"},
        required={"schema", "fixtureId", "values", "appliedEffectIds"},
        path="/state",
    )
    if state["schema"] != STATE_SCHEMA:
        raise _error(
            "unsupported_schema",
            f"State schema must be {STATE_SCHEMA!r}",
            path="/state/schema",
        )
    if "profileId" in state:
        state["profileId"] = validate_semantic_id(
            state["profileId"], label="profileId", path="/state/profileId"
        )
    state["fixtureId"] = validate_semantic_id(
        state["fixtureId"], label="fixtureId", path="/state/fixtureId"
    )
    if not isinstance(state["values"], dict):
        raise _error("invalid_state_values", "State values must be an object", path="/state/values")
    if not isinstance(state["appliedEffectIds"], list):
        raise _error(
            "invalid_applied_effect_ids",
            "appliedEffectIds must be an array",
            path="/state/appliedEffectIds",
        )
    normalized_ids: list[str] = []
    seen: set[str] = set()
    for index, effect_id in enumerate(state["appliedEffectIds"]):
        effect_id = validate_semantic_id(
            effect_id,
            label="applied effect ID",
            path=f"/state/appliedEffectIds/{index}",
        )
        if effect_id in seen:
            raise _error(
                "duplicate_applied_effect_id",
                f"Applied effect ID {effect_id!r} appears more than once",
                path=f"/state/appliedEffectIds/{index}",
            )
        seen.add(effect_id)
        normalized_ids.append(effect_id)
    state["appliedEffectIds"] = normalized_ids
    if "metadata" in state and not isinstance(state["metadata"], dict):
        raise _error("invalid_metadata", "State metadata must be an object", path="/state/metadata")
    return state


def empty_graph() -> dict[str, Any]:
    return {"schema": GRAPH_SCHEMA, "declarations": []}


def normalize_scene_body(value: Any) -> dict[str, Any]:
    """Validate the single serialized authoring body used by Scene Spec."""

    body = strict_json_loads(value, label="scene_body", expected_type=dict)
    fields = {"participants", "entryPredicate", "beats", "choices", "artRequests"}
    _expect_keys(body, allowed=fields, required=fields, path="/sceneBody")
    return body


def normalize_switch_body(value: Any) -> dict[str, Any]:
    """Validate ordered cases and the deliberately explicit fallback field."""

    body = strict_json_loads(value, label="switch_body", expected_type=dict)
    fields = {"cases", "fallback"}
    _expect_keys(body, allowed=fields, required=fields, path="/switchBody")
    return body


def normalize_graph(value: Any | None) -> dict[str, Any]:
    if value is None:
        return empty_graph()
    graph = strict_json_loads(value, label="graph", expected_type=dict)
    _expect_keys(
        graph,
        allowed={"schema", "declarations", "metadata"},
        required={"schema", "declarations"},
        path="/graph",
    )
    if graph["schema"] != GRAPH_SCHEMA:
        raise _error(
            "unsupported_schema",
            f"Graph schema must be {GRAPH_SCHEMA!r}",
            path="/graph/schema",
        )
    if not isinstance(graph["declarations"], list):
        raise _error(
            "invalid_declarations",
            "Graph declarations must be an array",
            path="/graph/declarations",
        )
    if "metadata" in graph and not isinstance(graph["metadata"], dict):
        raise _error("invalid_metadata", "Graph metadata must be an object", path="/graph/metadata")
    return graph


def normalize_bundle(value: Any) -> dict[str, Any]:
    """Validate a public bundle before evaluating any fixture against it."""

    bundle = strict_json_loads(value, label="bundle", expected_type=dict)
    _expect_keys(
        bundle,
        allowed={"schema", "source", "entrySceneId", "scenes", "switches"},
        required={"schema", "source", "entrySceneId", "scenes", "switches"},
        path="/bundle",
    )
    if bundle["schema"] != BUNDLE_SCHEMA:
        raise _error(
            "unsupported_schema",
            f"Bundle schema must be {BUNDLE_SCHEMA!r}",
            path="/bundle/schema",
        )
    source = _validate_bundle_source(bundle["source"], path="/bundle/source")
    if not isinstance(bundle["scenes"], list):
        raise _error(
            "invalid_scenes",
            "Bundle scenes must be an array",
            path="/bundle/scenes",
        )
    if not isinstance(bundle["switches"], list):
        raise _error(
            "invalid_switches",
            "Bundle switches must be an array",
            path="/bundle/switches",
        )

    # Reuse the compiler's complete structural, uniqueness, and reference
    # validation. The supplied receipt remains provenance for the original
    # declaration order; the temporary graph receipt is intentionally ignored.
    validation_graph = {
        "schema": GRAPH_SCHEMA,
        "declarations": [
            *copy.deepcopy(bundle["scenes"]),
            *copy.deepcopy(bundle["switches"]),
        ],
    }
    normalized, report = compile_graph(
        graph=validation_graph,
        workflow_id=source["workflowId"],
        entry_scene_id=bundle["entrySceneId"],
    )
    if report["status"] != "complete":
        raise VNContractError(
            {
                "schema": ERROR_SCHEMA,
                "status": "blocked",
                "errors": report["errors"],
            }
        )
    normalized["source"] = source
    return normalized


def append_declaration(graph: Any | None, declaration: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_graph(graph)
    result = copy.deepcopy(normalized)
    result["declarations"].append(copy.deepcopy(declaration))
    return result


def validate_predicate(predicate: Any, *, path: str = "/predicate") -> dict[str, Any]:
    if not isinstance(predicate, dict):
        raise _error("invalid_predicate", "Predicate must be an object", path=path)
    if not predicate:
        return {}
    if len(predicate) != 1:
        raise _error(
            "invalid_predicate",
            "Predicate objects must contain exactly one operator",
            path=path,
        )

    operator, payload = next(iter(predicate.items()))
    if operator in {"all", "any"}:
        if not isinstance(payload, list) or not payload:
            raise _error(
                "invalid_predicate",
                f"{operator!r} requires a non-empty predicate array",
                path=f"{path}/{operator}",
            )
        return {
            operator: [
                validate_predicate(item, path=f"{path}/{operator}/{index}")
                for index, item in enumerate(payload)
            ]
        }
    if operator == "not":
        return {"not": validate_predicate(payload, path=f"{path}/not")}
    if operator == "has-marker":
        marker_id = validate_semantic_id(
            payload,
            label="marker ID",
            path=f"{path}/has-marker",
        )
        return {"has-marker": marker_id}
    if operator not in {"eq", "in", "gte", "lte"}:
        raise _error(
            "unsupported_predicate_operator",
            f"Unsupported predicate operator {operator!r}",
            path=path,
        )
    if not isinstance(payload, dict):
        raise _error(
            "invalid_predicate",
            f"{operator!r} requires an object payload",
            path=f"{path}/{operator}",
        )
    required = {"path", "values"} if operator == "in" else {"path", "value"}
    _expect_keys(payload, allowed=required, required=required, path=f"{path}/{operator}")
    json_pointer = _validate_json_pointer(payload["path"], path=f"{path}/{operator}/path")
    if operator == "in":
        if not isinstance(payload["values"], list):
            raise _error(
                "invalid_predicate",
                "'in' values must be an array",
                path=f"{path}/in/values",
            )
        return {"in": {"path": json_pointer, "values": copy.deepcopy(payload["values"])}}
    if operator in {"gte", "lte"} and not _is_number(payload["value"]):
        raise _error(
            "invalid_predicate",
            f"{operator!r} value must be a finite number",
            path=f"{path}/{operator}/value",
        )
    return {operator: {"path": json_pointer, "value": copy.deepcopy(payload["value"])}}


def evaluate_predicate(
    predicate: Any,
    values: dict[str, Any],
    *,
    path: str = "/predicate",
) -> tuple[bool, dict[str, Any]]:
    normalized = validate_predicate(predicate, path=path)
    if not normalized:
        return True, {"operator": "always", "matched": True}

    operator, payload = next(iter(normalized.items()))
    if operator in {"all", "any"}:
        traces: list[dict[str, Any]] = []
        matches: list[bool] = []
        for index, child in enumerate(payload):
            matched, trace = evaluate_predicate(
                child,
                values,
                path=f"{path}/{operator}/{index}",
            )
            matches.append(matched)
            traces.append(trace)
        matched = all(matches) if operator == "all" else any(matches)
        return matched, {"operator": operator, "matched": matched, "items": traces}
    if operator == "not":
        child_match, child_trace = evaluate_predicate(payload, values, path=f"{path}/not")
        return (not child_match), {
            "operator": "not",
            "matched": not child_match,
            "item": child_trace,
        }
    if operator == "has-marker":
        markers = values.get("markers", [])
        if isinstance(markers, list):
            matched = payload in markers
        elif isinstance(markers, dict):
            matched = bool(markers.get(payload, False))
        else:
            matched = False
        return matched, {
            "operator": "has-marker",
            "markerId": payload,
            "matched": matched,
        }

    actual = _resolve_pointer(values, payload["path"])
    if actual is _MISSING:
        return False, {
            "operator": operator,
            "path": payload["path"],
            "matched": False,
            "reason": "path_not_found",
        }
    if operator == "eq":
        expected = payload["value"]
        matched = canonical_json(actual) == canonical_json(expected)
        trace = {"operator": operator, "path": payload["path"], "matched": matched}
        trace.update({"actual": copy.deepcopy(actual), "expected": copy.deepcopy(expected)})
        return matched, trace
    if operator == "in":
        matched = any(canonical_json(actual) == canonical_json(item) for item in payload["values"])
        return matched, {
            "operator": operator,
            "path": payload["path"],
            "matched": matched,
            "actual": copy.deepcopy(actual),
            "expected": copy.deepcopy(payload["values"]),
        }
    if not _is_number(actual):
        return False, {
            "operator": operator,
            "path": payload["path"],
            "matched": False,
            "actual": copy.deepcopy(actual),
            "expected": payload["value"],
            "reason": "actual_not_numeric",
        }
    matched = actual >= payload["value"] if operator == "gte" else actual <= payload["value"]
    return matched, {
        "operator": operator,
        "path": payload["path"],
        "matched": matched,
        "actual": actual,
        "expected": payload["value"],
    }


def build_scene_declaration(
    *,
    scene_id: str,
    title: str,
    participants: list[Any],
    entry_predicate: dict[str, Any],
    beats: list[Any],
    choices: list[Any],
    art_requests: list[Any],
    source_node_id: Any,
) -> dict[str, Any]:
    declaration = {
        "kind": "scene",
        "id": scene_id,
        "title": title,
        "participants": participants,
        "entryPredicate": entry_predicate,
        "beats": beats,
        "choices": choices,
        "artRequests": art_requests,
        "source": {"nodeId": str(source_node_id) if source_node_id is not None else "unknown"},
    }
    return validate_scene_declaration(declaration, path="/scene")


def validate_scene_declaration(value: Any, *, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error("invalid_scene", "Scene declaration must be an object", path=path)
    _expect_keys(
        value,
        allowed={
            "kind", "id", "title", "participants", "entryPredicate", "beats",
            "choices", "artRequests", "metadata", "source",
        },
        required={
            "kind", "id", "title", "participants", "entryPredicate", "beats",
            "choices", "artRequests", "source",
        },
        path=path,
    )
    if value["kind"] != "scene":
        raise _error("invalid_scene", "Scene kind must be 'scene'", path=f"{path}/kind")
    result = copy.deepcopy(value)
    result["id"] = validate_semantic_id(result["id"], label="scene ID", path=f"{path}/id")
    if not isinstance(result["title"], str):
        raise _error("invalid_scene", "Scene title must be a string", path=f"{path}/title")
    if not isinstance(result["participants"], list):
        raise _error("invalid_scene", "Scene participants must be an array", path=f"{path}/participants")
    result["participants"] = [
        validate_semantic_id(item, label="participant ID", path=f"{path}/participants/{index}")
        for index, item in enumerate(result["participants"])
    ]
    if len(set(result["participants"])) != len(result["participants"]):
        raise _error(
            "duplicate_participant_id",
            "Scene participants must not contain duplicate IDs",
            path=f"{path}/participants",
        )
    result["entryPredicate"] = validate_predicate(
        result["entryPredicate"], path=f"{path}/entryPredicate"
    )
    if not isinstance(result["beats"], list) or not result["beats"]:
        raise _error("invalid_scene", "Scene beats must be a non-empty array", path=f"{path}/beats")
    result["beats"] = [
        _validate_beat(item, path=f"{path}/beats/{index}")
        for index, item in enumerate(result["beats"])
    ]
    if not isinstance(result["choices"], list):
        raise _error("invalid_scene", "Scene choices must be an array", path=f"{path}/choices")
    result["choices"] = [
        _validate_choice(item, path=f"{path}/choices/{index}")
        for index, item in enumerate(result["choices"])
    ]
    if not isinstance(result["artRequests"], list):
        raise _error(
            "invalid_scene",
            "Scene artRequests must be an array",
            path=f"{path}/artRequests",
        )
    result["artRequests"] = [
        _validate_art_request(item, path=f"{path}/artRequests/{index}")
        for index, item in enumerate(result["artRequests"])
    ]
    result["source"] = _validate_source(result["source"], path=f"{path}/source")
    if "metadata" in result and not isinstance(result["metadata"], dict):
        raise _error("invalid_metadata", "Scene metadata must be an object", path=f"{path}/metadata")
    return result


def build_switch_declaration(
    *,
    switch_id: str,
    cases: list[Any],
    fallback: dict[str, Any] | None,
    source_node_id: Any,
) -> dict[str, Any]:
    declaration = {
        "kind": "switch",
        "id": switch_id,
        "cases": cases,
        "fallback": fallback,
        "source": {"nodeId": str(source_node_id) if source_node_id is not None else "unknown"},
    }
    return validate_switch_declaration(declaration, path="/switch")


def validate_switch_declaration(value: Any, *, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error("invalid_switch", "Switch declaration must be an object", path=path)
    _expect_keys(
        value,
        allowed={"kind", "id", "cases", "fallback", "metadata", "source"},
        required={"kind", "id", "cases", "fallback", "source"},
        path=path,
    )
    if value["kind"] != "switch":
        raise _error("invalid_switch", "Switch kind must be 'switch'", path=f"{path}/kind")
    result = copy.deepcopy(value)
    result["id"] = validate_semantic_id(result["id"], label="switch ID", path=f"{path}/id")
    if not isinstance(result["cases"], list) or not result["cases"]:
        raise _error("invalid_switch", "Switch cases must be a non-empty array", path=f"{path}/cases")
    result["cases"] = [
        _validate_switch_case(item, path=f"{path}/cases/{index}", fallback=False)
        for index, item in enumerate(result["cases"])
    ]
    if result["fallback"] is not None:
        result["fallback"] = _validate_switch_case(
            result["fallback"], path=f"{path}/fallback", fallback=True
        )
    result["source"] = _validate_source(result["source"], path=f"{path}/source")
    if "metadata" in result and not isinstance(result["metadata"], dict):
        raise _error("invalid_metadata", "Switch metadata must be an object", path=f"{path}/metadata")
    return result


def evaluate_switch(
    declaration: dict[str, Any],
    state: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    switch = validate_switch_declaration(declaration, path="/switch")
    state = normalize_state(state)
    evaluations: list[dict[str, Any]] = []
    selected: dict[str, Any] | None = None
    for index, case in enumerate(switch["cases"]):
        matched, trace = evaluate_predicate(
            case["when"], state["values"], path=f"/switch/cases/{index}/when"
        )
        evaluations.append({"id": case["id"], "matched": matched, "trace": trace})
        if selected is None and matched:
            selected = case
    used_fallback = False
    if selected is None and switch["fallback"] is not None:
        selected = switch["fallback"]
        used_fallback = True
    report = {
        "schema": "lf.vn.switch-preview.v1",
        "switchId": switch["id"],
        "fixtureId": state["fixtureId"],
        "cases": evaluations,
        "selectedCaseId": selected["id"] if selected else None,
        "targetSceneId": selected["targetSceneId"] if selected else None,
        "usedFallback": used_fallback,
        "status": "selected" if selected else "unmatched",
    }
    return copy.deepcopy(selected), report


def compile_graph(
    *,
    graph: Any,
    workflow_id: str,
    entry_scene_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    validated_workflow_id: str | None = None
    validated_entry_scene_id: str | None = None
    normalized_graph: dict[str, Any] | None = None

    try:
        validated_workflow_id = validate_semantic_id(
            workflow_id, label="workflow ID", path="/source/workflowId"
        )
    except VNContractError as error:
        errors.extend(_payload_errors(error.payload))

    try:
        validated_entry_scene_id = validate_semantic_id(
            entry_scene_id, label="entry scene ID", path="/entrySceneId"
        )
    except VNContractError as error:
        errors.extend(_payload_errors(error.payload))

    try:
        normalized_graph = normalize_graph(graph)
    except VNContractError as error:
        errors.extend(_payload_errors(error.payload))

    graph_receipt: str | None = None
    try:
        receipt_value = (
            normalized_graph
            if normalized_graph is not None
            else strict_json_loads(graph, label="graph")
        )
        graph_receipt = "sha256:" + hashlib.sha256(
            canonical_json(receipt_value).encode("utf-8")
        ).hexdigest()
    except VNContractError:
        # Invalid inputs still need to produce the validation report that
        # explains them. A null receipt is explicit and never masquerades as
        # provenance for content that could not be parsed canonically.
        pass
    scenes: list[dict[str, Any]] = []
    switches: list[dict[str, Any]] = []
    registered: dict[str, str] = {}

    if normalized_graph is not None:
        for index, declaration in enumerate(normalized_graph["declarations"]):
            path = f"/graph/declarations/{index}"
            try:
                if not isinstance(declaration, dict):
                    raise _error(
                        "invalid_declaration",
                        "Graph declaration must be an object",
                        path=path,
                    )
                kind = declaration.get("kind")
                if kind == "scene":
                    normalized = validate_scene_declaration(declaration, path=path)
                    normalized = _materialize_source_mapping(normalized)
                    scenes.append(normalized)
                elif kind == "switch":
                    normalized = validate_switch_declaration(declaration, path=path)
                    normalized = _materialize_source_mapping(normalized)
                    switches.append(normalized)
                    if normalized["fallback"] is None:
                        warnings.append(
                            _diagnostic(
                                "switch_without_fallback",
                                f"Switch {normalized['id']!r} explicitly has no fallback",
                                path=f"{path}/fallback",
                                semantic_id=normalized["id"],
                                source_node_id=normalized["source"]["nodeId"],
                            )
                        )
                else:
                    raise _error(
                        "unsupported_declaration_kind",
                        f"Unsupported declaration kind {kind!r}",
                        path=f"{path}/kind",
                    )
                _register_id(
                    registered,
                    normalized["id"],
                    f"{kind} declaration",
                    errors,
                    path=f"{path}/id",
                    source_node_id=normalized["source"]["nodeId"],
                )
                if kind == "scene":
                    for beat_index, beat in enumerate(normalized["beats"]):
                        _register_id(
                            registered, beat["id"], "beat", errors,
                            path=f"{path}/beats/{beat_index}/id",
                            source_node_id=normalized["source"]["nodeId"],
                        )
                    for choice_index, choice in enumerate(normalized["choices"]):
                        _register_id(
                            registered, choice["id"], "choice", errors,
                            path=f"{path}/choices/{choice_index}/id",
                            source_node_id=normalized["source"]["nodeId"],
                        )
                        for effect_index, effect in enumerate(choice["effects"]):
                            _register_id(
                                registered, effect["id"], "effect", errors,
                                path=f"{path}/choices/{choice_index}/effects/{effect_index}/id",
                                source_node_id=effect["source"]["nodeId"],
                            )
                            if effect["type"] not in _CORE_EFFECT_TYPES:
                                warnings.append(
                                    _diagnostic(
                                        "deferred_effect_capability",
                                        f"Effect {effect['id']!r} is consumer-owned and will be deferred during LF preview",
                                        path=f"{path}/choices/{choice_index}/effects/{effect_index}/type",
                                        semantic_id=effect["id"],
                                        source_node_id=effect["source"]["nodeId"],
                                    )
                                )
                    for art_index, art_request in enumerate(normalized["artRequests"]):
                        _register_id(
                            registered, art_request["id"], "art request", errors,
                            path=f"{path}/artRequests/{art_index}/id",
                            source_node_id=normalized["source"]["nodeId"],
                        )
                else:
                    for case_index, case in enumerate(normalized["cases"]):
                        _register_id(
                            registered, case["id"], "switch case", errors,
                            path=f"{path}/cases/{case_index}/id",
                            source_node_id=normalized["source"]["nodeId"],
                        )
                    if normalized["fallback"] is not None:
                        _register_id(
                            registered, normalized["fallback"]["id"], "switch fallback", errors,
                            path=f"{path}/fallback/id",
                            source_node_id=normalized["source"]["nodeId"],
                        )
            except VNContractError as error:
                errors.extend(_payload_errors(error.payload))

    scene_ids = {scene["id"] for scene in scenes}
    if not scenes:
        errors.append(_diagnostic("missing_scene", "Graph must contain at least one scene", path="/scenes"))
    elif (
        validated_entry_scene_id is not None
        and validated_entry_scene_id not in scene_ids
    ):
        errors.append(
            _diagnostic(
                "missing_entry_scene",
                f"Entry scene {validated_entry_scene_id!r} is not declared",
                path="/entrySceneId",
                semantic_id=validated_entry_scene_id,
            )
        )
    for scene_index, scene in enumerate(scenes):
        for choice_index, choice in enumerate(scene["choices"]):
            target = choice.get("nextSceneId")
            if target is not None and target not in scene_ids:
                errors.append(
                    _diagnostic(
                        "dangling_transition",
                        f"Choice {choice['id']!r} targets missing scene {target!r}",
                        path=f"/scenes/{scene_index}/choices/{choice_index}/nextSceneId",
                        semantic_id=choice["id"],
                        source_node_id=scene["source"]["nodeId"],
                    )
                )
    for switch_index, switch in enumerate(switches):
        branches = list(switch["cases"])
        if switch["fallback"] is not None:
            branches.append(switch["fallback"])
        for branch_index, branch in enumerate(branches):
            if branch["targetSceneId"] not in scene_ids:
                errors.append(
                    _diagnostic(
                        "dangling_switch_target",
                        f"Switch branch {branch['id']!r} targets missing scene {branch['targetSceneId']!r}",
                        path=f"/switches/{switch_index}/branches/{branch_index}/targetSceneId",
                        semantic_id=branch["id"],
                        source_node_id=switch["source"]["nodeId"],
                    )
                )

    report = {
        "schema": VALIDATION_SCHEMA,
        "status": "blocked" if errors else "complete",
        "source": {
            "workflowId": validated_workflow_id,
            "graphReceipt": graph_receipt,
            "semanticVersion": 1,
        },
        "counts": {
            "declarations": len(normalized_graph["declarations"]) if normalized_graph else 0,
            "scenes": len(scenes),
            "switches": len(switches),
        },
        "errors": errors,
        "warnings": warnings,
    }
    if errors:
        return {}, report
    bundle = {
        "schema": BUNDLE_SCHEMA,
        "source": copy.deepcopy(report["source"]),
        "entrySceneId": validated_entry_scene_id,
        "scenes": scenes,
        "switches": switches,
    }
    return bundle, report


def preview_bundle(
    *,
    bundle: dict[str, Any],
    state: dict[str, Any],
    selected_choice_id: str = "",
) -> tuple[dict[str, Any], dict[str, Any]]:
    bundle = normalize_bundle(bundle)
    state_before = normalize_state(state)
    before = _preview_snapshot(bundle, state_before, active_scene_id=bundle["entrySceneId"])
    state_after = copy.deepcopy(state_before)
    selection: dict[str, Any] | None = None

    if selected_choice_id != "":
        selected_choice_id = validate_semantic_id(
            selected_choice_id,
            label="selected choice ID",
            path="/selectedChoiceId",
        )
        active_scene = next(
            (scene for scene in before["scenes"] if scene["id"] == before["activeSceneId"]),
            None,
        )
        if active_scene is None:
            raise _error(
                "missing_active_scene",
                f"Active scene {before['activeSceneId']!r} is not declared",
                path="/preview/activeSceneId",
            )
        choice_preview = next(
            (choice for choice in active_scene["choices"] if choice["id"] == selected_choice_id),
            None,
        )
        source_scene = next(
            (scene for scene in bundle["scenes"] if scene["id"] == active_scene["id"]),
            None,
        )
        source_choice = next(
            (choice for choice in source_scene["choices"] if choice["id"] == selected_choice_id),
            None,
        ) if source_scene else None
        if choice_preview is None or source_choice is None:
            raise _error(
                "choice_not_in_active_scene",
                f"Choice {selected_choice_id!r} does not belong to active scene {active_scene['id']!r}",
                path="/selectedChoiceId",
                semantic_id=selected_choice_id,
            )
        if not choice_preview["available"]:
            raise _error(
                "choice_unavailable",
                f"Choice {selected_choice_id!r} is not available in fixture {state_before['fixtureId']!r}",
                path="/selectedChoiceId",
                semantic_id=selected_choice_id,
            )
        effect_result = _apply_effects(state_after, source_choice["effects"])
        next_scene_id = source_choice.get("nextSceneId")
        selection = {
            "choiceId": selected_choice_id,
            "sceneId": source_scene["id"],
            "nextSceneId": next_scene_id,
            **effect_result,
        }
        after = _preview_snapshot(
            bundle,
            state_after,
            active_scene_id=next_scene_id,
        )
    else:
        after = copy.deepcopy(before)

    preview = {
        "schema": PREVIEW_SCHEMA,
        "fixtureId": state_before["fixtureId"],
        "selectedChoice": selection,
        "before": before,
        "after": after,
    }
    if "profileId" in state_before:
        preview["profileId"] = state_before["profileId"]
    return preview, state_after


def format_compile_summary(
    report: dict[str, Any],
    preview: dict[str, Any] | None = None,
) -> str:
    status = report.get("status", "blocked")
    icon = "✅" if status == "complete" else "❌"
    counts = report.get("counts", {})
    lines = [
        f"## {icon} Visual Novel Compile",
        "",
        f"- Status: **{status}**",
        f"- Scenes: **{counts.get('scenes', 0)}**",
        f"- Switches: **{counts.get('switches', 0)}**",
        f"- Receipt: `{report.get('source', {}).get('graphReceipt', 'unavailable')}`",
    ]
    if report.get("errors"):
        lines.extend(["", "### Errors"])
        lines.extend(f"- `{item['code']}` — {item['message']}" for item in report["errors"])
    if report.get("warnings"):
        lines.extend(["", "### Warnings"])
        lines.extend(f"- `{item['code']}` — {item['message']}" for item in report["warnings"])
    if preview:
        after = preview["after"]
        lines.extend(
            [
                "",
                "### Fixture preview",
                f"- Fixture: `{preview['fixtureId']}`",
                f"- Active scene: `{after.get('activeSceneId')}`",
                "- Available choices: "
                + (", ".join(f"`{item}`" for item in after.get("availableChoiceIds", [])) or "none"),
            ]
        )
        selection = preview.get("selectedChoice")
        if selection:
            lines.extend(
                [
                    f"- Applied effects: **{len(selection['appliedEffectIds'])}**",
                    f"- Deferred effects: **{len(selection['deferredEffects'])}**",
                ]
            )
    return "\n".join(lines)


def _validate_beat(value: Any, *, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error("invalid_beat", "Beat must be an object", path=path)
    _expect_keys(
        value,
        allowed={"id", "speaker", "text", "localizationKey", "audience", "metadata", "source"},
        required={"id"},
        path=path,
    )
    result = copy.deepcopy(value)
    result["id"] = validate_semantic_id(result["id"], label="beat ID", path=f"{path}/id")
    text = result.get("text")
    localization_key = result.get("localizationKey")
    if not isinstance(text, str) and not isinstance(localization_key, str):
        raise _error(
            "invalid_beat",
            "Beat requires text or localizationKey",
            path=path,
            semantic_id=result["id"],
        )
    for field in ("speaker", "text", "localizationKey"):
        if field in result and not isinstance(result[field], str):
            raise _error("invalid_beat", f"Beat {field} must be a string", path=f"{path}/{field}")
    if "audience" in result:
        if not isinstance(result["audience"], list):
            raise _error("invalid_beat", "Beat audience must be an array", path=f"{path}/audience")
        result["audience"] = [
            validate_semantic_id(item, label="audience ID", path=f"{path}/audience/{index}")
            for index, item in enumerate(result["audience"])
        ]
    if "metadata" in result and not isinstance(result["metadata"], dict):
        raise _error("invalid_metadata", "Beat metadata must be an object", path=f"{path}/metadata")
    if "source" in result:
        result["source"] = _validate_source(result["source"], path=f"{path}/source")
    return result


def _validate_choice(value: Any, *, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error("invalid_choice", "Choice must be an object", path=path)
    _expect_keys(
        value,
        allowed={
            "id", "label", "localizationKey", "visibilityPredicate",
            "availabilityPredicate", "effects", "nextSceneId", "metadata", "source",
        },
        required={"id"},
        path=path,
    )
    result = copy.deepcopy(value)
    result["id"] = validate_semantic_id(result["id"], label="choice ID", path=f"{path}/id")
    if not isinstance(result.get("label"), str) and not isinstance(result.get("localizationKey"), str):
        raise _error(
            "invalid_choice",
            "Choice requires label or localizationKey",
            path=path,
            semantic_id=result["id"],
        )
    for field in ("label", "localizationKey"):
        if field in result and not isinstance(result[field], str):
            raise _error("invalid_choice", f"Choice {field} must be a string", path=f"{path}/{field}")
    result["visibilityPredicate"] = validate_predicate(
        result.get("visibilityPredicate", {}), path=f"{path}/visibilityPredicate"
    )
    result["availabilityPredicate"] = validate_predicate(
        result.get("availabilityPredicate", {}), path=f"{path}/availabilityPredicate"
    )
    effects = result.get("effects", [])
    if not isinstance(effects, list):
        raise _error("invalid_choice", "Choice effects must be an array", path=f"{path}/effects")
    result["effects"] = [
        _validate_effect(item, path=f"{path}/effects/{index}")
        for index, item in enumerate(effects)
    ]
    if result.get("nextSceneId") is not None:
        result["nextSceneId"] = validate_semantic_id(
            result["nextSceneId"],
            label="next scene ID",
            path=f"{path}/nextSceneId",
        )
    if "metadata" in result and not isinstance(result["metadata"], dict):
        raise _error("invalid_metadata", "Choice metadata must be an object", path=f"{path}/metadata")
    if "source" in result:
        result["source"] = _validate_source(result["source"], path=f"{path}/source")
    return result


def _validate_effect(value: Any, *, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error("invalid_effect", "Effect must be an object", path=path)
    _expect_keys(
        value,
        allowed={"id", "type", "payload", "metadata", "source"},
        required={"id", "type", "payload"},
        path=path,
    )
    result = copy.deepcopy(value)
    result["id"] = validate_semantic_id(result["id"], label="effect ID", path=f"{path}/id")
    result["type"] = validate_semantic_id(result["type"], label="effect type", path=f"{path}/type")
    if not isinstance(result["payload"], dict):
        raise _error("invalid_effect", "Effect payload must be an object", path=f"{path}/payload")
    if "metadata" in result and not isinstance(result["metadata"], dict):
        raise _error("invalid_metadata", "Effect metadata must be an object", path=f"{path}/metadata")
    if result["type"] in {"lf.marker.set", "lf.marker.clear"}:
        _expect_keys(
            result["payload"], allowed={"id"}, required={"id"}, path=f"{path}/payload"
        )
        result["payload"]["id"] = validate_semantic_id(
            result["payload"]["id"], label="marker ID", path=f"{path}/payload/id"
        )
    elif result["type"] in {"lf.state.set", "lf.state.unset"}:
        required = {"path", "value"} if result["type"] == "lf.state.set" else {"path"}
        _expect_keys(result["payload"], allowed=required, required=required, path=f"{path}/payload")
        result["payload"]["path"] = _validate_json_pointer(
            result["payload"]["path"], path=f"{path}/payload/path"
        )
    elif result["type"].startswith("lf."):
        raise _error(
            "unsupported_core_effect_type",
            f"Unsupported LF core effect type {result['type']!r}; consumer-owned effects must use their own namespace",
            path=f"{path}/type",
            semantic_id=result["id"],
        )
    if "source" in result:
        result["source"] = _validate_source(result["source"], path=f"{path}/source")
    return result


def _validate_art_request(value: Any, *, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error("invalid_art_request", "Art request must be an object", path=path)
    _expect_keys(
        value,
        allowed={"id", "slots", "direction", "metadata", "source"},
        required={"id"},
        path=path,
    )
    result = copy.deepcopy(value)
    result["id"] = validate_semantic_id(result["id"], label="art request ID", path=f"{path}/id")
    if "slots" in result and not isinstance(result["slots"], dict):
        raise _error("invalid_art_request", "Art request slots must be an object", path=f"{path}/slots")
    if "direction" in result and not isinstance(result["direction"], str):
        raise _error(
            "invalid_art_request",
            "Art request direction must be a string",
            path=f"{path}/direction",
        )
    if "metadata" in result and not isinstance(result["metadata"], dict):
        raise _error("invalid_metadata", "Art request metadata must be an object", path=f"{path}/metadata")
    if "source" in result:
        result["source"] = _validate_source(result["source"], path=f"{path}/source")
    return result


def _validate_switch_case(value: Any, *, path: str, fallback: bool) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error("invalid_switch_case", "Switch branch must be an object", path=path)
    allowed = {"id", "targetSceneId", "metadata", "source"} if fallback else {"id", "when", "targetSceneId", "metadata", "source"}
    required = {"id", "targetSceneId"} if fallback else {"id", "when", "targetSceneId"}
    _expect_keys(value, allowed=allowed, required=required, path=path)
    result = copy.deepcopy(value)
    result["id"] = validate_semantic_id(result["id"], label="switch case ID", path=f"{path}/id")
    result["targetSceneId"] = validate_semantic_id(
        result["targetSceneId"], label="target scene ID", path=f"{path}/targetSceneId"
    )
    if not fallback:
        result["when"] = validate_predicate(result["when"], path=f"{path}/when")
    if "metadata" in result and not isinstance(result["metadata"], dict):
        raise _error("invalid_metadata", "Switch branch metadata must be an object", path=f"{path}/metadata")
    if "source" in result:
        result["source"] = _validate_source(result["source"], path=f"{path}/source")
    return result


def _validate_source(value: Any, *, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error("invalid_source", "Source mapping must be an object", path=path)
    _expect_keys(value, allowed={"nodeId"}, required={"nodeId"}, path=path)
    if isinstance(value["nodeId"], bool) or not isinstance(value["nodeId"], (str, int)):
        raise _error("invalid_source", "Source nodeId must be a string or integer", path=f"{path}/nodeId")
    return {"nodeId": str(value["nodeId"])}


def _validate_bundle_source(value: Any, *, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise _error("invalid_source", "Bundle source must be an object", path=path)
    _expect_keys(
        value,
        allowed={"workflowId", "graphReceipt", "semanticVersion"},
        required={"workflowId", "graphReceipt", "semanticVersion"},
        path=path,
    )
    workflow_id = validate_semantic_id(
        value["workflowId"],
        label="workflow ID",
        path=f"{path}/workflowId",
    )
    receipt = value["graphReceipt"]
    if not isinstance(receipt, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", receipt):
        raise _error(
            "invalid_graph_receipt",
            "graphReceipt must be a lowercase SHA-256 receipt",
            path=f"{path}/graphReceipt",
        )
    semantic_version = value["semanticVersion"]
    if (
        isinstance(semantic_version, bool)
        or not isinstance(semantic_version, int)
        or semantic_version != 1
    ):
        raise _error(
            "unsupported_semantic_version",
            "Bundle semanticVersion must be 1",
            path=f"{path}/semanticVersion",
        )
    return {
        "workflowId": workflow_id,
        "graphReceipt": receipt,
        "semanticVersion": 1,
    }


def _materialize_source_mapping(declaration: dict[str, Any]) -> dict[str, Any]:
    """Attach owning Comfy node provenance to every compiled child item."""

    result = copy.deepcopy(declaration)
    source = copy.deepcopy(result["source"])
    if result["kind"] == "scene":
        for beat in result["beats"]:
            beat["source"] = copy.deepcopy(source)
        for choice in result["choices"]:
            choice["source"] = copy.deepcopy(source)
            for effect in choice["effects"]:
                effect["source"] = copy.deepcopy(source)
        for art_request in result["artRequests"]:
            art_request["source"] = copy.deepcopy(source)
    else:
        for case in result["cases"]:
            case["source"] = copy.deepcopy(source)
        if result["fallback"] is not None:
            result["fallback"]["source"] = copy.deepcopy(source)
    return result


def _preview_snapshot(
    bundle: dict[str, Any],
    state: dict[str, Any],
    *,
    active_scene_id: str | None,
) -> dict[str, Any]:
    scene_previews: list[dict[str, Any]] = []
    available_choice_ids: list[str] = []
    for scene_index, scene in enumerate(bundle["scenes"]):
        scene_matched, scene_trace = evaluate_predicate(
            scene["entryPredicate"],
            state["values"],
            path=f"/scenes/{scene_index}/entryPredicate",
        )
        choices: list[dict[str, Any]] = []
        for choice_index, choice in enumerate(scene["choices"]):
            visible_match, visible_trace = evaluate_predicate(
                choice["visibilityPredicate"],
                state["values"],
                path=f"/scenes/{scene_index}/choices/{choice_index}/visibilityPredicate",
            )
            available_match, available_trace = evaluate_predicate(
                choice["availabilityPredicate"],
                state["values"],
                path=f"/scenes/{scene_index}/choices/{choice_index}/availabilityPredicate",
            )
            visible = scene_matched and visible_match
            available = visible and available_match
            if scene["id"] == active_scene_id and available:
                available_choice_ids.append(choice["id"])
            choices.append(
                {
                    "id": choice["id"],
                    "visible": visible,
                    "available": available,
                    "visibilityTrace": visible_trace,
                    "availabilityTrace": available_trace,
                }
            )
        scene_previews.append(
            {
                "id": scene["id"],
                "eligible": scene_matched,
                "entryTrace": scene_trace,
                "choices": choices,
            }
        )
    switch_previews: list[dict[str, Any]] = []
    for switch in bundle["switches"]:
        _, switch_report = evaluate_switch(switch, state)
        switch_previews.append(switch_report)
    active_scene = next((item for item in scene_previews if item["id"] == active_scene_id), None)
    return {
        "activeSceneId": active_scene_id,
        "activeSceneEligible": bool(active_scene and active_scene["eligible"]),
        "availableChoiceIds": available_choice_ids,
        "scenes": scene_previews,
        "switches": switch_previews,
    }


def _apply_effects(state: dict[str, Any], effects: list[dict[str, Any]]) -> dict[str, Any]:
    applied = set(state["appliedEffectIds"])
    applied_now: list[str] = []
    skipped: list[str] = []
    deferred: list[dict[str, Any]] = []
    for effect in effects:
        if effect["id"] in applied:
            skipped.append(effect["id"])
            continue
        effect_type = effect["type"]
        if effect_type not in _CORE_EFFECT_TYPES:
            deferred.append(copy.deepcopy(effect))
            continue
        payload = effect["payload"]
        if effect_type in {"lf.marker.set", "lf.marker.clear"}:
            markers = state["values"].setdefault("markers", [])
            if not isinstance(markers, list) or any(not isinstance(item, str) for item in markers):
                raise _error(
                    "invalid_marker_state",
                    "Core marker effects require values.markers to be an array of IDs",
                    path="/state/values/markers",
                )
            marker_id = payload["id"]
            marker_set = set(markers)
            if effect_type == "lf.marker.set":
                marker_set.add(marker_id)
            else:
                marker_set.discard(marker_id)
            state["values"]["markers"] = sorted(marker_set)
        elif effect_type == "lf.state.set":
            _set_pointer(state["values"], payload["path"], copy.deepcopy(payload["value"]))
        else:
            _unset_pointer(state["values"], payload["path"])
        applied.add(effect["id"])
        applied_now.append(effect["id"])
    state["appliedEffectIds"] = sorted(applied)
    return {
        "appliedEffectIds": applied_now,
        "skippedEffectIds": skipped,
        "deferredEffects": deferred,
    }


def _register_id(
    registered: dict[str, str],
    semantic_id: str,
    kind: str,
    errors: list[dict[str, Any]],
    *,
    path: str,
    source_node_id: str,
) -> None:
    previous = registered.get(semantic_id)
    if previous is not None:
        errors.append(
            _diagnostic(
                "duplicate_semantic_id",
                f"{kind.capitalize()} ID {semantic_id!r} duplicates {previous}",
                path=path,
                semantic_id=semantic_id,
                source_node_id=source_node_id,
            )
        )
    else:
        registered[semantic_id] = kind


def _validate_json_pointer(value: Any, *, path: str) -> str:
    if not isinstance(value, str) or not value.startswith("/") or value == "/":
        raise _error(
            "invalid_json_pointer",
            "State paths must be non-root RFC 6901 JSON Pointers beginning with '/'",
            path=path,
        )
    for segment in value.split("/")[1:]:
        if re.search(r"~(?![01])", segment):
            raise _error(
                "invalid_json_pointer",
                f"Invalid JSON Pointer escape in {value!r}",
                path=path,
            )
    return value


def _pointer_segments(pointer: str) -> list[str]:
    return [segment.replace("~1", "/").replace("~0", "~") for segment in pointer.split("/")[1:]]


def _resolve_pointer(root: Any, pointer: str) -> Any:
    current = root
    for segment in _pointer_segments(pointer):
        if isinstance(current, dict) and segment in current:
            current = current[segment]
        elif isinstance(current, list) and segment.isdigit() and int(segment) < len(current):
            current = current[int(segment)]
        else:
            return _MISSING
    return current


def _set_pointer(root: dict[str, Any], pointer: str, value: Any) -> None:
    segments = _pointer_segments(pointer)
    current: dict[str, Any] = root
    for segment in segments[:-1]:
        child = current.get(segment)
        if child is None:
            child = {}
            current[segment] = child
        if not isinstance(child, dict):
            raise _error(
                "state_path_conflict",
                f"Cannot descend through non-object state value at {segment!r}",
                path=pointer,
            )
        current = child
    current[segments[-1]] = value


def _unset_pointer(root: dict[str, Any], pointer: str) -> None:
    segments = _pointer_segments(pointer)
    current: Any = root
    for segment in segments[:-1]:
        if not isinstance(current, dict) or segment not in current:
            return
        current = current[segment]
    if isinstance(current, dict):
        current.pop(segments[-1], None)


def _expect_keys(
    value: dict[str, Any],
    *,
    allowed: set[str],
    required: set[str],
    path: str,
) -> None:
    unknown = sorted(set(value) - allowed)
    missing = sorted(required - set(value))
    if unknown:
        raise _error(
            "unsupported_field",
            f"Unsupported field(s): {', '.join(unknown)}",
            path=path,
        )
    if missing:
        raise _error(
            "missing_field",
            f"Missing required field(s): {', '.join(missing)}",
            path=path,
        )


def _ensure_json_value(value: Any, path: str) -> None:
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int) and not isinstance(value, bool):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise _error("non_finite_number", "JSON numbers must be finite", path=path)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _ensure_json_value(item, f"{path}/{index}")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise _error("non_string_json_key", "JSON object keys must be strings", path=path)
            _ensure_json_value(item, f"{path}/{key}")
        return
    raise _error(
        "non_json_value",
        f"Unsupported JSON value type {type(value).__name__}",
        path=path,
    )


def _is_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    return isinstance(value, float) and math.isfinite(value)


def _diagnostic(
    code: str,
    message: str,
    *,
    path: str,
    semantic_id: str | None = None,
    source_node_id: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {"code": code, "message": message, "path": path}
    if semantic_id is not None:
        result["semanticId"] = semantic_id
    if source_node_id is not None:
        result["sourceNodeId"] = source_node_id
    return result


def _error(
    code: str,
    message: str,
    *,
    path: str,
    semantic_id: str | None = None,
    source_node_id: str | None = None,
) -> VNContractError:
    return VNContractError(
        [
            _diagnostic(
                code,
                message,
                path=path,
                semantic_id=semantic_id,
                source_node_id=source_node_id,
            )
        ]
    )


def _payload_errors(payload: dict[str, Any]) -> list[dict[str, Any]]:
    errors = payload.get("errors", [])
    return copy.deepcopy(errors) if isinstance(errors, list) else []


__all__ = [
    "BUNDLE_SCHEMA",
    "ERROR_SCHEMA",
    "GRAPH_SCHEMA",
    "PREVIEW_SCHEMA",
    "STATE_SCHEMA",
    "VALIDATION_SCHEMA",
    "VNContractError",
    "append_declaration",
    "build_scene_declaration",
    "build_switch_declaration",
    "canonical_json",
    "compile_graph",
    "empty_graph",
    "evaluate_predicate",
    "evaluate_switch",
    "format_compile_summary",
    "make_state",
    "normalize_graph",
    "normalize_bundle",
    "normalize_scene_body",
    "normalize_state",
    "normalize_switch_body",
    "preview_bundle",
    "strict_json_loads",
    "validate_predicate",
]
