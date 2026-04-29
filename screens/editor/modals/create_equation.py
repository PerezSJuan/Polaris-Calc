"""
Modal: Crear fórmula
Cubre únicamente los tipos de fórmula:
  · Fórmula sin error
  · Fórmula con error
La fórmula es obligatoria; las unidades se derivan automáticamente.
"""

import flet as ft
from flet_base.translations import instance_translation_manager as tm
from flet_base.components.inputs import dropdown, text_input
from flet_base.components.modals import modal
from flet_base.components.buttons import text_btn, filled_btn
from screens.editor.components.latex_dropdown import get_latex_widget
from utils.variable_types import (
    VARIABLE_TYPE_FORMULA_NO_ERROR,
    VARIABLE_TYPE_FORMULA_WITH_ERROR,
    VARIABLE_TYPE_LABELS,
)
from screens.editor.modals.utils import (
    _c,
    _section_header,
    _card,
    _parse_name_unit,
)

_FORMULA_TYPES = [
    VARIABLE_TYPE_FORMULA_NO_ERROR,
    VARIABLE_TYPE_FORMULA_WITH_ERROR,
]


async def open_create_formula_modal(
    page,
    pool,
    columns_row,
    on_column_data_changed,
    get_available_vars,
    refresh_all_dropdowns,
    update_shared_state,
    themes,
):
    t = themes.actual_theme
    acc = t.get("formula_accent", t["primary"])

    # ── Campos ────────────────────────────────────────────────────────────────
    name_field = text_input(
        placeholder=tm.translate("Nombre variable (ej: F, E_total...)")
    )
    desc_field = text_input(
        placeholder=tm.translate("Descripción (opcional)"),
        multiline=True,
        max_lines=3,
    )
    type_dropdown = dropdown(
        label=tm.translate("Tipo"),
        options=[
            ft.DropdownOption(
                key=vt,
                text=tm.translate(VARIABLE_TYPE_LABELS.get(vt, vt)),
            )
            for vt in _FORMULA_TYPES
        ],
        value=VARIABLE_TYPE_FORMULA_NO_ERROR,
    )
    formula_field = text_input(
        placeholder=tm.translate("Fórmula (ej: A * B + C)"),
    )

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
        name, _ = _parse_name_unit(raw)
        if not name:
            preview_container.visible = False
            try:
                preview_container.update()
            except RuntimeError:
                pass
            return
        has_special = any(c in name for c in ("^", "_", "\\"))
        lname = name if has_special else f"\\text{{{name}}}"
        new_widget = get_latex_widget(lname, size=16)
        preview_row.controls[1] = new_widget
        preview_container.visible = True
        try:
            preview_container.update()
        except RuntimeError:
            pass

    name_field.on_change = lambda e: _refresh_preview()

    # ── Aviso de unidades automáticas ─────────────────────────────────────────
    units_notice = ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=13, color=_c(0.40)),
                ft.Text(
                    tm.translate(
                        "Unidades calculadas automáticamente a partir de la fórmula."
                    ),
                    size=11,
                    color=_c(0.45),
                ),
            ],
            spacing=6,
        ),
        bgcolor=_c(0.03),
        border_radius=7,
        padding=ft.Padding(10, 6, 10, 6),
        border=ft.Border.all(1, _c(0.07)),
    )

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
        except RuntimeError:
            pass

    def _hide_error():
        error_banner.visible = False
        try:
            error_banner.update()
        except RuntimeError:
            pass

    def on_name_blur(e):
        raw = name_field.value or ""
        var_name, _ = _parse_name_unit(raw)
        name_field.value = var_name
        try:
            name_field.update()
        except RuntimeError:
            pass
        _refresh_preview()

    name_field.on_blur = on_name_blur

    # ── Contenido único (sin pasos) ───────────────────────────────────────────
    content_column = ft.Container(
        content=ft.Column(
            [
                _section_header(tm.translate("Identificación")),
                _card(name_field, preview_container),
                _section_header(tm.translate("Descripción")),
                _card(desc_field),
                _section_header(tm.translate("Tipo de fórmula")),
                _card(type_dropdown),
                _section_header(tm.translate("Fórmula")),
                _card(formula_field, units_notice),
            ],
            spacing=0,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=True,
    )

    # ── Guardar ───────────────────────────────────────────────────────────────
    def _save(e):
        _hide_error()
        raw_name = name_field.value.strip()
        var_name, _ = _parse_name_unit(raw_name)
        var_type = type_dropdown.value or VARIABLE_TYPE_FORMULA_NO_ERROR
        formula = (formula_field.value or "").strip()

        if not var_name:
            _show_error(tm.translate("El nombre no puede estar vacío."))
            return
        if var_name in pool:
            _show_error(tm.translate("Ya existe una variable con ese nombre."))
            return
        if not formula:
            _show_error(tm.translate("Debes ingresar una fórmula."))
            return

        pool[var_name] = {
            "values": [],
            "errors": [],
            "type": var_type,
            "magnitude": "none",
            "unit": "none",
            "description": desc_field.value.strip(),
            "formula": formula,
        }

        from screens.editor.components.column import EditableColumn

        new_col = EditableColumn(
            pool=pool,
            current_name=var_name,
            on_change=on_column_data_changed,
            available_vars_getter=get_available_vars,
            themes=themes,
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
        except RuntimeError:
            pass

        page.pop_dialog()
        try:
            page.update()
        except Exception:
            pass

    # ── Botón crear ───────────────────────────────────────────────────────────
    create_btn = filled_btn(
        tm.translate("Crear fórmula"),
        on_click=_save,
    )
    # ── Mostrar modal ─────────────────────────────────────────────────────────
    page.show_dialog(
        modal(
            title_str=tm.translate("Nueva fórmula"),
            content=[
                error_banner,
                content_column,
            ],
            actions=[
                text_btn(tm.translate("Cancelar"), on_click=lambda _: page.pop_dialog()),
                create_btn,
            ],
        )
    )