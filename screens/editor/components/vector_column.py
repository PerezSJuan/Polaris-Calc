import asyncio
import flet as ft
from flet_base.translations import instance_translation_manager as tm
import flet_base.components.texts as txt
from flet_base.components.inputs import dropdown
from screens.editor.components.latex_dropdown import latex_dropdown, get_latex_widget
from screens.editor.components.column import LatexCell
from utils.variable_types import (
    is_vector_type,
    is_constant_type,
    is_formula_type,
    infer_variable_type,
)

# ── Design tokens ──────────────────────────────────────────────────────────────
_CARD_W = 300
_PADDING = 15
_CARD_RADIUS = 12
_CELL_H = 35
_CELL_RADIUS = 6
_BTN_SPACE = 30


def _c(t, key, opacity=1.0):
    col = t[key]
    return ft.Colors.with_opacity(opacity, col) if opacity < 1.0 else col


def _type_accent(var_type: str, themes) -> str:
    vt = var_type.lower()
    t = themes.actual_theme
    if "formula" in vt:
        return t.get("formula_accent", t["primary"])
    if "constant" in vt:
        return t.get("constant_accent", t["secondary"])
    if "error" in vt:
        return t.get("error_accent", t["error"])
    if "bool" in vt:
        return t.get("boolean_accent", t["tertiary"])
    if "vector" in vt:
        return t.get("vector_accent", ft.Colors.GREEN)
    return t["primary"]


class VectorRow(ft.Container):
    """
    A row for vector with n cells.
    """

    def __init__(self, values, n, themes, on_change, read_only=False):
        super().__init__()
        self.values = values if values else ["0"] * n
        self.n = n
        self.themes = themes
        self._on_change_cb = on_change
        self.read_only = read_only

        self._build_ui()

    def _build_ui(self):
        cells = []
        for i in range(self.n):
            cell = LatexCell(
                value=self.values[i] if i < len(self.values) else "0",
                themes=self.themes,
                on_change=lambda v, idx=i: self._on_cell_change(idx, v),
                read_only=self.read_only,
                compact=True,
            )
            cells.append(cell)

        self.content = ft.Row(
            cells,
            spacing=4,
            alignment=ft.MainAxisAlignment.START,
        )

    def _on_cell_change(self, idx, value):
        self.values[idx] = value
        if self._on_change_cb:
            self._on_change_cb(self.values)


