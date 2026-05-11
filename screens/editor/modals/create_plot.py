"""
Modal: Crear plot
Configura un gráfico vinculado a variables del pool.

Estructura generada en el pool:
    pool[nombre] = {
        "type": "plot",
        "values": [], "errors": [],
        "magnitude": "none", "unit": "none",
        "description": "...",
        "formula": "",
        "plot_config": {
            "plot_type": "scatter",
            "x_var": "t",
            "y_var": "v",
            "x_err_var": "",
            "y_err_var": "",
            "title": "",
            "xlabel": "",
            "ylabel": "",
            "regression": "none",   # "none" | "linear" | "poly2" | "poly3"
            "show_legend": True,
            "style": "default",
        },
    }
"""

import flet as ft
from flet_base.translations import instance_translation_manager as tm
from flet_base.components.inputs import dropdown, text_input
from flet_base.components.modals import modal
from flet_base.components.buttons import text_btn, filled_btn
from utils.variable_types import VARIABLE_TYPE_PLOT
from screens.editor.modals.utils import _c, _section_header, _card

_PLOT_TYPES = [
    ("scatter",      "Dispersión (scatter)"),
    ("line",         "Línea"),
    ("errorbar",     "Barras de error (errorbar)"),
    ("histogram",    "Histograma"),
    ("bar",          "Barras verticales"),
    ("barh",         "Barras horizontales"),
    ("step",         "Escalón (step)"),
    ("fill_between", "Área entre curvas"),
]

_REGRESSION_OPTIONS = [
    ("none",   "Sin regresión"),
    ("linear", "Lineal  (y = mx + b)"),
    ("poly2",  "Polinómica grado 2"),
    ("poly3",  "Polinómica grado 3"),
]

_STYLE_OPTIONS = [
    "default",
    "seaborn-v0_8",
    "seaborn-v0_8-darkgrid",
    "ggplot",
    "bmh",
    "dark_background",
    "fast",
    "grayscale",
]

_NEEDS_XY     = {"scatter", "line", "errorbar", "bar", "barh", "step", "fill_between"}
_NEEDS_SINGLE = {"histogram"}
_ALLOWS_ERRORS = {"errorbar"}


