from __future__ import annotations

from typing import Any

from .eval_types import UndefinedSymbolError
from .pool_schema import PoolValue, canonical_type, infer_shape


def resolve_pool_variable(
    name: str,
    pool: dict,
    row_index: int | None = None,
) -> PoolValue:
    entry = pool.get(name)
    if entry is None:
        raise UndefinedSymbolError(f"Variable '{name}' no existe en el pool", name)

    var_type = entry.get("type", "column_no_error")
    values = entry.get("values", [])
    unit = entry.get("unit", "1") or "1"

    if row_index is not None and isinstance(values, list):
        if len(values) == 1:
            value = values[0]
        elif row_index < len(values):
            value = values[row_index]
        else:
            value = None
    else:
        value = values

    shape = entry.get("dimensions")
    if shape is None:
        shape = infer_shape(value)

    return PoolValue(name=name, type=var_type, value=value, unit=unit, shape=shape)
