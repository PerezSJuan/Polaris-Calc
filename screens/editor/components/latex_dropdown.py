import flet as ft
from functools import partial

# Importamos los componentes de base
from flet_base.themes.themes import instance_themes as themes
import flet_base.components.texts as txt


def latex_dropdown(label, options, value=None, on_change=None, width=200):
    """
    Componente Dropdown funcional que renderiza las opciones en formato LaTeX.
    Sigue el patrón de diseño de flet_base.
    """
    return LatexDropdown(label, options, value=value, on_change=on_change, width=width)


class LatexDropdown(ft.Column):
    """
    Componente de columna que envuelve un PopupMenuButton para simular un
    dropdown con renderizado LaTeX.
    """

    def __init__(self, label, options, value=None, on_change=None, width=200):
        super().__init__()
        self.label = label
        self.options = options  # Lista de strings (formato LaTeX esperado ej: "x_1")
        self.selected_value = value if value is not None else (options[0] if options else None)
        self.on_change = on_change
        self._width = width
        self.spacing = 2
        self.tight = True

        # Widgets internos que necesitamos actualizar
        self.label_text = ft.Text(
            self.label,
            size=10,
            color=themes.actual_theme["primary"],
            visible=not self.selected_value,
        )
        self.latex_display = self._get_latex_widget(self.selected_value)

        # El área visible que muestra la selección actual
        self.display_container = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            self.label_text,
                            self.latex_display,
                        ],
                        spacing=0,
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER
                        if self.selected_value
                        else ft.MainAxisAlignment.START,
                    ),
                    ft.Icon(
                        ft.Icons.ARROW_DROP_DOWN, color=themes.actual_theme["primary"]
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(12, 8, 12, 8),
            border=ft.Border.all(
                1, ft.Colors.with_opacity(0.1, themes.actual_theme["on_surface"])
            ),
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.04, themes.actual_theme["on_surface"]),
            width=self._width,
            on_hover=self._on_hover,
        )

        # El botón de menú desplegable que contiene al display_container
        self.menu_button = ft.PopupMenuButton(
            content=self.display_container,
            items=[],
        )

        self.controls = [self.menu_button]
        self._build_menu()

    def _on_hover(self, e):
        e.control.bgcolor = ft.Colors.with_opacity(
            0.08 if e.data == "true" else 0.04, themes.actual_theme["on_surface"]
        )
        e.control.update()

    def _get_latex_widget(self, val):
        if not val:
            return txt.body("-")

        # Lógica de detección simple similar a column.py
        if "^" in val or "_" in val or "\\" in val:
            latex_str = f"$${val}$$"
        else:
            latex_str = f"$$\\text{{{val}}}$$"

        return txt.markdown(latex_str, size=14)

    def _build_menu(self):
        items = []
        for opt in self.options:
            is_selected = opt == self.selected_value
            items.append(
                ft.PopupMenuItem(
                    content=ft.Container(
                        content=self._get_latex_widget(opt),
                        padding=ft.Padding(10, 5, 10, 5),
                        bgcolor=ft.Colors.with_opacity(
                            0.1, themes.actual_theme["primary"]
                        )
                        if is_selected
                        else None,
                        border_radius=6,
                        width=self._width - 40,
                    ),
                    on_click=partial(self._handle_change, opt),
                )
            )
        self.menu_button.items = items

    async def _handle_change(self, val, e):
        self.selected_value = val
        self._sync_ui()

        if self.on_change:
            if callable(self.on_change):
                try:
                    await self.on_change(val)
                except Exception:
                    self.on_change(val)

    def _sync_ui(self):
        """Sincroniza el estado interno con los widgets visuales."""
        self.label_text.visible = not self.selected_value
        # Reemplazamos el widget de LaTeX
        self.display_container.content.controls[0].controls[1] = self._get_latex_widget(
            self.selected_value
        )
        # Ajustamos el alineamiento si hay o no valor
        self.display_container.content.controls[0].alignment = (
            ft.MainAxisAlignment.CENTER
            if self.selected_value
            else ft.MainAxisAlignment.START
        )
        self._build_menu()
        try:
            self.update()
        except Exception:
            pass

    @property
    def value(self):
        return self.selected_value

    @value.setter
    def value(self, new_val):
        self.selected_value = new_val
        self._sync_ui()


# ------------------------------------------------------------------ #
#  Demo / Main                                                       #
# ------------------------------------------------------------------ #

if __name__ == "__main__":

    def main(page: ft.Page):
        # Inicializar temas si es necesario (generalmente flet_base lo hace)
        page.title = "LatexDropdown Demo"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 50
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # Sincronizar tema manual para la demo
        themes.actual_theme = themes.dark_theme

        def on_val_change(val):
            page.snack_bar = ft.SnackBar(ft.Text(f"Seleccionado: {val}"))
            page.snack_bar.open = True
            page.update()

        options = ["x_1", "y_{total}", "\\alpha^2", "V_{in}", "masa", "F_{gravity}"]

        ld = latex_dropdown(
            label="Selecciona una Variable",
            options=options,
            value="",
            on_change=on_val_change,
            width=250,
        )

        page.add(
            txt.title("Latex Dropdown Component", size=24),
            ft.Divider(height=40),
            ld,
            ft.Container(height=20),
            txt.caption(
                "Este componente permite usar subíndices, letras griegas y más.",
                italic=True,
            ),
        )

    ft.run(main)
