import re
import flet as ft
from flet_base.translations import instance_translation_manager as tm
from flet_base.themes.themes import instance_themes as global_themes
from screens.editor.utils.utils import load_default_units
from screens.editor.components.latex_dropdown import (
    latex_dropdown as make_latex_dropdown,
)

default_units = load_default_units()

# ── SI prefix table ────────────────────────────────────────────────────────────
SI_PREFIXES = [
    ("\\text{--- (ninguno)}", "", 1e0),
    ("Y \\cdot 10^{24}\\ \\text{(yotta)}", "Y", 1e24),
    ("Z \\cdot 10^{21}\\ \\text{(zetta)}", "Z", 1e21),
    ("E \\cdot 10^{18}\\ \\text{(exa)}", "E", 1e18),
    ("P \\cdot 10^{15}\\ \\text{(peta)}", "P", 1e15),
    ("T \\cdot 10^{12}\\ \\text{(tera)}", "T", 1e12),
    ("G \\cdot 10^{9}\\ \\text{(giga)}", "G", 1e9),
    ("M \\cdot 10^{6}\\ \\text{(mega)}", "M", 1e6),
    ("k \\cdot 10^{3}\\ \\text{(kilo)}", "k", 1e3),
    ("h \\cdot 10^{2}\\ \\text{(hecto)}", "h", 1e2),
    ("da \\cdot 10^{1}\\ \\text{(deca)}", "da", 1e1),
    ("d \\cdot 10^{-1}\\ \\text{(deci)}", "d", 1e-1),
    ("c \\cdot 10^{-2}\\ \\text{(centi)}", "c", 1e-2),
    ("m \\cdot 10^{-3}\\ \\text{(mili)}", "m", 1e-3),
    ("\\mu \\cdot 10^{-6}\\ \\text{(micro)}", "µ", 1e-6),
    ("n \\cdot 10^{-9}\\ \\text{(nano)}", "n", 1e-9),
    ("p \\cdot 10^{-12}\\ \\text{(pico)}", "p", 1e-12),
    ("f \\cdot 10^{-15}\\ \\text{(femto)}", "f", 1e-15),
    ("a \\cdot 10^{-18}\\ \\text{(atto)}", "a", 1e-18),
    ("z \\cdot 10^{-21}\\ \\text{(zepto)}", "z", 1e-21),
    ("y \\cdot 10^{-24}\\ \\text{(yocto)}", "y", 1e-24),
]

_LATEX_TO_SYMBOL = {latex: sym for latex, sym, _ in SI_PREFIXES}
_SYMBOL_TO_LATEX = {sym: latex for latex, sym, _ in SI_PREFIXES}
_PREFIX_OPTIONS = [latex for latex, _, _ in SI_PREFIXES]
_NONE_LATEX = SI_PREFIXES[0][0]


# ── Theme helpers ─────────────────────────────────────────────────────────────

def _c(opacity, color=None):
    col = color if color else global_themes.actual_theme["on_surface"]
    return ft.Colors.with_opacity(opacity, col)


def _accent(var_type: str, themes) -> str:
    vt = var_type.lower()
    t = themes.actual_theme
    if "formula" in vt:
        return t.get("formula_accent", t["primary"])
    if "constant" in vt:
        return t.get("constant_accent", t["secondary"])
    if "error" in vt:
        return t.get("error_accent", t["error"])
    return t["primary"]


def _divider():
    return ft.Divider(height=1, thickness=1, color=_c(0.08))


def _section_header(text: str) -> ft.Container:
    """Slim uppercase label as section separator."""
    return ft.Container(
        content=ft.Text(
            text.upper(),
            size=10,
            weight=ft.FontWeight.W_700,
            color=_c(0.38),
        ),
        padding=ft.Padding(0, 10, 0, 2),
    )


def _card(*controls, padding=10) -> ft.Container:
    """Groups controls in a subtle tinted card."""
    return ft.Container(
        content=ft.Column(
            list(controls),
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor=_c(0.04),
        border_radius=10,
        border=ft.Border.all(1, _c(0.08)),
        padding=padding,
    )


# ── Internal unit helpers ──────────────────────────────────────────────────────

def _resolve_unit(unit_str: str):
    for mag, units in default_units.items():
        if unit_str in units:
            return mag, _NONE_LATEX, unit_str
    sorted_prefixes = sorted(
        ((sym, latex) for latex, sym, _ in SI_PREFIXES if sym),
        key=lambda x: -len(x[0]),
    )
    for sym, latex in sorted_prefixes:
        matches = [sym]
        if sym == "µ":
            matches.append("u")
        for m in matches:
            if unit_str.startswith(m):
                base = unit_str[len(m) :]
                for mag, units in default_units.items():
                    if base in units and units[base].get("use_prefixes", False):
                        return mag, latex, base
    return None


def _parse_name_unit(raw: str):
    raw = raw.strip()
    match = re.fullmatch(r"(.*)\s*\(([^()]+)\)", raw)
    if match:
        name_part = match.group(1).strip()
        unit_part = match.group(2).strip()
        if _resolve_unit(unit_part):
            return name_part, unit_part
    return raw, ""


def _set_prefix_enabled(prefix_dd, enabled: bool):
    prefix_dd.opacity = 1.0 if enabled else 0.38
    prefix_dd.menu_button.disabled = not enabled
    try:
        prefix_dd.update()
    except RuntimeError:
        pass


def _build_prefix_dd(enabled: bool, value=None, on_change=None, width: int = 220):
    init_val = value if value is not None else _NONE_LATEX
    dd = make_latex_dropdown(
        label=tm.translate("Prefijo SI"),
        options=_PREFIX_OPTIONS,
        value=init_val,
        on_change=on_change,
        width=width,
    )
    if not enabled:
        dd.opacity = 0.38
        dd.menu_button.disabled = True
    return dd


def _prefix_symbol(prefix_dd) -> str:
    return _LATEX_TO_SYMBOL.get(prefix_dd.value, "")


def _full_unit(prefix_dd, unit_dd) -> str:
    base = unit_dd.value
    if not base or base == "none":
        return "none"
    return f"{_prefix_symbol(prefix_dd)}{base}"
