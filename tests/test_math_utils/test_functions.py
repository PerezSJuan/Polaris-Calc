import sys
import os
import math
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
ops_path = os.path.join(project_root, "utils", "math_utils", "complex_math_operations")

if ops_path not in sys.path:
    sys.path.insert(0, ops_path)

from functions import (
    from_function, apply_function,
    interpolate_linear, interpolate_cubic_spline, interpolate_nearest,
    interpolate_quadratic, interpolate_pchip, interpolate_akima
)


class TestColumnGeneration:
    def test_from_function_linear(self):
        result = from_function(lambda x: 2 * x, 0, 10, 5)
        assert len(result) == 5
        assert result[0] == 0
        assert result[-1] == 20

    def test_from_function_sqrt(self):
        result = from_function(lambda x: x ** 0.5, 0, 4, 3)
        assert result[0] == 0
        assert result[1] == pytest.approx(2 ** 0.5)
        assert result[2] == 2

    def test_from_function_n_100(self):
        result = from_function(lambda x: x + 1, 0, 99, 100)
        assert len(result) == 100
        assert result[0] == 1
        assert result[-1] == 100

    def test_apply_function(self):
        result = apply_function(lambda x: x ** 2, [1, 2, 3, 4])
        assert result == [1, 4, 9, 16]

    def test_apply_function_empty(self):
        assert apply_function(lambda x: x * 2, []) == []

    def test_apply_function_negative(self):
        result = apply_function(lambda x: abs(x), [-3, -2, -1, 0, 1])
        assert result == [3, 2, 1, 0, 1]


class TestInterpolation:
    def test_interpolate_linear(self):
        x = [0, 1, 2, 3, 4]
        y = [0, 2, 4, 6, 8]
        result = interpolate_linear(x, y, [0.5, 1.5, 2.5])
        assert result == [1, 3, 5]

    def test_interpolate_linear_extrapolate(self):
        x = [0, 1, 2]
        y = [0, 10, 20]
        # x_new within range only
        result = interpolate_linear(x, y, [0.5])
        assert result[0] == 5

    def test_interpolate_linear_single_point(self):
        x = [0, 1]
        y = [5, 10]
        result = interpolate_linear(x, y, [0.25, 0.75])
        assert result == [6.25, 8.75]

    def test_interpolate_cubic_spline(self):
        x = [0, 1, 2, 3, 4]
        y = [0, 1, 4, 9, 16]
        result = interpolate_cubic_spline(x, y, [0.5, 1.5, 2.5])
        assert result[0] == pytest.approx(0.25)
        assert result[1] == pytest.approx(2.25)
        assert result[2] == pytest.approx(6.25)

    def test_interpolate_cubic_spline_identity(self):
        x = [0, 1, 2, 3]
        y = [0, 1, 2, 3]
        result = interpolate_cubic_spline(x, y, [0, 1, 2, 3])
        for r, e in zip(result, y):
            assert r == pytest.approx(e)

    def test_interpolate_nearest(self):
        x = [0, 1, 2, 3, 4]
        y = [0, 10, 20, 30, 40]
        result = interpolate_nearest(x, y, [0.4, 0.6, 1.4, 1.6])
        assert result == [0, 10, 10, 20]

    def test_interpolate_quadratic(self):
        x = [0, 1, 2, 3, 4]
        y = [0, 1, 4, 9, 16]
        result = interpolate_quadratic(x, y, [2.5])
        assert result[0] == pytest.approx(6.25, rel=0.1)

    def test_interpolate_pchip(self):
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 1, 0, 1, 0, 1]
        result = interpolate_pchip(x, y, [0.5, 1.5, 2.5])
        assert len(result) == 3
        # PCHIP preserves monotonicity, so all results in [0, 1]
        for v in result:
            assert 0 <= v <= 1

    def test_interpolate_akima(self):
        x = [0, 1, 2, 3, 4, 5]
        y = [0, 2, 0, 4, 0, 6]
        result = interpolate_akima(x, y, [0.5, 1.5, 2.5])
        assert len(result) == 3

    def test_interpolate_mismatched_x_y_raises(self):
        with pytest.raises(ValueError):
            interpolate_linear([1, 2, 3], [1, 2], [1.5])

    def test_interpolation_returns_list(self):
        x = [1, 2, 3]
        y = [1, 4, 9]
        result = interpolate_linear(x, y, [2.5])
        assert isinstance(result, list)
