from __future__ import annotations

import re

import sympy as sp
from sympy.parsing.latex.lark import parse_latex_lark

from .ast_nodes import AddNode, CompareNode, FuncNode, MulNode, Node, NumberNode, PowNode, SymbolNode


def _preprocess_custom_latex(expr: str, operation_names: list[str]) -> str:
    normalized = expr
    for name in sorted(operation_names, key=len, reverse=True):
        if not name.startswith("\\"):
            continue
        bare = name[1:]
        normalized = re.sub(
            rf"{re.escape(name)}(?=\s*\()",
            rf"\\operatorname{{{bare}}}",
            normalized,
        )
    return normalized


def _fallback_custom_to_sympy(expr: str, operation_names: list[str]) -> str:
    normalized = expr.replace(r"\left", "").replace(r"\right", "")
    for name in sorted(operation_names, key=len, reverse=True):
        bare = name[1:] if name.startswith("\\") else name
        normalized = re.sub(rf"{re.escape(name)}(?=\s*\()", bare, normalized)
    normalized = re.sub(r"\\([A-Za-z]+)(?=\s*\()", r"\1", normalized)
    normalized = normalized.replace("{", "(").replace("}", ")")
    return normalized


def _fallback_locals(expr: str, operation_names: list[str]) -> dict[str, sp.Function]:
    locals_map = {
        (name[1:] if name.startswith("\\") else name): sp.Function(name[1:] if name.startswith("\\") else name)
        for name in operation_names
    }
    for found in re.findall(r"\\([A-Za-z]+)(?=\s*\()", expr):
        locals_map.setdefault(found, sp.Function(found))
    return locals_map


def parse_expression(expr: str, mode: str = "auto", operation_names: list[str] | None = None) -> sp.Expr:
    operation_names = operation_names or []
    if mode == "latex":
        prepared = _preprocess_custom_latex(expr, operation_names or [])
        try:
            return parse_latex_lark(prepared)
        except Exception:
            locals_map = _fallback_locals(expr, operation_names)
            return sp.sympify(_fallback_custom_to_sympy(expr, operation_names), locals=locals_map)
    if mode == "sympy":
        return sp.sympify(expr)
    try:
        return sp.sympify(expr)
    except Exception:
        prepared = _preprocess_custom_latex(expr, operation_names)
        try:
            return parse_latex_lark(prepared)
        except Exception:
            locals_map = _fallback_locals(expr, operation_names)
            return sp.sympify(_fallback_custom_to_sympy(expr, operation_names), locals=locals_map)


def _func_name(node: sp.Expr) -> str:
    name = getattr(node.func, "__name__", str(node.func))
    return rf"\{name}" if not name.startswith("\\") else name


def _fold_binary(node_type, args):
    current = args[0]
    for nxt in args[1:]:
        current = node_type([current, nxt])
    return current


def _sympy_to_ast(node: sp.Expr) -> Node:
    if isinstance(node, sp.Symbol):
        return SymbolNode(str(node))
    if isinstance(node, (sp.Number, sp.NumberSymbol)):
        value = complex(node.evalf()) if getattr(node, "is_complex", False) and not node.is_real else float(node.evalf())
        return NumberNode(value)
    if isinstance(node, sp.Add):
        return AddNode([_sympy_to_ast(arg) for arg in node.args])
    if isinstance(node, sp.Mul):
        return MulNode([_sympy_to_ast(arg) for arg in node.args])
    if isinstance(node, sp.Pow):
        return PowNode(_sympy_to_ast(node.args[0]), _sympy_to_ast(node.args[1]))
    if isinstance(node, (sp.GreaterThan, sp.LessThan, sp.StrictGreaterThan, sp.StrictLessThan, sp.Equality, sp.Unequality)):
        return CompareNode(node.rel_op, _sympy_to_ast(node.lhs), _sympy_to_ast(node.rhs))
    if getattr(node, "is_Function", False):
        return FuncNode(
            name=_func_name(node),
            latex_name=_func_name(node),
            args=[_sympy_to_ast(arg) for arg in node.args],
        )
    raise TypeError(f"Unsupported SymPy node type: {type(node)}")


def parse_latex_to_ast(expr: str, operation_names: list[str] | None = None) -> Node:
    parsed = parse_expression(expr, mode="latex", operation_names=operation_names)
    return _sympy_to_ast(parsed)
