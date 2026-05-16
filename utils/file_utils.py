import json
import os
from utils.variable_types import (
    VARIABLE_TYPE_COLUMN_NO_ERROR,
    infer_variable_type,
    is_boolean_type,
)


def _coerce_bool(val) -> bool:
    """Normalise any truthy/falsy representation to a proper Python bool.

    Handles: actual bool, int/float (0 → False, anything else → True),
    and strings like "True", "true", "1", "False", "false", "0".
    """
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    if isinstance(val, str):
        return val.strip().lower() in ("true", "1", "yes")
    return False


def _normalize_columns(raw_data):
    """Return columns in canonical format: [{name, values, errors, type, magnitude, unit, description, formula}]."""
    if isinstance(raw_data, dict):
        raw_columns = raw_data.get("columns", [])
    elif isinstance(raw_data, list):
        raw_columns = raw_data
    else:
        raw_columns = []

    columns = []
    for i, col in enumerate(raw_columns):
        if isinstance(col, dict):
            name = col.get("name") or col.get("header") or f"V{i + 1}"
            values = col.get("values")
            if not isinstance(values, list):
                values = col.get("data") if isinstance(col.get("data"), list) else []
            errors = col.get("errors", [])
            if isinstance(errors, list):
                normalized_errors = errors
            elif errors in ("", None):
                normalized_errors = []
            else:
                normalized_errors = [errors]
            magnitude = col.get("magnitude", "none")
            unit = col.get("unit", "none")
            description = col.get("description", "")
            formula = col.get("formula", "")
            var_type = infer_variable_type(col)
            if is_boolean_type(var_type):
                values = [_coerce_bool(v) for v in values]
        elif isinstance(col, list):
            (
                name,
                values,
                normalized_errors,
                var_type,
                magnitude,
                unit,
                description,
                formula,
            ) = (
                f"V{i + 1}",
                col,
                [],
                VARIABLE_TYPE_COLUMN_NO_ERROR,
                "none",
                "none",
                "",
                "",
            )
        else:
            continue

        columns.append(
            {
                "name": str(name),
                "values": values,
                "errors": normalized_errors,
                "type": var_type,
                "magnitude": magnitude,
                "unit": unit,
                "description": description,
                "formula": formula,
                "plot_config": col.get("plot_config", {}),
                "dimensions": col.get("dimensions"),
                "rows": col.get("rows"),
                "cols": col.get("cols"),
            }
        )

    return columns or [
        {
            "name": "V1",
            "values": [],
            "errors": [],
            "type": VARIABLE_TYPE_COLUMN_NO_ERROR,
            "magnitude": "none",
            "unit": "none",
            "description": "",
            "formula": "",
        }
    ]


def _normalize_layout(layout, columns_data):
    """Ensure layout has a valid tabs list."""
    if not isinstance(layout, dict):
        layout = {}

    tabs = layout.get("tabs")
    if not isinstance(tabs, list) or not tabs:
        all_cols = [c["name"] for c in columns_data]
        tabs = [{"name": "General", "columns": all_cols}]

    return {
        "tabs": tabs,
        "active_tab_index": layout.get("active_tab_index", 0),
    }


def save_plc(file_path, data):
    """Save columns and layout to a .plc file."""
    if not file_path.endswith(".plc"):
        file_path += ".plc"
    try:
        if isinstance(data, dict):
            columns = _normalize_columns(data.get("columns", []))
            layout = _normalize_layout(data.get("layout"), columns)
        else:
            columns = _normalize_columns(data)
            layout = _normalize_layout(None, columns)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"version": 2, "columns": columns, "layout": layout}, f, indent=4)

        print(f"File saved successfully: {file_path}")
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False


def load_plc(file_path):
    """Load a .plc file and return {columns, layout}."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        columns = _normalize_columns(data)
        layout = _normalize_layout(
            data.get("layout") if isinstance(data, dict) else None,
            columns,
        )

        print(f"File loaded successfully: {file_path}")
        return {"columns": columns, "layout": layout}
    except Exception as e:
        print(f"Error loading file: {e}")
        return None


def open_plc_dialog(page):
    pass


def save_plc_dialog(page):
    pass
