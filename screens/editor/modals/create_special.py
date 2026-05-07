"""
Modal: Datos especiales
Permite crear tipos booleanos:
  · Booleano (Constante)
  · Columna de booleanos
  · Función booleana (Fórmula)
"""

import flet as ft
from flet_base.translations import instance_translation_manager as tm
from flet_base.components.inputs import dropdown, text_input
from flet_base.components.modals import modal
from flet_base.components.buttons import text_btn, filled_btn
from screens.editor.components.latex_dropdown import get_latex_widget
from utils.variable_types import (
    VARIABLE_TYPE_BOOLEAN,
    VARIABLE_TYPE_BOOLEAN_COLUMN,
    VARIABLE_TYPE_LABELS,
    is_boolean_type,
)
from screens.editor.modals.utils import (
    _c,
    _section_header,
    _card,
    _parse_name_unit,
)


async def open_create_special_modal(
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
        placeholder=tm.translate("Nombre variable (ej: b1, b_alt...)")
    )
    desc_field = text_input(
        placeholder=tm.translate("Descripción (opcional)"),
        multiline=True,
        max_lines=3,
    )

    _SPECIAL_TYPES = [
        VARIABLE_TYPE_BOOLEAN,
        VARIABLE_TYPE_BOOLEAN_COLUMN,
    ]

    type_dropdown = dropdown(
        label=tm.translate("Tipo"),
        options=[
            ft.DropdownOption(
                key=vt,
                text=tm.translate(VARIABLE_TYPE_LABELS.get(vt, vt)),
            )
            for vt in _SPECIAL_TYPES
        ],
        value=VARIABLE_TYPE_BOOLEAN,
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
            except:
                pass
            return
        has_special = any(c in name for c in ("^", "_", "\\"))
        lname = name if has_special else f"\\text{{{name}}}"
        new_widget = get_latex_widget(lname, size=16)
        preview_row.controls[1] = new_widget
        preview_container.visible = True
        try:
            preview_container.update()
        except:
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
        except:
            pass

    def _hide_error():
        error_banner.visible = False
        try:
            error_banner.update()
        except:
            pass

    # ── Guardar ───────────────────────────────────────────────────────────────
    def _save(e):
        _hide_error()
        raw_name = name_field.value.strip()
        var_name, _ = _parse_name_unit(raw_name)
        var_type = type_dropdown.value

        if not var_name:
            _show_error(tm.translate("El nombre no puede estar vacío."))
            return
        if var_name in pool:
            _show_error(tm.translate("Ya existe una variable con ese nombre."))
            return

        pool[var_name] = {
            "values": [False] if var_type == VARIABLE_TYPE_BOOLEAN else [],
            "errors": [],
            "type": var_type,
            "magnitude": "none",
            "unit": "none",
            "description": desc_field.value.strip(),
            "formula": "",
        }

        from screens.editor.components.column import EditableColumn
        from screens.editor.components.boolean_column import BooleanColumn

        if is_boolean_type(var_type):
            new_col = BooleanColumn(
                pool=pool,
                current_name=var_name,
                on_change=on_column_data_changed,
                available_vars_getter=get_available_vars,
                themes=themes,
                on_manage=on_manage,
            )
        else:
            new_col = EditableColumn(
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
        except:
            pass

        page.pop_dialog()
        try:
            page.update()
        except:
            pass

    # ── Mostrar modal ─────────────────────────────────────────────────────────
    page.show_dialog(
        modal(
            title_str=tm.translate("Datos especiales (Booleanos)"),
            content=[
                error_banner,
                ft.Column(
                    [
                        _section_header(tm.translate("Identificación")),
                        _card(name_field, preview_container),
                        _section_header(tm.translate("Descripción")),
                        _card(desc_field),
                        _section_header(tm.translate("Tipo")),
                        _card(type_dropdown),
                    ],
                    spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            actions=[
                text_btn(tm.translate("Cancelar"), on_click=lambda _: page.pop_dialog()),
                filled_btn(tm.translate("Crear"), on_click=_save),
            ],
        )
    )
