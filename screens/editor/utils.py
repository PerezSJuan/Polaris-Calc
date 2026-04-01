import importlib.util
from pathlib import Path

def load_default_units():
    """Dynamically load default_units from the utils directory."""
    try:
        # Expected path: utils/math utils/unit conversor/default_units.py
        # Current file: screens/editor/utils.py
        # parent 1: screens/editor/
        # parent 2: screens/
        # parent 3: root
        root = Path(__file__).parents[2]
        units_path = (
            root / "utils" / "math utils" / "unit conversor" / "default_units.py"
        )

        if not units_path.exists():
            return {}

        spec = importlib.util.spec_from_file_location("default_units", str(units_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, "default_units", {})
    except Exception as e:
        print(f"Error loading units: {e}")
        return {}

def normalize_editor_data(raw_data):
    """Normalize editor data to [{name: str, values: list, magnitude: str, unit: str}] format."""
    normalized = []

    if isinstance(raw_data, dict):
        raw_columns = raw_data.get("columns", [])
    elif isinstance(raw_data, list):
        raw_columns = raw_data
    else:
        raw_columns = []

    for i, column in enumerate(raw_columns):
        if isinstance(column, dict):
            col_name = column.get("name") or column.get("header") or f"V{i + 1}"
            col_values = column.get("values")
            if not isinstance(col_values, list):
                col_values = (
                    column.get("data") if isinstance(column.get("data"), list) else []
                )
            col_mag = column.get("magnitude", "none")
            col_unit = column.get("unit", "none")
        elif isinstance(column, list):
            col_name = f"V{i + 1}"
            col_values = column
            col_mag = "none"
            col_unit = "none"
        else:
            continue

        normalized.append(
            {
                "name": str(col_name),
                "values": col_values,
                "magnitude": col_mag,
                "unit": col_unit,
            }
        )

    if not normalized:
        normalized = [{"name": "V1", "values": [], "magnitude": "none", "unit": "none"}]

    return normalized
