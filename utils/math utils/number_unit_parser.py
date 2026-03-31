"""
number_unit_parser.py
=====================
Parser y evaluador aritmético para strings con números en cualquier formato
y una unidad opcional.

USO RÁPIDO
----------
    from number_unit_parser import parse, evaluate

    parse("1.234,56 km")          # ParsedValue(value=1234.56, unit="km")
    evaluate("9,81 * 10 N")       # ParsedValue(value=98.1,    unit="N")
    evaluate("(3 + 2) * 20 €")    # ParsedValue(value=100.0,   unit="€")

FORMATOS DE NÚMERO SOPORTADOS
------------------------------
  "1,234.56"   → 1234.56   miles=coma,    decimal=punto
  "1.234,56"   → 1234.56   miles=punto,   decimal=coma
  "1 234,56"   → 1234.56   miles=espacio
  "1'234.56"   → 1234.56   miles=apóstrofe
  "3.14159"    → 3.14159   decimal=punto, sin separador de miles
  "3,14159"    → 3.14159   decimal=coma,  sin separador de miles
  "1.234"      → 1234      ambiguo → se asume miles
  "1.000.000"  → 1000000   varios separadores → miles
  "-3,14"      → -3.14     signo ASCII
  "−273.15"    → -273.15   signo tipográfico (U+2212)
  "1.5e3"      → 1500.0    notación científica
  "6.022e23"   → 6.022e23  idem

OPERADORES (en evaluate())
---------------------------
  + - * /  ^(potencia)  y paréntesis ( )
  También reconoce × y ÷ tipográficos.

POSICIÓN DE LA UNIDAD
---------------------
  Antes, después, pegada o con espacio: "$42", "42 km/h", "9,81 m/s²"
"""

import re
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Data class de resultado
# ---------------------------------------------------------------------------


@dataclass
class ParsedValue:
    raw: str
    value: float
    unit: Optional[str]

    def __repr__(self) -> str:
        u = f'"{self.unit}"' if self.unit else "None"
        return f"ParsedValue(value={self.value!r}, unit={u}, raw={self.raw!r})"


# ---------------------------------------------------------------------------
# Expresiones regulares compartidas
# ---------------------------------------------------------------------------

_NUM_RE = re.compile(
    r"""
    (?P<sign>[+\-])?
    (?P<integer>
        \d{1,3}
        (?:
            (?P<th>[,.\s'])
            \d{3}
            (?=[,.\s']\d{3}|\D|$)
        )*
    )
    (?:
        (?P<dec_sep>[,.\u066B\u2396])
        (?P<decimals>\d+)
    )?
    (?:[eE](?P<exp>[+\-]?\d+))?
    """,
    re.VERBOSE,
)

# Tokens de unidad: no empiezan por dígito ni por operadores/separadores
_UNIT_RE = re.compile(r"[^\d\s,.\'\+\-][^\s]*")
_UNIT_EXPR_RE = re.compile(r"[^\d\s,.\'\+\-\*\/\^\(\)][^\s\+\-\*\/\^\(\)]*")


# ---------------------------------------------------------------------------
# Núcleo: parsear un único número formateado
# ---------------------------------------------------------------------------


def _parse_num(m: re.Match) -> float:
    """Convierte un match de _NUM_RE en float."""
    sign_str = m.group("sign") or ""
    integer = m.group("integer")
    th_sep = m.group("th")
    dec_sep = m.group("dec_sep")
    decimals = m.group("decimals")
    exp_str = m.group("exp")

    # Regla A: exponente presente + separador único sin dec explícito → sep es decimal
    if exp_str and th_sep and not dec_sep:
        parts = re.split(re.escape(th_sep), integer)
        if len(parts) == 2:
            dec_sep, decimals, integer, th_sep = th_sep, parts[1], parts[0], None

    # Regla B: separador único con ≠3 dígitos detrás → es decimal
    elif th_sep and not dec_sep:
        parts = re.split(re.escape(th_sep), integer)
        if len(parts) == 2 and len(parts[-1]) != 3:
            dec_sep, decimals, integer, th_sep = th_sep, parts[1], parts[0], None

    clean_int = (
        re.sub(re.escape(th_sep), "", integer)
        if th_sep
        else re.sub(r"[\s']", "", integer)
    )
    num_str = sign_str + clean_int
    if dec_sep and decimals:
        num_str += "." + decimals
    if exp_str:
        num_str += "e" + exp_str
    return float(num_str)


