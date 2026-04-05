import uuid
import flet as ft
import flet_base.router as fr
from flet_base.translations import instance_translation_manager as tm

from screens.editor.utils import normalize_editor_data
from screens.editor.column import EditableColumn
from screens.editor.modals import open_create_column_modal


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
        }
        for col in normalized["columns"]
    }

    # ------------------------------------------------------------------
    # Tab state  [{id, name, columns: [var_name, ...]}]
    # ------------------------------------------------------------------
    raw_tabs = normalized["layout"]["tabs"]
    tabs: list[dict] = [
        {
            "id": str(uuid.uuid4()),
            "name": t["name"],
            "columns": list(t.get("columns", [])),
        }
        for t in raw_tabs
    ]
    active_index: list[int] = [
        max(0, min(normalized["layout"]["active_tab_index"], len(tabs) - 1))
    ]  # mutable via list so closures can write to it

    # ------------------------------------------------------------------
    # Column display area
    # ------------------------------------------------------------------
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
        # Persist active_tab_index before writing
        _current_tab()  # just a sanity access
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
        # Sync tab's column list from what is currently visible
        _current_tab()["columns"] = [col.current_name for col in _visible_columns()]
        update_shared_state()
        for col in _visible_columns():
            col.sync_with_pool()
            col._just_changed = False

    def refresh_all_dropdowns():
        for col in _visible_columns():
            col.update_dropdown()

    # ------------------------------------------------------------------
    # Columns row management
    # ------------------------------------------------------------------

    def _rebuild_columns_row():
        """Rebuild columns_row for the active tab."""
        columns_row.controls.clear()
        for var_name in _current_tab()["columns"]:
            if var_name in pool:
                columns_row.controls.append(_make_column(var_name))
        columns_row.controls.append(add_column_card)
        _try_update(columns_row)

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

    async def clear_all(e=None):
        pool.clear()
        pool["V1"] = {"values": [], "magnitude": "none", "unit": "none"}
        for t in tabs:
            t["columns"] = ["V1"]
        _rebuild_columns_row()
        update_shared_state()

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
    # Tab bar
    # ------------------------------------------------------------------

    tabs_row = ft.Row(spacing=4, scroll=ft.ScrollMode.ADAPTIVE)

    def _build_tab_bar():
        tabs_row.controls.clear()
        for i, tab in enumerate(tabs):
            is_active = i == active_index[0]
            tab_btn = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(
                            tab["name"],
                            size=13,
                            weight=ft.FontWeight.W_600
                            if is_active
                            else ft.FontWeight.NORMAL,
                            color=themes.actual_theme["primary"]
                            if is_active
                            else ft.Colors.with_opacity(
                                0.7, themes.actual_theme["on_surface"]
                            ),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=12,
                            icon_color=ft.Colors.with_opacity(
                                0.5, themes.actual_theme["on_surface"]
                            ),
                            on_click=lambda e, idx=i: _delete_tab(idx),
                            tooltip=tm.translate("Eliminar pestaña"),
                            width=24,
                            height=24,
                        ),
                    ],
                    spacing=2,
                    tight=True,
                ),
                padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                border_radius=ft.BorderRadius(6, 6, 0, 0),
                bgcolor=themes.actual_theme["on_primary"]
                if is_active
                else ft.Colors.with_opacity(0.05, themes.actual_theme["on_surface"]),
                border=ft.Border(
                    left=ft.BorderSide(
                        1,
                        ft.Colors.with_opacity(0.15, themes.actual_theme["on_surface"]),
                    ),
                    right=ft.BorderSide(
                        1,
                        ft.Colors.with_opacity(0.15, themes.actual_theme["on_surface"]),
                    ),
                    top=ft.BorderSide(
                        1,
                        ft.Colors.with_opacity(0.15, themes.actual_theme["on_surface"]),
                    ),
                ),
                on_click=lambda e, idx=i: _switch_tab(idx),
                data=f"tab_{i}",
            )
            tabs_row.controls.append(tab_btn)

        # "+" button to add a new tab
        tabs_row.controls.append(
            ft.IconButton(
                icon=ft.Icons.ADD,
                icon_size=16,
                icon_color=themes.actual_theme["primary"],
                on_click=_add_tab,
                tooltip=tm.translate("Nueva pestaña"),
            )
        )
        _try_update(tabs_row)

    def _switch_tab(idx: int):
        active_index[0] = idx
        _build_tab_bar()
        _rebuild_columns_row()
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
        if len(tabs) <= 1:
            return  # always keep at least one tab
        tabs.pop(idx)
        new_active = min(active_index[0], len(tabs) - 1)
        active_index[0] = new_active
        _build_tab_bar()
        _rebuild_columns_row()
        update_shared_state()

    # ------------------------------------------------------------------
    # "+" column card  (defined here so _rebuild_columns_row can use it)
    # ------------------------------------------------------------------
    add_column_card = ft.Container(
        content=ft.IconButton(
            icon=ft.Icons.ADD_ROUNDED,
            icon_size=40,
            icon_color=themes.actual_theme["primary"],
            on_click=add_ui_column,
            tooltip=tm.translate("Añadir columna visual"),
        ),
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
    _build_tab_bar()
    _rebuild_columns_row()

    # ------------------------------------------------------------------
    # Action buttons
    # ------------------------------------------------------------------
    action_buttons = ft.Row(
        [
            ft.TextButton(
                tm.translate("Atrás"),
                icon=ft.Icons.CHEVRON_LEFT,
                on_click=lambda _: data.page.go("/home"),
            ),
            ft.Row(
                [
                    ft.Button(
                        tm.translate("Agregar variable"),
                        icon=ft.Icons.ADD_BOX_OUTLINED,
                        on_click=trigger_create_modal,
                        style=ft.ButtonStyle(
                            color={"": themes.actual_theme["on_primary"]},
                            bgcolor={"": themes.actual_theme["primary"]},
                        ),
                    ),
                    ft.Button(
                        tm.translate("Limpiar todo"),
                        icon=ft.Icons.DELETE_SWEEP_OUTLINED,
                        on_click=clear_all,
                        color=ft.Colors.ERROR,
                    ),
                ],
                spacing=10,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    return ft.View(
        route="/editor",
        padding=30,
        controls=[
            action_buttons,
            ft.Container(height=12),
            # Tab bar
            ft.Container(
                content=tabs_row,
                border=ft.Border(
                    bottom=ft.BorderSide(
                        1,
                        ft.Colors.with_opacity(0.15, themes.actual_theme["on_surface"]),
                    )
                ),
            ),
            # Columns area
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
