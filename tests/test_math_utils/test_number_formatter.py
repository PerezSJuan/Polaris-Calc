import sys
import os
import pytest

# Add the directory containing the utils to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
utils_path = os.path.join(project_root, "utils", "math utils")

if utils_path not in sys.path:
    sys.path.append(utils_path)

from number_formatter import smart_format

def test_smart_format_no_change():
    # Numbers that already fit within max_chars should not change
    assert smart_format(42, 7) == "42"
    assert smart_format(10, 7) == "10"
    assert smart_format(100, 7) == "100"

def test_smart_format_scientific_text():
    # Large numbers should be formatted in scientific notation
    assert smart_format(2675353353535133, 7) == "2.68e15"
    assert smart_format(1_000_000_000, 7) == "1e9"
    assert smart_format(-9_876_543_210, 8) == "-9.877e9"

def test_smart_format_latex():
    # LaTeX mode
    assert smart_format(2675353353535133, 7, latex=True) == "2.68 \\times 10^{15}"
    assert smart_format(1_000_000_000, 7, latex=True) == "10^{9}"
    assert smart_format(-1_000_000_000, 7, latex=True) == "-10^{9}"

def test_smart_format_precision():
    # Precision depends on max_chars
    num = 2675353353535133
    # exp=15, suffix_len=3, budget=2, decimals=0, round(2.67)=3 -> "3e15"
    assert smart_format(num, 5) == "3e15"

def test_smart_format_zero():
    assert smart_format(0, 7) == "0"

def test_smart_format_invalid_max_chars():
    with pytest.raises(ValueError):
        smart_format(100, 2)
