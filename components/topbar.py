import flet as ft


def create_topbar(page: ft.Page, color_scheme, translation_manager):
    """
    Crea un topbar estilo Windows con Menús (Archivo, Editar, etc.)
    """

    # Definir las acciones de los menús (placeholders por ahora)
    def handle_menu_click(e):
        print(f"Click en: {e.control.content.value}")
        # Aquí se pueden añadir lógica para cada opción

    return ft.MenuBar(
        expand=True,
        style=ft.MenuStyle(
            alignment=ft.alignment.top_left,
            mouse_cursor=ft.MouseCursor.CLICK,
        ),
        controls=[
            ft.SubmenuButton(
                content=ft.Text("Archivo"),
                controls=[
                    ft.MenuItemButton(
                        content=ft.Text("Nuevo"),
                        leading=ft.Icon(ft.icons.CREATE_NEW_FOLDER_OUTLINED),
                        on_click=handle_menu_click,
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("Abrir"),
                        leading=ft.Icon(ft.icons.FOLDER_OPEN),
                        on_click=handle_menu_click,
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("Guardar"),
                        leading=ft.Icon(ft.icons.SAVE_OUTLINED),
                        on_click=handle_menu_click,
                    ),
                    ft.Divider(),
                    ft.MenuItemButton(
                        content=ft.Text("Salir"),
                        leading=ft.Icon(ft.icons.CLOSE),
                        on_click=lambda _: page.window_close(),
                    ),
                ],
            ),
            ft.SubmenuButton(
                content=ft.Text("Editar"),
                controls=[
                    ft.MenuItemButton(
                        content=ft.Text("Deshacer"),
                        leading=ft.Icon(ft.icons.UNDO),
                        on_click=handle_menu_click,
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("Rehacer"),
                        leading=ft.Icon(ft.icons.REDO),
                        on_click=handle_menu_click,
                    ),
                    ft.Divider(),
                    ft.MenuItemButton(
                        content=ft.Text("Cortar"),
                        leading=ft.Icon(ft.icons.CONTENT_CUT),
                        on_click=handle_menu_click,
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("Copiar"),
                        leading=ft.Icon(ft.icons.CONTENT_COPY),
                        on_click=handle_menu_click,
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("Pegar"),
                        leading=ft.Icon(ft.icons.CONTENT_PASTE),
                        on_click=handle_menu_click,
                    ),
                ],
            ),
            ft.SubmenuButton(
                content=ft.Text("Ver"),
                controls=[
                    ft.MenuItemButton(
                        content=ft.Text("Pantalla completa"),
                        leading=ft.Icon(ft.icons.FULLSCREEN),
                        on_click=handle_menu_click,
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("Tema claro/oscuro"),
                        leading=ft.Icon(ft.icons.BRIGHTNESS_4),
                        on_click=handle_menu_click,
                    ),
                ],
            ),
            ft.SubmenuButton(
                content=ft.Text("Ayuda"),
                controls=[
                    ft.MenuItemButton(
                        content=ft.Text("Documentación"),
                        leading=ft.Icon(ft.icons.DESCRIPTION_OUTLINED),
                        on_click=handle_menu_click,
                    ),
                    ft.MenuItemButton(
                        content=ft.Text("Acerca de"),
                        leading=ft.Icon(ft.icons.INFO_OUTLINE),
                        on_click=handle_menu_click,
                    ),
                ],
            ),
        ],
    )
