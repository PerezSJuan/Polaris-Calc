import importlib.util
from pathlib import Path


def load_default_units() -> dict:
    """Load default_units from utils/math utils/unit conversor/default_units.py."""
    units_path = (
        Path(__file__).parents[2] / "utils" / "math utils" / "unit conversor" / "default_units.py"
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


def normalize_editor_data(raw_data) -> list[dict]:
    """Normalize editor data to a list of {name, values, magnitude, unit} dicts."""
    if isinstance(raw_data, dict):
        raw_columns = raw_data.get("columns", [])
    elif isinstance(raw_data, list):
        raw_columns = raw_data
    else:
        raw_columns = []

    normalized = []
    for i, col in enumerate(raw_columns):
        if isinstance(col, dict):
            name = col.get("name") or col.get("header") or f"V{i + 1}"
            values = col.get("values")
            if not isinstance(values, list):
                values = col.get("data") if isinstance(col.get("data"), list) else []
            magnitude = col.get("magnitude", "none")
            unit = col.get("unit", "none")
        elif isinstance(col, list):
            name, values, magnitude, unit = f"V{i + 1}", col, "none", "none"
        else:
            continue

        normalized.append({
            "name": str(name),
            "values": values,
            "magnitude": magnitude,
            "unit": unit,
        })

    return normalized or [{"name": "V1", "values": [], "magnitude": "none", "unit": "none"}]
