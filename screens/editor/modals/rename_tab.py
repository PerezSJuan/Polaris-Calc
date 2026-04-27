import flet as ft
from flet_base.translations import instance_translation_manager as tm
from flet_base.components.inputs import text_input
from flet_base.components.modals import modal
from flet_base.components.buttons import filled_btn, text_btn


async def open_rename_tab_modal(page, current_name, on_save):
    rename_field = text_input(
        placeholder=tm.translate("Nombre de la pestaña"), value=current_name
    )

    def _on_save(e):
        new_name = rename_field.value.strip()
        if new_name:
            on_save(new_name)
        page.pop_dialog()
        try:
            page.update()
        except Exception:
            pass

    page.show_dialog(
        modal(
            title_str=tm.translate("Renombrar pestaña"),
            content=[
                ft.Container(
                    content=rename_field,
                    width=300,
                    padding=ft.Padding(0, 10, 0, 10),
                ),
            ],
            actions=[
                text_btn(
                    tm.translate("Cancelar"),
                    on_click=lambda _: (page.pop_dialog(), page.update()),
                ),
                filled_btn(tm.translate("Guardar"), on_click=_on_save),
            ],
        )
    )
