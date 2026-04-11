import flet as ft
from flet_base.translations import instance_translation_manager as tm
from flet_base.components.texts import body, subtitle
from flet_base.components.buttons import icon_btn
from functools import partial


def SummaryView(pool, themes, on_open_settings=None):
    """
    Returns a view showing a summary card for each variable in the pool.
    """

    async def _handle_open_settings(var_name, e):
        # var_name se pasa a través de functools.partial
        if on_open_settings:
            await on_open_settings(var_name)

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
            content=body(str(i + 1), size=10, color=themes.actual_theme["on_primary"]),
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
                            icon_btn(
                                ft.Icons.SETTINGS,
                                icon_size=18,
                                # Usamos partial para pasar el nombre sin ensuciar el atributo 'data' del botón
                                on_click=partial(_handle_open_settings, name),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Container(
                        content=body(
                            description
                            if description
                            else tm.translate("Sin descripción"),
                            size=11,
                            color=ft.Colors.with_opacity(
                                0.7, themes.actual_theme["on_surface"]
                            ),
                        ),
                        height=35,  # Forzar un espacio para la descripción
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
                    ft.Container(height=12),  # Espacio extra abajo
                ],
                spacing=8,
            ),
            width=220,
            height=200,
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
