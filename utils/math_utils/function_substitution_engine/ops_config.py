from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .default_operations import DEFAULT_OPERATIONS, OperationSpec


@dataclass
class ValidationError:
    canonical: str
    field: str
    message: str


_RESERVED_SUFFIX_TOKENS = {"!", "t", "T"}

_HARD_CODED_KEYS: dict[str, str] = {
    "factorial": r"\factorial",
    "bar": "bar",
    "transpose": "transpose",
}


def _load_defaults() -> list[dict[str, Any]]:
    path = Path(__file__).resolve().parent / "default_ops_config.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_overrides(raw: list[str] | None) -> dict[str, dict[str, Any]]:
    if not raw:
        return {}
    result: dict[str, dict[str, Any]] = {}
    for item in raw:
        k, _, v = item.partition("=")
        try:
            result[k] = json.loads(v)
        except json.JSONDecodeError:
            pass
    return result


def _save_overrides(overrides: dict[str, Any]) -> list[str]:
    return [f"{k}={json.dumps(v)}" for k, v in overrides.items()]


class OperationNamingConfig:
    def __init__(self):
        self._defaults: list[dict[str, Any]] = _load_defaults()
        self._overrides: dict[str, dict[str, Any]] = {}

    # ── public helpers for persistence ─────────────────────────────────

    def load_from_storage(self, raw: list[str] | None) -> None:
        self._overrides = _load_overrides(raw)

    def dump_to_storage(self) -> list[str]:
        return _save_overrides(self._overrides)

    # ── apply_overrides ────────────────────────────────────────────────

    def apply_overrides(self, raw: str | dict[str, Any] | None) -> None:
        if raw is None:
            return
        if isinstance(raw, str):
            parsed: dict[str, Any] = json.loads(raw)
            self._overrides.update(parsed)
        elif isinstance(raw, dict):
            self._overrides.update(raw)

    # ── export_overrides ───────────────────────────────────────────────

    def export_overrides(self) -> str:
        return json.dumps(self._overrides)

    # ── get_config_for_ui ──────────────────────────────────────────────

    def get_config_for_ui(self) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for default in self._defaults:
            canonical = default["canonical"]
            merged = dict(default)
            if canonical in self._overrides:
                merged.update(self._overrides[canonical])
            result.append(merged)
        return result

    # ── set_override ───────────────────────────────────────────────────

    def set_override(
        self,
        canonical: str,
        name: str | None = None,
        prefix_aliases: list[str] | None = None,
        suffix_aliases: list[str] | None = None,
        enabled: bool | None = None,
    ) -> None:
        default = self._find_default(canonical)
        if default is None:
            return

        override: dict[str, Any] = dict(self._overrides.get(canonical, {}))

        if name is not None:
            if name == default["name"]:
                override.pop("name", None)
            else:
                override["name"] = name
        if prefix_aliases is not None:
            if prefix_aliases == default["prefix_aliases"]:
                override.pop("prefix_aliases", None)
            else:
                override["prefix_aliases"] = prefix_aliases
        if suffix_aliases is not None:
            if suffix_aliases == default["suffix_aliases"]:
                override.pop("suffix_aliases", None)
            else:
                override["suffix_aliases"] = suffix_aliases
        if enabled is not None:
            if enabled == default["enabled"]:
                override.pop("enabled", None)
            else:
                override["enabled"] = enabled

        if override:
            self._overrides[canonical] = override
        else:
            self._overrides.pop(canonical, None)

    # ── reset_one / reset_all ──────────────────────────────────────────

    def reset_one(self, canonical: str) -> None:
        self._overrides.pop(canonical, None)

    def reset_all(self) -> None:
        self._overrides.clear()

    # ── validate ───────────────────────────────────────────────────────

    def validate(self) -> list[ValidationError]:
        errors: list[ValidationError] = []
        merged = self.get_config_for_ui()

        name_to_ops: dict[str, list[str]] = {}
        all_prefix_keys: dict[str, str] = {}
        all_suffix_keys: dict[str, str] = {}

        for entry in merged:
            canonical: str = entry["canonical"]
            name: str = entry["name"]
            prefix_aliases: list[str] = entry["prefix_aliases"]
            suffix_aliases: list[str] = entry["suffix_aliases"]

            # Empty name
            if not name:
                errors.append(ValidationError(
                    canonical=canonical,
                    field="name",
                    message=f"Operation '{canonical}' must have a non-empty name",
                ))

            # Invalid characters in name
            if name and not all(c.isalnum() or c in ("_", "\\") for c in name):
                errors.append(ValidationError(
                    canonical=canonical,
                    field="name",
                    message=f"Name '{name}' in '{canonical}' contains invalid characters",
                ))

            # Prefix alias with spaces
            for alias in prefix_aliases:
                if " " in alias:
                    errors.append(ValidationError(
                        canonical=canonical,
                        field="prefix_aliases",
                        message=f"Prefix alias '{alias}' in '{canonical}' contains spaces",
                    ))

            # Reserved suffix tokens
            for alias in suffix_aliases:
                if alias in _RESERVED_SUFFIX_TOKENS:
                    errors.append(ValidationError(
                        canonical=canonical,
                        field="suffix_aliases",
                        message=f"Suffix alias '{alias}' in '{canonical}' is a reserved built-in token",
                    ))

            # Track name for duplicate check
            name_to_ops.setdefault(name, []).append(canonical)

            # Track prefix keys
            for alias in prefix_aliases:
                if alias in all_prefix_keys:
                    other = all_prefix_keys[alias]
                    if other != canonical:
                        errors.append(ValidationError(
                            canonical=canonical,
                            field="prefix_aliases",
                            message=f"Prefix alias '{alias}' in '{canonical}' collides with '{other}'",
                        ))
                else:
                    all_prefix_keys[alias] = canonical

            # Track suffix keys
            for alias in suffix_aliases:
                if alias in all_suffix_keys:
                    other = all_suffix_keys[alias]
                    if other != canonical:
                        errors.append(ValidationError(
                            canonical=canonical,
                            field="suffix_aliases",
                            message=f"Suffix alias '{alias}' in '{canonical}' collides with '{other}'",
                        ))
                else:
                    all_suffix_keys[alias] = canonical

        # Check name collisions (including names as prefix keys)
        for name, ops_list in name_to_ops.items():
            if len(ops_list) > 1:
                for op in ops_list:
                    errors.append(ValidationError(
                        canonical=op,
                        field="name",
                        message=f"Name '{name}' is used by more than one operation: {', '.join(ops_list)}",
                    ))
            else:
                [op] = ops_list
                if name in all_prefix_keys and all_prefix_keys[name] != op:
                    errors.append(ValidationError(
                        canonical=op,
                        field="name",
                        message=f"Prefix alias '{name}' in '{op}' collides with '{all_prefix_keys[name]}'",
                    ))

        return errors

    # ── helpers ────────────────────────────────────────────────────────

    def _find_default(self, canonical: str) -> dict[str, Any] | None:
        for d in self._defaults:
            if d["canonical"] == canonical:
                return d
        return None


