# ── Re-exports from split modal scripts ────────────────────────────────────────

from screens.editor.modals.create_column import open_create_column_modal  # legado
from screens.editor.modals.create_var import open_create_variable_modal
from screens.editor.modals.create_equation import open_create_formula_modal
from screens.editor.modals.create_plot import open_create_plot_modal
from screens.editor.modals.create_bool import open_create_bool_modal
from screens.editor.modals.create_complex import open_create_complex_modal
from screens.editor.modals.create_vector import open_create_vector_modal
from screens.editor.modals.rename_tab import open_rename_tab_modal
from screens.editor.modals.variable_settings import open_variable_settings_modal

# ── Re-exports of common utilities ───────────────────────────────────────────

from screens.editor.modals.utils import (
    SI_PREFIXES,
    _resolve_unit,
    _parse_name_unit,
    _build_prefix_dd,
    _prefix_symbol,
    _full_unit,
    _set_prefix_enabled,
    _c,
    _accent,
    _divider,
    _section_header,
    _card,
)

__all__ = [
    "open_create_column_modal",
    "open_create_variable_modal",
    "open_create_formula_modal",
    "open_create_plot_modal",
    "open_create_bool_modal",
    "open_create_complex_modal",
    "open_create_vector_modal",
    "open_rename_tab_modal",
    "open_variable_settings_modal",
    "SI_PREFIXES",
    "_resolve_unit",
    "_parse_name_unit",
    "_build_prefix_dd",
    "_prefix_symbol",
    "_full_unit",
    "_set_prefix_enabled",
    "_c",
    "_accent",
    "_divider",
    "_section_header",
    "_card",
]