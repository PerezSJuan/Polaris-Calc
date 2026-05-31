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
from .default_constants import CONSTANTS
from .default_operations import DEFAULT_OPERATIONS, OperationSpec

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
    merged: dict[str, OperationSpec] = {}

    def register(name: str, spec: OperationSpec):
        merged[name] = spec
        for alias in spec.aliases:
            merged[alias] = spec
        if name.startswith("\\"):
            merged[name[1:]] = spec
        elif name:
            merged[f"\\{name}"] = spec

    for name, spec in DEFAULT_OPERATIONS.items():
        register(name, spec)
    for name, spec in (operations or {}).items():
        if isinstance(spec, OperationSpec):
            register(name, spec)
            continue
        normalized = OperationSpec(
            name=name,
            fn=spec["fn"],
            arity=spec.get("arity"),
            input_types=spec.get("input_types"),
            output_type=spec.get("output_type", VARIABLE_TYPE_CONSTANT_NO_ERROR),
            preserves_units=spec.get("preserves_units", True),
            min_arity=spec.get("min_arity"),
            max_arity=spec.get("max_arity"),
            aliases=tuple(spec.get("aliases", ())),
            validator=spec.get("validator"),
            unit_rule=spec.get("unit_rule"),
        )
        register(name, normalized)
    return merged
