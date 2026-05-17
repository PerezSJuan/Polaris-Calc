from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import sympy as sp

from .variable_types_compat import (
    VARIABLE_TYPE_BOOLEAN,
    VARIABLE_TYPE_BOOLEAN_COLUMN,
    VARIABLE_TYPE_COLUMN_NO_ERROR,
    VARIABLE_TYPE_COLUMN_WITH_ERROR_PER_VALUE,
    VARIABLE_TYPE_COLUMN_WITH_SINGLE_ERROR,
    VARIABLE_TYPE_COMPLEX,
    VARIABLE_TYPE_CONSTANT_NO_ERROR,
    VARIABLE_TYPE_CONSTANT_WITH_ERROR,
    VARIABLE_TYPE_FORMULA_NO_ERROR,
    VARIABLE_TYPE_FORMULA_WITH_ERROR,
    VARIABLE_TYPE_MATRIX,
    VARIABLE_TYPE_VECTOR,
)


CONSTANTS = {
    "e": (sp.E, "1"),
    "pi": (sp.pi, "1"),
    "G": (6.67430e-11, "m^3/(kg*s^2)"),
    "c": (299792458, "m/s"),
    "h": (6.62607015e-34, "J*s"),
    "kB": (1.380649e-23, "J/K"),
    "g0": (9.80665, "m/s^2"),
}

SCALAR_TYPES = {
    VARIABLE_TYPE_CONSTANT_NO_ERROR,
    VARIABLE_TYPE_CONSTANT_WITH_ERROR,
    VARIABLE_TYPE_FORMULA_NO_ERROR,
    VARIABLE_TYPE_FORMULA_WITH_ERROR,
}
COLUMN_TYPES = {
    VARIABLE_TYPE_COLUMN_NO_ERROR,
    VARIABLE_TYPE_COLUMN_WITH_SINGLE_ERROR,
    VARIABLE_TYPE_COLUMN_WITH_ERROR_PER_VALUE,
}


@dataclass
class PoolValue:
    name: str
    type: str
    value: Any
    unit: str = "1"
    shape: tuple[int, ...] | None = None


@dataclass
class OperationSpec:
    name: str
    fn: Callable[..., Any]
    arity: int
    input_types: Any
    output_type: str
    preserves_units: bool = True


def _default_sum(column):
    return sum(v for v in column if v is not None)


def _default_mean(column):
    valid = [v for v in column if v is not None]
    return sum(valid) / len(valid) if valid else 0.0


def _default_matmul(left, right):
    rows = len(left)
    inner = len(left[0]) if rows else 0
    cols = len(right[0]) if right else 0
    return [
        [sum(left[i][k] * right[k][j] for k in range(inner)) for j in range(cols)]
        for i in range(rows)
    ]


DEFAULT_OPERATIONS = {
    r"\sum": OperationSpec(
        name=r"\sum",
        fn=_default_sum,
        arity=1,
        input_types={"column", "vector"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        preserves_units=True,
    ),
    r"\mean": OperationSpec(
        name=r"\mean",
        fn=_default_mean,
        arity=1,
        input_types={"column", "vector"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        preserves_units=True,
    ),
    r"\matmul": OperationSpec(
        name=r"\matmul",
        fn=_default_matmul,
        arity=2,
        input_types=[{"matrix"}, {"matrix"}],
        output_type=VARIABLE_TYPE_MATRIX,
        preserves_units=True,
    ),
}


def infer_shape(value: Any) -> tuple[int, ...] | None:
    if isinstance(value, list):
        if value and isinstance(value[0], list):
            return (len(value), len(value[0]))
        return (len(value),)
    return None


def infer_type_from_value(value: Any) -> str:
    if isinstance(value, bool):
        return VARIABLE_TYPE_BOOLEAN
    if isinstance(value, complex):
        return VARIABLE_TYPE_COMPLEX
    if isinstance(value, list):
        if value and isinstance(value[0], list):
            return VARIABLE_TYPE_MATRIX
        if value and all(isinstance(item, bool) for item in value):
            return VARIABLE_TYPE_BOOLEAN_COLUMN
        return VARIABLE_TYPE_COLUMN_NO_ERROR
    return VARIABLE_TYPE_CONSTANT_NO_ERROR


def canonical_type(var_type: str) -> str:
    if var_type in SCALAR_TYPES:
        return "scalar"
    if var_type in COLUMN_TYPES:
        return "column"
    if var_type == VARIABLE_TYPE_VECTOR:
        return "vector"
    if var_type == VARIABLE_TYPE_MATRIX:
        return "matrix"
    if var_type == VARIABLE_TYPE_COMPLEX:
        return "complex"
    if var_type == VARIABLE_TYPE_BOOLEAN:
        return "boolean"
    if var_type == VARIABLE_TYPE_BOOLEAN_COLUMN:
        return "boolean_column"
    return var_type


def normalize_variable_entry(name: str, entry: Any) -> PoolValue:
    if isinstance(entry, PoolValue):
        return entry
    if isinstance(entry, tuple) and len(entry) == 2:
        value, unit = entry
        var_type = infer_type_from_value(value)
        return PoolValue(name=name, type=var_type, value=value, unit=unit or "1", shape=infer_shape(value))
    if isinstance(entry, dict):
        value = entry.get("value", entry.get("values"))
        var_type = entry.get("type") or infer_type_from_value(value)
        unit = entry.get("unit", "1") or "1"
        shape = tuple(entry["dimensions"]) if entry.get("dimensions") else infer_shape(value)
        return PoolValue(name=name, type=var_type, value=value, unit=unit, shape=shape)
    raise TypeError(f"Unsupported variable entry for '{name}': {type(entry)}")


def normalize_variables(variables: dict | None) -> dict[str, PoolValue]:
    return {
        name: normalize_variable_entry(name, entry)
        for name, entry in (variables or {}).items()
    }


def normalize_extra_constants(extra_constants: dict | None) -> dict[str, PoolValue]:
    normalized = {}
    for name, entry in (extra_constants or {}).items():
        if isinstance(entry, dict):
            normalized[name] = PoolValue(
                name=name,
                type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
                value=entry.get("value"),
                unit=entry.get("unit", "1") or "1",
            )
        else:
            normalized[name] = normalize_variable_entry(name, entry)
    return normalized


def normalize_builtin_constants() -> dict[str, PoolValue]:
    return {
        name: PoolValue(
            name=name,
            type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
            value=float(value.evalf()) if hasattr(value, "evalf") else float(value),
            unit=unit,
        )
        for name, (value, unit) in CONSTANTS.items()
    }


def normalize_operations(operations: dict | None) -> dict[str, OperationSpec]:
    merged = dict(DEFAULT_OPERATIONS)
    for name, spec in (operations or {}).items():
        if isinstance(spec, OperationSpec):
            merged[name] = spec
            continue
        merged[name] = OperationSpec(
            name=name,
            fn=spec["fn"],
            arity=spec["arity"],
            input_types=spec.get("input_types"),
            output_type=spec.get("output_type", VARIABLE_TYPE_CONSTANT_NO_ERROR),
            preserves_units=spec.get("preserves_units", True),
        )
    return merged
