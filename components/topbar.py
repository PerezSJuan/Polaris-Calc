import flet as ft


def create_topbar(page: ft.Page, color_scheme, translation_manager):
    # Colors based on theme
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    bg_color = (
        ft.Colors.with_opacity(0.1, color_scheme["on_surface"])
        if is_dark
        else ft.Colors.with_opacity(0.05, color_scheme["on_surface"])
    )
    border_color = ft.Colors.with_opacity(0.2, color_scheme["on_surface"])

    return ft.Container(
        bgcolor=bg_color,
        height=35,
        alignment=ft.Alignment.CENTER_LEFT,
        padding=ft.Padding.only(left=5, right=5),
        border=ft.Border.only(bottom=ft.BorderSide(1, border_color)),
        content=ft.MenuBar(
            style=ft.MenuStyle(
                alignment=ft.Alignment.TOP_LEFT,
                mouse_cursor=ft.MouseCursor.CLICK,
                bgcolor=ft.Colors.TRANSPARENT,
                shadow_color=ft.Colors.TRANSPARENT,
            ),
            controls=[
                ft.SubmenuButton(
                    content=ft.Text(translation_manager.translate("Archivo")),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text(translation_manager.translate("Nuevo")),
                            on_click=lambda _: print("Nuevo archivo"),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(translation_manager.translate("Abrir")),
                            on_click=lambda _: print("Abrir archivo"),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(translation_manager.translate("Guardar")),
                            on_click=lambda _: print("Guardar archivo"),
                        ),
                        ft.Divider(),
                        ft.MenuItemButton(
                            content=ft.Text(translation_manager.translate("Salir")),
                            on_click=lambda _: page.window.close(),
                        ),
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text(translation_manager.translate("Editar")),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text(translation_manager.translate("Deshacer")),
                            on_click=lambda _: print("Deshacer"),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(translation_manager.translate("Rehacer")),
                            on_click=lambda _: print("Rehacer"),
                        ),
                        ft.Divider(),
                        ft.MenuItemButton(
                            content=ft.Text(translation_manager.translate("Cortar")),
                            on_click=lambda _: print("Cortar"),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(translation_manager.translate("Copiar")),
                            on_click=lambda _: print("Copiar"),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(translation_manager.translate("Pegar")),
                            on_click=lambda _: print("Pegar"),
                        ),
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text(translation_manager.translate("Ver")),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text(
                                translation_manager.translate("Pantalla completa")
                            ),
                            on_click=lambda _: print("Pantalla completa"),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(translation_manager.translate("Tema")),
                            on_click=lambda _: print("Tema claro/oscuro"),
                        ),
                    ],
                ),
                ft.SubmenuButton(
                    content=ft.Text(translation_manager.translate("Ayuda")),
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text(
                                translation_manager.translate("Documentación")
                            ),
                            on_click=lambda _: print("Documentación"),
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(translation_manager.translate("Acerca de")),
                            on_click=lambda _: print("Acerca de"),
                        ),
                    ],
                ),
            ],
        ),
    )
