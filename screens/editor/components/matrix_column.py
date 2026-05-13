import asyncio
import flet as ft
from flet_base.translations import instance_translation_manager as tm
import flet_base.components.texts as txt
from flet_base.components.inputs import dropdown
from screens.editor.components.latex_dropdown import latex_dropdown, get_latex_widget
from screens.editor.components.column import LatexCell
from utils.variable_types import (
    is_matrix_type,
    is_constant_type,
    infer_variable_type,
)

# ── Design tokens ──────────────────────────────────────────────────────────────
_CARD_W = 350 # Slightly wider for matrices
_PADDING = 15
_CARD_RADIUS = 12
_CELL_H = 35
_CELL_RADIUS = 6

def _c(t, key, opacity=1.0):
    col = t[key]
    return ft.Colors.with_opacity(opacity, col) if opacity < 1.0 else col

def _type_accent(var_type: str, themes) -> str:
    t = themes.actual_theme
    return t.get("matrix_accent", ft.Colors.AMBER_400)

class MatrixGrid(ft.Container):
    """
    A grid for matrix with R rows and C columns.
    """
    def __init__(self, values, r, c, themes, on_change, read_only=False):
        super().__init__()
        # values is a list of lists: [ [r0c0, r0c1...], [r1c0, r1c1...], ... ]
        self.matrix_values = values
        self.r = r
        self.c = c
        self.themes = themes
        self._on_change_cb = on_change
        self.read_only = read_only
        self._build_ui()

    def _build_ui(self):
        rows = []
        for i in range(self.r):
            cells = []
            for j in range(self.c):
                val = "0"
                try:
                    val = self.matrix_values[i][j]
                except:
                    pass
                
                cell = LatexCell(
                    value=val,
                    themes=self.themes,
                    on_change=lambda v, row=i, col=j: self._on_cell_change(row, col, v),
                    read_only=self.read_only,
                    compact=True,
                )
                cells.append(ft.Container(content=cell, expand=True))
            
            rows.append(ft.Row(cells, spacing=4, alignment=ft.MainAxisAlignment.START))

        self.content = ft.Row(
            [
                ft.Column(
                    rows,
                    spacing=4,
                    alignment=ft.MainAxisAlignment.START,
                )
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
        )

    def _on_cell_change(self, row, col, value):
        while len(self.matrix_values) <= row:
            self.matrix_values.append([])
        while len(self.matrix_values[row]) <= col:
            self.matrix_values[row].append("0")
            
        self.matrix_values[row][col] = value
        if self._on_change_cb:
            self._on_change_cb(self.matrix_values)

class MatrixColumn(ft.Container):
    """
    Data-column card for matrices.
    """
    def __init__(self, pool, current_name, on_change, available_vars_getter, themes, on_manage=None):
        super().__init__()
        self.pool = pool
        self.current_name = current_name
        self.on_change = on_change
        self.available_vars_getter = available_vars_getter
        self.themes = themes
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
        self.expand = True

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

    def _build_ui(self):
        t = self.themes.actual_theme
        acc = _type_accent(self._var_type(), self.themes)

        self._accent_strip = ft.Container(
            height=3,
            bgcolor=acc,
            border_radius=ft.BorderRadius(top_left=_CARD_RADIUS, top_right=_CARD_RADIUS, bottom_left=0, bottom_right=0),
        )

        self.header_display = txt.markdown(self._get_latex_header(), size=14)

        # Management buttons
        self.move_left_btn = ft.IconButton(
            icon=ft.Icons.ARROW_BACK_IOS_NEW, icon_size=16, padding=4,
            on_click=lambda e: asyncio.create_task(self._on_manage_click("move_left", e)),
            visible=self._on_manage_cb is not None
        )
        self.move_right_btn = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD_IOS, icon_size=16, padding=4,
            on_click=lambda e: asyncio.create_task(self._on_manage_click("move_right", e)),
            visible=self._on_manage_cb is not None
        )
        self.remove_from_tab_btn = ft.IconButton(
            icon=ft.Icons.REMOVE_CIRCLE_OUTLINE, icon_size=16, padding=4,
            on_click=lambda e: asyncio.create_task(self._on_manage_click("remove_from_tab", e)),
            visible=self._on_manage_cb is not None
        )
        self.delete_variable_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE_ROUNDED, icon_size=16, padding=4,
            on_click=lambda e: asyncio.create_task(self._on_manage_click("delete_variable", e)),
            icon_color=ft.Colors.RED_400,
            visible=self._on_manage_cb is not None
        )

        _header = ft.Container(
            content=ft.Row([
                ft.Row([ft.Icon(ft.Icons.GRID_ON, size=18, color=acc), self.header_display], spacing=5, expand=True),
                ft.Row([self.move_left_btn, self.move_right_btn, self.remove_from_tab_btn, self.delete_variable_btn], spacing=2)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.Padding(left=_PADDING, top=10, right=6, bottom=6),
        )

        self.var_dropdown = latex_dropdown(
            label=tm.translate("Variable"),
            options=self.available_vars_getter(),
            value=self.current_name,
            on_change=self._on_var_switch,
            width=150,
        )

        self.grid_container = ft.Container(expand=True)
        self._load_grid()

        self._stats_container = ft.Container(
            content=self._build_stats_row(),
            padding=ft.Padding(12, 10, 12, 10),
            bgcolor=_c(t, "on_surface", 0.03),
            border=ft.Border(top=ft.BorderSide(1, _c(t, "on_surface", 0.07))),
        )

        self.content = ft.Column([
            self._accent_strip,
            _header,
            ft.Container(content=ft.Column([self.var_dropdown, ft.Divider(height=1, color=_c(t, "on_surface", 0.10))], spacing=10), padding=ft.Padding(_PADDING, 4, _PADDING, 0)),
            ft.Container(content=ft.Column([self.grid_container], scroll=ft.ScrollMode.ADAPTIVE), padding=_PADDING, expand=True),
            self._stats_container,
            ft.Container(height=10) # Padding bottom
        ], spacing=0, expand=True)

    @property
    def _entry(self): return self.pool.get(self.current_name, {})
    def _var_type(self): return self._entry.get("type", "matrix")
    def _rows(self): return self._entry.get("rows", 1)
    def _cols(self): return self._entry.get("cols", 1)

    def _get_latex_header(self):
        name = self.current_name
        r, c = self._rows(), self._cols()
        has_special = any(c in name for c in ("^", "_", "\\"))
        display_name = name if has_special else f"\\text{{{name}}}"
        return f"$${display_name} \\, [{r} \\times {c}]$$"

    def _load_grid(self):
        values = self._entry.get("values", [[]])
        matrix_data = values[0] if values else [[]]
        self.grid_container.content = MatrixGrid(
            values=matrix_data,
            r=self._rows(),
            c=self._cols(),
            themes=self.themes,
            on_change=self._on_matrix_change,
            read_only=bool(self._entry.get("formula", "").strip())
        )

    def _on_matrix_change(self, matrix_values):
        self._entry["values"] = [matrix_values]
        self._notify_change()

    def _on_description_change(self, e):
        self._entry["description"] = e.control.value
        self._notify_change()

    def _on_var_switch(self, e):
        new_name = e.control.value
        if new_name != self.current_name and new_name in self.pool:
            self.current_name = new_name
            self._load_grid()
            self.header_display.value = self._get_latex_header()
            self._refresh_stats()
            self._notify_change()
            try: self.update()
            except: pass

    async def _on_manage_click(self, action, e):
        if self._on_manage_cb: await self._on_manage_cb(self.current_name, action)

    def _build_stats_row(self):
        r, c = self._rows(), self._cols()
        return ft.Text(f"Matrix {r} x {c}", size=12, color=_c(self.themes.actual_theme, "on_surface", 0.6))

    def _refresh_stats(self):
        self._stats_container.content = self._build_stats_row()
        try: self._stats_container.update()
        except: pass

    def _notify_change(self):
        if self.on_change: self.on_change()

    def update_dropdown(self):
        self.var_dropdown.options = self.available_vars_getter()
        self.var_dropdown.value = self.current_name
        try: self.var_dropdown.update()
        except: pass

    def sync_with_pool(self):
        self._load_grid()
        self.header_display.value = self._get_latex_header()
        self._refresh_stats()
        try: self.update()
        except: pass
