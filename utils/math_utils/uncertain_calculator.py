import os
import sys
import sympy as sp
from sympy.parsing.latex.lark import parse_latex_lark

# Add 'unit_conversor' to path (same pattern as function_substitution.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
unit_conv_path = os.path.join(current_dir, "unit_conversor")
if unit_conv_path not in sys.path:
    sys.path.append(unit_conv_path)

from unit_conversor import convert, parse_compound_expression


# ============================================================
# CONSTANTS  (from function_substitution.py)
# ============================================================

CONSTANTS = {
    "e": (sp.E, "1"),
    "pi": (sp.pi, "1"),
    "G": (6.67430e-11, "m^3/(kg*s^2)"),
    "c": (299792458, "m/s"),
    "h": (6.62607015e-34, "J*s"),
    "kB": (1.380649e-23, "J/K"),
    "g0": (9.80665, "m/s^2"),
}

FEW_MEASURES_THRESHOLD = 4  # n <= this → covariance ignored


# ============================================================
# PARSER  (from function_substitution.py)
# ============================================================


def parse_expression(expr: str, mode: str = "auto") -> sp.Expr:
    """Parses a string expression into a SymPy object (latex, sympy, or auto)."""
    if mode == "latex":
        return parse_latex_lark(expr)
    if mode == "sympy":
        return sp.sympify(expr)
    try:
        return sp.sympify(expr)
    except Exception:
        return parse_latex_lark(expr)


# ============================================================
# UNIT HELPERS  (from function_substitution.py)
# ============================================================


def get_dim(unit: str) -> dict:
    dims, _ = parse_compound_expression(unit)
    return dims


def same_dim(u1: str, u2: str) -> bool:
    return get_dim(u1) == get_dim(u2)


def combine_units(u1: str, u2: str, op: str) -> str:
    if u2 == "1":
        return u1
    if u1 == "1":
        return u2 if op == "*" else f"1/{u2}"
    if op == "*":
        return f"{u1}*{u2}"
    if op == "/":
        return f"{u1}/{u2}"
    raise ValueError(f"Unsupported operation: {op}")


def resolve(name: str, variables: dict) -> tuple:
    if name in variables:
        return variables[name]
    if name in CONSTANTS:
        return CONSTANTS[name]
    raise ValueError(f"Undefined symbol: '{name}'")


# ============================================================
# DIMENSIONAL CHECK  (from function_substitution.py)
# ============================================================


