import flet as ft
from flet_base.translations import instance_translation_manager as tm
from flet_base.components.inputs import dropdown
from flet_base.components.modals import modal
from flet_base.components.buttons import filled_btn
from screens.editor.components.latex_dropdown import (
    get_latex_widget,
)
from utils.variable_types import (
    VARIABLE_TYPE_LABELS,
    infer_variable_type,
    is_formula_type,
)
from screens.editor.modals.utils import (
    default_units,
    _NONE_LATEX,
    _c,
    _accent,
    _section_header,
    _card,
    _build_prefix_dd,
    _set_prefix_enabled,
    _resolve_unit,
    _full_unit,
)


async def open_variable_settings_modal(page, var_name, pool, on_change, themes):
    entry = pool.get(var_name, {})
    var_type = infer_variable_type(entry)
    formula = entry.get("formula", "")
    is_derived = (
        is_formula_type(var_type) and isinstance(formula, str) and formula.strip() != ""
    )

    existing_unit = entry.get("unit", "none")
    resolved = (
        _resolve_unit(existing_unit) if existing_unit not in ("none", "") else None
    )
    init_mag = resolved[0] if resolved else entry.get("magnitude", "none")
    init_prefix = resolved[1] if resolved else _NONE_LATEX
    init_base = resolved[2] if resolved else existing_unit

    v_type_label = tm.translate(VARIABLE_TYPE_LABELS.get(var_type, var_type))
    acc = _accent(var_type, themes)

    # ── Header card ───────────────────────────────────────────────────────────
    type_pill = ft.Container(
        content=ft.Text(
            v_type_label,
            size=9,
            weight=ft.FontWeight.W_700,
            color=ft.Colors.with_opacity(0.9, acc),
        ),
        bgcolor=ft.Colors.with_opacity(0.12, acc),
        border_radius=20,
        padding=ft.Padding(8, 3, 8, 3),
    )

    formula_pill = ft.Container(
        content=ft.Row(
            [
                ft.Text("ƒ", size=10, color=acc, weight=ft.FontWeight.BOLD),
                ft.Text(
                    formula,
                    size=10,
                    color=_c(0.65),
                    overflow=ft.TextOverflow.ELLIPSIS,
                    max_lines=1,
                ),
            ],
            spacing=5,
        ),
        bgcolor=ft.Colors.with_opacity(0.07, acc),
        border_radius=6,
        padding=ft.Padding(7, 3, 7, 3),
        visible=is_derived,
        width=160,
    )

    header_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [type_pill, ft.Container(expand=True), formula_pill],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Container(height=8),
                ft.Row(
                    [get_latex_widget(var_name, size=20)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=0,
        ),
        bgcolor=ft.Colors.with_opacity(0.06, acc),
        border=ft.Border(
            left=ft.BorderSide(3, ft.Colors.with_opacity(0.40, acc)),
            right=ft.BorderSide(1, ft.Colors.with_opacity(0.10, acc)),
            top=ft.BorderSide(1, ft.Colors.with_opacity(0.10, acc)),
            bottom=ft.BorderSide(1, ft.Colors.with_opacity(0.10, acc)),
        ),
        border_radius=10,
        padding=ft.Padding(14, 12, 14, 12),
    )

    # ── Description ───────────────────────────────────────────────────────────
    def _on_desc_change(e):
        pool[var_name]["description"] = desc_field.value.strip()
        on_change()

    desc_field = ft.TextField(
        label=tm.translate("Descripción"),
        value=entry.get("description", ""),
        on_change=_on_desc_change,
        border_radius=8,
        text_size=13,
        multiline=True,
        min_lines=2,
        max_lines=3,
    )

    # ── Unit helpers ──────────────────────────────────────────────────────────
    async def _unit_options(mag):
        base = [ft.DropdownOption("none")]
        if mag in ("none", "") or mag not in default_units:
            return base
        return base + [ft.DropdownOption(u) for u in default_units[mag]]

    def _commit_unit():
        if is_derived:
            return
        pool[var_name]["unit"] = _full_unit(prefix_dropdown, unit_dropdown)
        on_change()

    def _refresh_prefix_state_s():
        if is_derived:
            prefix_dropdown.value = _NONE_LATEX
            _set_prefix_enabled(prefix_dropdown, False)
            return
        mag = mag_dropdown.value
        unit = unit_dropdown.value
        supports = (
            unit != "none"
            and mag != "none"
            and default_units.get(mag, {}).get(unit, {}).get("use_prefixes", False)
        )
        if not supports:
            prefix_dropdown.value = _NONE_LATEX
        _set_prefix_enabled(prefix_dropdown, supports)
        _commit_unit()

    init_supports = init_base not in ("none", "") and default_units.get(
        init_mag, {}
    ).get(init_base, {}).get("use_prefixes", False)

    def _on_prefix_change(val):
        if is_derived:
            return
        _commit_unit()

    prefix_dropdown = _build_prefix_dd(
        enabled=init_supports,
        value=init_prefix,
        on_change=_on_prefix_change,
        width=150,
    )

    def _on_unit_change(e):
        if is_derived:
            return
        _refresh_prefix_state_s()

    unit_dropdown = dropdown(
        label=tm.translate("Unidad"),
        options=await _unit_options(init_mag),
        value=init_base,
        on_change=_on_unit_change,
    )

    async def _on_mag_change(e):
        if is_derived:
            return
        mag = mag_dropdown.value
        pool[var_name]["magnitude"] = mag
        unit_dropdown.options = await _unit_options(mag)
        unit_dropdown.value = "none"
        _refresh_prefix_state_s()
        try:
            unit_dropdown.update()
        except RuntimeError:
            pass

    mag_dropdown = dropdown(
        label=tm.translate("Magnitud"),
        options=[ft.DropdownOption("none")]
        + [ft.DropdownOption(m) for m in default_units],
        value=init_mag,
        on_change=_on_mag_change,
    )
    mag_dropdown.disabled = is_derived
    unit_dropdown.disabled = is_derived
    if is_derived:
        _set_prefix_enabled(prefix_dropdown, False)

    # Notice for derived vars
    derived_notice = ft.Container(
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
        visible=is_derived,
    )

    page.show_dialog(
        modal(
            title_str=tm.translate("Configuración de variable"),
            content=[
                header_card,
                _section_header(tm.translate("Descripción")),
                desc_field,
                _section_header(tm.translate("Unidad física")),
                _card(
                    ft.Row([mag_dropdown], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row(
                        [prefix_dropdown, unit_dropdown],
                        spacing=10,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    derived_notice,
                ),
            ],
            actions=[
                filled_btn(
                    tm.translate("Cerrar"), on_click=lambda _: page.pop_dialog()
                ),
            ],
        )
    )
