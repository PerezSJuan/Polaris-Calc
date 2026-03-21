import json
import os


def _normalize_columns(raw_data):
    """Return columns in canonical format: [{name: str, values: list}]."""
    columns = []

    if isinstance(raw_data, dict):
        raw_columns = raw_data.get("columns", [])
    elif isinstance(raw_data, list):
        raw_columns = raw_data
    else:
        raw_columns = []

    for i, col in enumerate(raw_columns):
        if isinstance(col, dict):
            name = col.get("name") or col.get("header") or f"V{i + 1}"
            values = col.get("values")
            if not isinstance(values, list):
                values = col.get("data") if isinstance(col.get("data"), list) else []
        elif isinstance(col, list):
            name = f"V{i + 1}"
            values = col
        else:
            continue

        columns.append({"name": str(name), "values": values})

    if not columns:
        columns = [{"name": "V1", "values": []}]

    return columns


def save_plc(file_path, data):
    """
    Saves matrix columns to a .plc file.
    The canonical format stores column names and values.
    """
    if not file_path.endswith(".plc"):
        file_path += ".plc"

    try:
        payload = {
            "version": 1,
            "columns": _normalize_columns(data),
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)
        print(f"File saved successfully: {file_path}")
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False


def load_plc(file_path):
    """
    Loads data from a .plc file and returns canonical columns.
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"File loaded successfully: {file_path}")
        return _normalize_columns(data)
    except Exception as e:
        print(f"Error loading file: {e}")
        return None


def open_plc_dialog(page):
    """
    Example of how to trigger an open dialog in Flet (placeholder functionality).
    In a real app, this would use page.file_picker.pick_files().
    """
    pass


def save_plc_dialog(page):
    """
    Example of how to trigger a save dialog in Flet (placeholder functionality).
    In a real app, this would use page.file_picker.save_file().
    """
    pass
