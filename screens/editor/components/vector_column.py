import asyncio
import math
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
_PADDING     = 15
_CARD_RADIUS = 12
_CELL_W      = 88   # LatexCell base_w when compact=True
_CELL_BTN_W  = 30   # _BTN_SPACE in LatexCell
_CELL_TOTAL  = _CELL_W + _CELL_BTN_W   # 118 px per cell
_CELL_SPACING = 4
_DEL_BTN_W   = 28   # delete-row button + gap
_CARD_MIN_W  = 280


def _card_width(n_cells: int) -> int:
    """Ancho de tarjeta para n celdas en una fila."""
    content = n_cells * _CELL_TOTAL + max(0, n_cells - 1) * _CELL_SPACING
    return max(_CARD_MIN_W, content + 2 * _PADDING + _DEL_BTN_W)


def _c(t, key, opacity=1.0):
    col = t[key]
    return ft.Colors.with_opacity(opacity, col) if opacity < 1.0 else col


def _type_accent(var_type: str, themes) -> str:
    vt = var_type.lower()
    t  = themes.actual_theme
    if "formula"  in vt: return t.get("formula_accent",  t["primary"])
    if "constant" in vt: return t.get("constant_accent", t["secondary"])
    if "vector"   in vt: return t.get("vector_accent",   ft.Colors.GREEN_400)
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


# ── VectorRow ──────────────────────────────────────────────────────────────────

class VectorRow(ft.Container):
    """
    Una fila con n LatexCell editables, una por componente del vector.
    Usa on_blur (no on_change) para no perder el foco al escribir.
    """

    def __init__(self, values, n, themes, on_change, on_delete=None, read_only=False):
        super().__init__()
        self.vector_values = list(values) if values else ["0"] * n
        self.n             = n
        self.themes        = themes
        self._on_change_cb = on_change
        self._on_delete_cb = on_delete
        self.read_only     = read_only
        self.padding       = ft.Padding(0, 2, 0, 2)
        self._build_ui()

    def _build_ui(self):
        t = self.themes.actual_theme

        self._del_btn = ft.IconButton(
            icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
            icon_size=14, width=24, height=24,
            padding=0,
            tooltip=tm.translate("Eliminar fila"),
            on_click=self._handle_delete,
            icon_color=ft.Colors.RED_400,
            opacity=0.5,
            visible=(self._on_delete_cb is not None) and not self.read_only,
        )

        cells = []
        for i in range(self.n):
            raw = self.vector_values[i] if i < len(self.vector_values) else "0"
            try:
                val = float(raw)
            except Exception:
                val = 0.0
            cell = LatexCell(
                value=val,
                themes=self.themes,
                on_change=None,
                on_blur=self._make_blur_cb(i),
                read_only=self.read_only,
                compact=True,
            )
            cells.append(cell)
        self._cells = cells

        self.content = ft.Row(
            [ft.Row(cells, spacing=4), self._del_btn],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2, expand=True,
        )

    def _make_blur_cb(self, idx):
        async def _on_blur(e=None):
            try:
                self.vector_values[idx] = str(self._cells[idx].value_num)
            except Exception:
                pass
            if self._on_change_cb:
                self._on_change_cb()
        return _on_blur

    async def _handle_delete(self, e):
        if self._on_delete_cb:
            if asyncio.iscoroutinefunction(self._on_delete_cb):
                await self._on_delete_cb(self)
            else:
                self._on_delete_cb(self)

    def get_values(self) -> list:
        return [str(c.value_num) for c in self._cells]


# ── VectorColumn ───────────────────────────────────────────────────────────────

