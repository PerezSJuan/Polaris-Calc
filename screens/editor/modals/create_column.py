import flet as ft
from flet_base.translations import instance_translation_manager as tm
from flet_base.components.inputs import dropdown, text_input
from flet_base.components.modals import modal
from flet_base.components.buttons import text_btn
from screens.editor.components.latex_dropdown import (
    get_latex_widget,
)
from utils.variable_types import (
    ALL_VARIABLE_TYPES,
    VARIABLE_TYPE_COLUMN_NO_ERROR,
    VARIABLE_TYPE_FORMULA_NO_ERROR,
    VARIABLE_TYPE_LABELS,
    is_formula_type,
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


async def open_create_column_modal(
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
    acc = t["primary"]

    # ── Fields ────────────────────────────────────────────────────────────────
    name_field = text_input(
        placeholder=tm.translate("Nombre variable (ej: x, V1, Masa (kg)...)")
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
            for vt in ALL_VARIABLE_TYPES
        ],
        value=VARIABLE_TYPE_COLUMN_NO_ERROR,
    )
    formula_field = text_input(
        placeholder=tm.translate("Fórmula (ej: A * B + C)"),
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

    # ── Step state ────────────────────────────────────────────────────────────
    _step = [0]  # mutable so inner functions can write it

    # ── Live LaTeX preview ────────────────────────────────────────────────────
    # Shown inside a Container whose visibility we toggle
    preview_latex_widget = [get_latex_widget("", size=16)]  # wrapped in list to replace

    preview_row = ft.Row(
        [
            ft.Icon(ft.Icons.PREVIEW_ROUNDED, size=13, color=_c(0.30)),
            preview_latex_widget[0],
        ],
        spacing=6,
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
            except RuntimeError:
                pass
            return
        # Build a raw LaTeX expression (no $$ — get_latex_widget adds them)
        has_special = any(c in name for c in ("^", "_", "\\"))
        lname = name if has_special else f"\\text{{{name}}}"
        if unit_str:
            expr = f"{lname} \\ (\\text{{{unit_str}}})"
        else:
            expr = lname
        # get_latex_widget wraps in $$ automatically when it sees backslash
        new_widget = get_latex_widget(expr, size=16)
        preview_row.controls[1] = new_widget
        preview_container.visible = True
        try:
            preview_container.update()
        except RuntimeError:
            pass

    name_field.on_change = lambda e: _refresh_preview()

    # ── Error banner ──────────────────────────────────────────────────────────
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

    # ── Step containers ───────────────────────────────────────────────────────
    formula_container = ft.Container(
        content=formula_field,
        visible=False,
    )

    step0 = ft.Container(
        content=ft.Column(
            [
                _section_header(tm.translate("Identificación")),
                _card(name_field, preview_container),
                _section_header(tm.translate("Descripción")),
                _card(desc_field),
                _section_header(tm.translate("Tipo")),
                _card(type_dropdown, formula_container),
            ],
            spacing=0,
            expand=True,
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
        ),
        visible=False,
        expand=True,
    )

    # ── Step indicator dots ───────────────────────────────────────────────────
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
        except RuntimeError:
            pass

    # ── Nav buttons (using plain ft.TextButton / ft.FilledButton since
    #    flet_base wrappers don't accept `visible`) ────────────────────────────
    def _make_nav_btn(label, on_click, filled=False):
        style = ft.ButtonStyle(
            bgcolor=acc if filled else None,
            color=t["on_primary"] if filled else t["text_color"],
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding(16, 8, 16, 8),
        )
        return (
            ft.Button(
                label,
                on_click=on_click,
                style=style,
            )
            if filled
            else ft.TextButton(
                label,
                on_click=on_click,
                style=ft.ButtonStyle(
                    color=t["text_color"],
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
            )
        )

    back_btn = ft.TextButton(
        tm.translate("← Atrás"),
        on_click=lambda e: _go_step0(e),
        style=ft.ButtonStyle(color=t["text_color"]),
        visible=False,
    )
    next_btn = ft.Button(
        tm.translate("Siguiente →"),
        on_click=lambda e: _go_step1(e),
        style=ft.ButtonStyle(
            bgcolor=acc,
            color=t["on_primary"],
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
    )
    create_btn = ft.Button(
        tm.translate("Crear variable"),
        on_click=lambda e: save_new_column(e),
        style=ft.ButtonStyle(
            bgcolor=acc,
            color=t["on_primary"],
            shape=ft.RoundedRectangleBorder(radius=8),
        ),
        visible=False,
    )

    # ── Logic helpers ─────────────────────────────────────────────────────────
    def _is_formula_selected():
        return is_formula_type(type_dropdown.value)

    def _supports_prefix():
        mag = mag_dropdown.value
        unit = unit_dropdown.value
        return (
            unit != "none"
            and mag != "none"
            and default_units.get(mag, {}).get(unit, {}).get("use_prefixes", False)
        )

    def _set_unit_controls_enabled(enabled: bool):
        mag_dropdown.disabled = not enabled
        unit_dropdown.disabled = not enabled
        if not enabled:
            mag_dropdown.value = "none"
            unit_dropdown.options = [ft.DropdownOption("none")]
            unit_dropdown.value = "none"
            prefix_dropdown.value = _NONE_LATEX
        _set_prefix_enabled(prefix_dropdown, enabled and _supports_prefix())
        for ctrl in (mag_dropdown, unit_dropdown):
            try:
                ctrl.update()
            except RuntimeError:
                pass

    def _refresh_prefix_state():
        if _is_formula_selected():
            prefix_dropdown.value = _NONE_LATEX
            _set_prefix_enabled(prefix_dropdown, False)
            return
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
        except RuntimeError:
            pass

    def on_unit_change(e):
        _refresh_prefix_state()

    mag_dropdown.on_change = on_mag_change
    unit_dropdown.on_change = on_unit_change

    def on_type_change(e):
        is_formula = _is_formula_selected()
        formula_container.visible = is_formula
        if not is_formula:
            formula_field.value = ""
        _set_unit_controls_enabled(not is_formula)
        try:
            formula_container.update()
        except RuntimeError:
            pass

    type_dropdown.on_change = on_type_change

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
            except RuntimeError:
                pass

    def on_name_blur(e):
        raw = name_field.value or ""
        var_name, unit_str = _parse_name_unit(raw)
        if unit_str:
            if not _is_formula_selected():
                _apply_parsed_unit(unit_str)
            name_field.value = var_name
            try:
                name_field.update()
            except RuntimeError:
                pass
        _refresh_preview()

    name_field.on_blur = on_name_blur

    # ── Step navigation ───────────────────────────────────────────────────────
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
        if _is_formula_selected() and not formula_field.value.strip():
            _show_error(tm.translate("Debes ingresar una fórmula para este tipo."))
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
            except RuntimeError:
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
            except RuntimeError:
                pass

    # ── Save ──────────────────────────────────────────────────────────────────
    def save_new_column(e):
        _hide_error()
        raw_name = name_field.value.strip()
        var_name, unit_str = _parse_name_unit(raw_name)
        var_type = type_dropdown.value or VARIABLE_TYPE_COLUMN_NO_ERROR
        formula = (formula_field.value or "").strip()

        if formula and not is_formula_type(var_type):
            var_type = VARIABLE_TYPE_FORMULA_NO_ERROR
            type_dropdown.value = var_type
            try:
                type_dropdown.update()
            except RuntimeError:
                pass

        is_derived = is_formula_type(var_type)

        if unit_str and not is_derived:
            _apply_parsed_unit(unit_str)
            name_field.value = var_name
            try:
                name_field.update()
            except RuntimeError:
                pass
        elif unit_str and is_derived:
            name_field.value = var_name
            try:
                name_field.update()
            except RuntimeError:
                pass

        if not var_name or var_name in pool:
            _show_error(tm.translate("Nombre vacío o ya existente."))
            return
        if is_derived and not formula:
            _show_error(tm.translate("Debes ingresar una fórmula para esta variable."))
            return

        pool[var_name] = {
            "values": [],
            "errors": [],
            "type": var_type,
            "magnitude": "none" if is_derived else mag_dropdown.value,
            "unit": "none"
            if is_derived
            else _full_unit(prefix_dropdown, unit_dropdown),
            "description": desc_field.value.strip(),
            "formula": formula if is_derived else "",
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

    # ── Show modal ────────────────────────────────────────────────────────────
    page.show_dialog(
        modal(
            title_str=tm.translate("Nueva variable"),
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
