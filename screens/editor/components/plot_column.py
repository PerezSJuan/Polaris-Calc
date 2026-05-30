"""
PlotColumn
==========
Tarjeta del editor para variables de tipo plot.
Usa ft.MatplotlibChart para renderizar la figura matplotlib inline.
"""

import os
import sys
import matplotlib

matplotlib.use("Agg")
import flet as ft
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import io
import base64
import asyncio
from flet_base.translations import instance_translation_manager as tm

# ── math utils en el path ────────────────────────────────────────────────────
_current_dir = os.path.dirname(os.path.abspath(__file__))
_math_utils_path = os.path.abspath(
    os.path.join(_current_dir, "..", "..", "..", "utils", "math utils")
)
if _math_utils_path not in sys.path:
    sys.path.append(_math_utils_path)

from plotter.plotter import (
    FigureConfig,
    SubplotConfig,
    SeriesConfig,
    AxisConfig,
    LegendConfig,
)
from plotter.residuals_helper import linear_regression, polynomial_regression

from utils.variable_types import VARIABLE_TYPE_PLOT

_CARD_W = 340
_CARD_RADIUS = 12

_REGRESSION_DEGREES = {"poly2": 2, "poly3": 3}
_NEEDS_SINGLE_H = {"histogram"}


def _c(t, key, opacity=1.0):
    col = t[key]
    return ft.Colors.with_opacity(opacity, col) if opacity < 1.0 else col


def _migrate_old_config(cfg: dict) -> dict:
    """Convierte plot_config antiguo (formato plano) al nuevo multi-serie."""
    if "series" in cfg:
        return cfg
    pt = cfg.get("plot_type", "scatter")
    x_var = cfg.get("x_var", "")
    y_var = cfg.get("y_var", "")
    x_err_v = cfg.get("x_err_var", "")
    y_err_v = cfg.get("y_err_var", "")
    label = f"{y_var} vs {x_var}" if y_var else x_var
    return {
        "series": [
            {
                "label": label,
                "plot_type": pt,
                "x_var": x_var,
                "y_var": y_var,
                "x_err_var": x_err_v,
                "y_err_var": y_err_v,
                "color": None,
                "linestyle": "-",
                "marker": "o" if pt == "scatter" else ("" if pt == "fill_between" else ""),
                "linewidth": 1.5,
            }
        ],
        "title": cfg.get("title", ""),
        "xlabel": cfg.get("xlabel", x_var),
        "ylabel": cfg.get("ylabel", y_var),
        "regression": cfg.get("regression", "none"),
        "show_legend": cfg.get("show_legend", True),
        "style": cfg.get("style", "default"),
    }


