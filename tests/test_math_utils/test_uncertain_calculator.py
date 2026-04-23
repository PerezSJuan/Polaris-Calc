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

from uncertain_calculator import (
    evaluate, 
    compute_covariance, 
    compute_formula_error_few, 
    compute_formula_error_many,
    compute_formula_error_from_series
)

def test_evaluate_basic():
    variables = {"x": (10, "m"), "y": (5, "m")}
    val, unit = evaluate("x + y", variables)
    assert val == 15.0
    assert unit == "m"

def test_evaluate_units():
    variables = {"v": (10, "m/s"), "t": (2, "s")}
    val, unit = evaluate("v * t", variables)
    assert val == 20.0
    assert "m" in unit # might be m/s * s or simplified

def test_compute_covariance():
    series_i = [1, 2, 3, 4, 5]
    series_j = [2, 4, 6, 8, 10]
    cov, unit = compute_covariance(series_i, series_j, "m", "s")
    # Mean i = 3, Mean j = 6
    # (1-3)(2-6) + (2-3)(4-6) + (3-3)(6-6) + (4-3)(8-6) + (5-3)(10-6)
    # (-2)(-4) + (-1)(-2) + 0 + (1)(2) + (2)(4) = 8 + 2 + 0 + 2 + 8 = 20
    # 20 / (5-1) = 5
    assert cov == 5.0
    assert unit == "m*s"

def test_compute_formula_error_few():
    # f = x^2, sigma_x = 0.1, x = 10
    # df/dx = 2x = 20
    # sigma_f = sqrt((20*0.1)^2) = 2
    formula = "x^2"
    variables = ["x"]
    var_data = {"x": (10, "m")}
    sigma_data = {"x": (0.1, "m")}
    result = compute_formula_error_few(formula, variables, var_data, sigma_data)
    assert result["sigma_f_value"] == pytest.approx(2.0)
    assert "m^2" in result["sigma_f_unit"]

def test_compute_formula_error_many_no_cov():
    # Test many mode but with zero covariance
    formula = "x + y"
    variables = ["x", "y"]
    var_data = {"x": (10, "m"), "y": (20, "m")}
    sigma_data = {"x": (0.3, "m"), "y": (0.4, "m")}
    # sigma_f = sqrt(0.3^2 + 0.4^2) = 0.5
    covariances = {("x", "y"): (0, "m*m")}
    result = compute_formula_error_many(formula, variables, var_data, sigma_data, covariances)
    assert result["sigma_f_value"] == pytest.approx(0.5)

def test_error_from_series_dispatch():
    # n=3 <= THRESHOLD (4) -> few mode
    series = {"x": [9, 10, 11]}
    units = {"x": "m"}
    sigma_data = {"x": (0.1, "m")}
    result = compute_formula_error_from_series("x^2", ["x"], series, sigma_data, units)
    assert result["mode"] == "few"
    assert result["n"] == 3
    assert result["means"]["x"] == 10.0

    # n=5 > THRESHOLD -> many mode
    series = {"x": [8, 9, 10, 11, 12]}
    result = compute_formula_error_from_series("x^2", ["x"], series, sigma_data, units)
    assert result["mode"] == "many"
    assert result["n"] == 5
