from __future__ import annotations

import os
import sys
from typing import Any

current_dir = os.path.dirname(os.path.abspath(__file__))
math_utils_dir = os.path.dirname(current_dir)
unit_conv_path = os.path.join(math_utils_dir, "unit conversor")
if unit_conv_path not in sys.path:
    sys.path.append(unit_conv_path)

from unit_conversor import convert, get_unit_type, parse_compound_expression

from .eval_types import DimensionMismatchError, SemanticUnitWarning, UnitConversionError, UnitConversionWarning


SI_BASES = ("m", "kg", "s", "A", "K", "mol", "cd")


def get_dim(unit: str) -> tuple:
    if unit in ("", None, "1", "bool"):
        return (0, 0, 0, 0, 0, 0, 0)
    dims, _ = parse_compound_expression(unit)
    return tuple(dims)


def same_dim(u1: str, u2: str) -> bool:
    return get_dim(u1) == get_dim(u2)


def combine_units(u1: str, u2: str, op: str) -> str:
    if u1 in ("", None):
        u1 = "1"
    if u2 in ("", None):
        u2 = "1"
    if u2 == "1":
        return u1
    if u1 == "1":
        return u2 if op == "*" else f"1/{u2}"
    return f"{u1}{op}{u2}"


def _convert_value(value: Any, from_unit: str, to_unit: str):
    if from_unit == to_unit or from_unit in ("1", "bool"):
        return value
    if isinstance(value, list):
        return [_convert_value(item, from_unit, to_unit) for item in value]
    if value is None:
        return None
    return convert(value, from_unit, to_unit)


def semantic_warning(u1: str, u2: str, node_repr: str = ""):
    type1 = get_unit_type(u1)
    type2 = get_unit_type(u2)
    if type1 == type2 == "Currency" and u1 != u2:
        return SemanticUnitWarning(f"Implicit conversion between semantic units '{u1}' and '{u2}'", node_repr)
    return None


def harmonize_additive_units(results, node_repr: str = ""):
    if not results:
        return results, []
    base_unit = results[0].unit
    warnings = []
    normalized = [results[0]]
    for result in results[1:]:
        if not same_dim(base_unit, result.unit):
            raise DimensionMismatchError(f"Incompatible dimensions: {base_unit} and {result.unit}", node_repr)
        if result.unit != base_unit:
            normalized_value = _convert_value(result.value, result.unit, base_unit)
            normalized.append(result.__class__(normalized_value, base_unit, result.type, list(result.warnings), list(result.index_errors)))
            warnings.append(UnitConversionWarning(f"Converted '{result.unit}' to '{base_unit}'", node_repr))
            semantic = semantic_warning(base_unit, result.unit, node_repr)
            if semantic:
                warnings.append(semantic)
        else:
            normalized.append(result)
    return normalized, warnings


def convert_result_unit(result, target_unit: str):
    try:
        value = _convert_value(result.value, result.unit, target_unit)
    except Exception as exc:
        raise UnitConversionError(str(exc), target_unit) from exc
    result.value = value
    result.unit = target_unit
    return result


def si_unit_for(unit: str) -> str:
    dims = get_dim(unit)
    if dims == (0, 0, 0, 0, 0, 0, 0):
        return "1"
    num = []
    den = []
    for base, exponent in zip(SI_BASES, dims):
        if exponent > 0:
            num.append(base if exponent == 1 else f"{base}^{exponent}")
        elif exponent < 0:
            pos = abs(exponent)
            den.append(base if pos == 1 else f"{base}^{pos}")
    left = "*".join(num) if num else "1"
    if not den:
        return left
    right = "*".join(den)
    return f"{left}/{right}"
