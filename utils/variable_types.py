VARIABLE_TYPE_CONSTANT_NO_ERROR = "constant_no_error"
VARIABLE_TYPE_CONSTANT_WITH_ERROR = "constant_with_error"
VARIABLE_TYPE_COLUMN_NO_ERROR = "column_no_error"
VARIABLE_TYPE_COLUMN_WITH_SINGLE_ERROR = "column_with_single_error"
VARIABLE_TYPE_COLUMN_WITH_ERROR_PER_VALUE = "column_with_error_per_value"
VARIABLE_TYPE_FORMULA_NO_ERROR = "formula_no_error"
VARIABLE_TYPE_FORMULA_WITH_ERROR = "formula_with_error"

ALL_VARIABLE_TYPES = [
    VARIABLE_TYPE_CONSTANT_NO_ERROR,
    VARIABLE_TYPE_CONSTANT_WITH_ERROR,
    VARIABLE_TYPE_COLUMN_NO_ERROR,
    VARIABLE_TYPE_COLUMN_WITH_SINGLE_ERROR,
    VARIABLE_TYPE_COLUMN_WITH_ERROR_PER_VALUE,
    VARIABLE_TYPE_FORMULA_NO_ERROR,
    VARIABLE_TYPE_FORMULA_WITH_ERROR,
]

VARIABLE_TYPE_LABELS = {
    VARIABLE_TYPE_CONSTANT_NO_ERROR: "Constante sin error",
    VARIABLE_TYPE_CONSTANT_WITH_ERROR: "Constante con error",
    VARIABLE_TYPE_COLUMN_NO_ERROR: "Columna sin error",
    VARIABLE_TYPE_COLUMN_WITH_SINGLE_ERROR: "Columna con error único",
    VARIABLE_TYPE_COLUMN_WITH_ERROR_PER_VALUE: "Columna con error por valor",
    VARIABLE_TYPE_FORMULA_NO_ERROR: "Fórmula sin error",
    VARIABLE_TYPE_FORMULA_WITH_ERROR: "Fórmula con error",
}

FORMULA_VARIABLE_TYPES = {
    VARIABLE_TYPE_FORMULA_NO_ERROR,
    VARIABLE_TYPE_FORMULA_WITH_ERROR,
}

CONSTANT_VARIABLE_TYPES = {
    VARIABLE_TYPE_CONSTANT_NO_ERROR,
    VARIABLE_TYPE_CONSTANT_WITH_ERROR,
}

VARIABLE_TYPES_WITH_SINGLE_ERROR = {
    VARIABLE_TYPE_CONSTANT_WITH_ERROR,
    VARIABLE_TYPE_COLUMN_WITH_SINGLE_ERROR,
}


def infer_variable_type(entry: dict) -> str:
    declared = entry.get("type")
    if declared in ALL_VARIABLE_TYPES:
        return declared

    formula = entry.get("formula", "")
    if isinstance(formula, str) and formula.strip():
        return VARIABLE_TYPE_FORMULA_NO_ERROR

    return VARIABLE_TYPE_COLUMN_NO_ERROR


def is_formula_type(var_type: str) -> bool:
    return var_type in FORMULA_VARIABLE_TYPES


def is_constant_type(var_type: str) -> bool:
    return var_type in CONSTANT_VARIABLE_TYPES


def has_single_error(var_type: str) -> bool:
    return var_type in VARIABLE_TYPES_WITH_SINGLE_ERROR


def has_error_per_value(var_type: str) -> bool:
    return var_type == VARIABLE_TYPE_COLUMN_WITH_ERROR_PER_VALUE
