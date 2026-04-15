import json
import os


def _normalize_columns(raw_data):
    """Return columns in canonical format: [{name, values, magnitude, unit, description, formula}]."""
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
            magnitude = col.get("magnitude", "none")
            unit = col.get("unit", "none")
            description = col.get("description", "")
            formula = col.get("formula", "")
        elif isinstance(col, list):
            name, values, magnitude, unit, description, formula = (
                f"V{i + 1}",
                col,
                "none",
                "none",
                "",
                "",
            )
        else:
            continue

        columns.append({
            "name": str(name),
            "values": values,
            "magnitude": magnitude,
            "unit": unit,
            "description": description,
            "formula": formula,
        })

    return columns or [{
        "name": "V1",
        "values": [],
        "magnitude": "none",
        "unit": "none",
        "description": "",
        "formula": "",
    }]


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
