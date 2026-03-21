import os
from pathlib import Path

import flet as ft
import flet_base.router as fr
from flet_base.config import flet_config
from flet_base.translations import instance_translation_manager as tm
from flet_base.themes import instance_themes as themes
import flet_base.components.texts as txt


# -----------INPUTS----------------
from components.topbar import create_topbar
from screens.editor.editor import EditorScreen


def get_assets_dir() -> Path:
    default_assets_dir = Path(__file__).parent / "assets"  # fallback for local runs
    return Path(os.environ.get("FLET_ASSETS_DIR", str(default_assets_dir))).resolve()


# -----------CONFIG-----------------
flet_config.light_theme = {
    "primary": "#6200EE",
    "on_primary": "#FFFFFF",
    "secondary": "#03DAC6",
    "on_secondary": "#000000",
    "background": "#FFFFFF",
    "on_background": "#000000",
    "surface": "#FFFFFF",
    "on_surface": "#000000",
    "text_color": "#000000",
    "error": "#B00020",
    "on_error": "#FFFFFF",
    "warning": "#FFB300",
    "success": "#388E3C",
    "link": "#0000FF",
}
flet_config.dark_theme = {
    "primary": "#BB86FC",
    "on_primary": "#000000",
    "secondary": "#03DAC6",
    "on_secondary": "#000000",
    "background": "#121212",
    "on_background": "#FFFFFF",
    "surface": "#1E1E1E",
    "on_surface": "#FFFFFF",
    "text_color": "#FFFFFF",
    "error": "#CF6679",
    "on_error": "#000000",
    "warning": "#FFB300",
    "success": "#66BB6A",
    "link": "#5252FF",
}
flet_config.default_theme_mode = "dark"

flet_config.default_language = "en"
flet_config.translations_csv_path = os.path.join(get_assets_dir(), "translations.csv")
flet_config.translations_csv_separator = ","

flet_config.default_layout_spacing = 10
flet_config.default_layout_threshold = 0


# _____________AWAKE APP________________
app = fr.FletRouter(route_init="/home")


@app.middleware
async def Awake(data: fr.DataSystem):
    data.page.title = "Polaris Calc"
    data.page.scroll = ft.ScrollMode.ADAPTIVE
    data.page.fonts = {
        "Regular":os.path.join(get_assets_dir(), "fonts", "ComicNeue-Regular.ttf"),
        "Bold": os.path.join(get_assets_dir(), "fonts", "ComicNeue-Bold.ttf"),
        "Italic": os.path.join(get_assets_dir(), "fonts", "ComicNeue-Italic.ttf"),
        "BoldItalic": os.path.join(get_assets_dir(), "fonts", "ComicNeue-BoldItalic.ttf"),
    }
    data.page.window.icon = os.path.join(get_assets_dir(), "icons", "icon.png")
    data.page.window.resizable = True
    data.page.window.min_width = 500
    data.page.window.min_height = 0

    await tm.awake(data.page)
    await themes.awake(data.page)

    # Registrar pickers una sola vez por sesión
    if "file_picker_open" not in data.shared:
        fp_open = ft.FilePicker()
        fp_save = ft.FilePicker()
        data.page.services.extend([fp_open, fp_save])
        data.shared["file_picker_open"] = fp_open
        data.shared["file_picker_save"] = fp_save

    return fr.MiddlewareResult.next()


# _____________TOPBAR________________
@app.shell()
async def TopBar(data: fr.DataSystem, view: ft.View) -> ft.View:
    # Get the topbar component
    topbar = create_topbar(data.page, themes.actual_theme, tm, data.shared)

    # Store original horizontal alignment to apply it to the content area
    # This ensures the TopBar can STRETCH to full width while content remains centered/aligned as intended
    original_h_align = view.horizontal_alignment
    view.horizontal_alignment = ft.CrossAxisAlignment.STRETCH

    # We want the topbar to be at the very top, so we remove padding from the view
    view.padding = 0
    view.spacing = 0

    # We move the existing controls into a scrollable container with padding
    content_area = ft.Container(
        content=ft.Column(
            view.controls,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            spacing=flet_config.default_layout_spacing,
            horizontal_alignment=original_h_align,  # Restore original page alignment
        ),
        padding=20,
        expand=True,
    )

    # Reconstruct view controls: TopBar on top (stretching), then the rest
    view.controls = [topbar, content_area]

    return view


# _____________ROUTES________________
@app.page("/home")
async def Home(data: fr.DataSystem):
    return ft.View(
        route="/home",
        controls=[
            txt.body(tm.translate("Acerca de")),
            # Agrega aquí todos los controles de la página
            ft.Text("Contenido de la página principal"),
            ft.Button(
                "Ir al Editor", 
                on_click=lambda _: data.page.go("/editor")
            ),
        ],
        vertical_alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )


@app.page("/settings")
async def Settings(data: fr.DataSystem):
    pass


@app.page("/editor")
async def Editor(data: fr.DataSystem):
    return await EditorScreen(data, themes)


# ------------RUN APP----------------
if __name__ == "__main__":
    app.run(assets_dir="assets")
