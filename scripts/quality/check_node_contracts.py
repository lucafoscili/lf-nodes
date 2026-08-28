#!/usr/bin/env python3
"""Statically validate the public contracts of LF Nodes modules.

This checker deliberately uses only the Python standard library and parses node
sources without importing them.  That keeps it usable in a lightweight CI job
where ComfyUI and the node runtime dependencies are unavailable.
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


CLASS_MAPPINGS = "NODE_CLASS_MAPPINGS"
DISPLAY_MAPPINGS = "NODE_DISPLAY_NAME_MAPPINGS"
CONTRACT_ATTRIBUTES = {
    "INPUT_IS_LIST",
    "OUTPUT_IS_LIST",
    "OUTPUT_TOOLTIPS",
    "RETURN_NAMES",
    "RETURN_TYPES",
}

# Historical public socket names that contain ``_list`` but intentionally
# serialize one scalar collection.  Keep this allowlist exact and small: new
# list-named sockets must use Comfy's real list transport.
LEGACY_SCALAR_LIST_OUTPUTS = {
    ("LF_SetValueInJSON", "json_list"),
}


@dataclass(frozen=True)
class Finding:
    """One deterministic, source-addressable contract defect."""

    path: str
    line: int
    column: int
    code: str
    message: str

    def render(self) -> str:
        return (
            f"{self.path}:{self.line}:{self.column}: "
            f"{self.code}: {self.message}"
        )


@dataclass(frozen=True)
class MappingEntry:
    key: str
    value: ast.expr
    path: str
    line: int
    column: int


@dataclass(frozen=True)
class CheckResult:
    findings: tuple[Finding, ...]
    python_files: int
    public_mappings: int


def _source_position(node: ast.AST) -> tuple[int, int]:
    return getattr(node, "lineno", 1), getattr(node, "col_offset", 0) + 1


def _assignment_values(
    statements: Iterable[ast.stmt], names: set[str]
) -> Iterator[tuple[str, ast.expr, ast.AST]]:
    """Yield direct assignments to selected names in their source order."""

    for statement in statements:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    yield target.id, statement.value, target
        elif isinstance(statement, ast.AnnAssign):
            target = statement.target
            if (
                statement.value is not None
                and isinstance(target, ast.Name)
                and target.id in names
            ):
                yield target.id, statement.value, target


def _literal_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _parse_mapping(
    *,
    path: str,
    mapping_name: str,
    value: ast.expr,
    assignment_node: ast.AST,
    findings: list[Finding],
) -> list[MappingEntry]:
    if not isinstance(value, ast.Dict):
        line, column = _source_position(assignment_node)
        findings.append(
            Finding(
                path,
                line,
                column,
                "MAPPING_NOT_LITERAL",
                f"{mapping_name} must be a dictionary literal",
            )
        )
        return []

    entries: list[MappingEntry] = []
    for key_node, value_node in zip(value.keys, value.values):
        if key_node is None:
            line, column = _source_position(value_node)
            findings.append(
                Finding(
                    path,
                    line,
                    column,
                    "MAPPING_UNPACK",
                    f"{mapping_name} cannot contain a ** mapping expansion",
                )
            )
            continue

        key = _literal_string(key_node)
        if key is None:
            line, column = _source_position(key_node)
            findings.append(
                Finding(
                    path,
                    line,
                    column,
                    "MAPPING_KEY_NOT_LITERAL",
                    f"{mapping_name} keys must be string literals",
                )
            )
            continue

        line, column = _source_position(key_node)
        entries.append(MappingEntry(key, value_node, path, line, column))

        if mapping_name == DISPLAY_MAPPINGS and _literal_string(value_node) is None:
            value_line, value_column = _source_position(value_node)
            findings.append(
                Finding(
                    path,
                    value_line,
                    value_column,
                    "DISPLAY_NAME_NOT_LITERAL",
                    f"display name for {key!r} must be a string literal",
                )
            )

    return entries


def _sequence_length(node: ast.AST | None) -> int | None:
    """Return a statically provable sequence length, or None.

    Tuple/list literals are the important case.  The small set of extra forms
    covers declarations already used by this repository without evaluating any
    source code.
    """

    if isinstance(node, (ast.Tuple, ast.List)):
        length = 0
        for element in node.elts:
            if isinstance(element, ast.Starred):
                expanded_length = _sequence_length(element.value)
                if expanded_length is None:
                    return None
                length += expanded_length
            else:
                length += 1
        return length

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left_length = _sequence_length(node.left)
        right_length = _sequence_length(node.right)
        if left_length is not None and right_length is not None:
            return left_length + right_length
        return None

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        pairs = ((node.left, node.right), (node.right, node.left))
        for sequence_node, count_node in pairs:
            sequence_length = _sequence_length(sequence_node)
            if (
                sequence_length is not None
                and isinstance(count_node, ast.Constant)
                and type(count_node.value) is int
                and count_node.value >= 0
            ):
                return sequence_length * count_node.value
        return None

    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"list", "tuple"}
        and not node.keywords
    ):
        if not node.args:
            return 0
        if len(node.args) == 1:
            return _sequence_length(node.args[0])
        return None

    if isinstance(node, ast.IfExp):
        body_length = _sequence_length(node.body)
        else_length = _sequence_length(node.orelse)
        if body_length is not None and body_length == else_length:
            return body_length

    return None


def _class_assignments(class_node: ast.ClassDef) -> dict[str, tuple[ast.expr, ast.AST]]:
    assignments: dict[str, tuple[ast.expr, ast.AST]] = {}
    for name, value, target in _assignment_values(class_node.body, CONTRACT_ATTRIBUTES):
        # Python uses the final direct class-body assignment, so the checker does too.
        assignments[name] = (value, target)
    return assignments


def _tuple_return_branches(
    expression: ast.expr | None,
) -> Iterator[tuple[str, ast.Tuple]]:
    """Yield only statically visible result tuples from a return expression."""

    if isinstance(expression, ast.Tuple):
        yield "return tuple", expression
        return

    if isinstance(expression, ast.IfExp):
        yield from _tuple_return_branches(expression.body)
        yield from _tuple_return_branches(expression.orelse)
        return

    if not isinstance(expression, ast.Dict):
        return

    for key_node, value_node in zip(expression.keys, expression.values):
        if _literal_string(key_node) != "result":
            continue
        if isinstance(value_node, ast.Tuple):
            yield "dictionary 'result' tuple", value_node
        elif isinstance(value_node, ast.IfExp):
            for _, tuple_node in _tuple_return_branches(value_node):
                yield "dictionary 'result' tuple", tuple_node


class _OnExecReturnVisitor(ast.NodeVisitor):
    """Inspect returns in one method while excluding nested lexical scopes."""

    def __init__(
        self,
        *,
        class_name: str,
        expected_arity: int,
        path: str,
        findings: list[Finding],
    ) -> None:
        self.class_name = class_name
        self.expected_arity = expected_arity
        self.path = path
        self.findings = findings

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        # A nested helper's return contract is unrelated to its enclosing node.
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        return

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        return

    def visit_Lambda(self, node: ast.Lambda) -> None:
        return

    def visit_Return(self, node: ast.Return) -> None:
        for return_kind, tuple_node in _tuple_return_branches(node.value):
            actual_arity = _sequence_length(tuple_node)
            if actual_arity is None or actual_arity == self.expected_arity:
                continue
            line, column = _source_position(tuple_node)
            self.findings.append(
                Finding(
                    self.path,
                    line,
                    column,
                    "RETURN_ARITY",
                    (
                        f"{self.class_name}.on_exec {return_kind} has "
                        f"{actual_arity} item(s); RETURN_TYPES declares "
                        f"{self.expected_arity}"
                    ),
                )
            )


def _check_class_contract(
    *,
    class_node: ast.ClassDef,
    path: str,
    findings: list[Finding],
) -> None:
    assignments = _class_assignments(class_node)

    output_is_list = assignments.get("OUTPUT_IS_LIST")
    if output_is_list is not None:
        output_value, output_target = output_is_list
        if not isinstance(output_value, (ast.Tuple, ast.List)):
            line, column = _source_position(output_target)
            findings.append(
                Finding(
                    path,
                    line,
                    column,
                    "OUTPUT_IS_LIST_NOT_LITERAL",
                    (
                        f"{class_node.name}.OUTPUT_IS_LIST must be a tuple/list "
                        "literal whose entries are literal booleans"
                    ),
                )
            )
        else:
            for index, entry in enumerate(output_value.elts):
                if not (
                    isinstance(entry, ast.Constant) and type(entry.value) is bool
                ):
                    line, column = _source_position(entry)
                    findings.append(
                        Finding(
                            path,
                            line,
                            column,
                            "OUTPUT_IS_LIST_NON_BOOL",
                            (
                                f"{class_node.name}.OUTPUT_IS_LIST entry {index} "
                                "must be literal True or False"
                            ),
                        )
                    )

    input_is_list = assignments.get("INPUT_IS_LIST")
    if input_is_list is not None:
        input_value, input_target = input_is_list
        if not (
            isinstance(input_value, ast.Constant)
            and type(input_value.value) is bool
        ):
            line, column = _source_position(input_target)
            findings.append(
                Finding(
                    path,
                    line,
                    column,
                    "INPUT_IS_LIST_NOT_BOOL",
                    (
                        f"{class_node.name}.INPUT_IS_LIST must be one literal "
                        "boolean, never a tuple or list"
                    ),
                )
            )

    return_types = assignments.get("RETURN_TYPES")
    if return_types is None:
        return

    expected_arity = _sequence_length(return_types[0])
    if expected_arity is None:
        # Do not guess at dynamic contracts or produce return-arity false positives.
        return

    for attribute_name in ("RETURN_NAMES", "OUTPUT_TOOLTIPS", "OUTPUT_IS_LIST"):
        attribute = assignments.get(attribute_name)
        if attribute is None:
            continue
        attribute_value, attribute_target = attribute
        actual_arity = _sequence_length(attribute_value)
        if actual_arity is None or actual_arity == expected_arity:
            continue
        line, column = _source_position(attribute_target)
        findings.append(
            Finding(
                path,
                line,
                column,
                "ATTRIBUTE_ARITY",
                (
                    f"{class_node.name}.{attribute_name} has {actual_arity} "
                    f"item(s); RETURN_TYPES declares {expected_arity}"
                ),
            )
        )

    return_names = assignments.get("RETURN_NAMES")
    if return_names is not None and isinstance(return_names[0], (ast.Tuple, ast.List)):
        output_entries = (
            output_is_list[0].elts
            if output_is_list is not None
            and isinstance(output_is_list[0], (ast.Tuple, ast.List))
            else ()
        )
        for index, name_node in enumerate(return_names[0].elts):
            output_name = _literal_string(name_node)
            if (
                output_name is None
                or not output_name.endswith("_list")
                or (class_node.name, output_name) in LEGACY_SCALAR_LIST_OUTPUTS
            ):
                continue

            declared_as_list = (
                index < len(output_entries)
                and isinstance(output_entries[index], ast.Constant)
                and output_entries[index].value is True
            )
            if declared_as_list:
                continue

            line, column = _source_position(name_node)
            findings.append(
                Finding(
                    path,
                    line,
                    column,
                    "LIST_OUTPUT_NOT_DECLARED",
                    (
                        f"{class_node.name}.{output_name} must have literal "
                        f"OUTPUT_IS_LIST[{index}] = True"
                    ),
                )
            )

    methods = [
        statement
        for statement in class_node.body
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef))
        and statement.name == "on_exec"
    ]
    for method in methods:
        visitor = _OnExecReturnVisitor(
            class_name=class_node.name,
            expected_arity=expected_arity,
            path=path,
            findings=findings,
        )
        for statement in method.body:
            visitor.visit(statement)


def _is_direct_prompt_server_send(call: ast.Call) -> bool:
    function = call.func
    return (
        isinstance(function, ast.Attribute)
        and function.attr == "send_sync"
        and isinstance(function.value, ast.Attribute)
        and function.value.attr == "instance"
        and isinstance(function.value.value, ast.Name)
        and function.value.value.id == "PromptServer"
    )


def _check_event_suffixes(
    *,
    class_node: ast.ClassDef,
    public_name: str,
    path: str,
    findings: list[Finding],
) -> None:
    """Require literal node UI events to match the frontend's node event name."""

    expected_event = public_name.lower().replace("_", "-", 1)
    for node in ast.walk(class_node):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        if node.func.id != "safe_send_sync" or not node.args:
            continue
        suffix = _literal_string(node.args[0])
        if suffix is None:
            continue
        actual_event = f"lf-{suffix}"
        if actual_event == expected_event:
            continue
        line, column = _source_position(node.args[0])
        findings.append(
            Finding(
                path,
                line,
                column,
                "EVENT_SUFFIX_MISMATCH",
                (
                    f"{public_name} must emit {expected_event!r}, not "
                    f"{actual_event!r}"
                ),
            )
        )