class VectorColumn(ft.Container):
    """
    Data-column card for n-dimensional vectors.

    • Same 180 px width as original — tiles side by side correctly.
    • Expands vertically to fill available space (rows area grows, stats pinned at bottom).
    • Accent strip (3 px, colour-coded by type) at the top.
    • Formula badge when derived.
    • Stats strip (n / μ / σ) pinned at the bottom above the add-row button.
    """

    def __init__(
        self,
        pool,
        current_name,
        on_change,
        available_vars_getter,
        themes,
        on_manage=None,
    ):
        super().__init__()
        self.pool = pool
        self.current_name = current_name
        self.on_change = on_change
        self.available_vars_getter = available_vars_getter
        self.themes = themes
        self._just_changed = False
        self._focused_cell = None  # tracks which TextField is currently focused
        self._on_manage_cb = on_manage

        t = themes.actual_theme
        self.width = _CARD_W
        self.padding = 0
        self.border_radius = _CARD_RADIUS
        self.bgcolor = _c(t, "surface")
        self.border = ft.Border.all(1, _c(t, "on_surface", 0.10))
        self.shadow = [
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=12,
                offset=ft.Offset(0, 3),
                color=ft.Colors.with_opacity(0.14, ft.Colors.BLACK),
            )
        ]
        self.clip_behavior = ft.ClipBehavior.ANTI_ALIAS
        self.expand = True  # ← fill vertical space

        self.description_field = ft.TextField(
            label=tm.translate("Descripción"),
            value=self._entry.get("description", ""),
            on_change=self._on_description_change,
            border_radius=8,
            text_size=13,
            multiline=True,
            min_lines=1,
            max_lines=3,
        )

        self._build_ui()

    # ──────────────────────────────────────────────────────────────────────────
    #  BUILD
    # ──────────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        t = self.themes.actual_theme
        acc = _type_accent(self._var_type(), self.themes)

        # ── 3-px accent strip ─────────────────────────────────────────────────
        self._accent_strip = ft.Container(
            height=3,
            bgcolor=acc,
            border_radius=ft.BorderRadius(
                top_left=_CARD_RADIUS,
                top_right=_CARD_RADIUS,
                bottom_left=0,
                bottom_right=0,
            ),
        )

        # ── header: icon + LaTeX + ⚙ ─────────────────────────────────────────
        self.header_display = txt.markdown(self._get_latex_header(), size=14)

        self.move_left_btn = ft.IconButton(
            icon=ft.Icons.ARROW_BACK_IOS_NEW,
            icon_size=16,
            padding=ft.Padding.all(4),
            tooltip=tm.translate("Mover a la izquierda"),
            on_click=lambda e: asyncio.create_task(self._on_manage_click("move_left", e)),
            icon_color=_c(t, "on_surface", 0.65),
            visible=self._on_manage_cb is not None,
        )
        self.move_right_btn = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD_IOS,
            icon_size=16,
            padding=ft.Padding.all(4),
            tooltip=tm.translate("Mover a la derecha"),
            on_click=lambda e: asyncio.create_task(self._on_manage_click("move_right", e)),
            icon_color=_c(t, "on_surface", 0.65),
            visible=self._on_manage_cb is not None,
        )
        self.remove_from_tab_btn = ft.IconButton(
            icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
            icon_size=16,
            padding=ft.Padding.all(4),
            tooltip=tm.translate("Eliminar de la pestaña"),
            on_click=lambda e: asyncio.create_task(self._on_manage_click("remove_from_tab", e)),
            icon_color=_c(t, "on_surface", 0.65),
            visible=self._on_manage_cb is not None,
        )
        self.delete_variable_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
            icon_size=16,
            padding=ft.Padding.all(4),
            tooltip=tm.translate("Eliminar variable"),
            on_click=lambda e: asyncio.create_task(self._on_manage_click("delete_variable", e)),
            icon_color=ft.Colors.RED_400,
            visible=self._on_manage_cb is not None,
        )
        self.manage_btns = ft.Row(
            [
                self.move_left_btn,
                self.move_right_btn,
                self.remove_from_tab_btn,
                self.delete_variable_btn,
            ],
            spacing=2,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            visible=self._on_manage_cb is not None,
        )

        self.settings_btn = ft.IconButton(
            icon=ft.Icons.SETTINGS_OUTLINED,
            on_click=self._open_settings_modal,
            icon_size=18,
            tooltip=tm.translate("Configurar magnitud y unidad"),
            icon_color=_c(t, "primary", 0.60),
            style=ft.ButtonStyle(padding=ft.Padding.all(4)),
        )

        _header = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.GRID_VIEW, size=18, color=acc),  # Icon for vector
                            self.header_display,
                        ],
                        spacing=5,
                        expand=True,
                    ),
                    self.manage_btns,
                    self.settings_btn,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=_PADDING, top=10, right=6, bottom=6),
        )

        # ── formula badge ─────────────────────────────────────────────────────
        self.formula_badge = ft.Container(
            visible=False,
            content=ft.Text(
                "",
                size=11,
                overflow=ft.TextOverflow.ELLIPSIS,
                max_lines=1,
            ),
            border_radius=6,
            padding=ft.Padding(8, 3, 8, 3),
            margin=ft.Margin(left=_PADDING, right=_PADDING, top=0, bottom=0),
        )

        # ── var dropdown ──────────────────────────────────────────────────────
        self.var_dropdown = latex_dropdown(
            label=tm.translate("Variable"),
            options=self.available_vars_getter(),
            value=self.current_name,
            on_change=self._on_var_switch,
            width=150,
        )

        mag_options = [ft.DropdownOption("none")] + [
            ft.DropdownOption(m) for m in []  # No magnitudes for vector
        ]
        self.mag_dropdown = dropdown(
            label=tm.translate("Magnitud"),
            options=mag_options,
            value=self._entry.get("magnitude", "none"),
            on_change=self._on_mag_change,
        )
        self.unit_dropdown = dropdown(
            label=tm.translate("Unidad"),
            options=self._get_unit_options(self.mag_dropdown.value),
            value=self._entry.get("unit", "none"),
            on_change=self._on_unit_change,
        )

        # ── rows (scrollable, expands to fill) ───────────────────────────────
        self.rows_col = ft.Column(
            spacing=8,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,  # ← grows vertically
        )

        # ── global error ─────────────────────────────────────────────────────
        self.global_error_field = LatexCell(
            value="",
            themes=self.themes,
            on_change=self._on_global_error_change,
            on_focus=self._on_cell_focus,
            on_blur=self._on_cell_blur,
            is_error=True,
        )
        self.global_error_container = ft.Container(
            content=self.global_error_field,
            visible=False,
            margin=ft.Margin(0, 5, 0, 10),
        )

        # ── stats strip ───────────────────────────────────────────────────────
        # Must be created BEFORE _load_rows() since _refresh_stats() is called during initialization
        self._stats_container = ft.Container(
            content=self._build_stats_row(),
            padding=ft.Padding(12, 10, 12, 10),
            bgcolor=_c(t, "on_surface", 0.03),
            border=ft.Border(top=ft.BorderSide(1, _c(t, "on_surface", 0.07))),
        )

        self._load_rows()

        # ── add-row button ────────────────────────────────────────────────────
        self.add_row_btn = ft.IconButton(
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            on_click=self._add_row,
            icon_size=24,
            tooltip=tm.translate("Agregar fila"),
            icon_color=t["primary"],
        )

        # ── assemble: fixed top + expanding rows + fixed bottom ───────────────
        self.content = ft.Column(
            [
                # fixed top section
                self._accent_strip,
                _header,
                self.formula_badge,
                ft.Container(
                    content=ft.Column(
                        [
                            self.var_dropdown,
                            ft.Divider(
                                height=10,
                                thickness=0.5,
                                color=_c(t, "on_surface", 0.10),
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=ft.Padding(left=_PADDING, right=_PADDING, top=4, bottom=0),
                ),
                # expanding rows area
                ft.Container(
                    content=self.rows_col,
                    padding=ft.Padding(left=_PADDING, right=_PADDING, top=0, bottom=0),
                    expand=True,
                ),
                # fixed bottom section
                self.global_error_container,
                self._stats_container,
                ft.Container(
                    content=ft.Row([self.add_row_btn], alignment=ft.MainAxisAlignment.CENTER),
                    padding=ft.Padding(0, 4, 0, 8),
                ),
            ],
            spacing=0,
            expand=True,
        )

    # ──────────────────────────────────────────────────────────────────────────
    #  PROPERTIES
    # ──────────────────────────────────────────────────────────────────────────

    @property
    def _entry(self):
        return self.pool.get(self.current_name, {})

    def _entry_values(self):
        return self._entry.get("values", [])

    def _entry_errors(self):
        return self._entry.get("errors", [])

    def _var_type(self):
        return self._entry.get("type", "vector")

    def _dimensions(self):
        return self._entry.get("dimensions", 2)

    def _is_derived(self):
        return bool(self._entry.get("formula", "").strip())

    def _supports_per_value_error(self):
        return False  # Vector doesn't support per value error

    # ──────────────────────────────────────────────────────────────────────────
    #  ROWS
    # ──────────────────────────────────────────────────────────────────────────

    def _make_row(self, values=None):
        return VectorRow(
            values=values,
            n=self._dimensions(),
            themes=self.themes,
            on_change=self._on_row_change,
            read_only=self._is_derived(),
        )

    def _delete_row_callback(self, e):
        # Find which row control contained the clicked cell and delete it.
        btn = e.control
        target_row = None
        for r in self.rows_col.controls:
            if hasattr(r, 'content') and hasattr(r.content, 'controls'):
                for cell in r.content.controls:
                    if hasattr(cell, 'delete_btn') and cell.delete_btn is btn:
                        target_row = r
                        break
            if target_row:
                break

        if target_row:
            asyncio.create_task(self._delete_row(target_row))

    async def _delete_row(self, row_control):
        if row_control in self.rows_col.controls:
            self.rows_col.controls.remove(row_control)
            if not self.rows_col.controls:
                self.rows_col.controls.append(self._make_row())

            self.sync_pool()
            self._notify_change()
            try:
                await self.rows_col.update()
            except:
                pass

    def _load_rows(self):
        values = self._entry_values()
        if is_constant_type(self._var_type()):
            values = values[:1]
        rows = [self._make_row(v) for v in values]
        if not rows:
            rows = [self._make_row()]
        if is_constant_type(self._var_type()):
            rows = rows[:1]
        self.rows_col.controls = rows
        self._sync_global_error_field(self._entry_errors())
        self._refresh_unit_dropdowns()

    def _refresh_unit_dropdowns(self):
        entry = self._entry
        self.mag_dropdown.value = entry.get("magnitude", "none")
        self.unit_dropdown.options = self._get_unit_options(self.mag_dropdown.value)
        self.unit_dropdown.value = entry.get("unit", "none")
        self.description_field.value = entry.get("description", "")
        self._update_header()
        self._update_formula_badge()
        self._update_accent()
        self._apply_rows_mode()
        self._sync_global_error_field(self._entry_errors())
        self._apply_derived_controls_state()
        self._refresh_stats()

    def _update_header(self):
        self.header_display.value = self._get_latex_header()
        try:
            self.header_display.update()
        except Exception:
            pass

    def _get_latex_header(self):
        name = self.current_name
        n = self._dimensions()
        has_special = any(c in name for c in ("^", "_", "\\"))
        display_name = name if has_special else f"\\text{{{name}}}"
        return f"$${display_name} \\, [dim={n}]$$"

    def _update_formula_badge(self):
        formula = self._entry.get("formula", "").strip()
        if formula:
            self.formula_badge.content.value = f"Fórmula: {formula[:20]}{'...' if len(formula) > 20 else ''}"
            self.formula_badge.visible = True
        else:
            self.formula_badge.visible = False
        try:
            self.formula_badge.update()
        except:
            pass

    def _update_accent(self):
        acc = _type_accent(self._var_type(), self.themes)
        self._accent_strip.bgcolor = acc
        try:
            self._accent_strip.update()
        except:
            pass

    def _apply_rows_mode(self):
        read_only = self._is_derived()
        for row in self.rows_col.controls:
            if hasattr(row, 'read_only'):
                row.read_only = read_only
                try:
                    row.update()
                except:
                    pass

    def _apply_derived_controls_state(self):
        derived = self._is_derived()
        self.var_dropdown.disabled = derived
        self.mag_dropdown.disabled = derived
        self.unit_dropdown.disabled = derived
        self.description_field.disabled = derived
        try:
            self.var_dropdown.update()
            self.mag_dropdown.update()
            self.unit_dropdown.update()
            self.description_field.update()
        except:
            pass

    def _sync_global_error_field(self, errors):
        if self._supports_per_value_error():
            self.global_error_container.visible = False
        else:
            global_error = errors[0] if errors else ""
            self.global_error_field.value = global_error
            self.global_error_container.visible = bool(global_error)

    def _get_unit_options(self, mag):
        return [ft.DropdownOption("none")]

    # ──────────────────────────────────────────────────────────────────────────
    #  EVENTS
    # ──────────────────────────────────────────────────────────────────────────

    def _on_row_change(self, values):
        self.sync_pool()
        self._notify_change()

    def _on_global_error_change(self, value):
        entry = self._entry
        entry["errors"] = [value] if value else []
        self._notify_change()

    def _on_description_change(self, e):
        self._entry["description"] = e.control.value
        self._notify_change()

    def _on_var_switch(self, e):
        new_name = e.control.value
        if new_name != self.current_name and new_name in self.pool:
            # Switch to existing variable
            self.current_name = new_name
            self._refresh_unit_dropdowns()
            self._notify_change()

    def _on_mag_change(self, e):
        self._entry["magnitude"] = e.control.value
        self.unit_dropdown.options = self._get_unit_options(e.control.value)
        self.unit_dropdown.value = "none"
        try:
            self.unit_dropdown.update()
        except:
            pass
        self._notify_change()

    def _on_unit_change(self, e):
        self._entry["unit"] = e.control.value
        self._notify_change()

    def _on_cell_focus(self, cell):
        self._focused_cell = cell

    def _on_cell_blur(self, cell):
        if self._focused_cell == cell:
            self._focused_cell = None

    async def _on_manage_click(self, action, e):
        if self._on_manage_cb:
            await self._on_manage_cb(self.current_name, action)

    def _open_settings_modal(self, e):
        # Implement settings modal if needed
        pass

    def _add_row(self, e):
        new_row = self._make_row()
        self.rows_col.controls.append(new_row)
        self.sync_pool()
        self._notify_change()
        try:
            self.rows_col.update()
        except:
            pass

    def _build_stats_row(self):
        values = self._entry_values()
        if not values:
            return ft.Text(tm.translate("Sin datos"), size=12, color=_c(self.themes.actual_theme, "on_surface", 0.6))

        try:
            n = len(values)
            dims = self._dimensions()
            return ft.Text(f"n = {n}, dim = {dims}", size=12, color=_c(self.themes.actual_theme, "on_surface", 0.6))
        except:
            return ft.Text(tm.translate("Error en estadísticas"), size=12, color=_c(self.themes.actual_theme, "on_surface", 0.6))

    def _refresh_stats(self):
        self._stats_container.content = self._build_stats_row()
        try:
            self._stats_container.update()
        except:
            pass

    # ──────────────────────────────────────────────────────────────────────────
    #  Public interface
    # ──────────────────────────────────────────────────────────────────────────

    def update_dropdown(self):
        self.var_dropdown.options = self.available_vars_getter()
        self.var_dropdown.value = self.current_name

    def sync_with_pool(self):
        values = self._entry_values()
        if is_constant_type(self._var_type()):
            values = values[:1]
        rows = self.rows_col.controls
        if len(rows) != len(values):
            self._load_rows()
        else:
            for i, row in enumerate(rows):
                if i < len(values):
                    row.values = values[i]
                    try:
                        row._build_ui()
                        row.update()
                    except:
                        pass

    def sync_pool(self):
        entry = self._entry
        values = []
        for row in self.rows_col.controls:
            if hasattr(row, 'values'):
                values.append(row.values)
        entry["values"] = values
        entry["type"] = infer_variable_type(entry)

    def _notify_change(self):
        if self.on_change:
            self.on_change()