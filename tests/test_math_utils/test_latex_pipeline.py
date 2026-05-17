import os
import sys

import sympy as sp


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
utils_path = os.path.join(project_root, "utils", "math utils")

if utils_path not in sys.path:
    sys.path.append(utils_path)

from derivatives import compute_derivative
from sympy_latex_parser import parse_latex


def test_parse_latex_returns_expected_sympy_expression():
    expr = parse_latex(r"\frac{1}{x} + x^2")
    x = sp.Symbol("x")
    assert sp.simplify(expr - (1 / x + x**2)) == 0


def test_parse_latex_supports_grouped_algebraic_expression():
    expr = parse_latex(r"(x+1)^2")
    x = sp.Symbol("x")
    assert sp.simplify(expr - (x + 1) ** 2) == 0


def test_compute_derivative_handles_fraction_expression():
    assert compute_derivative(r"\frac{1}{x}", "x") == "- \\frac{1}{x^{2}}"