def check_repository(root: Path) -> CheckResult:
    root = root.resolve()
    nodes_directory = root / "modules" / "nodes"
    paths = sorted(nodes_directory.rglob("*.py"), key=lambda item: item.as_posix())
    findings: list[Finding] = []
    all_class_entries: list[MappingEntry] = []

    for source_path in paths:
        relative_path = source_path.relative_to(root).as_posix()
        try:
            source = source_path.read_text(encoding="utf-8-sig")
            tree = ast.parse(source, filename=relative_path)
        except (OSError, UnicodeError) as error:
            findings.append(
                Finding(
                    relative_path,
                    1,
                    1,
                    "SOURCE_READ_ERROR",
                    str(error),
                )
            )
            continue
        except SyntaxError as error:
            findings.append(
                Finding(
                    relative_path,
                    error.lineno or 1,
                    error.offset or 1,
                    "SYNTAX_ERROR",
                    error.msg,
                )
            )
            continue

        classes = {
            statement.name: statement
            for statement in tree.body
            if isinstance(statement, ast.ClassDef)
        }
        class_entries: list[MappingEntry] = []
        display_entries: list[MappingEntry] = []

        for mapping_name, value, assignment_node in _assignment_values(
            tree.body, {CLASS_MAPPINGS, DISPLAY_MAPPINGS}
        ):
            entries = _parse_mapping(
                path=relative_path,
                mapping_name=mapping_name,
                value=value,
                assignment_node=assignment_node,
                findings=findings,
            )
            if mapping_name == CLASS_MAPPINGS:
                class_entries.extend(entries)
            else:
                display_entries.extend(entries)

        all_class_entries.extend(class_entries)

        display_by_key: dict[str, list[MappingEntry]] = {}
        for entry in display_entries:
            display_by_key.setdefault(entry.key, []).append(entry)
        for key in sorted(display_by_key):
            occurrences = display_by_key[key]
            first = occurrences[0]
            for duplicate in occurrences[1:]:
                findings.append(
                    Finding(
                        duplicate.path,
                        duplicate.line,
                        duplicate.column,
                        "DUPLICATE_DISPLAY_KEY",
                        (
                            f"display mapping key {key!r} duplicates "
                            f"{first.path}:{first.line}:{first.column}"
                        ),
                    )
                )

        class_by_key: dict[str, list[MappingEntry]] = {}
        for entry in class_entries:
            class_by_key.setdefault(entry.key, []).append(entry)

        for key in sorted(set(class_by_key) - set(display_by_key)):
            entry = class_by_key[key][0]
            findings.append(
                Finding(
                    entry.path,
                    entry.line,
                    entry.column,
                    "DISPLAY_KEY_MISSING",
                    f"public node key {key!r} has no matching display mapping",
                )
            )

        for key in sorted(set(display_by_key) - set(class_by_key)):
            entry = display_by_key[key][0]
            findings.append(
                Finding(
                    entry.path,
                    entry.line,
                    entry.column,
                    "DISPLAY_KEY_EXTRA",
                    f"display mapping key {key!r} has no local class mapping",
                )
            )

        mapped_class_names: set[str] = set()
        public_name_by_class: dict[str, str] = {}
        for entry in class_entries:
            if not isinstance(entry.value, ast.Name):
                line, column = _source_position(entry.value)
                findings.append(
                    Finding(
                        entry.path,
                        line,
                        column,
                        "MAPPED_CLASS_NOT_NAME",
                        (
                            f"public node key {entry.key!r} must map directly "
                            "to a local class name"
                        ),
                    )
                )
                continue

            class_name = entry.value.id
            if class_name not in classes:
                line, column = _source_position(entry.value)
                findings.append(
                    Finding(
                        entry.path,
                        line,
                        column,
                        "MAPPED_CLASS_NOT_LOCAL",
                        (
                            f"public node key {entry.key!r} maps to {class_name!r}, "
                            "which is not a top-level class in this module"
                        ),
                    )
                )
                continue
            mapped_class_names.add(class_name)
            public_name_by_class[class_name] = entry.key

        for class_name in sorted(mapped_class_names):
            _check_class_contract(
                class_node=classes[class_name],
                path=relative_path,
                findings=findings,
            )
            _check_event_suffixes(
                class_node=classes[class_name],
                public_name=public_name_by_class[class_name],
                path=relative_path,
                findings=findings,
            )

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _is_direct_prompt_server_send(node):
                line, column = _source_position(node.func)
                findings.append(
                    Finding(
                        relative_path,
                        line,
                        column,
                        "DIRECT_SEND_SYNC",
                        (
                            "published node sources must not call "
                            "PromptServer.instance.send_sync directly"
                        ),
                    )
                )

    entries_by_key: dict[str, list[MappingEntry]] = {}
    for entry in all_class_entries:
        entries_by_key.setdefault(entry.key, []).append(entry)
    for key in sorted(entries_by_key):
        occurrences = entries_by_key[key]
        first = occurrences[0]
        for duplicate in occurrences[1:]:
            findings.append(
                Finding(
                    duplicate.path,
                    duplicate.line,
                    duplicate.column,
                    "DUPLICATE_PUBLIC_KEY",
                    (
                        f"public node key {key!r} duplicates "
                        f"{first.path}:{first.line}:{first.column}"
                    ),
                )
            )

    findings.sort(
        key=lambda finding: (
            finding.path,
            finding.line,
            finding.column,
            finding.code,
            finding.message,
        )
    )
    return CheckResult(tuple(findings), len(paths), len(all_class_entries))


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Check modules/nodes Python sources without importing LF Nodes or "
            "its runtime dependencies."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="repository root containing modules/nodes (default: inferred)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _build_argument_parser().parse_args(argv)
    root = arguments.root.resolve()
    nodes_directory = root / "modules" / "nodes"
    if not nodes_directory.is_dir():
        print(
            f"ERROR: node source directory does not exist: {nodes_directory}",
            file=sys.stderr,
        )
        return 2

    result = check_repository(root)
    for finding in result.findings:
        print(finding.render())

    if result.findings:
        print(
            "FAIL: "
            f"{len(result.findings)} contract defect(s); scanned "
            f"{result.python_files} Python file(s) and "
            f"{result.public_mappings} public mapping(s)."
        )
        return 1

    print(
        "PASS: "
        f"{result.public_mappings} public mapping(s) checked across "
        f"{result.python_files} Python file(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
