"""The utility module for unit conversion — with compound expression support."""

from default_units import default_units
from typing import Optional, List
import re
import warnings

# ---------------------------------------------------------------------------
# Standard SI Prefixes (Base 10)
# ---------------------------------------------------------------------------
prefixes = {
    "Y":  1e24,   # yotta
    "Z":  1e21,   # zetta
    "E":  1e18,   # exa
    "P":  1e15,   # peta
    "T":  1e12,   # tera
    "G":  1e9,    # giga
    "M":  1e6,    # mega
    "k":  1e3,    # kilo
    "h":  1e2,    # hecto
    "da": 1e1,    # deca
    "d":  1e-1,   # deci
    "c":  1e-2,   # centi
    "m":  1e-3,   # milli
    "u":  1e-6,   # micro (ASCII)
    "µ":  1e-6,   # micro (Unicode)
    "n":  1e-9,   # nano
    "p":  1e-12,  # pico
    "f":  1e-15,  # femto
    "a":  1e-18,  # atto
    "z":  1e-21,  # zepto
    "y":  1e-24,  # yocto
}

# ---------------------------------------------------------------------------
# Dimensional vectors  [L, M, T, I, Θ, N, J]
#   L = Length, M = Mass, T = Time, I = Electric current,
#   Θ = Temperature, N = Amount of substance, J = Luminous intensity
#
# Mass base unit is kilogram (kg), consistent with default_units["Mass"]
# where g has factor 0.001 (so kg = 1.0).
# All compound factors are therefore in kg·m·s·A·K·mol·cd space (SI standard).
#
# COLLISION NOTES
# ---------------
# Several unit symbols are ambiguous across categories in default_units:
#   "F"  → Electric Capacitance (Farad)  OR  Temperature (Fahrenheit)
#   "C"  → Electric Charge (Coulomb)     OR  Temperature (Celsius)
#   "T"  → Magnetic Flux Density (Tesla) OR  SI prefix Tera (handled separately)
#
# To avoid these collisions in base_dimensions we use unambiguous internal keys:
#   Farad     → "Farad"
#   Fahrenheit→ "F_temp"
#   Coulomb   → "Coulomb"
#   Tesla     → "T_mag"
#
# The mapping from (symbol, category) → internal key is in _DIM_KEY_OVERRIDES.
# ---------------------------------------------------------------------------
base_dimensions = {
    # --- SI base units ---
    "m":       (1,  0,  0,  0,  0,  0,  0),   # metre
    "kg":      (0,  1,  0,  0,  0,  0,  0),   # kilogram (base for M)
    "g":       (0,  1,  0,  0,  0,  0,  0),   # gram (dimensionally identical)
    "s":       (0,  0,  1,  0,  0,  0,  0),   # second
    "A":       (0,  0,  0,  1,  0,  0,  0),   # ampere
    "K":       (0,  0,  0,  0,  1,  0,  0),   # kelvin
    "mol":     (0,  0,  0,  0,  0,  1,  0),   # mole
    "cd":      (0,  0,  0,  0,  0,  0,  1),   # candela

    # --- Dimensionless ---
    "rad":     (0,  0,  0,  0,  0,  0,  0),
    "sr":      (0,  0,  0,  0,  0,  0,  0),
    "bit":     (0,  0,  0,  0,  0,  0,  0),
    "B":       (0,  0,  0,  0,  0,  0,  0),

    # --- Temperature scale aliases (treated as Θ differences in compounds) ---
    "C":       (0,  0,  0,  0,  1,  0,  0),   # Celsius
    "F_temp":  (0,  0,  0,  0,  1,  0,  0),   # Fahrenheit (unambiguous key)
    "R":       (0,  0,  0,  0,  1,  0,  0),   # Rankine

    # --- Derived SI units ---
    "N":       ( 1,  1, -2,  0,  0,  0,  0),  # Newton      kg·m/s²
    "J":       ( 2,  1, -2,  0,  0,  0,  0),  # Joule       N·m
    "W":       ( 2,  1, -3,  0,  0,  0,  0),  # Watt        J/s
    "Pa":      (-1,  1, -2,  0,  0,  0,  0),  # Pascal      N/m²
    "Hz":      ( 0,  0, -1,  0,  0,  0,  0),  # Hertz       s⁻¹
    "V":       ( 2,  1, -3, -1,  0,  0,  0),  # Volt        W/A
    "Ω":       ( 2,  1, -3, -2,  0,  0,  0),  # Ohm         V/A
    "Ohm":     ( 2,  1, -3, -2,  0,  0,  0),  # Ohm (alias)
    "Farad":   (-2, -1,  4,  2,  0,  0,  0),  # Farad       C/V  (unambiguous key)
    "Coulomb": ( 0,  0,  1,  1,  0,  0,  0),  # Coulomb     A·s  (unambiguous key)
    "H":       ( 2,  1, -2, -2,  0,  0,  0),  # Henry       V·s/A
    "Wb":      ( 2,  1, -2, -1,  0,  0,  0),  # Weber       V·s
    "T_mag":   ( 0,  1, -2, -1,  0,  0,  0),  # Tesla       Wb/m² (unambiguous key)
    "lm":      ( 0,  0,  0,  0,  0,  0,  1),  # Lumen       cd·sr
    "lx":      (-2,  0,  0,  0,  0,  0,  1),  # Lux         lm/m²
    "Bq":      ( 0,  0, -1,  0,  0,  0,  0),  # Becquerel   s⁻¹
    "Gy":      ( 2,  0, -2,  0,  0,  0,  0),  # Gray        J/kg
    "Sv":      ( 2,  0, -2,  0,  0,  0,  0),  # Sievert     J/kg
    "kat":     ( 0,  0, -1,  0,  0,  1,  0),  # Katal       mol/s

    # --- Non-SI common units ---
    "cal":     ( 2,  1, -2,  0,  0,  0,  0),  # calorie       ≡ J
    "Wh":      ( 2,  1, -2,  0,  0,  0,  0),  # watt-hour     ≡ J
    "eV":      ( 2,  1, -2,  0,  0,  0,  0),  # electronvolt  ≡ J
    "BTU":     ( 2,  1, -2,  0,  0,  0,  0),  # BTU           ≡ J
    "bar":     (-1,  1, -2,  0,  0,  0,  0),  # bar           ≡ Pa
    "atm":     (-1,  1, -2,  0,  0,  0,  0),  # atmosphere    ≡ Pa
    "psi":     (-1,  1, -2,  0,  0,  0,  0),  # psi           ≡ Pa
    "l":       ( 3,  0,  0,  0,  0,  0,  0),  # litre         ≡ m³  (lowercase)
    "L":       ( 3,  0,  0,  0,  0,  0,  0),  # litre         ≡ m³  (uppercase)
    "min":     ( 0,  0,  1,  0,  0,  0,  0),  # minute        ≡ s
    "h":       ( 0,  0,  1,  0,  0,  0,  0),  # hour          ≡ s
    "day":     ( 0,  0,  1,  0,  0,  0,  0),  # day           ≡ s
    # Imperial length
    "in":      ( 1,  0,  0,  0,  0,  0,  0),
    "ft":      ( 1,  0,  0,  0,  0,  0,  0),
    "yd":      ( 1,  0,  0,  0,  0,  0,  0),
    "mi":      ( 1,  0,  0,  0,  0,  0,  0),
    # Imperial / common mass
    "lb":      ( 0,  1,  0,  0,  0,  0,  0),
    "oz":      ( 0,  1,  0,  0,  0,  0,  0),
    # Force variants
    "lbf":     ( 1,  1, -2,  0,  0,  0,  0),
    "kgf":     ( 1,  1, -2,  0,  0,  0,  0),
    "dyn":     ( 1,  1, -2,  0,  0,  0,  0),
}

