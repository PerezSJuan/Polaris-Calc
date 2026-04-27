import asyncio
import flet as ft
from flet_base.components.buttons import icon_btn

def EditorTabBar(
    tabs,
    active_index,
    on_switch_tab,
    on_add_tab,
    on_delete_tab,
    on_rename_tab,
    on_move_tab,
    themes,
):
    """
    Component that renders the tab bar for the editor.
    """
    tabs_row = ft.Row(spacing=4, scroll=ft.ScrollMode.ADAPTIVE)

    for i, tab in enumerate(tabs):
        is_active = i == active_index
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
            async def on_rename_click(e, idx=i):
                await on_rename_tab(idx)

            controls.extend(
                [
                    icon_btn(
                        icon=ft.Icons.EDIT_OUTLINED,
                        on_click=on_rename_click,
                        icon_size=14,
                    ),
                    icon_btn(
                        icon=ft.Icons.CLOSE,
                        on_click=lambda e, idx=i: on_delete_tab(idx),
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
            on_click=lambda e, idx=i: on_switch_tab(idx),
            data=i,
        )

        draggable = ft.Draggable(
            group="tabs",
            content=tab_btn,
            data=i,
        )

        drag_target = ft.DragTarget(
            group="tabs",
            content=draggable,
            on_accept=lambda e: on_move_tab(e, i),
        )

        tabs_row.controls.append(drag_target)

    # "+" button to add a new tab
    tabs_row.controls.append(
        icon_btn(
            icon=ft.Icons.ADD,
            on_click=on_add_tab,
            icon_size=18,
        )
    )

    return ft.Container(
        content=tabs_row,
        border=ft.Border(
            bottom=ft.BorderSide(
                1,
                ft.Colors.with_opacity(0.15, themes.actual_theme["on_surface"]),
            )
        ),
    )
