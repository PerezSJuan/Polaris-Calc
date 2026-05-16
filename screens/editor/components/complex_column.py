"""
complex_column.py
─────────────────
Tarjeta de columna para variables de números complejos.

Modos de representación (solo visual — el pool siempre almacena binomial "a+bj"):
  • MODE_BINOMIAL   → celdas editables: parte real  +  parte imaginaria
  • MODE_POLAR_DEG  → celdas editables: módulo r    +  ángulo θ en grados
  • MODE_POLAR_RAD  → celdas editables: módulo r    +  ángulo θ en radianes

Editar en cualquier modo convierte y guarda en binomial al perder el foco
(igual que EditableColumn — on_blur, no on_change, para no perder el foco).
"""

import math
import asyncio
import flet as ft
from flet_base.translations import instance_translation_manager as tm
import flet_base.components.texts as txt
from screens.editor.components.latex_dropdown import latex_dropdown
from screens.editor.components.column import LatexCell
from screens.editor.modals import open_variable_settings_modal
from utils.variable_types import (
    is_constant_type,
    is_formula_type,
    infer_variable_type,
)

# ── Design tokens ──────────────────────────────────────────────────────────────
_CARD_W = 310
_PADDING = 15
_CARD_RADIUS = 12

MODE_BINOMIAL = "binomial"
MODE_POLAR_DEG = "polar_deg"
MODE_POLAR_RAD = "polar_rad"

_ENTRY_FORM_TO_MODE = {
    "rectangular": MODE_BINOMIAL,
    "binomial": MODE_BINOMIAL,
    "polar_deg": MODE_POLAR_DEG,
    "polar_rad": MODE_POLAR_RAD,
}

_MODE_TO_ENTRY_FORM = {
    MODE_BINOMIAL: "binomial",
    MODE_POLAR_DEG: "polar_deg",
    MODE_POLAR_RAD: "polar_rad",
}

_MODE_META = [
    (MODE_BINOMIAL, "a+bi", "Forma binomial", ft.Icons.FUNCTIONS),
    (MODE_POLAR_DEG, "r∠θ°", "Polar – grados", ft.Icons.EXPLORE_OUTLINED),
    (MODE_POLAR_RAD, "re^iθ", "Polar – radianes", ft.Icons.ROTATE_RIGHT),
]


# ── Helpers ────────────────────────────────────────────────────────────────────


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
    if "complex" in vt:
        return t.get("complex_accent", ft.Colors.PURPLE_300)
    return t["primary"]


def _fmt(v: float) -> str:
    if not math.isfinite(v):
        return str(v)
    if v == int(v) and abs(v) < 1e12:
        return str(int(v))
    return f"{v:.6g}"


def _parse_complex(value) -> complex:
    if isinstance(value, complex):
        return value
    try:
        s = str(value).strip().strip("()")
        return complex(s)
    except Exception:
        return complex(0, 0)


def _complex_to_str(real: float, imag: float) -> str:
    """Serializa como 'a+bj' sin paréntesis — seguro para msgpack."""
    sign = "+" if imag >= 0 else ""
    return f"{_fmt(real)}{sign}{_fmt(imag)}j"


# ── ComplexRow ─────────────────────────────────────────────────────────────────


