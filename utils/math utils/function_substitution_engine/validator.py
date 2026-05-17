from __future__ import annotations

from .ast_nodes import AddNode, CompareNode, FuncNode, MulNode, NumberNode, PowNode, SymbolNode
from .eval_types import ValidationIssue, ValidationReport
from .parser import parse_expression
from .pool_schema import normalize_builtin_constants, normalize_extra_constants, normalize_operations, normalize_variables
from .resolver import resolve_node
from .type_checker import TypeDescriptor, check_type_compatibility, descriptor_from_pool_value
from .units import get_dim, same_dim


def _warning(code: str, message: str, node_repr: str) -> ValidationIssue:
    return ValidationIssue(code=code, message=message, node_repr=node_repr, severity="warning")


def _error(code: str, message: str, node_repr: str) -> ValidationIssue:
    return ValidationIssue(code=code, message=message, node_repr=node_repr, severity="error")


def validate(
    expr: str,
    variables: dict,
    extra_constants: dict | None = None,
    operations: dict | None = None,
    target_unit: str | None = None,
    mode: str = "auto",
) -> ValidationReport:
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
    normalized_variables = normalize_variables(variables)
    normalized_constants = normalize_extra_constants(extra_constants)
    normalized_builtin = normalize_builtin_constants()
    normalized_operations = normalize_operations(operations)

    try:
        sympy_expr = parse_expression(expr, mode=mode, operation_names=list(normalized_operations.keys()))
        from .parser import _sympy_to_ast
        ast = _sympy_to_ast(sympy_expr)
    except Exception as exc:
        return ValidationReport(valid=False, errors=[_error("SYNTAX_ERROR", str(exc), expr)], warnings=[])

    def walk(node) -> TypeDescriptor | None:
        if isinstance(node, NumberNode):
            return TypeDescriptor(type="constant_no_error", unit="1")
        if isinstance(node, SymbolNode):
            try:
                resolved = resolve_node(node, normalized_variables, normalized_constants, normalized_builtin, normalized_operations)
            except Exception as exc:
                code = getattr(exc, "code", "EVAL_ERROR")
                errors.append(_error(code, str(exc), str(node)))
                return None
            return descriptor_from_pool_value(resolved.symbol)
        if isinstance(node, FuncNode):
            try:
                resolved = resolve_node(node, normalized_variables, normalized_constants, normalized_builtin, normalized_operations)
            except Exception as exc:
                code = getattr(exc, "code", "EVAL_ERROR")
                errors.append(_error(code, str(exc), str(node)))
                return None
            child_descs = [walk(child.node) for child in resolved.children]
            available = [desc for desc in child_descs if desc is not None]
            if len(available) != len(child_descs):
                return None
            try:
                output_type = check_type_compatibility(resolved.operation, available)
            except Exception as exc:
                errors.append(_error(getattr(exc, "code", "TYPE_MISMATCH"), str(exc), str(node)))
                return None
            if resolved.operation.arity != len(available):
                errors.append(_error("ARITY_MISMATCH", f"Expected {resolved.operation.arity} arguments", str(node)))
            if any(desc.canonical in {"column", "vector", "matrix"} for desc in available) and any(desc.canonical == "scalar" for desc in available):
                warnings.append(_warning("IMPLICIT_BROADCAST", "Scalar input will be broadcast across a structured operand", str(node)))
            if any(desc.canonical in {"column", "vector"} for desc in available):
                warnings.append(_warning("COLUMN_LENGTH_UNKNOWN", "Column lengths are validated during evaluation", str(node)))
            return TypeDescriptor(type=output_type, unit=available[0].unit if resolved.operation.preserves_units and available else "1")
        if isinstance(node, AddNode):
            child_descs = [walk(child) for child in node.operands]
            available = [desc for desc in child_descs if desc is not None]
            if len(available) != len(child_descs):
                return None
            for left, right in zip(available, available[1:]):
                try:
                    check_type_compatibility("+", [left, right])
                except Exception as exc:
                    errors.append(_error(getattr(exc, "code", "TYPE_MISMATCH"), str(exc), str(node)))
                if not same_dim(left.unit, right.unit):
                    errors.append(_error("DIMENSION_MISMATCH", f"Incompatible dimensions: {left.unit} vs {right.unit}", str(node)))
                elif left.unit != right.unit:
                    warnings.append(_warning("UNIT_CONVERSION_NEEDED", f"Implicit conversion from {right.unit} to {left.unit}", str(node)))
            if any(desc.canonical in {"column", "vector"} for desc in available) and any(desc.canonical == "scalar" for desc in available):
                warnings.append(_warning("IMPLICIT_BROADCAST", "Scalar input will be broadcast across a column/vector", str(node)))
            return available[0]
        if isinstance(node, MulNode):
            child_descs = [walk(child) for child in node.operands]
            available = [desc for desc in child_descs if desc is not None]
            if len(available) != len(child_descs):
                return None
            current = available[0]
            for nxt in available[1:]:
                try:
                    output_type = check_type_compatibility("*", [current, nxt])
                except Exception as exc:
                    errors.append(_error(getattr(exc, "code", "TYPE_MISMATCH"), str(exc), str(node)))
                    return None
                current = TypeDescriptor(type=output_type, unit=f"{current.unit}*{nxt.unit}")
            return current
        if isinstance(node, PowNode):
            base = walk(node.base)
            exponent = walk(node.exponent)
            if base is None or exponent is None:
                return None
            try:
                output_type = check_type_compatibility("^", [base, exponent])
            except Exception as exc:
                errors.append(_error(getattr(exc, "code", "TYPE_MISMATCH"), str(exc), str(node)))
                return None
            return TypeDescriptor(type=output_type, unit=base.unit)
        if isinstance(node, CompareNode):
            left = walk(node.left)
            right = walk(node.right)
            if left is None or right is None:
                return None
            try:
                output_type = check_type_compatibility(node.operator, [left, right])
            except Exception as exc:
                code = "BOOLEAN_IN_ARITHMETIC" if "Boolean" in str(exc) else getattr(exc, "code", "TYPE_MISMATCH")
                errors.append(_error(code, str(exc), str(node)))
                return None
            if not same_dim(left.unit, right.unit):
                errors.append(_error("DIMENSION_MISMATCH", f"Incompatible dimensions: {left.unit} vs {right.unit}", str(node)))
            return TypeDescriptor(type=output_type, unit="bool")
        return None

    final_desc = walk(ast)
    if target_unit and final_desc is not None:
        try:
            if get_dim(final_desc.unit) != get_dim(target_unit):
                errors.append(_error("TARGET_UNIT_DIMENSION_MISMATCH", f"Target unit '{target_unit}' is incompatible with '{final_desc.unit}'", str(ast)))
        except Exception as exc:
            errors.append(_error("TARGET_UNIT_DIMENSION_MISMATCH", str(exc), str(ast)))

    return ValidationReport(valid=not errors, errors=errors, warnings=warnings)