# ---------------------------------------------------------------------------
# Disambiguation: (symbol_in_default_units, category) → key in base_dimensions
# ---------------------------------------------------------------------------
_DIM_KEY_OVERRIDES = {
    ("F", "Electric Capacitance"): "Farad",
    ("F", "Temperature"):          "F_temp",
    ("C", "Electric Charge"):      "Coulomb",
    ("C", "Temperature"):          "C",
    ("T", "Magnetic Flux Density"): "T_mag",
}

# ---------------------------------------------------------------------------
# Reverse-lookup: dimensional vector → list of all physically distinct
# interpretations that share those dimensions.
#
# A single dimensional vector can correspond to multiple physically different
# quantities.  Examples:
#   (0,0,-1,0,0,0,0)  →  Hz (frequency), rad/s (angular velocity), Bq (radioactivity)
#   (2,0,-2,0,0,0,0)  →  Gy (absorbed dose), Sv (equivalent dose), J/kg
#
# Each entry is a list so that simplify_expression() returns ALL matches
# rather than silently discarding the ambiguity.
# ---------------------------------------------------------------------------
derived_units: dict = {
    ( 1,  1, -2,  0,  0,  0,  0): ["N"],
    ( 2,  1, -2,  0,  0,  0,  0): ["J", "N·m"],
    ( 2,  1, -3,  0,  0,  0,  0): ["W"],
    (-1,  1, -2,  0,  0,  0,  0): ["Pa", "N/m²"],
    # T⁻¹: frequency, angular velocity, and radioactivity share this vector
    # but represent physically distinct quantities.
    ( 0,  0, -1,  0,  0,  0,  0): ["Hz", "rad/s", "Bq"],
    ( 2,  1, -3, -1,  0,  0,  0): ["V"],
    ( 2,  1, -3, -2,  0,  0,  0): ["Ω"],
    (-2, -1,  4,  2,  0,  0,  0): ["F"],           # Farad
    ( 0,  0,  1,  1,  0,  0,  0): ["C"],           # Coulomb = A·s
    ( 2,  1, -2, -2,  0,  0,  0): ["H"],           # Henry
    ( 2,  1, -2, -1,  0,  0,  0): ["Wb"],
    ( 0,  1, -2, -1,  0,  0,  0): ["T"],           # Tesla
    ( 0,  0,  0,  0,  0,  0,  1): ["cd"],
    (-2,  0,  0,  0,  0,  0,  1): ["lx"],
    # L²T⁻²: absorbed dose, equivalent dose, and specific energy are
    # dimensionally identical but physically (and metrologically) different.
    ( 2,  0, -2,  0,  0,  0,  0): ["Gy", "Sv", "J/kg"],
    ( 2,  0, -2,  0, -1,  0,  0): ["J/(kg·K)", "m²/(s²·K)"],  # specific heat
    # Angular momentum / action: J·s = kg·m²/s
    ( 2,  1, -1,  0,  0,  0,  0): ["J·s", "kg·m²/s"],
    # Dynamic viscosity
    (-1,  1, -1,  0,  0,  0,  0): ["Pa·s", "kg/(m·s)"],
    # Kinematic viscosity / thermal diffusivity
    ( 2,  0, -1,  0,  0,  0,  0): ["m²/s"],
    # Surface tension / spring constant per unit length
    ( 0,  1, -2,  0,  0,  0,  0): ["N/m", "J/m²"],
    # Catalytic activity
    ( 0,  0, -1,  0,  0,  1,  0): ["kat", "mol/s"],
}

