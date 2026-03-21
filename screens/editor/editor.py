import flet as ft
import flet_base.router as fr
from flet_base.translations import instance_translation_manager as tm
import flet_base.components.texts as txt


def normalize_editor_data(raw_data):
    """Normalize editor data to [{name: str, values: list}] format."""
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
        elif isinstance(column, list):
            col_name = f"V{i + 1}"
            col_values = column
        else:
            continue

        normalized.append({"name": str(col_name), "values": col_values})

    if not normalized:
        normalized = [{"name": "V1", "values": []}]

    return normalized


class DataColumn(ft.Column):
    def __init__(self, index, data=None, header=None, on_change=None):
        super().__init__(expand=False)
        self.index = index
        self._data = data if data is not None else []
        self.header = header if header else f"V{self.index + 1}"
        self.on_change = on_change
        self.controls = []
        self.width = 150
        self.spacing = 5
        self.build_column()

    def build_column(self):
        self.header_display = ft.Container(
            content=txt.markdown(f"$${self.header}$$", size=14),
            alignment=ft.Alignment.CENTER,
            height=40,
            on_click=self.start_edit_header,
            tooltip=tm.translate("Clic para editar nombre"),
        )

        self.header_field = ft.TextField(
            label=f"Col {self.index + 1}",
            value=self.header,
            text_align=ft.TextAlign.CENTER,
            dense=True,
            height=40,
            visible=False,
            on_blur=self.finish_edit_header,
            on_submit=self.finish_edit_header,
        )

        self.controls = [
            self.header_display,
            self.header_field,
            ft.Divider(height=1, thickness=1),
        ]

        # Rows
        self.rows_container = ft.Column(spacing=2)
        for val in self._data:
            self.rows_container.controls.append(self.create_cell(val))

        self.controls.append(self.rows_container)

        # Add Row Button
        self.controls.append(
            ft.IconButton(
                icon=ft.Icons.ADD,
                on_click=self.add_row,
                tooltip=tm.translate("Agregar fila"),
                icon_size=16,
            )
        )

    def create_cell(self, value):
        return ft.TextField(
            value=str(value),
            dense=True,
            height=35,
            text_align=ft.TextAlign.RIGHT,
            on_change=self.handle_cell_change,
        )

    def handle_cell_change(self, e):
        if self.on_change:
            self.on_change()

    def start_edit_header(self, e):
        self.header_display.visible = False
        self.header_field.visible = True
        self.header_field.focus()
        self.update()

    def finish_edit_header(self, e):
        self.header = self.header_field.value or f"V{self.index + 1}"
        self.header_display.content = txt.markdown(f"$${self.header}$$", size=14)
        self.header_display.visible = True
        self.header_field.visible = False
        self.update()
        if self.on_change:
            self.on_change()

    def add_row(self, e=None):
        self.rows_container.controls.append(self.create_cell(""))
        self.update()
        if self.on_change:
            self.on_change()

    def get_data(self):
        data = []
        for ctrl in self.rows_container.controls:
            try:
                val = float(ctrl.value) if ctrl.value else 0.0
                data.append(val)
            except ValueError:
                data.append(0.0)
        return data

    def get_column_data(self):
        return {
            "name": self.header,
            "values": self.get_data(),
        }

    def set_data(self, data):
        self._data = data
        self.rows_container.controls.clear()
        for val in data:
            self.rows_container.controls.append(self.create_cell(val))
        self.update()


async def EditorScreen(data: fr.DataSystem, themes):
    data.shared["editor_data"] = normalize_editor_data(data.shared.get("editor_data"))

    # Container for all columns
    columns_row = ft.Row(
        scroll=ft.ScrollMode.ADAPTIVE,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=20,
    )

    def on_data_changed():
        # Update shared state
        matrices = []
        for col_ctrl in columns_row.controls:
            if isinstance(col_ctrl, DataColumn):
                matrices.append(col_ctrl.get_column_data())
        data.shared["editor_data"] = matrices

    def add_column(e=None):
        idx = len([c for c in columns_row.controls if isinstance(c, DataColumn)])
        new_col = DataColumn(index=idx, header=f"V{idx + 1}", on_change=on_data_changed)
        # Shift the "+" button to the end
        if len(columns_row.controls) > 0:
            columns_row.controls.insert(len(columns_row.controls) - 1, new_col)
        else:
            columns_row.controls.append(new_col)
        on_data_changed()
        columns_row.update()

    def clear_all(e=None):
        columns_row.controls.clear()
        data.shared["editor_data"] = [{"name": "V1", "values": []}]
        for i, col_data in enumerate(data.shared["editor_data"]):
            columns_row.controls.append(
                DataColumn(
                    index=i,
                    data=col_data.get("values", []),
                    header=col_data.get("name", f"V{i + 1}"),
                    on_change=on_data_changed,
                )
            )
        columns_row.controls.append(add_col_btn)
        on_data_changed()
        columns_row.update()

    # Initialize columns from shared data
    for i, col_data in enumerate(data.shared["editor_data"]):
        columns_row.controls.append(
            DataColumn(
                index=i,
                data=col_data.get("values", []),
                header=col_data.get("name", f"V{i + 1}"),
                on_change=on_data_changed,
            )
        )

    # Button to add new column
    add_col_btn = ft.Container(
        content=ft.Column(
            [
                ft.IconButton(
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    on_click=add_column,
                    icon_size=40,
                    tooltip=tm.translate("Agregar columna"),
                    icon_color=themes.actual_theme["primary"],
                ),
                ft.Text(
                    tm.translate("Nueva Columna"),
                    size=12,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        width=150,
        height=150,
        border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE)),
        border_radius=10,
        margin=ft.margin.only(top=50),
    )
    columns_row.controls.append(add_col_btn)

    return ft.View(
        route="/editor",
        controls=[
            ft.Row(
                [
                    ft.Text(
                        tm.translate("Editor de Matrices"),
                        size=28,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                tm.translate("Atrás"),
                                icon=ft.Icons.ARROW_BACK,
                                on_click=lambda _: data.page.go("/home"),
                            ),
                            ft.ElevatedButton(
                                tm.translate("Limpiar todo"),
                                icon=ft.Icons.DELETE_SWEEP,
                                on_click=clear_all,
                                color=ft.Colors.ERROR,
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Divider(height=20),
            ft.Container(
                content=columns_row,
                expand=True,
                padding=20,
                border_radius=10,
                bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.ON_SURFACE),
            ),
        ],
    )
