from __future__ import annotations

from dataclasses import dataclass
from importlib import util
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .eval_types import DimensionMismatchError, ShapeMismatchError
from .units import combine_units, same_dim
from .variable_types_compat import (
    VARIABLE_TYPE_COMPLEX,
    VARIABLE_TYPE_CONSTANT_NO_ERROR,
    VARIABLE_TYPE_MATRIX,
)


@dataclass
class OperationSpec:
    name: str
    fn: Callable[..., Any]
    arity: int | None
    input_types: Any
    output_type: str
    preserves_units: bool = True
    min_arity: int | None = None
    max_arity: int | None = None
    aliases: tuple[str, ...] = ()
    result_type_rule: Callable[[list[Any]], str] | None = None
    validator: Callable[[list[Any]], None] | None = None
    unit_rule: Callable[[list[Any]], str] | None = None


def _load_math_module(module_name: str, filename: str):
    module_path = Path(__file__).resolve().parent.parent / "complex math operations" / filename
    spec = util.spec_from_file_location(f"function_substitution_engine.{module_name}", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load math module '{filename}'")
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GEOMETRY = _load_math_module("complex_geometry", "geometry.py")
ENGINEERING = _load_math_module("complex_engineering", "engineering.py")


def _spec(
    name: str,
    fn: Callable[..., Any],
    *,
    arity: int | None,
    input_types: Any,
    output_type: str,
    preserves_units: bool = True,
    min_arity: int | None = None,
    max_arity: int | None = None,
    aliases: tuple[str, ...] = (),
    result_type_rule: Callable[[list[Any]], str] | None = None,
    validator: Callable[[list[Any]], None] | None = None,
    unit_rule: Callable[[list[Any]], str] | None = None,
) -> OperationSpec:
    return OperationSpec(
        name=name,
        fn=fn,
        arity=arity,
        input_types=input_types,
        output_type=output_type,
        preserves_units=preserves_units,
        min_arity=min_arity,
        max_arity=max_arity,
        aliases=aliases,
        result_type_rule=result_type_rule,
        validator=validator,
        unit_rule=unit_rule,
    )


def _dimensionless_validator(node_name: str):
    def validator(operands):
        for operand in operands:
            if not same_dim(operand.unit, "1"):
                raise DimensionMismatchError(f"Operation '{node_name}' requires dimensionless inputs", node_name)

    return validator


def _square_matrix_validator(node_name: str):
    def validator(operands):
        [matrix] = operands
        shape = matrix.shape
        if shape is None or len(shape) != 2 or shape[0] != shape[1]:
            raise ShapeMismatchError(f"Operation '{node_name}' requires a square matrix", node_name)

    return validator


def _matrix_multiply_validator(node_name: str):
    def validator(operands):
        left, right = operands
        left_shape = left.shape
        right_shape = right.shape
        if left_shape is None or right_shape is None or len(left_shape) != 2 or len(right_shape) != 2:
            return
        if left_shape[1] != right_shape[0]:
            raise ShapeMismatchError(
                f"Matrix shapes are incompatible for '{node_name}'",
                node_name,
            )

    return validator


def _unit_rule_same_unit(operands) -> str:
    return operands[0].unit if operands else "1"


def _unit_rule_dimensionless(operands) -> str:
    return "1"


def _result_type_matrix_or_scalar(operands) -> str:
    if operands and operands[0].canonical == "matrix":
        return VARIABLE_TYPE_COMPLEX
    return VARIABLE_TYPE_CONSTANT_NO_ERROR


def _unit_rule_determinant(operands) -> str:
    matrix = operands[0]
    unit = matrix.unit
    if unit in {"", None, "1", "bool"}:
        return "1"
    size = matrix.shape[0] if matrix.shape and len(matrix.shape) == 2 else 1
    current = "1"
    for _ in range(size):
        current = combine_units(current, unit, "*")
    return current


def _unit_rule_inverse(operands) -> str:
    unit = operands[0].unit
    if unit in {"", None, "1", "bool"}:
        return "1"
    return f"1/({unit})"


def _unit_rule_matrix_product(operands) -> str:
    return combine_units(operands[0].unit, operands[1].unit, "*")


def _unit_rule_matrix_division(operands) -> str:
    return combine_units(operands[0].unit, operands[1].unit, "/")


def _unit_rule_product(operands) -> str:
    current = operands[0].unit if operands else "1"
    for operand in operands[1:]:
        current = combine_units(current, operand.unit, "*")
    return current


def _transpose(matrix):
    if not matrix:
        return []
    return [list(row) for row in zip(*matrix)]


def _norm(value):
    if isinstance(value, list):
        array = np.asarray(value)
        if array.dtype == object:
            array = np.asarray(value, dtype=float)
        return float(np.linalg.norm(array))
    return abs(value)


def _bar_dispatch(value):
    if isinstance(value, list):
        if value and isinstance(value[0], list):
            return GEOMETRY.mdeterm(value)
        return _norm(value)
    return GEOMETRY.absolute(value)


DEFAULT_OPERATIONS = {
    "sum": _spec(
        "sum",
        GEOMETRY.sum_values,
        arity=1,
        input_types={"column", "vector"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        aliases=(r"\sum",),
        preserves_units=True,
    ),
    "mean": _spec(
        "mean",
        GEOMETRY.mean,
        arity=1,
        input_types={"column", "vector"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        aliases=(r"\mean",),
        preserves_units=True,
    ),
    "abs": _spec(
        "abs",
        GEOMETRY.absolute,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        aliases=("absolute",),
        preserves_units=True,
    ),
    "bar": _spec(
        "bar",
        _bar_dispatch,
        arity=1,
        input_types={"scalar", "complex", "column", "vector", "matrix"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        aliases=("|",),
        preserves_units=False,
        result_type_rule=_result_type_matrix_or_scalar,
        validator=lambda operands: _square_matrix_validator("bar")(operands)
        if operands and operands[0].canonical == "matrix"
        else None,
        unit_rule=lambda operands: _unit_rule_determinant(operands)
        if operands and operands[0].canonical == "matrix"
        else _unit_rule_same_unit(operands),
    ),
    "sign": _spec(
        "sign",
        GEOMETRY.sign,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        preserves_units=False,
        unit_rule=_unit_rule_dimensionless,
    ),
    "factorial": _spec(
        "factorial",
        GEOMETRY.factorial,
        arity=1,
        input_types={"scalar"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        preserves_units=False,
        validator=_dimensionless_validator("factorial"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "double_factorial": _spec(
        "double_factorial",
        GEOMETRY.double_factorial,
        arity=1,
        input_types={"scalar"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        preserves_units=False,
        validator=_dimensionless_validator("double_factorial"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "comb": _spec(
        "comb",
        GEOMETRY.combin,
        arity=2,
        input_types={"scalar"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        preserves_units=False,
        validator=_dimensionless_validator("comb"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "combina": _spec(
        "combina",
        GEOMETRY.combina,
        arity=2,
        input_types={"scalar"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        preserves_units=False,
        validator=_dimensionless_validator("combina"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "multinomial": _spec(
        "multinomial",
        GEOMETRY.multinomial,
        arity=None,
        min_arity=1,
        input_types={"scalar"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        preserves_units=False,
        validator=_dimensionless_validator("multinomial"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "gcd": _spec(
        "gcd",
        GEOMETRY.gcd,
        arity=None,
        min_arity=2,
        input_types={"scalar"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        preserves_units=False,
        validator=_dimensionless_validator("gcd"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "lcm": _spec(
        "lcm",
        GEOMETRY.lcm,
        arity=None,
        min_arity=2,
        input_types={"scalar"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        preserves_units=False,
        validator=_dimensionless_validator("lcm"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "complex_number": _spec(
        "complex_number",
        ENGINEERING.complex_number,
        arity=2,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=True,
    ),
    "imabs": _spec(
        "imabs",
        ENGINEERING.imabs,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        preserves_units=True,
    ),
    "imreal": _spec(
        "imreal",
        ENGINEERING.imreal,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        preserves_units=True,
    ),
    "imaginary": _spec(
        "imaginary",
        ENGINEERING.imaginary,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        preserves_units=True,
    ),
    "imargument": _spec(
        "imargument",
        ENGINEERING.imargument,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        preserves_units=False,
        validator=_dimensionless_validator("imargument"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "imconjugate": _spec(
        "imconjugate",
        ENGINEERING.imconjugate,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=True,
    ),
    "imsum": _spec(
        "imsum",
        ENGINEERING.imsum,
        arity=None,
        min_arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=True,
    ),
    "imsub": _spec(
        "imsub",
        ENGINEERING.imsub,
        arity=2,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=True,
    ),
    "improduct": _spec(
        "improduct",
        ENGINEERING.improduct,
        arity=None,
        min_arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        unit_rule=_unit_rule_product,
    ),
    "imdiv": _spec(
        "imdiv",
        ENGINEERING.imdiv,
        arity=2,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        unit_rule=_unit_rule_matrix_division,
    ),
    "imsqrt": _spec(
        "imsqrt",
        ENGINEERING.imsqrt,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        validator=_dimensionless_validator("imsqrt"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "imexp": _spec(
        "imexp",
        ENGINEERING.imexp,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        validator=_dimensionless_validator("imexp"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "imln": _spec(
        "imln",
        ENGINEERING.imln,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        validator=_dimensionless_validator("imln"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "imlog10": _spec(
        "imlog10",
        ENGINEERING.imlog10,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        validator=_dimensionless_validator("imlog10"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "imlog2": _spec(
        "imlog2",
        ENGINEERING.imlog2,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        validator=_dimensionless_validator("imlog2"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "imsin": _spec(
        "imsin",
        ENGINEERING.imsin,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        validator=_dimensionless_validator("imsin"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "imcos": _spec(
        "imcos",
        ENGINEERING.imcos,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        validator=_dimensionless_validator("imcos"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "imtan": _spec(
        "imtan",
        ENGINEERING.imtan,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        validator=_dimensionless_validator("imtan"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "imcot": _spec(
        "imcot",
        ENGINEERING.imcot,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        validator=_dimensionless_validator("imcot"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "imsec": _spec(
        "imsec",
        ENGINEERING.imsec,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        validator=_dimensionless_validator("imsec"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "imcsc": _spec(
        "imcsc",
        ENGINEERING.imcsc,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        validator=_dimensionless_validator("imcsc"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "imsinh": _spec(
        "imsinh",
        ENGINEERING.imsinh,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        validator=_dimensionless_validator("imsinh"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "imcosh": _spec(
        "imcosh",
        ENGINEERING.imcosh,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        validator=_dimensionless_validator("imcosh"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "imsech": _spec(
        "imsech",
        ENGINEERING.imsech,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        validator=_dimensionless_validator("imsech"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "imcsch": _spec(
        "imcsch",
        ENGINEERING.imcsch,
        arity=1,
        input_types={"scalar", "complex"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        validator=_dimensionless_validator("imcsch"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "det": _spec(
        "det",
        GEOMETRY.mdeterm,
        arity=1,
        input_types={"matrix"},
        output_type=VARIABLE_TYPE_COMPLEX,
        preserves_units=False,
        aliases=("mdeterm",),
        validator=_square_matrix_validator("det"),
        unit_rule=_unit_rule_determinant,
    ),
    "inverse": _spec(
        "inverse",
        GEOMETRY.minverse,
        arity=1,
        input_types={"matrix"},
        output_type=VARIABLE_TYPE_MATRIX,
        preserves_units=False,
        aliases=("minverse",),
        validator=_square_matrix_validator("inverse"),
        unit_rule=_unit_rule_inverse,
    ),
    "matmul": _spec(
        "matmul",
        GEOMETRY.mmult,
        arity=2,
        input_types=[{"matrix"}, {"matrix"}],
        output_type=VARIABLE_TYPE_MATRIX,
        preserves_units=False,
        aliases=("mmult",),
        validator=_matrix_multiply_validator("matmul"),
        unit_rule=_unit_rule_matrix_product,
    ),
    "transpose": _spec(
        "transpose",
        _transpose,
        arity=1,
        input_types={"matrix"},
        output_type=VARIABLE_TYPE_MATRIX,
        preserves_units=False,
        result_type_rule=lambda operands: VARIABLE_TYPE_MATRIX,
        unit_rule=_unit_rule_same_unit,
    ),
    "identity": _spec(
        "identity",
        GEOMETRY.munit,
        arity=1,
        input_types={"scalar"},
        output_type=VARIABLE_TYPE_MATRIX,
        preserves_units=False,
        aliases=("munit",),
        validator=_dimensionless_validator("identity"),
        unit_rule=_unit_rule_dimensionless,
    ),
    "norm": _spec(
        "norm",
        _norm,
        arity=1,
        input_types={"scalar", "complex", "column", "vector", "matrix"},
        output_type=VARIABLE_TYPE_CONSTANT_NO_ERROR,
        preserves_units=False,
        unit_rule=_unit_rule_same_unit,
    ),
}
