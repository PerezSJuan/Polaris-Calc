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
from utils.variable_types import (
    ALL_VARIABLE_TYPES,
    VARIABLE_TYPE_COLUMN_NO_ERROR,
    VARIABLE_TYPE_FORMULA_NO_ERROR,
    VARIABLE_TYPE_LABELS,
    infer_variable_type,
    is_formula_type,
)

from screens.editor.utils.utils import load_default_units

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


# ── Theme helpers (only use ft.Colors, ft.Container, ft.Text directly) ─────────


from flet_base.themes.themes import instance_themes as global_themes


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
        content=ft.Column(list(controls), spacing=8),
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


# ── Modal: Nueva columna ───────────────────────────────────────────────────────


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
                    ft.Row([prefix_dropdown, unit_dropdown], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
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
                text_btn(tm.translate("Cancelar"), on_click=lambda _: page.pop_dialog()),
                back_btn,
                next_btn,
                create_btn,
            ],
        )
    )


# ── Modal: Renombrar pestaña ───────────────────────────────────────────────────


async def open_rename_tab_modal(page, current_name, on_save):
    rename_field = text_input(value=current_name)

    # Live preview of the typed name
    preview_text = ft.Text(
        current_name or "…",
        size=15,
        weight=ft.FontWeight.W_500,
        text_align=ft.TextAlign.CENTER,
    )
    preview_box = ft.Container(
        content=preview_text,
        alignment=ft.Alignment.CENTER,
        bgcolor=_c(0.04),
        border_radius=8,
        padding=ft.Padding(12, 8, 12, 8),
        border=ft.Border.all(1, _c(0.08)),
    )

    def _on_change(e):
        preview_text.value = rename_field.value or "…"
        try:
            preview_text.update()
        except RuntimeError:
            pass

    rename_field.on_change = _on_change

    def _on_save(e):
        new_name = rename_field.value.strip()
        if new_name:
            on_save(new_name)
        page.pop_dialog()

    page.show_dialog(
        modal(
            title_str=tm.translate("Renombrar pestaña"),
            content=[
                rename_field,
                preview_box,
            ],
            actions=[
                text_btn(
                    tm.translate("Cancelar"), on_click=lambda _: page.pop_dialog()
                ),
                filled_btn(tm.translate("Guardar"), on_click=_on_save),
            ],
        )
    )


# ── Modal: Configuración de variable ──────────────────────────────────────────


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
                    ft.Row([prefix_dropdown, unit_dropdown], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
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