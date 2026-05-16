import asyncio
import math
import numpy as np
import flet as ft
from flet_base.translations import instance_translation_manager as tm
import flet_base.components.texts as txt
from screens.editor.components.latex_dropdown import latex_dropdown
from screens.editor.components.column import LatexCell
from utils.variable_types import (
    is_constant_type,
    is_formula_type,
    infer_variable_type,
)

# ── Design tokens ──────────────────────────────────────────────────────────────
_PADDING      = 15
_CARD_RADIUS  = 12
_CELL_W       = 88
_CELL_BTN_W   = 30
_CELL_TOTAL   = _CELL_W + _CELL_BTN_W   # 118 px per cell
_CELL_SPACING = 4
_CARD_MIN_W   = 280


def _card_width(n_cols: int) -> int:
    content = n_cols * _CELL_TOTAL + max(0, n_cols - 1) * _CELL_SPACING
    return max(_CARD_MIN_W, content + 2 * _PADDING)


def _c(t, key, opacity=1.0):
    col = t[key]
    return ft.Colors.with_opacity(opacity, col) if opacity < 1.0 else col


def _type_accent(var_type: str, themes) -> str:
    vt = var_type.lower()
    t  = themes.actual_theme
    if "formula"  in vt: return t.get("formula_accent",  t["primary"])
    if "constant" in vt: return t.get("constant_accent", t["secondary"])
    if "matrix"   in vt: return t.get("matrix_accent",   ft.Colors.AMBER_400)
    return t["primary"]


def _fmt(v) -> str:
    try:
        f = float(v)
        if not math.isfinite(f):
            return str(f)
        if f == int(f) and abs(f) < 1e12:
            return str(int(f))
        return f"{f:.6g}"
    except Exception:
        return str(v)


# ── MatrixGrid ─────────────────────────────────────────────────────────────────

class MatrixGrid(ft.Container):
    """
    Grid editable de R×C celdas LatexCell.
    Usa on_blur (no on_change) para no perder el foco al escribir.
    """

    def __init__(self, values, r, c, themes, on_change, read_only=False):
        super().__init__()
        self.matrix_values = values
        self.r             = r
        self.c             = c
        self.themes        = themes
        self._on_change_cb = on_change
        self.read_only     = read_only
        self._build_ui()

    def _build_ui(self):
        self._cells = []
        row_widgets = []

        for i in range(self.r):
            self._cells.append([])
            cells_row = []
            for j in range(self.c):
                val = "0"
                try:
                    val = self.matrix_values[i][j]
                except Exception:
                    pass
                try:
                    num_val = float(val)
                except Exception:
                    num_val = 0.0

                cell = LatexCell(
                    value=num_val,
                    themes=self.themes,
                    on_change=None,
                    on_blur=self._make_blur_cb(i, j),
                    read_only=self.read_only,
                    compact=True,
                )
                self._cells[i].append(cell)
                cells_row.append(ft.Container(content=cell, expand=True))

            row_widgets.append(
                ft.Row(cells_row, spacing=4, alignment=ft.MainAxisAlignment.START)
            )

        self.content = ft.Row(
            [ft.Column(row_widgets, spacing=4, tight=True)],
        )

    def _make_blur_cb(self, i, j):
        async def _on_blur(e=None):
            try:
                val = str(self._cells[i][j].value_num)
                while len(self.matrix_values) <= i:
                    self.matrix_values.append([])
                while len(self.matrix_values[i]) <= j:
                    self.matrix_values[i].append("0")
                self.matrix_values[i][j] = val
            except Exception:
                pass
            if self._on_change_cb:
                self._on_change_cb(self.matrix_values)
        return _on_blur

    def get_values(self) -> list:
        result = []
        for row_cells in self._cells:
            result.append([str(c.value_num) for c in row_cells])
        return result


# ── MatrixColumn ───────────────────────────────────────────────────────────────

