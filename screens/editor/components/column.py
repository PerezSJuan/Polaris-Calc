import asyncio
import flet as ft
from flet_base.translations import instance_translation_manager as tm
import flet_base.components.texts as txt
from flet_base.components.inputs import dropdown
from screens.editor.components.latex_dropdown import latex_dropdown, get_latex_widget
from screens.editor.modals import open_variable_settings_modal

from screens.editor.utils.utils import (
    load_default_units,
    load_number_unit_parser,
    load_smart_format,
)

_evaluate_expr = load_number_unit_parser()
_smart_format = load_smart_format()
from utils.variable_types import (
    has_error_per_value,
    has_single_error,
    infer_variable_type,
    is_constant_type,
    is_formula_type,
)

default_units = load_default_units()

# ── Design tokens ──────────────────────────────────────────────────────────────
_CARD_W = 180
_PADDING = 15
_CARD_RADIUS = 12
_CELL_H = 35
_CELL_RADIUS = 6


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
        is_dark = t.get("background") == themes.dark_theme.get("background")
        return ft.Colors.TEAL_400 if not is_dark else ft.Colors.TEAL_200
    return t["primary"]


def _fmt(v: float) -> str:
    import math

    if not math.isfinite(v):
        return str(v)  # "inf", "-inf", "nan"
    # Use a larger budget (12) for the UI to avoid premature rounding/scientific notation
    if v == int(v) and abs(v) < 1e15:
        return _smart_format(int(v), max_chars=12)
    return _smart_format(v, max_chars=12)


def _fmt_edit(v: float) -> str:
    """Format for editing: show full number unless it is extremely large."""
    import math

    if not math.isfinite(v):
        return str(v)
    if abs(v) >= 1e20:
        return f"{v:e}"
    # Use enough precision to avoid scientific notation, then strip
    res = f"{v:.15f}".rstrip("0").rstrip(".")
    return res if res != "-0" else "0"


class LatexCell(ft.Stack):
    """
    A dual-state cell:
    - Idle: Shows formatted LaTeX using Markdown.
    - Focused/Editing: Shows a plain TextField with the full numeric value.
    """

    def __init__(
        self,
        value,
        themes,
        on_change,
        on_focus=None,
        on_blur=None,
        compact=False,
        read_only=False,
        is_error=False,
    ):
        super().__init__()
        self.value_num = value if isinstance(value, (int, float)) else 0.0
        self.themes = themes
        self._on_change_cb = on_change
        self._on_focus_cb = on_focus
        self._on_blur_cb = on_blur
        self.compact = compact
        self.read_only = read_only
        self.is_error = is_error

        self.width = 88 if compact else (58 if is_error else None)
        self.height = _CELL_H

        # 1. TextField for editing
        self.edit_field = ft.TextField(
            value=_fmt_edit(self.value_num),
            dense=True,
            width=self.width,
            height=_CELL_H,
            text_align=ft.TextAlign.RIGHT,
            on_change=self._on_text_change,
            on_blur=self._on_blur,
            read_only=read_only,
            border=ft.InputBorder.NONE,
            bgcolor=self._cell_bg_color(),
            color=self._cell_text_color(),
            border_radius=_CELL_RADIUS,
            text_size=13,
            content_padding=ft.Padding.symmetric(horizontal=10),
            visible=False,
        )

        # 2. Container for display (LaTeX)
        self.display_container = ft.Container(
            content=ft.Row(
                [get_latex_widget(self._get_display_str(), size=13)],
                alignment=ft.MainAxisAlignment.END,
            ),
            padding=ft.Padding.symmetric(horizontal=10),
            on_click=self._on_display_click,
            bgcolor=self._cell_bg_color(),
            border_radius=_CELL_RADIUS,
            expand=True,
            height=_CELL_H,
            visible=True,
        )

        self.controls = [self.display_container, self.edit_field]

    @property
    def value(self):
        # This property makes it act somewhat like a TextField for the rest of the code
        return _fmt_edit(self.value_num)

    @value.setter
    def value(self, val):
        try:
            self.value_num = _evaluate_expr(str(val)).value
            self.edit_field.value = _fmt_edit(self.value_num)
            if self.page:
                self.page.run_task(self._update_display)
            else:
                self.display_container.content.controls[0] = get_latex_widget(
                    self._get_display_str(), size=13
                )
        except:
            pass

    def _get_display_str(self):
        return _smart_format(self.value_num, latex=True)

    async def _update_display(self):
        self.display_container.content.controls[0] = get_latex_widget(
            self._get_display_str(), size=13
        )
        try:
            await self.update()
        except:
            pass

    def _cell_bg_color(self):
        t = self.themes.actual_theme
        if self.is_error:
            return _c(t, "error", 0.06)
        return _c(t, "on_surface", 0.05)

    def _cell_text_color(self):
        t = self.themes.actual_theme
        if self.is_error:
            return _c(t, "error", 0.80)
        return _c(t, "on_surface", 1.0)

    async def _on_display_click(self, e):
        if self.read_only:
            return
        self.display_container.visible = False
        self.edit_field.visible = True
        self.edit_field.value = _fmt_edit(self.value_num)
        try:
            await self.update()
        except:
            pass
        await self.edit_field.focus()
        if self._on_focus_cb:
            # Simulate a focus event for the column to track it
            e.control = self.edit_field
            if asyncio.iscoroutinefunction(self._on_focus_cb):
                await self._on_focus_cb(e)
            else:
                self._on_focus_cb(e)

    async def _on_blur(self, e):
        self.display_container.visible = True
        self.edit_field.visible = False
        try:
            self.value_num = _evaluate_expr(self.edit_field.value).value
        except:
            pass
        await self._update_display()
        if self._on_blur_cb:
            e.control = self.edit_field
            if asyncio.iscoroutinefunction(self._on_blur_cb):
                await self._on_blur_cb(e)
            else:
                self._on_blur_cb(e)

    async def _on_text_change(self, e):
        try:
            self.value_num = _evaluate_expr(self.edit_field.value).value
        except:
            pass
        if self._on_change_cb:
            if asyncio.iscoroutinefunction(self._on_change_cb):
                await self._on_change_cb(e)
            else:
                self._on_change_cb(e)


