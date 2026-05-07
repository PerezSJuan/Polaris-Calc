import os
import sys
import uuid
import asyncio
from functools import partial
import flet as ft
import flet_base.router as fr
from flet_base.translations import instance_translation_manager as tm

from flet_base.components.buttons import icon_btn

current_dir = os.path.dirname(os.path.abspath(__file__))
math_utils_path = os.path.abspath(
    os.path.join(current_dir, "..", "..", "utils", "math utils")
)
if math_utils_path not in sys.path:
    sys.path.append(math_utils_path)

from function_substitution import CONSTANTS, evaluate, parse_expression

from screens.editor.utils.utils import normalize_editor_data
from screens.editor.components.column import EditableColumn
from screens.editor.components.plot_column import PlotColumn
from screens.editor.components.boolean_column import BooleanColumn
from utils.variable_types import (
    VARIABLE_TYPE_COLUMN_NO_ERROR,
    VARIABLE_TYPE_FORMULA_WITH_ERROR,
    VARIABLE_TYPE_BOOLEAN_FORMULA,
    infer_variable_type,
    is_formula_type,
    is_plot_type,
    is_boolean_type,
)
from screens.editor.modals import (
    open_create_variable_modal,
    open_create_formula_modal,
    open_create_plot_modal,
    open_create_special_modal,
    open_rename_tab_modal,
    open_variable_settings_modal,
)
from screens.editor.components.summary_view import SummaryView
from screens.editor.components.tab_bar import EditorTabBar


