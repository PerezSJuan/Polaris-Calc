"""
smart_format.py
---------------
Formatea números grandes en notación científica compacta.

Reglas:
  - Solo se aplica si el número tiene MÁS dígitos que `max_chars`.
  - Evita resultados absurdos como "1e1" para 10 (que no ahorra espacio).
  - El output nunca supera `max_chars` caracteres (modo texto).
  - Soporta enteros y flotantes, positivos y negativos.
  - Modo LaTeX: devuelve  3.14 \times 10^{15}  (sin límite de chars,
    ya que LaTeX no se mide en caracteres visibles).

Uso:
    from smart_format import smart_format

    smart_format(2675353353535133)              # → "2.68e15"
    smart_format(2675353353535133, latex=True)  # → "2.68 \times 10^{15}"
    smart_format(1_000_000_000, latex=True)     # → "10^{9}"
    smart_format(42)                            # → "42"   (sin cambio)
    smart_format(10)                            # → "10"   (no ahorra nada)
"""

import math


def smart_format(
    number: int | float,
    max_chars: int = 7,
    latex: bool = False,
) -> str:
    """
    Devuelve una representación compacta de `number`.

    Parámetros
    ----------
    number    : El número a formatear (int o float).
    max_chars : Longitud máxima del string resultante en modo texto.
                En modo LaTeX controla la precisión de la mantisa
                (misma lógica de presupuesto de dígitos).
                Mínimo útil: 4  (e.g. "1e9")
    latex     : Si True, devuelve notación LaTeX: "M \times 10^{E}"
                Si la mantisa es exactamente 1, devuelve solo "10^{E}".

    Retorna
    -------
    str con la representación original si ya es suficientemente corta,
    o la notación científica en el formato pedido.
    """
    if max_chars < 3:
        raise ValueError("max_chars debe ser al menos 3.")

    # ── Representación original ──────────────────────────────────────────────
    original = str(number)
    negative = number < 0
    abs_number = abs(number)

    # Si ya cabe en modo texto, devolvemos tal cual
    if len(original) <= max_chars:
        return original

    # ── Cálculo del exponente ────────────────────────────────────────────────
    if abs_number == 0:
        return "0"

    exp = int(math.floor(math.log10(abs_number)))

    # ── Guardia temprana: exp <= 1 nunca ahorra espacio ──────────────────────
    if exp <= 1:
        return original

    # ── Presupuesto de caracteres para la mantisa ────────────────────────────
    sign_chars = 1 if negative else 0
    exp_str = str(exp)
    suffix_len = 1 + len(exp_str)  # "e" + dígitos del exp
    mantissa_budget = max_chars - sign_chars - suffix_len

    if mantissa_budget < 1:
        return original

    # ── Construcción de la mantisa ───────────────────────────────────────────
    decimals = max(mantissa_budget - 2, 0)  # -1 dígito entero, -1 punto
    mantissa_value = abs_number / (10**exp)

    if decimals == 0:
        mantissa_str = str(round(mantissa_value))
        if mantissa_str == "10":
            exp += 1
            exp_str = str(exp)
            mantissa_str = "1"
    else:
        mantissa_str = f"{mantissa_value:.{decimals}f}"
        if mantissa_str.startswith("10"):
            exp += 1
            exp_str = str(exp)
            suffix_len = 1 + len(exp_str)
            mantissa_budget = max_chars - sign_chars - suffix_len
            decimals = max(mantissa_budget - 2, 0)
            mantissa_value = abs_number / (10**exp)
            mantissa_str = (
                f"{mantissa_value:.{decimals}f}"
                if decimals > 0
                else str(round(mantissa_value))
            )

    # Eliminar ceros finales innecesarios
    if "." in mantissa_str:
        mantissa_str = mantissa_str.rstrip("0").rstrip(".")

    sign_str = "-" if negative else ""

    # ── Modo LaTeX ───────────────────────────────────────────────────────────
    if latex:
        if mantissa_str == "1":
            # 1 x 10^n  →  simplificar a  10^{n}
            return f"{sign_str}10^{{{exp_str}}}"
        return f"{sign_str}{mantissa_str} \\times 10^{{{exp_str}}}"

    # ── Modo texto ───────────────────────────────────────────────────────────
    scientific = f"{sign_str}{mantissa_str}e{exp_str}"

    if len(scientific) >= len(original):
        return original

    return scientific


# ── Demo ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    casos = [
        (2675353353535133, 7),
        (2675353353535133, 5),
        (2675353353535133, 9),
        (2675353353535133, 4),
        (1_000_000_000, 7),
        (10_000, 7),
        (999_999_999_999, 7),
        (42, 7),
        (10, 7),
        (100, 7),
        (-9_876_543_210, 8),
        (1.23456789e18, 8),
        (3.141592653589793, 7),
        (0, 7),
    ]

    print("── Modo texto ──────────────────────────────────────────────────")
    header = f"{'Número original':<25} {'max':<5} {'Resultado'}"
    print(header)
    print("─" * len(header))
    for num, width in casos:
        result = smart_format(num, width)
        saved = len(str(num)) - len(result)
        note = f"  ← {saved:+d} chars" if saved != 0 else "  ← sin cambio"
        print(f"{str(num):<25} {width:<5} {result}{note}")

    print()
    print("── Modo LaTeX ──────────────────────────────────────────────────")
    header = f"{'Número original':<25} {'max':<5} {'LaTeX'}"
    print(header)
    print("─" * len(header))
    for num, width in casos:
        result = smart_format(num, width, latex=True)
        print(f"{str(num):<25} {width:<5} {result}")
