"""Static contracts for metadata exposed by every published LF node.

The package discovers node modules dynamically, so this test reads the same
``NODE_CLASS_MAPPINGS`` declarations without importing ComfyUI or optional
model dependencies.  Keeping the check source-based also makes its result
independent of module import order and the machine's installed models.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterator


REPO_ROOT = Path(__file__).resolve().parents[3]
NODES_ROOT = REPO_ROOT / "modules" / "nodes"
OUTPUT_METADATA = ("RETURN_NAMES", "OUTPUT_TOOLTIPS")


def _assignment_value(statement: ast.stmt, attribute: str) -> ast.expr | None:
    if isinstance(statement, ast.Assign):
        if any(isinstance(target, ast.Name) and target.id == attribute for target in statement.targets):
            return statement.value
    elif isinstance(statement, ast.AnnAssign):
        if isinstance(statement.target, ast.Name) and statement.target.id == attribute:
            return statement.value
    return None


def _class_scope_statements(statements: list[ast.stmt]) -> Iterator[ast.stmt]:
    """Yield class-scope statements, including conditional branches.

    Function and nested-class bodies are deliberately excluded: assignments
    there do not define Comfy node declaration metadata.
    """

    for statement in statements:
        yield statement
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue

        nested_blocks: list[list[ast.stmt]] = []
        for field in ("body", "orelse", "finalbody"):
            block = getattr(statement, field, None)
            if isinstance(block, list):
                nested_blocks.append(block)

        if isinstance(statement, ast.Try):
            nested_blocks.extend(handler.body for handler in statement.handlers)
        elif isinstance(statement, ast.Match):
            nested_blocks.extend(case.body for case in statement.cases)

        for block in nested_blocks:
            yield from _class_scope_statements(block)


def _scalar_value(expression: ast.expr) -> int | str:
    if isinstance(expression, ast.Constant) and isinstance(expression.value, int):
        return expression.value
    if (
        isinstance(expression, ast.Call)
        and isinstance(expression.func, ast.Name)
        and expression.func.id == "len"
        and len(expression.args) == 1
        and isinstance(expression.args[0], ast.Name)
    ):
        return f"len({expression.args[0].id})"
    raise AssertionError(f"Unsupported sequence multiplier: {ast.unparse(expression)}")


def _sum_cardinality(left: int | str, right: int | str) -> int | str:
    if isinstance(left, int) and isinstance(right, int):
        return left + right
    return f"({left}+{right})"


def _multiply_cardinality(cardinality: int | str, scalar: int | str) -> int | str:
    if isinstance(cardinality, int) and isinstance(scalar, int):
        return cardinality * scalar
    if cardinality == 1:
        return scalar
    if scalar == 1:
        return cardinality
    return f"({cardinality}*{scalar})"


def _sequence_cardinality(expression: ast.expr) -> int | str:
    if isinstance(expression, (ast.Tuple, ast.List)):
        cardinality: int | str = 0
        for element in expression.elts:
            element_cardinality = (
                _sequence_cardinality(element.value)
                if isinstance(element, ast.Starred)
                else 1
            )
            cardinality = _sum_cardinality(cardinality, element_cardinality)
        return cardinality

    if isinstance(expression, ast.Name):
        return f"len({expression.id})"

    if isinstance(expression, ast.BinOp) and isinstance(expression.op, ast.Add):
        return _sum_cardinality(
            _sequence_cardinality(expression.left),
            _sequence_cardinality(expression.right),
        )

    if isinstance(expression, ast.BinOp) and isinstance(expression.op, ast.Mult):
        try:
            sequence = _sequence_cardinality(expression.left)
            scalar = _scalar_value(expression.right)
        except AssertionError:
            sequence = _sequence_cardinality(expression.right)
            scalar = _scalar_value(expression.left)
        return _multiply_cardinality(sequence, scalar)

    if (
        isinstance(expression, ast.Call)
        and isinstance(expression.func, ast.Name)
        and expression.func.id in {"list", "tuple"}
        and len(expression.args) == 1
    ):
        return _sequence_cardinality(expression.args[0])

    raise AssertionError(f"Unsupported output metadata declaration: {ast.unparse(expression)}")


def _published_classes(tree: ast.Module, path: Path) -> list[tuple[str, ast.ClassDef]]:
    classes = {
        statement.name: statement
        for statement in tree.body
        if isinstance(statement, ast.ClassDef)
    }
    published: list[tuple[str, ast.ClassDef]] = []

    for statement in tree.body:
        mapping = _assignment_value(statement, "NODE_CLASS_MAPPINGS")
        if mapping is None:
            continue
        assert isinstance(mapping, ast.Dict), f"{path}: NODE_CLASS_MAPPINGS must be a dict literal"

        for key, value in zip(mapping.keys, mapping.values):
            assert (
                isinstance(key, ast.Constant)
                and isinstance(key.value, str)
                and isinstance(value, ast.Name)
            ), f"{path}: published node mappings must use literal names and local classes"
            assert value.id in classes, f"{path}: mapped class {value.id!r} was not found"
            published.append((key.value, classes[value.id]))

    return published


def _metadata_cardinalities(node_class: ast.ClassDef, attribute: str) -> set[int | str]:
    values = [
        value
        for statement in _class_scope_statements(node_class.body)
        if (value := _assignment_value(statement, attribute)) is not None
    ]
    return {_sequence_cardinality(value) for value in values}


def test_published_node_output_metadata_matches_return_types() -> None:
    failures: list[str] = []
    published_count = 0

    for path in sorted(NODES_ROOT.rglob("*.py")):
        if path.name == "__init__.py" or "tests" in path.parts or path.name.startswith("test_"):
            continue

        tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        for public_name, node_class in _published_classes(tree, path):
            published_count += 1
            return_types = _metadata_cardinalities(node_class, "RETURN_TYPES")
            if not return_types:
                failures.append(f"{public_name}: RETURN_TYPES is missing")
                continue

            for attribute in OUTPUT_METADATA:
                cardinalities = _metadata_cardinalities(node_class, attribute)
                if cardinalities and cardinalities != return_types:
                    failures.append(
                        f"{public_name}: {attribute} has {sorted(cardinalities, key=str)!r}; "
                        f"RETURN_TYPES has {sorted(return_types, key=str)!r}"
                    )

    assert published_count > 0, "No published LF nodes were discovered"
    assert not failures, "Output metadata cardinality mismatches:\n" + "\n".join(failures)
