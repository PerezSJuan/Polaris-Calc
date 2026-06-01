import sys
import os
import pytest
import sympy as sp

# Add the directory containing the utils to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
utils_path = os.path.join(project_root, "utils", "math utils")

if utils_path not in sys.path:
    sys.path.append(utils_path)

from function_substitution_engine import (
    evaluate, 
    parse_latex_to_ast,
    parse_expression, 
    check_dimensions,
    CONSTANTS,
    validate,
    DimensionMismatchError,
    ShapeMismatchError,
    TypeMismatchError,
    UnknownOperationError,
    NonIntegerExponentError,
)

def test_parse_expression():
    expr = parse_expression("x + y", mode="sympy")
    assert isinstance(expr, sp.Add)
    
    expr = parse_expression("x^2", mode="latex")
    assert isinstance(expr, sp.Pow)


def test_parse_latex_to_ast_custom_function():
    ast = parse_latex_to_ast(r"\sum(x)", operation_names=[r"\sum"])
    assert str(ast) == r"\sum(x)"


def test_parse_latex_to_ast_supports_bar_and_transpose_notation():
    ast = parse_latex_to_ast(r"|x| + B^t")
    assert "bar(" in str(ast)
    assert "transpose(" in str(ast)


def test_evaluate_basic():
    variables = {"x": (10, "m"), "y": (5, "m")}
    val, unit = evaluate("x + y", variables)
    assert val == 15.0
    assert unit == "m"

def test_evaluate_with_constants():
    variables = {}
    val, unit = evaluate("pi", variables)
    assert val == pytest.approx(3.14159, rel=1e-5)
    assert unit == "1"

def test_evaluate_conversion():
    variables = {"L": (1, "km")}
    # Convert 1km to m
    val, unit = evaluate("L", variables, target_unit="m")
    assert val == 1000.0
    assert unit == "m"

def test_dimensional_check_error():
    variables = {"x": (10, "m"), "t": (5, "s")}
    # Cannot add meters and seconds
    expr = parse_expression("x + t", mode="sympy")
    with pytest.raises(ValueError, match="incompatible dimensions"):
        check_dimensions(expr, variables)

def test_evaluate_complex_expression():
    # v = d/t
    variables = {"d": (100, "m"), "t": (10, "s")}
    val, unit = evaluate("d / t", variables)
    assert val == 10.0
    assert "m" in unit and "s" in unit # Simplified to m/s or similar

def test_builtin_constants():
    assert "c" in CONSTANTS
    assert CONSTANTS["c"][1] == "m/s"


def test_evaluate_returns_eval_result_and_preserves_unpacking():
    result = evaluate("x + y", {"x": (2, "m"), "y": (3, "m")})
    val, unit = result
    assert result.type == "constant_no_error"
    assert val == 5.0
    assert unit == "m"


def test_evaluate_column_broadcast_with_extra_constants():
    result = evaluate(
        "x + k",
        {
            "x": {
                "type": "column_no_error",
                "value": [1.0, 2.0, 3.0],
                "unit": "m",
            }
        },
        extra_constants={"k": {"value": 2.0, "unit": "m"}},
    )
    assert result.value == [3.0, 4.0, 5.0]
    assert result.type == "column_no_error"
    assert result.unit == "m"


def test_evaluate_custom_latex_operation_sum():
    result = evaluate(
        r"\sum(x)",
        {
            "x": {
                "type": "column_no_error",
                "value": [1.0, 2.0, 3.0],
                "unit": "m",
            }
        },
        mode="latex",
    )
    assert result.value == 6.0
    assert result.unit == "m"


def test_validate_reports_warnings_without_evaluating():
    report = validate(
        "x + y",
        {"x": (1.0, "m"), "y": (1.0, "km")},
    )
    assert report.valid is True
    assert any(issue.code == "UNIT_CONVERSION_NEEDED" for issue in report.warnings)


def test_validate_accumulates_multiple_errors():
    report = validate("a + b", {})
    assert report.valid is False
    assert [issue.code for issue in report.errors].count("UNDEFINED_SYMBOL") == 2