# ---------------------------------------------------------------------------
# Internal helpers  (private — prefix with _)
# ---------------------------------------------------------------------------

def _get_base_unit_info(unit_symbol: str,
                        unit_collection: dict = default_units) -> Optional[dict]:
    """Return the info dict for *unit_symbol*, or None if not found."""
    for _category, units in unit_collection.items():
        if unit_symbol in units:
            return units[unit_symbol]
    return None


def _get_unit_category(unit_symbol: str,
                       unit_collection: dict = default_units) -> Optional[str]:
    """Return the category name for *unit_symbol*, or None."""
    for category, units in unit_collection.items():
        if unit_symbol in units:
            return category
    return None


def _is_compound(expression: str) -> bool:
    """Return True if *expression* contains compound-expression operators."""
    return bool(re.search(r'[*/^·×÷]', expression))


def _resolve_dim_key(base_name: str, category: Optional[str]) -> str:
    """Map (symbol, category) → the correct key in *base_dimensions*.

    Handles ambiguous symbols such as 'F', 'C', and 'T' that represent
    different physical quantities in different unit categories.
    """
    return _DIM_KEY_OVERRIDES.get((base_name, category), base_name)


def _flip_operators(expression: str) -> str:
    """Replace every '*' with '/' and every '/' with '*' in *expression*."""
    result = []
    for ch in expression:
        if ch == '*':
            result.append('/')
        elif ch == '/':
            result.append('*')
        else:
            result.append(ch)
    return ''.join(result)


