#!/usr/bin/env python3
"""Verify curated Roblox API claims against live Roblox creator-docs YAML.

Usage:
    python3 verify_api_drift.py
    python3 verify_api_drift.py --verbose

Exit 0 means every registry claim still matches the current docs.
Exit 1 means drift, parse errors, or network/doc fetch errors were found.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = ROOT / "api_drift_registry.yaml"
BASE_URL = "https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine"
MIRROR_DIR = ROOT / "vendor" / "creator-docs"
CACHE: dict[tuple[str, str], dict[str, Any]] = {}


def fetch_doc(category: str, name: str) -> dict[str, Any]:
    key = (category, name)
    if key in CACHE:
        return CACHE[key]
    # Prefer the local mirror (populated by mirror_creator_docs.py) so the
    # checker runs offline and against a pinned snapshot. Fall back to live
    # creator-docs when the mirror is absent.
    mirror_path = MIRROR_DIR / category / f"{name}.yaml"
    if mirror_path.is_file():
        data = yaml.safe_load(mirror_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise RuntimeError(f"{mirror_path} did not parse as a YAML mapping")
        CACHE[key] = data
        return data
    url = f"{BASE_URL}/{category}/{name}.yaml"
    req = urllib.request.Request(url, headers={"User-Agent": "roblox-brain-api-drift"})
    with urllib.request.urlopen(req, timeout=30) as response:
        data = yaml.safe_load(response.read().decode("utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{url} did not parse as a YAML mapping")
    CACHE[key] = data
    return data


def nonempty(value: Any) -> bool:
    return bool(str(value or "").strip())


def find_named(items: list[dict[str, Any]], full_name: str) -> dict[str, Any] | None:
    for item in items or []:
        if item.get("name") == full_name:
            return item
    return None


def find_method(doc: dict[str, Any], class_name: str, method_name: str) -> dict[str, Any] | None:
    methods = doc.get("methods") or []
    return find_named(methods, f"{class_name}:{method_name}") or find_named(
        methods, f"{class_name}.{method_name}"
    )


def has_parameters(item: dict[str, Any], names: list[str]) -> bool:
    params = item.get("parameters") or []
    return [p.get("name") for p in params] == names


def expected_bool(expected: str) -> bool:
    if expected == "deprecated":
        return True
    if expected in {"not_deprecated", "active"}:
        return False
    raise ValueError(f"unsupported expected value: {expected}")


def validate_file_paths(entry: dict[str, Any]) -> list[str]:
    """Validate repository paths attached to a registry claim."""
    missing = []
    for file_ref in entry.get("files") or []:
        relative = str(file_ref.get("path", "")).strip()
        if not relative:
            missing.append("missing path")
            continue
        path = ROOT / relative
        if not path.is_file():
            missing.append(relative)
    return missing


def claim_needles(entry: dict[str, Any]) -> list[str]:
    """Return identifiers that must still appear in the teaching files."""
    explicit = entry.get("teaching_needles")
    if explicit is not None:
        return [str(needle) for needle in explicit if str(needle)]

    check = entry.get("check") or {}
    check_type = check.get("type")
    if check_type == "class_deprecation_status":
        return [str(check.get("class", ""))]
    if check_type in {"constructor_deprecation_status", "constructor_description_contains"}:
        return [f"{check.get('datatype', '')}.{check.get('constructor', '')}".strip(".")]
    for key in ("property", "method", "member", "item"):
        value = check.get(key)
        if value:
            return [str(value)]
    return []


def validate_claim_tether(entry: dict[str, Any], root: Path = ROOT) -> list[str]:
    """Reject registry file links whose claimed identifiers disappeared."""
    missing = []
    needles = claim_needles(entry)
    for file_ref in entry.get("files") or []:
        relative = str(file_ref.get("path", ""))
        path = root / relative
        if path.is_file():
            haystack = path.read_text(encoding="utf-8")
            missing.extend(
                f"{relative}:{needle}"
                for needle in needles
                if not re.search(
                    rf"(?<![A-Za-z0-9_]){re.escape(needle)}(?![A-Za-z0-9_])",
                    haystack,
                    re.IGNORECASE,
                )
            )
    return missing


def verify(entry: dict[str, Any]) -> tuple[str, str]:
    check = entry["check"]
    check_type = check["type"]

    if check_type == "property_exists":
        class_name = check["class"]
        prop_name = check["property"]
        doc = fetch_doc("classes", class_name)
        prop = find_named(doc.get("properties") or [], f"{class_name}.{prop_name}")
        if prop:
            return "pass", f"{class_name}.{prop_name} exists"
        return "fail", f"{class_name}.{prop_name} missing"

    if check_type == "property_write_security":
        class_name = check["class"]
        prop_name = check["property"]
        expected = check["expected"]
        doc = fetch_doc("classes", class_name)
        prop = find_named(doc.get("properties") or [], f"{class_name}.{prop_name}")
        if not prop:
            return "fail", f"{class_name}.{prop_name} missing"
        actual = (prop.get("security") or {}).get("write")
        if actual == expected:
            return "pass", f"{class_name}.{prop_name} write security={actual}"
        return "fail", f"{class_name}.{prop_name} write security={actual}, expected {expected}"

    if check_type == "property_has_tag":
        class_name = check["class"]
        prop_name = check["property"]
        expected_tag = check["tag"]
        doc = fetch_doc("classes", class_name)
        prop = find_named(doc.get("properties") or [], f"{class_name}.{prop_name}")
        if not prop:
            return "fail", f"{class_name}.{prop_name} missing"
        tags = prop.get("tags") or []
        if expected_tag in tags:
            return "pass", f"{class_name}.{prop_name} has tag {expected_tag}"
        return "fail", f"{class_name}.{prop_name} tags={tags}, expected {expected_tag}"

    if check_type == "member_exists":
        # Searches properties, methods, and events for a named member.
        class_name = check["class"]
        member_name = check["member"]
        doc = fetch_doc("classes", class_name)
        for collection, sep in (
            ("properties", "."),
            ("methods", ":"),
            ("events", "."),
            ("callbacks", "."),
        ):
            if find_named(doc.get(collection) or [], f"{class_name}{sep}{member_name}"):
                return "pass", f"{class_name}{sep}{member_name} exists ({collection})"
        return "fail", f"{class_name} member {member_name} missing (checked properties/methods/events/callbacks)"

    if check_type == "enum_item_exists":
        enum_name = check["enum"]
        item_name = check["item"]
        doc = fetch_doc("enums", enum_name)
        if find_named(doc.get("items") or [], item_name):
            return "pass", f"{enum_name}.{item_name} exists"
        return "fail", f"{enum_name}.{item_name} missing"

    if check_type == "property_deprecation_status":
        class_name = check["class"]
        prop_name = check["property"]
        doc = fetch_doc("classes", class_name)
        prop = find_named(doc.get("properties") or [], f"{class_name}.{prop_name}")
        if not prop:
            return "fail", f"{class_name}.{prop_name} missing"
        deprecated = nonempty(prop.get("deprecation_message")) or "Deprecated" in (prop.get("tags") or [])
        expected = expected_bool(check["expected"])
        if deprecated == expected:
            return "pass", f"{class_name}.{prop_name} deprecated={deprecated}"
        return "fail", f"{class_name}.{prop_name} deprecated={deprecated}, expected {expected}"

    if check_type == "method_parameter_type":
        class_name = check["class"]
        method_name = check["method"]
        parameter_name = check["parameter"]
        expected_type = check["expected"]
        doc = fetch_doc("classes", class_name)
        method = find_method(doc, class_name, method_name)
        if not method:
            return "fail", f"{class_name}:{method_name} missing"
        parameter = next((p for p in method.get("parameters") or [] if p.get("name") == parameter_name), None)
        if not parameter:
            return "fail", f"{class_name}:{method_name} parameter {parameter_name} missing"
        actual_type = parameter.get("type")
        if actual_type == expected_type:
            return "pass", f"{class_name}:{method_name}.{parameter_name} type={actual_type}"
        return "fail", f"{class_name}:{method_name}.{parameter_name} type={actual_type}, expected {expected_type}"

    if check_type == "method_return_type":
        class_name = check["class"]
        method_name = check["method"]
        return_index = int(check.get("return_index", 0))
        expected_type = check["expected"]
        doc = fetch_doc("classes", class_name)
        method = find_method(doc, class_name, method_name)
        if not method:
            return "fail", f"{class_name}:{method_name} missing"
        returns = method.get("returns") or []
        if return_index >= len(returns):
            return "fail", f"{class_name}:{method_name} return {return_index} missing"
        actual_type = returns[return_index].get("type")
        if actual_type == expected_type:
            return "pass", f"{class_name}:{method_name} return {return_index} type={actual_type}"
        return "fail", f"{class_name}:{method_name} return {return_index} type={actual_type}, expected {expected_type}"

    if check_type == "method_description_contains":
        class_name = check["class"]
        method_name = check["method"]
        needle = check["contains"]
        doc = fetch_doc("classes", class_name)
        method = find_method(doc, class_name, method_name)
        if not method:
            return "fail", f"{class_name}:{method_name} missing"
        haystack = str(method.get("description") or "") + " " + str(method.get("summary") or "")
        if needle.lower() in haystack.lower():
            return "pass", f"{class_name}:{method_name} description contains '{needle}'"
        return "fail", f"{class_name}:{method_name} description does not contain '{needle}'"

    if check_type == "class_deprecation_status":
        class_name = check["class"]
        doc = fetch_doc("classes", class_name)
        deprecated = nonempty(doc.get("deprecation_message")) or "Deprecated" in (doc.get("tags") or [])
        expected = expected_bool(check["expected"])
        if deprecated == expected:
            return "pass", f"{class_name} deprecated={deprecated}"
        return "fail", f"{class_name} deprecated={deprecated}, expected {expected}"

    if check_type == "method_deprecation_status":
        class_name = check["class"]
        member_name = check["member"]
        doc = fetch_doc("classes", class_name)
        member = find_method(doc, class_name, member_name)
        if not member:
            return "fail", f"{class_name}:{member_name} missing"
        deprecated = nonempty(member.get("deprecation_message")) or "Deprecated" in (member.get("tags") or [])
        expected = expected_bool(check["expected"])
        if deprecated == expected:
            return "pass", f"{class_name}:{member_name} deprecated={deprecated}"
        return "fail", f"{class_name}:{member_name} deprecated={deprecated}, expected {expected}"

    if check_type == "constructor_deprecation_status":
        datatype = check["datatype"]
        ctor_name = check["constructor"]
        params = check.get("parameters") or []
        doc = fetch_doc("datatypes", datatype)
        candidates = [c for c in doc.get("constructors") or [] if c.get("name") == f"{datatype}.{ctor_name}"]
        ctor = next((c for c in candidates if has_parameters(c, params)), None)
        if not ctor:
            return "fail", f"{datatype}.{ctor_name}({', '.join(params)}) missing"
        deprecated = nonempty(ctor.get("deprecation_message")) or "Deprecated" in (ctor.get("tags") or [])
        expected = expected_bool(check["expected"])
        if deprecated == expected:
            return "pass", f"{datatype}.{ctor_name}({', '.join(params)}) deprecated={deprecated}"
        return "fail", f"{datatype}.{ctor_name}({', '.join(params)}) deprecated={deprecated}, expected {expected}"

    if check_type == "constructor_description_contains":
        datatype = check["datatype"]
        ctor_name = check["constructor"]
        params = check.get("parameters") or []
        needle = check["contains"]
        doc = fetch_doc("datatypes", datatype)
        candidates = [c for c in doc.get("constructors") or [] if c.get("name") == f"{datatype}.{ctor_name}"]
        ctor = next((c for c in candidates if has_parameters(c, params)), None)
        if not ctor:
            return "fail", f"{datatype}.{ctor_name}({', '.join(params)}) missing"
        haystack = str(ctor.get("description") or "") + " " + str(ctor.get("summary") or "")
        if needle.lower() in haystack.lower():
            return "pass", f"{datatype}.{ctor_name}({', '.join(params)}) description contains '{needle}'"
        return "fail", f"{datatype}.{ctor_name}({', '.join(params)}) description does not contain '{needle}'"

    return "error", f"unknown check type: {check_type}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Roblox API drift registry")
    parser.add_argument("--verbose", action="store_true", help="show passing checks")
    args = parser.parse_args()

    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    entries = registry.get("entries") or []
    print(f"Checking {len(entries)} registry entries...\n")

    counts = {"pass": 0, "fail": 0, "error": 0}
    for entry in entries:
        try:
            missing_paths = validate_file_paths(entry)
            if missing_paths:
                status = "error"
                message = "missing repository path(s): " + ", ".join(missing_paths)
            else:
                untethered = validate_claim_tether(entry)
                if untethered:
                    status = "error"
                    message = "registry identifier(s) absent from teaching files: " + ", ".join(untethered)
                else:
                    status, message = verify(entry)
        except Exception as exc:  # noqa: BLE001, surface exact failing entry
            status, message = "error", str(exc)
        counts[status] += 1
        if status != "pass" or args.verbose:
            icon = {"pass": "✅", "fail": "❌", "error": "⚠️"}[status]
            print(f"  {icon} {entry.get('id', '<missing id>')}: {message}")
            if status != "pass":
                print(f"     Claim: {entry.get('claim', '?')}")
                for file_ref in entry.get("files") or []:
                    print(f"     File: {file_ref.get('path', '?')}")

    print(f"\nResults: {counts['pass']} pass, {counts['fail']} drift, {counts['error']} error")
    if counts["fail"] or counts["error"]:
        print("❌ Drift or verification errors detected")
        return 1
    print("✅ All registered API claims verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
