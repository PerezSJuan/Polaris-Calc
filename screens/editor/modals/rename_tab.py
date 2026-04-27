import flet as ft
from flet_base.translations import instance_translation_manager as tm
from flet_base.components.inputs import text_input
from flet_base.components.modals import modal
from flet_base.components.buttons import filled_btn, text_btn
from screens.editor.modals.utils import _c


async def open_rename_tab_modal(page, current_name, on_save):
    rename_field = text_input(value=current_name)

    # Live preview of the typed name
    preview_text = ft.Text(
        current_name or "…",
        size=15,
        weight=ft.FontWeight.W_500,
        text_align=ft.TextAlign.CENTER,
    )
    preview_box = ft.Container(
        content=preview_text,
        alignment=ft.Alignment.CENTER,
        bgcolor=_c(0.04),
        border_radius=8,
        padding=ft.Padding(12, 8, 12, 8),
        border=ft.Border.all(1, _c(0.08)),
    )

    def _on_change(e):
        preview_text.value = rename_field.value or "…"
        try:
            preview_text.update()
        except RuntimeError:
            pass

    rename_field.on_change = _on_change

    def _on_save(e):
        new_name = rename_field.value.strip()
        if new_name:
            on_save(new_name)
        page.pop_dialog()

    page.show_dialog(
        modal(
            title_str=tm.translate("Renombrar pestaña"),
            content=[
                rename_field,
                preview_box,
            ],
            actions=[
                text_btn(
                    tm.translate("Cancelar"), on_click=lambda _: page.pop_dialog()
                ),
                filled_btn(tm.translate("Guardar"), on_click=_on_save),
            ],
        )
    )
