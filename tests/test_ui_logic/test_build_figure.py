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

from screens.editor.components.plot_column import (
    _build_figure,
    _fig_to_base64,
    _migrate_old_config,
)


class TestMigrateOldConfig:
    def test_already_new_format(self):
        cfg = {"series": [{"label": "a", "plot_type": "line"}]}
        assert _migrate_old_config(cfg) is cfg

    def test_old_flat_format(self):
        cfg = {
            "plot_type": "scatter",
            "x_var": "t",
            "y_var": "v",
            "x_err_var": "e1",
            "y_err_var": "e2",
            "title": "Test",
            "xlabel": "Tiempo",
            "ylabel": "Velocidad",
        }
        result = _migrate_old_config(cfg)
        assert "series" in result
        assert len(result["series"]) == 1
        s = result["series"][0]
        assert s["plot_type"] == "scatter"
        assert s["x_var"] == "t"
        assert s["y_var"] == "v"
        assert s["x_err_var"] == "e1"
        assert s["y_err_var"] == "e2"
        assert result["title"] == "Test"
        assert result["xlabel"] == "Tiempo"
        assert result["ylabel"] == "Velocidad"

    def test_old_format_minimal(self):
        cfg = {"x_var": "x"}
        result = _migrate_old_config(cfg)
        assert result["series"][0]["x_var"] == "x"
        assert result["series"][0]["plot_type"] == "scatter"
        assert result["title"] == ""

    def test_old_format_with_regression(self):
        cfg = {"x_var": "x", "y_var": "y", "regression": "linear", "show_legend": False}
        result = _migrate_old_config(cfg)
        assert result["regression"] == "linear"
        assert result["show_legend"] is False