class ComplexRow(ft.Container):
    """
    Fila con tres pares de LatexCell editables según el modo activo.

    Usa on_blur (no on_change) para leer y convertir, igual que EditableColumn,
    evitando la pérdida de foco al escribir.

    El valor canónico se guarda como dos floats (_real, _imag) para evitar
    que msgpack intente serializar un objeto complex nativo de Python.
    """

    def __init__(
        self,
        value="0+0j",
        themes=None,
        on_change=None,
        read_only=False,
        display_mode=MODE_BINOMIAL,
        on_delete=None,
        on_cell_focus=None,
        on_cell_blur=None,
    ):
        super().__init__()
        self.themes = themes
        self._on_change = on_change  # callback() sin args — se llama en on_blur
        self._on_delete = on_delete
        self._on_cell_focus_cb = on_cell_focus
        self._on_cell_blur_cb = on_cell_blur
        self.read_only = read_only
        self._mode = display_mode

        # Dos floats en lugar de complex nativo (msgpack no serializa complex)
        _parsed = _parse_complex(value)
        self._real: float = _parsed.real
        self._imag: float = _parsed.imag

        self.padding = ft.Padding(0, 2, 0, 2)
        self._build_ui()

    # ── Build ──────────────────────────────────────────────────────────────────

    def _build_ui(self):
        t = self.themes.actual_theme

        self._del_btn = ft.IconButton(
            icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
            icon_size=14,
            width=24,
            height=24,
            padding=0,
            tooltip=tm.translate("Eliminar fila"),
            on_click=self._handle_delete,
            icon_color=ft.Colors.RED_400,
            opacity=0.5,
            visible=(self._on_delete is not None) and not self.read_only,
        )

        # ── Binomial ───────────────────────────────────────────────────────────
        self._cell_real = LatexCell(
            value=_fmt(self._real),
            themes=self.themes,
            on_change=None,
            on_focus=self._on_cell_focus,
            on_blur=self._on_blur_binomial,
            read_only=self.read_only,
            compact=True,
        )
        self._cell_imag = LatexCell(
            value=_fmt(self._imag),
            themes=self.themes,
            on_change=None,
            on_focus=self._on_cell_focus,
            on_blur=self._on_blur_binomial,
            read_only=self.read_only,
            compact=True,
        )
        self._lbl_plus = ft.Text("+", size=12, color=_c(t, "on_surface", 0.45))
        self._lbl_i = ft.Text(
            "i", size=12, weight=ft.FontWeight.BOLD, color=_c(t, "on_surface", 0.65)
        )

        # ── Polar ──────────────────────────────────────────────────────────────
        mod = math.sqrt(self._real**2 + self._imag**2)
        arg = math.atan2(self._imag, self._real)

        self._cell_r = LatexCell(
            value=_fmt(mod),
            themes=self.themes,
            on_change=None,
            on_focus=self._on_cell_focus,
            on_blur=self._on_blur_polar,
            read_only=self.read_only,
            compact=True,
        )
        self._cell_deg = LatexCell(
            value=_fmt(math.degrees(arg)),
            themes=self.themes,
            on_change=None,
            on_focus=self._on_cell_focus,
            on_blur=self._on_blur_polar,
            read_only=self.read_only,
            compact=True,
        )
        self._cell_rad = LatexCell(
            value=_fmt(arg),
            themes=self.themes,
            on_change=None,
            on_focus=self._on_cell_focus,
            on_blur=self._on_blur_polar,
            read_only=self.read_only,
            compact=True,
        )
        self._lbl_angle = ft.Text("∠", size=13, color=_c(t, "on_surface", 0.45))
        self._lbl_deg_unit = ft.Text("°", size=11, color=_c(t, "on_surface", 0.50))
        self._lbl_rad_unit = ft.Text("rad", size=10, color=_c(t, "on_surface", 0.50))

        self._row_binomial = ft.Row(
            [self._cell_real, self._lbl_plus, self._cell_imag, self._lbl_i],
            spacing=3,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self._row_polar_deg = ft.Row(
            [self._cell_r, self._lbl_angle, self._cell_deg, self._lbl_deg_unit],
            spacing=3,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self._row_polar_rad = ft.Row(
            [self._cell_r, self._lbl_angle, self._cell_rad, self._lbl_rad_unit],
            spacing=3,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.content = ft.Row(
            [self._row_for(self._mode), self._del_btn],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
            expand=True,
        )

    def _row_for(self, mode: str) -> ft.Row:
        return {
            MODE_BINOMIAL: self._row_binomial,
            MODE_POLAR_DEG: self._row_polar_deg,
            MODE_POLAR_RAD: self._row_polar_rad,
        }[mode]

    # ── on_blur handlers (leen, convierten, notifican) ─────────────────────────

    async def _on_blur_binomial(self, e=None):
        try:
            self._real = float(self._cell_real.value or 0)
            self._imag = float(self._cell_imag.value or 0)
        except ValueError:
            pass
        if self._on_change:
            self._on_change()
        await self._on_cell_blur(e)

    async def _on_blur_polar(self, e=None):
        if self._mode == MODE_POLAR_DEG:
            try:
                r = float(self._cell_r.value or 0)
                deg = float(self._cell_deg.value or 0)
                rad = math.radians(deg)
                self._real = r * math.cos(rad)
                self._imag = r * math.sin(rad)
            except ValueError:
                pass
        else:
            try:
                r = float(self._cell_r.value or 0)
                rad = float(self._cell_rad.value or 0)
                self._real = r * math.cos(rad)
                self._imag = r * math.sin(rad)
            except ValueError:
                pass
        if self._on_change:
            self._on_change()
        await self._on_cell_blur(e)

    async def _on_cell_focus(self, e=None):
        if not self._on_cell_focus_cb:
            return
        if asyncio.iscoroutinefunction(self._on_cell_focus_cb):
            await self._on_cell_focus_cb(e)
        else:
            self._on_cell_focus_cb(e)

    async def _on_cell_blur(self, e=None):
        if not self._on_cell_blur_cb:
            return
        if asyncio.iscoroutinefunction(self._on_cell_blur_cb):
            await self._on_cell_blur_cb(e)
        else:
            self._on_cell_blur_cb(e)

    # ── Cambio de modo ─────────────────────────────────────────────────────────

    def set_display_mode(self, mode: str):
        if mode == self._mode:
            return
        self._mode = mode
        self._sync_cells_to_value()
        self.content.controls[0] = self._row_for(mode)
        try:
            self.update()
        except Exception:
            pass

    def _sync_cells_to_value(self):
        mod = math.sqrt(self._real**2 + self._imag**2)
        arg = math.atan2(self._imag, self._real)
        self._cell_real.value = _fmt(self._real)
        self._cell_imag.value = _fmt(self._imag)
        self._cell_r.value = _fmt(mod)
        self._cell_deg.value = _fmt(math.degrees(arg))
        self._cell_rad.value = _fmt(arg)

    # ── Propiedad pública ──────────────────────────────────────────────────────

    @property
    def complex_value(self) -> complex:
        return complex(self._real, self._imag)

    @complex_value.setter
    def complex_value(self, c: complex):
        self._real = c.real
        self._imag = c.imag
        self._sync_cells_to_value()
        try:
            self.update()
        except Exception:
            pass

    async def _handle_delete(self, e):
        if self._on_delete:
            if asyncio.iscoroutinefunction(self._on_delete):
                await self._on_delete(self)
            else:
                self._on_delete(self)

    def has_focused_cell(self, cell) -> bool:
        if cell is None:
            return False
        return cell in (
            self._cell_real.edit_field,
            self._cell_imag.edit_field,
            self._cell_r.edit_field,
            self._cell_deg.edit_field,
            self._cell_rad.edit_field,
        )


# ── ComplexColumn ──────────────────────────────────────────────────────────────


class ComplexColumn(ft.Container):
    """
    Tarjeta de columna para números complejos.

    Patrón visual idéntico a EditableColumn (column.py):
    accent strip · header con icon + LaTeX + mode buttons (a+bi / r∠θ° / re^iθ)
    + delete_variable + settings · formula badge · var dropdown · rows ·
    stats strip · botón ➕.
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
        self._on_manage_cb = on_manage
        self._just_changed = False
        entry_form = (
            str(self.pool.get(self.current_name, {}).get("form", "")).strip().lower()
        )
        self._display_mode = _ENTRY_FORM_TO_MODE.get(entry_form, MODE_BINOMIAL)
        self._focused_cell = None

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

        self._build_ui()

    # ── BUILD ──────────────────────────────────────────────────────────────────

    def _build_ui(self):
        t = self.themes.actual_theme
        acc = _type_accent(self._var_type(), self.themes)

        # ── Accent strip ───────────────────────────────────────────────────────
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

        # ── Header ─────────────────────────────────────────────────────────────
        self.header_display = txt.markdown(self._get_latex_header(), size=14)

        def _mgr_btn(icon, action, color=None, tooltip=""):
            return ft.IconButton(
                icon=icon,
                icon_size=16,
                padding=ft.Padding.all(4),
                tooltip=tooltip,
                on_click=lambda e, a=action: asyncio.create_task(
                    self._on_manage_click(a, e)
                ),
                icon_color=color or _c(t, "on_surface", 0.65),
                visible=self._on_manage_cb is not None,
            )

        self.move_left_btn = _mgr_btn(
            ft.Icons.ARROW_BACK_IOS_NEW,
            "move_left",
            tooltip=tm.translate("Mover a la izquierda"),
        )
        self.move_right_btn = _mgr_btn(
            ft.Icons.ARROW_FORWARD_IOS,
            "move_right",
            tooltip=tm.translate("Mover a la derecha"),
        )
        self.remove_from_tab_btn = _mgr_btn(
            ft.Icons.REMOVE_CIRCLE_OUTLINE,
            "remove_from_tab",
            tooltip=tm.translate("Eliminar de la pestaña"),
        )
        self.delete_variable_btn = _mgr_btn(
            ft.Icons.DELETE_OUTLINE_ROUNDED,
            "delete_variable",
            color=ft.Colors.RED_400,
            tooltip=tm.translate("Eliminar variable"),
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

        # Botón de configuración (⚙)
        self.settings_btn = ft.IconButton(
            icon=ft.Icons.SETTINGS_OUTLINED,
            on_click=self._open_settings_modal,
            icon_size=18,
            tooltip=tm.translate("Configurar magnitud y unidad"),
            icon_color=_c(t, "primary", 0.60),
            style=ft.ButtonStyle(padding=ft.Padding.all(4)),
        )

        # ── Botones de modo ────────────────────────────────────────────────────
        self._mode_btns: dict[str, ft.Container] = {}
        mode_row = ft.Row(spacing=2, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        for mode_key, label, tooltip, icon in _MODE_META:
            hit_area, btn = self._build_mode_btn(mode_key, label, tooltip, icon, acc, t)
            self._mode_btns[mode_key] = btn
            mode_row.controls.append(hit_area)

        _header = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.BLUR_CIRCULAR_ROUNDED,
                                        size=18,
                                        color=acc,
                                    ),
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
                    ft.Row(
                        [mode_row],
                        alignment=ft.MainAxisAlignment.END,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=6,
            ),
            padding=ft.Padding(left=_PADDING, top=10, right=6, bottom=6),
        )

        # ── Formula badge ──────────────────────────────────────────────────────
        self.formula_badge = ft.Container(
            visible=False,
            content=ft.Text(
                "",
                size=11,
                weight=ft.FontWeight.W_500,
                overflow=ft.TextOverflow.ELLIPSIS,
                max_lines=1,
            ),
            border_radius=6,
            padding=ft.Padding(8, 3, 8, 3),
            margin=ft.Margin(left=_PADDING, right=_PADDING, top=0, bottom=0),
        )

        # ── Var dropdown ───────────────────────────────────────────────────────
        self.var_dropdown = latex_dropdown(
            label=tm.translate("Variable"),
            options=self.available_vars_getter(),
            value=self.current_name,
            on_change=self._on_var_switch,
            width=150,
        )

        # ── Rows ───────────────────────────────────────────────────────────────
        self.rows_col = ft.Column(
            spacing=6,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
        )

        # ── Add-row button (antes de _load_rows) ───────────────────────────────
        self.add_row_btn = ft.IconButton(
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            on_click=self._add_row,
            icon_size=24,
            tooltip=tm.translate("Agregar fila"),
            icon_color=t["primary"],
        )

        # ── Stats strip (antes de _load_rows) ──────────────────────────────────
        self._stats_container = ft.Container(
            content=self._build_stats_row(),
            padding=ft.Padding(12, 10, 12, 10),
            bgcolor=_c(t, "on_surface", 0.03),
            border=ft.Border(top=ft.BorderSide(1, _c(t, "on_surface", 0.07))),
        )

        self._load_rows()

        # ── Ensamblado ─────────────────────────────────────────────────────────
        self.content = ft.Column(
            [
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
                ft.Container(
                    content=self.rows_col,
                    padding=ft.Padding(left=_PADDING, right=_PADDING, top=4, bottom=15),
                    expand=True,
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

    # ── Mode button builder ────────────────────────────────────────────────────

    def _build_mode_btn(
        self, mode_key, label, tooltip, icon, acc, t
    ) -> tuple[ft.GestureDetector, ft.Container]:
        is_active = mode_key == self._display_mode
        visual_btn = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(
                        icon,
                        size=11,
                        color=acc if is_active else _c(t, "on_surface", 0.40),
                    ),
                    ft.Text(
                        label,
                        size=9,
                        weight=ft.FontWeight.W_600
                        if is_active
                        else ft.FontWeight.NORMAL,
                        color=acc if is_active else _c(t, "on_surface", 0.50),
                    ),
                ],
                spacing=2,
                tight=True,
            ),
            padding=ft.Padding(5, 3, 5, 3),
            border_radius=5,
            tooltip=tooltip,
            bgcolor=ft.Colors.with_opacity(0.14, acc)
            if is_active
            else ft.Colors.with_opacity(0.04, t["on_surface"]),
            border=ft.Border.all(
                1,
                ft.Colors.with_opacity(0.45, acc)
                if is_active
                else ft.Colors.with_opacity(0.08, t["on_surface"]),
            ),
            data=mode_key,
        )
        hit_area = ft.GestureDetector(
            content=visual_btn,
            on_tap_down=lambda e, m=mode_key: self._on_mode_change(m),
            mouse_cursor=ft.MouseCursor.CLICK,
        )
        return hit_area, visual_btn

    # ── Mode change ────────────────────────────────────────────────────────────

    def _on_mode_change(self, mode: str):
        if mode == self._display_mode:
            return
        self._display_mode = mode
        self._entry["form"] = _MODE_TO_ENTRY_FORM.get(mode, MODE_BINOMIAL)
        self._apply_display_mode(mode)

    def _apply_display_mode(self, mode: str):
        t = self.themes.actual_theme
        acc = _type_accent(self._var_type(), self.themes)

        for m, btn in self._mode_btns.items():
            is_active = m == mode
            btn.content.controls[0].color = (
                acc if is_active else _c(t, "on_surface", 0.40)
            )
            btn.content.controls[1].weight = (
                ft.FontWeight.W_600 if is_active else ft.FontWeight.NORMAL
            )
            btn.content.controls[1].color = (
                acc if is_active else _c(t, "on_surface", 0.50)
            )
            btn.bgcolor = (
                ft.Colors.with_opacity(0.14, acc)
                if is_active
                else ft.Colors.with_opacity(0.04, t["on_surface"])
            )
            btn.border = ft.Border.all(
                1,
                ft.Colors.with_opacity(0.45, acc)
                if is_active
                else ft.Colors.with_opacity(0.08, t["on_surface"]),
            )
            try:
                btn.update()
            except Exception:
                pass

        for row in self.rows_col.controls:
            if isinstance(row, ComplexRow):
                row.set_display_mode(mode)

    # ── Rows ───────────────────────────────────────────────────────────────────

    def _make_row(self, value="0+0j") -> ComplexRow:
        is_const = is_constant_type(self._var_type())
        return ComplexRow(
            value=value,
            themes=self.themes,
            on_change=self._on_cell_change,
            read_only=self._is_derived(),
            display_mode=self._display_mode,
            on_delete=None if (self._is_derived() or is_const) else self._delete_row,
            on_cell_focus=self._on_cell_focus,
            on_cell_blur=self._on_cell_blur,
        )

    def _load_rows(self):
        values = self._entry_values()
        if is_constant_type(self._var_type()):
            values = values[:1]
        rows = [self._make_row(v) for v in values] or [self._make_row()]
        self.rows_col.controls = rows
        self._update_header()
        self._update_formula_badge()
        self._apply_derived_state()
        self._refresh_stats()

    def _delete_row(self, row: ComplexRow):
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
        t = self.themes.actual_theme
        block = self._is_derived() or is_constant_type(self._var_type())
        self.add_row_btn.disabled = block
        self.add_row_btn.icon_color = _c(t, "primary", 0.30) if block else t["primary"]
        try:
            self.add_row_btn.update()
        except Exception:
            pass

    # ── Stats ──────────────────────────────────────────────────────────────────

    def _build_stats_row(self):
        t = self.themes.actual_theme
        values = [_parse_complex(v) for v in self._entry_values()]
        n = len(values)

        def chip(label, val_str):
            return ft.Column(
                [
                    ft.Text(
                        label,
                        size=9,
                        weight=ft.FontWeight.W_600,
                        color=_c(t, "on_surface", 0.38),
                    ),
                    ft.Text(
                        val_str,
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
            c = values[0]
            mod = abs(c)
            arg = math.degrees(math.atan2(c.imag, c.real))
            chips = [
                chip("n", "1"),
                chip("|z|", _fmt(mod)),
                chip("arg", f"{_fmt(arg)}°"),
            ]
        else:
            mods = [abs(c) for c in values]
            args = [math.degrees(math.atan2(c.imag, c.real)) for c in values]
            mean_m = sum(mods) / n
            mean_a = sum(args) / n
            chips = [
                chip("n", str(n)),
                chip("|z̄|", _fmt(mean_m)),
                chip("ārg", f"{_fmt(mean_a)}°"),
            ]

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
        has_special = any(ch in name for ch in ("^", "_", "\\"))
        latex_name = name if has_special else f"\\text{{{name}}}"
        return f"$${latex_name} \\in \\mathbb{{C}}$$"

    def _update_header(self):
        self.header_display.value = self._get_latex_header()
        try:
            self.header_display.update()
        except Exception:
            pass

    def _update_formula_badge(self):
        formula = self._entry.get("formula", "").strip()
        acc = _type_accent(self._var_type(), self.themes)
        if formula:
            self.formula_badge.content.value = f"ƒ  {formula}"
            self.formula_badge.content.color = acc
            self.formula_badge.bgcolor = ft.Colors.with_opacity(0.10, acc)
            self.formula_badge.border = ft.Border.all(
                1, ft.Colors.with_opacity(0.20, acc)
            )
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
        page = self.page
        if not page:
            return

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

    # ── Properties ─────────────────────────────────────────────────────────────

    @property
    def _entry(self):
        return self.pool.get(self.current_name, {})

    def _entry_values(self) -> list:
        return self._entry.get("values", [])

    def _var_type(self) -> str:
        return infer_variable_type(self._entry)

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

    async def _on_cell_focus(self, e):
        self._focused_cell = getattr(e, "control", None)

    async def _on_cell_blur(self, e):
        cell = getattr(e, "control", None)
        if self._focused_cell is cell:
            self._focused_cell = None

    def _on_var_switch(self, new_name=None):
        if new_name is None:
            new_name = self.var_dropdown.value
        if new_name and new_name != self.current_name and new_name in self.pool:
            self.current_name = new_name
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
        self.var_dropdown.value = self.current_name
        try:
            self.var_dropdown.update()
        except Exception:
            pass

    def sync_pool(self):
        """Lee las celdas y escribe en el pool siempre en binomial."""
        values = []
        for row in self.rows_col.controls:
            if isinstance(row, ComplexRow):
                values.append(_complex_to_str(row._real, row._imag))
        if is_constant_type(self._var_type()):
            values = values[:1]
        entry = self._entry
        entry["values"] = values
        entry["type"] = infer_variable_type(entry)

    def sync_with_pool(self):
        """Actualiza la UI leyendo los valores del pool."""
        entry = self._entry

        # Sincronizar modo de representación
        form = str(entry.get("form", "")).strip().lower()
        new_mode = _ENTRY_FORM_TO_MODE.get(form, MODE_BINOMIAL)
        if new_mode != self._display_mode:
            self._display_mode = new_mode
            self._apply_display_mode(new_mode)

        values = self._entry_values()
        if is_constant_type(self._var_type()):
            values = values[:1]
        rows = self.rows_col.controls
        if len(rows) != max(1, len(values)):
            self._load_rows()
            return
        for i, row in enumerate(rows):
            if isinstance(row, ComplexRow) and i < len(values):
                if row.has_focused_cell(self._focused_cell):
                    continue
                row.complex_value = _parse_complex(values[i])
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
