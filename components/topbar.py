import flet as ft
from utils.file_utils import save_plc, load_plc


def create_topbar(page: ft.Page, color_scheme, translation_manager, shared=None):
    # Colors based on theme
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    bg_color = (
        ft.Colors.with_opacity(0.1, color_scheme["on_surface"])
        if is_dark
        else ft.Colors.with_opacity(0.05, color_scheme["on_surface"])
    )
    border_color = ft.Colors.with_opacity(0.2, color_scheme["on_surface"])

    def get_or_create_picker(key: str) -> ft.FilePicker:
        picker = shared.get(key) if shared is not None else None
        if picker is None:
            picker = ft.FilePicker()
            page.services.append(picker)
            if shared is not None:
                shared[key] = picker
        return picker

    async def handle_new(e):
        if shared is not None:
            shared["editor_data"] = [{"name": "V1", "values": []}]
            shared["current_file_path"] = None
        if page.route == "/editor":
            page.go("/home")
        page.go("/editor")
        page.update()

    async def handle_open(e):
        files = await get_or_create_picker("file_picker_open").pick_files(
            allowed_extensions=["plc"],
            dialog_title=translation_manager.translate("Seleccionar archivo PLC"),
        )
        if files:
            file_path = getattr(files[0], "path", None)
            if not file_path:
                page.snack_bar = ft.SnackBar(
                    ft.Text(
                        translation_manager.translate(
                            "No se pudo leer la ruta del archivo"
                        )
                    )
                )
                page.snack_bar.open = True
                page.update()
                return
            data_loaded = load_plc(file_path)
            if data_loaded is not None:
                if shared is not None:
                    shared["editor_data"] = data_loaded
                    shared["current_file_path"] = file_path

                page.snack_bar = ft.SnackBar(
                    ft.Text(f"{translation_manager.translate('Cargado')}: {file_path}")
                )
                page.snack_bar.open = True

                if page.route == "/editor":
                    page.go("/home")
                page.go("/editor")
                page.update()

    async def handle_save_as(e):
        saved_file = await get_or_create_picker("file_picker_save").save_file(
            allowed_extensions=["plc"],
            dialog_title=translation_manager.translate("Guardar archivo PLC como"),
            file_name="matrices.plc",
        )
        file_path = getattr(saved_file, "path", saved_file) if saved_file else None
        if file_path:
            current_data = shared.get("editor_data", []) if shared else []
            success = save_plc(file_path, current_data)
            if success:
                if shared is not None:
                    shared["current_file_path"] = file_path
                page.snack_bar = ft.SnackBar(
                    ft.Text(f"{translation_manager.translate('Guardado')}: {file_path}")
                )
                page.snack_bar.open = True
                page.update()

    async def handle_save(e):
        current_path = shared.get("current_file_path") if shared is not None else None
        if current_path:
            current_data = shared.get("editor_data", []) if shared else []
            success = save_plc(current_path, current_data)
            if success:
                page.snack_bar = ft.SnackBar(
                    ft.Text(
                        f"{translation_manager.translate('Guardado')}: {current_path}"
                    )
                )
                page.snack_bar.open = True
                page.update()
        else:
            await handle_save_as(e)

    async def handle_go_home(e):
        await page.push_route("/home")

    async def handle_trigger_create_modal(e):
        trigger = shared.get("open_create_column_modal") if shared is not None else None
        if trigger:
            await trigger(e)

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
                            on_click=handle_new,
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(translation_manager.translate("Abrir")),
                            on_click=handle_open,
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(translation_manager.translate("Guardar")),
                            on_click=handle_save,
                            disabled=page.route != "/editor",
                        ),
                        ft.MenuItemButton(
                            content=ft.Text(
                                translation_manager.translate("Guardar como")
                            ),
                            on_click=handle_save_as,
                            disabled=page.route != "/editor",
                        ),
                        ft.Divider(),
                        ft.MenuItemButton(
                            content=ft.Text(
                                translation_manager.translate("Ir al menú principal")
                            ),
                            on_click=handle_go_home,
                        ),
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
                    content=ft.Text(translation_manager.translate("Datos")),
                    visible=page.route == "/editor",
                    controls=[
                        ft.MenuItemButton(
                            content=ft.Text(
                                translation_manager.translate("Nueva columna")
                            ),
                            disabled=page.route != "/editor",
                            on_click=handle_trigger_create_modal,
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
