import sys
import os
import pytest
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
utils_math_path = os.path.join(project_root, "utils", "math_utils")
if utils_math_path not in sys.path:
    sys.path.insert(0, utils_math_path)

from plotter.plotter import (
    _render_series,
    _render_subplot,
    _apply_axis_config,
    plot,
    FigureConfig,
    SubplotConfig,
    SeriesConfig,
    AxisConfig,
    LegendConfig,
    quick_line,
    quick_scatter,
    quick_histogram,
)


class TestRenderSeries:
    def test_line(self):
        fig, ax = plt.subplots()
        s = SeriesConfig(plot_type="line", x=[1, 2, 3], y=[4, 5, 6], label="L")
        _render_series(ax, s, color="blue")
        lines = ax.get_lines()
        assert len(lines) == 1
        assert list(lines[0].get_xdata()) == [1, 2, 3]
        assert list(lines[0].get_ydata()) == [4, 5, 6]
        assert lines[0].get_label() == "L"
        plt.close(fig)

    def test_scatter(self):
        fig, ax = plt.subplots()
        s = SeriesConfig(plot_type="scatter", x=[1, 2], y=[3, 4], label="S")
        _render_series(ax, s, color="red")
        assert len(ax.collections) >= 1
        plt.close(fig)

    def test_bar(self):
        fig, ax = plt.subplots()
        s = SeriesConfig(plot_type="bar", x=[1, 2], y=[3, 4], label="B")
        _render_series(ax, s, color="green")
        assert len(ax.patches) >= 1
        plt.close(fig)

    def test_barh(self):
        fig, ax = plt.subplots()
        s = SeriesConfig(plot_type="barh", x=[1, 2], y=[3, 4], label="BH")
        _render_series(ax, s, color="purple")
        assert len(ax.patches) >= 1
        plt.close(fig)

    def test_histogram(self):
        fig, ax = plt.subplots()
        s = SeriesConfig(plot_type="histogram", x=[1, 1, 2, 2, 2, 3], label="H")
        _render_series(ax, s, color="orange")
        assert len(ax.patches) >= 1
        plt.close(fig)

    def test_step(self):
        fig, ax = plt.subplots()
        s = SeriesConfig(plot_type="step", x=[1, 2, 3], y=[4, 5, 6], label="St")
        _render_series(ax, s, color="cyan")
        assert len(ax.get_lines()) >= 1
        plt.close(fig)

    def test_fill_between(self):
        fig, ax = plt.subplots()
        s = SeriesConfig(plot_type="fill_between", x=[1, 2, 3], y=[4, 5, 6], y2=0, label="F")
        _render_series(ax, s, color="yellow")
        assert len(ax.collections) >= 1 or len(ax.get_lines()) >= 1
        plt.close(fig)

    def test_errorbar(self):
        fig, ax = plt.subplots()
        s = SeriesConfig(
            plot_type="errorbar", x=[1, 2], y=[3, 4],
            xerr=[0.1, 0.1], yerr=[0.2, 0.2], label="E",
        )
        _render_series(ax, s, color="brown")
        assert len(ax.containers) >= 1
        plt.close(fig)

    def test_pie(self):
        fig, ax = plt.subplots()
        s = SeriesConfig(plot_type="pie", y=[30, 40, 30], label="Pie")
        _render_series(ax, s, color=None)
        plt.close(fig)

    def test_boxplot(self):
        fig, ax = plt.subplots()
        s = SeriesConfig(plot_type="boxplot", y=[[1, 2, 3, 5], [4, 5, 6, 7]], box_labels=["A", "B"])
        _render_series(ax, s, color="blue")
        plt.close(fig)

    def test_boxplot_single_group(self):
        fig, ax = plt.subplots()
        s = SeriesConfig(plot_type="boxplot", y=[1, 2, 3, 5], label="G1")
        _render_series(ax, s, color="blue")
        plt.close(fig)

    def test_violin(self):
        fig, ax = plt.subplots()
        s = SeriesConfig(plot_type="violin", y=[[1, 2, 3], [4, 5, 6]])
        _render_series(ax, s, color="blue")
        plt.close(fig)

    def test_heatmap(self):
        fig, ax = plt.subplots()
        s = SeriesConfig(plot_type="heatmap", x=[[1, 2], [3, 4]], heatmap_annot=True)
        _render_series(ax, s, color=None)
        plt.close(fig)

    def test_contour(self):
        fig, ax = plt.subplots()
        x = np.linspace(-2, 2, 10)
        y = np.linspace(-2, 2, 10)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X) * np.cos(Y)
        s = SeriesConfig(plot_type="contour", x=X, y=Y, y2=Z)
        _render_series(ax, s, color=None)
        plt.close(fig)

    def test_unknown_plot_type_raises(self):
        fig, ax = plt.subplots()
        s = SeriesConfig(plot_type="invalid_type", x=[1], y=[2])
        with pytest.raises(ValueError):
            _render_series(ax, s, color="blue")
        plt.close(fig)

    def test_series_color_override(self):
        fig, ax = plt.subplots()
        s = SeriesConfig(plot_type="line", x=[1, 2], y=[3, 4], label="C", color="red")
        _render_series(ax, s, color="blue")
        lines = ax.get_lines()
        assert lines[0].get_color() == "red"
        plt.close(fig)


