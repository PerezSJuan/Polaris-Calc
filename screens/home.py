import flet as ft
import flet_base.router as fr
from flet_base.translations import instance_translation_manager as tm
import flet_base.components.texts as txt
from flet_base.components.buttons import filled_btn, icon_btn
from utils.variable_types import VARIABLE_TYPE_COLUMN_NO_ERROR
from utils.file_utils import load_plc
import os


async def HomeScreen(data: fr.DataSystem):
    async def go_to_editor(e):
        await data.page.push_route("/editor")

    async def handle_new(e):
        if data.shared is not None:
            data.shared["editor_data"] = [
                {
                    "name": "V1",
                    "values": [],
                    "errors": [],
                    "type": VARIABLE_TYPE_COLUMN_NO_ERROR,
                }
            ]
            data.shared["current_file_path"] = None
        await data.page.push_route("/editor")

    async def handle_open(e):
        files = await data.shared["file_picker_open"].pick_files(
            allowed_extensions=["plc"],
            dialog_title=tm.translate("Seleccionar archivo PLC"),
        )
        if files:
            file_path = getattr(files[0], "path", None)
            if file_path:
                loaded_data = load_plc(file_path)
                data.shared["editor_data"] = loaded_data
                data.shared["current_file_path"] = file_path
                await data.page.push_route("/editor")

    async def go_to_settings(e):
        await data.page.push_route("/settings")

    # Get assets path
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

    return ft.View(
        route="/home",
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        # Header
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.Column(
                                        [
                                            txt.title("Polaris-Calc", size=48),
                                            txt.body("High-performance spreadsheets for the next generation of work.", size=18),
                                        ],
                                        spacing=5,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20,
                            ),
                            padding=ft.Padding.symmetric(vertical=40),
                        ),
                        # Welcome message
                        ft.Container(
                            content=txt.body("Welcome! Choose an option to get started.", size=16),
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Container(height=40),
                        # Action cards
                        ft.Row(
                            [
                                ft.Card(
                                    content=ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Icon(ft.Icons.ADD, size=40, color=ft.Colors.PRIMARY),
                                                txt.body(tm.translate("Nuevo"), size=16),
                                                txt.caption("Create a new spreadsheet", size=12),
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=10,
                                        ),
                                        padding=20,
                                        alignment=ft.Alignment.CENTER,
                                        on_click=handle_new,
                                    ),
                                    width=200,
                                    height=150,
                                ),
                                ft.Card(
                                    content=ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Icon(ft.Icons.FOLDER_OPEN, size=40, color=ft.Colors.PRIMARY),
                                                txt.body(tm.translate("Abrir"), size=16),
                                                txt.caption("Open an existing file", size=12),
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=10,
                                        ),
                                        padding=20,
                                        alignment=ft.Alignment.CENTER,
                                        on_click=handle_open,
                                    ),
                                    width=200,
                                    height=150,
                                ),
                                ft.Card(
                                    content=ft.Container(
                                        content=ft.Column(
                                            [
                                                ft.Icon(ft.Icons.SETTINGS, size=40, color=ft.Colors.PRIMARY),
                                                txt.body("Settings", size=16),
                                                txt.caption("Configure the app", size=12),
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=10,
                                        ),
                                        padding=20,
                                        alignment=ft.Alignment.CENTER,
                                        on_click=go_to_settings,
                                    ),
                                    width=200,
                                    height=150,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
                        ),
                        ft.Container(height=40),
                        # Footer
                        ft.Container(
                            content=txt.caption("© 2026 Polaris-Calc. Built with Flet.", size=12),
                            alignment=ft.Alignment.CENTER,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=20,
    )