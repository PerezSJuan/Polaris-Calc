import os
import sys
from pathlib import Path

import flet as ft
import flet_base.router as fr
from flet_base.config import flet_config
from flet_base.translations import instance_translation_manager as tm
from flet_base.themes import instance_themes as themes
import flet_base.components.buttons as btn
import flet_base.components.texts as txt
import flet_base.components.data_display as dd
import flet_base.components.inputs as inputs



def get_assets_dir() -> Path:
    default_assets_dir = Path(__file__).parent / "assets"   # fallback for local runs
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
    data.page.fonts = os.path.join(get_assets_dir(), "fonts", "ComicNeue-Regular.ttf")
    data.page.window.icon = os.path.join(get_assets_dir(), "icons", "icon.png")
    data.page.window.resizable = True
    data.page.window.min_width = 500
    data.page.window.min_height = 0
    
    await tm.awake(data.page)
    await themes.awake(data.page)
    return fr.MiddlewareResult.next()


# _____________TOPBAR________________
@app.shell()
async def TopBar(data: fr.DataSystem):
    pass


#_____________ROUTES________________
@app.page("/home")
async def Home(data:fr.DataSystem):
    data.page.add(txt.body(tm.translate("Acerca de")))



# ------------RUN APP----------------
if __name__ == "__main__":
    app.run(assets_dir="assets")
