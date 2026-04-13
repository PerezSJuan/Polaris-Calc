import re
import flet as ft
from flet_base.translations import instance_translation_manager as tm
from flet_base.components.inputs import dropdown, text_input
from flet_base.components.modals import modal
from flet_base.components.buttons import filled_btn, text_btn
from screens.editor.components.latex_dropdown import (
    get_latex_widget,
    latex_dropdown as make_latex_dropdown,
)


from screens.editor.utils.utils import load_default_units

default_units = load_default_units()

# ---------------------------------------------------------------------------
# SI prefix table
# Each entry: (latex_display, symbol, factor)
#   latex_display  -> option string rendered inside LatexDropdown
#   symbol         -> actual character(s) prepended to the unit (saved to pool)
#   factor         -> multiplicative factor relative to base unit (informational)
# ---------------------------------------------------------------------------
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

# Lookup helpers
_LATEX_TO_SYMBOL = {latex: sym for latex, sym, _ in SI_PREFIXES}
_SYMBOL_TO_LATEX = {sym: latex for latex, sym, _ in SI_PREFIXES}
_PREFIX_OPTIONS = [latex for latex, _, _ in SI_PREFIXES]
_NONE_LATEX = SI_PREFIXES[0][0]  # "--- (ninguno)" entry


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_unit(unit_str: str):
    """
    Resolves a possibly-prefixed unit string (e.g. 'km', 'muA', 'ms') to
    (magnitude, prefix_latex, base_unit).
    prefix_latex is the LaTeX display string used as the LatexDropdown value.
    Returns None if the unit cannot be matched.
    """
    # Exact match first (unit with no prefix)
    for mag, units in default_units.items():
        if unit_str in units:
            return mag, _NONE_LATEX, unit_str

    # Try stripping a known prefix (longer symbols first to avoid ambiguity)
    sorted_prefixes = sorted(
        ((sym, latex) for latex, sym, _ in SI_PREFIXES if sym),
        key=lambda x: -len(x[0]),
    )
    for sym, latex in sorted_prefixes:
        # Check both the symbol and common aliases (like 'u' for 'µ')
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
    """
    Splits 'Velocidad (km/h)' into ('Velocidad', 'km/h').
    Returns (name, '') if no parenthesized unit is found or if it's not a valid unit.
    The unit is always searched in the last parenthesis block to allow names like 'Prob (A) (%)'.
    """
    raw = raw.strip()
    # Match the LAST parentheses block. Greedy (.*) ensures we get the last one.
    match = re.fullmatch(r"(.*)\s*\(([^()]+)\)", raw)
    if match:
        name_part = match.group(1).strip()
        unit_part = match.group(2).strip()
        # Verify if it's a real unit before splitting
        if _resolve_unit(unit_part):
            return name_part, unit_part

    return raw, ""


def _set_prefix_enabled(prefix_dd, enabled: bool):
    """Visually enable/disable a LatexDropdown used as a prefix selector."""
    prefix_dd.opacity = 1.0 if enabled else 0.38
    prefix_dd.menu_button.disabled = not enabled
    try:
        prefix_dd.update()
    except RuntimeError:
        pass


def _build_prefix_dd(enabled: bool, value=None, on_change=None, width: int = 220):
    """Constructs a LatexDropdown for SI prefix selection."""
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
    """Returns the raw symbol (e.g. 'k', 'mu') for the selected prefix."""
    return _LATEX_TO_SYMBOL.get(prefix_dd.value, "")


def _full_unit(prefix_dd, unit_dd) -> str:
    """Combines prefix symbol + base unit into the string stored in pool."""
    base = unit_dd.value
    if not base or base == "none":
        return "none"
    return f"{_prefix_symbol(prefix_dd)}{base}"


