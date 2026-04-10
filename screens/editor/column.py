import flet as ft
from flet_base.translations import instance_translation_manager as tm
import flet_base.components.texts as txt
from flet_base.components.modals import modal
from flet_base.components.buttons import filled_btn
from flet_base.components.inputs import dropdown

from screens.editor.utils import load_default_units

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
        self.var_dropdown = dropdown(
            label=tm.translate("Variable"),
            options=self._get_var_options(),
            value=self.current_name,
            on_change=self._on_var_switch,
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
                self.var_dropdown,
                ft.Divider(
                    height=10,
                    thickness=0.5,
                    color=ft.Colors.with_opacity(0.1, self.themes.actual_theme["on_surface"]),
                ),
                ft.Container(content=self.rows_col, height=320),
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

    def _get_latex_header(self):
        mag = self._entry.get("magnitude", "none")
        unit = self._entry.get("unit", "none")
        display = mag if mag != "none" else self.current_name

        if "^" in display or "_" in display:
            header = f"$${display}"
        else:
            header = f"$$\\text{{{display}}}"

        header += f" \\ (\\text{{{unit}}})$$" if unit != "none" else "$$"
        return header

    def _get_unit_options(self, mag):
        base = [ft.DropdownOption("none")]
        if mag == "none" or mag not in default_units:
            return base
        return base + [ft.DropdownOption(u) for u in default_units[mag]]

    def _get_var_options(self):
        return [ft.DropdownOption(name) for name in self.available_vars_getter()]

    def _make_cell(self, value=""):
        return ft.TextField(
            value=str(value),
            dense=True,
            height=35,
            text_align=ft.TextAlign.RIGHT,
            on_change=self._on_cell_change,
            border=ft.InputBorder.NONE,
            bgcolor=ft.Colors.with_opacity(0.05, self.themes.actual_theme["on_surface"]),
            border_radius=6,
            text_size=13,
            content_padding=ft.Padding.symmetric(horizontal=10),
        )

    # ------------------------------------------------------------------ #
    #  Row management                                                      #
    # ------------------------------------------------------------------ #

    def _load_rows(self):
        values = self._entry.get("values", [])
        self.rows_col.controls = [self._make_cell(v) for v in values] or [self._make_cell()]
        self._refresh_unit_dropdowns()

    def _refresh_unit_dropdowns(self):
        entry = self._entry
        self.mag_dropdown.value = entry.get("magnitude", "none")
        self.unit_dropdown.options = self._get_unit_options(self.mag_dropdown.value)
        self.unit_dropdown.value = entry.get("unit", "none")
        self._update_header()

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
        self.var_dropdown.options = self._get_var_options()
        self.var_dropdown.value = self.current_name

    def sync_with_pool(self):
        """Update row TextFields in-place from pool, preserving focus."""
        values = self._entry.get("values", [])
        rows = self.rows_col.controls

        # Reconcile row count
        while len(rows) < len(values):
            rows.append(self._make_cell())
        del rows[len(values):]
        if not values:
            rows.append(self._make_cell())

        # Update values without touching focused fields
        for cell, val in zip(rows, values):
            if isinstance(cell, ft.TextField) and not getattr(cell, "focused", False):
                new = str(val)
                if cell.value != new:
                    cell.value = new

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
        self.pool[self.current_name] = {
            "values": [
                self._parse_cell(c) for c in self.rows_col.controls
                if isinstance(c, ft.TextField)
            ],
            "magnitude": entry.get("magnitude", "none"),
            "unit": entry.get("unit", "none"),
        }

    def get_export_data(self):
        entry = self._entry
        return {
            "name": self.current_name,
            "values": entry.get("values", []),
            "magnitude": entry.get("magnitude", "none"),
            "unit": entry.get("unit", "none"),
        }

    # ------------------------------------------------------------------ #
    #  Event handlers                                                      #
    # ------------------------------------------------------------------ #

    def _notify_change(self):
        self._just_changed = True
        self.on_change()

    def _on_var_switch(self, e):
        self.sync_pool()
        self.current_name = self.var_dropdown.value
        self._load_rows()
        self._notify_change()

    def _on_cell_change(self, e):
        self.sync_pool()
        self._notify_change()

    def _add_row(self, e):
        self.rows_col.controls.append(self._make_cell())
        self.sync_pool()
        self._notify_change()

    def _on_mag_change(self, e):
        self.pool[self.current_name]["magnitude"] = self.mag_dropdown.value
        self.unit_dropdown.options = self._get_unit_options(self.mag_dropdown.value)
        self.unit_dropdown.value = "none"
        self.pool[self.current_name]["unit"] = "none"
        self._update_header()
        self._notify_change()

    def _on_unit_change(self, e):
        self.pool[self.current_name]["unit"] = self.unit_dropdown.value
        self._update_header()
        self._notify_change()

    def _open_settings_modal(self, e):
        page = self.page
        if not page:
            return
        page.show_dialog(
            modal(
                title_str=tm.translate("Configuración de Columna"),
                content=[
                    ft.Text(
                        f"{tm.translate('Variable')}: {self.current_name}",
                        weight=ft.FontWeight.BOLD,
                    ),
                    self.mag_dropdown,
                    self.unit_dropdown,
                ],
                actions=[
                    filled_btn(tm.translate("Cerrar"), on_click=lambda _: page.pop_dialog()),
                ],
            )
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
