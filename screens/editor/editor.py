import uuid
import flet as ft
import flet_base.router as fr
from flet_base.translations import instance_translation_manager as tm

from flet_base.components.buttons import icon_btn, text_btn
from flet_base.components.texts import body, subtitle

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

    def _build_summary_view():
        cards = []
        for i, (name, entry) in enumerate(pool.items()):
            values = entry.get("values", [])
            count = len(values)
            magnitude = entry.get("magnitude", "none")
            unit = entry.get("unit", "none")
            description = entry.get("description", "")

            v_type = (
                tm.translate("Vector")
                if count > 1
                else tm.translate("Escalar")
                if count == 1
                else tm.translate("Vacío")
            )

            # Badge para el número si tiene datos
            num_badge = ft.Container(
                content=body(
                    str(i + 1), size=10, color=themes.actual_theme["on_primary"]
                ),
                bgcolor=themes.actual_theme["primary"],
                padding=ft.Padding(6, 2, 6, 2),
                border_radius=5,
                visible=count > 0,
            )

            card = ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                num_badge,
                                body(name, size=18),
                                ft.Icon(
                                    ft.Icons.LAYERS_OUTLINED,
                                    size=18,
                                    color=themes.actual_theme["secondary"],
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        body(
                            description,
                            size=11,
                            color=ft.Colors.with_opacity(
                                0.7, themes.actual_theme["on_surface"]
                            ),
                        ),
                        ft.Divider(
                            height=10,
                            thickness=0.5,
                            color=ft.Colors.with_opacity(
                                0.1, themes.actual_theme["on_surface"]
                            ),
                        ),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        body(
                                            tm.translate("Tipo"),
                                            size=10,
                                            color=ft.Colors.with_opacity(
                                                0.6, themes.actual_theme["on_surface"]
                                            ),
                                        ),
                                        body(v_type, size=12),
                                    ],
                                    spacing=2,
                                ),
                                ft.Column(
                                    [
                                        body(
                                            tm.translate("Datos"),
                                            size=10,
                                            color=themes.actual_theme["on_surface"],
                                        ),
                                        body(str(count), size=12),
                                    ],
                                    spacing=2,
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        body(
                                            tm.translate("Magnitud"),
                                            size=10,
                                            color=themes.actual_theme["on_surface"],
                                        ),
                                        body(
                                            magnitude if magnitude != "none" else "-",
                                            size=12,
                                        ),
                                    ],
                                    spacing=2,
                                ),
                                ft.Column(
                                    [
                                        body(
                                            tm.translate("Unidad"),
                                            size=10,
                                            color=themes.actual_theme["on_surface"],
                                        ),
                                        body(unit if unit != "none" else "-", size=12),
                                    ],
                                    spacing=2,
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ],
                    spacing=10,
                ),
                width=220,
                height=170,
                padding=15,
                border_radius=15,
                bgcolor=ft.Colors.with_opacity(0.08, themes.actual_theme["on_surface"]),
                border=ft.Border.all(
                    1, ft.Colors.with_opacity(0.1, themes.actual_theme["on_surface"])
                ),
            )
            cards.append(card)

        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.GRID_VIEW_ROUNDED,
                                color=themes.actual_theme["primary"],
                                size=28,
                            ),
                            subtitle(tm.translate("Inventario de Variables"), size=22),
                        ],
                        spacing=15,
                    ),
                    body(
                        tm.translate(
                            "Vista general de todas las colecciones de datos en la sesión actual."
                        ),
                        size=13,
                        color=themes.actual_theme["on_surface"],
                    ),
                    ft.Divider(
                        height=30,
                        thickness=1,
                        color=ft.Colors.with_opacity(
                            0.1, themes.actual_theme["on_surface"]
                        ),
                    ),
                    ft.Row(
                        controls=cards,
                        spacing=20,
                        run_spacing=20,
                        alignment=ft.MainAxisAlignment.START,
                        wrap=True,
                    ),
                ],
                scroll=ft.ScrollMode.ADAPTIVE,
                spacing=10,
            ),
            padding=30,
            expand=True,
        )

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
        curr = _current_tab()
        if curr.get("id") == "fixed_summary":
            columns_row.controls.append(_build_summary_view())
        else:
            for var_name in curr["columns"]:
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
        pool["V1"] = {
            "values": [],
            "magnitude": "none",
            "unit": "none",
            "description": "",
        }
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
            is_fixed = tab.get("fixed", False)

            controls = []
            if is_fixed:
                controls.append(
                    ft.Icon(
                        ft.Icons.GRID_VIEW_ROUNDED,
                        size=20 if is_fixed else 16,
                        color=themes.actual_theme["primary"]
                        if is_active
                        else ft.Colors.with_opacity(
                            0.7, themes.actual_theme["on_surface"]
                        ),
                    )
                )

            controls.append(
                ft.Text(
                    tab["name"],
                    size=14 if is_fixed else 11,
                    weight=ft.FontWeight.W_600 if is_active or is_fixed else ft.FontWeight.NORMAL,
                    color=themes.actual_theme["primary"]
                    if is_active
                    else ft.Colors.with_opacity(0.7, themes.actual_theme["on_surface"]),
                )
            )

            if not is_fixed:
                controls.extend(
                    [
                        icon_btn(
                            icon=ft.Icons.EDIT_OUTLINED,
                            on_click=lambda e, idx=i: _rename_tab(idx),
                            icon_size=14,
                        ),
                        icon_btn(
                            icon=ft.Icons.CLOSE,
                            on_click=lambda e, idx=i: _delete_tab(idx),
                            icon_size=14,
                        ),
                    ]
                )

            tab_btn = ft.Container(
                content=ft.Row(
                    controls,
                    spacing=6 if is_fixed else 2,
                    tight=True,
                ),
                padding=ft.Padding.symmetric(
                    horizontal=18 if is_fixed else 8, vertical=10 if is_fixed else 4
                ),
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
                data=i,  # Usar el índice directamente
            )

            draggable = ft.Draggable(
                group="tabs",
                content=tab_btn,
                data=i,
            )

            drag_target = ft.DragTarget(
                group="tabs",
                content=draggable,
                on_accept=lambda e, idx=i: _move_tab(e, idx),
            )

            tabs_row.controls.append(drag_target)

        # "+" button to add a new tab
        tabs_row.controls.append(
            icon_btn(
                icon=ft.Icons.ADD,
                on_click=_add_tab,
                icon_size=18,
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
        if tabs[idx].get("fixed") or len(tabs) <= 1:
            return  # always keep at least one tab and don't delete fixed tabs
        tabs.pop(idx)
        new_active = min(active_index[0], len(tabs) - 1)
        active_index[0] = new_active
        _build_tab_bar()
        _rebuild_columns_row()
        update_shared_state()

    def _rename_tab(idx: int):
        if tabs[idx].get("fixed"):
            return

        def _close_dlg(e):
            rename_dlg.open = False
            data.page.update()

        def _save_name(e):
            new_name = rename_field.value.strip()
            if new_name:
                tabs[idx]["name"] = new_name
                _build_tab_bar()
                update_shared_state()
            _close_dlg(e)

        rename_field = ft.TextField(
            value=tabs[idx]["name"], autofocus=True, on_submit=_save_name
        )
        rename_dlg = ft.AlertDialog(
            title=body(tm.translate("Renombrar pestaña")),
            content=rename_field,
            actions=[
                text_btn(tm.translate("Cancelar"), on_click=_close_dlg),
                text_btn(tm.translate("Guardar"), on_click=_save_name),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        data.page.overlay.append(rename_dlg)
        rename_dlg.open = True
        data.page.update()

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

        _build_tab_bar()
        update_shared_state()

    # ------------------------------------------------------------------
    # "+" column card  (defined here so _rebuild_columns_row can use it)
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
    _build_tab_bar()
    _rebuild_columns_row()

    return ft.View(
        route="/editor",
        padding=30,
        controls=[
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