async def open_create_plot_modal(
    page,
    pool,
    columns_row,
    on_column_data_changed,
    get_available_vars,
    refresh_all_dropdowns,
    update_shared_state,
    themes,
    on_manage=None,
    shared=None,
):
    t = themes.actual_theme
    acc = t.get("formula_accent", t["primary"])

    available_vars = [v for v in get_available_vars() if pool.get(v, {}).get("type") != VARIABLE_TYPE_PLOT]
    var_opts_none = [ft.DropdownOption("—")] + [ft.DropdownOption(v) for v in available_vars]
    var_opts      = [ft.DropdownOption(v) for v in available_vars] if available_vars else [ft.DropdownOption("—")]

    # ── Campos básicos ────────────────────────────────────────────────────────
    name_field = text_input(placeholder=tm.translate("Nombre del plot (ej: Gráfico v-t)"))
    desc_field = text_input(
        placeholder=tm.translate("Descripción (opcional)"),
        multiline=True, max_lines=2,
    )

    # ── Tipo de gráfico ───────────────────────────────────────────────────────
    plot_type_dd = dropdown(
        label=tm.translate("Tipo de gráfico"),
        options=[ft.DropdownOption(key=k, text=tm.translate(label)) for k, label in _PLOT_TYPES],
        value="scatter",
    )

    # ── Variables ─────────────────────────────────────────────────────────────
    x_var_dd = dropdown(
        label=tm.translate("Variable X"),
        options=var_opts,
        value=available_vars[0] if available_vars else "—",
    )
    y_var_dd = dropdown(
        label=tm.translate("Variable Y"),
        options=var_opts,
        value=available_vars[1] if len(available_vars) > 1 else (available_vars[0] if available_vars else "—"),
    )
    x_err_dd = dropdown(label=tm.translate("Error en X (opcional)"), options=var_opts_none, value="—")
    y_err_dd = dropdown(label=tm.translate("Error en Y (opcional)"), options=var_opts_none, value="—")

    # ── Etiquetas ─────────────────────────────────────────────────────────────
    title_field  = text_input(placeholder=tm.translate("Título del gráfico (opcional)"))
    xlabel_field = text_input(placeholder=tm.translate("Etiqueta eje X (opcional)"))
    ylabel_field = text_input(placeholder=tm.translate("Etiqueta eje Y (opcional)"))

    # ── Regresión y estilo ────────────────────────────────────────────────────
    regression_dd = dropdown(
        label=tm.translate("Regresión"),
        options=[ft.DropdownOption(key=k, text=tm.translate(label)) for k, label in _REGRESSION_OPTIONS],
        value="none",
    )
    style_dd = dropdown(
        label=tm.translate("Estilo matplotlib"),
        options=[ft.DropdownOption(s) for s in _STYLE_OPTIONS],
        value="default",
    )

    # ── Visibilidad dinámica ──────────────────────────────────────────────────
    error_section     = ft.Container(content=ft.Row([x_err_dd, y_err_dd], spacing=10), visible=False)
    regression_section = ft.Container(content=regression_dd, visible=True)

    def _refresh_visibility():
        pt = plot_type_dd.value
        is_hist = pt in _NEEDS_SINGLE
        y_var_dd.visible = not is_hist
        error_section.visible = pt in _ALLOWS_ERRORS
        regression_section.visible = pt in _NEEDS_XY and not is_hist
        for ctrl in (y_var_dd, error_section, regression_section):
            try: ctrl.update()
            except RuntimeError: pass

    plot_type_dd.on_change = lambda e: _refresh_visibility()

    # ── Banner de error ───────────────────────────────────────────────────────
    error_text_ctrl = ft.Text("", size=12, color=t["error"])
    error_banner = ft.Container(
        content=ft.Row([ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, size=15, color=t["error"]), error_text_ctrl], spacing=6),
        bgcolor=ft.Colors.with_opacity(0.08, t["error"]),
        border_radius=8,
        padding=ft.Padding(10, 6, 10, 6),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.20, t["error"])),
        visible=False,
    )

    def _show_error(msg):
        error_text_ctrl.value = msg
        error_banner.visible = True
        try: error_banner.update()
        except RuntimeError: pass

    def _hide_error():
        error_banner.visible = False
        try: error_banner.update()
        except RuntimeError: pass

    # ── Pasos ─────────────────────────────────────────────────────────────────
    _step = [0]

    step0 = ft.Container(
        content=ft.Column([
            _section_header(tm.translate("Identificación")),
            _card(name_field),
            _section_header(tm.translate("Descripción")),
            _card(desc_field),
            _section_header(tm.translate("Tipo de gráfico")),
            _card(plot_type_dd),
            _section_header(tm.translate("Variables")),
            _card(ft.Row([x_var_dd, y_var_dd], spacing=10), error_section),
        ], spacing=0, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        visible=True, expand=True,
    )

    step1 = ft.Container(
        content=ft.Column([
            _section_header(tm.translate("Etiquetas")),
            _card(title_field, xlabel_field, ylabel_field),
            _section_header(tm.translate("Análisis")),
            _card(regression_section),
            _section_header(tm.translate("Estilo matplotlib")),
            _card(style_dd),
        ], spacing=0, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        visible=False, expand=True,
    )

    # ── Dots ──────────────────────────────────────────────────────────────────
    def _dot(active):
        return ft.Container(width=24 if active else 8, height=8, border_radius=4,
                            bgcolor=acc if active else _c(0.20))

    dots_row = ft.Row([_dot(True), _dot(False)], spacing=6, alignment=ft.MainAxisAlignment.CENTER)

    def _refresh_dots():
        dots_row.controls = [_dot(_step[0] == i) for i in range(2)]
        try: dots_row.update()
        except RuntimeError: pass

    # ── Botones ───────────────────────────────────────────────────────────────
    back_btn   = text_btn(tm.translate("← Atrás"),    on_click=lambda e: _go_step0())
    next_btn   = filled_btn(tm.translate("Siguiente →"), on_click=lambda e: _go_step1())
    create_btn = filled_btn(tm.translate("Crear plot"),  on_click=lambda e: _save())
    back_btn.visible   = False
    create_btn.visible = False

    def _go_step1():
        _hide_error()
        if not name_field.value.strip():
            _show_error(tm.translate("El nombre no puede estar vacío."))
            return
        if name_field.value.strip() in pool:
            _show_error(tm.translate("Ya existe una variable con ese nombre."))
            return
        if not available_vars:
            _show_error(tm.translate("No hay variables en el pool para graficar."))
            return
        _step[0] = 1
        step0.visible = False; step1.visible = True
        back_btn.visible = True; next_btn.visible = False; create_btn.visible = True
        _refresh_dots()
        for c in (step0, step1, back_btn, next_btn, create_btn):
            try: c.update()
            except RuntimeError: pass

    def _go_step0():
        _step[0] = 0
        step0.visible = True; step1.visible = False
        back_btn.visible = False; next_btn.visible = True; create_btn.visible = False
        _refresh_dots()
        for c in (step0, step1, back_btn, next_btn, create_btn):
            try: c.update()
            except RuntimeError: pass

    # ── Guardar ───────────────────────────────────────────────────────────────
    def _save():
        _hide_error()
        plot_name = name_field.value.strip()
        if not plot_name or plot_name in pool:
            _show_error(tm.translate("Nombre vacío o ya existente."))
            return

        pt    = plot_type_dd.value
        x_var = x_var_dd.value if x_var_dd.value != "—" else ""
        y_var = y_var_dd.value if (y_var_dd.value != "—" and pt not in _NEEDS_SINGLE) else ""
        x_err = x_err_dd.value if x_err_dd.value != "—" else ""
        y_err = y_err_dd.value if y_err_dd.value != "—" else ""

        if not x_var:
            _show_error(tm.translate("Selecciona al menos la variable X."))
            return

        pool[plot_name] = {
            "values": [], "errors": [],
            "type": VARIABLE_TYPE_PLOT,
            "magnitude": "none", "unit": "none",
            "description": desc_field.value.strip(),
            "formula": "",
            "plot_config": {
                "plot_type": pt,
                "x_var": x_var, "y_var": y_var,
                "x_err_var": x_err, "y_err_var": y_err,
                "title":  title_field.value.strip(),
                "xlabel": xlabel_field.value.strip(),
                "ylabel": ylabel_field.value.strip(),
                "regression":   regression_dd.value,
                "show_legend":  True,
                "style":        style_dd.value,
            },
        }

        from screens.editor.components.plot_column import PlotColumn
        new_col = PlotColumn(
            pool=pool,
            plot_name=plot_name,
            on_change=on_column_data_changed,
            themes=themes,
            on_manage=on_manage,
            shared=shared,
        )

        controls = columns_row.controls
        if controls and getattr(controls[-1], "data", None) == "add_button":
            controls.insert(-1, new_col)
        else:
            controls.append(new_col)

        refresh_all_dropdowns()
        on_column_data_changed()
        try: columns_row.update()
        except RuntimeError: pass

        page.pop_dialog()
        try: page.update()
        except Exception: pass

    # ── Mostrar modal ─────────────────────────────────────────────────────────
    page.show_dialog(
        modal(
            title_str=tm.translate("Nuevo plot"),
            content=[dots_row, error_banner, step0, step1],
            actions=[
                text_btn(tm.translate("Cancelar"), on_click=lambda _: page.pop_dialog()),
                back_btn, next_btn, create_btn,
            ],
        )
    )
