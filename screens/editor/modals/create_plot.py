"""
Modal: Crear plot
Configura un gráfico vinculado a variables del pool con múltiples series.

Estructura generada en el pool:
    pool[nombre] = {
        "type": "plot",
        "values": [], "errors": [],
        "magnitude": "none", "unit": "none",
        "description": "...",
        "formula": "",
        "plot_config": {
            "series": [
                {
                    "label": "Serie 1",
                    "plot_type": "scatter",
                    "x_var": "t",
                    "y_var": "v",
                    "x_err_var": "",
                    "y_err_var": "",
                    "color": "#1f77b4",
                    "linestyle": "-",
                    "marker": "o",
                    "linewidth": 1.5,
                },
            ],
            "title": "",
            "xlabel": "",
            "ylabel": "",
            "regression": "none",
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

_COLORS = [
    ("#1f77b4", "Azul"),
    ("#ff7f0e", "Naranja"),
    ("#2ca02c", "Verde"),
    ("#d62728", "Rojo"),
    ("#9467bd", "Púrpura"),
    ("#8c564b", "Marrón"),
    ("#e377c2", "Rosa"),
    ("#7f7f7f", "Gris"),
    ("#bcbd22", "Amarillo"),
    ("#17becf", "Cian"),
    ("#aec7e8", "Azul claro"),
    ("#ffbb78", "Naranja claro"),
    ("#98df8a", "Verde claro"),
    ("#ff9896", "Rojo claro"),
    ("#c5b0d5", "Lavanda"),
    ("#9edae5", "Cian claro"),
]

_LINESTYLES = [
    ("-", "Sólida (—)"),
    ("--", "Discontinua (--)"),
    ("-.", "Guión-punto (-.)"),
    (":", "Punteada (:)"),
    ("None", "Ninguna"),
]

_MARKERS = [
    ("o", "Círculo (o)"),
    ("s", "Cuadrado (s)"),
    ("^", "Triángulo (^)"),
    ("D", "Diamante (D)"),
    ("v", "Triángulo invertido (v)"),
    ("*", "Estrella (*)"),
    ("x", "X (x)"),
    ("+", "Cruz (+)"),
    (".", "Punto (.)"),
    ("|", "Línea vertical (|)"),
    ("_", "Línea horizontal (_)"),
    ("None", "Ninguno"),
]

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

    # ── Campos básicos ────────────────────────────────────────────────────────
    name_field = text_input(placeholder=tm.translate("Nombre del plot (ej: Gráfico v-t)"))
    desc_field = text_input(
        placeholder=tm.translate("Descripción (opcional)"),
        multiline=True, max_lines=2,
    )

    # ── Series dinámicas ──────────────────────────────────────────────────────
    series_container = ft.Column(spacing=12, scroll=ft.ScrollMode.AUTO)
    _series_data = []  # lista de dicts con los controles de cada serie

    def _build_series_widgets(series_idx: int):
        sv = available_vars
        var_opts_none = [ft.DropdownOption("—")] + [ft.DropdownOption(v) for v in sv]
        var_opts = [ft.DropdownOption(v) for v in sv] if sv else [ft.DropdownOption("—")]

        label_f = text_input(
            placeholder=tm.translate("Etiqueta (opcional)"),
        )
        pt_dd = dropdown(
            label=tm.translate("Tipo"),
            options=[ft.DropdownOption(key=k, text=tm.translate(la)) for k, la in _PLOT_TYPES],
            value="scatter"
        )
        x_dd = dropdown(
            label="X",
            options=var_opts,
            value=sv[0] if sv else "—"
        )
        y_dd = dropdown(
            label="Y",
            options=var_opts,
            value=sv[1] if len(sv) > 1 else (sv[0] if sv else "—")
        )
        x_err_dd = dropdown(label="X err", options=var_opts_none, value="—", )
        y_err_dd = dropdown(label="Y err", options=var_opts_none, value="—", )
        err_row = ft.Row([x_err_dd, y_err_dd], spacing=8, visible=False)

        c_dd = dropdown(
            label=tm.translate("Color"),
            options=[ft.DropdownOption(key=k, text=la) for k, la in _COLORS],
            value=_COLORS[series_idx % len(_COLORS)][0]
        )
        ls_dd = dropdown(
            label=tm.translate("Línea"),
            options=[ft.DropdownOption(key=k, text=la) for k, la in _LINESTYLES],
            value="-"
        )
        mk_dd = dropdown(
            label=tm.translate("Marca"),
            options=[ft.DropdownOption(key=k, text=la) for k, la in _MARKERS],
            value="o"
        )

        def _on_type_change(e):
            is_hist = pt_dd.value in _NEEDS_SINGLE
            y_dd.visible = not is_hist
            err_row.visible = pt_dd.value in _ALLOWS_ERRORS
            try:
                y_dd.update()
                err_row.update()
            except RuntimeError:
                pass

        pt_dd.on_change = _on_type_change
        _on_type_change(None)

        # Botón eliminar serie
        def _make_del_handler(idx):
            async def _del(e):
                if len(_series_data) <= 1:
                    return
                _series_data.pop(idx)
                _rebuild_series_list()
            return _del

        del_btn = ft.IconButton(
            icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
            icon_size=18,
            tooltip=tm.translate("Eliminar serie"),
            on_click=_make_del_handler(series_idx),
            icon_color=ft.Colors.RED_400,
            padding=ft.Padding.all(2),
        )

        return {
            "label_f": label_f,
            "pt_dd": pt_dd,
            "x_dd": x_dd,
            "y_dd": y_dd,
            "x_err_dd": x_err_dd,
            "y_err_dd": y_err_dd,
            "err_row": err_row,
            "c_dd": c_dd,
            "ls_dd": ls_dd,
            "mk_dd": mk_dd,
            "del_btn": del_btn,
            "widget": None,
        }

    def _make_series_card(idx: int, data: dict) -> ft.Container:
        header = ft.Row(
            [
                ft.Text(f"{tm.translate('Serie')} {idx + 1}", size=12, weight=ft.FontWeight.W_600, color=ft.Colors.with_opacity(0.75, t["on_surface"])),
                ft.Container(expand=True),
                data["del_btn"],
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Fila superior: label + tipo
        row1 = ft.Row([data["label_f"], data["pt_dd"]], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START)

        # Fila variables: X, Y
        row2 = ft.Row([data["x_dd"], data["y_dd"]], spacing=8, visible=not (data["pt_dd"].value in _NEEDS_SINGLE))

        # Fila errores
        row3 = data["err_row"]

        # Fila apariencia: color, línea, marca
        row4 = ft.Row([data["c_dd"], data["ls_dd"], data["mk_dd"]], spacing=8)

        card = ft.Container(
            content=ft.Column([header, row1, row2, row3, row4], spacing=6),
            bgcolor=ft.Colors.with_opacity(0.04, t["on_surface"]),
            border_radius=8,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.10, t["on_surface"])),
            padding=10,
        )
        data["widget"] = card
        return card

    def _rebuild_series_list():
        series_container.controls.clear()
        for i, sd in enumerate(_series_data):
            sd["del_btn"].on_click = _make_del_handler(i)
            series_container.controls.append(_make_series_card(i, sd))
        try:
            series_container.update()
        except RuntimeError:
            pass

    def _make_del_handler(idx):
        async def _del(e):
            if len(_series_data) <= 1:
                return
            _series_data.pop(idx)
            _rebuild_series_list()
        return _del

    # Serie inicial
    _series_data.append(_build_series_widgets(0))
    _rebuild_series_list()

    add_series_btn = text_btn(
        tm.translate("+ Añadir serie"),
        on_click=lambda e: _add_series(),
    )

    def _add_series():
        idx = len(_series_data)
        _series_data.append(_build_series_widgets(idx))
        _rebuild_series_list()

    series_section = ft.Container(
        content=ft.Column([
            ft.Text(tm.translate("Series"), size=13, weight=ft.FontWeight.W_600, color=ft.Colors.with_opacity(0.75, t["on_surface"])),
            series_container,
            ft.Row([add_series_btn], alignment=ft.MainAxisAlignment.CENTER),
        ], spacing=8),
    )

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
            series_section,
        ], spacing=4, scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        visible=True, expand=True,
    )

    step1 = ft.Container(
        content=ft.Column([
            _section_header(tm.translate("Etiquetas")),
            _card(title_field, xlabel_field, ylabel_field),
            _section_header(tm.translate("Análisis")),
            _card(regression_dd),
            _section_header(tm.translate("Estilo matplotlib")),
            _card(style_dd),
        ], spacing=4, scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        visible=False, expand=True,
    )

    # ── Dots ──────────────────────────────────────────────────────────────────
    def _dot(active):
        return ft.Container(width=24 if active else 8, height=8, border_radius=4,
                            bgcolor=acc if active else ft.Colors.with_opacity(0.20, t["on_surface"]))

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

        series_list = []
        for sd in _series_data:
            pt = sd["pt_dd"].value
            x_var = sd["x_dd"].value if sd["x_dd"].value != "—" else ""
            y_var = sd["y_dd"].value if (sd["y_dd"].value != "—" and pt not in _NEEDS_SINGLE) else ""
            x_err = sd["x_err_dd"].value if sd["x_err_dd"].value != "—" else ""
            y_err = sd["y_err_dd"].value if sd["y_err_dd"].value != "—" else ""
            label = sd["label_f"].value.strip() or f"{y_var or x_var} ({pt})"

            if not x_var:
                _show_error(tm.translate("Cada serie necesita una variable X."))
                return

            series_list.append({
                "label": label,
                "plot_type": pt,
                "x_var": x_var,
                "y_var": y_var,
                "x_err_var": x_err,
                "y_err_var": y_err,
                "color": sd["c_dd"].value,
                "linestyle": sd["ls_dd"].value if sd["ls_dd"].value != "None" else "",
                "marker": sd["mk_dd"].value if sd["mk_dd"].value != "None" else "",
                "linewidth": 1.5,
            })

        pool[plot_name] = {
            "values": [], "errors": [],
            "type": VARIABLE_TYPE_PLOT,
            "magnitude": "none", "unit": "none",
            "description": desc_field.value.strip(),
            "formula": "",
            "plot_config": {
                "series": series_list,
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
