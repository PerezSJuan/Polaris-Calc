import importlib.util
from pathlib import Path
from utils.variable_types import (
    VARIABLE_TYPE_COLUMN_NO_ERROR,
    infer_variable_type,
)


def _load_module(relative_path: str, module_name: str):
    """Load a module from utils/math utils/ by path (spaces in dirname)."""
    path = Path(__file__).parents[3] / "utils" / "math utils" / relative_path
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_number_unit_parser():
    """Return the evaluate() function from number_unit_parser."""
    mod = _load_module("number_unit_parser.py", "number_unit_parser")
    return mod.evaluate


def load_smart_format():
    """Return smart_format() from number_formatter."""
    mod = _load_module("number_formatter.py", "number_formatter")
    return mod.smart_format


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
            "columns": [{name, values, errors, type, magnitude, unit, description, formula}, ...],
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
        elif isinstance(col, list):
            name, values, normalized_errors, var_type, magnitude, unit, description, formula = (
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