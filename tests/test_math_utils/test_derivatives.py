import sys
import os
import pytest

# Add the directory containing the utils to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
utils_path = os.path.join(project_root, "utils", "math_utils")

if utils_path not in sys.path:
    sys.path.append(utils_path)

from derivatives import compute_derivative

def test_compute_derivative_basic():
    # Simple derivative: x^2 -> 2x
    assert compute_derivative("x^2", "x") == "2 x"

def test_compute_derivative_with_respect_to_y():
    # Derivative of y^3 with respect to y: y^3 -> 3y^2
    assert compute_derivative("y^3", "y") == "3 y^{2}"

def test_compute_derivative_constant():
    # Derivative of constant: 5 -> 0
    assert compute_derivative("5", "x") == "0"

def test_compute_derivative_multiple_terms():
    # x^2 + 3x + 5 -> 2x + 3
    assert compute_derivative("x^2 + 3*x + 5", "x") == "2 x + 3"

def test_compute_derivative_trig():
    # sin(x) -> cos(x)
    assert compute_derivative("\\sin(x)", "x") == "\\cos{\\left(x \\right)}"

def test_compute_derivative_error():
    # Invalid latex
    result = compute_derivative("invalid(", "x")
    assert "Error computing derivative" in result
