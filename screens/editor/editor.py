import flet as ft
import flet_base.router as fr
from flet_base.translations import instance_translation_manager as tm


from screens.editor.utils import normalize_editor_data
from screens.editor.column import EditableColumn
from screens.editor.modals import open_create_column_modal


async def EditorScreen(data: fr.DataSystem, themes):
    """
    Main screen for managing and editing data vectors.
    """
    # Prepare shared data
    raw_data = normalize_editor_data(data.shared.get("editor_data", []))

    # Central pool for synchronization
    # pool: { "V1": {"values": [1,2,3], "magnitude": "none", "unit": "none"} }
    pool = {
        col["name"]: {
            "values": col["values"],
            "magnitude": col["magnitude"],
            "unit": col["unit"],
        }
        for col in raw_data
    }

    # Initial states
    initial_ui_configs = [col["name"] for col in raw_data]

    # UI Main Container
    columns_container = ft.Row(
        scroll=ft.ScrollMode.ADAPTIVE,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=20,
    )

    # --- Logic Callbacks ---

    def get_available_vars():
        return list(pool.keys())

    def update_shared_state():
        export_list = []
        for name, entry in pool.items():
            export_list.append(
                {
                    "name": name,
                    "values": entry["values"],
                    "magnitude": entry["magnitude"],
                    "unit": entry["unit"],
                }
            )
        data.shared["editor_data"] = export_list

    def on_column_data_changed():
        # Update the shared state dictionary and then synchronize all column UI.
        # ``refresh_all_columns`` now uses ``sync_with_pool`` which updates the
        # existing TextField controls in place, preserving the user's focus.
        update_shared_state()
        refresh_all_columns()
        # Reset the just_changed flag on all columns after the refresh.
        for ctrl in columns_container.controls:
            if isinstance(ctrl, EditableColumn):
                ctrl._just_changed = False

    def refresh_all_dropdowns():
        for ctrl in columns_container.controls:
            if isinstance(ctrl, EditableColumn):
                ctrl.update_dropdown()

    def refresh_all_columns():
        """Synchronize all ``EditableColumn`` instances with the current ``pool``.

        ``sync_with_pool`` updates the existing ``TextField`` controls in place
        without recreating the widget hierarchy, which preserves the user's
        cursor position. We now apply it to every column; the method itself avoids
        actions that would steal focus.
        """
        for ctrl in columns_container.controls:
            if isinstance(ctrl, EditableColumn):
                ctrl.sync_with_pool()

    async def trigger_create_modal(e=None):
        await open_create_column_modal(
            page=data.page,
            pool=pool,
            columns_container=columns_container,
            on_column_data_changed=on_column_data_changed,
            get_available_vars=get_available_vars,
            refresh_all_dropdowns=refresh_all_dropdowns,
            update_shared_state=update_shared_state,
            themes=themes,
        )

    # Let other parts of the app (like top-bar) trigger the modal
    data.shared["open_create_column_modal"] = trigger_create_modal

    # --- UI Actions ---

    async def add_ui_column(e=None):
        """Add a new visual column for a variable that is not yet displayed.

        The function determines which variables are already represented, picks
        the first unused variable (or creates a new one), and inserts a new
        ``EditableColumn`` before the ``+`` button card. The container update is
        performed after insertion; individual column widgets handle their own
        UI updates, preserving any active text field focus.
        """
        all_vars = get_available_vars()
        # Variables currently shown in visible columns.
        visible_vars = [
            ctrl.current_name
            for ctrl in columns_container.controls
            if isinstance(ctrl, EditableColumn)
        ]

        target_var = next((v for v in all_vars if v not in visible_vars), None)

        if not target_var:
            target_var = all_vars[0] if all_vars else "V1"
            if target_var not in pool:
                pool[target_var] = {"values": [], "magnitude": "none", "unit": "none"}

        new_col = EditableColumn(
            pool=pool,
            current_name=target_var,
            on_change=on_column_data_changed,
            available_vars_getter=get_available_vars,
            themes=themes,
        )

        # Insert before the "+" button card.
        if (
            len(columns_container.controls) > 0
            and getattr(columns_container.controls[-1], "data", None) == "add_button"
        ):
            columns_container.controls.insert(-1, new_col)
        else:
            columns_container.controls.append(new_col)

        # Update the container layout.
        try:
            columns_container.update()
        except RuntimeError:
            pass

    async def clear_all(e=None):
        pool.clear()
        pool["V1"] = {"values": [], "magnitude": "none", "unit": "none"}
        columns_container.controls.clear()
        # Re-add V1 visually
        # (This avoids leaving the screen completely empty)
        await add_ui_column()
        # Add the "+" button card back if it was cleared
        columns_container.controls.append(add_column_card)
        update_shared_state()
        try:
            columns_container.update()
        except RuntimeError:
            pass

    # --- Initial UI Construction ---

    for name in initial_ui_configs:
        columns_container.controls.append(
            EditableColumn(
                pool=pool,
                current_name=name,
                on_change=on_column_data_changed,
                available_vars_getter=get_available_vars,
                themes=themes,
            )
        )

    # "+" card for adding more visual columns
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
    columns_container.controls.append(add_column_card)

    # Top Buttons Row
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
                        tm.translate("Agregar columna"),
                        icon=ft.Icons.ADD_BOX_OUTLINED,
                        on_click=add_ui_column,
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
                content=columns_container,
                expand=True,
                padding=10,
                border_radius=15,
                bgcolor=ft.Colors.with_opacity(
                    0.01, themes.actual_theme["on_background"]
                ),
            ),
        ],
    )
