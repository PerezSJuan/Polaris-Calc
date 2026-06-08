import json
import os
import sys

import pytest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
utils_path = os.path.join(project_root, "utils", "math_utils")
if utils_path not in sys.path:
    sys.path.append(utils_path)

from function_substitution_engine import DEFAULT_OPERATIONS, evaluate
from function_substitution_engine.ops_config import (
    OperationNamingConfig,
    ValidationError,
    _load_overrides,
    _save_overrides,
    build_user_operations,
)


# ======================================================================
# OperationNamingConfig — 18 tests
# ======================================================================


def test_defaults_structure():
    cfg = OperationNamingConfig()
    merged = cfg.get_config_for_ui()
    assert len(merged) == 14
    for entry in merged:
        assert "canonical" in entry
        assert "name" in entry
        assert "prefix_aliases" in entry
        assert "suffix_aliases" in entry
        assert "enabled" in entry
        assert "description" in entry
        assert "notations" in entry
        assert "editable" in entry
        assert isinstance(entry["prefix_aliases"], list)
        assert isinstance(entry["suffix_aliases"], list)
        assert isinstance(entry["notations"], list)


def test_defaults_bar():
    cfg = OperationNamingConfig()
    merged = cfg.get_config_for_ui()
    bar = next(e for e in merged if e["canonical"] == "bar")
    assert bar["editable"] is False
    assert bar["prefix_aliases"] == []
    assert bar["suffix_aliases"] == []


def test_apply_overrides_dict():
    cfg = OperationNamingConfig()
    cfg.apply_overrides({"det": {"name": "determinante"}})
    merged = cfg.get_config_for_ui()
    det = next(e for e in merged if e["canonical"] == "det")
    assert det["name"] == "determinante"


def test_apply_overrides_string():
    cfg = OperationNamingConfig()
    cfg.apply_overrides('{"det": {"name": "determinante"}}')
    merged = cfg.get_config_for_ui()
    det = next(e for e in merged if e["canonical"] == "det")
    assert det["name"] == "determinante"


def test_apply_overrides_none():
    cfg = OperationNamingConfig()
    cfg.apply_overrides(None)
    merged = cfg.get_config_for_ui()
    det = next(e for e in merged if e["canonical"] == "det")
    assert det["name"] == "det"


def test_apply_overrides_encoded_list():
    cfg = OperationNamingConfig()
    encoded = _save_overrides({"det": {"name": "determinante"}})
    cfg.load_from_storage(encoded)
    merged = cfg.get_config_for_ui()
    det = next(e for e in merged if e["canonical"] == "det")
    assert det["name"] == "determinante"


def test_set_override_name():
    cfg = OperationNamingConfig()
    cfg.set_override("det", name="determinante")
    merged = cfg.get_config_for_ui()
    det = next(e for e in merged if e["canonical"] == "det")
    assert det["name"] == "determinante"


def test_set_override_prefix_aliases():
    cfg = OperationNamingConfig()
    cfg.set_override("det", prefix_aliases=[r"\det", r"\determinante"])
    merged = cfg.get_config_for_ui()
    det = next(e for e in merged if e["canonical"] == "det")
    assert det["prefix_aliases"] == [r"\det", r"\determinante"]


def test_set_override_suffix_aliases():
    cfg = OperationNamingConfig()
    cfg.set_override("factorial", suffix_aliases=["fac"])
    merged = cfg.get_config_for_ui()
    fac = next(e for e in merged if e["canonical"] == "factorial")
    assert fac["suffix_aliases"] == ["fac"]


def test_set_override_enabled():
    cfg = OperationNamingConfig()
    cfg.set_override("det", enabled=False)
    merged = cfg.get_config_for_ui()
    det = next(e for e in merged if e["canonical"] == "det")
    assert det["enabled"] is False


def test_set_override_default_value_removes_entry():
    cfg = OperationNamingConfig()
    cfg.set_override("det", name="determinante")
    cfg.set_override("det", name="det")
    assert "det" not in cfg._overrides


def test_reset_one():
    cfg = OperationNamingConfig()
    cfg.set_override("det", name="determinante")
    cfg.set_override("factorial", enabled=False)
    cfg.reset_one("det")
    merged = cfg.get_config_for_ui()
    det = next(e for e in merged if e["canonical"] == "det")
    assert det["name"] == "det"
    fac = next(e for e in merged if e["canonical"] == "factorial")
    assert fac["enabled"] is False


def test_reset_all():
    cfg = OperationNamingConfig()
    cfg.set_override("det", name="determinante")
    cfg.set_override("factorial", enabled=False)
    cfg.reset_all()
    merged = cfg.get_config_for_ui()
    for entry in merged:
        assert entry["name"] == entry["canonical"] or entry["canonical"] == "bar"


def test_round_trip():
    cfg = OperationNamingConfig()
    cfg.set_override("det", name="determinante", prefix_aliases=[r"\det"])
    exported = cfg.export_overrides()
    cfg2 = OperationNamingConfig()
    cfg2.apply_overrides(exported)
    m1 = cfg.get_config_for_ui()
    m2 = cfg2.get_config_for_ui()
    for e1, e2 in zip(m1, m2):
        assert e1["name"] == e2["name"]
        assert e1["prefix_aliases"] == e2["prefix_aliases"]
        assert e1["enabled"] == e2["enabled"]


def test_get_config_for_ui_merged():
    cfg = OperationNamingConfig()
    cfg.set_override("det", name="determinante")
    cfg.set_override("factorial", enabled=False)
    merged = cfg.get_config_for_ui()
    det = next(e for e in merged if e["canonical"] == "det")
    assert det["name"] == "determinante"
    fac = next(e for e in merged if e["canonical"] == "factorial")
    assert fac["enabled"] is False
    # Other operations unchanged
    mean = next(e for e in merged if e["canonical"] == "mean")
    assert mean["name"] == "mean"
    assert mean["enabled"] is True


