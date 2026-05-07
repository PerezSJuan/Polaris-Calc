import asyncio
import flet as ft
from flet_base.translations import instance_translation_manager as tm
import flet_base.components.texts as txt
from flet_base.components.inputs import dropdown
from screens.editor.components.latex_dropdown import latex_dropdown
from utils.variable_types import (
    is_boolean_type,
    is_constant_type,
    is_formula_type,
    infer_variable_type,
)

# ── Design tokens ──────────────────────────────────────────────────────────────
_CARD_W = 245
_PADDING = 15
_CARD_RADIUS = 12
_CELL_H = 35
_CELL_RADIUS = 6
_BTN_SPACE = 30


def _c(t, key, opacity=1.0):
    col = t[key]
    return ft.Colors.with_opacity(opacity, col) if opacity < 1.0 else col


class BooleanCell(ft.Container):
    """
    A polished button-like component for boolean values.
    """

    def __init__(self, value, themes, on_change, read_only=False):
        super().__init__()
        self.value_bool = bool(value)
        self.themes = themes
        self._on_change_cb = on_change
        self.read_only = read_only

        self.height = _CELL_H
        self.border_radius = _CELL_RADIUS
        self.alignment = ft.Alignment.CENTER
        self.mouse_cursor = (
            ft.MouseCursor.CLICK if not read_only else ft.MouseCursor.BASIC
        )
        self.on_click = self._toggle if not read_only else None
        self.on_hover = self._handle_hover
        self.animate = ft.Animation(200, ft.AnimationCurve.DECELERATE)
        self.expand = True
        self._update_style()

    @property
    def value(self):
        return str(self.value_bool)

    @value.setter
    def value(self, val):
        if isinstance(val, bool):
            self.value_bool = val
        elif isinstance(val, (int, float)):
            self.value_bool = bool(val)
        else:
            self.value_bool = str(val).lower() == "true"
        self._update_style()
        try:
            if self.page:
                self.update()
        except:
            pass

    def _update_style(self, hovered=False):
        t = self.themes.actual_theme
        is_dark = t.get("background") == self.themes.dark_theme.get("background")
        acc = ft.Colors.TEAL_400 if not is_dark else ft.Colors.TEAL_200

        if self.value_bool:
            self.bgcolor = acc if not hovered else ft.Colors.with_opacity(0.8, acc)
            self.content = ft.Text(
                "True", color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD
            )
            self.border = None
        else:
            base_bg = ft.Colors.with_opacity(0.05, t["on_surface"])
            self.bgcolor = (
                base_bg if not hovered else ft.Colors.with_opacity(0.1, t["on_surface"])
            )
            self.content = ft.Text(
                "False", color=ft.Colors.with_opacity(0.7, t["on_surface"]), size=12
            )
            self.border = ft.Border.all(1, ft.Colors.with_opacity(0.1, t["on_surface"]))

    def _handle_hover(self, e):
        if self.read_only:
            return
        self._update_style(hovered=(e.data == "true"))
        try:
            self.update()
        except:
            pass

    async def _toggle(self, e):
        if self.read_only:
            return
        self.value_bool = not self.value_bool
        self._update_style(hovered=True)
        try:
            await self.update()
        except:
            pass
        if self._on_change_cb:
            if asyncio.iscoroutinefunction(self._on_change_cb):
                await self._on_change_cb(e)
            else:
                self._on_change_cb(e)


