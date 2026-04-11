import uuid
import flet as ft
import flet_base.router as fr
from flet_base.translations import instance_translation_manager as tm

from flet_base.components.buttons import icon_btn
from flet_base.components.texts import body

from screens.editor.utils.utils import normalize_editor_data
from screens.editor.components.column import EditableColumn
from screens.editor.modals.modals import open_create_column_modal, open_rename_tab_modal
from screens.editor.components.summary_view import SummaryView
from screens.editor.components.tab_bar import EditorTabBar


async def EditorScreen(data: fr.DataSystem, themes):
    """Main screen for managing and editing data vectors, with tab layout."""

    normalized = normalize_editor_data(data.shared.get("editor_data", []))

    # ------------------------------------------------------------------
    # Global pool  {name: {values, magnitude, unit}}
    # ------------------------------------------------------------------
    pool = {
        col["name"]: {
            "values": col["values"],
            "magnitude": col["magnitude"],
            "unit": col["unit"],
            "description": col.get("description", ""),
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

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_available_vars():
        return list(pool.keys())

    def _visible_columns() -> list[EditableColumn]:
        return [c for c in columns_row.controls if isinstance(c, EditableColumn)]

    def _try_update(widget):
        try:
            widget.update()
        except RuntimeError:
            pass

    def _current_tab() -> dict:
        return tabs[active_index[0]]

    def _make_column(name: str) -> EditableColumn:
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
        _current_tab()["columns"] = [col.current_name for col in _visible_columns()]
        update_shared_state()
        for col in _visible_columns():
            col.sync_with_pool()
            col._just_changed = False

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
        columns_row.controls.clear()
        curr = _current_tab()
        if curr.get("id") == "fixed_summary":
            columns_row.controls.append(SummaryView(pool, themes))
        else:
            for var_name in curr["columns"]:
                if var_name in pool:
                    columns_row.controls.append(_make_column(var_name))
            columns_row.controls.append(add_column_card)
        _try_update(columns_row)

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
        if target_idx == 0: return
        src_ctrl = data.page.get_control(e.src_id)
        if not src_ctrl: return
        src_idx = src_ctrl.data
        if src_idx == 0 or src_idx == target_idx: return

        active_id = tabs[active_index[0]]["id"]
        moved_tab = tabs.pop(src_idx)
        tabs.insert(target_idx, moved_tab)
        active_index[0] = next(i for i, t in enumerate(tabs) if t["id"] == active_id)
        
        _refresh_ui()
        update_shared_state()

    # ------------------------------------------------------------------
    # Column Actions
    # ------------------------------------------------------------------

    async def add_ui_column(e=None):
        visible_names = {col.current_name for col in _visible_columns()}
        target = next((v for v in get_available_vars() if v not in visible_names), None)

        if target is None:
            target = get_available_vars()[0] if pool else "V1"
            pool.setdefault(target, {"values": [], "magnitude": "none", "unit": "none"})

        controls = columns_row.controls
        new_col = _make_column(target)
        if controls and getattr(controls[-1], "data", None) == "add_button":
            controls.insert(-1, new_col)
        else:
            controls.append(new_col)

        _current_tab()["columns"] = [col.current_name for col in _visible_columns()]
        update_shared_state()
        _try_update(columns_row)

    async def trigger_create_modal(e=None):
        await open_create_column_modal(
            page=data.page,
            pool=pool,
            columns_row=columns_row,
            on_column_data_changed=on_column_data_changed,
            get_available_vars=get_available_vars,
            refresh_all_dropdowns=refresh_all_dropdowns,
            update_shared_state=update_shared_state,
            themes=themes,
        )

    data.shared["open_create_column_modal"] = trigger_create_modal

    # ------------------------------------------------------------------
    # Static Elements
    # ------------------------------------------------------------------
    add_column_card = ft.Container(
        content=icon_btn(icon=ft.Icons.ADD_ROUNDED, on_click=add_ui_column),
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
    _refresh_ui()

    return ft.View(
        route="/editor",
        padding=30,
        controls=[
            tab_bar_container,
            ft.Container(
                content=columns_row,
                expand=True,
                padding=ft.Padding(10, 16, 10, 10),
                border_radius=ft.BorderRadius(0, 12, 12, 12),
                bgcolor=ft.Colors.with_opacity(
                    0.01, themes.actual_theme["on_background"]
                ),
            ),
        ],
    )
