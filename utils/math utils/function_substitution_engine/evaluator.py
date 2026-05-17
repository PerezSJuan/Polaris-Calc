from __future__ import annotations

from copy import deepcopy
from typing import Any

from .variable_types_compat import VARIABLE_TYPE_BOOLEAN_COLUMN

from .ast_nodes import AddNode, CompareNode, FuncNode, MulNode, NumberNode, PowNode, SymbolNode
from .eval_types import (
    ArityMismatchError,
    ColumnLengthWarning,
    EvalResult,
    IndexOutOfBoundsError,
    NonIntegerExponentError,
    ShapeMismatchError,
)
from .parser import _sympy_to_ast, parse_expression, parse_latex_to_ast
from .pool_schema import (
    PoolValue,
    canonical_type,
    infer_shape,
    normalize_builtin_constants,
    normalize_extra_constants,
    normalize_operations,
    normalize_variables,
)
from .resolver import ResolvedNode, resolve_node
from .type_checker import TypeDescriptor, check_type_compatibility
from .units import combine_units, convert_result_unit, harmonize_additive_units, si_unit_for


def _result(value: Any, unit: str, type_name: str, warnings=None, index_errors=None) -> EvalResult:
    return EvalResult(value=value, unit=unit, type=type_name, warnings=warnings or [], index_errors=index_errors or [])


def _descriptor_from_result(result: EvalResult) -> TypeDescriptor:
    return TypeDescriptor(type=result.type, unit=result.unit, shape=infer_shape(result.value))


def _coerce_pool_result(pool_value: PoolValue) -> EvalResult:
    return _result(deepcopy(pool_value.value), pool_value.unit, pool_value.type)


def _apply_compare(op: str, left, right):
    if op == ">":
        return left > right
    if op == "<":
        return left < right
    if op == ">=":
        return left >= right
    if op == "<=":
        return left <= right
    if op == "==":
        return left == right
    if op == "!=":
        return left != right
    raise ValueError(op)


def _binary_elemwise(op: str, left: EvalResult, right: EvalResult, output_type: str, node_repr: str) -> EvalResult:
    left_kind = canonical_type(left.type)
    right_kind = canonical_type(right.type)
    warnings = [*left.warnings, *right.warnings]
    index_errors = [*left.index_errors, *right.index_errors]

    if op in {"+", "-", ">", "<", ">=", "<=", "==", "!="}:
        [left, right], unit_warnings = harmonize_additive_units([left, right], node_repr)
        warnings.extend(unit_warnings)
    unit = left.unit if op in {"+", "-"} else "bool" if op in {">", "<", ">=", "<=", "==", "!="} else combine_units(left.unit, right.unit, "*" if op == "*" else "/")

    if left_kind in {"scalar", "complex", "boolean"} and right_kind in {"scalar", "complex", "boolean"}:
        if op == "+":
            value = left.value + right.value
        elif op == "-":
            value = left.value - right.value
        elif op == "*":
            value = left.value * right.value
        elif op == "/":
            value = left.value / right.value
        else:
            value = _apply_compare(op, left.value, right.value)
        return _result(value, unit, output_type, warnings, index_errors)

    if op in {"+", "-", "/", ">", "<", ">=", "<=", "==", "!="} and (
        {left_kind, right_kind} <= {"scalar", "column"}
        or {left_kind, right_kind} <= {"scalar", "vector"}
        or {left_kind, right_kind} == {"column"}
        or {left_kind, right_kind} == {"vector"}
    ):
        lhs = left.value if isinstance(left.value, list) else [left.value] * len(right.value)
        rhs = right.value if isinstance(right.value, list) else [right.value] * len(left.value)
        size = max(len(lhs), len(rhs))
        values = []
        if len(lhs) != len(rhs):
            warnings.append(ColumnLengthWarning("Columns with different lengths produced partial result", node_repr))
        for idx in range(size):
            if idx >= len(lhs) or idx >= len(rhs):
                values.append(None)
                index_errors.append(IndexOutOfBoundsError(index=idx, column_name=node_repr, message="Missing column index", node_repr=node_repr))
                continue
            if op == "+":
                values.append(lhs[idx] + rhs[idx])
            elif op == "-":
                values.append(lhs[idx] - rhs[idx])
            elif op == "/":
                values.append(lhs[idx] / rhs[idx])
            else:
                values.append(_apply_compare(op, lhs[idx], rhs[idx]))
        final_unit = unit if output_type != VARIABLE_TYPE_BOOLEAN_COLUMN else "bool"
        return _result(values, final_unit, output_type, warnings, index_errors)

    if op == "*" and ((left_kind == "scalar" and right_kind in {"column", "vector"}) or (right_kind == "scalar" and left_kind in {"column", "vector"})):
        scalar = left.value if left_kind == "scalar" else right.value
        series = right.value if left_kind == "scalar" else left.value
        return _result([scalar * item for item in series], unit, output_type, warnings, index_errors)

    if op == "*" and ((left_kind == "scalar" and right_kind == "matrix") or (right_kind == "scalar" and left_kind == "matrix")):
        scalar = left.value if left_kind == "scalar" else right.value
        matrix = right.value if left_kind == "scalar" else left.value
        return _result([[scalar * item for item in row] for row in matrix], unit, output_type, warnings, index_errors)

    if op in {"+", "-"} and left_kind == right_kind == "matrix":
        if infer_shape(left.value) != infer_shape(right.value):
            raise ShapeMismatchError("Matrix shape mismatch", node_repr)
        values = []
        for left_row, right_row in zip(left.value, right.value):
            values.append([a + b if op == "+" else a - b for a, b in zip(left_row, right_row)])
        return _result(values, unit, output_type, warnings, index_errors)

    raise ShapeMismatchError(f"Unsupported element-wise operation '{op}'", node_repr)