async def EditorScreen(data: fr.DataSystem, themes):
    """Main screen for managing and editing data vectors, with tab layout."""

    normalized = normalize_editor_data(data.shared.get("editor_data", []))

    def _normalize_errors(raw_errors):
        if isinstance(raw_errors, list):
            return raw_errors
        if raw_errors in ("", None):
            return []
        return [raw_errors]

    # ------------------------------------------------------------------
    # Global pool  {name: {values, magnitude, unit}}
    # ------------------------------------------------------------------
    pool = {
        col["name"]: {
            "values": col["values"],
            "magnitude": col["magnitude"],
            "unit": col["unit"],
            "description": col.get("description", ""),
            "formula": col.get("formula", ""),
            "type": infer_variable_type(col),
            "errors": _normalize_errors(col.get("errors", [])),
            "plot_config": col.get("plot_config", {}),
        }
        for col in normalized["columns"]
    }

    # ------------------------------------------------------------------
    # Tab state  [{id, name, columns: [var_name, ...], fixed: bool}]
    # ------------------------------------------------------------------
    raw_tabs = normalized["layout"]["tabs"]

    summary_tab = {
        "id": "fixed_summary",
        "name": tm.translate("Resumen"),
        "columns": [],
        "fixed": True,
    }

    tabs: list[dict] = [summary_tab] + [
        {
            "id": str(uuid.uuid4()),
            "name": t["name"],
            "columns": list(t.get("columns", [])),
            "fixed": False,
        }
        for t in raw_tabs
        if t.get("id") != "fixed_summary"
    ]
    # Shift active index to account for summary tab at 0
    saved_active = normalized["layout"].get("active_tab_index", 0)
    active_index: list[int] = [
        min(saved_active + 1, len(tabs) - 1) if saved_active >= 0 else 0
    ]  # mutable via list so closures can write to it

    # ------------------------------------------------------------------
    # UI Containers
    # ------------------------------------------------------------------
    tab_bar_container = ft.Container()

    columns_row = ft.Row(
        scroll=ft.ScrollMode.ADAPTIVE,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=20,
    )
    summary_col = ft.Column(
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True,
        spacing=0,
    )
    content_container = ft.Container(
        content=columns_row,
        expand=True,
    )
    formula_error_state = {"message": None}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_available_vars():
        return list(pool.keys())

    def _visible_columns() -> list:
        return [
            c
            for c in columns_row.controls
            if isinstance(c, (EditableColumn, BooleanColumn))
        ]

    def _visible_column_names() -> set[str]:
        """Returns names of all visible columns, including PlotColumns."""
        names = set()
        for c in columns_row.controls:
            if isinstance(c, (EditableColumn, BooleanColumn)):
                names.add(c.current_name)
            elif isinstance(c, PlotColumn):
                names.add(c.plot_name)
        return names

    def _all_named_columns() -> list[str]:
        result = []
        for c in columns_row.controls:
            if isinstance(c, (EditableColumn, BooleanColumn)):
                result.append(c.current_name)
            elif isinstance(c, PlotColumn):
                result.append(c.plot_name)
        return result

    def _try_update(widget):
        try:
            widget.update()
        except RuntimeError:
            pass

    def _current_tab() -> dict:
        return tabs[active_index[0]]

    def _normalize_unit_for_eval(unit: str) -> str:
        return "1" if unit in ("none", "", None) else unit

    def _normalize_unit_for_pool(unit: str) -> str:
        return "none" if unit in ("1", "", None) else unit

    def _is_derived(name: str) -> bool:
        entry = pool.get(name, {})
        formula = entry.get("formula", "")
        return (
            is_formula_type(infer_variable_type(entry))
            and isinstance(formula, str)
            and formula.strip() != ""
        )

    def _show_formula_error(message):
        if formula_error_state["message"] == message:
            return
        formula_error_state["message"] = message
        if not message:
            return
        data.page.snack_bar = ft.SnackBar(ft.Text(message))
        data.page.snack_bar.open = True
        _try_update(data.page)

    def _as_float(value) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _extract_dependencies(variable_name: str, formula: str) -> list[str]:
        expr = parse_expression(formula, mode="auto")
        symbols = {str(sym) for sym in expr.free_symbols}
        unknown = sorted(
            symbol
            for symbol in symbols
            if symbol not in pool and symbol not in CONSTANTS
        )
        if unknown:
            raise ValueError(
                f"{variable_name}: símbolos no definidos ({', '.join(unknown)})"
            )
        return sorted(symbol for symbol in symbols if symbol in pool)

    def _evaluate_formula_vector(variable_name: str, formula: str, deps: list[str]):
        variable_type = infer_variable_type(pool.get(variable_name, {}))
        if variable_type == VARIABLE_TYPE_FORMULA_WITH_ERROR:
            raise NotImplementedError(
                "El cálculo de errores para variables de fórmula aún no está implementado."
            )
        dep_lengths = {}
        for dep in deps:
            dep_values = pool.get(dep, {}).get("values", [])
            dep_lengths[dep] = len(dep_values) if isinstance(dep_values, list) else 0

        non_scalar_lengths = {length for length in dep_lengths.values() if length != 1}
        if len(non_scalar_lengths) > 1:
            length_info = ", ".join(f"{name}={dep_lengths[name]}" for name in deps)
            raise ValueError(
                f"{variable_name}: longitudes incompatibles ({length_info}). "
                "Solo se permite broadcast de escalares (len=1)."
            )

        target_len = non_scalar_lengths.pop() if non_scalar_lengths else 1
        if any(length not in (1, target_len) for length in dep_lengths.values()):
            length_info = ", ".join(f"{name}={dep_lengths[name]}" for name in deps)
            raise ValueError(
                f"{variable_name}: longitudes incompatibles ({length_info}). "
                "Solo se permite broadcast de escalares (len=1)."
            )

        result_values = []
        result_unit = "none"

        for idx in range(target_len):
            variables = {}
            for dep in deps:
                dep_entry = pool.get(dep, {})
                dep_values = dep_entry.get("values", [])
                if len(dep_values) == 1:
                    dep_value = dep_values[0]
                else:
                    dep_value = dep_values[idx]
                variables[dep] = (
                    _as_float(dep_value),
                    _normalize_unit_for_eval(dep_entry.get("unit", "none")),
                )

            value, unit = evaluate(formula, variables, mode="auto")
            if variable_type == VARIABLE_TYPE_BOOLEAN_FORMULA:
                result_values.append(bool(value))
            else:
                result_values.append(float(value))
            result_unit = _normalize_unit_for_pool(unit)

        return result_values, result_unit

    def recalculate_derived_variables(show_errors=True) -> bool:
        derived_names = [name for name in pool if _is_derived(name)]
        if not derived_names:
            if show_errors:
                _show_formula_error(None)
            return True

        try:
            dependencies = {}
            for name in derived_names:
                formula = pool[name].get("formula", "").strip()
                dependencies[name] = _extract_dependencies(name, formula)

            derived_set = set(derived_names)
            graph = {name: set() for name in derived_names}
            indegree = {name: 0 for name in derived_names}

            for name, deps in dependencies.items():
                for dep in deps:
                    if dep in derived_set:
                        graph[dep].add(name)
                        indegree[name] += 1

            queue = [name for name in derived_names if indegree[name] == 0]
            ordered = []
            while queue:
                current = queue.pop(0)
                ordered.append(current)
                for nxt in graph[current]:
                    indegree[nxt] -= 1
                    if indegree[nxt] == 0:
                        queue.append(nxt)

            if len(ordered) != len(derived_names):
                cyclic = [name for name in derived_names if indegree[name] > 0]
                raise ValueError(
                    "Dependencia cíclica entre derivadas: " + ", ".join(sorted(cyclic))
                )

            for name in ordered:
                formula = pool[name].get("formula", "").strip()
                values, unit = _evaluate_formula_vector(
                    name, formula, dependencies[name]
                )
                pool[name]["values"] = values
                pool[name]["unit"] = unit
                pool[name]["magnitude"] = "none"
                if infer_variable_type(pool[name]) != VARIABLE_TYPE_FORMULA_WITH_ERROR:
                    pool[name]["errors"] = []

            if show_errors:
                _show_formula_error(None)
            return True
        except Exception as exc:
            if show_errors:
                _show_formula_error(f"Error en variable derivada: {exc}")
            return False

    def _make_column(name: str) -> ft.Control:
        vt = infer_variable_type(pool.get(name, {}))
        if is_plot_type(vt):
            return PlotColumn(
                pool=pool,
                plot_name=name,
                on_change=on_column_data_changed,
                themes=themes,
            )
        if is_boolean_type(vt):
            return BooleanColumn(
                pool=pool,
                current_name=name,
                on_change=on_column_data_changed,
                available_vars_getter=get_available_vars,
                themes=themes,
            )
        return EditableColumn(
            pool=pool,
            current_name=name,
            on_change=on_column_data_changed,
            available_vars_getter=get_available_vars,
            themes=themes,
        )

    # ------------------------------------------------------------------
    # State persistence
    # ------------------------------------------------------------------

    def update_shared_state():
        data.shared["editor_data"] = {
            "columns": [{"name": name, **entry} for name, entry in pool.items()],
            "layout": {
                "tabs": [
                    {"name": t["name"], "columns": list(t["columns"])} for t in tabs
                ],
                "active_tab_index": active_index[0],
            },
        }

    # ------------------------------------------------------------------
    # Column sync
    # ------------------------------------------------------------------

    def on_column_data_changed():
        _current_tab()["columns"] = _all_named_columns()
        recalculate_derived_variables(show_errors=True)
        update_shared_state()
        for c in columns_row.controls:
            if isinstance(c, (EditableColumn, PlotColumn, BooleanColumn)):
                c.sync_with_pool()
                c._just_changed = False
        _update_add_column_menu_items()
        if active_index[0] == 0:  # If we are on Summary tab
            _refresh_ui()


    def refresh_all_dropdowns():
        for col in _visible_columns():
            col.update_dropdown()

    # ------------------------------------------------------------------
    # Rendering Logic
    # ------------------------------------------------------------------

    def _refresh_ui():
        """Top-level UI refresh."""
        tab_bar_container.content = EditorTabBar(
            tabs=tabs,
            active_index=active_index[0],
            on_switch_tab=_switch_tab,
            on_add_tab=_add_tab,
            on_delete_tab=_delete_tab,
            on_rename_tab=_rename_tab,
            on_move_tab=_move_tab,
            themes=themes,
        )
        _rebuild_columns_row()
        _try_update(tab_bar_container)

    def _rebuild_columns_row():
        curr = _current_tab()
        if curr.get("id") == "fixed_summary":
            summary_col.controls = [
                SummaryView(
                    pool,
                    themes,
                    on_open_settings=lambda name: open_variable_settings_modal(
                        data.page, name, pool, on_column_data_changed, themes
                    ),
                )
            ]
            content_container.content = summary_col
            _try_update(summary_col)
        else:
            columns_row.controls.clear()
            for var_name in curr["columns"]:
                if var_name in pool:
                    columns_row.controls.append(_make_column(var_name))
            _update_add_column_menu_items()
            columns_row.controls.append(add_column_card)
            content_container.content = columns_row
        _try_update(content_container)

    # ------------------------------------------------------------------
    # Tab Actions
    # ------------------------------------------------------------------

    def _switch_tab(idx: int):
        active_index[0] = idx
        _refresh_ui()
        update_shared_state()

    def _add_tab(e=None):
        new_tab = {
            "id": str(uuid.uuid4()),
            "name": f"{tm.translate('Hoja')} {len(tabs) + 1}",
            "columns": [],
        }
        tabs.append(new_tab)
        _switch_tab(len(tabs) - 1)

    def _delete_tab(idx: int):
        if tabs[idx].get("fixed") or len(tabs) <= 1:
            return
        tabs.pop(idx)
        active_index[0] = min(active_index[0], len(tabs) - 1)
        _refresh_ui()
        update_shared_state()

    async def _rename_tab(idx: int):
        if tabs[idx].get("fixed"):
            return

        def save_name(new_name):
            tabs[idx]["name"] = new_name
            _refresh_ui()
            update_shared_state()

        await open_rename_tab_modal(data.page, tabs[idx]["name"], save_name)

    def _move_tab(e, target_idx: int):
        if target_idx == 0:
            return
        src_ctrl = data.page.get_control(e.src_id)
        if not src_ctrl:
            return
        src_idx = src_ctrl.data
        if src_idx == 0 or src_idx == target_idx:
            return

        active_id = tabs[active_index[0]]["id"]
        moved_tab = tabs.pop(src_idx)
        tabs.insert(target_idx, moved_tab)
        active_index[0] = next(i for i, t in enumerate(tabs) if t["id"] == active_id)

        _refresh_ui()
        update_shared_state()

    # ------------------------------------------------------------------
    # Column Actions
    # ------------------------------------------------------------------

    async def add_ui_column(e=None, var_name=None):
        if var_name:
            target = var_name
        else:
            visible_names = _visible_column_names()
            target = next(
                (v for v in get_available_vars() if v not in visible_names), None
            )

        if target is None:
            target = get_available_vars()[0] if pool else "V1"
            pool.setdefault(
                target,
                {
                    "values": [],
                    "magnitude": "none",
                    "unit": "none",
                    "description": "",
                    "formula": "",
                    "type": VARIABLE_TYPE_COLUMN_NO_ERROR,
                    "errors": [],
                },
            )

        controls = columns_row.controls
        new_col = _make_column(target)
        if controls and getattr(controls[-1], "data", None) == "add_button":
            controls.insert(-1, new_col)
        else:
            controls.append(new_col)

        _current_tab()["columns"] = _all_named_columns()
        update_shared_state()
        _try_update(columns_row)

    async def trigger_create_variable_modal(e=None):
        await open_create_variable_modal(
            page=data.page,
            pool=pool,
            columns_row=columns_row,
            on_column_data_changed=on_column_data_changed,
            get_available_vars=get_available_vars,
            refresh_all_dropdowns=refresh_all_dropdowns,
            update_shared_state=update_shared_state,
            themes=themes,
        )

    async def trigger_create_formula_modal(e=None):
        await open_create_formula_modal(
            page=data.page,
            pool=pool,
            columns_row=columns_row,
            on_column_data_changed=on_column_data_changed,
            get_available_vars=get_available_vars,
            refresh_all_dropdowns=refresh_all_dropdowns,
            update_shared_state=update_shared_state,
            themes=themes,
        )

    data.shared["open_create_variable_modal"] = trigger_create_variable_modal
    data.shared["open_create_equation_modal"] = trigger_create_formula_modal

    async def trigger_create_plot_modal(e=None):
        await open_create_plot_modal(
            page=data.page,
            pool=pool,
            columns_row=columns_row,
            on_column_data_changed=on_column_data_changed,
            get_available_vars=get_available_vars,
            refresh_all_dropdowns=refresh_all_dropdowns,
            update_shared_state=update_shared_state,
            themes=themes,
        )

    data.shared["open_create_plot_modal"] = trigger_create_plot_modal

    async def trigger_create_special_modal(e=None):
        await open_create_special_modal(
            page=data.page,
            pool=pool,
            columns_row=columns_row,
            on_column_data_changed=on_column_data_changed,
            get_available_vars=get_available_vars,
            refresh_all_dropdowns=refresh_all_dropdowns,
            update_shared_state=update_shared_state,
            themes=themes,
        )

    data.shared["open_create_special_modal"] = trigger_create_special_modal

    # ------------------------------------------------------------------
    # Static Elements
    # ------------------------------------------------------------------
    add_column_menu = ft.PopupMenuButton(
        content=ft.Container(
            content=ft.Icon(ft.Icons.ADD_ROUNDED, size=30),
            alignment=ft.Alignment.CENTER,
            expand=True,
        ),
        items=[],
    )

    def _update_add_column_menu_items():
        from screens.editor.components.latex_dropdown import get_latex_widget

        available = get_available_vars()

        items = []
        for v in sorted(available):
            items.append(
                ft.PopupMenuItem(
                    content=ft.Container(
                        content=get_latex_widget(v),
                        padding=ft.Padding(10, 5, 10, 5),
                    ),
                    on_click=partial(add_ui_column, var_name=v),
                )
            )

        if not items:
            items.append(
                ft.PopupMenuItem(
                    content=ft.Text(
                        tm.translate("Todas las variables están en uso"),
                        italic=True,
                        size=12,
                        color=ft.Colors.with_opacity(0.5, themes.actual_theme["on_surface"]),
                    ),
                    disabled=True,
                )
            )

        add_column_menu.items = items

    add_column_card = ft.Container(
        content=add_column_menu,
        width=180,
        height=450,
        border=ft.Border.all(
            2, ft.Colors.with_opacity(0.1, themes.actual_theme["on_surface"])
        ),
        border_radius=12,
        alignment=ft.Alignment.CENTER,
        data="add_button",
    )

    # ------------------------------------------------------------------
    # Initial render
    # ------------------------------------------------------------------
    recalculate_derived_variables(show_errors=False)
    _refresh_ui()

    return ft.View(
        route="/editor",
        padding=30,
        controls=[
            tab_bar_container,
            ft.Container(
                content=content_container,
                expand=True,
                padding=ft.Padding(10, 16, 10, 10),
                border_radius=ft.BorderRadius(0, 12, 12, 12),
                bgcolor=ft.Colors.with_opacity(
                    0.01, themes.actual_theme["on_background"]
                ),
            ),
        ],
    )
