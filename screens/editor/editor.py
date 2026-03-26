import flet as ft
import flet_base.router as fr
from flet_base.translations import instance_translation_manager as tm
from flet_base.components.inputs import dropdown
import flet_base.components.texts as txt
import importlib.util
from pathlib import Path


def load_default_units():
    """Dynamically load default_units from the utils directory."""
    try:
        # Expected path: utils/math utils/unit conversor/default_units.py
        root = Path(__file__).parents[2]
        units_path = (
            root / "utils" / "math utils" / "unit conversor" / "default_units.py"
        )

        if not units_path.exists():
            return {}

        spec = importlib.util.spec_from_file_location("default_units", str(units_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, "default_units", {})
    except Exception as e:
        print(f"Error loading units: {e}")
        return {}


default_units = load_default_units()


def normalize_editor_data(raw_data):
    """Normalize editor data to [{name: str, values: list, magnitude: str, unit: str}] format."""
    normalized = []

    if isinstance(raw_data, dict):
        raw_columns = raw_data.get("columns", [])
    elif isinstance(raw_data, list):
        raw_columns = raw_data
    else:
        raw_columns = []

    for i, column in enumerate(raw_columns):
        if isinstance(column, dict):
            col_name = column.get("name") or column.get("header") or f"V{i + 1}"
            col_values = column.get("values")
            if not isinstance(col_values, list):
                col_values = (
                    column.get("data") if isinstance(column.get("data"), list) else []
                )
            col_mag = column.get("magnitude", "none")
            col_unit = column.get("unit", "none")
        elif isinstance(column, list):
            col_name = f"V{i + 1}"
            col_values = column
            col_mag = "none"
            col_unit = "none"
        else:
            continue

        normalized.append(
            {
                "name": str(col_name),
                "values": col_values,
                "magnitude": col_mag,
                "unit": col_unit,
            }
        )

    if not normalized:
        normalized = [{"name": "V1", "values": [], "magnitude": "none", "unit": "none"}]

    return normalized


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
        self.border = ft.border.all(
            1, ft.Colors.with_opacity(0.1, themes.actual_theme["on_surface"])
        )

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

        self.content = ft.Column(
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
                ),
                self.var_dropdown,
                ft.Column(
                    [self.mag_dropdown, self.unit_dropdown],
                    spacing=5,
                ),
                ft.Divider(
                    height=10,
                    thickness=0.5,
                    color=ft.Colors.with_opacity(
                        0.1, self.themes.actual_theme["on_surface"]
                    ),
                ),
                ft.Container(
                    content=self.rows_col, height=250
                ),  # Reduced height for additional dropdowns
                ft.Row([self.add_row_btn], alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=10,
        )

    def get_latex_header(self):
        mag = self.pool[self.current_name].get("magnitude", "none")
        unit = self.pool[self.current_name].get("unit", "none")
        name = self.current_name

        # Format: Magnitude Name (unit of measure) in latex
        display_mag = mag if mag != "none" else name

        if unit != "none":
            return f"$\\text{{{display_mag}}} \\ (\\text{{{unit}}})$"
        else:
            return f"$\\text{{{display_mag}}}$"

    def update_header(self):
        self.header_display.value = self.get_latex_header()

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
        try:
            self.update()
        except RuntimeError:
            pass

    def handle_unit_change(self, e):
        self.pool[self.current_name]["unit"] = self.unit_dropdown.value
        self.update_header()
        self.on_change()
        try:
            self.update()
        except RuntimeError:
            pass

    def get_options(self):
        return [ft.dropdown.Option(name) for name in self.available_vars_getter()]

    def update_dropdown(self):
        self.var_dropdown.options = self.get_options()
        self.var_dropdown.value = self.current_name
        try:
            self.update()
        except RuntimeError:
            pass

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

        try:
            self.update()
        except RuntimeError:
            pass

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
            content_padding=ft.padding.symmetric(horizontal=10),
        )

    def handle_var_switch(self, e):
        self.sync_pool()  # Save old one first
        self.current_name = self.var_dropdown.value
        self.load_data()
        self.on_change()

    def handle_cell_change(self, e):
        self.sync_pool()
        self.on_change()

    def add_row(self, e):
        self.rows_col.controls.append(self.create_cell(""))
        self.sync_pool()
        self.on_change()
        try:
            self.update()
        except RuntimeError:
            pass

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

    def get_export_data(self):
        entry = self.pool.get(self.current_name, {})
        return {
            "name": self.current_name,
            "values": entry.get("values", []),
            "magnitude": entry.get("magnitude", "none"),
            "unit": entry.get("unit", "none"),
        }


