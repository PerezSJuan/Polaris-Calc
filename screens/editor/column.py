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
        self.pool = pool  # Dict of {name: {"values": list, "magnitude": str, "unit": str}}
        self.current_name = current_name
        self.on_change = on_change
        self.available_vars_getter = available_vars_getter
        self.themes = themes

        self.width = 180
        self.padding = 15
        self.border_radius = 12
        self.bgcolor = ft.Colors.with_opacity(0.05, themes.actual_theme["on_surface"])
        self.border = ft.Border.all(
            1, ft.Colors.with_opacity(0.1, themes.actual_theme["on_surface"])
        )

        # Internal flag used to indicate that this column initiated a change.
        # The editor will skip synchronizing this column during the global
        # refresh to avoid overwriting the active TextField and losing focus.
        self._just_changed = False

        self.build_ui()

    def build_ui(self):
        # Header text (LaTeX style)
        self.header_display = txt.markdown(self.get_latex_header(), size=14)

        # Dropdown for selecting which variable this column represents
        self.var_dropdown = dropdown(
            label=tm.translate("Variable"),
            options=self.get_options(),
            value=self.current_name,
            on_change=self.handle_var_switch,
        )

        # Magnitude selector
        mag_options = [ft.dropdown.Option("none")] + [
            ft.dropdown.Option(m) for m in default_units.keys()
        ]
        self.mag_dropdown = dropdown(
            label=tm.translate("Magnitud"),
            options=mag_options,
            value=self.pool[self.current_name].get("magnitude", "none"),
            on_change=self.handle_mag_change,
        )

        # Unit selector
        unit_options = self.get_unit_options(self.mag_dropdown.value)
        self.unit_dropdown = dropdown(
            label=tm.translate("Unidad"),
            options=unit_options,
            value=self.pool[self.current_name].get("unit", "none"),
            on_change=self.handle_unit_change,
        )

        # Container for rows
        self.rows_col = ft.Column(spacing=8, scroll=ft.ScrollMode.ADAPTIVE)
        self.load_data()

        # Add row button
        self.add_row_btn = ft.IconButton(
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            on_click=self.add_row,
            icon_size=24,
            tooltip=tm.translate("Agregar fila"),
            icon_color=self.themes.actual_theme["primary"],
        )

        # Settings button to open modal
        self.settings_btn = ft.IconButton(
            icon=ft.Icons.SETTINGS_OUTLINED,
            on_click=self.open_settings_modal,
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
                    color=ft.Colors.with_opacity(
                        0.1, self.themes.actual_theme["on_surface"]
                    ),
                ),
                ft.Container(
                    content=self.rows_col,
                    height=320,
                ),
                ft.Row([self.add_row_btn], alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=10,
        )

    def open_settings_modal(self, e):
        # We need to reach the page to show the modal
        page = self.page
        if not page:
            return

        settings_dialog = modal(
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
                filled_btn(
                    tm.translate("Cerrar"), on_click=lambda _: page.pop_dialog()
                ),
            ],
        )
        page.show_dialog(settings_dialog)

    def get_latex_header(self):
        mag = self.pool[self.current_name].get("magnitude", "none")
        unit = self.pool[self.current_name].get("unit", "none")
        name = self.current_name

        display_mag = mag if mag != "none" else name

        if "^" in display_mag or "_" in display_mag:
            header = f"$${display_mag}"
        else:
            header = f"$$\\text{{{display_mag}}}"

        if unit != "none":
            header += f" \\ (\\text{{{unit}}})$$"
        else:
            header += "$$"

        return header

    def update_header(self):
        self.header_display.value = self.get_latex_header()
        try:
            self.header_display.update()
        except Exception:
            pass

    def get_unit_options(self, mag):
        if mag == "none" or mag not in default_units:
            return [ft.dropdown.Option("none")]
        units = list(default_units[mag].keys())
        return [ft.dropdown.Option("none")] + [ft.dropdown.Option(u) for u in units]

    def handle_mag_change(self, e):
        mag = self.mag_dropdown.value
        self.pool[self.current_name]["magnitude"] = mag
        self.unit_dropdown.options = self.get_unit_options(mag)
        self.unit_dropdown.value = "none"
        self.pool[self.current_name]["unit"] = "none"
        self.update_header()
        self.on_change()
        self._just_changed = True
        # Do not call ``self.update()`` here to avoid a full widget redraw that
        # would cause the active TextField to lose focus. Individual control
        # updates are performed above.

    def handle_unit_change(self, e):
        self.pool[self.current_name]["unit"] = self.unit_dropdown.value
        self.update_header()
        self.on_change()
        self._just_changed = True

    def get_options(self):
        return [ft.dropdown.Option(name) for name in self.available_vars_getter()]

    def update_dropdown(self):
        self.var_dropdown.options = self.get_options()
        self.var_dropdown.value = self.current_name

    def load_data(self):
        self.rows_col.controls.clear()
        data_entry = self.pool.get(self.current_name, {})
        values = data_entry.get("values", [])
        for val in values:
            self.rows_col.controls.append(self.create_cell(val))

        if len(values) == 0:
            self.add_row(None)

        # Update unit dropdown state
        self.mag_dropdown.value = data_entry.get("magnitude", "none")
        self.unit_dropdown.options = self.get_unit_options(self.mag_dropdown.value)
        self.unit_dropdown.value = data_entry.get("unit", "none")
        self.update_header()


    def create_cell(self, value):
        return ft.TextField(
            value=str(value),
            dense=True,
            height=35,
            text_align=ft.TextAlign.RIGHT,
            on_change=self.handle_cell_change,
            border=ft.InputBorder.NONE,
            bgcolor=ft.Colors.with_opacity(
                0.05, self.themes.actual_theme["on_surface"]
            ),
            border_radius=6,
            text_size=13,
            content_padding=ft.Padding.symmetric(horizontal=10),
        )

    def handle_var_switch(self, e):
        self.sync_pool()  # Save old one first
        self.current_name = self.var_dropdown.value
        self.load_data()
        # Mark this column as the source of the change to avoid self.update()
        self._just_changed = True
        self.on_change()

    def handle_cell_change(self, e):
        self.sync_pool()
        # Mark this column as the source of the change.
        self._just_changed = True
        self.on_change()

    def add_row(self, e):
        self.rows_col.controls.append(self.create_cell(""))
        self.sync_pool()
        self._just_changed = True
        self.on_change()

    def sync_pool(self):
        data = []
        for ctrl in self.rows_col.controls:
            if isinstance(ctrl, ft.TextField):
                try:
                    val = float(ctrl.value) if ctrl.value else 0.0
                    data.append(val)
                except ValueError:
                    data.append(0.0)

        current_entry = self.pool.get(self.current_name, {})
        self.pool[self.current_name] = {
            "values": data,
            "magnitude": current_entry.get("magnitude", "none"),
            "unit": current_entry.get("unit", "none"),
        }

    def sync_with_pool(self):
        """Update the UI rows to reflect the current values in ``self.pool``.

        This method updates existing ``TextField`` controls in place, adding or
        removing rows as necessary, without recreating the entire column UI.
        It is used to keep multiple columns that reference the same variable
        in sync while preserving the user's focus on any active text field.
        """
        entry = self.pool.get(self.current_name, {})
        values = entry.get("values", [])
        # Adjust number of rows to match the values list
        current_len = len(self.rows_col.controls)
        target_len = len(values)
        # Add missing rows
        for _ in range(target_len - current_len):
            self.rows_col.controls.append(self.create_cell(""))
        # Remove extra rows
        if target_len < current_len:
            del self.rows_col.controls[target_len:]
        # If there are no values, ensure at least one empty row (mirrors load_data behavior)
        if target_len == 0:
            self.rows_col.controls.append(self.create_cell(""))
        # Update values in existing rows
        for ctrl, val in zip(self.rows_col.controls, values):
            if isinstance(ctrl, ft.TextField):
                # If this TextField currently has focus, skip updating its value
                # to avoid resetting the cursor position.
                if getattr(ctrl, "focused", False):
                    continue
                new_val = str(val)
                if ctrl.value != new_val:
                    ctrl.value = new_val
        # Ensure header and dropdowns reflect any magnitude/unit changes
        self.mag_dropdown.value = entry.get("magnitude", "none")
        self.unit_dropdown.options = self.get_unit_options(self.mag_dropdown.value)
        self.unit_dropdown.value = entry.get("unit", "none")
        self.update_header()
        # Update the rows container once to reflect new values without
        # triggering a full widget redraw that could steal focus.
        try:
            self.rows_col.update()
        except Exception:
            pass
        # Refresh the container so that any changes to the rows become visible.
        # Only refresh the container if this column did not originate the change.
        # ``self._just_changed`` is set by the event handlers before calling
        # ``on_change``. Skipping the container update prevents the active
        # TextField from losing focus while still updating the rows layout.
        if not getattr(self, "_just_changed", False):
            try:
                self.update()
            except RuntimeError:
                pass
        # Reset the flag after synchronization so future changes are handled normally.
        self._just_changed = False
        # Refresh the column container so that header and dropdown changes are
        # applied. This does not recreate the TextField widgets (their values are
        # only changed when necessary), so the current cursor position remains
        # intact.
        # Update the column container itself so that any header or dropdown
        # changes become visible. This does not recreate the TextField widgets,
        # so the current cursor position remains intact.

    def get_export_data(self):
        entry = self.pool.get(self.current_name, {})
        return {
            "name": self.current_name,
            "values": entry.get("values", []),
            "magnitude": entry.get("magnitude", "none"),
            "unit": entry.get("unit", "none"),
        }
