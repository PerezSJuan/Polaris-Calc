import os
import sys

import sympy as sp
from sympy.parsing.latex.lark import parse_latex_lark

# Add 'unit conversor' to path to allow importing its modules
# since the folder name contains a space
current_dir = os.path.dirname(os.path.abspath(__file__))
unit_conv_path = os.path.join(current_dir, "unit conversor")
if unit_conv_path not in sys.path:
    sys.path.append(unit_conv_path)

from unit_conversor import convert, parse_compound_expression


# ============================================================
# CONSTANTS
# ============================================================

# Common physical and mathematical constants mapped to their values and SI units
CONSTANTS = {
    "e": (sp.E, "1"),  # Euler's number (dimensionless)
    "pi": (sp.pi, "1"),  # Pi (dimensionless)
    "G": (6.67430e-11, "m^3/(kg*s^2)"),  # Gravitational constant
    "c": (299792458, "m/s"),  # Speed of light in vacuum
    "h": (6.62607015e-34, "J*s"),  # Planck constant
    "kB": (1.380649e-23, "J/K"),  # Boltzmann constant
    "g0": (9.80665, "m/s^2"),  # Standard gravity
}


# ============================================================
# PARSER (NORMAL + LATEX)
# ============================================================


def parse_expression(expr: str, mode: str = "auto") -> sp.Expr:
    """Parses a string expression into a SymPy object (latex, sympy, or auto)."""
    if mode == "latex":
        return parse_latex_lark(expr)

    if mode == "sympy":
        return sp.sympify(expr)

    # Auto mode: try sympy first, fallback to latex
    try:
        return sp.sympify(expr)
    except Exception:
        return parse_latex_lark(expr)


# ============================================================
# DIMENSIONS (FAST CHECK)
# ============================================================


def get_dim(unit: str) -> dict:
    """Returns the dimensionality dictionary for a given unit string."""
    dims, _ = parse_compound_expression(unit)
    return dims


def same_dim(u1: str, u2: str) -> bool:
    """Returns True if two unit strings share the same physical dimensions."""
    return get_dim(u1) == get_dim(u2)


def combine_units(u1: str, u2: str, op: str) -> str:
    """Combines two units according to an operation ('*' or '/')."""
    if u2 == "1":
        return u1
    if u1 == "1":
        if op == "*":
            return u2
        elif op == "/":
            return f"1/{u2}"

    if op == "*":
        return f"{u1}*{u2}"
    elif op == "/":
        return f"{u1}/{u2}"
    else:
        raise ValueError(f"Unsupported operation: {op}")


# ============================================================
# RESOLUTION
# ============================================================


def resolve(name: str, variables: dict) -> tuple:
    """Resolves a symbol name to its (value, unit) from variables or constants."""
    if name in variables:
        return variables[name]

    if name in CONSTANTS:
        return CONSTANTS[name]

    raise ValueError(f"Undefined symbol: '{name}'")


# ============================================================
# DIMENSIONAL CHECK
# ============================================================


def check_dimensions(expr: sp.Expr, variables: dict) -> str:
    """Verifies that a SymPy expression is dimensionally consistent and returns result unit."""

    def _check(node):
        if isinstance(node, sp.Symbol):
            _, unit = resolve(str(node), variables)
            return unit

        elif isinstance(node, (sp.Number, sp.NumberSymbol)):
            return "1"  # Pure numbers and constants like pi are dimensionless

        elif isinstance(node, sp.Add):
            units = [_check(a) for a in node.args]
            base_unit = units[0]

            for u in units[1:]:
                if not same_dim(base_unit, u):
                    raise ValueError(
                        f"❌ Invalid sum: Cannot add quantities with incompatible dimensions ({base_unit} and {u})"
                    )

            return base_unit

        elif isinstance(node, sp.Mul):
            units = [_check(a) for a in node.args]
            result_unit = units[0]

            for u in units[1:]:
                result_unit = combine_units(result_unit, u, "*")

            return result_unit

        elif isinstance(node, sp.Pow):
            base_unit = _check(node.args[0])
            exponent = node.args[1]

            if not exponent.is_number:
                raise ValueError(
                    "Only numeric exponents are supported in dimensional analysis"
                )

            if base_unit == "1":
                return "1"

            exp_str = str(exponent)
            # Remove redundant .0 for integer exponents
            if float(exponent).is_integer():
                exp_str = str(int(float(exponent)))

            return f"{base_unit}^{exp_str}"

        elif isinstance(node, (sp.GreaterThan, sp.LessThan, sp.StrictGreaterThan, sp.StrictLessThan, sp.Equality, sp.Unequality)):
            return "bool"

        else:
            raise TypeError(f"Unsupported node type in dimensional check: {type(node)}")

    return _check(expr)