def check_dimensions(expr: sp.Expr, variables: dict) -> str:
    def _check(node):
        if isinstance(node, sp.Symbol):
            _, unit = resolve(str(node), variables)
            return unit
        elif isinstance(node, (sp.Number, sp.NumberSymbol)):
            return "1"
        elif isinstance(node, sp.Add):
            units = [_check(a) for a in node.args]
            base_unit = units[0]
            for u in units[1:]:
                if not same_dim(base_unit, u):
                    raise ValueError(
                        f"Invalid sum: incompatible dimensions ({base_unit} vs {u})"
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
            exp_str = (
                str(int(float(exponent)))
                if float(exponent).is_integer()
                else str(exponent)
            )
            return f"{base_unit}^{exp_str}"
        else:
            raise TypeError(f"Unsupported node type: {type(node)}")

    return _check(expr)


# ============================================================
# EVALUATOR  (from function_substitution.py)
# ============================================================


def evaluate(
    expr_input: str,
    variables: dict,
    target_unit: str = None,
    mode: str = "auto",
) -> tuple:
    """Evaluates an expression with unit tracking and optional unit conversion."""
    expr = parse_expression(expr_input, mode)
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
            for v, u in vals[1:]:
                base_val += convert(v, u, base_unit)
            return base_val, base_unit
        elif isinstance(node, sp.Mul):
            vals = [_eval(a) for a in node.args]
            val, unit = vals[0]
            for v, u in vals[1:]:
                val *= v
                unit = combine_units(unit, u, "*")
            return val, unit
        elif isinstance(node, sp.Pow):
            val, unit = _eval(node.args[0])
            exp = float(node.args[1])
            if unit == "1":
                return val**exp, "1"
            exp_str = str(int(exp)) if float(exp).is_integer() else str(exp)
            return val**exp, f"{unit}^{exp_str}"
        else:
            raise TypeError(f"Unsupported node type: {type(node)}")

    value, unit = _eval(expr)
    if target_unit:
        value = convert(value, unit, target_unit)
        unit = target_unit
    return value, unit


# ============================================================
# COVARIANCE FROM SERIES
# ============================================================


def compute_covariance(
    series_i: list,
    series_j: list,
    unit_i: str,
    unit_j: str,
) -> tuple:
    """
    Computes the sample covariance between two series of equal length.

        σ_ij = Σ[(x_k - x̄)(y_k - ȳ)] / (n - 1)

    Args:
        series_i, series_j : lists of floats (same length, n > 1).
        unit_i, unit_j     : units of each series.

    Returns:
        (cov_value, cov_unit)
    """
    n = len(series_i)
    if n != len(series_j):
        raise ValueError("Series must have the same length to compute covariance.")
    if n < 2:
        raise ValueError("Need at least 2 points to compute covariance.")

    mean_i = sum(series_i) / n
    mean_j = sum(series_j) / n

    cov = sum((series_i[k] - mean_i) * (series_j[k] - mean_j) for k in range(n)) / (
        n - 1
    )
    cov_unit = combine_units(unit_i, unit_j, "*")

    return cov, cov_unit


# ============================================================
# CENTRAL VALUE FROM SERIES
# ============================================================


def series_mean(series: list) -> float:
    """Returns the arithmetic mean of a series."""
    return sum(series) / len(series)


# ============================================================
# FORMULA ERROR PROPAGATION  (few measures — no covariance)
# ============================================================


def compute_formula_error_few(
    formula_input: str,
    variables: list,
    var_data: dict,
    sigma_data: dict,
    target_unit: str = None,
    mode: str = "auto",
) -> dict:
    """
    Error propagation ignoring covariance terms (n <= FEW_MEASURES_THRESHOLD).

        σ²_f = Σ_i (∂f/∂x_i)² · σ²_i

    Args:
        formula_input : f as a SymPy or LaTeX string.
        variables     : ordered list of variable names.
        var_data      : {name: (value, unit)} — central values (typically means).
        sigma_data    : {name: (σ, unit)}     — pre-computed errors.
        target_unit   : optional unit for σ_f.
        mode          : parsing mode.

    Returns a dict with symbolic and numeric results.
    """
    formula_expr = parse_expression(formula_input, mode)
    syms = {v: sp.Symbol(v) for v in variables}

    partials_sym = {v: sp.diff(formula_expr, syms[v]) for v in variables}

    # Symbolic variance (no cross terms)
    sigma_syms = {v: sp.Symbol(f"sigma_{v}") for v in variables}
    variance_sym = sp.Integer(0)
    for v in variables:
        variance_sym += partials_sym[v] ** 2 * sigma_syms[v] ** 2

    # Numeric partials
    partial_values = {}
    partial_units = {}
    for v in variables:
        try:
            val, unit = evaluate(str(partials_sym[v]), var_data, mode="sympy")
            partial_values[v] = val
            partial_units[v] = unit
        except Exception as e:
            raise ValueError(f"Could not evaluate ∂f/∂{v} numerically: {e}")

    # Accumulate variance
    variance_value = 0.0
    variance_unit = None
    term_details = []

    for v in variables:
        dfdv_val, dfdv_unit = partial_values[v], partial_units[v]
        sigma_val, sigma_unit = sigma_data[v]

        term_val = (dfdv_val**2) * (sigma_val**2)
        term_unit = combine_units(
            f"{dfdv_unit}^2" if dfdv_unit != "1" else "1",
            f"{sigma_unit}^2" if sigma_unit != "1" else "1",
            "*",
        )

        term_details.append(
            {
                "var": v,
                "dfdv_val": dfdv_val,
                "dfdv_unit": dfdv_unit,
                "sigma_val": sigma_val,
                "sigma_unit": sigma_unit,
                "term_val": term_val,
                "term_unit": term_unit,
            }
        )

        if variance_unit is None:
            variance_unit = term_unit
            variance_value += term_val
        else:
            try:
                variance_value += convert(term_val, term_unit, variance_unit)
            except Exception:
                raise ValueError(
                    f"Dimensional mismatch: term for '{v}' has unit '{term_unit}', "
                    f"expected '{variance_unit}'"
                )

    sigma_f_value = variance_value**0.5
    sigma_f_unit = (
        f"({variance_unit})^(1/2)" if (variance_unit and variance_unit != "1") else "1"
    )

    if target_unit:
        sigma_f_value = convert(sigma_f_value, sigma_f_unit, target_unit)
        sigma_f_unit = target_unit

    return {
        "mode": "few",
        "formula_sym": formula_expr,
        "partials_sym": partials_sym,
        "partials_latex": {v: sp.latex(partials_sym[v]) for v in variables},
        "variance_sym": variance_sym,
        "variance_latex": sp.latex(variance_sym),
        "partial_values": partial_values,
        "partial_units": partial_units,
        "term_details": term_details,
        "cov_details": [],
        "variance_value": variance_value,
        "variance_unit": variance_unit,
        "sigma_f_value": sigma_f_value,
        "sigma_f_unit": sigma_f_unit,
    }


# ============================================================
# FORMULA ERROR PROPAGATION  (many measures — with covariance)
# ============================================================


def compute_formula_error_many(
    formula_input: str,
    variables: list,
    var_data: dict,
    sigma_data: dict,
    covariances: dict,
    target_unit: str = None,
    mode: str = "auto",
) -> dict:
    """
    Full error propagation including covariance terms (n > FEW_MEASURES_THRESHOLD).

        σ²_f = Σ_i (∂f/∂x_i)² · σ²_i
             + 2 · Σ_{i<j} (∂f/∂x_i)(∂f/∂x_j) · σ_{x_i x_j}

    Args:
        formula_input : f as a SymPy or LaTeX string.
        variables     : ordered list of variable names.
        var_data      : {name: (value, unit)} — central values (typically means).
        sigma_data    : {name: (σ, unit)}     — pre-computed errors.
        covariances   : {(vi, vj): (σ_ij, unit)} — sample covariances (all pairs required).
        target_unit   : optional unit for σ_f.
        mode          : parsing mode.

    Returns a dict with symbolic and numeric results.
    """
    formula_expr = parse_expression(formula_input, mode)
    syms = {v: sp.Symbol(v) for v in variables}

    partials_sym = {v: sp.diff(formula_expr, syms[v]) for v in variables}

    # Symbolic variance (with cross terms)
    sigma_syms = {v: sp.Symbol(f"sigma_{v}") for v in variables}
    cov_syms = {
        (vi, vj): sp.Symbol(f"sigma_{vi}{vj}")
        for i, vi in enumerate(variables)
        for vj in variables[i + 1 :]
    }
    variance_sym = sp.Integer(0)
    for v in variables:
        variance_sym += partials_sym[v] ** 2 * sigma_syms[v] ** 2
    for i, vi in enumerate(variables):
        for vj in variables[i + 1 :]:
            variance_sym += 2 * partials_sym[vi] * partials_sym[vj] * cov_syms[(vi, vj)]

    # Numeric partials
    partial_values = {}
    partial_units = {}
    for v in variables:
        try:
            val, unit = evaluate(str(partials_sym[v]), var_data, mode="sympy")
            partial_values[v] = val
            partial_units[v] = unit
        except Exception as e:
            raise ValueError(f"Could not evaluate ∂f/∂{v} numerically: {e}")

    # Accumulate diagonal variance terms
    variance_value = 0.0
    variance_unit = None
    term_details = []

    for v in variables:
        dfdv_val, dfdv_unit = partial_values[v], partial_units[v]
        sigma_val, sigma_unit = sigma_data[v]

        term_val = (dfdv_val**2) * (sigma_val**2)
        term_unit = combine_units(
            f"{dfdv_unit}^2" if dfdv_unit != "1" else "1",
            f"{sigma_unit}^2" if sigma_unit != "1" else "1",
            "*",
        )

        term_details.append(
            {
                "var": v,
                "dfdv_val": dfdv_val,
                "dfdv_unit": dfdv_unit,
                "sigma_val": sigma_val,
                "sigma_unit": sigma_unit,
                "term_val": term_val,
                "term_unit": term_unit,
            }
        )

        if variance_unit is None:
            variance_unit = term_unit
            variance_value += term_val
        else:
            try:
                variance_value += convert(term_val, term_unit, variance_unit)
            except Exception:
                raise ValueError(
                    f"Dimensional mismatch: term for '{v}' has unit '{term_unit}', "
                    f"expected '{variance_unit}'"
                )

    # Covariance cross terms
    cov_details = []
    for i, vi in enumerate(variables):
        for vj in variables[i + 1 :]:
            if (vi, vj) not in covariances:
                raise ValueError(
                    f"Missing covariance for pair ({vi}, {vj}). "
                    f"All pairs are required in many-measures mode."
                )
            cov_val, cov_unit = covariances[(vi, vj)]

            dfdvi_val, dfdvi_unit = partial_values[vi], partial_units[vi]
            dfdvj_val, dfdvj_unit = partial_values[vj], partial_units[vj]

            cross_val = 2.0 * dfdvi_val * dfdvj_val * cov_val
            cross_unit = combine_units(
                combine_units(
                    dfdvi_unit if dfdvi_unit != "1" else "1",
                    dfdvj_unit if dfdvj_unit != "1" else "1",
                    "*",
                ),
                cov_unit if cov_unit != "1" else "1",
                "*",
            )

            cov_details.append(
                {
                    "pair": (vi, vj),
                    "cross_val": cross_val,
                    "cross_unit": cross_unit,
                }
            )

            if variance_unit is not None:
                try:
                    variance_value += convert(cross_val, cross_unit, variance_unit)
                except Exception:
                    raise ValueError(
                        f"Dimensional mismatch in covariance term ({vi},{vj}): "
                        f"unit '{cross_unit}' vs accumulated '{variance_unit}'"
                    )

    sigma_f_value = variance_value**0.5
    sigma_f_unit = (
        f"({variance_unit})^(1/2)" if (variance_unit and variance_unit != "1") else "1"
    )

    if target_unit:
        sigma_f_value = convert(sigma_f_value, sigma_f_unit, target_unit)
        sigma_f_unit = target_unit

    return {
        "mode": "many",
        "formula_sym": formula_expr,
        "partials_sym": partials_sym,
        "partials_latex": {v: sp.latex(partials_sym[v]) for v in variables},
        "variance_sym": variance_sym,
        "variance_latex": sp.latex(variance_sym),
        "partial_values": partial_values,
        "partial_units": partial_units,
        "term_details": term_details,
        "cov_details": cov_details,
        "variance_value": variance_value,
        "variance_unit": variance_unit,
        "sigma_f_value": sigma_f_value,
        "sigma_f_unit": sigma_f_unit,
    }


# ============================================================
# DISPATCHER — entry point from series data
# ============================================================


def compute_formula_error_from_series(
    formula_input: str,
    variables: list,
    series: dict,
    sigma_data: dict,
    units: dict,
    target_unit: str = None,
    mode: str = "auto",
) -> dict:
    """
    Main entry point when measurement series are available.

    Automatically selects few/many mode based on n, computes means as central
    values, and (if many) computes all pairwise covariances from the series.

    Args:
        formula_input : f as a SymPy or LaTeX string.
        variables     : ordered list of variable names.
        series        : {name: [v1, v2, ..., vn]} — all series same length n.
        sigma_data    : {name: (σ, unit)} — pre-computed errors (one per variable).
        units         : {name: unit_str} — physical unit of each variable's measurements.
        target_unit   : optional unit for σ_f.
        mode          : parsing mode.

    Returns the result dict from compute_formula_error_few or _many,
    plus added keys: "n", "means", "covariances_computed".
    """
    # Validate all series have the same length
    lengths = {v: len(series[v]) for v in variables}
    if len(set(lengths.values())) != 1:
        raise ValueError(f"All series must have the same length. Got: {lengths}")

    n = lengths[variables[0]]

    # Central values = means of each series
    var_data = {v: (series_mean(series[v]), units[v]) for v in variables}

    if n <= FEW_MEASURES_THRESHOLD:
        result = compute_formula_error_few(
            formula_input=formula_input,
            variables=variables,
            var_data=var_data,
            sigma_data=sigma_data,
            target_unit=target_unit,
            mode=mode,
        )
        result["covariances_computed"] = None  # not applicable

    else:
        # Compute all pairwise sample covariances from the series
        covariances = {}
        covariances_computed = {}
        for i, vi in enumerate(variables):
            for vj in variables[i + 1 :]:
                cov_val, cov_unit = compute_covariance(
                    series[vi], series[vj], units[vi], units[vj]
                )
                covariances[(vi, vj)] = (cov_val, cov_unit)
                covariances_computed[(vi, vj)] = (cov_val, cov_unit)

        result = compute_formula_error_many(
            formula_input=formula_input,
            variables=variables,
            var_data=var_data,
            sigma_data=sigma_data,
            covariances=covariances,
            target_unit=target_unit,
            mode=mode,
        )
        result["covariances_computed"] = covariances_computed

    result["n"] = n
    result["means"] = {v: var_data[v][0] for v in variables}
    return result


# ============================================================
# PRETTY PRINT
# ============================================================


def print_result(result: dict, variables: list) -> None:
    W = 56
    SEP = "=" * W

    print(f"\n{SEP}")
    print(f"  f = {sp.latex(result['formula_sym'])}")
    mode_label = (
        (
            f"few measures (n={result['n']}, covariance ignored)"
            if result["mode"] == "few"
            else f"many measures (n={result['n']}, covariance included)"
        )
        if "n" in result
        else result["mode"]
    )
    print(f"  Mode: {mode_label}")
    print(SEP)

    if "means" in result:
        print("\n  ── Means (central values) ──")
        for v in variables:
            val, unit = result["means"][v], ""
            print(f"    {v}̄  =  {val:.6g}")

    print("\n  ── Partial derivatives (symbolic) ──")
    for v in variables:
        print(f"    ∂f/∂{v}  =  {result['partials_latex'][v]}")

    print("\n  ── Partial derivatives (numeric) ──")
    for v in variables:
        val = result["partial_values"][v]
        unit = result["partial_units"][v]
        unit_str = f" [{unit}]" if unit != "1" else ""
        print(f"    ∂f/∂{v}  =  {val:.6g}{unit_str}")

    if result.get("covariances_computed"):
        print("\n  ── Covariances (computed from series) ──")
        for (vi, vj), (cov_val, cov_unit) in result["covariances_computed"].items():
            unit_str = f" [{cov_unit}]" if cov_unit != "1" else ""
            print(f"    σ_{vi}{vj}  =  {cov_val:.6g}{unit_str}")

    print("\n  ── Variance terms (∂f/∂xᵢ)² · σ²ᵢ ──")
    for t in result["term_details"]:
        unit_str = f"  [{t['term_unit']}]" if t["term_unit"] != "1" else ""
        print(
            f"    var({t['var']})  =  "
            f"({t['dfdv_val']:.4g})² · ({t['sigma_val']:.4g})²"
            f"  =  {t['term_val']:.6g}{unit_str}"
        )

    for c in result["cov_details"]:
        vi, vj = c["pair"]
        unit_str = f"  [{c['cross_unit']}]" if c["cross_unit"] != "1" else ""
        print(
            f"    2·(∂f/∂{vi})·(∂f/∂{vj})·σ_{vi}{vj}  =  {c['cross_val']:.6g}{unit_str}"
        )

    var_unit_str = (
        f"  [{result['variance_unit']}]" if result["variance_unit"] != "1" else ""
    )
    print("\n  ── Result ──")
    print(f"    σ²_f  =  {result['variance_value']:.6g}{var_unit_str}")
    print(f"    σ_f   =  {result['sigma_f_value']:.6g}  [{result['sigma_f_unit']}]")
    print()


# ============================================================
# CONSOLE
# ============================================================


def _input_val_unit(prompt: str) -> tuple:
    """Reads 'value unit' or just 'value' from stdin."""
    raw = input(prompt).strip()
    if " " in raw:
        val_str, unit = raw.rsplit(" ", 1)
    else:
        val_str, unit = raw, "1"
    return float(val_str), unit


def _input_series(prompt: str) -> list:
    """Reads a space- or comma-separated list of floats."""
    raw = input(prompt).strip().replace(",", " ")
    return [float(x) for x in raw.split()]


if __name__ == "__main__":
    SEP = "-" * 56
    print(SEP)
    print("  FORMULA ERROR PROPAGATION")
    print(f"  n <= {FEW_MEASURES_THRESHOLD}: covariance ignored")
    print(f"  n >  {FEW_MEASURES_THRESHOLD}: covariance computed from series")
    print(SEP)
    print("  Values: 'value unit'  or  'value'")
    print("  Series: space- or comma-separated numbers")
    print(SEP)

    while True:
        try:
            print()
            formula_input = input(
                "Formula f (SymPy or LaTeX, 'exit' to quit): "
            ).strip()
            if formula_input.lower() == "exit":
                break

            vars_raw = input("Variable names (space-separated): ").strip()
            variables = vars_raw.split()
            if not variables:
                print("  ⚠ No variables entered.")
                continue

            # Series of measurements
            print("\n  Measurement series for each variable:")
            series = {}
            units = {}
            for v in variables:
                raw_series = _input_series(f"    {v} values: ")
                unit = input(f"    {v} unit (Enter = dimensionless): ").strip() or "1"
                series[v] = raw_series
                units[v] = unit

            # Pre-computed errors
            print("\n  Pre-computed error σ for each variable:")
            sigma_data = {}
            for v in variables:
                val, unit = _input_val_unit(f"    σ_{v} = ")
                sigma_data[v] = (val, unit)

            target_unit = (
                input("\n  Target unit for σ_f (Enter to skip): ").strip() or None
            )

            result = compute_formula_error_from_series(
                formula_input=formula_input,
                variables=variables,
                series=series,
                sigma_data=sigma_data,
                units=units,
                target_unit=target_unit,
            )

            print_result(result, variables)

        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\n  ❌ {e}")
