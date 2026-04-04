import flet as ft
import flet_base.router as fr
from flet_base.translations import instance_translation_manager as tm

from screens.editor.utils import normalize_editor_data
from screens.editor.column import EditableColumn
from screens.editor.modals import open_create_column_modal


async def EditorScreen(data: fr.DataSystem, themes):
    """Main screen for managing and editing data vectors."""

    raw_data = normalize_editor_data(data.shared.get("editor_data", []))
    pool = {
        col["name"]: {
            "values": col["values"],
            "magnitude": col["magnitude"],
            "unit": col["unit"],
        }
        for col in raw_data
    }

    columns_row = ft.Row(
        scroll=ft.ScrollMode.ADAPTIVE,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=20,
    )

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def get_available_vars():
        return list(pool.keys())

    def _visible_columns():
        return [c for c in columns_row.controls if isinstance(c, EditableColumn)]

    def _try_update(widget):
        try:
            widget.update()
        except RuntimeError:
            pass

    # ------------------------------------------------------------------ #
    #  Pool / state sync                                                   #
    # ------------------------------------------------------------------ #

    def update_shared_state():
        data.shared["editor_data"] = [
            {"name": name, **entry} for name, entry in pool.items()
        ]

    def on_column_data_changed():
        update_shared_state()
        for col in _visible_columns():
            col.sync_with_pool()
            col._just_changed = False

    def refresh_all_dropdowns():
        for col in _visible_columns():
            col.update_dropdown()

    # ------------------------------------------------------------------ #
    #  Column management                                                   #
    # ------------------------------------------------------------------ #

    def _make_column(name):
        return EditableColumn(
            pool=pool,
            current_name=name,
            on_change=on_column_data_changed,
            available_vars_getter=get_available_vars,
            themes=themes,
        )

    def _insert_column(col):
        """Insert before the '+' card (always the last control)."""
        controls = columns_row.controls
        if controls and getattr(controls[-1], "data", None) == "add_button":
            controls.insert(-1, col)
        else:
            controls.append(col)

    async def add_ui_column(e=None):
        visible_names = {col.current_name for col in _visible_columns()}
        target = next((v for v in get_available_vars() if v not in visible_names), None)

        if target is None:
            target = get_available_vars()[0] if pool else "V1"
            pool.setdefault(target, {"values": [], "magnitude": "none", "unit": "none"})

        _insert_column(_make_column(target))
        _try_update(columns_row)

    async def clear_all(e=None):
        pool.clear()
        pool["V1"] = {"values": [], "magnitude": "none", "unit": "none"}
        columns_row.controls.clear()
        columns_row.controls.append(add_column_card)
        await add_ui_column()
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

    # ------------------------------------------------------------------ #
    #  Initial UI                                                          #
    # ------------------------------------------------------------------ #

    for name in (col["name"] for col in raw_data):
        columns_row.controls.append(_make_column(name))

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
    columns_row.controls.append(add_column_card)

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
            ft.Column(
                [
                    ft.Text(
                        tm.translate("Editor de Matrices"),
                        size=36,
                        weight=ft.FontWeight.W_800,
                    ),
                    ft.Text(
                        tm.translate("Gestiona y edita tus vectores de datos"),
                        size=16,
                        color=ft.Colors.with_opacity(
                            0.6, themes.actual_theme["on_surface"]
                        ),
                    ),
                ],
                spacing=5,
            ),
            ft.Divider(height=20, thickness=0.5),
            action_buttons,
            ft.Container(height=20),
            ft.Container(
                content=columns_row,
                expand=True,
                padding=10,
                border_radius=15,
                bgcolor=ft.Colors.with_opacity(
                    0.01, themes.actual_theme["on_background"]
                ),
            ),
        ],
    )