def build_user_operations(config: OperationNamingConfig | list[dict[str, Any]]) -> dict[str, OperationSpec]:
    if isinstance(config, OperationNamingConfig):
        config_list = config.get_config_for_ui()
    else:
        config_list = config

    result: dict[str, OperationSpec] = {}

    for entry in config_list:
        if not entry["enabled"]:
            continue

        canonical: str = entry["canonical"]
        if canonical not in DEFAULT_OPERATIONS:
            continue

        orig_spec = DEFAULT_OPERATIONS[canonical]
        new_spec = OperationSpec(
            name=entry["name"],
            fn=orig_spec.fn,
            arity=orig_spec.arity,
            input_types=orig_spec.input_types,
            output_type=orig_spec.output_type,
            preserves_units=orig_spec.preserves_units,
            min_arity=orig_spec.min_arity,
            max_arity=orig_spec.max_arity,
            aliases=tuple(entry["prefix_aliases"]),
            result_type_rule=orig_spec.result_type_rule,
            validator=orig_spec.validator,
            unit_rule=orig_spec.unit_rule,
        )

        # Path A — user-facing prefix keys
        result[entry["name"]] = new_spec
        for alias in entry["prefix_aliases"]:
            result[alias] = new_spec

        # Path B — internal re-registration of hard-coded keys
        if canonical in _HARD_CODED_KEYS:
            result[_HARD_CODED_KEYS[canonical]] = new_spec

        # Path C — suffix aliases (postfix tokens)
        for alias in entry["suffix_aliases"]:
            result[alias] = new_spec

    return result