def _matmul(left, right):
    if not left or not right:
        return []
    rows = len(left)
    inner = len(left[0])
    if any(len(row) != inner for row in left):
        raise ShapeMismatchError("Jagged left matrix", r"\matmul")
    if any(len(row) != len(right[0]) for row in right):
        pass
    if inner != len(right):
        raise ShapeMismatchError("Matrix shapes are incompatible for multiplication", r"\matmul")
    cols = len(right[0])
    return [[sum(left[i][k] * right[k][j] for k in range(inner)) for j in range(cols)] for i in range(rows)]


def _matrix_pow(matrix, exponent, node_repr: str):
    if int(exponent) != exponent:
        raise NonIntegerExponentError("Matrix exponent must be an integer", node_repr)
    exponent = int(exponent)
    shape = infer_shape(matrix)
    if shape is None or shape[0] != shape[1]:
        raise ShapeMismatchError("Matrix power requires a square matrix", node_repr)
    size = shape[0]
    result = [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]
    if exponent == 0:
        return result
    base = deepcopy(matrix)
    for _ in range(exponent):
        result = _matmul(result, base)
    return result


def evaluate_node(node: ResolvedNode) -> EvalResult:
    if isinstance(node.node, NumberNode):
        raw = node.node.value
        if isinstance(raw, complex):
            return _result(raw, "1", "complex")
        return _result(raw, "1", "constant_no_error")
    if isinstance(node.node, SymbolNode):
        return _coerce_pool_result(node.symbol)
    if isinstance(node.node, AddNode):
        current = evaluate_node(node.children[0])
        for child in node.children[1:]:
            next_result = evaluate_node(child)
            current = _binary_elemwise(
                "+",
                current,
                next_result,
                check_type_compatibility("+", [_descriptor_from_result(current), _descriptor_from_result(next_result)]),
                str(node.node),
            )
        return current
    if isinstance(node.node, MulNode):
        current = evaluate_node(node.children[0])
        for child in node.children[1:]:
            next_result = evaluate_node(child)
            descs = [_descriptor_from_result(current), _descriptor_from_result(next_result)]
            if canonical_type(descs[1].type) == "scalar" and next_result.unit == "1" and next_result.value == -1 and canonical_type(descs[0].type) in {"scalar", "column", "vector", "matrix"}:
                pass
            current = _binary_elemwise("*", current, next_result, check_type_compatibility("*", descs), str(node.node))
        return current
    if isinstance(node.node, PowNode):
        base = evaluate_node(node.children[0])
        exponent = evaluate_node(node.children[1])
        output_type = check_type_compatibility("^", [_descriptor_from_result(base), _descriptor_from_result(exponent)])
        if canonical_type(base.type) == "matrix":
            value = _matrix_pow(base.value, exponent.value, str(node.node))
            unit = f"{base.unit}^{int(exponent.value)}" if base.unit != "1" else "1"
            return _result(value, unit, output_type, [*base.warnings, *exponent.warnings], [*base.index_errors, *exponent.index_errors])
        if isinstance(base.value, list):
            return _result([item ** exponent.value if item is not None else None for item in base.value], f"{base.unit}^{exponent.value}" if base.unit != "1" else "1", output_type, [*base.warnings, *exponent.warnings], [*base.index_errors, *exponent.index_errors])
        unit = "1" if base.unit == "1" else f"{base.unit}^{int(exponent.value) if float(exponent.value).is_integer() else exponent.value}"
        return _result(base.value ** exponent.value, unit, output_type, [*base.warnings, *exponent.warnings], [*base.index_errors, *exponent.index_errors])
    if isinstance(node.node, CompareNode):
        left = evaluate_node(node.children[0])
        right = evaluate_node(node.children[1])
        return _binary_elemwise(node.node.operator, left, right, check_type_compatibility(node.node.operator, [_descriptor_from_result(left), _descriptor_from_result(right)]), str(node.node))
    if isinstance(node.node, FuncNode):
        operands = [evaluate_node(child) for child in node.children]
        output_type = check_type_compatibility(node.operation, [_descriptor_from_result(operand) for operand in operands])
        if len(operands) != node.operation.arity:
            raise ArityMismatchError(f"Operation '{node.operation.name}' expects {node.operation.arity} arguments", str(node.node))
        if node.operation.name == r"\matmul":
            [left, right], warnings = operands, []
            if len(left.value[0]) != len(right.value):
                raise ShapeMismatchError("Matrix shapes are incompatible for multiplication", str(node.node))
            value = _matmul(left.value, right.value)
            unit = combine_units(left.unit, right.unit, "*") if node.operation.preserves_units else "1"
            return _result(value, unit, output_type, [*left.warnings, *right.warnings, *warnings], [*left.index_errors, *right.index_errors])
        if node.operation.preserves_units:
            harmonized, warnings = harmonize_additive_units(operands, str(node.node))
            base_unit = harmonized[0].unit if harmonized else "1"
        else:
            harmonized, warnings = operands, []
            base_unit = "1"
        value = node.operation.fn(*[operand.value for operand in harmonized])
        merged_warnings = warnings[:]
        merged_index_errors = []
        for operand in harmonized:
            merged_warnings.extend(operand.warnings)
            merged_index_errors.extend(operand.index_errors)
        return _result(value, base_unit, output_type, merged_warnings, merged_index_errors)
    raise TypeError(f"Unsupported resolved node type: {type(node.node)}")


