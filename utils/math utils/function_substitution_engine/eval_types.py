from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvalWarning:
    code: str
    message: str
    node_repr: str = ""


@dataclass
class ValidationIssue:
    code: str
    message: str
    node_repr: str
    severity: str


@dataclass
class ValidationReport:
    valid: bool
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)


@dataclass
class EvalResult:
    value: Any
    unit: str
    type: str
    warnings: list[EvalWarning] = field(default_factory=list)
    index_errors: list["IndexOutOfBoundsError"] = field(default_factory=list)

    def __iter__(self):
        yield self.value
        yield self.unit


class EvalError(Exception):
    code = "EVAL_ERROR"

    def __init__(self, message: str, node_repr: str = ""):
        super().__init__(message)
        self.message = message
        self.node_repr = node_repr


class UndefinedSymbolError(EvalError):
    code = "UNDEFINED_SYMBOL"


class UnknownOperationError(EvalError):
    code = "UNKNOWN_OPERATION"


class TypeMismatchError(EvalError):
    code = "TYPE_MISMATCH"


class DimensionMismatchError(EvalError):
    code = "DIMENSION_MISMATCH"


class ShapeMismatchError(EvalError):
    code = "SHAPE_MISMATCH"


class NonIntegerExponentError(EvalError):
    code = "NON_INTEGER_EXPONENT"


class UnitConversionError(EvalError):
    code = "UNIT_CONVERSION_ERROR"


class ArityMismatchError(EvalError):
    code = "ARITY_MISMATCH"


@dataclass
class IndexOutOfBoundsError(EvalError):
    index: int = -1
    column_name: str = ""
    message: str = "Index out of bounds"
    node_repr: str = ""

    code = "INDEX_OUT_OF_BOUNDS"

    def __post_init__(self):
        super().__init__(self.message, self.node_repr)


class UnitConversionWarning(EvalWarning):
    def __init__(self, message: str, node_repr: str = ""):
        super().__init__("UNIT_CONVERSION_NEEDED", message, node_repr)


class SemanticUnitWarning(EvalWarning):
    def __init__(self, message: str, node_repr: str = ""):
        super().__init__("SEMANTIC_UNIT_MISMATCH", message, node_repr)


class ColumnLengthWarning(EvalWarning):
    def __init__(self, message: str, node_repr: str = ""):
        super().__init__("COLUMN_LENGTH_UNKNOWN", message, node_repr)
