import flet as ft
from flet_base.translations import instance_translation_manager as tm
import flet_base.components.texts as txt
from flet_base.components.inputs import dropdown
from screens.editor.components.latex_dropdown import latex_dropdown
from screens.editor.modals.modals import open_variable_settings_modal

from screens.editor.utils.utils import load_default_units
from utils.variable_types import (
    has_error_per_value,
    has_single_error,
    infer_variable_type,
    is_constant_type,
    is_formula_type,
)

default_units = load_default_units()


class EditableColumn(ft.Container):
    def __init__(self, pool, current_name, on_change, available_vars_getter, themes):
        super().__init__()
        self.pool = pool
        self.current_name = current_name
        self.on_change = on_change
        self.available_vars_getter = available_vars_getter
        self.themes = themes
        self._just_changed = False

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

        self.width = 180
        self.padding = 15
        self.border_radius = 12
        self.bgcolor = ft.Colors.with_opacity(0.05, themes.actual_theme["on_surface"])
        self.border = ft.Border.all(
            1, ft.Colors.with_opacity(0.1, themes.actual_theme["on_surface"])
        )

        self._build_ui()

    # ------------------------------------------------------------------ #
    #  Build                                                               #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        self.header_display = txt.markdown(self._get_latex_header(), size=14)
        self.formula_badge = ft.Container(
            visible=False,
            content=ft.Text(
                "",
                size=11,
                color=ft.Colors.with_opacity(0.75, self.themes.actual_theme["on_surface"]),
            ),
            bgcolor=ft.Colors.with_opacity(0.07, self.themes.actual_theme["on_surface"]),
            border_radius=6,
            padding=ft.Padding(8, 2, 8, 2),
        )
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

        self.rows_col = ft.Column(spacing=8, scroll=ft.ScrollMode.ADAPTIVE)
        self.global_error_field = ft.TextField(
            label=tm.translate("Error"),
            dense=True,
            height=38,
            text_align=ft.TextAlign.RIGHT,
            on_change=self._on_global_error_change,
            border=ft.InputBorder.NONE,
            bgcolor=ft.Colors.with_opacity(0.05, self.themes.actual_theme["error"]),
            border_radius=6,
            text_size=13,
            content_padding=ft.Padding.symmetric(horizontal=10),
        )
        self.global_error_container = ft.Container(
            content=self.global_error_field,
            visible=False,
        )
        self._load_rows()

        self.add_row_btn = ft.IconButton(
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            on_click=self._add_row,
            icon_size=24,
            tooltip=tm.translate("Agregar fila"),
            icon_color=self.themes.actual_theme["primary"],
        )
        self.settings_btn = ft.IconButton(
            icon=ft.Icons.SETTINGS_OUTLINED,
            on_click=self._open_settings_modal,
            icon_size=18,
            tooltip=tm.translate("Configurar magnitud y unidad"),
            icon_color=self.themes.actual_theme["secondary"],
        )

        self.content = ft.Column(
            [
                ft.Row(
                    [
                        ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.TABLE_CHART_OUTLINED,
                                    size=20,
                                    color=self.themes.actual_theme["secondary"],
                                ),
                                self.header_display,
                            ],
                            spacing=5,
                            expand=True,
                        ),
                        self.settings_btn,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                self.formula_badge,
                self.var_dropdown,
                ft.Divider(
                    height=10,
                    thickness=0.5,
                    color=ft.Colors.with_opacity(0.1, self.themes.actual_theme["on_surface"]),
                ),
                ft.Container(content=self.rows_col, height=274),
                self.global_error_container,
                ft.Row([self.add_row_btn], alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=10,
        )

    # ------------------------------------------------------------------ #
    #  Properties / helpers                                                #
    # ------------------------------------------------------------------ #

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
        else:
            return f"$${latex_name}$$"

    def _get_unit_options(self, mag):
        base = [ft.DropdownOption("none")]
        if mag == "none" or mag not in default_units:
            return base
        return base + [ft.DropdownOption(u) for u in default_units[mag]]

    def _cell_bg_color(self):
        opacity = 0.02 if self._is_derived() else 0.05
        return ft.Colors.with_opacity(opacity, self.themes.actual_theme["on_surface"])

    def _cell_text_color(self):
        opacity = 0.7 if self._is_derived() else 1.0
        return ft.Colors.with_opacity(opacity, self.themes.actual_theme["on_surface"])

    def _make_value_cell(self, value="", compact=False):
        return ft.TextField(
            value=str(value),
            dense=True,
            width=88 if compact else None,
            height=35,
            text_align=ft.TextAlign.RIGHT,
            on_change=self._on_cell_change,
            read_only=self._is_derived(),
            border=ft.InputBorder.NONE,
            bgcolor=self._cell_bg_color(),
            color=self._cell_text_color(),
            border_radius=6,
            text_size=13,
            content_padding=ft.Padding.symmetric(horizontal=10),
        )

    def _make_error_cell(self, value=""):
        return ft.TextField(
            value=str(value),
            dense=True,
            width=58,
            height=35,
            text_align=ft.TextAlign.RIGHT,
            on_change=self._on_cell_change,
            read_only=self._is_derived(),
            border=ft.InputBorder.NONE,
            bgcolor=ft.Colors.with_opacity(0.04, self.themes.actual_theme["error"]),
            color=self._cell_text_color(),
            border_radius=6,
            text_size=13,
            content_padding=ft.Padding.symmetric(horizontal=8),
            tooltip=tm.translate("Error"),
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
        if isinstance(row, ft.TextField):
            return row, None
        if isinstance(row, ft.Row):
            value_cell = row.controls[0] if len(row.controls) > 0 else None
            error_cell = row.controls[1] if len(row.controls) > 1 else None
            if isinstance(value_cell, ft.TextField) and isinstance(error_cell, ft.TextField):
                return value_cell, error_cell
        return None, None

    def _row_matches_mode(self, row) -> bool:
        value_cell, error_cell = self._extract_row_cells(row)
        if self._supports_per_value_error():
            return value_cell is not None and error_cell is not None
        return isinstance(row, ft.TextField)

    def _update_formula_badge(self):
        formula = self._entry.get("formula", "")
        has_formula = self._is_derived()
        self.formula_badge.visible = has_formula
        self.formula_badge.content.value = f"ƒ {formula}" if has_formula else ""
        try:
            self.formula_badge.update()
        except RuntimeError:
            pass

    def _sync_global_error_field(self, errors: list):
        show_single_error = self._supports_single_error()
        self.global_error_container.visible = show_single_error
        if not show_single_error:
            self.global_error_field.value = ""
            return

        error_value = errors[0] if errors else ""
        new_value = str(error_value) if error_value != "" else ""
        if not getattr(self.global_error_field, "focused", False):
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
                cell.bgcolor = self._cell_bg_color()
                cell.color = self._cell_text_color()

    def _apply_derived_controls_state(self):
        if not hasattr(self, "add_row_btn"):
            return
        block_add_rows = self._is_derived() or is_constant_type(self._var_type())
        self.add_row_btn.disabled = block_add_rows
        self.add_row_btn.icon_color = (
            ft.Colors.with_opacity(0.35, self.themes.actual_theme["primary"])
            if block_add_rows
            else self.themes.actual_theme["primary"]
        )
        try:
            self.add_row_btn.update()
        except RuntimeError:
            pass

    # ------------------------------------------------------------------ #
    #  Row management                                                      #
    # ------------------------------------------------------------------ #

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
        self._apply_rows_mode()
        self._sync_global_error_field(self._entry_errors())
        self._apply_derived_controls_state()

    def _update_header(self):
        self.header_display.value = self._get_latex_header()
        try:
            self.header_display.update()
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    #  Public interface                                                    #
    # ------------------------------------------------------------------ #

    def update_dropdown(self):
        self.var_dropdown.options = self.available_vars_getter()
        self.var_dropdown.value = self.current_name

    def sync_with_pool(self):
        """Update row TextFields in-place from pool, preserving focus."""
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
            next_value = str(values[idx]) if idx < len(values) else ""
            if (
                value_cell is not None
                and not getattr(value_cell, "focused", False)
                and value_cell.value != next_value
            ):
                value_cell.value = next_value

            if error_cell is not None:
                next_error = str(errors[idx]) if idx < len(errors) else ""
                if (
                    not getattr(error_cell, "focused", False)
                    and error_cell.value != next_error
                ):
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
        """Write current TextField values back to the pool."""
        entry = self._entry
        var_type = self._var_type()
        formula = entry.get("formula", "")

        if self._is_derived():
            values = self._entry_values()
        else:
            values = []
            for row in self.rows_col.controls:
                value_cell, _ = self._extract_row_cells(row)
                if isinstance(value_cell, ft.TextField):
                    values.append(self._parse_cell(value_cell))

        if is_constant_type(var_type):
            values = values[:1]

        if self._supports_single_error():
            errors = [self._parse_cell(self.global_error_field)]
        elif self._supports_per_value_error():
            errors = []
            for row in self.rows_col.controls:
                _, error_cell = self._extract_row_cells(row)
                if isinstance(error_cell, ft.TextField):
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

    # ------------------------------------------------------------------ #
    #  Event handlers                                                      #
    # ------------------------------------------------------------------ #

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
                    page,
                    self.current_name,
                    self.pool,
                    self._notify_change,
                )
            )
        else:
            open_variable_settings_modal(
                page,
                self.current_name,
                self.pool,
                self._notify_change,
            )

    # ------------------------------------------------------------------ #
    #  Internal utils                                                      #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_cell(cell):
        try:
            return float(cell.value) if cell.value else 0.0
        except ValueError:
            return 0.0