def _expand_parens(expression: str) -> str:
    """Distribute the operator preceding each parenthesised group.

    Rules
    -----
    A/(B*C)  →  A/B/C    (division flips all operators inside)
    A*(B*C)  →  A*B*C    (multiplication keeps operators unchanged)
    (B*C)*A  →  B*C*A    (leading group: just remove parens)

    Only handles flat (non-nested) groups.  Nested groups are resolved
    iteratively up to a safety limit of 20 passes.
    """
    pattern = re.compile(r'([*/]?)\(([^()]+)\)')

    def _replace_group(match: re.Match) -> str:
        preceding_op = match.group(1)   # '*', '/', or ''
        inner_expr   = match.group(2)
        if preceding_op == '/':
            return '/' + _flip_operators(inner_expr)
        elif preceding_op == '*':
            return '*' + inner_expr
        else:
            # No preceding operator — expression starts with '(' or follows '^'
            return inner_expr

    for _ in range(20):
        if '(' not in expression:
            break
        expression = pattern.sub(_replace_group, expression)

    return expression


# ---------------------------------------------------------------------------
# Public helpers  (same API as original module)
# ---------------------------------------------------------------------------

def get_unit_info(unit_str: str,
                  unit_collection: dict = default_units) -> Optional[dict]:
    """Return unit info for a simple unit string, supporting SI prefixes."""
    info = _get_base_unit_info(unit_str, unit_collection)
    if info:
        return info

    prefix, base_name, combined_factor = parse_unit_with_prefix(unit_str, unit_collection)
    if base_name:
        base_info = _get_base_unit_info(base_name, unit_collection)
        return {
            "factor":       combined_factor,
            "use_prefixes": False,
            "base_unit":    base_name,
            "prefix":       prefix,
            "offset":       base_info.get("offset", 0.0),
        }
    return None


def get_unit_type(unit_str: str,
                  unit_collection: dict = default_units) -> Optional[str]:
    """Return the physical category of a unit, supporting prefixes and compound
    expressions (e.g. 'kg*m/s^2', 'J/(kg*K)', 'km/h').

    For compound expressions the return value is:
    - A comma-separated string of all matching derived-unit names when the
      dimensional vector is recognised (e.g. 'Hz, rad/s, Bq' for T⁻¹).
    - 'Compound' for valid but unrecognised compound expressions.
    - The category string (e.g. 'Length', 'Mass') for simple units.
    - None if the unit cannot be resolved at all.
    """
    if _is_compound(unit_str):
        _check_no_currency(unit_str, unit_collection)
        matches = simplify_expression(unit_str, unit_collection)
        if matches:
            return ", ".join(matches)
        return "Compound"

    # Exact match
    for category, units in unit_collection.items():
        if unit_str in units:
            return category

    # Try with SI prefix
    _prefix, base_unit, _factor = parse_unit_with_prefix(unit_str, unit_collection)
    if base_unit:
        for category, units in unit_collection.items():
            if base_unit in units:
                return category

    return None


def parse_unit_with_prefix(unit_str: str,
                            unit_collection: dict = default_units) -> tuple:
    """Parse a unit string that may carry an SI prefix.

    Returns
    -------
    (prefix_str, base_unit_str, combined_factor)
        All three values are None when the unit cannot be resolved.
    """
    # Exact match (no prefix)
    unit_info = _get_base_unit_info(unit_str, unit_collection)
    if unit_info:
        return "", unit_str, unit_info["factor"]

    # Try each prefix in declaration order
    for prefix_str, prefix_value in prefixes.items():
        if unit_str.startswith(prefix_str):
            remainder = unit_str[len(prefix_str):]
            unit_info = _get_base_unit_info(remainder, unit_collection)
            if unit_info and unit_info.get("use_prefixes", False):
                return prefix_str, remainder, prefix_value * unit_info["factor"]

    return None, None, None


