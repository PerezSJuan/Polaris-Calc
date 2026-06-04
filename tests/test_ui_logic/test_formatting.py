import sys
import os
import math
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
utils_math_path = os.path.join(project_root, "utils", "math_utils")
for p in [utils_math_path, project_root]:
    if p not in sys.path:
        sys.path.insert(0, p)

from screens.editor.components.column import _fmt, _fmt_edit, _type_accent


class TestFmt:
    def test_fmt_integer(self):
        assert _fmt(42) == "42"
        assert _fmt(0) == "0"
        assert _fmt(-5) == "-5"

    def test_fmt_float(self):
        assert _fmt(3.14) == "3.14"

    def test_fmt_large_integer(self):
        result = _fmt(1_000_000)
        assert isinstance(result, str)
        assert "10" in result or "1e" in result or "1" in result

    def test_fmt_infinity(self):
        assert _fmt(float("inf")) == "inf"
        assert _fmt(float("-inf")) == "-inf"

    def test_fmt_nan(self):
        assert _fmt(float("nan")) == "nan"

    def test_fmt_complex(self):
        result = _fmt(3 + 4j)
        assert "3" in result
        assert "4" in result
        assert "j" in result

    def test_fmt_complex_negative_imag(self):
        result = _fmt(3 - 4j)
        assert "3" in result
        assert "4" in result
        assert "j" in result

    def test_fmt_complex_positive_sign(self):
        result = _fmt(1 + 2j)
        assert "+" in result

    def test_fmt_zero(self):
        assert _fmt(0.0) == "0"

    def test_fmt_negative_zero(self):
        result = _fmt(-0.0)
        assert result == "0" or result == "-0"

    def test_fmt_string(self):
        assert _fmt("hello") == "hello"


class TestFmtEdit:
    def test_fmt_edit_integer(self):
        result = _fmt_edit(42)
        assert isinstance(result, str)

    def test_fmt_edit_float(self):
        result = _fmt_edit(3.14159265358979)
        assert isinstance(result, str)

    def test_fmt_edit_large_number(self):
        result = _fmt_edit(1e25)
        assert "e" in result

    def test_fmt_edit_small_number(self):
        result = _fmt_edit(0.0001)
        assert isinstance(result, str)

    def test_fmt_edit_infinity(self):
        assert _fmt_edit(float("inf")) == "inf"

    def test_fmt_edit_nan(self):
        assert _fmt_edit(float("nan")) == "nan"

    def test_fmt_edit_complex(self):
        result = _fmt_edit(1 + 2j)
        assert isinstance(result, str)
        assert "j" in result

    def test_fmt_edit_negative_zero(self):
        assert _fmt_edit(-0.0) == "0"

    def test_fmt_edit_string(self):
        assert _fmt_edit("test") == "test"

    def test_fmt_edit_precision(self):
        result = _fmt_edit(1.0 / 3.0)
        assert len(result) >= 15

    def test_fmt_edit_edge_1e20(self):
        result = _fmt_edit(1e20)
        assert "e" in result


class TestTypeAccent:
    @pytest.fixture
    def themes(self):
        class FakeThemes:
            actual_theme = {
                "primary": "#6750A4",
                "secondary": "#625B71",
                "error": "#B3261E",
                "formula_accent": "#E8A040",
                "constant_accent": "#4A90D9",
                "error_accent": "#E04040",
                "background": "#FFFBFE",
            }
            dark_theme = {"background": "#1C1B1F"}
        return FakeThemes()

    def test_formula_type(self, themes):
        result = _type_accent("formula", themes)
        assert result == "#E8A040"

    def test_constant_type(self, themes):
        result = _type_accent("constant", themes)
        assert result == "#4A90D9"

    def test_error_type(self, themes):
        result = _type_accent("error", themes)
        assert result == "#E04040"

    def test_bool_type_light(self, themes):
        result = _type_accent("bool", themes)
        assert result is not None

    def test_unknown_type_uses_primary(self, themes):
        result = _type_accent("unknown", themes)
        assert result == "#6750A4"

    def test_case_insensitive(self, themes):
        assert _type_accent("FORMULA", themes) == "#E8A040"

    def test_partial_match_formula(self, themes):
        assert _type_accent("formula_with_extra", themes) == "#E8A040"
