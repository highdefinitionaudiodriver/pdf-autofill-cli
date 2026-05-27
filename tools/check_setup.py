#!/usr/bin/env python3
"""Validate the local setup for pdf-autofill-cli."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

PROJECT_FILES = [
    "main.py",
    "requirements.txt",
    "config/user_profile.json",
    "config/mapping_config.json",
    "templates/sample_template.pdf",
    "templates/iryouhi_meisai/user_profile.iryouhi.json",
    "templates/iryouhi_meisai/mapping_config.iryouhi.json",
]

JSON_PAIRS = [
    (
        ROOT / "config" / "user_profile.json",
        ROOT / "config" / "mapping_config.json",
        "default sample",
    ),
    (
        ROOT / "templates" / "iryouhi_meisai" / "user_profile.iryouhi.json",
        ROOT / "templates" / "iryouhi_meisai" / "mapping_config.iryouhi.json",
        "iryouhi meisai sample",
    ),
]


def _ok(message: str) -> None:
    print(f"OK   {message}")


def _warn(message: str) -> None:
    print(f"WARN {message}")


def _ng(message: str) -> None:
    print(f"NG   {message}")


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        return None, f"missing JSON file: {path.relative_to(ROOT)}"
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {path.relative_to(ROOT)} ({exc})"
    if not isinstance(data, dict):
        return None, f"JSON root must be an object: {path.relative_to(ROOT)}"
    return data, None


def check_project_files() -> list[str]:
    errors: list[str] = []
    for relative in PROJECT_FILES:
        path = ROOT / relative
        if path.exists():
            _ok(f"found {relative}")
        else:
            errors.append(f"missing required file: {relative}")
            _ng(errors[-1])
    return errors


def check_python_modules() -> list[str]:
    errors: list[str] = []
    if importlib.util.find_spec("fitz") is None:
        errors.append("missing Python package: PyMuPDF (install with: python -m pip install -r requirements.txt)")
        _ng(errors[-1])
    else:
        _ok("python package available: PyMuPDF")
    return errors


def check_font_candidates() -> list[str]:
    font_candidates = [
        Path("C:/Windows/Fonts/msgothic.ttc"),
        Path("C:/Windows/Fonts/meiryo.ttc"),
        Path("C:/Windows/Fonts/YuGothR.ttc"),
    ]
    found = [path for path in font_candidates if path.exists()]
    if found:
        _ok(f"Japanese font candidate found: {found[0]}")
    else:
        _warn("Japanese font candidate was not found; ASCII fallback will be used")
    return []


def _validate_mapping_entry(entry: Any, index: int, profile: dict[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(entry, dict):
        return [f"{label}: mappings[{index}] must be an object"]

    field_key = entry.get("field_key")
    if not isinstance(field_key, str) or not field_key:
        errors.append(f"{label}: mappings[{index}].field_key is required")
    elif field_key not in profile:
        errors.append(f"{label}: profile key not found for mappings[{index}]: {field_key}")

    method = entry.get("method", "coordinate")
    if method == "coordinate":
        for key in ("page", "x", "y"):
            if key not in entry:
                errors.append(f"{label}: mappings[{index}].{key} is required for coordinate")
            elif not isinstance(entry[key], (int, float)):
                errors.append(f"{label}: mappings[{index}].{key} must be numeric")
        font_size = entry.get("font_size", 10)
        if not isinstance(font_size, (int, float)) or font_size <= 0:
            errors.append(f"{label}: mappings[{index}].font_size must be a positive number")
    elif method == "form_field":
        if not isinstance(entry.get("field_name"), str) or not entry.get("field_name"):
            errors.append(f"{label}: mappings[{index}].field_name is required for form_field")
    else:
        errors.append(f"{label}: mappings[{index}].method is unsupported: {method}")

    return errors


def check_mapping_pair(profile_path: Path, mapping_path: Path, label: str) -> list[str]:
    errors: list[str] = []
    profile, profile_error = _load_json(profile_path)
    mapping, mapping_error = _load_json(mapping_path)
    for error in (profile_error, mapping_error):
        if error:
            errors.append(error)
            _ng(error)
    if profile is None or mapping is None:
        return errors

    mappings = mapping.get("mappings")
    if not isinstance(mappings, list) or not mappings:
        errors.append(f"{label}: mappings must be a non-empty array")
        _ng(errors[-1])
        return errors

    for index, entry in enumerate(mappings):
        errors.extend(_validate_mapping_entry(entry, index, profile, label))

    if errors:
        for error in errors:
            _ng(error)
    else:
        _ok(f"{label}: {len(mappings)} mapping entries validated")
    return errors


def main() -> int:
    print(f"Checking pdf-autofill-cli setup under: {ROOT}")
    errors: list[str] = []
    errors.extend(check_project_files())
    errors.extend(check_python_modules())
    errors.extend(check_font_candidates())
    for profile_path, mapping_path, label in JSON_PAIRS:
        errors.extend(check_mapping_pair(profile_path, mapping_path, label))

    if errors:
        print()
        print("Setup check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print()
    print("PDF Auto-Fill setup check OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
