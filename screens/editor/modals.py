import flet as ft
from flet_base.translations import instance_translation_manager as tm
from flet_base.components.inputs import dropdown, text_input
from flet_base.components.modals import modal
from flet_base.components.buttons import filled_btn
from screens.editor.column import EditableColumn
from screens.editor.utils import load_default_units

default_units = load_default_units()

async def open_create_column_modal(
    page, 
    pool, 
    columns_container, 
    on_column_data_changed, 
    get_available_vars, 
    refresh_all_dropdowns, 
    update_shared_state, 
    themes
):
    name_field = text_input(
        placeholder=tm.translate("Nombre variable (ej: x, V1...)")
    )

    mag_dropdown = dropdown(
        label=tm.translate("Magnitud"),
        options=[ft.dropdown.Option("none")]
        + [ft.dropdown.Option(m) for m in default_units.keys()],
        value="none",
    )

    unit_dropdown = dropdown(
        label=tm.translate("Unidad"),
        options=[ft.dropdown.Option("none")],
        value="none",
    )

    async def on_mag_change(e):
        mag = mag_dropdown.value
        unit_dropdown.options = [ft.dropdown.Option("none")] + [
            ft.dropdown.Option(u) for u in default_units.get(mag, {}).keys()
        ]
        unit_dropdown.value = "none"
        try:
            unit_dropdown.update()
        except RuntimeError:
            pass

    mag_dropdown.on_change = on_mag_change

    async def save_new_column(e):
        new_name = name_field.value.strip()
        if not new_name:
            return
        if new_name in pool:
            # Maybe show an error here in the future
            return

        pool[new_name] = {
            "values": [],
            "magnitude": mag_dropdown.value,
            "unit": unit_dropdown.value,
        }

        # Add UI column
        new_col = EditableColumn(
            pool=pool,
            current_name=new_name,
            on_change=on_column_data_changed,
            available_vars_getter=get_available_vars,
            themes=themes,
        )
        columns_container.controls.append(new_col)

        refresh_all_dropdowns()
        update_shared_state()
        try:
            columns_container.update()
        except RuntimeError:
            pass

        page.pop_dialog()

    create_dialog = modal(
        title_str=tm.translate("Nueva columna de datos"),
        content=[name_field, mag_dropdown, unit_dropdown],
        actions=[
            filled_btn(tm.translate("Crear"), on_click=save_new_column),
            filled_btn(
                tm.translate("Cancelar"),
                on_click=lambda _: page.pop_dialog(),
            ),
        ],
    )

    page.show_dialog(create_dialog)
