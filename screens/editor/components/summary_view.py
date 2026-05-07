import flet as ft
import asyncio
from flet_base.translations import instance_translation_manager as tm
from flet_base.components.texts import body, subtitle


from screens.editor.components.latex_dropdown import get_latex_widget
from utils.variable_types import (
    VARIABLE_TYPE_LABELS,
    infer_variable_type,
    is_formula_type,
    is_plot_type,
)


def _c(t, key, opacity=1.0):
    # Ensure t is a dict and has the key, else fallback to black
    col = t.get(key, "#000000") if isinstance(t, dict) else "#000000"
    try:
        return ft.Colors.with_opacity(opacity, col) if opacity < 1.0 else col
    except Exception:
        return "#000000"


def _type_accent(var_type: str, themes) -> str:
    t = getattr(themes, "actual_theme", {})
    vt = var_type.lower()
    if "formula" in vt:
        return t.get("formula_accent", t.get("primary", ft.Colors.BLUE))
    if "constant" in vt:
        return t.get("constant_accent", t.get("secondary", ft.Colors.BLUE))
    if "error" in vt:
        return t.get("error_accent", t.get("error", ft.Colors.BLUE))
    return t.get("primary", ft.Colors.BLUE)


from screens.editor.utils.utils import load_smart_format
_smart_format = load_smart_format()

def _fmt(v: float) -> str:
    import math
    if not math.isfinite(v):
        return str(v)
    return _smart_format(v, latex=True)


