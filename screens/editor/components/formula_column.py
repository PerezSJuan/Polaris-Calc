import asyncio
import inspect
import flet as ft
from flet_base.translations import instance_translation_manager as tm
from screens.editor.components.latex_dropdown import get_latex_widget
from utils.variable_types import (
    VARIABLE_TYPE_BOOLEAN_FORMULA,
    infer_variable_type,
)
from screens.editor.modals import open_variable_settings_modal

from screens.editor.components.column import (
    LatexCell,
    _type_accent,
    _c,
    _fmt,
    _PADDING,
)
from screens.editor.components.boolean_column import BooleanCell
from screens.editor.components.complex_column import ComplexRow
from screens.editor.components.vector_column import VectorRow
from screens.editor.components.matrix_column import MatrixGrid


_CARD_W = 245
_CARD_RADIUS = 12


class FormulaColumn(ft.Container):
    def __init__(
        self,
        pool,
        current_name,
        on_change,
        available_vars_getter,
        themes,
        on_manage=None,
        shared=None,
    ):
        self.pool = pool
        self.current_name = current_name
        self.on_change = on_change
        self.available_vars_getter = available_vars_getter
        self.themes = themes
        self._on_manage_cb = on_manage
        self._shared = shared
        self._focused_cell = None
        self._just_changed = False

        super().__init__()

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
        self._load_values()

    # ── helpers ────────────────────────────────────────────────────────

    def _entry(self):
        return self.pool.get(self.current_name, {})

    def _entry_values(self):
        v = self._entry().get("values", [])
        return v if isinstance(v, list) else []

    def _var_type(self):
        return infer_variable_type(self._entry())

    def _detect_result_type(self):
        vt = self._var_type()
        if vt == VARIABLE_TYPE_BOOLEAN_FORMULA:
            return "boolean"
        values = self._entry_values()
        if not values:
            return "scalar"
        v = values[0]
        if isinstance(v, bool):
            return "boolean"
        if isinstance(v, complex):
            return "complex"
        if isinstance(v, (list, tuple)):
            if v and isinstance(v[0], (list, tuple)):
                return "matrix"
            return "vector"
        return "scalar"

    def _compute_width(self, result_type, values):
        CELL_W = 118
        CELL_SPACING = 4
        PADDING = 15
        
        if result_type == "matrix" and values:
            m = values[0]
            if isinstance(m, (list, tuple)) and m and isinstance(m[0], (list, tuple)):
                n_cols = len(m[0])
                content = n_cols * CELL_W + max(0, n_cols - 1) * CELL_SPACING
                return max(_CARD_W, content + 2 * PADDING)
        elif result_type == "vector" and values:
            v = values[0]
            n_cells = len(v) if isinstance(v, (list, tuple)) else 1
            content = n_cells * CELL_W + max(0, n_cells - 1) * CELL_SPACING
            return max(_CARD_W, content + 2 * PADDING)
            
        return _CARD_W  # scalar, boolean, complex

    def _update_size(self, result_type, values):
        self.width = self._compute_width(result_type, values)

    # ── UI construction ────────────────────────────────────────────────

    def _build_ui(self):
        t = self.themes.actual_theme
        acc = _type_accent(self._var_type(), self.themes)

        self._accent_strip = ft.Container(
            height=3,
            bgcolor=acc,
            border_radius=ft.BorderRadius(
                top_left=_CARD_RADIUS, top_right=_CARD_RADIUS,
                bottom_left=0, bottom_right=0,
            ),
        )

        self.header_display = get_latex_widget(self.current_name, size=16)
        self.move_left_btn = ft.IconButton(
            icon=ft.Icons.KEYBOARD_ARROW_LEFT,
            icon_size=16, padding=ft.Padding.all(4),
            tooltip=tm.translate("Mover izquierda"),
            on_click=lambda e: asyncio.create_task(self._on_manage_click("move_left", e)),
            icon_color=_c(t, "on_surface", 0.65),
            visible=self._on_manage_cb is not None,
        )
        self.move_right_btn = ft.IconButton(
            icon=ft.Icons.KEYBOARD_ARROW_RIGHT,
            icon_size=16, padding=ft.Padding.all(4),
            tooltip=tm.translate("Mover derecha"),
            on_click=lambda e: asyncio.create_task(self._on_manage_click("move_right", e)),
            icon_color=_c(t, "on_surface", 0.65),
            visible=self._on_manage_cb is not None,
        )
        self.remove_from_tab_btn = ft.IconButton(
            icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
            icon_size=16, padding=ft.Padding.all(4),
            tooltip=tm.translate("Eliminar de la pestaña"),
            on_click=lambda e: asyncio.create_task(self._on_manage_click("remove_from_tab", e)),
            icon_color=_c(t, "on_surface", 0.65),
            visible=self._on_manage_cb is not None,
        )
        self.delete_variable_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
            icon_size=16, padding=ft.Padding.all(4),
            tooltip=tm.translate("Eliminar variable"),
            on_click=lambda e: asyncio.create_task(self._on_manage_click("delete_variable", e)),
            icon_color=ft.Colors.RED_400,
            visible=self._on_manage_cb is not None,
        )
        self.manage_btns = ft.Row(
            [self.move_left_btn, self.move_right_btn, self.remove_from_tab_btn, self.delete_variable_btn],
            spacing=2, visible=self._on_manage_cb is not None,
        )
        self.settings_btn = ft.IconButton(
            icon=ft.Icons.SETTINGS_OUTLINED,
            icon_size=18,
            tooltip=tm.translate("Configurar variable"),
            on_click=self._open_settings_modal,
            icon_color=_c(t, "primary", 0.60),
            style=ft.ButtonStyle(padding=ft.Padding.all(4)),
        )

        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.FUNCTIONS, size=18, color=acc),
                    self.header_display,
                ], spacing=5, expand=True),
                self.manage_btns,
                self.settings_btn,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
               vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding(left=_PADDING, top=10, right=6, bottom=6),
        )

        formula = self._entry().get("formula", "")
        self._formula_text = ft.Text(
            formula, size=11, italic=True,
            color=_c(t, "on_surface", 0.65),
            overflow=ft.TextOverflow.ELLIPSIS, max_lines=1,
        )
        self.formula_display = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.FUNCTIONS, size=13, color=_c(t, "on_surface", 0.45)),
                self._formula_text,
            ], spacing=5),
            border_radius=6,
            padding=ft.Padding(10, 3, 10, 3),
            margin=ft.Margin(left=_PADDING, right=_PADDING, top=0, bottom=6),
            bgcolor=_c(t, "on_surface", 0.04),
            border=ft.Border.all(1, _c(t, "on_surface", 0.08)),
        )

        self._badge_text = ft.Text(
            "—", size=9, weight=ft.FontWeight.W_700,
            color=_c(t, "on_surface", 0.50),
        )
        self._type_badge = ft.Container(
            content=self._badge_text,
            bgcolor=_c(t, "on_surface", 0.06),
            border_radius=10,
            padding=ft.Padding(8, 2, 8, 2),
            margin=ft.Margin(left=_PADDING, right=_PADDING, top=0, bottom=0),
        )

        self.rows_col = ft.Column(spacing=8, scroll=ft.ScrollMode.ADAPTIVE, expand=True)

        self._empty_label = ft.Container(
            content=ft.Text(
                tm.translate("Sin datos — la fórmula se evaluará automáticamente."),
                size=11, italic=True, color=_c(t, "on_surface", 0.30),
                text_align=ft.TextAlign.CENTER,
            ),
            alignment=ft.Alignment.CENTER, expand=True,
        )

        self._stats_container = ft.Container(
            content=ft.Column([ft.Text("", size=9)]),
            padding=ft.Padding(_PADDING, 10, _PADDING, 10),
            bgcolor=_c(t, "on_surface", 0.03),
            border=ft.Border(top=ft.BorderSide(1, _c(t, "on_surface", 0.07))),
        )

        self.content = ft.Column([
            self._accent_strip,
            header,
            self.formula_display,
            self._type_badge,
            ft.Container(content=self.rows_col, expand=True,
                         padding=ft.Padding(left=_PADDING, right=_PADDING, top=6, bottom=6)),
            self._stats_container,
        ], spacing=0, tight=True)

    # ── value loading ─────────────────────────────────────────────────

    def _load_values(self):
        values = self._entry_values()
        result_type = self._detect_result_type()

        self._badge_text.value = self._badge_label(result_type, values)
        self._update_size(result_type, values)

        self.rows_col.controls.clear()
        if not values:
            self.rows_col.controls.append(self._empty_label)
        elif result_type == "matrix":
            self._render_matrix(values)
        else:
            for val in values:
                row = self._make_value_row(val, result_type)
                if row is not None:
                    self.rows_col.controls.append(row)
        self._rebuild_stats()
        self._try_update(self)

    def _badge_label(self, result_type, values):
        labels = {
            "scalar": "Escalar",
            "boolean": "Booleano",
            "complex": "Complejo",
            "vector": "Vector",
            "matrix": "Matriz",
        }
        label = labels.get(result_type, "—")
        if result_type == "vector" and values:
            d = len(values[0]) if isinstance(values[0], (list, tuple)) else 0
            label = f"Vector ({d})"
        elif result_type == "matrix" and values:
            m = values[0]
            if isinstance(m, (list, tuple)):
                label = f"Matriz {len(m)}×{len(m[0]) if m and isinstance(m[0], (list, tuple)) else 0}"
        return label

    def _make_value_row(self, val, result_type):
        if result_type == "scalar":
            return ft.Container(
                content=LatexCell(value=val, themes=self.themes,
                                  on_change=lambda e: None, read_only=True, compact=True),
                padding=ft.Padding(0, 2, 0, 2),
            )
        if result_type == "boolean":
            return ft.Container(
                content=BooleanCell(value=val, themes=self.themes,
                                    on_change=lambda e: None, read_only=True),
                padding=ft.Padding(0, 2, 0, 2),
            )
        if result_type == "complex":
            return ft.Container(
                content=ComplexRow(value=val, themes=self.themes,
                                   on_change=lambda: None, read_only=True),
                padding=ft.Padding(0, 2, 0, 2),
            )
        if result_type == "vector":
            n = len(val) if isinstance(val, (list, tuple)) else 1
            return ft.Container(
                content=VectorRow(values=val, n=n, themes=self.themes,
                                  on_change=lambda: None, read_only=True),
                padding=ft.Padding(0, 2, 0, 2),
            )
        return None

    def _render_matrix(self, values):
        if not values:
            self.rows_col.controls.append(self._empty_label)
            return
        m = values[0]
        if not isinstance(m, (list, tuple)):
            self.rows_col.controls.append(self._empty_label)
            return
        self.rows_col.controls.append(
            ft.Container(
                content=MatrixGrid(values=m, r=len(m),
                                   c=len(m[0]) if m and isinstance(m[0], (list, tuple)) else 1,
                                   themes=self.themes,
                                   on_change=lambda _: None, read_only=True),
                alignment=ft.Alignment.CENTER,
            )
        )

    # ── stats ─────────────────────────────────────────────────────────

    def _rebuild_stats(self):
        values = self._entry_values()
        n = len(values)
        result_type = self._detect_result_type()
        chips = [self._chip("n", str(n) if n else "—")]

        if n and result_type == "scalar":
            nums = [v for v in values if isinstance(v, (int, float))]
            if n == 1:
                chips.append(self._chip("val", _fmt(nums[0])))
            elif n > 1:
                m = sum(nums) / n
                chips += [self._chip("μ", _fmt(m)),
                          self._chip("σ", _fmt((sum((v - m) ** 2 for v in nums) / n) ** 0.5)),
                          self._chip("Σ", _fmt(sum(nums)))]
        elif n and result_type == "boolean":
            t_count = sum(1 for v in values if v)
            chips += [self._chip("V", str(t_count)), self._chip("F", str(n - t_count))]
        elif n and result_type == "complex":
            mags = [abs(v) for v in values if isinstance(v, complex)]
            if mags:
                chips.append(self._chip("|z| prom", _fmt(sum(mags) / len(mags))))
        elif n and result_type == "vector":
            dims = {len(v) for v in values if isinstance(v, (list, tuple))}
            chips.append(self._chip("dim", str(next(iter(dims)) if len(dims) == 1 else 0)))
        elif n and result_type == "matrix":
            m = values[0]
            if isinstance(m, (list, tuple)):
                r, c = len(m), (len(m[0]) if m and isinstance(m[0], (list, tuple)) else 0)
                chips.append(self._chip("tamaño", f"{r}×{c}"))

        self._stats_container.content = ft.Row(chips, alignment=ft.MainAxisAlignment.SPACE_AROUND)

    def _chip(self, label, value_str):
        t = self.themes.actual_theme
        return ft.Column([
            ft.Text(label, size=9, weight=ft.FontWeight.W_600,
                    color=_c(t, "on_surface", 0.38)),
            ft.Text(value_str, size=11, weight=ft.FontWeight.W_500,
                    color=_c(t, "on_surface", 0.75)),
        ], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def _try_update(self, ctrl):
        try:
            ctrl.update()
        except Exception:
            pass

    # ── sync ──────────────────────────────────────────────────────────

    def sync_with_pool(self):
        if self.current_name in self.pool:
            self._update_formula_text()
            self._load_values()

    def sync_pool(self):
        pass

    def _update_formula_text(self):
        formula = self._entry().get("formula", "")
        self._formula_text.value = formula
        self._try_update(self._formula_text)

    def update_dropdown(self):
        pass

    # ── settings ──────────────────────────────────────────────────────

    def _open_settings_modal(self, e):
        page = self.page
        if not page:
            return
        if inspect.iscoroutinefunction(open_variable_settings_modal):
            asyncio.create_task(
                open_variable_settings_modal(
                    page, self.current_name, self.pool, self._notify_change, self.themes
                )
            )
        else:
            open_variable_settings_modal(
                page, self.current_name, self.pool, self._notify_change, self.themes
            )

    def _notify_change(self):
        self.on_change()

    # ── manage ────────────────────────────────────────────────────────

    async def _on_manage_click(self, action, e):
        if not self._on_manage_cb:
            return
        if inspect.iscoroutinefunction(self._on_manage_cb):
            await self._on_manage_cb(self.current_name, action)
        else:
            self._on_manage_cb(self.current_name, action)
