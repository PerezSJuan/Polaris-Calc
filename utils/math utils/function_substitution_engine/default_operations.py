from dataclasses import dataclass
from typing import Any, Callable

from .variable_types_compat import (
    VARIABLE_TYPE_CONSTANT_NO_ERROR,
    VARIABLE_TYPE_MATRIX,
)


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