class TestApplyAxisConfig:
    def test_label(self):
        fig, ax = plt.subplots()
        cfg = AxisConfig(label="Time (s)")
        _apply_axis_config(ax, cfg, "x")
        assert ax.get_xlabel() == "Time (s)"
        plt.close(fig)

    def test_scale(self):
        fig, ax = plt.subplots()
        cfg = AxisConfig(scale="log")
        _apply_axis_config(ax, cfg, "y")
        assert ax.get_yscale() == "log"
        plt.close(fig)

    def test_limits(self):
        fig, ax = plt.subplots()
        cfg = AxisConfig(limits=(0, 100))
        _apply_axis_config(ax, cfg, "x")
        assert ax.get_xlim() == (0, 100)
        plt.close(fig)

    def test_grid_off(self):
        fig, ax = plt.subplots()
        cfg = AxisConfig(grid=False)
        _apply_axis_config(ax, cfg, "x")
        grid_visible = ax.get_xgridlines()[0].get_visible() if hasattr(ax, "get_xgridlines") else False
        plt.close(fig)


class TestRenderSubplot:
    def test_single_series(self):
        fig, ax = plt.subplots()
        sub = SubplotConfig(
            series=[SeriesConfig(plot_type="line", x=[1, 2, 3], y=[4, 5, 6], label="L")],
            title="Test",
            xlabel=AxisConfig(label="X"),
            ylabel=AxisConfig(label="Y"),
            legend=LegendConfig(show=True),
        )
        _render_subplot(ax, sub)
        assert ax.get_title() == "Test"
        assert ax.get_xlabel() == "X"
        assert ax.get_ylabel() == "Y"
        lines = ax.get_lines()
        assert len(lines) == 1
        assert lines[0].get_label() == "L"
        plt.close(fig)

    def test_no_legend_when_disabled(self):
        fig, ax = plt.subplots()
        sub = SubplotConfig(
            series=[SeriesConfig(plot_type="line", x=[1, 2], y=[3, 4], label="L")],
            legend=LegendConfig(show=False),
        )
        _render_subplot(ax, sub)
        assert ax.get_legend() is None
        plt.close(fig)

    def test_background_color(self):
        fig, ax = plt.subplots()
        sub = SubplotConfig(
            series=[SeriesConfig(plot_type="line", x=[1, 2], y=[3, 4])],
            background_color="#F0F0F0",
        )
        _render_subplot(ax, sub)
        assert ax.get_facecolor() is not None
        plt.close(fig)

    def test_multiple_series(self):
        fig, ax = plt.subplots()
        sub = SubplotConfig(
            series=[
                SeriesConfig(plot_type="line", x=[1, 2, 3], y=[4, 5, 6], label="A"),
                SeriesConfig(plot_type="line", x=[1, 2, 3], y=[6, 5, 4], label="B"),
            ]
        )
        _render_subplot(ax, sub)
        assert len(ax.get_lines()) == 2
        plt.close(fig)


class TestPlot:
    def test_plot_line(self):
        cfg = FigureConfig(
            subplots=[SubplotConfig(
                series=[SeriesConfig(plot_type="line", x=[1, 2, 3], y=[4, 5, 6], label="L")],
            )],
            show=False,
        )
        fig = plot(cfg)
        assert fig is not None
        assert len(fig.axes) >= 1
        plt.close(fig)

    def test_plot_suptitle(self):
        cfg = FigureConfig(
            subplots=[SubplotConfig(
                series=[SeriesConfig(plot_type="line", x=[1, 2], y=[3, 4])],
            )],
            suptitle="Main Title",
            show=False,
        )
        fig = plot(cfg)
        assert fig._suptitle is not None
        assert fig._suptitle.get_text() == "Main Title"
        plt.close(fig)

    def test_plot_multiple_subplots(self):
        cfg = FigureConfig(
            nrows=1, ncols=2,
            subplots=[
                SubplotConfig(
                    series=[SeriesConfig(plot_type="line", x=[1, 2], y=[3, 4], label="A")],
                ),
                SubplotConfig(
                    series=[SeriesConfig(plot_type="scatter", x=[1, 2], y=[5, 6], label="B")],
                ),
            ],
            show=False,
        )
        fig = plot(cfg)
        assert len(fig.axes) >= 2
        plt.close(fig)

    def test_plot_hides_extra_axes(self):
        cfg = FigureConfig(
            nrows=2, ncols=2,
            subplots=[SubplotConfig(
                series=[SeriesConfig(plot_type="line", x=[1, 2], y=[3, 4])],
            )],
            show=False,
        )
        fig = plot(cfg)
        axes = fig.axes
        assert len(axes) == 4
        plt.close(fig)


class TestQuickFunctions:
    def test_quick_line(self):
        fig = quick_line([1, 2, 3], [4, 5, 6], title="QLine", show=False)
        assert fig is not None
        assert fig.axes[0].get_title() == "QLine"
        plt.close(fig)

    def test_quick_scatter(self):
        fig = quick_scatter([1, 2, 3], [4, 5, 6], title="QScatter", show=False)
        assert fig is not None
        assert fig.axes[0].get_title() == "QScatter"
        plt.close(fig)

    def test_quick_histogram(self):
        fig = quick_histogram([1, 1, 2, 2, 2, 3], title="QHist", show=False)
        assert fig is not None
        assert fig.axes[0].get_title() == "QHist"
        plt.close(fig)