def check_dimensions(expr, variables: dict, extra_constants: dict | None = None, operations: dict | None = None) -> str:
    normalized_variables = normalize_variables(variables)
    normalized_constants = normalize_extra_constants(extra_constants)
    normalized_builtin = normalize_builtin_constants()
    normalized_operations = normalize_operations(operations)
    operation_names = list(normalized_operations.keys())

    if isinstance(expr, str):
        parsed = parse_expression(expr, mode="auto", operation_names=operation_names)
        ast = _sympy_to_ast(parsed)
    else:
        ast = _sympy_to_ast(expr)

    resolved = resolve_node(ast, normalized_variables, normalized_constants, normalized_builtin, normalized_operations)

    def walk(resolved_node: ResolvedNode) -> str:
        if isinstance(resolved_node.node, NumberNode):
            return "1"
        if isinstance(resolved_node.node, SymbolNode):
            return resolved_node.symbol.unit
        if isinstance(resolved_node.node, AddNode):
            units = [walk(child) for child in resolved_node.children]
            base = units[0]
            for unit in units[1:]:
                if unit != base:
                    from .units import same_dim

                    if not same_dim(base, unit):
                        raise ValueError(f"Invalid sum: incompatible dimensions ({base} vs {unit})")
            return base
        if isinstance(resolved_node.node, MulNode):
            units = [walk(child) for child in resolved_node.children]
            current = units[0]
            for unit in units[1:]:
                current = combine_units(current, unit, "*")
            return current
        if isinstance(resolved_node.node, PowNode):
            base_unit = walk(resolved_node.children[0])
            exponent_result = evaluate_node(resolved_node.children[1])
            exponent = exponent_result.value
            if base_unit == "1":
                return "1"
            exp_str = int(exponent) if float(exponent).is_integer() else exponent
            return f"{base_unit}^{exp_str}"
        if isinstance(resolved_node.node, CompareNode):
            left = walk(resolved_node.children[0])
            right = walk(resolved_node.children[1])
            from .units import same_dim

            if not same_dim(left, right):
                raise ValueError(f"Invalid comparison: incompatible dimensions ({left} vs {right})")
            return "bool"
        if isinstance(resolved_node.node, FuncNode):
            operand_units = [walk(child) for child in resolved_node.children]
            if resolved_node.operation.preserves_units and operand_units:
                base = operand_units[0]
                for unit in operand_units[1:]:
                    from .units import same_dim

                    if not same_dim(base, unit):
                        raise ValueError(f"Invalid function application: incompatible dimensions ({base} vs {unit})")
                return base
            return "1"
        raise TypeError(f"Unsupported node type in dimensional check: {type(resolved_node.node)}")

    return walk(resolved)


def constant_in_system(name: str, target_unit: str):
    result = evaluate(name, {}, target_unit=target_unit)
    return result.value, result.unit


def evaluate(
    expr: str,
    variables: dict,
    extra_constants: dict | None = None,
    operations: dict | None = None,
    target_unit: str | None = None,
    mode: str = "auto",
) -> EvalResult:
    normalized_variables = normalize_variables(variables)
    normalized_constants = normalize_extra_constants(extra_constants)
    normalized_builtin = normalize_builtin_constants()
    normalized_operations = normalize_operations(operations)

    operation_names = list(normalized_operations.keys())
    if mode == "latex":
        ast = parse_latex_to_ast(expr, operation_names)
    else:
        sympy_expr = parse_expression(expr, mode=mode, operation_names=operation_names)
        ast = _sympy_to_ast(sympy_expr)

    resolved = resolve_node(ast, normalized_variables, normalized_constants, normalized_builtin, normalized_operations)
    result = evaluate_node(resolved)
    if target_unit:
        result = convert_result_unit(result, target_unit)
    elif result.unit not in {"1", "bool"}:
        try:
            result = convert_result_unit(result, si_unit_for(result.unit))
        except Exception:
            pass
    return result
