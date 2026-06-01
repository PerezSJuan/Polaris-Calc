from __future__ import annotations

import sympy as sp
from sympy.parsing.latex.lark import parse_latex_lark


def _bars_to_abs(expr: str) -> str:
    normalized = expr.replace(r"\left", "").replace(r"\right", "")
    normalized = normalized.replace(r"\lvert", "|").replace(r"\rvert", "|")
    buffers: list[list[str]] = [[]]
    for ch in normalized:
        if ch == "|":
            if len(buffers) == 1:
                buffers.append([])
            else:
                inner = "".join(buffers.pop())
                buffers[-1].append(f"Abs({inner})")
            continue
        buffers[-1].append(ch)
    if len(buffers) != 1:
        return normalized
    return "".join(buffers[0])


def parse_latex(latex: str):
    try:
        return parse_latex_lark(latex)
    except Exception:
        return sp.sympify(_bars_to_abs(latex))


# DEMO
if __name__ == "__main__":
    while True:
        latex = input("Enter latex to parse (exit to quit): ")
        if latex == "exit":
            break
        print(parse_latex(latex))
