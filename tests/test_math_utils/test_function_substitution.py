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

from function_substitution import (
    evaluate, 
    parse_expression, 
    check_dimensions,
    CONSTANTS
)

def test_parse_expression():
    expr = parse_expression("x + y", mode="sympy")
    assert isinstance(expr, sp.Add)
    
    expr = parse_expression("x^2", mode="latex")
    assert isinstance(expr, sp.Pow)

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
