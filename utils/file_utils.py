import json
import os

def save_plc(file_path, data):
    """
    Saves a list of n matrices (dimension 1xm) to a .plc file.
    data corresponds to a list of lists, where each inner list represents a 1xm matrix.
    """
    # Ensure the file has the .plc extension
    if not file_path.endswith(".plc"):
        file_path += ".plc"
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"File saved successfully: {file_path}")
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False

def load_plc(file_path):
    """
    Loads data from a .plc file.
    Returns the list of 1xm matrices.
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"File loaded successfully: {file_path}")
        return data
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
