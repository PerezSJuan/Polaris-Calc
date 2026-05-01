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


def _c(t, key, opacity=1.0):
    col = t[key]
    return ft.Colors.with_opacity(opacity, col) if opacity < 1.0 else col


def _build_figure(pool: dict, plot_name: str) -> plt.Figure | None:
    """Construye la figura matplotlib a partir de plot_config."""
    entry = pool.get(plot_name, {})
    cfg = entry.get("plot_config", {})
    if not cfg:
        return None

    pt = cfg.get("plot_type", "scatter")
    x_var = cfg.get("x_var", "")
    y_var = cfg.get("y_var", "")
    x_err_v = cfg.get("x_err_var", "")
    y_err_v = cfg.get("y_err_var", "")
    title = cfg.get("title", plot_name)
    xlabel = cfg.get("xlabel", x_var)
    ylabel = cfg.get("ylabel", y_var)
    reg = cfg.get("regression", "none")
    style = cfg.get("style", "default")

    x_vals = pool.get(x_var, {}).get("values", []) if x_var else []
    y_vals = pool.get(y_var, {}).get("values", []) if y_var else []

    if not x_vals:
        return None

    x = np.asarray(x_vals, dtype=float)
    y = np.asarray(y_vals, dtype=float) if y_vals else None

    # errores
    xerr = None
    yerr = None
    if pt == "errorbar":
        if x_err_v and pool.get(x_err_v, {}).get("values"):
            xerr = np.asarray(pool[x_err_v]["values"], dtype=float)
        if y_err_v and pool.get(y_err_v, {}).get("values"):
            yerr = np.asarray(pool[y_err_v]["values"], dtype=float)

    series: list[SeriesConfig] = []

    # serie principal
    s_kwargs: dict = {}
    if pt == "histogram":
        s_kwargs = dict(plot_type="histogram", x=x, label=x_var)
    elif pt == "errorbar":
        s_kwargs = dict(
            plot_type="errorbar",
            x=x,
            y=y,
            xerr=xerr,
            yerr=yerr,
            label=f"{y_var} vs {x_var}",
            marker="o",
        )
    elif pt in ("bar", "barh"):
        s_kwargs = dict(plot_type=pt, x=x, y=y, label=f"{y_var}")
    else:
        s_kwargs = dict(
            plot_type=pt, x=x, y=y, label=f"{y_var} vs {x_var}" if y_var else x_var
        )
    series.append(SeriesConfig(**s_kwargs))

    # regresión sobre scatter/line
    if reg != "none" and y is not None and len(x) > 1:
        try:
            x_fit = np.linspace(x.min(), x.max(), 200)
            if reg == "linear":
                res = linear_regression(x, y)
                y_fit = res.slope * x_fit + res.intercept
                reg_label = f"Lineal  R²={res.r_squared:.3f}"
            else:
                deg = _REGRESSION_DEGREES.get(reg, 2)
                res = polynomial_regression(x, y, degree=deg)
                y_fit = np.polyval(res.coefficients, x_fit)
                reg_label = f"Polinómica g{deg}  R²={res.r_squared:.3f}"
            series.append(
                SeriesConfig(
                    plot_type="line",
                    x=x_fit,
                    y=y_fit,
                    label=reg_label,
                    linestyle="--",
                    linewidth=1.5,
                )
            )
        except Exception:
            pass

    fig_cfg = FigureConfig(
        subplots=[
            SubplotConfig(
                series=series,
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

    def __init__(self, pool: dict, plot_name: str, on_change, themes):
        super().__init__()
        self.pool = pool
        self.plot_name = plot_name
        self.on_change = on_change
        self.themes = themes

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

        header = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.SHOW_CHART_ROUNDED, size=18, color=acc),
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
                    ft.IconButton(
                        icon=ft.Icons.REFRESH_ROUNDED,
                        icon_size=16,
                        icon_color=_c(t, "on_surface", 0.45),
                        tooltip=tm.translate("Actualizar gráfico"),
                        on_click=lambda e: self._refresh_chart(),
                        style=ft.ButtonStyle(padding=ft.Padding.all(4)),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=14, top=10, right=6, bottom=4),
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

        # ── variables chips ───────────────────────────────────────────────────
        x_var = cfg.get("x_var", "—")
        y_var = cfg.get("y_var", "")
        reg = cfg.get("regression", "none")
        reg_labels = {
            "none": "—",
            "linear": "Lineal",
            "poly2": "Grado 2",
            "poly3": "Grado 3",
        }

        info_row = ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.SWAP_HORIZ_ROUNDED,
                                size=12,
                                color=_c(t, "on_surface", 0.35),
                            ),
                            ft.Text(
                                f"{x_var} → {y_var}" if y_var else x_var,
                                size=10,
                                color=_c(t, "on_surface", 0.60),
                            ),
                        ],
                        spacing=4,
                    ),
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

    def _refresh_chart(self):
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