def test_evaluate_dimension_mismatch_raises():
    with pytest.raises(DimensionMismatchError):
        evaluate("x + t", {"x": (1.0, "m"), "t": (1.0, "s")})


def test_evaluate_boolean_in_arithmetic_raises():
    with pytest.raises(TypeMismatchError):
        evaluate("flag + x", {"flag": {"type": "boolean", "value": True, "unit": "1"}, "x": (1.0, "m")})


def test_evaluate_column_partial_result_with_index_errors():
    result = evaluate(
        "x + y",
        {
            "x": {"type": "column_no_error", "value": [1.0, 2.0, 3.0], "unit": "m"},
            "y": {"type": "column_no_error", "value": [10.0], "unit": "m"},
        },
    )
    assert result.value == [11.0, None, None]
    assert len(result.index_errors) == 2
    assert any(warning.code == "COLUMN_LENGTH_UNKNOWN" for warning in result.warnings)


def test_evaluate_column_division_by_scalar():
    result = evaluate(
        "x / k",
        {
            "x": {"type": "column_no_error", "value": [2.0, 4.0, 6.0], "unit": "m"},
        },
        extra_constants={"k": {"value": 2.0, "unit": "1"}},
    )
    assert result.value == [1.0, 2.0, 3.0]
    assert result.unit == "m"


def test_evaluate_comparison_returns_boolean_column():
    result = evaluate(
        "x > t",
        {
            "x": {"type": "column_no_error", "value": [1.0, 3.0, 5.0], "unit": "m"},
            "t": {"type": "constant_no_error", "value": 2.0, "unit": "m"},
        },
    )
    assert result.type == "boolean_column"
    assert result.value == [False, True, True]
    assert result.unit == "bool"


def test_evaluate_matrix_addition():
    result = evaluate(
        "A + B",
        {
            "A": {"type": "matrix", "value": [[1.0, 2.0], [3.0, 4.0]], "unit": "m"},
            "B": {"type": "matrix", "value": [[10.0, 20.0], [30.0, 40.0]], "unit": "m"},
        },
    )
    assert result.type == "matrix"
    assert result.value == [[11.0, 22.0], [33.0, 44.0]]


def test_evaluate_matrix_addition_shape_mismatch():
    with pytest.raises(ShapeMismatchError):
        evaluate(
            "A + B",
            {
                "A": {"type": "matrix", "value": [[1.0, 2.0]], "unit": "m"},
                "B": {"type": "matrix", "value": [[1.0, 2.0], [3.0, 4.0]], "unit": "m"},
            },
        )


def test_evaluate_custom_matmul():
    result = evaluate(
        r"\matmul(A,B)",
        {
            "A": {"type": "matrix", "value": [[1.0, 2.0], [3.0, 4.0]], "unit": "m"},
            "B": {"type": "matrix", "value": [[5.0, 6.0], [7.0, 8.0]], "unit": "s"},
        },
        mode="latex",
    )
    assert result.type == "matrix"
    assert result.value == [[19.0, 22.0], [43.0, 50.0]]
    assert result.unit == "m*s"


def test_evaluate_matrix_power_requires_integer_exponent():
    with pytest.raises(NonIntegerExponentError):
        evaluate(
            "A ^ p",
            {
                "A": {"type": "matrix", "value": [[1.0, 0.0], [0.0, 1.0]], "unit": "1"},
                "p": {"type": "constant_no_error", "value": 0.5, "unit": "1"},
            },
        )


def test_evaluate_matrix_determinant():
    result = evaluate(
        "det(A)",
        {
            "A": {"type": "matrix", "value": [[1.0, 2.0], [3.0, 4.0]], "unit": "m"},
        },
        target_unit="m^2",
    )
    assert result.type == "complex"
    assert result.value == pytest.approx(-2.0)
    assert result.unit == "m^2"