async def EditorScreen(data: fr.DataSystem, themes):
    # Prepare shared data
    raw_data = normalize_editor_data(data.shared.get("editor_data", []))

    # We use a central pool (dict) for synchronization
    # pool: { "V1": {"values": [1,2,3], "magnitude": "none", "unit": "none"} }
    pool = {
        col["name"]: {
            "values": col["values"],
            "magnitude": col["magnitude"],
            "unit": col["unit"],
        }
        for col in raw_data
    }

    # Visual columns track which variable they are currently showing
    initial_ui_configs = [col["name"] for col in raw_data]

    columns_container = ft.Row(
        scroll=ft.ScrollMode.ADAPTIVE,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=20,
    )

    def get_available_vars():
        return list(pool.keys())

    def update_shared_state():
        export_list = []
        for name, entry in pool.items():
            export_list.append(
                {
                    "name": name,
                    "values": entry["values"],
                    "magnitude": entry["magnitude"],
                    "unit": entry["unit"],
                }
            )
        data.shared["editor_data"] = export_list

    def on_column_data_changed():
        update_shared_state()

    def add_ui_column(e=None):
        # Create a new variable in the pool if needed
        idx = 1
        new_name = f"V{len(pool) + 1}"
        while new_name in pool:
            idx += 1
            new_name = f"V{len(pool) + idx}"

        pool[new_name] = {"values": [], "magnitude": "none", "unit": "none"}

        # Add a new UI column bound to this new variable
        new_col = EditableColumn(
            pool=pool,
            current_name=new_name,
            on_change=on_column_data_changed,
            available_vars_getter=get_available_vars,
            themes=themes,
        )
        columns_container.controls.append(new_col)

        # Refresh all existing column dropdowns because a new variable is available
        refresh_all_dropdowns()
        update_shared_state()
        try:
            columns_container.update()
        except RuntimeError:
            pass

    def refresh_all_dropdowns():
        for ctrl in columns_container.controls:
            if isinstance(ctrl, EditableColumn):
                ctrl.update_dropdown()

    def clear_all(e=None):
        pool.clear()
        pool["V1"] = {"values": [], "magnitude": "none", "unit": "none"}
        columns_container.controls.clear()
        # Add one initial column
        add_ui_column()
        update_shared_state()
        try:
            columns_container.update()
        except RuntimeError:
            pass

    # Build initial UI
    for name in initial_ui_configs:
        columns_container.controls.append(
            EditableColumn(
                pool=pool,
                current_name=name,
                on_change=on_column_data_changed,
                available_vars_getter=get_available_vars,
                themes=themes,
            )
        )

    # Top Buttons Row
    action_buttons = ft.Row(
        [
            ft.TextButton(
                tm.translate("Atrás"),
                icon=ft.Icons.CHEVRON_LEFT,
                on_click=lambda _: data.page.go("/home"),
            ),
            ft.Row(
                [
                    ft.ElevatedButton(
                        tm.translate("Agregar columna"),
                        icon=ft.Icons.ADD_BOX_OUTLINED,
                        on_click=add_ui_column,
                        style=ft.ButtonStyle(
                            color={"": themes.actual_theme["on_primary"]},
                            bgcolor={"": themes.actual_theme["primary"]},
                        ),
                    ),
                    ft.ElevatedButton(
                        tm.translate("Limpiar todo"),
                        icon=ft.Icons.DELETE_SWEEP_OUTLINED,
                        on_click=clear_all,
                        color=ft.Colors.ERROR,
                    ),
                ],
                spacing=10,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    return ft.View(
        route="/editor",
        padding=30,
        controls=[
            ft.Column(
                [
                    ft.Text(
                        tm.translate("Editor de Matrices"),
                        size=36,
                        weight=ft.FontWeight.W_800,
                    ),
                    ft.Text(
                        tm.translate("Gestiona y edita tus vectores de datos"),
                        size=16,
                        color=ft.Colors.with_opacity(
                            0.6, themes.actual_theme["on_surface"]
                        ),
                    ),
                ],
                spacing=5,
            ),
            ft.Divider(height=20, thickness=0.5),
            action_buttons,
            ft.Container(height=20),
            ft.Container(
                content=columns_container,
                expand=True,
                padding=10,
                border_radius=15,
                bgcolor=ft.Colors.with_opacity(
                    0.01, themes.actual_theme["on_background"]
                ),
            ),
        ],
    )

