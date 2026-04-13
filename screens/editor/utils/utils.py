import importlib.util
from pathlib import Path


def load_default_units() -> dict:
    """Load default_units from utils/math utils/unit conversor/default_units.py."""
    units_path = (
        Path(__file__).parents[3] / "utils" / "math utils" / "unit conversor" / "default_units.py"
    )
    if not units_path.exists():
        return {}
    try:
        spec = importlib.util.spec_from_file_location("default_units", units_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, "default_units", {})
    except Exception as e:
        print(f"Error loading units: {e}")
        return {}


def normalize_editor_data(raw_data) -> dict:
    """
    Normalize editor data into canonical form:
        {
            "columns": [{name, values, magnitude, unit}, ...],
            "layout": {
                "tabs": [{"name": str, "columns": [var_name, ...]}, ...],
                "active_tab_index": int,
            }
        }

    Accepts both the legacy flat list/dict format and the current
    {columns, layout} dict produced by file_utils.load_plc.
    """
    if isinstance(raw_data, dict) and "columns" in raw_data and "layout" in raw_data:
        columns = _normalize_columns(raw_data["columns"])
        layout = _normalize_layout(raw_data.get("layout"), columns)
        return {"columns": columns, "layout": layout}

    # Legacy: flat list of columns or dict with just a "columns" key
    columns = _normalize_columns(raw_data)
    layout = _normalize_layout(None, columns)
    return {"columns": columns, "layout": layout}


# ------------------------------------------------------------------ #
#  Internal helpers                                                    #
# ------------------------------------------------------------------ #

def _normalize_columns(raw) -> list[dict]:
    if isinstance(raw, dict):
        raw_columns = raw.get("columns", [])
    elif isinstance(raw, list):
        raw_columns = raw
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
        elif isinstance(col, list):
            name, values, magnitude, unit, description = f"V{i + 1}", col, "none", "none", ""
        else:
            continue
        columns.append(
            {
                "name": str(name),
                "values": values,
                "magnitude": magnitude,
                "unit": unit,
                "description": description,
            }
        )

    return columns or [
        {"name": "V1", "values": [], "magnitude": "none", "unit": "none", "description": ""}
    ]


def _normalize_layout(layout, columns_data) -> dict:
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