def _build_figure(pool: dict, plot_name: str) -> plt.Figure | None:
    """Construye la figura matplotlib a partir de plot_config (multi-serie)."""
    entry = pool.get(plot_name, {})
    cfg = entry.get("plot_config", {})
    if not cfg:
        return None

    cfg = _migrate_old_config(cfg)

    series_list = cfg.get("series", [])
    title = cfg.get("title", plot_name)
    xlabel = cfg.get("xlabel", "")
    ylabel = cfg.get("ylabel", "")
    reg = cfg.get("regression", "none")
    style = cfg.get("style", "default")

    # Inferir etiquetas de ejes si no están definidas
    if not xlabel:
        x_vars = [s.get("x_var", "") for s in series_list if s.get("x_var")]
        xlabel = x_vars[0] if x_vars else "x"
    if not ylabel:
        y_vars = [s.get("y_var", "") for s in series_list if s.get("y_var") and s.get("plot_type") not in _NEEDS_SINGLE_H]
        ylabel = y_vars[0] if y_vars else "y"

    plot_series: list[SeriesConfig] = []

    for sc in series_list:
        pt = sc.get("plot_type", "line")
        x_var = sc.get("x_var", "")
        y_var = sc.get("y_var", "")
        x_err_v = sc.get("x_err_var", "")
        y_err_v = sc.get("y_err_var", "")

        x_vals = pool.get(x_var, {}).get("values", []) if x_var else []
        y_vals = pool.get(y_var, {}).get("values", []) if y_var else []

        if not x_vals:
            continue

        x = np.asarray(x_vals, dtype=float)
        y = np.asarray(y_vals, dtype=float) if y_vals else None

        xerr = None
        yerr = None
        if pt == "errorbar":
            if x_err_v and pool.get(x_err_v, {}).get("values"):
                xerr = np.asarray(pool[x_err_v]["values"], dtype=float)
            if y_err_v and pool.get(y_err_v, {}).get("values"):
                yerr = np.asarray(pool[y_err_v]["values"], dtype=float)

        s_kwargs: dict = dict(
            plot_type=pt,
            x=x,
            label=sc.get("label", y_var or x_var),
            color=sc.get("color") or None,
            linestyle=sc.get("linestyle", "-") or "-",
            linewidth=sc.get("linewidth", 1.5),
        )
        s_kwargs["marker"] = sc.get("marker") or None
        s_kwargs["markersize"] = sc.get("markersize", 6.0)

        if pt == "histogram":
            s_kwargs["x"] = x
            s_kwargs.pop("y", None)
            s_kwargs.pop("color", None)
            s_kwargs.pop("marker", None)
            s_kwargs.pop("linestyle", None)
            s_kwargs["color"] = sc.get("color") or None
        elif pt == "errorbar":
            s_kwargs["y"] = y
            s_kwargs["xerr"] = xerr
            s_kwargs["yerr"] = yerr
        else:
            s_kwargs["y"] = y

        plot_series.append(SeriesConfig(**{k: v for k, v in s_kwargs.items() if v is not None or k in ("color",)}))

    # regresión (usar la primera serie con y para calcular)
    first_y_series = next(
        (s for s in series_list if s.get("y_var") and pool.get(s["y_var"], {}).get("values")),
        None,
    )
    if reg != "none" and first_y_series:
        y_var_reg = first_y_series["y_var"]
        x_var_reg = first_y_series.get("x_var", "")
        x_vals_reg = pool.get(x_var_reg, {}).get("values", [])
        y_vals_reg = pool.get(y_var_reg, {}).get("values", [])
        if x_vals_reg and y_vals_reg and len(x_vals_reg) > 1:
            try:
                x_r = np.asarray(x_vals_reg, dtype=float)
                y_r = np.asarray(y_vals_reg, dtype=float)
                x_fit = np.linspace(x_r.min(), x_r.max(), 200)
                if reg == "linear":
                    res = linear_regression(x_r, y_r)
                    y_fit = res.slope * x_fit + res.intercept
                    reg_label = f"Lineal  R²={res.r_squared:.3f}"
                else:
                    deg = _REGRESSION_DEGREES.get(reg, 2)
                    res = polynomial_regression(x_r, y_r, degree=deg)
                    y_fit = np.polyval(res.coefficients, x_fit)
                    reg_label = f"Polinómica g{deg}  R²={res.r_squared:.3f}"
                plot_series.append(
                    SeriesConfig(
                        plot_type="line",
                        x=x_fit,
                        y=y_fit,
                        label=reg_label,
                        linestyle="--",
                        linewidth=1.5,
                        color=None,
                    )
                )
            except Exception:
                pass

    if not plot_series:
        return None

    fig_cfg = FigureConfig(
        subplots=[
            SubplotConfig(
                series=plot_series,
                title=title,
                xlabel=AxisConfig(label=xlabel),
                ylabel=AxisConfig(label=ylabel),
                legend=LegendConfig(show=cfg.get("show_legend", True)),
            )
        ],
        figsize=(4.2, 3.0),
        dpi=100,
        style=style,
        show=False,
    )

    try:
        plt.style.use(fig_cfg.style)
    except Exception:
        plt.style.use("default")

    fig = Figure(figsize=fig_cfg.figsize, dpi=fig_cfg.dpi)
    ax = fig.add_subplot(111)
    sub = fig_cfg.subplots[0]

    from plotter.plotter import _render_subplot

    _render_subplot(ax, sub)
    fig.tight_layout()
    return fig