class VectorColumn(ft.Container):
    """
    Tarjeta de columna para vectores n-dimensionales.
    Patrón visual idéntico a ComplexColumn / EditableColumn:
    accent strip · header con icon + LaTeX + manage buttons + settings ·
    formula badge · var dropdown · rows scrollables · stats strip · botón ➕.
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

        t = themes.actual_theme
        self.width          = _card_width(self._dimensions())
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

        # Accent strip
        self._accent_strip = ft.Container(
            height=3, bgcolor=acc,
            border_radius=ft.BorderRadius(
                top_left=_CARD_RADIUS, top_right=_CARD_RADIUS,
                bottom_left=0, bottom_right=0,
            ),
        )

        # Header
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
                        [ft.Icon(ft.Icons.GRID_VIEW, size=18, color=acc),
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

        # Formula badge
        self.formula_badge = ft.Container(
            visible=False,
            content=ft.Text("", size=11, weight=ft.FontWeight.W_500,
                            overflow=ft.TextOverflow.ELLIPSIS, max_lines=1),
            border_radius=6,
            padding=ft.Padding(8, 3, 8, 3),
            margin=ft.Margin(left=_PADDING, right=_PADDING, top=0, bottom=0),
        )

        # Var dropdown
        self.var_dropdown = latex_dropdown(
            label=tm.translate("Variable"),
            options=self.available_vars_getter(),
            value=self.current_name,
            on_change=self._on_var_switch,
            width=150,
        )

        # Rows
        self.rows_col = ft.Column(
            spacing=6, scroll=ft.ScrollMode.ADAPTIVE, expand=True,
        )

        # Add-row button — antes de _load_rows
        self.add_row_btn = ft.IconButton(
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            on_click=self._add_row, icon_size=24,
            tooltip=tm.translate("Agregar fila"),
            icon_color=t["primary"],
        )

        # Stats strip — antes de _load_rows
        self._stats_container = ft.Container(
            content=self._build_stats_row(),
            padding=ft.Padding(12, 10, 12, 10),
            bgcolor=_c(t, "on_surface", 0.03),
            border=ft.Border(top=ft.BorderSide(1, _c(t, "on_surface", 0.07))),
        )

        self._load_rows()

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
                    content=self.rows_col,
                    padding=ft.Padding(left=_PADDING, right=_PADDING, top=4, bottom=15),
                    expand=True,
                ),
                self._stats_container,
                ft.Container(
                    content=ft.Row([self.add_row_btn],
                                   alignment=ft.MainAxisAlignment.CENTER),
                    padding=ft.Padding(0, 4, 0, 8),
                ),
            ],
            spacing=0, expand=True,
        )

    # ── Rows ───────────────────────────────────────────────────────────────────

    def _make_row(self, values=None) -> VectorRow:
        is_const = is_constant_type(self._var_type())
        return VectorRow(
            values=values,
            n=self._dimensions(),
            themes=self.themes,
            on_change=self._on_cell_change,
            on_delete=None if (self._is_derived() or is_const) else self._delete_row,
            read_only=self._is_derived(),
        )

    def _load_rows(self):
        raw = self._entry_values()

        # Normalizar: si el pool tiene strings sueltos en lugar de listas,
        # envolverlos como una sola fila
        if raw and not isinstance(raw[0], (list, tuple)):
            values = [raw]
        else:
            values = raw

        if is_constant_type(self._var_type()):
            values = values[:1]
        rows = [self._make_row(v) for v in values] or [self._make_row()]
        self.rows_col.controls = rows
        self._update_header()
        self._update_formula_badge()
        self._apply_derived_state()
        self._refresh_stats()

    def _delete_row(self, row: VectorRow):
        if row in self.rows_col.controls:
            self.rows_col.controls.remove(row)
            if not self.rows_col.controls:
                self.rows_col.controls.append(self._make_row())
            self.sync_pool()
            self._notify_change()
            try:
                self.rows_col.update()
            except Exception:
                pass

    def _add_row(self, e=None):
        if self._is_derived() or is_constant_type(self._var_type()):
            return
        self.rows_col.controls.append(self._make_row())
        self.sync_pool()
        self._notify_change()
        try:
            self.rows_col.update()
        except Exception:
            pass

    def _apply_derived_state(self):
        if not hasattr(self, "add_row_btn"):
            return
        t     = self.themes.actual_theme
        block = self._is_derived() or is_constant_type(self._var_type())
        self.add_row_btn.disabled   = block
        self.add_row_btn.icon_color = _c(t, "primary", 0.30) if block else t["primary"]
        try:
            self.add_row_btn.update()
        except Exception:
            pass

    # ── Stats ──────────────────────────────────────────────────────────────────

    def _build_stats_row(self):
        t      = self.themes.actual_theme
        values = self._entry_values()
        n      = len(values)
        dims   = self._dimensions()

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

        chips = [chip("n", str(n) if n else "—"), chip("dim", str(dims))]

        if n > 0:
            try:
                # Norma media de los vectores
                norms = []
                for row_vals in values:
                    s = sum(float(v) ** 2 for v in row_vals)
                    norms.append(math.sqrt(s))
                mean_norm = sum(norms) / len(norms)
                chips.append(chip("‖v̄‖", _fmt(mean_norm)))
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
        n    = self._dimensions()
        has_special = any(ch in name for ch in ("^", "_", "\\"))
        latex_name  = name if has_special else f"\\text{{{name}}}"
        return f"$${latex_name} \\in \\mathbb{{R}}^{{{n}}}$$"

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

    def _entry_values(self) -> list:
        return self._entry.get("values", [])

    def _entry_errors(self) -> list:
        return self._entry.get("errors", [])

    def _var_type(self) -> str:
        return infer_variable_type(self._entry)

    def _dimensions(self) -> int:
        return self._entry.get("dimensions", 2)

    def _is_derived(self) -> bool:
        formula = self._entry.get("formula", "")
        return (
            is_formula_type(self._var_type())
            and isinstance(formula, str)
            and formula.strip() != ""
        )

    # ── Events ─────────────────────────────────────────────────────────────────

    def _on_cell_change(self):
        self.sync_pool()
        self._notify_change()

    def _on_var_switch(self, new_name=None):
        if new_name is None:
            new_name = self.var_dropdown.value
        if new_name and new_name != self.current_name and new_name in self.pool:
            self.current_name = new_name
            self.width = _card_width(self._dimensions())
            self._load_rows()
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

    def sync_pool(self):
        values = []
        for row in self.rows_col.controls:
            if isinstance(row, VectorRow):
                values.append(row.get_values())
        if is_constant_type(self._var_type()):
            values = values[:1]
        entry = self._entry
        entry["values"] = values
        entry["type"]   = infer_variable_type(entry)

    def sync_with_pool(self):
        values = self._entry_values()
        if is_constant_type(self._var_type()):
            values = values[:1]
        rows = self.rows_col.controls
        if len(rows) != max(1, len(values)):
            self._load_rows()
            return
        for i, row in enumerate(rows):
            if isinstance(row, VectorRow) and i < len(values):
                row.vector_values = list(values[i])
                row._build_ui()
                try:
                    row.update()
                except Exception:
                    pass
        self.width = _card_width(self._dimensions())
        self._update_header()
        self._update_formula_badge()
        self._update_accent()
        self._apply_derived_state()
        self._refresh_stats()
        if not self._just_changed:
            try:
                self.update()
            except Exception:
                pass
        self._just_changed = False