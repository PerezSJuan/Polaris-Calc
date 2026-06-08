import os
import sys
from typing import Any

import flet as ft

current_dir = os.path.dirname(os.path.abspath(__file__))
math_utils_path = os.path.abspath(
    os.path.join(current_dir, "..", "utils", "math_utils")
)
if math_utils_path not in sys.path:
    sys.path.append(math_utils_path)

from function_substitution_engine.ops_config import OperationNamingConfig, ValidationError

_STORAGE_KEY = "polaris.ops_overrides"


async def SettingsScreen(page: ft.Page, themes) -> ft.View:
    _store = ft.SharedPreferences()
    cfg = OperationNamingConfig()

    raw = await _store.get(_STORAGE_KEY)
    if raw:
        cfg.load_from_storage(raw)

    ui_errors: dict[str, dict[str, str]] = {}
    scroll_ref = ft.Ref[ft.Column]()
    widgets: dict[str, dict[str, Any]] = {}

    def _parse_aliases(raw: str) -> list[str]:
        return [a.strip() for a in raw.split(",") if a.strip()]

    def _clear_error(canonical: str, field: str):
        if canonical in ui_errors and field in ui_errors[canonical]:
            del ui_errors[canonical][field]
            if not ui_errors[canonical]:
                del ui_errors[canonical]
            _rebuild_ui()

    def _show_errors(errors: list[ValidationError]):
        ui_errors.clear()
        for err in errors:
            ui_errors.setdefault(err.canonical, {})[err.field] = err.message

    def _build_op_card(entry: dict[str, Any]) -> ft.Container:
        canonical = entry["canonical"]
        editable = entry["editable"]
        err = ui_errors.get(canonical, {})

        name_field = ft.TextField(
            label="Name",
            value=entry["name"],
            read_only=not editable,
            dense=True,
            on_change=lambda e, c=canonical: _clear_error(c, "name"),
        )
        prefix_field = ft.TextField(
            label="Prefix aliases",
            value=", ".join(entry["prefix_aliases"]),
            read_only=not editable,
            dense=True,
            on_change=lambda e, c=canonical: _clear_error(c, "prefix_aliases"),
        )
        suffix_field = ft.TextField(
            label="Suffix aliases",
            value=", ".join(entry["suffix_aliases"]),
            read_only=not editable,
            dense=True,
            on_change=lambda e, c=canonical: _clear_error(c, "suffix_aliases"),
        )
        enabled_switch = ft.Switch(
            value=entry["enabled"],
            disabled=not editable,
            on_change=lambda e, c=canonical: _clear_error(c, "enabled"),
        )

        name_err_txt = ft.Text(
            value=err.get("name", ""),
            color=ft.Colors.RED,
            size=11,
            visible="name" in err,
        )
        prefix_err_txt = ft.Text(
            value=err.get("prefix_aliases", ""),
            color=ft.Colors.RED,
            size=11,
            visible="prefix_aliases" in err,
        )
        suffix_err_txt = ft.Text(
            value=err.get("suffix_aliases", ""),
            color=ft.Colors.RED,
            size=11,
            visible="suffix_aliases" in err,
        )

        notations = entry.get("notations", [])
        notations_col = ft.Column(
            [
                ft.Row(
                    [ft.Text("\u26a1", size=11), ft.Text(n, size=11, color=ft.Colors.with_opacity(0.6, ft.Colors.GREY))],
                    spacing=4,
                )
                for n in notations
            ],
            spacing=2,
        )

        card = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(entry["canonical"], weight=ft.FontWeight.BOLD, size=16),
                            ft.Container(expand=True),
                            ft.Text("Enabled", size=12),
                            enabled_switch if editable
                            else ft.Text("(not configurable)", size=11, italic=True, color=ft.Colors.GREY),
                            ft.IconButton(
                                icon=ft.Icons.REFRESH_ROUNDED,
                                tooltip="Reset to default",
                                icon_size=18,
                                on_click=lambda e, c=canonical: _reset_one(c),
                                visible=editable,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Text(entry.get("description", ""), size=12, color=ft.Colors.with_opacity(0.7, ft.Colors.GREY)),
                    ft.Divider(height=8, thickness=0.5),
                    ft.Column(
                        [
                            ft.Row([ft.Text("Name:", size=12, width=100), name_field], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            name_err_txt,
                            ft.Row([ft.Text("Prefix aliases:", size=12, width=100), prefix_field], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            prefix_err_txt,
                            ft.Row([ft.Text("Suffix aliases:", size=12, width=100), suffix_field], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            suffix_err_txt,
                            notations_col,
                        ],
                        spacing=4,
                    ),
                ],
                spacing=4,
            ),
            padding=15,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, ft.Colors.GREY)),
            border_radius=8,
            margin=ft.Margin(0, 0, 0, 8),
            bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.GREY) if not editable else None,
            data=canonical,
        )

        widgets[canonical] = {
            "name": name_field,
            "prefix_aliases": prefix_field,
            "suffix_aliases": suffix_field,
            "enabled": enabled_switch,
        }
        return card

    def _collect_ui_state() -> list[dict[str, Any]]:
        merged = cfg.get_config_for_ui()
        for entry in merged:
            c = entry["canonical"]
            w = widgets.get(c)
            if w is None:
                continue
            entry["name"] = w["name"].value.strip()
            entry["prefix_aliases"] = _parse_aliases(w["prefix_aliases"].value)
            entry["suffix_aliases"] = _parse_aliases(w["suffix_aliases"].value)
            entry["enabled"] = w["enabled"].value
        return merged

    async def _save(e=None):
        merged = _collect_ui_state()
        for entry in merged:
            if not entry.get("editable", True):
                continue
            cfg.set_override(
                canonical=entry["canonical"],
                name=entry["name"],
                prefix_aliases=entry["prefix_aliases"],
                suffix_aliases=entry["suffix_aliases"],
                enabled=entry["enabled"],
            )

        errors = cfg.validate()
        if errors:
            _show_errors(errors)
            _rebuild_ui()
            return

        ui_errors.clear()
        encoded = cfg.dump_to_storage()
        await _store.set(_STORAGE_KEY, encoded)
        _rebuild_ui()

    async def _reset_one(canonical: str):
        cfg.reset_one(canonical)
        ui_errors.pop(canonical, None)
        encoded = cfg.dump_to_storage()
        await _store.set(_STORAGE_KEY, encoded)
        _rebuild_ui()

    async def _reset_all(e=None):
        cfg.reset_all()
        ui_errors.clear()
        encoded = cfg.dump_to_storage()
        await _store.set(_STORAGE_KEY, encoded)
        _rebuild_ui()

    async def _go_back(e):
        await page.push_route("/home")

    def _rebuild_ui():
        widgets.clear()
        merged = cfg.get_config_for_ui()
        cards = [_build_op_card(e) for e in merged]
        action_row = ft.Container(
            content=ft.Row(
                [
                    ft.FilledButton("Save", icon=ft.Icons.SAVE, on_click=_save),
                    ft.OutlinedButton("Reset All to Defaults", on_click=_reset_all),
                ],
                spacing=10,
            ),
            padding=ft.Padding(0, 10, 0, 0),
        )
        scroll_ref.current.controls = cards + [action_row]
        try:
            page.update()
        except Exception:
            pass

    header = ft.Row(
        [
            ft.Text("Operation Naming Configuration", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=_go_back),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    scroll_col = ft.Column(ref=scroll_ref, scroll=ft.ScrollMode.ADAPTIVE, expand=True)

    _rebuild_ui()

    return ft.View(
        route="/settings",
        controls=[
            ft.Container(
                content=ft.Column(
                    [header, ft.Divider(height=10), scroll_col],
                    expand=True,
                    spacing=0,
                ),
                padding=30,
                expand=True,
            )
        ],
    )