class BooleanColumn(ft.Container):
    """
    A column card specialized for boolean data, rendered as a list of buttons.
    """

    def __init__(self, pool, current_name, on_change, available_vars_getter, themes):
        super().__init__()
        self.pool = pool
        self.current_name = current_name
        self.on_change = on_change
        self.available_vars_getter = available_vars_getter
        self.themes = themes
        self._just_changed = False

        t = themes.actual_theme
        self.width = _CARD_W
        self.border_radius = _CARD_RADIUS
        self.bgcolor = _c(t, "surface")
        self.border = ft.Border.all(1, _c(t, "on_surface", 0.10))
        self.shadow = [
            ft.BoxShadow(
                blur_radius=15,
                offset=ft.Offset(0, 5),
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            )
        ]
        self.clip_behavior = ft.ClipBehavior.ANTI_ALIAS
        self.expand = True

        self._build_ui()

    def _build_ui(self):
        t = self.themes.actual_theme
        is_dark = t.get("background") == self.themes.dark_theme.get("background")
        acc = ft.Colors.TEAL_400 if not is_dark else ft.Colors.TEAL_200

        self._accent_strip = ft.Container(
            height=3,
            bgcolor=acc,
            border_radius=ft.BorderRadius(
                top_left=_CARD_RADIUS, top_right=_CARD_RADIUS, bottom_left=0, bottom_right=0
            ),
        )

        self.header_display = txt.markdown(self._get_latex_header(), size=15)

        _header = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CHECK_BOX_OUTLINED, size=18, color=acc),
                    self.header_display,
                ],
                spacing=5,
            ),
            padding=ft.Padding(left=_PADDING, top=10, right=6, bottom=6),
        )

        self.formula_badge = ft.Container(
            visible=False,
            content=ft.Text("", size=11, weight=ft.FontWeight.W_500),
            border_radius=8,
            padding=ft.Padding(10, 4, 10, 4),
            margin=ft.Margin(15, 0, 15, 5),
        )

        self.var_dropdown = latex_dropdown(
            label=tm.translate("Variable"),
            options=self.available_vars_getter(),
            value=self.current_name,
            on_change=self._on_var_switch,
            width=150,
        )

        self.rows_col = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
        )

        self._stats_container = ft.Container(
            content=self._build_stats_row(),
            padding=ft.Padding(15, 12, 15, 12),
            bgcolor=_c(t, "on_surface", 0.03),
            border=ft.Border(top=ft.BorderSide(1, _c(t, "on_surface", 0.08))),
        )

        self.add_row_btn = ft.IconButton(
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            icon_size=24,
            tooltip=tm.translate("Agregar fila"),
            on_click=self._add_row,
            icon_color=t["primary"],
        )

        self._load_rows()

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
                                height=1, thickness=0.5, color=_c(t, "on_surface", 0.08)
                            ),
                        ],
                        spacing=12,
                    ),
                    padding=ft.Padding(15, 5, 15, 10),
                ),
                ft.Container(
                    content=self.rows_col,
                    padding=ft.Padding(left=_PADDING, right=_PADDING, top=0, bottom=15),
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

    def _build_stats_row(self):
        t = self.themes.actual_theme
        vals = self._entry_values()
        trues = sum(1 for v in vals if bool(v))
        falses = len(vals) - trues

        def stat(label, val, color=None):
            return ft.Column(
                [
                    ft.Text(
                        label,
                        size=9,
                        weight=ft.FontWeight.W_600,
                        color=_c(t, "on_surface", 0.4),
                    ),
                    ft.Text(
                        val,
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=color or _c(t, "on_surface", 0.8),
                    ),
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )

        return ft.Row(
            [
                stat("N", str(len(vals))),
                stat("TRUE", str(trues), ft.Colors.TEAL_400),
                stat("FALSE", str(falses)),
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        )

    def _refresh_stats(self):
        self._stats_container.content = self._build_stats_row()
        try:
            self._stats_container.update()
        except:
            pass

    @property
    def _entry(self):
        return self.pool.get(self.current_name, {})

    def _var_type(self):
        return infer_variable_type(self._entry)

    def _is_derived(self):
        formula = self._entry.get("formula", "")
        return (
            is_formula_type(self._var_type())
            and isinstance(formula, str)
            and formula.strip() != ""
        )

    def _entry_values(self):
        v = self._entry.get("values", [])
        return v if isinstance(v, list) else []

    def _get_latex_header(self):
        d = self.current_name
        ln = d if any(c in d for c in ("^", "_", "\\")) else f"\\text{{{d}}}"
        return f"$${ln}$$"

    def _load_rows(self):
        vals = self._entry_values()
        if is_constant_type(self._var_type()):
            vals = vals[:1]
        if not vals and not self._is_derived():
            vals = [False]
        self.rows_col.controls = [self._make_row_item(v) for v in vals]
        self._update_header()
        self._update_formula_badge()
        self._apply_derived_state()
        self._refresh_stats()

    def _make_row_item(self, val=False):
        btn = BooleanCell(
            value=val,
            themes=self.themes,
            read_only=self._is_derived(),
            on_change=self._on_cell_change,
        )

        if self._is_derived() or is_constant_type(self._var_type()):
            return btn

        return ft.Row(
            [
                btn,
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                    icon_size=13,
                    width=22,
                    height=22,
                    padding=0,
                    tooltip=tm.translate("Eliminar fila"),
                    on_click=lambda _: self._remove_row(btn),
                    opacity=0.4,
                    icon_color=ft.Colors.RED_400,
                ),
            ],
            spacing=5,
            alignment=ft.MainAxisAlignment.END,
        )

    def _remove_row(self, btn):
        # Find the row container and remove it
        for idx, row in enumerate(self.rows_col.controls):
            if isinstance(row, ft.Row) and row.controls[0] is btn:
                self.rows_col.controls.pop(idx)
                break
        self.sync_pool()
        self._notify_change()
        try:
            self.rows_col.update()
        except:
            pass

    def _apply_derived_state(self):
        t = self.themes.actual_theme
        block = self._is_derived() or is_constant_type(self._var_type())
        self.add_row_btn.disabled = block
        self.add_row_btn.icon_color = _c(t, "primary", 0.30) if block else t["primary"]
        try:
            self.add_row_btn.update()
        except:
            pass

    def _update_header(self):
        self.header_display.value = self._get_latex_header()
        try:
            self.header_display.update()
        except:
            pass

    def _update_formula_badge(self):
        f = self._entry.get("formula", "")
        derived = self._is_derived()
        self.formula_badge.visible = derived
        if derived:
            is_dark = self.themes.actual_theme.get(
                "background"
            ) == self.themes.dark_theme.get("background")
            acc = ft.Colors.TEAL_400 if not is_dark else ft.Colors.TEAL_300
            self.formula_badge.content.value = f"ƒ  {f}"
            self.formula_badge.content.color = acc
            self.formula_badge.bgcolor = ft.Colors.with_opacity(0.1, acc)
            self.formula_badge.border = ft.Border.all(
                1, ft.Colors.with_opacity(0.2, acc)
            )
        try:
            self.formula_badge.update()
        except:
            pass

    def update_dropdown(self):
        self.var_dropdown.options = self.available_vars_getter()
        self.var_dropdown.value = self.current_name
        try:
            self.var_dropdown.update()
        except:
            pass

    def sync_with_pool(self):
        vals = self._entry_values()
        rows = self.rows_col.controls
        target = max(1, len(vals)) if not self._is_derived() else len(vals)
        if is_constant_type(self._var_type()):
            target = 1

        # Re-load if lengths differ or mode changed
        if len(rows) != target:
            self._load_rows()
            return

        for idx, item in enumerate(rows):
            cell = item.controls[0] if isinstance(item, ft.Row) else item
            v = vals[idx] if idx < len(vals) else False
            cell.value = v

        self._update_header()
        self._update_formula_badge()
        self._apply_derived_state()
        self._refresh_stats()
        try:
            self.rows_col.update()
        except:
            pass

    def sync_pool(self):
        if self._is_derived():
            values = self._entry_values()
        else:
            values = []
            for item in self.rows_col.controls:
                cell = item.controls[0] if isinstance(item, ft.Row) else item
                values.append(cell.value_bool)

        if is_constant_type(self._var_type()):
            values = values[:1]

        self.pool[self.current_name]["values"] = values

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

    def _add_row(self, e):
        if self._is_derived() or is_constant_type(self._var_type()):
            return
        self.rows_col.controls.append(self._make_row_item())
        self.sync_pool()
        self._notify_change()
        try:
            self.rows_col.update()
        except:
            pass