class MatrixColumn(ft.Container):
    """
    Tarjeta de columna para matrices.
    Patrón visual idéntico a ComplexColumn / EditableColumn.
    Stats: filas, cols, traza y determinante (numpy) para matrices cuadradas.
    """

    def __init__(self, pool, current_name, on_change, available_vars_getter,
                 themes, on_manage=None):
        super().__init__()
        self.pool                  = pool
        self.current_name          = current_name
        self.on_change             = on_change
        self.available_vars_getter = available_vars_getter
        self.themes                = themes
        self._on_manage_cb         = on_manage
        self._just_changed         = False
        self._debounce_task        = None

        t = themes.actual_theme
        self.width          = _card_width(self._cols())
        self.padding        = 0
        self.border_radius  = _CARD_RADIUS
        self.bgcolor        = _c(t, "surface")
        self.border         = ft.Border.all(1, _c(t, "on_surface", 0.10))
        self.shadow         = [ft.BoxShadow(
            spread_radius=0, blur_radius=12,
            offset=ft.Offset(0, 3),
            color=ft.Colors.with_opacity(0.14, ft.Colors.BLACK),
        )]
        self.clip_behavior  = ft.ClipBehavior.ANTI_ALIAS
        self.expand         = True

        self._build_ui()

    # ── BUILD ──────────────────────────────────────────────────────────────────

    def _build_ui(self):
        t   = self.themes.actual_theme
        acc = _type_accent(self._var_type(), self.themes)

        self._accent_strip = ft.Container(
            height=3, bgcolor=acc,
            border_radius=ft.BorderRadius(
                top_left=_CARD_RADIUS, top_right=_CARD_RADIUS,
                bottom_left=0, bottom_right=0,
            ),
        )

        self.header_display = txt.markdown(self._get_latex_header(), size=14)

        def _mgr_btn(icon, action, color=None, tooltip=""):
            return ft.IconButton(
                icon=icon, icon_size=16,
                padding=ft.Padding.all(4),
                tooltip=tooltip,
                on_click=lambda e, a=action: asyncio.create_task(
                    self._on_manage_click(a, e)
                ),
                icon_color=color or _c(t, "on_surface", 0.65),
                visible=self._on_manage_cb is not None,
            )

        self.move_left_btn       = _mgr_btn(ft.Icons.ARROW_BACK_IOS_NEW,     "move_left",
                                            tooltip=tm.translate("Mover a la izquierda"))
        self.move_right_btn      = _mgr_btn(ft.Icons.ARROW_FORWARD_IOS,      "move_right",
                                            tooltip=tm.translate("Mover a la derecha"))
        self.remove_from_tab_btn = _mgr_btn(ft.Icons.REMOVE_CIRCLE_OUTLINE,  "remove_from_tab",
                                            tooltip=tm.translate("Eliminar de la pestaña"))
        self.delete_variable_btn = _mgr_btn(ft.Icons.DELETE_OUTLINE_ROUNDED, "delete_variable",
                                            color=ft.Colors.RED_400,
                                            tooltip=tm.translate("Eliminar variable"))

        self.manage_btns = ft.Row(
            [self.move_left_btn, self.move_right_btn,
             self.remove_from_tab_btn, self.delete_variable_btn],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            visible=self._on_manage_cb is not None,
        )

        self.settings_btn = ft.IconButton(
            icon=ft.Icons.SETTINGS_OUTLINED,
            on_click=self._open_settings_modal,
            icon_size=18,
            tooltip=tm.translate("Configurar"),
            icon_color=_c(t, "primary", 0.60),
            style=ft.ButtonStyle(padding=ft.Padding.all(4)),
        )

        _header = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [ft.Icon(ft.Icons.GRID_ON, size=18, color=acc),
                         self.header_display],
                        spacing=5, expand=True,
                    ),
                    self.manage_btns,
                    self.settings_btn,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=_PADDING, top=10, right=6, bottom=6),
        )

        self.formula_badge = ft.Container(
            visible=False,
            content=ft.Text("", size=11, weight=ft.FontWeight.W_500,
                            overflow=ft.TextOverflow.ELLIPSIS, max_lines=1),
            border_radius=6,
            padding=ft.Padding(8, 3, 8, 3),
            margin=ft.Margin(left=_PADDING, right=_PADDING, top=0, bottom=0),
        )

        self.var_dropdown = latex_dropdown(
            label=tm.translate("Variable"),
            options=self.available_vars_getter(),
            value=self.current_name,
            on_change=self._on_var_switch,
            width=150,
        )

        self.grid_container = ft.Container()

        # Stats strip — antes de _load_grid
        self._stats_container = ft.Container(
            content=self._build_stats_row(),
            padding=ft.Padding(12, 10, 12, 10),
            bgcolor=_c(t, "on_surface", 0.03),
            border=ft.Border(top=ft.BorderSide(1, _c(t, "on_surface", 0.07))),
        )

        self._load_grid()

        self.content = ft.Column(
            [
                self._accent_strip,
                _header,
                self.formula_badge,
                ft.Container(
                    content=ft.Column(
                        [self.var_dropdown,
                         ft.Divider(height=10, thickness=0.5,
                                    color=_c(t, "on_surface", 0.10))],
                        spacing=10,
                    ),
                    padding=ft.Padding(left=_PADDING, right=_PADDING, top=4, bottom=0),
                ),
                ft.Container(
                    content=self.grid_container,
                    padding=_PADDING,
                ),
                self._stats_container,
                ft.Container(height=10),
            ],
            spacing=0,
            tight=True,   # ← la columna se ajusta al contenido, sin scroll
        )

    # ── Grid ───────────────────────────────────────────────────────────────────

    def _load_grid(self):
        values = self._entry.get("values", [[]])
        matrix_data = values[0] if values else [[]]
        self.grid_container.content = MatrixGrid(
            values=matrix_data,
            r=self._rows(),
            c=self._cols(),
            themes=self.themes,
            on_change=self._on_matrix_change,
            read_only=bool(self._entry.get("formula", "").strip()),
        )

    def _on_matrix_change(self, matrix_values):
        self._entry["values"] = [matrix_values]
        self._refresh_stats()
        # Debounce para agrupar ediciones rápidas consecutivas
        if self._debounce_task:
            self._debounce_task.cancel()
        self._debounce_task = asyncio.ensure_future(self._debounced_notify())

    async def _debounced_notify(self):
        try:
            await asyncio.sleep(0.15)
            self._notify_change()
        except asyncio.CancelledError:
            pass

    # ── Stats ──────────────────────────────────────────────────────────────────

    def _build_stats_row(self):
        t = self.themes.actual_theme
        r = self._rows()
        c = self._cols()

        def chip(label, val_str):
            return ft.Column(
                [
                    ft.Text(label, size=9, weight=ft.FontWeight.W_600,
                            color=_c(t, "on_surface", 0.38)),
                    ft.Text(val_str, size=11, weight=ft.FontWeight.W_500,
                            color=_c(t, "on_surface", 0.75)),
                ],
                spacing=1,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

        chips = [chip("filas", str(r)), chip("cols", str(c))]

        if r == c:
            values = self._entry.get("values", [[]])
            matrix_data = values[0] if values else []
            try:
                m = np.array(
                    [[float(matrix_data[i][j]) for j in range(c)]
                     for i in range(r)],
                    dtype=float,
                )
                trace = float(np.trace(m))
                det   = float(np.linalg.det(m))
                chips.append(chip("tr",  _fmt(trace)))
                chips.append(chip("det", _fmt(det)))
            except Exception:
                pass

        return ft.Row(chips, alignment=ft.MainAxisAlignment.SPACE_AROUND)

    def _refresh_stats(self):
        self._stats_container.content = self._build_stats_row()
        try:
            self._stats_container.update()
        except Exception:
            pass

    # ── Header / badge ─────────────────────────────────────────────────────────

    def _get_latex_header(self) -> str:
        name = self.current_name
        r, c = self._rows(), self._cols()
        has_special = any(ch in name for ch in ("^", "_", "\\"))
        latex_name  = name if has_special else f"\\text{{{name}}}"
        return f"$${latex_name} \\in \\mathbb{{R}}^{{{r} \\times {c}}}$$"

    def _update_header(self):
        self.header_display.value = self._get_latex_header()
        try:
            self.header_display.update()
        except Exception:
            pass

    def _update_formula_badge(self):
        formula = self._entry.get("formula", "").strip()
        acc     = _type_accent(self._var_type(), self.themes)
        if formula:
            self.formula_badge.content.value = f"ƒ  {formula}"
            self.formula_badge.content.color  = acc
            self.formula_badge.bgcolor        = ft.Colors.with_opacity(0.10, acc)
            self.formula_badge.border         = ft.Border.all(
                1, ft.Colors.with_opacity(0.20, acc))
            self.formula_badge.visible = True
        else:
            self.formula_badge.visible = False
        try:
            self.formula_badge.update()
        except Exception:
            pass

    def _update_accent(self):
        acc = _type_accent(self._var_type(), self.themes)
        self._accent_strip.bgcolor = acc
        try:
            self._accent_strip.update()
        except Exception:
            pass

    def _open_settings_modal(self, e):
        pass

    # ── Properties ─────────────────────────────────────────────────────────────

    @property
    def _entry(self):
        return self.pool.get(self.current_name, {})

    def _var_type(self) -> str:
        return self._entry.get("type", "matrix")

    def _rows(self) -> int:
        return self._entry.get("rows", 1)

    def _cols(self) -> int:
        return self._entry.get("cols", 1)

    def _is_derived(self) -> bool:
        formula = self._entry.get("formula", "")
        return (
            is_formula_type(self._var_type())
            and isinstance(formula, str)
            and formula.strip() != ""
        )

    # ── Events ─────────────────────────────────────────────────────────────────

    def _on_var_switch(self, new_name=None):
        if new_name is None:
            new_name = self.var_dropdown.value
        if new_name and new_name != self.current_name and new_name in self.pool:
            self.current_name = new_name
            self.width = _card_width(self._cols())
            self._load_grid()
            self._update_header()
            self._update_formula_badge()
            self._refresh_stats()
            self._notify_change()
            try:
                self.update()
            except Exception:
                pass

    async def _on_manage_click(self, action, e):
        if self._on_manage_cb:
            if asyncio.iscoroutinefunction(self._on_manage_cb):
                await self._on_manage_cb(self.current_name, action)
            else:
                self._on_manage_cb(self.current_name, action)

    # ── Interfaz pública ───────────────────────────────────────────────────────

    def _notify_change(self):
        self._just_changed = True
        if self.on_change:
            self.on_change()

    def update_dropdown(self):
        self.var_dropdown.options = self.available_vars_getter()
        self.var_dropdown.value   = self.current_name
        try:
            self.var_dropdown.update()
        except Exception:
            pass

    def sync_with_pool(self):
        self.width = _card_width(self._cols())
        if self._just_changed:
            # Los valores ya están en el pool desde _on_matrix_change.
            # No recrear el grid — destruiría las celdas que el usuario edita.
            self._just_changed = False
            return
        self._load_grid()
        self._update_header()
        self._update_formula_badge()
        self._update_accent()
        self._refresh_stats()
        try:
            self.update()
        except Exception:
            pass