def _fig_to_base64(fig: Figure) -> str:
    """Convierte una figura matplotlib a string base64 PNG."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    return b64


class PlotColumn(ft.Container):
    """
    Tarjeta del editor para variables de tipo plot.
    Renderiza la figura con ft.MatplotlibChart.
    """

    def __init__(
        self,
        pool: dict,
        plot_name: str,
        on_change,
        themes,
        on_manage=None,
        shared=None,
    ):
        super().__init__()
        self.pool = pool
        self.plot_name = plot_name
        self.on_change = on_change
        self.themes = themes
        self._just_changed = False
        self._on_manage_cb = on_manage
        self.shared = shared

        t = themes.actual_theme
        acc = t.get("formula_accent", t["primary"])

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

        self._acc = acc
        self._t = t
        try:
            self._build_ui()
        except Exception as e:
            print(f"Error building PlotColumn for {plot_name}: {e}")
            self._build_error_ui(str(e))

    def _build_error_ui(self, err_msg):
        t = self._t
        self.content = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, color=ft.Colors.RED, size=30),
                ft.Text(f"Error: {err_msg}", size=12, color=_c(t, "on_surface", 0.6))
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            alignment=ft.Alignment.CENTER
        )

    # ── UI ───────────────────────────────────────────────────────────────────

    def _build_ui(self):
        t = self._t
        acc = self._acc
        entry = self.pool.get(self.plot_name, {})
        cfg = entry.get("plot_config", {})
        pt_label = cfg.get("plot_type", "plot").capitalize()
        desc = entry.get("description", "")

        accent_strip = ft.Container(
            height=3,
            bgcolor=acc,
            border_radius=ft.BorderRadius(_CARD_RADIUS, _CARD_RADIUS, 0, 0),
        )

        type_pill = ft.Container(
            content=ft.Text(
                f"Plot · {pt_label}",
                size=9,
                weight=ft.FontWeight.W_600,
                color=ft.Colors.with_opacity(0.85, acc),
            ),
            bgcolor=ft.Colors.with_opacity(0.10, acc),
            border_radius=20,
            padding=ft.Padding(8, 2, 8, 2),
        )

        self.move_left_btn = ft.IconButton(
            icon=ft.Icons.ARROW_BACK_IOS_NEW,
            icon_size=16,
            padding=ft.Padding.all(4),
            tooltip=tm.translate("Mover a la izquierda"),
            on_click=lambda e: asyncio.create_task(self._on_manage_click("move_left", e)),
            icon_color=_c(t, "on_surface", 0.65),
            visible=self._on_manage_cb is not None,
        )
        self.move_right_btn = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD_IOS,
            icon_size=16,
            padding=ft.Padding.all(4),
            tooltip=tm.translate("Mover a la derecha"),
            on_click=lambda e: asyncio.create_task(self._on_manage_click("move_right", e)),
            icon_color=_c(t, "on_surface", 0.65),
            visible=self._on_manage_cb is not None,
        )
        self.remove_from_tab_btn = ft.IconButton(
            icon=ft.Icons.REMOVE_CIRCLE_OUTLINE,
            icon_size=16,
            padding=ft.Padding.all(4),
            tooltip=tm.translate("Eliminar de la pestaña"),
            on_click=lambda e: asyncio.create_task(self._on_manage_click("remove_from_tab", e)),
            icon_color=_c(t, "on_surface", 0.65),
            visible=self._on_manage_cb is not None,
        )
        self.delete_variable_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
            icon_size=16,
            padding=ft.Padding.all(4),
            tooltip=tm.translate("Eliminar variable"),
            on_click=lambda e: asyncio.create_task(self._on_manage_click("delete_variable", e)),
            icon_color=ft.Colors.RED_400,
            visible=self._on_manage_cb is not None,
        )
        self.export_btn = ft.IconButton(
            icon=ft.Icons.DOWNLOAD_OUTLINED,
            icon_size=16,
            padding=ft.Padding.all(4),
            tooltip=tm.translate("Exportar como PNG"),
            on_click=lambda e: asyncio.create_task(self._export_plot(e)),
            icon_color=_c(t, "on_surface", 0.65),
            visible=self.shared is not None,
        )
        self.manage_btns = ft.Row(
            [
                self.move_left_btn,
                self.move_right_btn,
                self.remove_from_tab_btn,
                self.delete_variable_btn,
            ],
            spacing=2,
            visible=self._on_manage_cb is not None,
        )

        header = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.SHOW_CHART_OUTLINED, size=18, color=acc),
                            ft.Text(
                                self.plot_name,
                                size=14,
                                weight=ft.FontWeight.W_600,
                                color=_c(t, "on_surface"),
                                overflow=ft.TextOverflow.ELLIPSIS,
                                max_lines=1,
                                expand=True,
                            ),
                        ],
                        spacing=6,
                        expand=True,
                    ),
                    ft.Row([self.export_btn, self.manage_btns], spacing=4),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding(left=14, top=10, right=14, bottom=4),
        )

        desc_text = ft.Container(
            content=ft.Text(
                desc if desc else tm.translate("Sin descripción"),
                size=11,
                italic=not bool(desc),
                color=_c(t, "on_surface", 0.42 if not desc else 0.60),
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            padding=ft.Padding(14, 0, 14, 6),
        )

        # ── chart area ───────────────────────────────────────────────────────
        fig = _build_figure(self.pool, self.plot_name)
        if fig:
            chart_ctrl = ft.Image(
                src=f"data:image/png;base64,{_fig_to_base64(fig)}",
                tooltip=tm.translate("Gráfico generado"),
            )
            plt.close(fig)
        else:
            chart_ctrl = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            ft.Icons.INSERT_CHART_OUTLINED_ROUNDED,
                            size=38,
                            color=_c(t, "on_surface", 0.18),
                        ),
                        ft.Text(
                            tm.translate("Sin datos para graficar"),
                            size=12,
                            color=_c(t, "on_surface", 0.30),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )

        self._chart_container = ft.Container(
            content=chart_ctrl,
            height=240,
            border=ft.Border(
                top=ft.BorderSide(1, _c(t, "on_surface", 0.07)),
                bottom=ft.BorderSide(1, _c(t, "on_surface", 0.07)),
            ),
            bgcolor=_c(t, "on_surface", 0.02),
        )

        # ── variables chips (multi-serie) ──────────────────────────────────────
        raw_cfg = _migrate_old_config(cfg)
        series_list = raw_cfg.get("series", [])
        reg = cfg.get("regression", "none")
        reg_labels = {
            "none": "—",
            "linear": "Lineal",
            "poly2": "Grado 2",
            "poly3": "Grado 3",
        }

        series_chips = []
        for sc in series_list:
            s_x = sc.get("x_var", "—")
            s_y = sc.get("y_var", "")
            s_pt = sc.get("plot_type", "line")
            s_color = sc.get("color")
            chip_color = _c(t, "on_surface", 0.60)
            series_chips.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                width=8, height=8,
                                border_radius=4,
                                bgcolor=s_color or _c(t, "on_surface", 0.35),
                            ),
                            ft.Text(
                                f"{s_x} → {s_y}" if s_y else s_x,
                                size=9,
                                color=chip_color,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=4,
                    ),
                    padding=ft.Padding(0, 1, 0, 1),
                )
            )

        info_row = ft.Container(
            content=ft.Row(
                [
                    ft.Column(series_chips, spacing=2, expand=True),
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.TRENDING_UP_ROUNDED,
                                size=12,
                                color=_c(t, "on_surface", 0.35),
                            ),
                            ft.Text(
                                tm.translate(reg_labels.get(reg, "—")),
                                size=10,
                                color=_c(t, "on_surface", 0.60),
                            ),
                        ],
                        spacing=4,
                    ),
                    type_pill,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            padding=ft.Padding(14, 6, 14, 10),
        )

        self.content = ft.Column(
            [
                accent_strip,
                header,
                desc_text,
                self._chart_container,
                info_row,
            ],
            spacing=0,
            expand=True,
        )

    async def _on_manage_click(self, action, e):
        if not self._on_manage_cb:
            return
        if asyncio.iscoroutinefunction(self._on_manage_cb):
            await self._on_manage_cb(self.plot_name, action)
        else:
            self._on_manage_cb(self.plot_name, action)

    async def _export_plot(self, e):
        if not self.shared or "file_picker_save" not in self.shared:
            return
        fig = _build_figure(self.pool, self.plot_name)
        if not fig:
            return
        saved_file = await self.shared["file_picker_save"].save_file(
            allowed_extensions=["png"],
            dialog_title=tm.translate("Guardar gráfico como PNG"),
            file_name=f"{self.plot_name}.png",
        )
        if saved_file:
            fig.savefig(saved_file, format="png", bbox_inches="tight")
        plt.close(fig)

    def sync_with_pool(self):
        """Regenera la figura y reemplaza el control chart."""
        t = self._t
        fig = _build_figure(self.pool, self.plot_name)
        if fig:
            self._chart_container.content = ft.Image(
                src=f"data:image/png;base64,{_fig_to_base64(fig)}",
            )
            plt.close(fig)
        else:
            self._chart_container.content = ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(
                            ft.Icons.INSERT_CHART_OUTLINED_ROUNDED,
                            size=38,
                            color=_c(t, "on_surface", 0.18),
                        ),
                        ft.Text(
                            tm.translate("Sin datos para graficar"),
                            size=12,
                            color=_c(t, "on_surface", 0.30),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )
        try:
            self._chart_container.update()
        except RuntimeError:
            pass