# ---------------------------------------------------------------------------
# Modals
# ---------------------------------------------------------------------------


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
    name_field = text_input(
        placeholder=tm.translate("Nombre variable (ej: x, V1, Masa (kg)...)")
    )
    desc_field = text_input(
        placeholder=tm.translate("Descripcion (opcional)"), multiline=True, max_lines=3
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
        except RuntimeError:
            pass

    def on_unit_change(e):
        _refresh_prefix_state()

    mag_dropdown.on_change = on_mag_change
    unit_dropdown.on_change = on_unit_change

    def _apply_parsed_unit(unit_str: str):
        resolved = _resolve_unit(unit_str)
        if resolved is None:
            return  # ignore silently

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
            _apply_parsed_unit(unit_str)
            name_field.value = var_name
            try:
                name_field.update()
            except RuntimeError:
                pass

    name_field.on_blur = on_name_blur

    def save_new_column(e):
        raw_name = name_field.value.strip()
        var_name, unit_str = _parse_name_unit(raw_name)

        if unit_str:
            # Enforce unit settings if found in name even if blur didn't fire
            _apply_parsed_unit(unit_str)
            name_field.value = var_name
            try:
                name_field.update()
            except RuntimeError:
                pass

        if not var_name or var_name in pool:
            return

        pool[var_name] = {
            "values": [],
            "magnitude": mag_dropdown.value,
            "unit": _full_unit(prefix_dropdown, unit_dropdown),
            "description": desc_field.value.strip(),
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
        update_shared_state()

        try:
            columns_row.update()
        except RuntimeError:
            pass

        page.pop_dialog()
        try:
            page.update()
        except Exception:
            pass

    # Removed on_submit to prevent automatic closing on Enter
    # name_field.on_submit = save_new_column
    # desc_field.on_submit = save_new_column

    page.show_dialog(
        modal(
            title_str=tm.translate("Nueva columna de datos"),
            content=[
                name_field,
                desc_field,
                mag_dropdown,
                ft.Row(
                    [prefix_dropdown, unit_dropdown],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            actions=[
                filled_btn(tm.translate("Crear"), on_click=save_new_column),
                filled_btn(
                    tm.translate("Cancelar"), on_click=lambda _: page.pop_dialog()
                ),
            ],
        )
    )


async def open_rename_tab_modal(page, current_name, on_save):
    """Opens a modal to rename a tab."""
    rename_field = text_input(value=current_name, autofocus=True)

    def _on_save(e):
        new_name = rename_field.value.strip()
        if new_name:
            on_save(new_name)
        page.pop_dialog()

    # Removed on_submit to prevent automatic closing on Enter
    # rename_field.on_submit = _on_save

    page.show_dialog(
        modal(
            title_str=tm.translate("Renombrar pestana"),
            content=[rename_field],
            actions=[
                text_btn(
                    tm.translate("Cancelar"), on_click=lambda _: page.pop_dialog()
                ),
                text_btn(tm.translate("Guardar"), on_click=_on_save),
            ],
        )
    )


async def open_variable_settings_modal(page, var_name, pool, on_change):
    """
    Opens a modal to live-edit a variable's magnitude, prefix, unit and description.
    Restores existing prefixed units correctly (e.g. 'km' -> k + m).
    """
    entry = pool.get(var_name, {})

    existing_unit = entry.get("unit", "none")
    resolved = (
        _resolve_unit(existing_unit) if existing_unit not in ("none", "") else None
    )
    init_mag = resolved[0] if resolved else entry.get("magnitude", "none")
    init_prefix = resolved[1] if resolved else _NONE_LATEX
    init_base = resolved[2] if resolved else existing_unit

    # ── description ──────────────────────────────────────────────────────────

    def _on_desc_change(e):
        pool[var_name]["description"] = desc_field.value.strip()
        on_change()

    desc_field = ft.TextField(
        label=tm.translate("Descripcion"),
        value=entry.get("description", ""),
        on_change=_on_desc_change,
        border_radius=8,
        text_size=13,
        multiline=True,
        min_lines=1,
        max_lines=3,
    )

    # ── shared helpers ────────────────────────────────────────────────────────

    async def _unit_options(mag):
        base = [ft.DropdownOption("none")]
        if mag in ("none", "") or mag not in default_units:
            return base
        return base + [ft.DropdownOption(u) for u in default_units[mag]]

    def _commit_unit():
        pool[var_name]["unit"] = _full_unit(prefix_dropdown, unit_dropdown)
        on_change()

    def _refresh_prefix_state_s():
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

    # ── prefix dropdown ───────────────────────────────────────────────────────

    init_supports = init_base not in ("none", "") and default_units.get(
        init_mag, {}
    ).get(init_base, {}).get("use_prefixes", False)

    # LatexDropdown calls on_change with the selected value string directly
    def _on_prefix_change(val):
        _commit_unit()

    prefix_dropdown = _build_prefix_dd(
        enabled=init_supports,
        value=init_prefix,
        on_change=_on_prefix_change,
        width=150,
    )

    # ── unit dropdown ─────────────────────────────────────────────────────────

    def _on_unit_change(e):
        _refresh_prefix_state_s()

    unit_dropdown = dropdown(
        label=tm.translate("Unidad"),
        options=await _unit_options(init_mag),
        value=init_base,
        on_change=_on_unit_change,
    )

    # ── magnitude dropdown ────────────────────────────────────────────────────

    async def _on_mag_change(e):
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

    page.show_dialog(
        modal(
            title_str=tm.translate("Configuracion de Variable"),
            content=[
                ft.Row(
                    [
                        ft.Text(
                            f"{tm.translate('Variable')}:",
                            weight=ft.FontWeight.BOLD,
                        ),
                        get_latex_widget(var_name, size=14),
                    ],
                    spacing=5,
                ),
                desc_field,
                mag_dropdown,
                ft.Row(
                    [prefix_dropdown, unit_dropdown],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            actions=[
                filled_btn(
                    tm.translate("Cerrar"),
                    on_click=lambda _: page.pop_dialog(),
                ),
            ],
        )
    )
