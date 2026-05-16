"""
Modal: Crear Vector
Permite crear variables de tipo vector n-dimensional con soporte de magnitudes y unidades.
"""

import flet as ft
from flet_base.translations import instance_translation_manager as tm
from flet_base.components.inputs import dropdown, text_input
from flet_base.components.modals import modal
from flet_base.components.buttons import text_btn, filled_btn
from screens.editor.components.latex_dropdown import get_latex_widget
from utils.variable_types import (
    VARIABLE_TYPE_VECTOR,
)
from screens.editor.modals.utils import (
    default_units,
    _NONE_LATEX,
    _c,
    _section_header,
    _card,
    _parse_name_unit,
    _build_prefix_dd,
    _set_prefix_enabled,
    _resolve_unit,
    _full_unit,
)


async def open_create_vector_modal(
    page,
    pool,
    columns_row,
    on_column_data_changed,
    get_available_vars,
    refresh_all_dropdowns,
    update_shared_state,
    themes,
    on_manage=None,
):
    t = themes.actual_theme
    acc = t["primary"]

    # ── Campos ────────────────────────────────────────────────────────────────
    name_field = text_input(
        placeholder=tm.translate("Nombre variable (ej: v1, F_vec...)")
    )
    desc_field = text_input(
        placeholder=tm.translate("Descripción (opcional)"),
        multiline=True,
        max_lines=3,
    )

    # ── Spinner de dimensiones ────────────────────────────────────────────────
    dimensions_value = [2]  # contenedor mutable para el closure

    dims_display = ft.Text(
        str(dimensions_value[0]),
        size=24,
        weight="bold",
        text_align=ft.TextAlign.CENTER,
    )

    def _update_dims_display():
        dims_display.value = str(dimensions_value[0])
        try:
            dims_display.update()
        except Exception:
            pass

    def _increment_dims(e):
        dimensions_value[0] = min(dimensions_value[0] + 1, 10)
        _update_dims_display()

    def _decrement_dims(e):
        dimensions_value[0] = max(dimensions_value[0] - 1, 1)
        _update_dims_display()

    dims_spinner = ft.Row(
        [
            ft.IconButton(
                icon=ft.Icons.REMOVE,
                on_click=_decrement_dims,
                tooltip=tm.translate("Disminuir dimensiones"),
            ),
            ft.Container(
                content=dims_display,
                alignment=ft.Alignment.CENTER,
                width=60,
            ),
            ft.IconButton(
                icon=ft.Icons.ADD,
                on_click=_increment_dims,
                tooltip=tm.translate("Aumentar dimensiones"),
            ),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
    )
    
    mag_dropdown = dropdown(
        label=tm.translate("Magnitud"),
        options=[ft.DropdownOption("none")]
        + [ft.DropdownOption(m) for m in default_units],
        value="none",
    )
    prefix_dropdown = _build_prefix_dd(enabled=False, width=150)
    unit_dropdown = dropdown(
        label=tm.translate("Unidad"),
        options=[ft.DropdownOption("none")],
        value="none",
    )

    # ── Estado de paso ────────────────────────────────────────────────────────
    _step = [0]

    # ── Preview LaTeX ─────────────────────────────────────────────────────────
    preview_latex_widget = [get_latex_widget("", size=16)]
    preview_row = ft.Row(
        [
            ft.Icon(ft.Icons.PREVIEW_ROUNDED, size=13, color=_c(0.30)),
            preview_latex_widget[0],
        ],
        spacing=6,
        alignment=ft.MainAxisAlignment.CENTER,
    )
    preview_container = ft.Container(
        content=preview_row,
        bgcolor=_c(0.03),
        border_radius=8,
        padding=ft.Padding(10, 6, 10, 6),
        border=ft.Border.all(1, _c(0.07)),
        visible=False,
        height=42,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

    def _refresh_preview():
        raw = name_field.value or ""
        name, unit_str = _parse_name_unit(raw)
        if not name:
            preview_container.visible = False
            try:
                preview_container.update()
            except Exception:
                pass
            return
        has_special = any(c in name for c in ("^", "_", "\\"))
        lname = name if has_special else f"\\text{{{name}}}"
        expr = f"{lname} \\ (\\text{{{unit_str}}})" if unit_str else lname
        new_widget = get_latex_widget(expr, size=16)
        preview_row.controls[1] = new_widget
        preview_container.visible = True
        try:
            preview_container.update()
        except Exception:
            pass

    name_field.on_change = lambda e: _refresh_preview()

    # ── Banner de error ───────────────────────────────────────────────────────
    error_text_ctrl = ft.Text("", size=12, color=t["error"])
    error_banner = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, size=15, color=t["error"]),
                error_text_ctrl,
            ],
            spacing=6,
        ),
        bgcolor=ft.Colors.with_opacity(0.08, t["error"]),
        border_radius=8,
        padding=ft.Padding(10, 6, 10, 6),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.20, t["error"])),
        visible=False,
    )

    def _show_error(msg: str):
        error_text_ctrl.value = msg
        error_banner.visible = True
        try:
            error_banner.update()
        except Exception:
            pass

    def _hide_error():
        error_banner.visible = False
        try:
            error_banner.update()
        except Exception:
            pass

    # ── Helpers de unidad ─────────────────────────────────────────────────────
    def _supports_prefix():
        mag = mag_dropdown.value
        unit = unit_dropdown.value
        return (
            unit != "none"
            and mag != "none"
            and default_units.get(mag, {}).get(unit, {}).get("use_prefixes", False)
        )

    def _refresh_prefix_state():
        supports = _supports_prefix()
        if not supports:
            prefix_dropdown.value = _NONE_LATEX
        _set_prefix_enabled(prefix_dropdown, supports)

    def on_mag_change(e):
        mag = mag_dropdown.value
        unit_dropdown.options = [ft.DropdownOption("none")] + [
            ft.DropdownOption(u) for u in default_units.get(mag, {})
        ]
        unit_dropdown.value = "none"
        _refresh_prefix_state()
        try:
            unit_dropdown.update()
        except Exception:
            pass

    def on_unit_change(e):
        _refresh_prefix_state()

    mag_dropdown.on_change = on_mag_change
    unit_dropdown.on_change = on_unit_change

    def _apply_parsed_unit(unit_str: str):
        resolved = _resolve_unit(unit_str)
        if resolved is None:
            return
        mag, prefix_latex, base = resolved
        mag_dropdown.value = mag
        unit_dropdown.options = [ft.DropdownOption("none")] + [
            ft.DropdownOption(u) for u in default_units.get(mag, {})
        ]
        unit_dropdown.value = base
        prefix_dropdown.value = prefix_latex
        supports = default_units.get(mag, {}).get(base, {}).get("use_prefixes", False)
        _set_prefix_enabled(prefix_dropdown, supports)
        for ctrl in (mag_dropdown, unit_dropdown):
            try:
                ctrl.update()
            except Exception:
                pass

    def on_name_blur(e):
        raw = name_field.value or ""
        var_name, unit_str = _parse_name_unit(raw)
        if unit_str:
            _apply_parsed_unit(unit_str)
            name_field.value = var_name
            try:
                name_field.update()
            except Exception:
                pass
        _refresh_preview()

    name_field.on_blur = on_name_blur

    # ── Contenedores de pasos ─────────────────────────────────────────────────
    step0 = ft.Container(
        content=ft.Column(
            [
                _section_header(tm.translate("Identificación")),
                _card(name_field, preview_container),
                _section_header(tm.translate("Descripción")),
                _card(desc_field),
                _section_header(tm.translate("Dimensiones")),
                _card(dims_spinner),
            ],
            spacing=0,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        visible=True,
        expand=True,
    )

    step1 = ft.Container(
        content=ft.Column(
            [
                _section_header(tm.translate("Magnitud física")),
                _card(
                    ft.Row([mag_dropdown], alignment=ft.MainAxisAlignment.CENTER),
                ),
                _section_header(tm.translate("Unidad y prefijo SI")),
                _card(
                    ft.Row(
                        [prefix_dropdown, unit_dropdown],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ),
            ],
            spacing=0,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        visible=False,
        expand=True,
    )

    # ── Indicador de pasos ────────────────────────────────────────────────────
    def _dot(active: bool) -> ft.Container:
        return ft.Container(
            width=24 if active else 8,
            height=8,
            border_radius=4,
            bgcolor=acc if active else _c(0.20),
        )

    dots_row = ft.Row(
        [_dot(True), _dot(False)],
        spacing=6,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    def _refresh_dots():
        dots_row.controls = [_dot(_step[0] == i) for i in range(2)]
        try:
            dots_row.update()
        except Exception:
            pass

    # ── Botones de navegación ─────────────────────────────────────────────────
    back_btn = text_btn(
        tm.translate("← Atrás"),
        on_click=lambda e: _go_step0(e),
    )
    back_btn.visible = False

    next_btn = filled_btn(
        tm.translate("Siguiente →"),
        on_click=lambda e: _go_step1(e),
    )
    create_btn = filled_btn(
        tm.translate("Crear vector"),
        on_click=lambda e: _save(e),
    )
    create_btn.visible = False

    # ── Navegación ────────────────────────────────────────────────────────────
    def _go_step1(e):
        _hide_error()
        raw = name_field.value.strip()
        name, _ = _parse_name_unit(raw)
        if not name:
            _show_error(tm.translate("El nombre no puede estar vacío."))
            return
        if name in pool:
            _show_error(tm.translate("Ya existe una variable con ese nombre."))
            return
        _step[0] = 1
        step0.visible = False
        step1.visible = True
        back_btn.visible = True
        next_btn.visible = False
        create_btn.visible = True
        _refresh_dots()
        for ctrl in (step0, step1, back_btn, next_btn, create_btn):
            try:
                ctrl.update()
            except Exception:
                pass

    def _go_step0(e):
        _step[0] = 0
        step0.visible = True
        step1.visible = False
        back_btn.visible = False
        next_btn.visible = True
        create_btn.visible = False
        _refresh_dots()
        for ctrl in (step0, step1, back_btn, next_btn, create_btn):
            try:
                ctrl.update()
            except Exception:
                pass

    # ── Guardar ───────────────────────────────────────────────────────────────
    def _save(e):
        _hide_error()
        raw_name = name_field.value.strip()
        var_name, unit_str = _parse_name_unit(raw_name)

        if unit_str:
            _apply_parsed_unit(unit_str)
            name_field.value = var_name
            try:
                name_field.update()
            except Exception:
                pass

        if not var_name or var_name in pool:
            _show_error(tm.translate("Nombre vacío o ya existente."))
            return

        n = dimensions_value[0]
        pool[var_name] = {
            "values": [[]],
            "errors": [],
            "type": VARIABLE_TYPE_VECTOR,
            "magnitude": mag_dropdown.value,
            "unit": _full_unit(prefix_dropdown, unit_dropdown),
            "description": desc_field.value.strip(),
            "formula": "",
            "dimensions": n,
        }

        from screens.editor.components.vector_column import VectorColumn

        new_col = VectorColumn(
            pool=pool,
            current_name=var_name,
            on_change=on_column_data_changed,
            available_vars_getter=get_available_vars,
            themes=themes,
            on_manage=on_manage,
        )

        controls = columns_row.controls
        if controls and getattr(controls[-1], "data", None) == "add_button":
            controls.insert(-1, new_col)
        else:
            controls.append(new_col)

        refresh_all_dropdowns()
        on_column_data_changed()

        try:
            columns_row.update()
        except Exception:
            pass

        page.pop_dialog()
        try:
            page.update()
        except Exception:
            pass

    # ── Mostrar modal ─────────────────────────────────────────────────────────
    page.show_dialog(
        modal(
            title_str=tm.translate("Crear Vector"),
            content=[
                dots_row,
                error_banner,
                step0,
                step1,
            ],
            actions=[
                text_btn(
                    tm.translate("Cancelar"), on_click=lambda _: page.pop_dialog()
                ),
                back_btn,
                next_btn,
                create_btn,
            ],
        )
    )