class TestBuildFigure:
    def _make_pool(self, overrides=None):
        pool = {
            "x": {"values": [1, 2, 3, 4, 5], "unit": "s"},
            "y": {"values": [2, 4, 6, 8, 10], "unit": "m"},
        }
        if overrides:
            pool.update(overrides)
        return pool

    def _make_plot_entry(self, series_list, **kwargs):
        cfg = {
            "series": series_list,
            "title": kwargs.get("title", "Test"),
            "xlabel": kwargs.get("xlabel", "X"),
            "ylabel": kwargs.get("ylabel", "Y"),
            "regression": kwargs.get("regression", "none"),
            "show_legend": kwargs.get("show_legend", True),
            "style": kwargs.get("style", "default"),
        }
        return {"values": [], "plot_config": cfg}

    def test_returns_figure_with_line_plot(self):
        pool = self._make_pool({
            "p1": self._make_plot_entry([
                {"label": "line1", "plot_type": "line", "x_var": "x", "y_var": "y"}
            ])
        })
        fig = _build_figure(pool, "p1")
        assert fig is not None
        assert len(fig.axes) == 1
        lines = fig.axes[0].get_lines()
        assert len(lines) == 1
        assert list(lines[0].get_xdata()) == [1, 2, 3, 4, 5]
        assert list(lines[0].get_ydata()) == [2, 4, 6, 8, 10]
        plt.close(fig)

    def test_returns_figure_with_scatter_plot(self):
        pool = self._make_pool({
            "p1": self._make_plot_entry([
                {"label": "scatter1", "plot_type": "scatter", "x_var": "x", "y_var": "y"}
            ])
        })
        fig = _build_figure(pool, "p1")
        assert fig is not None
        ax = fig.axes[0]
        collections = ax.collections
        assert len(collections) >= 1
        plt.close(fig)

    def test_returns_figure_with_histogram(self):
        pool = {
            "data": {"values": [1, 1, 2, 2, 2, 3, 3, 3, 3]},
            "p1": self._make_plot_entry([
                {"label": "hist1", "plot_type": "histogram", "x_var": "data", "y_var": ""}
            ], title="Histogram"),
        }
        fig = _build_figure(pool, "p1")
        assert fig is not None
        ax = fig.axes[0]
        assert len(ax.patches) > 0
        assert ax.get_title() == "Histogram"
        plt.close(fig)

    def test_returns_figure_with_errorbar(self):
        pool = self._make_pool({
            "ex": {"values": [0.1, 0.1, 0.1, 0.1, 0.1]},
            "ey": {"values": [0.2, 0.2, 0.2, 0.2, 0.2]},
            "p1": self._make_plot_entry([
                {
                    "label": "eb1", "plot_type": "errorbar",
                    "x_var": "x", "y_var": "y",
                    "x_err_var": "ex", "y_err_var": "ey",
                }
            ]),
        })
        fig = _build_figure(pool, "p1")
        assert fig is not None
        ax = fig.axes[0]
        assert len(ax.containers) >= 1
        plt.close(fig)

    def test_multiple_series(self):
        pool = self._make_pool({
            "y2": {"values": [3, 6, 9, 12, 15]},
            "p1": self._make_plot_entry([
                {"label": "s1", "plot_type": "line", "x_var": "x", "y_var": "y"},
                {"label": "s2", "plot_type": "scatter", "x_var": "x", "y_var": "y2"},
            ]),
        })
        fig = _build_figure(pool, "p1")
        assert fig is not None
        ax = fig.axes[0]
        lines = ax.get_lines()
        assert len(lines) >= 1
        handles, labels = ax.get_legend_handles_labels()
        assert "s1" in labels
        assert "s2" in labels
        plt.close(fig)

    def test_returns_none_when_missing_plot(self):
        fig = _build_figure({}, "nonexistent")
        assert fig is None

    def test_returns_none_when_no_config(self):
        pool = {"p1": {"values": []}}
        fig = _build_figure(pool, "p1")
        assert fig is None

    def test_returns_none_when_no_series_with_data(self):
        pool = {
            "x": {"values": []},
            "p1": self._make_plot_entry([
                {"label": "s1", "plot_type": "line", "x_var": "x", "y_var": ""}
            ]),
        }
        fig = _build_figure(pool, "p1")
        assert fig is None

    def test_linear_regression_overlay(self):
        pool = self._make_pool({
            "p1": self._make_plot_entry([
                {"label": "data", "plot_type": "scatter", "x_var": "x", "y_var": "y"}
            ], regression="linear"),
        })
        fig = _build_figure(pool, "p1")
        assert fig is not None
        lines = fig.axes[0].get_lines()
        assert len(lines) == 1
        assert "R²" in lines[0].get_label()
        plt.close(fig)

    def test_polynomial_regression_overlay(self):
        pool = self._make_pool({
            "p1": self._make_plot_entry([
                {"label": "data", "plot_type": "scatter", "x_var": "x", "y_var": "y"}
            ], regression="poly2"),
        })
        fig = _build_figure(pool, "p1")
        assert fig is not None
        lines = fig.axes[0].get_lines()
        assert len(lines) == 1
        assert "R²" in lines[0].get_label()
        plt.close(fig)

    def test_inferred_axis_labels(self):
        pool = self._make_pool({
            "p1": self._make_plot_entry([
                {"label": "s1", "plot_type": "line", "x_var": "x", "y_var": "y"}
            ], xlabel="", ylabel=""),
        })
        fig = _build_figure(pool, "p1")
        assert fig is not None
        ax = fig.axes[0]
        assert ax.get_xlabel() == "x"
        assert ax.get_ylabel() == "y"
        plt.close(fig)

    def test_custom_style_applied(self):
        pool = self._make_pool({
            "p1": self._make_plot_entry([
                {"label": "s1", "plot_type": "line", "x_var": "x", "y_var": "y"}
            ], style="ggplot"),
        })
        fig = _build_figure(pool, "p1")
        assert fig is not None
        plt.close(fig)

    def test_old_config_migration_on_fly(self):
        pool = {
            "x": {"values": [1, 2, 3]},
            "y": {"values": [4, 5, 6]},
            "p1": {
                "values": [],
                "plot_config": {
                    "plot_type": "line",
                    "x_var": "x",
                    "y_var": "y",
                    "title": "Legacy",
                },
            },
        }
        fig = _build_figure(pool, "p1")
        assert fig is not None
        assert fig.axes[0].get_title() == "Legacy"
        plt.close(fig)

    def test_legend_toggle(self):
        pool = self._make_pool({
            "p1": self._make_plot_entry([
                {"label": "s1", "plot_type": "line", "x_var": "x", "y_var": "y"}
            ], show_legend=False),
        })
        fig = _build_figure(pool, "p1")
        assert fig is not None
        ax = fig.axes[0]
        legend = ax.get_legend()
        assert legend is None or not legend.get_visible()
        plt.close(fig)

    def test_color_setting(self):
        pool = self._make_pool({
            "p1": self._make_plot_entry([
                {
                    "label": "s1", "plot_type": "line", "x_var": "x", "y_var": "y",
                    "color": "#FF0000", "marker": "o", "markersize": 8.0,
                }
            ]),
        })
        fig = _build_figure(pool, "p1")
        assert fig is not None
        lines = fig.axes[0].get_lines()
        assert lines[0].get_color() == "#FF0000"
        plt.close(fig)


class TestFigToBase64:
    def test_converts_figure_to_base64_png(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [4, 5, 6])
        b64 = _fig_to_base64(fig)
        assert isinstance(b64, str)
        assert len(b64) > 0
        import base64
        decoded = base64.b64decode(b64)
        assert decoded.startswith(b"\x89PNG")
        plt.close(fig)

    def test_empty_figure_returns_string(self):
        fig, ax = plt.subplots()
        b64 = _fig_to_base64(fig)
        assert isinstance(b64, str)
        assert len(b64) > 0
        plt.close(fig)