def test_dump_storage_roundtrip():
    cfg = OperationNamingConfig()
    cfg.set_override("det", name="determinante", prefix_aliases=[r"\det"])
    encoded = cfg.dump_to_storage()
    cfg2 = OperationNamingConfig()
    cfg2.load_from_storage(encoded)
    assert cfg2._overrides == cfg._overrides


def test_dump_storage_empty():
    cfg = OperationNamingConfig()
    encoded = cfg.dump_to_storage()
    assert encoded == []


def test_export_overrides_no_changes():
    cfg = OperationNamingConfig()
    exported = cfg.export_overrides()
    assert exported == "{}"


# ======================================================================
# validate() — 8 tests
# ======================================================================


def test_validate_duplicate_name():
    cfg = OperationNamingConfig()
    cfg.set_override("sum", name="myop")
    cfg.set_override("mean", name="myop")
    errors = cfg.validate()
    assert len(errors) >= 2
    assert any(e.field == "name" and "myop" in e.message for e in errors)


def test_validate_prefix_collision():
    cfg = OperationNamingConfig()
    cfg.set_override("det", prefix_aliases=["myalias"])
    cfg.set_override("factorial", name="myalias")
    errors = cfg.validate()
    assert any("myalias" in e.message for e in errors)


def test_validate_reserved_suffix():
    cfg = OperationNamingConfig()
    cfg.set_override("factorial", suffix_aliases=["!"])
    errors = cfg.validate()
    assert len(errors) >= 1
    assert any(
        e.field == "suffix_aliases" and "reserved" in e.message for e in errors
    )


def test_validate_suffix_collision():
    cfg = OperationNamingConfig()
    cfg.set_override("factorial", suffix_aliases=["postfix"])
    cfg.set_override("det", suffix_aliases=["postfix"])
    errors = cfg.validate()
    assert any("postfix" in e.message for e in errors)


def test_validate_empty_name():
    cfg = OperationNamingConfig()
    cfg.set_override("det", name="")
    errors = cfg.validate()
    assert any(e.field == "name" and "non-empty" in e.message for e in errors)


def test_validate_invalid_name_chars():
    cfg = OperationNamingConfig()
    cfg.set_override("det", name="det value")
    errors = cfg.validate()
    assert any(e.field == "name" and "invalid" in e.message for e in errors)


def test_validate_prefix_alias_space():
    cfg = OperationNamingConfig()
    cfg.set_override("det", prefix_aliases=[r"\det value"])
    errors = cfg.validate()
    assert any(e.field == "prefix_aliases" and "spaces" in e.message for e in errors)


def test_validate_valid():
    cfg = OperationNamingConfig()
    cfg.set_override("det", name="determinante", prefix_aliases=[r"\det"])
    cfg.set_override("factorial", enabled=True)
    errors = cfg.validate()
    assert errors == []


# ======================================================================
# build_user_operations — 5 tests
# ======================================================================


def test_build_contains_all_enabled():
    cfg = OperationNamingConfig()
    ops = build_user_operations(cfg)
    assert len(ops) >= 13  # bar included but h as no prefix/suffix keys beyond Path B


def test_build_excludes_disabled():
    cfg = OperationNamingConfig()
    cfg.set_override("det", enabled=False)
    cfg.set_override("factorial", enabled=False)
    ops = build_user_operations(cfg)
    assert "det" not in ops
    assert "factorial" not in ops


def test_build_renamed_operation_appears():
    cfg = OperationNamingConfig()
    cfg.set_override("det", name="determinante", prefix_aliases=[r"\det"])
    ops = build_user_operations(cfg)
    assert "determinante" in ops
    assert r"\det" in ops


def test_build_prefix_aliases_and_hard_coded_keys():
    cfg = OperationNamingConfig()
    cfg.set_override("factorial", name="fac", prefix_aliases=[])
    ops = build_user_operations(cfg)
    assert "fac" in ops
    assert r"\factorial" in ops  # Path B re-registration


def test_build_fn_callable():
    cfg = OperationNamingConfig()
    cfg.set_override("det", name="determinante")
    ops = build_user_operations(cfg)
    assert "determinante" in ops
    assert callable(ops["determinante"].fn)


# ======================================================================
# Integration — 3 tests
# ======================================================================


def test_integration_prefix_call_renamed():
    cfg = OperationNamingConfig()
    cfg.set_override("det", name="determinante", prefix_aliases=[r"\det"])
    ops = build_user_operations(cfg)
    A = [[1.0, 2.0], [3.0, 4.0]]
    result = evaluate(
        "determinante(A)",
        {"A": {"type": "matrix", "value": A, "unit": "m"}},
        operations=ops,
        target_unit="m^2",
    )
    assert result.value == pytest.approx(-2.0)


def test_integration_postfix_factorial_after_rename():
    cfg = OperationNamingConfig()
    cfg.set_override("factorial", name="fac", prefix_aliases=[])
    ops = build_user_operations(cfg)
    result = evaluate(
        "5!",
        {},
        operations=ops,
    )
    assert result.value == 120.0


def test_integration_surround_determinant():
    cfg = OperationNamingConfig()
    cfg.set_override("det", name="determinante")
    ops = build_user_operations(cfg)
    A = [[1.0, 2.0], [3.0, 4.0]]
    result = evaluate(
        r"|A|",
        {"A": {"type": "matrix", "value": A, "unit": "m"}},
        operations=ops,
        mode="latex",
    )
    assert result.value == pytest.approx(-2.0)