def _make_card(
    i: int,
    name: str,
    entry: dict,
    themes,
    on_open_settings,
    on_delete=None,
) -> ft.Container:
    t = getattr(themes, "actual_theme", themes if isinstance(themes, dict) else {})
    values = entry.get("values", [])
    count = len(values)
    magnitude = entry.get("magnitude", "none")
    unit = entry.get("unit", "none")
    description = entry.get("description", "")
    formula = entry.get("formula", "")
    var_type_key = infer_variable_type(entry)
    v_type = tm.translate(VARIABLE_TYPE_LABELS.get(var_type_key, var_type_key))
    derived = is_formula_type(var_type_key) and formula.strip()
    acc = _type_accent(var_type_key, themes)

    # ── index badge ───────────────────────────────────────────────────────────
    index_badge = ft.Container(
        content=ft.Text(
            str(i + 1),
            size=9,
            weight=ft.FontWeight.W_700,
            color=ft.Colors.with_opacity(0.9, acc),
        ),
        width=20,
        height=20,
        border_radius=5,
        bgcolor=ft.Colors.with_opacity(0.15, acc),
        alignment=ft.Alignment.CENTER,
    )

    # ── header row ────────────────────────────────────────────────────────────
    header_row = ft.Row(
        [
            ft.Row(
                [index_badge, get_latex_widget(name, size=17)], spacing=8, expand=True
            ),
            ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS_OUTLINED,
                        icon_size=16,
                        icon_color=_c(t, "on_surface", 0.35),
                        style=ft.ButtonStyle(padding=ft.Padding.all(2)),
                        on_click=(lambda n: lambda e: on_open_settings(n))(name)
                        if on_open_settings
                        else None,
                        tooltip=tm.translate("Configurar"),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                        icon_size=16,
                        icon_color=ft.Colors.RED_400,
                        style=ft.ButtonStyle(padding=ft.Padding.all(2)),
                        on_click=(lambda n: lambda e: on_delete(n))(name)
                        if on_delete
                        else None,
                        tooltip=tm.translate("Eliminar variable"),
                    ),
                ],
                spacing=2,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ── type pill ─────────────────────────────────────────────────────────────
    type_pill = ft.Container(
        content=ft.Text(
            v_type,
            size=9,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.with_opacity(0.85, acc),
        ),
        bgcolor=ft.Colors.with_opacity(0.10, acc),
        border_radius=20,
        padding=ft.Padding(8, 2, 8, 2),
    )

    # ── description ───────────────────────────────────────────────────────────
    desc = ft.Text(
        description if description else tm.translate("Sin descripción"),
        size=11,
        color=_c(t, "on_surface", 0.42 if not description else 0.65),
        italic=not bool(description),
        max_lines=2,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    # ── formula badge (derived only) ──────────────────────────────────────────
    formula_badge = ft.Container(
        visible=bool(derived),
        content=ft.Row(
            [
                ft.Text("ƒ", size=10, color=acc, weight=ft.FontWeight.BOLD),
                ft.Text(
                    formula,
                    size=10,
                    color=_c(t, "on_surface", 0.65),
                    overflow=ft.TextOverflow.ELLIPSIS,
                    max_lines=1,
                    expand=True,
                ),
            ],
            spacing=5,
        ),
        bgcolor=ft.Colors.with_opacity(0.07, acc),
        border_radius=5,
        padding=ft.Padding(7, 3, 7, 3),
    )

    # ── single value (only if exactly 1 numeric value) ────────────────────────
    single_nums = [v for v in values if isinstance(v, (int, float))]
    single_val_widget = ft.Container(
        visible=len(single_nums) == 1,
        content=ft.Row(
            [
                ft.Text(
                    _fmt(single_nums[0]) if single_nums else "",
                    size=22,
                    weight=ft.FontWeight.W_600,
                    color=_c(t, "on_surface", 0.90),
                ),
                ft.Text(
                    unit if unit != "none" else "",
                    size=12,
                    color=_c(t, "on_surface", 0.42),
                ),
            ],
            spacing=5,
            vertical_alignment=ft.CrossAxisAlignment.BASELINE,
        ),
    )

    # ── info chips row (n datos / magnitud / unidad) ──────────────────────────
    def info_chip(icon_name, label, value):
        return ft.Row(
            [
                ft.Icon(icon_name, size=13, color=_c(t, "on_surface", 0.35)),
                ft.Column(
                    [
                        ft.Text(
                            label,
                            size=9,
                            color=_c(t, "on_surface", 0.40),
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.Text(value, size=11, color=_c(t, "on_surface", 0.75)),
                    ],
                    spacing=0,
                ),
            ],
            spacing=5,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    n_label = "ƒ" if derived else str(count)
    mag_label = magnitude if magnitude != "none" else "—"
    unit_label = unit if unit != "none" else "—"

    chips_row = ft.Row(
        [
            info_chip(ft.Icons.NUMBERS_ROUNDED, tm.translate("Datos"), n_label),
            ft.Container(
                width=1, height=24, bgcolor=_c(t, "on_surface", 0.10)
            ),  # vertical divider
            info_chip(ft.Icons.STRAIGHTEN_ROUNDED, tm.translate("Magnitud"), mag_label),
            ft.Container(width=1, height=24, bgcolor=_c(t, "on_surface", 0.10)),
            info_chip(ft.Icons.SCIENCE_OUTLINED, tm.translate("Unidad"), unit_label),
        ],
        spacing=10,
        wrap=False,
    )

    # ── card body ─────────────────────────────────────────────────────────────
    body_col = ft.Column(
        [
            header_row,
            ft.Row([type_pill], alignment=ft.MainAxisAlignment.START),
            desc,
            formula_badge,
            single_val_widget,
            ft.Divider(height=8, thickness=0.5, color=_c(t, "on_surface", 0.09)),
            chips_row,
        ],
        spacing=7,
    )

    # ── card shell with accent strip ──────────────────────────────────────────
    return ft.Container(
        content=ft.Column(
            [
                ft.Container(  # 3-px accent top strip
                    height=3,
                    bgcolor=acc,
                    border_radius=ft.BorderRadius(15, 15, 0, 0),
                ),
                ft.Container(content=body_col, padding=14),
            ],
            spacing=0,
        ),
        width=230,
        border_radius=15,
        bgcolor=t["surface"],
        border=ft.Border(
            left=ft.BorderSide(3, ft.Colors.with_opacity(0.22, acc)),
            right=ft.BorderSide(1, _c(t, "on_surface", 0.05)),
            top=ft.BorderSide(1, _c(t, "on_surface", 0.05)),
            bottom=ft.BorderSide(1, _c(t, "on_surface", 0.05)),
        ),
        shadow=[
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                offset=ft.Offset(0, 3),
                color=ft.Colors.with_opacity(0.10, ft.Colors.BLACK),
            )
        ],
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )


def _make_plot_card(
    i: int,
    name: str,
    entry: dict,
    themes,
    on_open_settings,
    on_delete=None,
) -> ft.Container:
    t = getattr(themes, "actual_theme", themes if isinstance(themes, dict) else {})
    acc = t.get("formula_accent", t.get("primary", ft.Colors.BLUE))
    cfg = (entry.get("plot_config") or {}) if isinstance(entry, dict) else {}
    pt_label = str(cfg.get("plot_type", "plot")).capitalize()
    x_var = str(cfg.get("x_var", "—"))
    y_var = str(cfg.get("y_var", ""))
    reg = str(cfg.get("regression", "none"))
    description = str(entry.get("description", ""))
    reg_labels = {
        "none": "—",
        "linear": "Lineal",
        "poly2": "Grado 2",
        "poly3": "Grado 3",
    }

    index_badge = ft.Container(
        content=ft.Text(
            str(i + 1),
            size=9,
            weight=ft.FontWeight.W_700,
            color=ft.Colors.with_opacity(0.9, acc),
        ),
        width=20,
        height=20,
        border_radius=5,
        bgcolor=ft.Colors.with_opacity(0.15, acc),
        alignment=ft.Alignment.CENTER,
    )

    header_row = ft.Row(
        [
            ft.Row(
                [
                    index_badge,
                    ft.Icon(ft.Icons.SHOW_CHART_ROUNDED, size=16, color=acc),
                    ft.Text(
                        name,
                        size=14,
                        weight=ft.FontWeight.W_600,
                        color=_c(t, "on_surface"),
                        overflow=ft.TextOverflow.ELLIPSIS,
                        max_lines=1,
                    ),
                ],
                spacing=6,
                expand=True,
            ),
            ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS_OUTLINED,
                        icon_size=16,
                        icon_color=_c(t, "on_surface", 0.35),
                        style=ft.ButtonStyle(padding=ft.Padding.all(2)),
                        on_click=(lambda n: lambda e: on_open_settings(n))(name)
                        if on_open_settings
                        else None,
                        tooltip=tm.translate("Configurar"),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                        icon_size=16,
                        icon_color=ft.Colors.RED_400,
                        style=ft.ButtonStyle(padding=ft.Padding.all(2)),
                        on_click=(lambda n: lambda e: on_delete(n))(name)
                        if on_delete
                        else None,
                        tooltip=tm.translate("Eliminar variable"),
                    ),
                ],
                spacing=2,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    type_pill = ft.Container(
        content=ft.Text(
            f"Plot · {pt_label}",
            size=9,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.with_opacity(0.85, acc),
        ),
        bgcolor=ft.Colors.with_opacity(0.10, acc),
        border_radius=20,
        padding=ft.Padding(8, 2, 8, 2),
    )

    vars_str = f"{x_var} → {y_var}" if y_var else x_var
    vars_chip = ft.Row(
        [
            ft.Icon(
                ft.Icons.SWAP_HORIZ_ROUNDED, size=12, color=_c(t, "on_surface", 0.35)
            ),
            ft.Text(
                vars_str,
                size=10,
                color=_c(t, "on_surface", 0.60),
                overflow=ft.TextOverflow.ELLIPSIS,
                max_lines=1,
                expand=True,
            ),
        ],
        spacing=4,
    )

    desc_text = ft.Text(
        description if description else tm.translate("Sin descripción"),
        size=11,
        italic=not bool(description),
        color=_c(t, "on_surface", 0.42 if not description else 0.65),
        max_lines=2,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    chips_row = ft.Row(
        [
            ft.Row(
                [
                    ft.Icon(
                        ft.Icons.TRENDING_UP_ROUNDED,
                        size=12,
                        color=_c(t, "on_surface", 0.35),
                    ),
                    ft.Text(
                        tm.translate("Regresión"),
                        size=9,
                        color=_c(t, "on_surface", 0.40),
                        weight=ft.FontWeight.W_600,
                    ),
                ],
                spacing=3,
            ),
            ft.Text(
                tm.translate(reg_labels.get(reg, "—")),
                size=10,
                color=_c(t, "on_surface", 0.65),
            ),
        ],
        spacing=6,
    )

    body_col = ft.Column(
        [
            header_row,
            ft.Row([type_pill], alignment=ft.MainAxisAlignment.START),
            vars_chip,
            desc_text,
            ft.Divider(height=8, thickness=0.5, color=_c(t, "on_surface", 0.09)),
            chips_row,
        ],
        spacing=7,
    )

    return ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    height=3, bgcolor=acc, border_radius=ft.BorderRadius(15, 15, 0, 0)
                ),
                ft.Container(content=body_col, padding=14),
            ],
            spacing=0,
        ),
        width=230,
        border_radius=15,
        bgcolor=t.get("surface", "#1e1e1e"),
        border=ft.Border(
            left=ft.BorderSide(3, ft.Colors.with_opacity(0.22, acc)),
            right=ft.BorderSide(1, _c(t, "on_surface", 0.05)),
            top=ft.BorderSide(1, _c(t, "on_surface", 0.05)),
            bottom=ft.BorderSide(1, _c(t, "on_surface", 0.05)),
        ),
        shadow=[
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                offset=ft.Offset(0, 3),
                color=ft.Colors.with_opacity(0.10, ft.Colors.BLACK),
            )
        ],
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )


