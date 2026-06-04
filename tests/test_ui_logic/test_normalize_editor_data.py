import sys
import os
import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
for p in [project_root]:
    if p not in sys.path:
        sys.path.insert(0, p)

from screens.editor.utils.utils import (
    normalize_editor_data,
    _normalize_columns,
    _normalize_layout,
)


class TestNormalizeColumns:
    def test_empty_list(self):
        result = _normalize_columns([])
        assert len(result) == 1
        assert result[0]["name"] == "V1"
        assert result[0]["values"] == []

    def test_single_dict_column(self):
        raw = [{"name": "x", "values": [1, 2, 3]}]
        result = _normalize_columns(raw)
        assert len(result) == 1
        assert result[0]["name"] == "x"
        assert result[0]["values"] == [1, 2, 3]

    def test_dict_without_name_uses_header(self):
        raw = [{"header": "col1", "values": [1, 2]}]
        result = _normalize_columns(raw)
        assert result[0]["name"] == "col1"

    def test_dict_without_name_or_header_uses_fallback(self):
        raw = [{"values": [1, 2]}]
        result = _normalize_columns(raw)
        assert result[0]["name"] == "V1"

    def test_values_from_data_key(self):
        raw = [{"name": "x", "data": [1, 2, 3]}]
        result = _normalize_columns(raw)
        assert result[0]["values"] == [1, 2, 3]

    def test_errors_normalization_list(self):
        raw = [{"name": "x", "values": [1], "errors": [0.1]}]
        result = _normalize_columns(raw)
        assert result[0]["errors"] == [0.1]

    def test_errors_normalization_empty_string(self):
        raw = [{"name": "x", "values": [1], "errors": ""}]
        result = _normalize_columns(raw)
        assert result[0]["errors"] == []

    def test_errors_normalization_scalar(self):
        raw = [{"name": "x", "values": [1], "errors": 0.5}]
        result = _normalize_columns(raw)
        assert result[0]["errors"] == [0.5]

    def test_errors_normalization_none(self):
        raw = [{"name": "x", "values": [1], "errors": None}]
        result = _normalize_columns(raw)
        assert result[0]["errors"] == []

    def test_list_column_legacy(self):
        raw = [[1, 2, 3]]
        result = _normalize_columns(raw)
        assert result[0]["name"] == "V1"
        assert result[0]["values"] == [1, 2, 3]

    def test_non_list_non_dict_skipped(self):
        raw = ["invalid", {"name": "x", "values": [1]}]
        result = _normalize_columns(raw)
        assert len(result) == 1
        assert result[0]["name"] == "x"

    def test_preserves_plot_config(self):
        raw = [{"name": "p1", "values": [], "plot_config": {"series": []}}]
        result = _normalize_columns(raw)
        assert result[0]["plot_config"] == {"series": []}

    def test_preserves_dimensions_rows_cols(self):
        raw = [{"name": "m", "values": [[1, 2]], "dimensions": "2x2", "rows": 2, "cols": 2}]
        result = _normalize_columns(raw)
        assert result[0]["dimensions"] == "2x2"
        assert result[0]["rows"] == 2
        assert result[0]["cols"] == 2

    def test_default_magnitude_and_unit(self):
        raw = [{"name": "x", "values": [1]}]
        result = _normalize_columns(raw)
        assert result[0]["magnitude"] == "none"
        assert result[0]["unit"] == "none"

    def test_custom_magnitude_and_unit(self):
        raw = [{"name": "x", "values": [1], "magnitude": "length", "unit": "m"}]
        result = _normalize_columns(raw)
        assert result[0]["magnitude"] == "length"
        assert result[0]["unit"] == "m"


class TestNormalizeLayout:
    def test_none_layout_creates_single_tab(self):
        columns = [{"name": "a"}, {"name": "b"}]
        result = _normalize_layout(None, columns)
        assert len(result["tabs"]) == 1
        assert result["tabs"][0]["name"] == "General"
        assert result["tabs"][0]["columns"] == ["a", "b"]

    def test_empty_dict_layout(self):
        columns = [{"name": "a"}]
        result = _normalize_layout({}, columns)
        assert len(result["tabs"]) == 1

    def test_preserves_tabs(self):
        columns = [{"name": "a"}, {"name": "b"}]
        layout = {"tabs": [{"name": "Tab1", "columns": ["a"]}, {"name": "Tab2", "columns": ["b"]}]}
        result = _normalize_layout(layout, columns)
        assert len(result["tabs"]) == 2

    def test_default_active_tab_index(self):
        result = _normalize_layout({}, [{"name": "a"}])
        assert result["active_tab_index"] == 0

    def test_preserves_active_tab_index(self):
        result = _normalize_layout({"active_tab_index": 2}, [{"name": "a"}])
        assert result["active_tab_index"] == 2


class TestNormalizeEditorData:
    def test_new_format_dict(self):
        data = {
            "columns": [{"name": "x", "values": [1, 2]}],
            "layout": {"tabs": [{"name": "Main", "columns": ["x"]}]},
        }
        result = normalize_editor_data(data)
        assert "columns" in result
        assert "layout" in result
        assert result["columns"][0]["name"] == "x"
        assert result["layout"]["tabs"][0]["name"] == "Main"

    def test_legacy_list_format(self):
        data = [{"name": "x", "values": [1, 2]}]
        result = normalize_editor_data(data)
        assert result["columns"][0]["name"] == "x"

    def test_legacy_dict_without_layout(self):
        data = {"columns": [{"name": "x", "values": [1]}]}
        result = normalize_editor_data(data)
        assert result["columns"][0]["name"] == "x"
        assert result["layout"]["tabs"][0]["name"] == "General"

    def test_empty_data_returns_default_column(self):
        result = normalize_editor_data([])
        assert len(result["columns"]) == 1
        assert result["columns"][0]["name"] == "V1"

    def test_invalid_data(self):
        result = normalize_editor_data("invalid")
        assert len(result["columns"]) == 1

    def test_roundtrip_full(self):
        data = {
            "columns": [
                {"name": "t", "values": [0.0, 0.1, 0.2], "unit": "s", "magnitude": "time"},
                {"name": "v", "values": [0.0, 1.0, 2.0], "unit": "m/s", "magnitude": "velocity"},
            ],
            "layout": {
                "tabs": [{"name": "Data", "columns": ["t", "v"]}],
                "active_tab_index": 0,
            },
        }
        result = normalize_editor_data(data)
        assert len(result["columns"]) == 2
        assert result["columns"][0]["magnitude"] == "time"
        assert result["columns"][1]["unit"] == "m/s"
        assert result["layout"]["tabs"][0]["name"] == "Data"
