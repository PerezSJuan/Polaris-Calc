from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .variable_types_compat import (
    VARIABLE_TYPE_BOOLEAN,
    VARIABLE_TYPE_BOOLEAN_COLUMN,
    VARIABLE_TYPE_COLUMN_NO_ERROR,
    VARIABLE_TYPE_COMPLEX,
    VARIABLE_TYPE_CONSTANT_NO_ERROR,
    VARIABLE_TYPE_MATRIX,
)

from .eval_types import ArityMismatchError, DimensionMismatchError, NonIntegerExponentError, ShapeMismatchError, TypeMismatchError
from .pool_schema import OperationSpec, PoolValue, canonical_type


@dataclass
class TypeDescriptor:
    type: str
    unit: str
    shape: tuple[int, ...] | None = None
    symbol_name: str = ""

    @property
    def canonical(self) -> str:
        return canonical_type(self.type)


def descriptor_from_pool_value(value: PoolValue) -> TypeDescriptor:
    return TypeDescriptor(type=value.type, unit=value.unit, shape=value.shape, symbol_name=value.name)


def _match_allowed(actual: str, allowed: Any) -> bool:
    if allowed is None:
        return True
    if isinstance(allowed, set):
        return actual in allowed or canonical_type(actual) in allowed or "column_*" in allowed and canonical_type(actual) == "column"
    if isinstance(allowed, str):
        return actual == allowed or canonical_type(actual) == allowed or allowed == "column_*" and canonical_type(actual) == "column"
    return False


def _scalarish(kind: str) -> bool:
    return kind in {"scalar", "complex"}


def _check_arity(op: OperationSpec, operand_count: int) -> None:
    if op.arity is not None:
        if operand_count != op.arity:
            raise ArityMismatchError(f"Operation '{op.name}' expects {op.arity} arguments, got {operand_count}", op.name)
        return
    min_arity = op.min_arity or 0
    max_arity = op.max_arity
    if operand_count < min_arity or (max_arity is not None and operand_count > max_arity):
        if max_arity is None:
            raise ArityMismatchError(f"Operation '{op.name}' expects at least {min_arity} arguments, got {operand_count}", op.name)
        raise ArityMismatchError(
            f"Operation '{op.name}' expects between {min_arity} and {max_arity} arguments, got {operand_count}",
            op.name,
        )


def check_type_compatibility(op: str | OperationSpec, operands: list[TypeDescriptor]) -> str:
    kinds = [operand.canonical for operand in operands]
    if isinstance(op, OperationSpec):
        _check_arity(op, len(operands))
        if isinstance(op.input_types, list):
            for idx, allowed in enumerate(op.input_types):
                if not _match_allowed(operands[idx].type, allowed):
                    raise TypeMismatchError(f"Operation '{op.name}' does not accept type '{operands[idx].type}' at position {idx}", op.name)
        elif op.input_types is not None:
            for operand in operands:
                if not _match_allowed(operand.type, op.input_types):
                    raise TypeMismatchError(f"Operation '{op.name}' does not accept type '{operand.type}'", op.name)
        if op.validator is not None:
            op.validator(operands)
        if op.result_type_rule is not None:
            return op.result_type_rule(operands)
        return op.output_type

    if any(kind.startswith("boolean") for kind in kinds) and op in {"+", "-", "*", "/", "^"}:
        raise TypeMismatchError("Boolean value used in arithmetic operation", op)

    left, right = kinds
    left_shape = operands[0].shape
    right_shape = operands[1].shape

    if op in {"+", "-"}:
        if _scalarish(left) and _scalarish(right):
            return VARIABLE_TYPE_COMPLEX if "complex" in kinds else VARIABLE_TYPE_CONSTANT_NO_ERROR
        if {left, right} <= {"scalar", "column"} or {left, right} <= {"complex", "column"}:
            return VARIABLE_TYPE_COLUMN_NO_ERROR
        if {left, right} <= {"scalar", "vector"}:
            return "vector"
        if left == right == "column" or left == right == "vector":
            return VARIABLE_TYPE_COLUMN_NO_ERROR if left == "column" else "vector"
        if left == right == "matrix":
            if left_shape and right_shape and left_shape != right_shape:
                raise ShapeMismatchError("Matrix shapes are incompatible for addition/subtraction", op)
            return VARIABLE_TYPE_MATRIX
        raise TypeMismatchError(f"Unsupported operand types for '{op}': {left}, {right}", op)

    if op == "*":
        if _scalarish(left) and _scalarish(right):
            return VARIABLE_TYPE_COMPLEX if "complex" in kinds else VARIABLE_TYPE_CONSTANT_NO_ERROR
        if (left == "scalar" and right in {"column", "matrix", "vector"}) or (right == "scalar" and left in {"column", "matrix", "vector"}):
            return operands[0].type if left != "scalar" else operands[1].type
        raise TypeMismatchError(f"Unsupported operand types for '*': {left}, {right}", op)

    if op == "@":
        if left != "matrix" or right != "matrix":
            raise TypeMismatchError(f"Unsupported operand types for '@': {left}, {right}", op)
        if left_shape and right_shape and len(left_shape) == 2 and len(right_shape) == 2 and left_shape[1] != right_shape[0]:
            raise ShapeMismatchError("Matrix shapes are incompatible for multiplication", op)
        return VARIABLE_TYPE_MATRIX

    if op == "/":
        if _scalarish(left) and _scalarish(right):
            return VARIABLE_TYPE_COMPLEX if "complex" in kinds else VARIABLE_TYPE_CONSTANT_NO_ERROR
        if left in {"column", "vector"} and right == "scalar":
            return operands[0].type
        if left == "scalar" and right in {"column", "vector"}:
            return operands[1].type
        raise TypeMismatchError(f"Unsupported operand types for '/': {left}, {right}", op)

    if op == "^":
        if right not in {"scalar", "complex"}:
            raise TypeMismatchError("Exponent must be scalar", op)
        if left in {"scalar", "complex"}:
            return VARIABLE_TYPE_COMPLEX if left == "complex" else VARIABLE_TYPE_CONSTANT_NO_ERROR
        if left in {"column", "vector"}:
            return operands[0].type
        if left == "matrix":
            return VARIABLE_TYPE_MATRIX
        raise TypeMismatchError(f"Unsupported operand types for '^': {left}, {right}", op)

    if op in {">", "<", ">=", "<=", "==", "!="}:
        if left == right == "matrix":
            raise TypeMismatchError("Matrix comparison is not supported", op)
        if _scalarish(left) and _scalarish(right):
            return VARIABLE_TYPE_BOOLEAN
        if {left, right} <= {"scalar", "column"} or left == right == "column":
            return VARIABLE_TYPE_BOOLEAN_COLUMN
        if {left, right} <= {"scalar", "vector"} or left == right == "vector":
            return VARIABLE_TYPE_BOOLEAN_COLUMN
        raise TypeMismatchError(f"Unsupported operand types for comparison '{op}': {left}, {right}", op)

    raise TypeMismatchError(f"Unsupported operation '{op}'", str(op))
