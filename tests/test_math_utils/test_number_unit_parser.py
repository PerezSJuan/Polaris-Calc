import sys
import os
import pytest

# Add the directory containing the utils to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
utils_path = os.path.join(project_root, "utils", "math_utils")

if utils_path not in sys.path:
    sys.path.append(utils_path)

from number_unit_parser import parse, evaluate, ParsedValue

def test_parse_basic():
    res = parse("1.234,56 km")
    assert res.value == 1234.56
    assert res.unit == "km"

def test_parse_different_formats():
    assert parse("1,234.56 km").value == 1234.56
    assert parse("1 234,56 km").value == 1234.56
    assert parse("1'234.56 km").value == 1234.56
    assert parse("3.14159").value == 3.14159
    assert parse("3,14159").value == 3.14159

def test_parse_negative():
    assert parse("-3,14 °C").value == -3.14
    assert parse("−273.15°C").value == -273.15

def test_parse_scientific():
    assert parse("1.5e3 Hz").value == 1500.0
    assert parse("6.022e23 mol⁻¹").value == 6.022e23

def test_parse_unit_position():
    assert parse("$1,234.99").unit == "$"
    assert parse("€ 1.234,99").unit == "€"
    assert parse("42%").unit == "%"

def test_evaluate_basic():
    res = evaluate("1.234,56 + 765,44 km")
    assert res.value == 2000.0
    assert res.unit == "km"

def test_evaluate_expressions():
    assert evaluate("100 * 3,14 m²").value == 314.0
    assert evaluate("2^10 bits").value == 1024.0
    assert evaluate("(3 + 2) * 20 €").value == 100.0

def test_evaluate_no_operators():
    # Should delegate to parse()
    assert evaluate("3,14159").value == 3.14159
    assert evaluate("100 km").unit == "km"

def test_parse_error():
    with pytest.raises(ValueError):
        parse("no number here")

def test_evaluate_error():
    with pytest.raises(ValueError):
        evaluate("3 + (2 * )")
