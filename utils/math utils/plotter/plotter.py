"""
math_utils/plotter.py
=====================
Utilidad de graficado altamente configurable basada en matplotlib.
Soporta múltiples tipos de gráfico, subplots, estilos, anotaciones y más.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Literal, Sequence

# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------

PlotType = Literal[
    "line",
    "scatter",
    "bar",
    "barh",
    "histogram",
    "pie",
    "boxplot",
    "violin",
    "step",
    "fill_between",
    "errorbar",
    "heatmap",
    "contour",
    "contourf",
]

LegendLocation = Literal[
    "best",
    "upper right",
    "upper left",
    "lower left",
    "lower right",
    "right",
    "center left",
    "center right",
    "lower center",
    "upper center",
    "center",
]


# ---------------------------------------------------------------------------
# Dataclasses de configuración
# ---------------------------------------------------------------------------


@dataclass
class AxisConfig:
    """Configuración de un eje individual."""

    label: str = ""
    scale: Literal["linear", "log", "symlog", "logit"] = "linear"
    limits: tuple[float, float] | None = None
    ticks: Sequence[float] | None = None
    tick_labels: Sequence[str] | None = None
    tick_rotation: float = 0
    grid: bool = True
    grid_style: dict[str, Any] = field(
        default_factory=lambda: {"linestyle": "--", "alpha": 0.5, "color": "gray"}
    )
    formatter: mticker.Formatter | None = None


@dataclass
class LegendConfig:
    """Configuración de la leyenda."""

    show: bool = True
    location: LegendLocation = "best"
    title: str = ""
    fontsize: int = 10
    framealpha: float = 0.8
    ncols: int = 1


@dataclass
class AnnotationConfig:
    """Una anotación de texto sobre el gráfico."""

    text: str
    xy: tuple[float, float]
    xytext: tuple[float, float] | None = None
    fontsize: int = 9
    color: str = "black"
    arrowprops: dict[str, Any] | None = None


@dataclass
class SeriesConfig:
    """Configuración de una serie de datos dentro de un subplot."""

    plot_type: PlotType
    x: np.ndarray | Sequence | None = None
    y: np.ndarray | Sequence | None = None

    # --- Apariencia general ---
    label: str = ""
    color: str | None = None
    alpha: float = 1.0
    zorder: int = 2

    # --- Línea / paso ---
    linestyle: str = "-"
    linewidth: float = 1.5
    marker: str | None = None
    markersize: float = 6.0

    # --- Barras ---
    bar_width: float = 0.8
    bar_align: Literal["center", "edge"] = "center"
    bar_bottom: np.ndarray | Sequence | float = 0

    # --- Histograma ---
    bins: int | str | Sequence = "auto"
    hist_density: bool = False
    hist_cumulative: bool = False
    hist_orientation: Literal["vertical", "horizontal"] = "vertical"

    # --- Pie ---
    pie_explode: Sequence[float] | None = None
    pie_autopct: str | None = "%1.1f%%"
    pie_startangle: float = 90
    pie_shadow: bool = False
    pie_labels: Sequence[str] | None = None

    # --- Boxplot / Violin ---
    vert: bool = True
    box_notch: bool = False
    box_labels: Sequence[str] | None = None  # etiquetas de grupo para boxplot/violin
    violin_showmeans: bool = True

    # --- Errorbar ---
    xerr: np.ndarray | Sequence | float | None = None
    yerr: np.ndarray | Sequence | float | None = None
    err_capsize: float = 4.0
    err_elinewidth: float = 1.0

    # --- Fill between ---
    y2: np.ndarray | Sequence | float = 0
    fill_where: np.ndarray | Sequence | None = None

    # --- Heatmap / Contour (usa x como Z 2D) ---
    cmap: str = "viridis"
    colorbar: bool = True
    colorbar_label: str = ""
    contour_levels: int | Sequence[float] = 10
    heatmap_vmin: float | None = None
    heatmap_vmax: float | None = None
    heatmap_annot: bool = False  # anotar celdas en heatmap
    heatmap_fmt: str = ".2f"
    heatmap_xticklabels: Sequence[str] | None = None
    heatmap_yticklabels: Sequence[str] | None = None

    # --- Extras ---
    extra_kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass
class SubplotConfig:
    """Configuración de un subplot (un panel dentro de la figura)."""

    series: list[SeriesConfig]
    title: str = ""
    title_fontsize: int = 12
    xlabel: AxisConfig = field(default_factory=AxisConfig)
    ylabel: AxisConfig = field(default_factory=AxisConfig)
    legend: LegendConfig = field(default_factory=LegendConfig)
    annotations: list[AnnotationConfig] = field(default_factory=list)
    aspect: str | float = "auto"
    twin_x: list[SeriesConfig] = field(default_factory=list)  # eje Y derecho
    twin_y: list[SeriesConfig] = field(default_factory=list)  # eje X superior
    background_color: str | None = None


@dataclass
class FigureConfig:
    """Configuración global de la figura."""

    subplots: list[SubplotConfig]

    # --- Layout ---
    nrows: int = 1
    ncols: int = 1
    figsize: tuple[float, float] = (10, 6)
    dpi: int = 100
    suptitle: str = ""
    suptitle_fontsize: int = 14
    suptitle_y: float = 1.02
    tight_layout: bool = True
    constrained_layout: bool = False

    # --- Estilo ---
    style: str = "default"  # cualquier estilo matplotlib, p.ej. "seaborn-v0_8"
    palette: list[str] | None = None  # colores cíclicos para las series

    # --- Espaciado ---
    hspace: float | None = None
    wspace: float | None = None
    subplot_kw: dict[str, Any] = field(default_factory=dict)

    # --- Guardado ---
    save_path: str | None = None
    save_format: str = "png"
    save_bbox_inches: str = "tight"
    save_transparent: bool = False

    # --- Mostrar ---
    show: bool = True


# ---------------------------------------------------------------------------
# Motor de renderizado
# ---------------------------------------------------------------------------


def _apply_axis_config(ax: plt.Axes, cfg: AxisConfig, axis: Literal["x", "y"]) -> None:
    set_label = ax.set_xlabel if axis == "x" else ax.set_ylabel
    set_scale = ax.set_xscale if axis == "x" else ax.set_yscale
    set_lim = ax.set_xlim if axis == "x" else ax.set_ylim
    set_ticks = ax.set_xticks if axis == "x" else ax.set_yticks
    set_tick_labels = ax.set_xticklabels if axis == "x" else ax.set_yticklabels
    tick_params_axis = axis

    if cfg.label:
        set_label(cfg.label)
    set_scale(cfg.scale)
    if cfg.limits is not None:
        set_lim(cfg.limits)
    if cfg.ticks is not None:
        set_ticks(cfg.ticks)
        if cfg.tick_labels is not None:
            set_tick_labels(cfg.tick_labels, rotation=cfg.tick_rotation)
    else:
        ax.tick_params(axis=tick_params_axis, rotation=cfg.tick_rotation)
    if cfg.formatter is not None:
        if axis == "x":
            ax.xaxis.set_major_formatter(cfg.formatter)
        else:
            ax.yaxis.set_major_formatter(cfg.formatter)
    if cfg.grid:
        ax.grid(axis=axis, **cfg.grid_style)


def _render_series(ax: plt.Axes, s: SeriesConfig, color: str | None = None) -> Any:
    """Renderiza una SeriesConfig sobre un Axes y devuelve el objeto artístico."""
    c = s.color or color
    kw = s.extra_kwargs

    x = np.asarray(s.x) if s.x is not None else None
    y = np.asarray(s.y) if s.y is not None else None

    if s.plot_type == "line":
        return ax.plot(
            x,
            y,
            label=s.label,
            color=c,
            alpha=s.alpha,
            linestyle=s.linestyle,
            linewidth=s.linewidth,
            marker=s.marker,
            markersize=s.markersize,
            zorder=s.zorder,
            **kw,
        )

    elif s.plot_type == "scatter":
        return ax.scatter(
            x,
            y,
            label=s.label,
            color=c,
            alpha=s.alpha,
            s=s.markersize**2,
            marker=s.marker or "o",
            zorder=s.zorder,
            **kw,
        )

    elif s.plot_type == "bar":
        return ax.bar(
            x,
            y,
            width=s.bar_width,
            align=s.bar_align,
            bottom=s.bar_bottom,
            label=s.label,
            color=c,
            alpha=s.alpha,
            zorder=s.zorder,
            **kw,
        )

    elif s.plot_type == "barh":
        return ax.barh(
            x,
            y,
            height=s.bar_width,
            align=s.bar_align,
            left=s.bar_bottom,
            label=s.label,
            color=c,
            alpha=s.alpha,
            zorder=s.zorder,
            **kw,
        )

    elif s.plot_type == "histogram":
        data = y if y is not None else x
        return ax.hist(
            data,
            bins=s.bins,
            density=s.hist_density,
            cumulative=s.hist_cumulative,
            orientation=s.hist_orientation,
            label=s.label,
            color=c,
            alpha=s.alpha,
            zorder=s.zorder,
            **kw,
        )

    elif s.plot_type == "pie":
        labels = (
            s.pie_labels
            if s.pie_labels is not None
            else ([str(v) for v in y] if y is not None else None)
        )
        return ax.pie(
            y,
            explode=s.pie_explode,
            labels=labels,
            autopct=s.pie_autopct,
            startangle=s.pie_startangle,
            shadow=s.pie_shadow,
            colors=None if c is None else None,
            **kw,
        )

    elif s.plot_type == "boxplot":
        data = (
            [np.asarray(col) for col in y]
            if isinstance(y[0], (list, np.ndarray))
            else [y]
        )
        kw.pop("labels", None)  # evitar duplicado si viene en extra_kwargs
        box_lbls = s.box_labels or ([s.label] if s.label else None)
        return ax.boxplot(data, notch=s.box_notch, vert=s.vert, labels=box_lbls, **kw)

    elif s.plot_type == "violin":
        data = (
            [np.asarray(col) for col in y]
            if isinstance(y[0], (list, np.ndarray))
            else [y]
        )
        return ax.violinplot(data, vert=s.vert, showmeans=s.violin_showmeans, **kw)

    elif s.plot_type == "step":
        return ax.step(
            x,
            y,
            label=s.label,
            color=c,
            alpha=s.alpha,
            linewidth=s.linewidth,
            zorder=s.zorder,
            **kw,
        )

    elif s.plot_type == "fill_between":
        return ax.fill_between(
            x,
            y,
            s.y2,
            where=s.fill_where,
            label=s.label,
            color=c,
            alpha=s.alpha,
            zorder=s.zorder,
            **kw,
        )

    elif s.plot_type == "errorbar":
        return ax.errorbar(
            x,
            y,
            xerr=s.xerr,
            yerr=s.yerr,
            label=s.label,
            color=c,
            alpha=s.alpha,
            capsize=s.err_capsize,
            elinewidth=s.err_elinewidth,
            linestyle=s.linestyle,
            linewidth=s.linewidth,
            marker=s.marker or "o",
            markersize=s.markersize,
            zorder=s.zorder,
            **kw,
        )

    elif s.plot_type == "heatmap":
        # x contiene la matriz 2D Z
        Z = np.asarray(s.x)
        im = ax.imshow(
            Z,
            cmap=s.cmap,
            vmin=s.heatmap_vmin,
            vmax=s.heatmap_vmax,
            aspect=s.aspect if isinstance(s.aspect, str) else "auto",
            origin="upper",
            **kw,
        )
        if s.heatmap_xticklabels is not None:
            ax.set_xticks(range(Z.shape[1]))
            ax.set_xticklabels(s.heatmap_xticklabels, rotation=45, ha="right")
        if s.heatmap_yticklabels is not None:
            ax.set_yticks(range(Z.shape[0]))
            ax.set_yticklabels(s.heatmap_yticklabels)
        if s.heatmap_annot:
            for i in range(Z.shape[0]):
                for j in range(Z.shape[1]):
                    ax.text(
                        j,
                        i,
                        format(Z[i, j], s.heatmap_fmt),
                        ha="center",
                        va="center",
                        fontsize=8,
                    )
        if s.colorbar:
            cbar = ax.figure.colorbar(im, ax=ax)
            if s.colorbar_label:
                cbar.set_label(s.colorbar_label)
        return im

    elif s.plot_type in ("contour", "contourf"):
        # x=X 2D, y=Y 2D, z en extra_kwargs["z"] o s.y2
        Z = np.asarray(s.y2) if not isinstance(s.y2, (int, float)) else None
        if Z is None:
            raise ValueError("Para contour/contourf, pasa la matriz Z en `y2`.")
        fn = ax.contourf if s.plot_type == "contourf" else ax.contour
        cs = fn(x, y, Z, levels=s.contour_levels, cmap=s.cmap, alpha=s.alpha, **kw)
        if s.colorbar:
            cbar = ax.figure.colorbar(cs, ax=ax)
            if s.colorbar_label:
                cbar.set_label(s.colorbar_label)
        if s.plot_type == "contour":
            ax.clabel(cs, inline=True, fontsize=8)
        return cs

    else:
        raise ValueError(f"plot_type desconocido: {s.plot_type!r}")


def _render_subplot(
    ax: plt.Axes, sub: SubplotConfig, palette: list[str] | None = None
) -> None:
    colors = palette or plt.rcParams["axes.prop_cycle"].by_key()["color"]
    color_cycle = (colors[i % len(colors)] for i in range(1000))

    for s in sub.series:
        _render_series(ax, s, color=next(color_cycle) if s.color is None else None)

    if sub.title:
        ax.set_title(sub.title, fontsize=sub.title_fontsize)
    if sub.background_color:
        ax.set_facecolor(sub.background_color)

    _apply_axis_config(ax, sub.xlabel, "x")
    _apply_axis_config(ax, sub.ylabel, "y")

    if sub.legend.show:
        handles, labels = ax.get_legend_handles_labels()
        if labels:
            ax.legend(
                handles,
                labels,
                loc=sub.legend.location,
                title=sub.legend.title,
                fontsize=sub.legend.fontsize,
                framealpha=sub.legend.framealpha,
                ncols=sub.legend.ncols,
            )

    for ann in sub.annotations:
        kwargs: dict[str, Any] = dict(
            fontsize=ann.fontsize,
            color=ann.color,
        )
        if ann.xytext:
            kwargs["xytext"] = ann.xytext
            kwargs["arrowprops"] = ann.arrowprops or {"arrowstyle": "->"}
        ax.annotate(ann.text, xy=ann.xy, **kwargs)

    if isinstance(sub.aspect, (int, float)):
        ax.set_aspect(sub.aspect)

    # Eje Y derecho (twin_x)
    if sub.twin_x:
        ax2 = ax.twinx()
        for s in sub.twin_x:
            _render_series(ax2, s, color=next(color_cycle) if s.color is None else None)
        handles2, labels2 = ax2.get_legend_handles_labels()
        if labels2 and sub.legend.show:
            ax2.legend(
                handles2, labels2, loc="upper right", fontsize=sub.legend.fontsize
            )

    # Eje X superior (twin_y)
    if sub.twin_y:
        ax3 = ax.twiny()
        for s in sub.twin_y:
            _render_series(ax3, s, color=next(color_cycle) if s.color is None else None)


def plot(cfg: FigureConfig) -> plt.Figure:
    """
    Renderiza una figura completa a partir de un FigureConfig.

    Parámetros
    ----------
    cfg : FigureConfig
        Toda la configuración de la figura.

    Devuelve
    --------
    fig : matplotlib.figure.Figure
    """
    plt.style.use(cfg.style)

    fig, axes = plt.subplots(
        nrows=cfg.nrows,
        ncols=cfg.ncols,
        figsize=cfg.figsize,
        dpi=cfg.dpi,
        subplot_kw=cfg.subplot_kw,
        constrained_layout=cfg.constrained_layout,
    )

    # Normalizar axes a lista plana
    if cfg.nrows == 1 and cfg.ncols == 1:
        axes_flat = [axes]
    elif cfg.nrows == 1 or cfg.ncols == 1:
        axes_flat = list(np.ravel(axes))
    else:
        axes_flat = list(np.ravel(axes))

    for ax, sub in zip(axes_flat, cfg.subplots):
        _render_subplot(ax, sub, palette=cfg.palette)

    # Ocultar axes sobrantes
    for ax in axes_flat[len(cfg.subplots) :]:
        ax.set_visible(False)

    if cfg.suptitle:
        fig.suptitle(cfg.suptitle, fontsize=cfg.suptitle_fontsize, y=cfg.suptitle_y)

    if cfg.tight_layout and not cfg.constrained_layout:
        spacing: dict[str, Any] = {}
        if cfg.hspace is not None:
            spacing["hspace"] = cfg.hspace
        if cfg.wspace is not None:
            spacing["wspace"] = cfg.wspace
        fig.tight_layout(**spacing)

    if cfg.save_path:
        fig.savefig(
            cfg.save_path,
            format=cfg.save_format,
            bbox_inches=cfg.save_bbox_inches,
            transparent=cfg.save_transparent,
        )

    if cfg.show:
        plt.show()

    return fig


# ---------------------------------------------------------------------------
# Helpers de conveniencia (constructores rápidos)
# ---------------------------------------------------------------------------


def quick_line(
    x: Sequence,
    y: Sequence,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    label: str = "",
    **figure_kwargs: Any,
) -> plt.Figure:
    """Atajo para graficar una línea simple."""
    cfg = FigureConfig(
        subplots=[
            SubplotConfig(
                series=[SeriesConfig(plot_type="line", x=x, y=y, label=label)],
                title=title,
                xlabel=AxisConfig(label=xlabel),
                ylabel=AxisConfig(label=ylabel),
            )
        ],
        **figure_kwargs,
    )
    return plot(cfg)


def quick_scatter(
    x: Sequence,
    y: Sequence,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    label: str = "",
    **figure_kwargs: Any,
) -> plt.Figure:
    cfg = FigureConfig(
        subplots=[
            SubplotConfig(
                series=[SeriesConfig(plot_type="scatter", x=x, y=y, label=label)],
                title=title,
                xlabel=AxisConfig(label=xlabel),
                ylabel=AxisConfig(label=ylabel),
            )
        ],
        **figure_kwargs,
    )
    return plot(cfg)


def quick_histogram(
    data: Sequence,
    bins: int | str = "auto",
    title: str = "",
    xlabel: str = "",
    ylabel: str = "Frecuencia",
    label: str = "",
    density: bool = False,
    **figure_kwargs: Any,
) -> plt.Figure:
    cfg = FigureConfig(
        subplots=[
            SubplotConfig(
                series=[
                    SeriesConfig(
                        plot_type="histogram",
                        x=data,
                        bins=bins,
                        hist_density=density,
                        label=label,
                    )
                ],
                title=title,
                xlabel=AxisConfig(label=xlabel),
                ylabel=AxisConfig(label=ylabel),
            )
        ],
        **figure_kwargs,
    )
    return plot(cfg)
