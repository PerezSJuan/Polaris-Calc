import flet as ft
from flet_base.translations import instance_translation_manager as tm
from flet_base.components.inputs import dropdown, text_input
from flet_base.components.modals import modal
from flet_base.components.buttons import filled_btn, text_btn

from screens.editor.components.column import EditableColumn
from screens.editor.utils.utils import load_default_units

default_units = load_default_units()


async def open_create_column_modal(
    page,
    pool,
    columns_row,
    on_column_data_changed,
    get_available_vars,
    refresh_all_dropdowns,
    update_shared_state,
    themes,
):
    name_field = text_input(placeholder=tm.translate("Nombre variable (ej: x, V1...)"))
    desc_field = text_input(
        placeholder=tm.translate("Descripción (opcional)"), multiline=True, max_lines=3
    )

    mag_dropdown = dropdown(
        label=tm.translate("Magnitud"),
        options=[ft.DropdownOption("none")]
        + [ft.DropdownOption(m) for m in default_units],
        value="none",
    )
    unit_dropdown = dropdown(
        label=tm.translate("Unidad"),
        options=[ft.DropdownOption("none")],
        value="none",
    )

    def on_mag_change(e):
        mag = mag_dropdown.value
        unit_dropdown.options = [ft.DropdownOption("none")] + [
            ft.DropdownOption(u) for u in default_units.get(mag, {})
        ]
        unit_dropdown.value = "none"
        try:
            unit_dropdown.update()
        except RuntimeError:
            pass

    mag_dropdown.on_change = on_mag_change

    def save_new_column(e):
        name = name_field.value.strip()
        if not name or name in pool:
            return

        pool[name] = {
            "values": [],
            "magnitude": mag_dropdown.value,
            "unit": unit_dropdown.value,
            "description": desc_field.value.strip(),
        }

        new_col = EditableColumn(
            pool=pool,
            current_name=name,
            on_change=on_column_data_changed,
            available_vars_getter=get_available_vars,
            themes=themes,
        )

        controls = columns_row.controls
        if controls and getattr(controls[-1], "data", None) == "add_button":
            controls.insert(-1, new_col)
        else:
            controls.append(new_col)

        refresh_all_dropdowns()
        update_shared_state()

        try:
            columns_row.update()
        except RuntimeError:
            pass

        page.pop_dialog()
        try:
            page.update()
        except Exception:
            pass

    name_field.on_submit = save_new_column
    desc_field.on_submit = save_new_column

    page.show_dialog(
        modal(
            title_str=tm.translate("Nueva columna de datos"),
            content=[name_field, desc_field, mag_dropdown, unit_dropdown],
            actions=[
                filled_btn(tm.translate("Crear"), on_click=save_new_column),
                filled_btn(
                    tm.translate("Cancelar"), on_click=lambda _: page.pop_dialog()
                ),
            ],
        )
    )


async def open_rename_tab_modal(page, current_name, on_save):
    """
    Opens a modal to rename a tab.
    """
    rename_field = text_input(value=current_name, autofocus=True)

    def _on_save(e):
        new_name = rename_field.value.strip()
        if new_name:
            on_save(new_name)
        page.pop_dialog()

    rename_field.on_submit = _on_save

    page.show_dialog(
        modal(
            title_str=tm.translate("Renombrar pestaña"),
            content=[rename_field],
            actions=[
                text_btn(
                    tm.translate("Cancelar"), on_click=lambda _: page.pop_dialog()
                ),
                text_btn(tm.translate("Guardar"), on_click=_on_save),
            ],
        )
    )


async def open_variable_settings_modal(
    page,
    var_name,
    pool,
    on_change,
):
    """
    Opens a modal to configure a variable's magnitude, unit, and description.
    Updates are live-editing, following the pattern of the matrix editor.
    """
    entry = pool.get(var_name, {})

    def _on_desc_change(e):
        pool[var_name]["description"] = desc_field.value.strip()
        on_change()

    desc_field = ft.TextField(
        label=tm.translate("Descripción"),
        value=entry.get("description", ""),
        on_change=_on_desc_change,
        border_radius=8,
        text_size=13,
        multiline=True,
        min_lines=1,
        max_lines=3,
    )

    async def get_unit_options(mag):
        base = [ft.DropdownOption("none")]
        if mag == "none" or mag not in default_units:
            return base
        return base + [ft.DropdownOption(u) for u in default_units[mag]]

    def _on_unit_change(e):
        pool[var_name]["unit"] = unit_dropdown.value
        on_change()

    unit_dropdown = dropdown(
        label=tm.translate("Unidad"),
        options=await get_unit_options(entry.get("magnitude", "none")),
        value=entry.get("unit", "none"),
        on_change=_on_unit_change,
    )

    async def _on_mag_change(e):
        mag = mag_dropdown.value
        pool[var_name]["magnitude"] = mag
        unit_dropdown.options = await get_unit_options(mag)
        unit_dropdown.value = "none"
        pool[var_name]["unit"] = "none"
        on_change()
        try:
            unit_dropdown.update()
        except RuntimeError:
            pass

    mag_dropdown = dropdown(
        label=tm.translate("Magnitud"),
        options=[ft.DropdownOption("none")]
        + [ft.DropdownOption(m) for m in default_units],
        value=entry.get("magnitude", "none"),
        on_change=_on_mag_change,
    )

    page.show_dialog(
        modal(
            title_str=tm.translate("Configuración de Variable"),
            content=[
                ft.Text(
                    f"{tm.translate('Variable')}: {var_name}", weight=ft.FontWeight.BOLD
                ),
                desc_field,
                mag_dropdown,
                unit_dropdown,
            ],
            actions=[
                filled_btn(
                    tm.translate("Cerrar"), on_click=lambda _: page.pop_dialog()
                ),
            ],
        )
    )
