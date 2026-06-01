from __future__ import annotations

import json
import os
import sys


current_dir = os.path.dirname(os.path.abspath(__file__))
math_utils_dir = os.path.abspath(os.path.join(current_dir, ".."))
if math_utils_dir not in sys.path:
    sys.path.append(math_utils_dir)

from function_substitution_engine import evaluate, validate


def _load_json_dict(path: str | None) -> dict:
    if not path:
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in '{path}'")
    return data


def _print_result(result) -> None:
    print("\nResult")
    print(f"  value: {result.value}")
    print(f"  unit : {result.unit}")
    print(f"  type : {result.type}")
    if result.warnings:
        print("  warnings:")
        for warning in result.warnings:
            print(f"    - {warning.code}: {warning.message}")
    if result.index_errors:
        print("  index_errors:")
        for error in result.index_errors:
            print(f"    - idx={error.index}: {error.message}")


def _print_validation(report) -> None:
    print("\nValidation")
    print(f"  valid: {report.valid}")
    if report.errors:
        print("  errors:")
        for issue in report.errors:
            print(f"    - {issue.code}: {issue.message}")
    if report.warnings:
        print("  warnings:")
        for issue in report.warnings:
            print(f"    - {issue.code}: {issue.message}")


def main() -> None:
    print("-" * 33)
    print("FUNCTION SUBSTITUTION ENGINE CLI")
    print("-" * 33)
    print("Commands: :vars <json>, :const <json>, :ops <json>, :target <unit>, :mode <auto|sympy|latex>, :quit")

    variables: dict = {}
    extra_constants: dict = {}
    operations: dict = {}
    target_unit: str | None = None
    mode = "auto"

    while True:
        try:
            raw = input("\nexpr> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not raw:
            continue
        if raw in {":quit", ":exit"}:
            print("Bye.")
            break
        if raw.startswith(":vars "):
            variables = _load_json_dict(raw[6:].strip())
            print(f"Loaded variables: {list(variables.keys())}")
            continue
        if raw.startswith(":const "):
            extra_constants = _load_json_dict(raw[7:].strip())
            print(f"Loaded extra constants: {list(extra_constants.keys())}")
            continue
        if raw.startswith(":ops "):
            print("Custom operation callables are not loadable from JSON in this CLI.")
            continue
        if raw.startswith(":target "):
            target_unit = raw[8:].strip() or None
            print(f"Target unit: {target_unit}")
            continue
        if raw.startswith(":mode "):
            mode = raw[6:].strip() or "auto"
            print(f"Mode: {mode}")
            continue

        try:
            report = validate(
                raw,
                variables=variables,
                extra_constants=extra_constants,
                operations=operations,
                target_unit=target_unit,
                mode=mode,
            )
            _print_validation(report)
            if report.valid:
                result = evaluate(
                    raw,
                    variables=variables,
                    extra_constants=extra_constants,
                    operations=operations,
                    target_unit=target_unit,
                    mode=mode,
                )
                _print_result(result)
        except Exception as exc:
            print(f"\nError: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