class EditableColumn(ft.Container):
    """
    Data-column card.

    • Same 180 px width as original — tiles side by side correctly.
    • Expands vertically to fill available space (rows area grows, stats pinned at bottom).
    • Accent strip (3 px, colour-coded by type) at the top.
    • Formula badge when derived.
    • Stats strip (n / μ / σ) pinned at the bottom above the add-row button.
    """

    def __init__(self, pool, current_name, on_change, available_vars_getter, themes):
        super().__init__()
        self.pool = pool
        self.current_name = current_name
        self.on_change = on_change
        self.available_vars_getter = available_vars_getter
        self.themes = themes
        self._just_changed = False
        self._focused_cell = None  # tracks which TextField is currently focused

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
                            ft.Icon(ft.Icons.TABLE_CHART_OUTLINED, size=18, color=acc),
                            self.header_display,
                        ],
                        spacing=5,
                        expand=True,
                    ),
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
            ft.DropdownOption(m) for m in default_units
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

        # ── global error ──────────────────────────────────────────────────────
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
                    padding=ft.Padding(left=_PADDING, right=_PADDING, top=0, bottom=15),
                    expand=True,
                ),
                # fixed bottom section
                ft.Container(
                    content=self.global_error_container,
                    padding=ft.Padding(left=_PADDING, right=_PADDING, top=0, bottom=0),
                ),
                self._stats_container,
                ft.Container(
                    content=ft.Row(
                        [self.add_row_btn], alignment=ft.MainAxisAlignment.CENTER
                    ),
                    padding=ft.Padding(0, 4, 0, 8),
                ),
            ],
            spacing=0,
            expand=True,
        )

    # ──────────────────────────────────────────────────────────────────────────
    #  Stats row
    # ──────────────────────────────────────────────────────────────────────────

    def _build_stats_row(self):
        t = self.themes.actual_theme
        vals = [v for v in self._entry_values() if isinstance(v, (int, float))]
        n = len(vals)

        def chip(label, value_str):
            return ft.Column(
                [
                    ft.Text(
                        label,
                        size=9,
                        weight=ft.FontWeight.W_600,
                        color=_c(t, "on_surface", 0.38),
                    ),
                    ft.Text(
                        value_str,
                        size=11,
                        weight=ft.FontWeight.W_500,
                        color=_c(t, "on_surface", 0.75),
                    ),
                ],
                spacing=1,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

        if n == 0:
            chips = [chip("n", "—")]
        elif n == 1:
            chips = [chip("n", "1"), chip("val", _fmt(vals[0]))]
        else:
            mean = sum(vals) / n
            sigma = (sum((v - mean) ** 2 for v in vals) / n) ** 0.5
            suma = sum(vals)
            chips = [
                chip("n", str(n)),
                chip("μ", _fmt(mean)),
                chip("σ", _fmt(sigma)),
                chip("Σ", str(suma)),
            ]

        return ft.Row(chips, alignment=ft.MainAxisAlignment.SPACE_AROUND)

    def _refresh_stats(self):
        self._stats_container.content = self._build_stats_row()
        try:
            self._stats_container.update()
        except RuntimeError:
            pass

    # ──────────────────────────────────────────────────────────────────────────
    #  Properties / helpers
    # ──────────────────────────────────────────────────────────────────────────

    @property
    def _entry(self):
        return self.pool.get(self.current_name, {})

    def _var_type(self) -> str:
        return infer_variable_type(self._entry)

    def _is_derived(self) -> bool:
        formula = self._entry.get("formula", "")
        return (
            is_formula_type(self._var_type())
            and isinstance(formula, str)
            and formula.strip() != ""
        )

    def _supports_single_error(self) -> bool:
        return has_single_error(self._var_type()) and not self._is_derived()

    def _supports_per_value_error(self) -> bool:
        return has_error_per_value(self._var_type()) and not self._is_derived()

    def _entry_values(self) -> list:
        values = self._entry.get("values", [])
        return values if isinstance(values, list) else []

    def _entry_errors(self) -> list:
        errors = self._entry.get("errors", [])
        if isinstance(errors, list):
            return errors
        if errors in ("", None):
            return []
        return [errors]

    def _get_latex_header(self):
        mag = self._entry.get("magnitude", "none")
        unit = self._entry.get("unit", "none")
        display = mag if mag != "none" else self.current_name
        if "^" in display or "_" in display or "\\" in display:
            latex_name = display
        else:
            latex_name = f"\\text{{{display}}}"
        if unit != "none":
            return f"$${latex_name} \\ (\\text{{{unit}}})$$"
        return f"$${latex_name}$$"

    def _get_unit_options(self, mag):
        base = [ft.DropdownOption("none")]
        if mag == "none" or mag not in default_units:
            return base
        return base + [ft.DropdownOption(u) for u in default_units[mag]]

    def _cell_bg_color(self):
        t = self.themes.actual_theme
        return _c(t, "on_surface", 0.02 if self._is_derived() else 0.05)

    def _cell_text_color(self):
        t = self.themes.actual_theme
        return _c(t, "on_surface", 0.55 if self._is_derived() else 1.0)

    async def _on_cell_focus(self, e):
        self._focused_cell = e.control
        cell = e.control
        # If focused, show the 'true' value for editing if it's a number
        raw = (cell.value or "").strip()
        if raw and raw not in ("-", "+", ".", ","):
            try:
                # Try to evaluate and show expanded version
                val = _evaluate_expr(raw).value
                expanded = _fmt_edit(val)
                if cell.value != expanded:
                    cell.value = expanded
                    try:
                        await cell.update()
                    except:
                        pass
            except Exception:
                pass

    async def _on_cell_blur(self, e):
        cell = e.control
        if self._focused_cell is cell:
            self._focused_cell = None
        # Evaluate and reformat the cell content, then submit
        raw = (cell.value or "").strip()
        if raw and raw not in ("-", "+", ".", ","):
            try:
                result = _evaluate_expr(raw).value
                cell.value = _fmt(result)
                try:
                    await cell.update()
                except:
                    pass
            except Exception:
                pass
        if not self._is_derived():
            if asyncio.iscoroutinefunction(self.sync_pool):
                await self.sync_pool()
            else:
                self.sync_pool()
            if asyncio.iscoroutinefunction(self._notify_change):
                await self._notify_change()
            else:
                self._notify_change()

    def _make_value_cell(self, value="", compact=False):
        return LatexCell(
            value=value,
            themes=self.themes,
            compact=compact,
            read_only=self._is_derived(),
            on_change=self._on_cell_change,
            on_focus=self._on_cell_focus,
            on_blur=self._on_cell_blur,
        )

    def _make_error_cell(self, value=""):
        return LatexCell(
            value=value,
            themes=self.themes,
            is_error=True,
            read_only=self._is_derived(),
            on_change=self._on_cell_change,
            on_focus=self._on_cell_focus,
            on_blur=self._on_cell_blur,
        )

    def _make_row(self, value="", error=""):
        if self._supports_per_value_error():
            return ft.Row(
                [
                    self._make_value_cell(value=value, compact=True),
                    self._make_error_cell(error),
                ],
                spacing=6,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
        return self._make_value_cell(value=value)

    @staticmethod
    def _extract_row_cells(row):
        if isinstance(row, LatexCell):
            return row, None
        if isinstance(row, ft.Row):
            value_cell = row.controls[0] if len(row.controls) > 0 else None
            error_cell = row.controls[1] if len(row.controls) > 1 else None
            if isinstance(value_cell, LatexCell) and isinstance(error_cell, LatexCell):
                return value_cell, error_cell
        return None, None

    def _row_matches_mode(self, row) -> bool:
        value_cell, error_cell = self._extract_row_cells(row)
        if self._supports_per_value_error():
            return value_cell is not None and error_cell is not None
        return isinstance(row, LatexCell)

    def _update_formula_badge(self):
        formula = self._entry.get("formula", "")
        has_formula = self._is_derived()
        t = self.themes.actual_theme
        acc = _type_accent(self._var_type(), self.themes)
        self.formula_badge.visible = has_formula
        if has_formula:
            self.formula_badge.content.value = f"ƒ  {formula}"
            self.formula_badge.content.color = ft.Colors.with_opacity(0.85, acc)
            self.formula_badge.bgcolor = ft.Colors.with_opacity(0.08, acc)
            self.formula_badge.border = ft.Border.all(
                1, ft.Colors.with_opacity(0.18, acc)
            )
        try:
            self.formula_badge.update()
        except RuntimeError:
            pass

    def _sync_global_error_field(self, errors: list):
        show = self._supports_single_error()
        self.global_error_container.visible = show
        if not show:
            self.global_error_field.value = ""
            return
        error_value = errors[0] if errors else ""
        new_value = _fmt(error_value) if isinstance(error_value, (int, float)) else ""

        # Don't overwrite if this specific cell or its parent is focused
        is_focused = self.global_error_field.edit_field is self._focused_cell
        if not is_focused:
            self.global_error_field.value = new_value
        self.global_error_field.read_only = self._is_derived()
        self.global_error_field.bgcolor = self._cell_bg_color()
        self.global_error_field.color = self._cell_text_color()

    def _apply_rows_mode(self):
        for row in self.rows_col.controls:
            value_cell, error_cell = self._extract_row_cells(row)
            for cell in (value_cell, error_cell):
                if cell is None:
                    continue
                cell.read_only = self._is_derived()
                try:
                    cell.update()
                except (RuntimeError, AssertionError):
                    pass

    def _apply_derived_controls_state(self):
        if not hasattr(self, "add_row_btn"):
            return
        t = self.themes.actual_theme
        block = self._is_derived() or is_constant_type(self._var_type())
        self.add_row_btn.disabled = block
        self.add_row_btn.icon_color = _c(t, "primary", 0.30) if block else t["primary"]
        try:
            self.add_row_btn.update()
        except RuntimeError:
            pass

    def _update_accent(self):
        t = self.themes.actual_theme
        acc = _type_accent(self._var_type(), self.themes)
        self._accent_strip.bgcolor = acc
        try:
            self._accent_strip.update()
        except Exception:
            pass

    # ──────────────────────────────────────────────────────────────────────────
    #  Row management
    # ──────────────────────────────────────────────────────────────────────────

    def _load_rows(self):
        values = self._entry_values()
        errors = self._entry_errors()
        if is_constant_type(self._var_type()):
            values = values[:1]
        if self._supports_per_value_error():
            rows = [
                self._make_row(v, errors[i] if i < len(errors) else "")
                for i, v in enumerate(values)
            ]
        else:
            rows = [self._make_row(v) for v in values]
        if not rows:
            rows = [self._make_row()]
        if is_constant_type(self._var_type()):
            rows = rows[:1]
        self.rows_col.controls = rows
        self._sync_global_error_field(errors)
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

    # ──────────────────────────────────────────────────────────────────────────
    #  Public interface
    # ──────────────────────────────────────────────────────────────────────────

    def update_dropdown(self):
        self.var_dropdown.options = self.available_vars_getter()
        self.var_dropdown.value = self.current_name

    def sync_with_pool(self):
        values = self._entry_values()
        errors = self._entry_errors()
        if is_constant_type(self._var_type()):
            values = values[:1]
        rows = self.rows_col.controls
        if any(not self._row_matches_mode(row) for row in rows):
            self._load_rows()
            rows = self.rows_col.controls
        target_len = max(1, len(values))
        if is_constant_type(self._var_type()):
            target_len = 1
        while len(rows) < target_len:
            rows.append(self._make_row())
        del rows[target_len:]
        for idx, row in enumerate(rows):
            value_cell, error_cell = self._extract_row_cells(row)

            # Update Value Cell
            if value_cell is not None:
                next_value = _fmt(values[idx]) if idx < len(values) else ""

                # Skip if this cell's editor is focused
                if value_cell.edit_field is not self._focused_cell:
                    if value_cell.value != next_value:
                        value_cell.value = next_value

            # Update Error Cell
            if error_cell is not None:
                next_error = _fmt(errors[idx]) if idx < len(errors) else ""
                # Skip if this cell's editor is focused
                if error_cell.edit_field is not self._focused_cell:
                    if error_cell.value != next_error:
                        error_cell.value = next_error
        self._refresh_unit_dropdowns()
        try:
            self.rows_col.update()
        except Exception:
            pass
        if not self._just_changed:
            try:
                self.update()
            except RuntimeError:
                pass
        self._just_changed = False

    def sync_pool(self):
        entry = self._entry
        var_type = self._var_type()
        formula = entry.get("formula", "")
        if self._is_derived():
            values = self._entry_values()
        else:
            values = []
            for row in self.rows_col.controls:
                value_cell, _ = self._extract_row_cells(row)
                if isinstance(value_cell, LatexCell):
                    values.append(self._parse_cell(value_cell))
        if is_constant_type(var_type):
            values = values[:1]
        if self._supports_single_error():
            errors = [self._parse_cell(self.global_error_field)]
        elif self._supports_per_value_error():
            errors = []
            for row in self.rows_col.controls:
                _, error_cell = self._extract_row_cells(row)
                if isinstance(error_cell, LatexCell):
                    errors.append(self._parse_cell(error_cell))
        else:
            errors = []
        self.pool[self.current_name] = {
            "values": values,
            "errors": errors,
            "type": var_type,
            "magnitude": entry.get("magnitude", "none"),
            "unit": entry.get("unit", "none"),
            "description": self.description_field.value,
            "formula": formula if is_formula_type(var_type) else "",
        }

    def get_export_data(self):
        entry = self._entry
        return {
            "name": self.current_name,
            "values": entry.get("values", []),
            "errors": entry.get("errors", []),
            "type": infer_variable_type(entry),
            "magnitude": entry.get("magnitude", "none"),
            "unit": entry.get("unit", "none"),
            "description": entry.get("description", ""),
            "formula": entry.get("formula", ""),
        }

    # ──────────────────────────────────────────────────────────────────────────
    #  Event handlers
    # ──────────────────────────────────────────────────────────────────────────

    def _notify_change(self):
        self._just_changed = True
        self.on_change()

    def _on_var_switch(self, e=None):
        self.sync_pool()
        self.current_name = self.var_dropdown.value
        self._load_rows()
        self._notify_change()

    def _on_cell_change(self, e=None):
        if self._is_derived():
            return
        self.sync_pool()
        self._notify_change()

    def _on_global_error_change(self, e=None):
        if self._is_derived() or not self._supports_single_error():
            return
        self.sync_pool()
        self._notify_change()

    def _add_row(self, e):
        if self._is_derived() or is_constant_type(self._var_type()):
            return
        self.rows_col.controls.append(self._make_row())
        self.sync_pool()
        self._notify_change()

    def _on_mag_change(self, e=None):
        self.pool[self.current_name]["magnitude"] = self.mag_dropdown.value
        self.unit_dropdown.options = self._get_unit_options(self.mag_dropdown.value)
        self.unit_dropdown.value = "none"
        self.pool[self.current_name]["unit"] = "none"
        self._update_header()
        self._notify_change()

    def _on_unit_change(self, e=None):
        self.pool[self.current_name]["unit"] = self.unit_dropdown.value
        self._update_header()
        self._notify_change()

    def _on_description_change(self, e=None):
        self.pool[self.current_name]["description"] = self.description_field.value
        self._notify_change()

    def _open_settings_modal(self, e):
        page = self.page
        if not page:
            return
        import asyncio

        if asyncio.iscoroutinefunction(open_variable_settings_modal):
            asyncio.create_task(
                open_variable_settings_modal(
                    page, self.current_name, self.pool, self._notify_change, self.themes
                )
            )
        else:
            open_variable_settings_modal(
                page, self.current_name, self.pool, self._notify_change, self.themes
            )

    @staticmethod
    def _parse_cell(cell):
        if isinstance(cell, LatexCell):
            return cell.value_num
        raw = (cell.value or "").strip()
        if not raw or raw in ("-", "+", ".", ","):
            return 0.0
        try:
            return _evaluate_expr(raw).value
        except Exception:
            return 0.0