# ---------------------------------------------------------------------------
# parse() — número + unidad
# ---------------------------------------------------------------------------


def parse(text: str) -> ParsedValue:
    """
    Parsea un string con número y unidad opcional.

    Raises:
        ValueError: si no se encuentra ningún número.
    """
    original = text
    normalized = (
        text.strip()
        .replace("\u2212", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
    )

    best_match, best_len = None, -1
    for m in _NUM_RE.finditer(normalized):
        if not any(c.isdigit() for c in m.group()):
            continue
        if (length := m.end() - m.start()) > best_len:
            best_match, best_len = m, length

    if best_match is None:
        raise ValueError(f"No se encontró ningún número en: {original!r}")

    value = _parse_num(best_match)

    num_start, num_end = best_match.span()
    before = normalized[:num_start].strip()
    after = normalized[num_end:].strip()

    unit_parts: list[str] = []
    for fragment in (before, after):
        if fragment:
            unit_parts.extend(_UNIT_RE.findall(fragment))

    return ParsedValue(
        raw=original,
        value=value,
        unit=" ".join(unit_parts).strip() or None,
    )


# ---------------------------------------------------------------------------
# evaluate() — expresión aritmética + unidad
# ---------------------------------------------------------------------------


def _normalize(text: str) -> str:
    return (
        text.replace("\u2212", "-")
        .replace("\u2013", "-")
        .replace("\u00d7", "*")
        .replace("\u00f7", "/")
        .replace("^", "**")
    )


def _tokenize(text: str) -> list:
    """
    Convierte la expresión en tokens:
      float                   → número ya parseado
      str                     → operador o paréntesis
      ("unit", str)           → token de unidad
    """
    tokens = []
    i = 0
    while i < len(text):
        c = text[i]

        if c == " ":
            i += 1
            continue

        if text[i : i + 2] == "**":
            tokens.append("**")
            i += 2
            continue

        if c in "+-*/()":
            tokens.append(c)
            i += 1
            continue

        # Intento de número
        if c.isdigit() or (c in "+-" and i + 1 < len(text) and text[i + 1].isdigit()):
            m = _NUM_RE.match(text, i)
            if m and any(ch.isdigit() for ch in m.group()):
                tokens.append(_parse_num(m))
                i = m.end()
                continue

        # Token de unidad
        um = _UNIT_EXPR_RE.match(text, i)
        if um:
            tokens.append(("unit", um.group()))
            i = um.end()
            continue

        i += 1  # carácter no reconocido

    return tokens


def _build_expr(tokens: list) -> tuple[str, Optional[str]]:
    expr_parts, unit_parts = [], []
    for tok in tokens:
        if isinstance(tok, tuple) and tok[0] == "unit":
            unit_parts.append(tok[1])
        elif isinstance(tok, float):
            expr_parts.append(repr(tok))
        else:
            expr_parts.append(str(tok))
    return " ".join(expr_parts), " ".join(unit_parts) or None


def evaluate(text: str) -> ParsedValue:
    """
    Evalúa una expresión aritmética simple con números en cualquier formato
    y una unidad opcional.

    Operadores soportados: + - * / ^ ( )
    También reconoce × y ÷ tipográficos.

    Si no hay operadores, delega en parse().

    Examples:
        evaluate("1.234,56 + 765,44 km")  → ParsedValue(value=2000.0, unit="km")
        evaluate("9,81 * 10 N")           → ParsedValue(value=98.1,   unit="N")
        evaluate("2^10 bits")             → ParsedValue(value=1024.0, unit="bits")
        evaluate("(3 + 2) * 20 €")        → ParsedValue(value=100.0,  unit="€")

    Raises:
        ValueError: si la expresión no puede evaluarse.
    """
    original = text.strip()

    # ¿Hay operadores reales? (ignorar posible signo inicial)
    body = re.sub(r"^[\s\+\-]", "", original)
    if not re.search(r"[\+\-\*\/\^]", body):
        return parse(original)

    tokens = _tokenize(_normalize(original))
    expr, unit = _build_expr(tokens)

    try:
        value = float(eval(expr, {"__builtins__": {}}))  # noqa: S307
    except Exception as exc:
        raise ValueError(f"No se pudo evaluar la expresión '{expr}': {exc}") from exc

    return ParsedValue(raw=original, value=value, unit=unit)


# ---------------------------------------------------------------------------
# Funciones de conveniencia
# ---------------------------------------------------------------------------


def parse_number(text: str) -> float:
    """Devuelve solo el valor numérico de parse()."""
    return parse(text).value


def parse_unit(text: str) -> Optional[str]:
    """Devuelve solo la unidad de parse()."""
    return parse(text).unit


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("═" * 72)
    print("  parse() — número + unidad, cualquier formato")
    print("═" * 72)

    parse_examples = [
        ("1.234,56 km", "miles=. decimal=,"),
        ("1,234.56 km", "miles=, decimal=."),
        ("1 234,56 km", "miles=espacio"),
        ("1'234.56 km", "miles=apóstrofe"),
        ("3.14159", "decimal=. sin miles"),
        ("3,14159", "decimal=, sin miles"),
        ("-3,14 °C", "negativo"),
        ("−273.15°C", "signo tipográfico"),
        ("$1,234.99", "símbolo delante"),
        ("€ 1.234,99", "símbolo + espacio"),
        ("£42", "libra sin espacio"),
        ("1.5e3 Hz", "científica"),
        ("6.022e23 mol⁻¹", "Avogadro"),
        ("1.38e-23 J/K", "e negativo"),
        ("42", "entero"),
        ("1.000.000", "millón puntos"),
        ("1,000,000", "millón comas"),
        ("9,81 m/s²", "aceleración"),
        ("60 km/h", "velocidad"),
        ("37,5 %", "porcentaje"),
    ]

    w1, w2, w3 = 22, 14, 12
    print(f"  {'Input':<{w1}} {'Value':>{w2}}  {'Unit':<{w3}} Nota")
    print("  " + "─" * (w1 + w2 + w3 + 22))
    for ex, nota in parse_examples:
        try:
            r = parse(ex)
            print(f"  {ex!r:<{w1}} {r.value:>{w2}.8g}  {r.unit or '—':<{w3}} {nota}")
        except ValueError as e:
            print(f"  {ex!r:<{w1}}  ERROR: {e}")

    print()
    print("═" * 72)
    print("  evaluate() — expresiones aritméticas")
    print("═" * 72)

    eval_examples = [
        ("1.234,56 + 765,44 km", "suma con formatos mixtos"),
        ("100 * 3,14 m²", "multiplicación"),
        ("1.000 / 4", "división"),
        ("2^10 bits", "potencia"),
        ("9,81 * 10 N", "física"),
        ("1.500 - 250,50 USD", "resta"),
        ("60 * 60 s", "segundos en 1 hora"),
        ("(3 + 2) * 20 €", "paréntesis"),
        ("3 + 1.5e3 Hz", "notación científica"),
        ("1.000 * 1.000", "sin unidad"),
        ("3,14159", "sin operadores → parse()"),
    ]

    print(f"  {'Input':<28} {'Value':>{w2}}  {'Unit':<{w3}} Nota")
    print("  " + "─" * (28 + w2 + w3 + 22))
    for ex, nota in eval_examples:
        try:
            r = evaluate(ex)
            print(f"  {ex!r:<28} {r.value:>{w2}.8g}  {r.unit or '—':<{w3}} {nota}")
        except ValueError as e:
            print(f"  {ex!r:<28}  ERROR: {e}")