def convert_units(value: float, from_unit: str, to_unit: str,
                  unit_collection: dict = default_units) -> float:
    """Convert *value* from *from_unit* to *to_unit* (simple units only)."""
    _p1, base1, factor1 = parse_unit_with_prefix(from_unit, unit_collection)
    _p2, base2, factor2 = parse_unit_with_prefix(to_unit,   unit_collection)

    if base1 is None:
        raise ValueError(f"Unknown unit: '{from_unit}'")
    if base2 is None:
        raise ValueError(f"Unknown unit: '{to_unit}'")

    if from_unit == to_unit:
        return value

    type1 = get_unit_type(from_unit, unit_collection)
    type2 = get_unit_type(to_unit,   unit_collection)

    if type1 != type2:
        raise ValueError(
            f"Dimensional mismatch: cannot convert {type1} ('{from_unit}') "
            f"to {type2} ('{to_unit}')"
        )

    info1 = _get_base_unit_info(base1, unit_collection)
    info2 = _get_base_unit_info(base2, unit_collection)

    # To internal base (offset applied for e.g. temperatures)
    base_val = value * factor1 + info1.get("offset", 0.0)
    # From internal base to target unit
    result = (base_val - info2.get("offset", 0.0)) / factor2

    return result


# ---------------------------------------------------------------------------
# Compound expression parsing
# ---------------------------------------------------------------------------

def _check_no_currency(expression: str,
                       unit_collection: dict = default_units) -> None:
    """Raise ValueError if any unit token in *expression* is a currency.

    Must be called *after* tokenize_expression is defined.
    """
    tokens = tokenize_expression(expression)
    for token in tokens:
        if token in ('*', '/'):
            continue
        unit_part = token.split('^')[0]   # strip exponent
        _prefix, base_name, _factor = parse_unit_with_prefix(unit_part, unit_collection)
        name_to_check = base_name if base_name else unit_part
        if _get_unit_category(name_to_check, unit_collection) == "Currency":
            raise ValueError(
                f"Currency unit '{name_to_check}' cannot be used inside a "
                f"compound physical expression."
            )


def tokenize_expression(expression: str) -> list:
    """Break a compound unit expression into unit tokens and operator tokens.

    Supported input formats
    -----------------------
    kg*m/s^2    → ['kg', '*', 'm', '/', 's^2']
    kg·m/s²     → ['kg', '*', 'm', '/', 's^2']   (Unicode operators / superscripts)
    J/(kg*K)    → ['J', '/', 'kg', '/', 'K']      (parentheses expanded correctly)
    km^3        → ['km^3']
    kg m        → ['kg', '*', 'm']                 (implicit multiplication)
    """
    # 1. Normalise Unicode operators to ASCII equivalents
    expression = (expression
                  .replace('·', '*')
                  .replace('×', '*')
                  .replace('÷', '/'))

    # 2. Normalise Unicode superscript digits to ^n notation
    _superscripts = {
        '¹': '^1', '²': '^2', '³': '^3', '⁴': '^4', '⁵': '^5',
        '⁶': '^6', '⁷': '^7', '⁸': '^8', '⁹': '^9',
    }
    for superscript_char, replacement in _superscripts.items():
        expression = expression.replace(superscript_char, replacement)

    # 3. Expand parentheses (distributes division sign into the group)
    expression = _expand_parens(expression)

    # 4. Split on * and / delimiters, keeping them as separate tokens
    raw_parts = re.split(r'([*/])', expression)

    tokens = []
    for part in raw_parts:
        part = part.strip()
        if not part:
            continue
        if part in ('*', '/'):
            tokens.append(part)
        else:
            # Handle implicit multiplication: "kg m" → ['kg', '*', 'm']
            sub_parts = re.split(r'\s+', part)
            for index, sub in enumerate(sub_parts):
                if sub:
                    if index > 0:
                        tokens.append('*')
                    tokens.append(sub)

    return tokens


# ---------------------------------------------------------------------------
# Dimension arithmetic
# ---------------------------------------------------------------------------

def _dim_add(dim_a: tuple, dim_b: tuple) -> tuple:
    """Add two dimensional vectors (corresponds to multiplying units)."""
    return tuple(a + b for a, b in zip(dim_a, dim_b))


def _dim_sub(dim_a: tuple, dim_b: tuple) -> tuple:
    """Subtract two dimensional vectors (corresponds to dividing units)."""
    return tuple(a - b for a, b in zip(dim_a, dim_b))


