import sys
import os
import math
import numpy as np
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
ops_path = os.path.join(project_root, "utils", "math_utils", "complex_math_operations")

if ops_path not in sys.path:
    sys.path.insert(0, ops_path)

from fitting import (
    linest_slope, linest_intercept, linest_r2,
    polyfit_coeffs, polyfit_r2, polyval,
    fit_exponential_coeffs, fit_exponential_r2,
    fit_power_coeffs, fit_power_r2,
    fit_logarithmic_coeffs, fit_logarithmic_r2,
    r_squared, rmse, mae,
)


class TestLinearRegression:
    def test_linest_slope_perfect(self):
        x = [0, 1, 2, 3, 4]
        y = [0, 2, 4, 6, 8]
        assert linest_slope(x, y) == pytest.approx(2.0)

    def test_linest_slope_negative(self):
        x = [0, 1, 2]
        y = [10, 5, 0]
        assert linest_slope(x, y) == pytest.approx(-5.0)

    def test_linest_intercept(self):
        x = [0, 1, 2]
        y = [5, 7, 9]
        assert linest_intercept(x, y) == pytest.approx(5.0)

    def test_linest_r2_perfect(self):
        x = [0, 1, 2, 3, 4]
        y = [0, 2, 4, 6, 8]
        assert linest_r2(x, y) == pytest.approx(1.0)

    def test_linest_single_point_raises(self):
        with pytest.raises(ValueError, match="at least 2"):
            linest_slope([1], [2])


class TestPolynomialRegression:
    def test_polyfit_coeffs_degree_2(self):
        x = [0, 1, 2, 3, 4]
        y = [0, 1, 4, 9, 16]
        coeffs = polyfit_coeffs(x, y, 2)
        assert len(coeffs) == 3
        assert coeffs[0] == pytest.approx(1.0, abs=1e-10)
        assert coeffs[1] == pytest.approx(0.0, abs=1e-10)
        assert coeffs[2] == pytest.approx(0.0, abs=1e-10)

    def test_polyfit_coeffs_degree_1(self):
        x = [0, 1, 2, 3, 4]
        y = [5, 7, 9, 11, 13]
        coeffs = polyfit_coeffs(x, y, 1)
        assert len(coeffs) == 2
        assert coeffs[0] == pytest.approx(2.0)
        assert coeffs[1] == pytest.approx(5.0)

    def test_polyfit_r2_perfect(self):
        x = [0, 1, 2, 3, 4]
        y = [0, 1, 4, 9, 16]
        assert polyfit_r2(x, y, 2) == pytest.approx(1.0)

    def test_polyval(self):
        coeffs = [1, 0, 0]  # y = x^2
        x_vals = [0, 1, 2, 3]
        result = polyval(coeffs, x_vals)
        assert result == [0, 1, 4, 9]

    def test_polyval_linear(self):
        coeffs = [2, 5]  # y = 2x + 5
        x_vals = [0, 1, 2]
        result = polyval(coeffs, x_vals)
        assert result == [5, 7, 9]

    def test_polyfit_mismatched_raises(self):
        with pytest.raises(TypeError):
            polyfit_coeffs([1, 2, 3], [1, 2], 1)

    def test_polyfit_degree_too_high_raises(self):
        with pytest.raises(ValueError):
            polyfit_coeffs([0, 1], [0, 1], 3)


class TestExponentialRegression:
    def test_fit_exponential_coeffs(self):
        import math
        x = [0, 1, 2, 3]
        y = [2.0, 2.0 * math.e, 2.0 * math.e ** 2, 2.0 * math.e ** 3]
        a, b = fit_exponential_coeffs(x, y)
        assert a == pytest.approx(2.0, rel=0.01)
        assert b == pytest.approx(1.0, rel=0.01)

    def test_fit_exponential_r2_perfect(self):
        import math
        x = [0.0, 1.0, 2.0, 3.0]
        y = [1.0, math.e, math.e ** 2, math.e ** 3]
        r2 = fit_exponential_r2(x, y)
        assert r2 == pytest.approx(1.0, abs=0.01)

    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def test_fit_exponential_negative_y_raises(self):
        with pytest.raises(ValueError, match="y must be positive"):
            fit_exponential_coeffs([0.0, 1.0, 2.0], [-1.0, 1.0, 4.0])


class TestPowerRegression:
    def test_fit_power_coeffs(self):
        x = [1, 2, 3, 4, 5]
        y = [3.0 * xi ** 1.5 for xi in [1, 2, 3, 4, 5]]
        a, b = fit_power_coeffs(x, y)
        assert a == pytest.approx(3.0, rel=0.01)
        assert b == pytest.approx(1.5, rel=0.01)

    def test_fit_power_r2_perfect(self):
        x = [1, 2, 3, 4]
        y = [xi ** 2 for xi in x]
        r2 = fit_power_r2(x, y)
        assert r2 == pytest.approx(1.0, abs=0.01)


class TestLogarithmicRegression:
    def test_fit_logarithmic_coeffs(self):
        import numpy as np
        x = [1, 2, 3, 4, 5]
        y = [1.0 + 2.0 * np.log(xi) for xi in x]
        a, b = fit_logarithmic_coeffs(x, y)
        assert a == pytest.approx(1.0, rel=0.1)
        assert b == pytest.approx(2.0, rel=0.1)

    def test_fit_logarithmic_r2_perfect(self):
        import numpy as np
        x = [1, 2, 3, 4]
        y = [np.log(xi) for xi in x]
        r2 = fit_logarithmic_r2(x, y)
        assert r2 == pytest.approx(1.0, abs=0.01)


class TestGoodnessOfFit:
    def test_r_squared_perfect(self):
        y_true = [1, 2, 3, 4, 5]
        y_pred = [1, 2, 3, 4, 5]
        assert r_squared(y_true, y_pred) == pytest.approx(1.0)

    def test_r_squared_poor(self):
        y_true = [1, 2, 3, 4, 5]
        y_pred = [5, 4, 3, 2, 1]
        assert r_squared(y_true, y_pred) == pytest.approx(-3.0)

    def test_r_squared_constant_y_true(self):
        y_true = [0, 0, 0, 0, 0]
        y_pred = [1, 2, 3, 4, 5]
        assert r_squared(y_true, y_pred) == 0.0

    def test_r_squared_constant_y(self):
        y_true = [5, 5, 5]
        y_pred = [1, 2, 3]
        assert r_squared(y_true, y_pred) == 0.0

    def test_rmse(self):
        y_true = [1, 2, 3]
        y_pred = [1.1, 1.9, 3.2]
        expected = math.sqrt((0.01 + 0.01 + 0.04) / 3)
        assert rmse(y_true, y_pred) == pytest.approx(expected)

    def test_rmse_perfect(self):
        assert rmse([1, 2, 3], [1, 2, 3]) == 0.0

    def test_mae(self):
        y_true = [1, 2, 3]
        y_pred = [1.1, 1.9, 3.2]
        expected = (0.1 + 0.1 + 0.2) / 3
        assert mae(y_true, y_pred) == pytest.approx(expected)

    def test_mae_perfect(self):
        assert mae([1, 2, 3], [1, 2, 3]) == 0.0

    def test_rmse_mismatched_lengths_raises(self):
        with pytest.raises(ValueError):
            rmse([1, 2], [1, 2, 3])

    def test_mae_mismatched_lengths_raises(self):
        with pytest.raises(ValueError):
            mae([1, 2], [1, 2, 3])