# ============================================================
# EVALUATION
# ============================================================


def evaluate(
    expr_input: str, variables: dict, target_unit: str = None, mode: str = "auto"
) -> tuple:
    """Evaluates an expression with unit tracking and optional target conversion."""
    expr = parse_expression(expr_input, mode)

    # ⚡ Pre-check dimensional consistency to catch invalid operations early
    check_dimensions(expr, variables)

    def _eval(node):
        if isinstance(node, sp.Symbol):
            val, unit = resolve(str(node), variables)
            return float(val), unit

        elif isinstance(node, (sp.Number, sp.NumberSymbol)):
            return float(node.evalf()), "1"

        elif isinstance(node, sp.Add):
            vals = [_eval(a) for a in node.args]
            base_val, base_unit = vals[0]

            # In summation, convert all subsequent operands to the base_unit before adding
            for v, u in vals[1:]:
                v_conv = convert(v, u, base_unit)
                base_val += v_conv

            return base_val, base_unit

        elif isinstance(node, sp.Mul):
            vals = [_eval(a) for a in node.args]

            val, unit = vals[0]
            # In multiplication, just multiply values and combine units
            for v, u in vals[1:]:
                val *= v
                unit = combine_units(unit, u, "*")

            return val, unit

            return val**exp, f"{unit}^{exp_str}"
        
        elif isinstance(node, (sp.GreaterThan, sp.LessThan, sp.StrictGreaterThan, sp.StrictLessThan, sp.Equality, sp.Unequality)):
            lhs_val, _ = _eval(node.lhs)
            rhs_val, _ = _eval(node.rhs)
            
            # Simple numeric comparison
            if isinstance(node, sp.GreaterThan): res = lhs_val >= rhs_val
            elif isinstance(node, sp.LessThan): res = lhs_val <= rhs_val
            elif isinstance(node, sp.StrictGreaterThan): res = lhs_val > rhs_val
            elif isinstance(node, sp.StrictLessThan): res = lhs_val < rhs_val
            elif isinstance(node, sp.Equality): res = lhs_val == rhs_val
            elif isinstance(node, sp.Unequality): res = lhs_val != rhs_val
            else: res = False
            
            return (1.0 if res else 0.0), "bool"

        else:
            raise TypeError(f"Unsupported node type in evaluation: {type(node)}")

    value, unit = _eval(expr)

    # Final conversion to requested target unit
    if target_unit:
        value = convert(value, unit, target_unit)
        unit = target_unit

    return value, unit


# ============================================================
# SYSTEM CONSTANTS
# ============================================================


def constant_in_system(name: str, target_unit: str) -> tuple:
    """Returns a built-in constant value converted to a specific target unit."""
    if name not in CONSTANTS:
        raise ValueError(f"Constant '{name}' not found.")

    val, base_unit = CONSTANTS[name]
    return convert(val, base_unit, target_unit), target_unit


if __name__ == "__main__":
    print("-" * 23)
    print("FUNCTION SUBSTITUTION CONSOLE")
    print("-" * 23)
    while True:
        try:
            expr_input = input("Enter expression: ")
            if expr_input.strip().lower() == "exit":
                break

            variables = {}
            while True:
                var_input = input(
                    "Enter variable (name=value unit) or 'done' to finish: "
                )
                if var_input.strip().lower() == "done":
                    break

                try:
                    name, value_str = var_input.split("=")
                    value_str = value_str.strip()
                    if " " in value_str:
                        value, unit = value_str.rsplit(" ", 1)
                        value = float(value)
                    else:
                        value = float(value_str)
                        unit = "1"
                    variables[name.strip()] = (value, unit)
                except ValueError:
                    print(
                        "Invalid variable format. Use 'name=value unit' or 'name=value'."
                    )

            target_unit = input("Enter target unit (optional): ").strip()
            if not target_unit:
                target_unit = None

            value, unit = evaluate(expr_input, variables, target_unit)
            print(f"Result: {value} {unit}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
