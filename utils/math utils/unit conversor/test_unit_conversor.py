
"""Unit tests for the compound expression converter.

Run with:
    python test_unit_conversor.py
or:
    python -m pytest test_unit_conversor.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# We import from the new module.  If running from the outputs folder, adjust
# the path so that default_units.py is found.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unit_conversor import (
    tokenize_expression,
    parse_term,
    parse_compound_expression,
    simplify_expression,
    convert_compound,
    convert,
    get_unit_type,
)

import math

PASS = "[PASS]"
FAIL = "[FAIL]"

results = []

def check(name, got, expected, *, rel_tol=1e-6, is_approx=False):
    if is_approx:
        ok = math.isclose(got, expected, rel_tol=rel_tol)
    elif isinstance(expected, float):
        ok = math.isclose(got, expected, rel_tol=rel_tol)
    else:
        ok = got == expected
    status = PASS if ok else FAIL
    results.append(ok)
    print(f"  [{status}]  {name}")
    if not ok:
        print(f"          got:      {got!r}")
        print(f"          expected: {expected!r}")


def check_raises(name, fn, exc_type=ValueError):
    try:
        fn()
        results.append(False)
        print(f"  [{FAIL}]  {name}  (no exception raised)")
    except exc_type:
        results.append(True)
        print(f"  [{PASS}]  {name}")
    except Exception as e:
        results.append(False)
        print(f"  [{FAIL}]  {name}  (wrong exception: {type(e).__name__}: {e})")


# ===========================================================================
print("\n=== tokenize_expression ===")
check("kg*m/s^2",
      tokenize_expression("kg*m/s^2"),
      ['kg', '*', 'm', '/', 's^2'])

check("J/(kg*K) - parens expanded to J/kg/K",
      tokenize_expression("J/(kg*K)"),
      ['J', '/', 'kg', '/', 'K'])

check("km^3 - single token",
      tokenize_expression("km^3"),
      ['km^3'])

check("kg m - implicit multiplication",
      tokenize_expression("kg m"),
      ['kg', '*', 'm'])

check("Unicode * operator",
      tokenize_expression("kg·m/s^2"),
      ['kg', '*', 'm', '/', 's^2'])

check("Unicode ^2 superscript",
      tokenize_expression("m²"),
      ['m^2'])


# ===========================================================================
print("\n=== parse_term (factor correctness) ===")

# km → factor = 1000 * 1.0  (m base factor = 1.0)
dim, f = parse_term("km")
check("km dim = L", dim, (1, 0, 0, 0, 0, 0, 0))
check("km factor = 1000", f, 1000.0)

# km^3 → factor = (1000)^3 = 1e9
dim, f = parse_term("km^3")
check("km^3 dim = L^3", dim, (3, 0, 0, 0, 0, 0, 0))
check("km^3 factor = 1e9", f, 1e9)

# kg -> prefix k on g -> factor = 1000 * 0.001 = 1.0
dim, f = parse_term("kg")
check("kg dim = M", dim, (0, 1, 0, 0, 0, 0, 0))
check("kg factor = 1", f, 1.0)

# s^2 → factor = 1^2 = 1
dim, f = parse_term("s^2")
check("s^2 dim = T^2", dim, (0, 0, 2, 0, 0, 0, 0))
check("s^2 factor = 1", f, 1.0)

# ms → prefix m on s, use_prefixes=False for s? Check:
# s has use_prefixes=False in default_units; so ms should NOT match via prefix.
# It should raise / return None.  Let's just check behaviour is not silently wrong.
# (ms is millisecond only if s has use_prefixes=True; here it doesn't — ms maps to nothing.)


# ===========================================================================
print("\n=== parse_compound_expression (dimensions) ===")

# kg*m/s^2 -> N -> (1,1,-2,0,0,0,0)
dim, f = parse_compound_expression("kg*m/s^2")
check("kg*m/s^2 dim = N", dim, (1, 1, -2, 0, 0, 0, 0))

# m^2*kg/s^2 -> J -> (2,1,-2,0,0,0,0)
dim, f = parse_compound_expression("m^2*kg/s^2")
check("m^2*kg/s^2 dim = J", dim, (2, 1, -2, 0, 0, 0, 0))

# J/(kg*K) -> specific heat -> (2,0,-2,0,-1,0,0)
dim, f = parse_compound_expression("J/(kg*K)")
check("J/(kg*K) dim = spec heat", dim, (2, 0, -2, 0, -1, 0, 0))

# km^3 -> L^3 -> (3,0,0,0,0,0,0)
dim, f = parse_compound_expression("km^3")
check("km^3 dim = L^3", dim, (3, 0, 0, 0, 0, 0, 0))
check("km^3 factor = 1e9", f, 1e9)


# ===========================================================================
print("\n=== simplify_expression (returns List[str] or None) ===")

check("kg*m/s^2 -> ['N']",        simplify_expression("kg*m/s^2"),   ["N"])
check("m^2*kg/s^2 -> ['J','N·m']",simplify_expression("m^2*kg/s^2"), ["J", "N·m"])
check("J/(kg*K) -> spec heat list",
      simplify_expression("J/(kg*K)"), ["J/(kg·K)", "m²/(s²·K)"])
# T^-1 is the key ambiguity case: Hz, rad/s, and Bq all share the same dims
check("s^-1 -> ['Hz','rad/s','Bq']",
      simplify_expression("s^-1"), ["Hz", "rad/s", "Bq"])
check("km/h -> None (not in derived_units)",
      simplify_expression("km/h"), None)

print("\n=== get_unit_type (compound -> comma-joined string) ===")

check("kg*m/s^2 -> 'N'",     get_unit_type("kg*m/s^2"), "N")
check("km/h -> 'Compound'",  get_unit_type("km/h"),     "Compound")
check("USD -> 'Currency'",   get_unit_type("USD"),       "Currency")
check("km -> 'Length'",      get_unit_type("km"),        "Length")
check("Pa -> 'Pressure'",    get_unit_type("Pa"),        "Pressure")
# Ambiguous T^-1: get_unit_type should join all matches
check("s^-1 -> 'Hz, rad/s, Bq'", get_unit_type("s^-1"), "Hz, rad/s, Bq")

# ===========================================================================
print("\n=== convert (volume with power + prefix) ===")

res = convert(1.0, "km^3", "m^3")
check("1 km^3 = 1e9 m^3", res, 1e9)

res = convert(3.0, "km^3", "m^3")
check("3 km^3 = 3e9 m^3", res, 3e9)

res = convert(1.0, "m^3", "cm^3")
check("1 m^3 = 1e6 cm^3", res, 1e6)


# ===========================================================================
print("\n=== convert (specific heat capacity) ===")

res = convert(1.0, "J/(kg*K)", "cal/(g*K)")
check("1 J/(kg·K) ≈ 2.39e-4 cal/(g·K)", res, 1/4184, rel_tol=1e-4, is_approx=True)


# ===========================================================================
print("\n=== convert (simple units — backward compat) ===")

res = convert(1000.0, "m", "km")
check("1000 m = 1 km", res, 1.0)

res = convert(1.0, "km", "m")
check("1 km = 1000 m", res, 1000.0)

res = convert(0.0, "C", "K")
check("0 C = 273.15 K", res, 273.15)

res = convert(100.0, "C", "F")
check("100 C = 212 F", res, 212.0, rel_tol=1e-5, is_approx=True)


# ===========================================================================
print("\n=== error cases ===")

check_raises("currency in compound raises ValueError",
             lambda: convert(1.0, "kg*USD", "g*EUR"))

check_raises("dimension mismatch raises ValueError",
             lambda: convert_compound(1.0, "J", "m"))


# ===========================================================================
print("\n=== Summary ===")
passed = sum(results)
total = len(results)
print(f"  {passed}/{total} tests passed.")
if passed < total:
    print("  Some tests FAILED — review output above.")
else:
    print("  All tests passed! ✓")