def SummaryView(pool, themes, on_open_settings=None, on_delete=None):
    t = getattr(themes, "actual_theme", themes if isinstance(themes, dict) else {})

    def _handle_open_settings(var_name):
        if on_open_settings:
            asyncio.create_task(on_open_settings(var_name))

    def _handle_delete(var_name):
        if on_delete:
            asyncio.create_task(on_delete(var_name))

    cards = []
    if isinstance(pool, dict):
        for i, (name, entry) in enumerate(pool.items()):
            try:
                var_type = infer_variable_type(entry)
                if is_plot_type(var_type):
                    cards.append(
                        _make_plot_card(
                            i,
                            name,
                            entry,
                            themes,
                            _handle_open_settings,
                            _handle_delete,
                        )
                    )
                else:
                    cards.append(
                        _make_card(
                            i,
                            name,
                            entry,
                            themes,
                            _handle_open_settings,
                            _handle_delete,
                        )
                    )
            except Exception as e:
                # Silently skip failed cards but log to console if possible
                print(f"Error rendering card for {name}: {e}")
                continue

    empty_state = ft.Container(
        content=ft.Column(
            [
                ft.Icon(
                    ft.Icons.INBOX_OUTLINED, size=52, color=_c(t, "on_surface", 0.18)
                ),
                ft.Text(
                    tm.translate("No hay variables en esta sesión"),
                    size=14,
                    color=_c(t, "on_surface", 0.32),
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
    )

    header = ft.Row(
        [
            ft.Icon(ft.Icons.GRID_VIEW_ROUNDED, color=t.get("primary", ft.Colors.BLUE), size=28),
            subtitle(tm.translate("Inventario de Variables"), size=22),
        ],
        spacing=15,
    )

    sub = body(
        tm.translate(
            "Vista general de todas las colecciones de datos en la sesión actual."
        ),
        size=13,
        color=t.get("on_surface", "#ffffff"),
    )

    return ft.Container(
        content=ft.Column(
            [
                header,
                sub,
                ft.Divider(height=30, thickness=1, color=_c(t, "on_surface", 0.10)),
                ft.Row(
                    controls=cards,
                    spacing=20,
                    run_spacing=20,
                    alignment=ft.MainAxisAlignment.START,
                    wrap=True,
                )
                if cards
                else empty_state,
            ],
            spacing=10,
        ),
        padding=30,
    )