def _dim_scale(dim: tuple, exponent) -> tuple:
    """Scale a dimensional vector by *exponent* (integer or float)."""
    return tuple(component * exponent for component in dim)


# ---------------------------------------------------------------------------
# Core compound-expression functions
# ---------------------------------------------------------------------------

def parse_term(term: str,
               unit_collection: dict = default_units,
               as_difference: bool = True) -> tuple:
    """Parse one unit token (with optional exponent) into (dim, factor).

    Parameters
    ----------
    term : str
        A token such as 'km', 'km^3', 's^2', 'K', or 'cal'.
    unit_collection : dict
        Unit database to use (default: default_units).
    as_difference : bool
        When True (always the case for compound expressions) temperature
        offsets are ignored, so K, °C, °F, and °R share the same dimension Θ
        and can be used interchangeably in expressions like J/(kg·K).

    Returns
    -------
    (dim, factor)
        dim    — 7-tuple [L M T I Θ N J]
        factor — converts one unit of *term* to the internal SI base
                 (g, m, s, A, K, mol, cd).
    """
    # --- Separate base symbol from exponent ---
    if '^' in term:
        unit_part, exp_str = term.split('^', 1)
        try:
            exponent = int(exp_str)
        except ValueError:
            exponent = float(exp_str)
    else:
        unit_part = term
        exponent = 1

    # --- Resolve unit + optional SI prefix ---
    _prefix, base_name, combined_factor = parse_unit_with_prefix(unit_part, unit_collection)

    if base_name is None:
        warnings.warn(
            f"Unit '{unit_part}' not found in unit collection; "
            f"treating as dimensionless with factor 1.0.",
            UserWarning,
            stacklevel=3,
        )
        base_name = unit_part
        combined_factor = 1.0

    # --- Block currencies ---
    category = _get_unit_category(base_name, unit_collection)
    if category == "Currency":
        raise ValueError(
            f"Currency unit '{base_name}' cannot appear in a compound expression."
        )

    # --- Resolve potentially ambiguous symbol to the correct dimension key ---
    dim_key = _resolve_dim_key(base_name, category)

    dim_base = base_dimensions.get(dim_key)
    if dim_base is None:
        warnings.warn(
            f"No dimensional vector defined for '{base_name}' (dim_key='{dim_key}'); "
            f"treating as dimensionless.",
            UserWarning,
            stacklevel=3,
        )
        dim_base = (0, 0, 0, 0, 0, 0, 0)

    # --- Apply exponent: prefix factor is raised to the same power (e.g. km³ → (1000)³) ---
    dim = _dim_scale(dim_base, exponent)
    factor = combined_factor ** exponent

    return dim, factor


def parse_compound_expression(expression: str,
                               unit_collection: dict = default_units) -> tuple:
    """Parse a compound unit expression and return (dim, factor_to_SI_base).

    The factor converts one unit of *expression* into the internal SI base
    system (g, m, s, A, K, mol, cd).

    Parameters
    ----------
    expression : str
        E.g. 'kg*m/s^2', 'J/(kg*K)', 'km^3', 'cal/(g*K)'.

    Returns
    -------
    (dim, factor)
        dim    — 7-tuple of ints  [L M T I Θ N J]
        factor — float
    """
    _check_no_currency(expression, unit_collection)
    tokens = tokenize_expression(expression)

    dim_acc    = (0, 0, 0, 0, 0, 0, 0)
    factor_acc = 1.0
    current_op = '*'

    for token in tokens:
        if token in ('*', '/'):
            current_op = token
        else:
            dim_t, factor_t = parse_term(token, unit_collection, as_difference=True)
            if current_op == '*':
                dim_acc     = _dim_add(dim_acc, dim_t)
                factor_acc *= factor_t
            else:
                dim_acc     = _dim_sub(dim_acc, dim_t)
                factor_acc /= factor_t

    return dim_acc, factor_acc


