import os
from pathlib import Path

import flet as ft
import flet_base.router as fr
from flet_base.config import flet_config
from flet_base.translations import instance_translation_manager as tm
from flet_base.themes.themes import themes as ThemesClass
import flet_base.components.texts as txt


# -----------INPUTS----------------
from components.topbar import create_topbar
from screens.editor.editor import EditorScreen
from screens.home import HomeScreen


def get_assets_dir() -> Path:
    default_assets_dir = Path(__file__).parent / "assets"  # fallback for local runs
    return Path(os.environ.get("FLET_ASSETS_DIR", str(default_assets_dir))).resolve()


# -----------CONFIG-----------------
flet_config.default_layout_spacing = 10
flet_config.default_layout_threshold = 0

flet_config.light_theme.update(
    {
        "primary": "#0B7D73",
        "on_primary": "#FFFFFF",
        "secondary": "#18B7B0",
        "on_secondary": "#062F2C",
        "background": "#F7F9F9",
        "on_background": "#0F172A",
        "surface": "#FFFFFF",
        "on_surface": "#111827",
        "text_color": "#0F172A",
        "error": "#D14343",
        "on_error": "#FFFFFF",
        "warning": "#F59E0B",
        "success": "#15803D",
        "link": "#2563EB",
        "formula_accent": "#7C6AF7",
        "constant_accent": "#2DD4BF",
        "error_accent": "#F59E0B",
    }
)

flet_config.dark_theme.update(
    {
        "primary": "#14B8A6",
        "on_primary": "#042F2E",
        "secondary": "#2DD4BF",
        "on_secondary": "#042F2E",
        "background": "#0B1214",
        "on_background": "#E6F1F1",
        "surface": "#0F1A1D",
        "on_surface": "#D1E7E7",
        "text_color": "#E6F1F1",
        "error": "#F87171",
        "on_error": "#1A0B0B",
        "warning": "#FBBF24",
        "success": "#4ADE80",
        "link": "#60A5FA",
        "formula_accent": "#7C6AF7",
        "constant_accent": "#2DD4BF",
        "error_accent": "#F59E0B",
    }
)

flet_config.default_theme_mode = "dark"
flet_config.default_language = "en"
flet_config.translations_csv_path = os.path.join(get_assets_dir(), "translations.csv")
flet_config.translations_csv_separator = ","

flet_config.font_files = {
    "Regular": "fonts/ComicNeue-Regular.ttf",
    "Bold": "fonts/ComicNeue-Bold.ttf",
    "Italic": "fonts/ComicNeue-Italic.ttf",
    "BoldItalic": "fonts/ComicNeue-BoldItalic.ttf",
}
flet_config.main_font_family = "Regular"

from flet_base.themes.themes import instance_themes as themes

themes.__init__()  # Re-read config after updates


# _____________AWAKE APP________________
app = fr.FletRouter(route_init="/home")


@app.middleware
async def Awake(data: fr.DataSystem):
    data.page.title = "Polaris Calc"
    data.page.scroll = ft.ScrollMode.ADAPTIVE
    data.page.window.icon = "icons/favicon.png"
    data.page.window.resizable = True
    data.page.window.min_width = 500
    data.page.window.min_height = 0
    data.page.theme_animation = ft.Animation(0)

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
    # --- Optimized Custom Theme Switcher ---
    async def custom_switch_theme(page: ft.Page):
        # 1. Determine and set the new state in silence
        if themes.actual_theme == themes.light_theme:
            new_mode = ft.ThemeMode.DARK
            themes.actual_theme = themes.dark_theme
            pref = "dark"
        else:
            new_mode = ft.ThemeMode.LIGHT
            themes.actual_theme = themes.light_theme
            pref = "light"

        # 2. Apply state to page properties (without calling page.update() yet)
        page.theme_mode = new_mode
        page.bgcolor = themes.actual_theme["background"]

        # 3. Save preference asynchronously
        await ft.SharedPreferences().set("theme", pref)

        # 4. Trigger the route refresh.
        # The router's on_route_change will call page.update() at the end,
        # sending EVERYTHING (theme + new controls) in a single transaction.
        class RefreshEvent:
            def __init__(self, route):
                self.route = route

        await page.on_route_change(RefreshEvent(page.route))

    topbar = create_topbar(
        data.page, themes.actual_theme, tm, custom_switch_theme, data.shared
    )

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
    return await HomeScreen(data)


@app.page("/settings")
async def Settings(data: fr.DataSystem):
    pass


@app.page("/editor")
async def Editor(data: fr.DataSystem):
    return await EditorScreen(data, themes)


# ------------RUN APP----------------
if __name__ == "__main__":
    app.run(assets_dir="assets")