def test_evaluate_bar_notation_uses_determinant_for_matrix():
    result = evaluate(
        r"|A|",
        {
            "A": {"type": "matrix", "value": [[1.0, 2.0], [3.0, 4.0]], "unit": "m"},
        },
        mode="latex",
    )
    assert result.type == "complex"
    assert result.value == pytest.approx(-2.0)


def test_evaluate_bar_notation_uses_absolute_value_for_scalars():
    result = evaluate(
        r"|-3|",
        {},
        mode="latex",
    )
    assert result.value == 3.0
    assert result.unit == "1"


def test_evaluate_transpose_notation():
    result = evaluate(
        r"B^t",
        {
            "B": {"type": "matrix", "value": [[1.0, 2.0], [3.0, 4.0]], "unit": "m"},
        },
        mode="latex",
    )
    assert result.type == "matrix"
    assert result.value == [[1.0, 3.0], [2.0, 4.0]]


def test_validate_reports_matrix_shape_mismatch_for_determinant():
    report = validate(
        r"|A|",
        {
            "A": {"type": "matrix", "value": [[1.0, 2.0, 3.0]], "unit": "m"},
        },
        mode="latex",
    )
    assert report.valid is False
    assert any(issue.code == "SHAPE_MISMATCH" for issue in report.errors)


def test_validate_reports_dimension_mismatch_for_dimensionless_function():
    report = validate(
        "imexp(x)",
        {
            "x": (1.0, "m"),
        },
    )
    assert report.valid is False
    assert any(issue.code == "DIMENSION_MISMATCH" for issue in report.errors)


def test_validate_reports_transpose_requires_matrix():
    report = validate(
        r"x^t",
        {
            "x": (1.0, "m"),
        },
        mode="latex",
    )
    assert report.valid is False
    assert any(issue.code == "TYPE_MISMATCH" for issue in report.errors)


def test_evaluate_unknown_operation_raises():
    with pytest.raises(UnknownOperationError):
        evaluate(r"\mystery(x)", {"x": (1.0, "m")}, mode="latex")


def test_validate_reports_target_unit_mismatch():
    report = validate("x + y", {"x": (1.0, "m"), "y": (2.0, "m")}, target_unit="s")
    assert report.valid is False
    assert any(issue.code == "TARGET_UNIT_DIMENSION_MISMATCH" for issue in report.errors)


def test_validate_reports_type_mismatch_for_boolean_arithmetic():
    report = validate(
        "flag + x",
        {"flag": {"type": "boolean", "value": True, "unit": "1"}, "x": (1.0, "m")},
    )
    assert report.valid is False
    assert any(issue.code == "TYPE_MISMATCH" for issue in report.errors)


def test_validate_reports_unknown_operation():
    report = validate(r"\mystery(x)", {"x": (1.0, "m")}, mode="latex")
    assert report.valid is False
    assert any(issue.code == "UNKNOWN_OPERATION" for issue in report.errors)


def test_validate_reports_arity_mismatch():
    report = validate(
        r"\sum(x,y)",
        {
            "x": {"type": "column_no_error", "value": [1.0], "unit": "m"},
            "y": {"type": "column_no_error", "value": [2.0], "unit": "m"},
        },
        mode="latex",
    )
    assert report.valid is False
    assert any(issue.code == "ARITY_MISMATCH" for issue in report.errors)


def test_validate_reports_implicit_broadcast_warning():
    report = validate(
        "x + y",
        {
            "x": {"type": "column_no_error", "value": [1.0, 2.0], "unit": "m"},
            "y": {"type": "constant_no_error", "value": 2.0, "unit": "m"},
        },
    )
    assert any(issue.code == "IMPLICIT_BROADCAST" for issue in report.warnings)


def test_validate_reports_column_length_unknown_warning_on_registered_function():
    report = validate(
        r"\mean(x)",
        {
            "x": {"type": "column_no_error", "value": [1.0, 2.0], "unit": "m"},
        },
        mode="latex",
    )
    assert report.valid is True
    assert any(issue.code == "COLUMN_LENGTH_UNKNOWN" for issue in report.warnings)
