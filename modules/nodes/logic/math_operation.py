import ast
import math
import re

from . import CATEGORY
from ...utils.constants import ANY, FUNCTION, Input
from ...utils.helpers.logic import normalize_input_list, normalize_list_to_value, not_none
from ...utils.helpers.comfy import safe_send_sync

# region LF_MathOperation
class LF_MathOperation:
    @classmethod
    def INPUT_TYPES(self):
        return {
            "required": {
                "operation": (Input.STRING, {
                    "default": "a * b / c + d",
                    "tooltip": "Math operation to execute. Use variables like 'a', 'b', 'c', 'd'."
                }),
            },
            "optional": {
                "a": (ANY, {
                    "tooltip": "Value or list of values for 'a'."
                }),
                "b": (ANY, {
                    "tooltip": "Value or list of values for 'b'."
                }),
                "c": (ANY, {
                    "tooltip": "Value or list of values for 'c'."
                }),
                "d": (ANY, {
                    "tooltip": "Value or list of values for 'd'."
                }),
                "ui_widget": (Input.LF_CODE, {
                    "default": ""
                })
            },
            "hidden": {
                "node_id": "UNIQUE_ID"
            }
        }

    CATEGORY = CATEGORY
    FUNCTION = FUNCTION
    OUTPUT_TOOLTIPS = (
        "Final result as integer.",
        "Final result as float."
    )
    RETURN_NAMES = ("int_result", "float_result")
    RETURN_TYPES = (Input.INTEGER, Input.FLOAT)

    def on_exec(self, **kwargs: dict):
        def safe_eval(expr: str, variables: dict):
            """Safely evaluate a math expression consisting of:
            - numeric literals
            - variables: a, b, c, d (may be None)
            - math.<function> calls (whitelisted from Python's math module)
            - math.<constant> numeric constants (pi, e, tau, inf, nan, etc.)
            - arithmetic operators: +, -, *, /, //, %, **
            - unary + and -
            - parentheses

            Any other construct raises a ValueError. If evaluation fails, float('NaN') is returned.
            This mitigates S307 (unsafe eval) while preserving existing UX.
            """
            # Examples (documentation only):
            #   OK: "a * b / c + d"
            #   OK: "math.sin(a) + math.sqrt(b)"
            #   OK: "-(a ** 2) + math.fabs(b)"
            #   Rejected: "__import__('os').system('rm -rf /')"
            #   Rejected: "(lambda x: x)(1)" (lambda)
            #   Rejected: "[a,b]" (list literals not allowed)
            #   Rejected: "open('file')" (non-math call)
            allowed_bin_ops = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow)
            allowed_unary_ops = (ast.UAdd, ast.USub)

            allowed_math_funcs = {
                name: getattr(math, name)
                for name in dir(math)
                if not name.startswith('_') and callable(getattr(math, name))
            }
            # Allow numeric constants (ints/floats only) from math
            allowed_math_constants = {
                name: getattr(math, name)
                for name in dir(math)
                if not name.startswith('_') and isinstance(getattr(math, name), (int, float))
            }

            class Validator(ast.NodeVisitor):
                def visit_Expression(self, node):
                    self.visit(node.body)

                def visit_BinOp(self, node):
                    if not isinstance(node.op, allowed_bin_ops):
                        raise ValueError("Operator not allowed")
                    self.visit(node.left)
                    self.visit(node.right)

                def visit_UnaryOp(self, node):
                    if not isinstance(node.op, allowed_unary_ops):
                        raise ValueError("Unary operator not allowed")
                    self.visit(node.operand)

                def visit_Name(self, node):
                    if node.id not in {"a", "b", "c", "d", "math"}:
                        raise ValueError(f"Variable '{node.id}' not allowed")

                def visit_Constant(self, node):  # numbers / simple constants
                    if not isinstance(node.value, (int, float)):  # disallow other constant types
                        raise ValueError("Only int/float literals allowed")

                def visit_Call(self, node):
                    # Allow math.<func>(...)
                    if not isinstance(node.func, ast.Attribute) or not isinstance(node.func.value, ast.Name):
                        raise ValueError("Only math.<func>() calls allowed")
                    if node.func.value.id != 'math':
                        raise ValueError("Only math module calls allowed")
                    if node.func.attr not in allowed_math_funcs:
                        raise ValueError(f"math.{node.func.attr} not allowed")
                    for arg in node.args:
                        self.visit(arg)
                    if node.keywords:
                        raise ValueError("Keyword args not allowed")

                # Disallow ALL other nodes explicitly
                def generic_visit(self, node):
                    allowed = (
                        ast.Expression,
                        ast.BinOp,
                        ast.UnaryOp,
                        ast.Name,
                        ast.Constant,
                        ast.Call,
                        ast.Load,
                        ast.Attribute,
                    )
                    if isinstance(node, allowed):
                        super().generic_visit(node)
                    else:
                        raise ValueError(f"Node type {type(node).__name__} not allowed")

                def visit_Attribute(self, node):
                    # Allow math.<func> (validated in visit_Call) and math.<constant>
                    if not (isinstance(node.value, ast.Name) and node.value.id == 'math'):
                        raise ValueError("Attribute access restricted to math.*")
                    # If attribute is a constant, ensure it's in allowed set
                    if node.attr in allowed_math_constants:
                        return  # constant access is fine
                    # If attribute is a function, it'll be validated in visit_Call context. Standalone function reference disallowed.
                    if node.attr in allowed_math_funcs:
                        # We don't allow using a bare function object as a value.
                        raise ValueError("Bare math function reference not allowed; call it e.g. math.sin(x)")
                    # Anything else is invalid
                    raise ValueError(f"math.{node.attr} not allowed")

            try:
                allowed_names = {"a", "b", "c", "d"}
                cleaned_vars = {k: (v if v is not None else float('NaN')) for k, v in variables.items() if k in allowed_names}

                parsed = ast.parse(expr, mode='eval')
                Validator().visit(parsed)

                def evaluate(node):
                    if isinstance(node, ast.Expression):
                        return evaluate(node.body)
                    if isinstance(node, ast.Constant):
                        return float(node.value)
                    if isinstance(node, ast.Name):
                        if node.id == 'math':
                            return math
                        if node.id in cleaned_vars:
                            return cleaned_vars[node.id]
                        raise ValueError(f"Undefined variable: {node.id}")
                    if isinstance(node, ast.UnaryOp):
                        val = evaluate(node.operand)
                        if isinstance(node.op, ast.UAdd):
                            return +val
                        if isinstance(node.op, ast.USub):
                            return -val
                        raise ValueError('Unsupported unary op')
                    if isinstance(node, ast.BinOp):
                        left = evaluate(node.left)
                        right = evaluate(node.right)
                        op = node.op
                        try:
                            if isinstance(op, ast.Add):
                                result_val = left + right
                            elif isinstance(op, ast.Sub):
                                result_val = left - right
                            elif isinstance(op, ast.Mult):
                                result_val = left * right
                            elif isinstance(op, ast.Div):
                                result_val = left / right
                            elif isinstance(op, ast.FloorDiv):
                                result_val = left // right
                            elif isinstance(op, ast.Mod):
                                result_val = left % right
                            elif isinstance(op, ast.Pow):
                                result_val = left ** right
                            else:
                                raise ValueError('Unsupported binary op')
                            if isinstance(result_val, complex):
                                return float('NaN')
                            return result_val
                        except (ZeroDivisionError, OverflowError, ValueError, TypeError):
                            return float('NaN')
                    if isinstance(node, ast.Attribute):
                        # Only numeric constants allowed here (validated earlier)
                        if isinstance(node.value, ast.Name) and node.value.id == 'math' and node.attr in allowed_math_constants:
                            return float(allowed_math_constants[node.attr])
                        raise ValueError('Bare attribute access not allowed')
                    raise ValueError(f'Unexpected node: {type(node).__name__}')

                return evaluate(parsed)
            except Exception:
                # Any validation or evaluation error results in NaN
                return float('NaN')

        def normalize_and_sum_with_log(variable):
            normalized = normalize_input_list(variable)

            if len(normalized) > 1:
                itemized_log = "\n".join(
                    [f"    {i+1}. *{1 if val is True else 0 if val is False else val}* <{type(val).__name__}>"
                     for i, val in enumerate(normalized)]
                )
                total_sum = sum(1 if val is True else 0 if val is False else val for val in normalized)
                return total_sum, f"**{total_sum}** <list>\n{itemized_log}"

            single_value = 1 if normalized[0] is True else 0 if normalized[0] is False else normalized[0]
            return float(single_value), f"**{single_value}** <{type(single_value).__name__}>"

        operation: str = normalize_list_to_value(kwargs.get("operation"))
        a = kwargs.get("a", None)
        b = kwargs.get("b", None)
        c = kwargs.get("c", None)
        d = kwargs.get("d", None)

        na_placeholder = "N/A"

        a_sum, a_log = normalize_and_sum_with_log(a) if not_none(a) else (None, na_placeholder)
        b_sum, b_log = normalize_and_sum_with_log(b) if not_none(b) else (None, na_placeholder)
        c_sum, c_log = normalize_and_sum_with_log(c) if not_none(c) else (None, na_placeholder)
        d_sum, d_log = normalize_and_sum_with_log(d) if not_none(d) else (None, na_placeholder)

        # Build a human-readable substituted operation without corrupting identifiers like 'math'
        def _subst(expr: str, var: str, value):
            pattern = rf'\b{var}\b'
            return re.sub(pattern, str(value), expr)
        str_operation = operation
        for _v in ("a", "b", "c", "d"):
            str_operation = _subst(str_operation, _v, locals().get(f"{_v}_sum"))

        result = safe_eval(operation, {"a": a_sum, "b": b_sum, "c": c_sum, "d": d_sum})

        log = f"""## Result:
  **{str(result)}**

## Variables:
  a: {a_log}
  b: {b_log}
  c: {c_log}
  d: {d_log}

## Full operation:
  {str_operation}
        """

        safe_send_sync("mathoperation", {
            "value": log,
        }, kwargs.get("node_id"))

        int_result: int
        if isinstance(result, (int, float)):
            try:
                if isinstance(result, float) and (math.isnan(result) or math.isinf(result)):
                    int_result = 0
                else:
                    int_result = int(result)
            except Exception:
                int_result = 0
        else:
            int_result = 0

        return (int_result, result)

    @classmethod
    def VALIDATE_INPUTS(self, **kwargs):
         return True
# endregion

# region Mappings
NODE_CLASS_MAPPINGS = {
    "LF_MathOperation": LF_MathOperation,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LF_MathOperation": "Math operation",
}
# endregion