def simplify_expression(expression: str,
                         unit_collection: dict = default_units) -> Optional[List[str]]:
    """Match *expression* against all known named derived units with the same
    dimensional vector.

    Because multiple physically distinct quantities can share the same
    dimensional vector (e.g. Hz, rad/s, and Bq are all T⁻¹), this function
    returns the **full list** of matching names rather than a single string.

    Parameters
    ----------
    expression : str
        A compound unit expression, e.g. 'kg*m/s^2', 'J/(kg*K)', 's^-1'.

    Returns
    -------
    List[str] or None
        Ordered list of all matching unit / quantity names (e.g. ['Hz', 'rad/s', 'Bq']),
        or None if no match is found.
    """
    try:
        dim, _factor = parse_compound_expression(expression, unit_collection)
    except (ValueError, TypeError):
        return None
    return derived_units.get(dim)  # already a list, or None


def convert_compound(value: float, from_expression: str, to_expression: str,
                     unit_collection: dict = default_units) -> float:
    """Convert *value* between two dimensionally compatible compound expressions.

    Parameters
    ----------
    value : float
        Numeric value in *from_expression* units.
    from_expression : str
        Source compound expression, e.g. 'J/(kg*K)'.
    to_expression : str
        Target compound expression, e.g. 'cal/(g*K)'.

    Returns
    -------
    float — converted value in *to_expression* units.

    Raises
    ------
    ValueError
        If the two expressions have different physical dimensions.
    """
    dim_from, factor_from = parse_compound_expression(from_expression, unit_collection)
    dim_to,   factor_to   = parse_compound_expression(to_expression,   unit_collection)

    if dim_from != dim_to:
        raise ValueError(
            f"Dimensional mismatch: '{from_expression}' has dimensions {dim_from}, "
            f"but '{to_expression}' has dimensions {dim_to}."
        )

    # value × factor_from  → SI base value
    # SI base value / factor_to  → value in target units
    return value * factor_from / factor_to


def convert(value: float, from_unit: str, to_unit: str,
            unit_collection: dict = default_units) -> float:
    """Unified conversion for both simple and compound unit strings.

    Routes to *convert_compound* when either argument contains a compound
    operator (* / ^ · × ÷); otherwise delegates to *convert_units*.

    Parameters
    ----------
    value : float
        Numeric value to convert.
    from_unit : str
        Source unit — simple ('km') or compound ('km^3', 'J/(kg*K)').
    to_unit : str
        Target unit.

    Returns
    -------
    float — converted value.
    """
    if _is_compound(from_unit) or _is_compound(to_unit):
        return convert_compound(value, from_unit, to_unit, unit_collection)
    return convert_units(value, from_unit, to_unit, unit_collection)


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    while True:
        print("\n--- Unit Conversor Tester ---")
        print("1. Inspect unit / compound expression")
        print("2. Convert units (simple or compound)")
        print("3. Simplify compound expression")
        print("4. Get unit type")
        print("Type 'exit' to quit.")

        choice = input("Choice: ").strip()
        if choice == "exit":
            break

        if choice == "1":
            unit_str = input("Unit or expression (e.g. 'km', 'km^3', 'J/(kg*K)'): ").strip()
            if _is_compound(unit_str):
                try:
                    dim, factor = parse_compound_expression(unit_str)
                    print(f"  Dimensions : {dim}")
                    print(f"  SI factor  : {factor}")
                    simplified = simplify_expression(unit_str)
                    print(f"  Simplified : {simplified or '(no match)'}")
                except ValueError as err:
                    print(f"  Error: {err}")
            else:
                print(f"  parse_unit_with_prefix : {parse_unit_with_prefix(unit_str)}")
                print(f"  get_unit_type          : {get_unit_type(unit_str)}")
                print(f"  get_unit_info          : {get_unit_info(unit_str)}")

        elif choice == "2":
            try:
                val    = float(input("Value: "))
                from_u = input("From unit: ").strip()
                to_u   = input("To unit  : ").strip()
                result = convert(val, from_u, to_u)
                print(f"  {val} {from_u} = {result} {to_u}")
            except (ValueError, TypeError) as err:
                print(f"  Error: {err}")

        elif choice == "3":
            expr = input("Expression (e.g. 'kg*m/s^2'): ").strip()
            result = simplify_expression(expr)
            print(f"  Simplified: {result or '(no known derived unit)'}")

        elif choice == "4":
            unit_str = input("Unit (e.g. 'km/h', 'kg*m/s^2'): ").strip()
            try:
                unit_type = get_unit_type(unit_str)
                print(f"  Type: {unit_type or '(unknown)'}")
            except ValueError as err:
                print(f"  Error: {err}")