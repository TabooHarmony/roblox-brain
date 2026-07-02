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
import sys
import urllib.request
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = ROOT / "api_drift_registry.yaml"
BASE_URL = "https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine"
CACHE: dict[tuple[str, str], dict[str, Any]] = {}


def fetch_doc(category: str, name: str) -> dict[str, Any]:
    key = (category, name)
    if key in CACHE:
        return CACHE[key]
    url = f"{BASE_URL}/{category}/{name}.yaml"
    req = urllib.request.Request(url, headers={"User-Agent": "roblox-brain-api-drift"})
    with urllib.request.urlopen(req, timeout=30) as response:
        data = yaml.safe_load(response.read().decode("utf-8"))
    if not isinstance(data, dict):
        raise RuntimeError(f"{url} did not parse as a YAML mapping")
    CACHE[key] = data
    return data


def fetch_first(name: str, categories: tuple[str, ...]) -> dict[str, Any]:
    errors = []
    for category in categories:
        try:
            return fetch_doc(category, name)
        except Exception as exc:  # noqa: BLE001, report all attempted locations
            errors.append(f"{category}: {exc}")
    raise RuntimeError(f"could not fetch {name}: " + "; ".join(errors))


def nonempty(value: Any) -> bool:
    return bool(str(value or "").strip())


def find_named(items: list[dict[str, Any]], full_name: str) -> dict[str, Any] | None:
    for item in items or []:
        if item.get("name") == full_name:
            return item
    return None


def has_parameters(item: dict[str, Any], names: list[str]) -> bool:
    params = item.get("parameters") or []
    return [p.get("name") for p in params] == names


def expected_bool(expected: str) -> bool:
    if expected == "deprecated":
        return True
    if expected in {"not_deprecated", "active"}:
        return False
    raise ValueError(f"unsupported expected value: {expected}")


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

    if check_type == "class_deprecation_status":
        class_name = check["class"]
        doc = fetch_doc("classes", class_name)
        deprecated = nonempty(doc.get("deprecation_message")) or "Deprecated" in (doc.get("tags") or [])
        expected = expected_bool(check["expected"])
        if deprecated == expected:
            return "pass", f"{class_name} deprecated={deprecated}"
        return "fail", f"{class_name} deprecated={deprecated}, expected {expected}"

    if check_type == "member_deprecation_status":
        class_name = check["class"]
        member_name = check["member"]
        doc = fetch_doc("classes", class_name)
        member = find_named(doc.get("methods") or [], f"{class_name}:{member_name}")
        member = member or find_named(doc.get("methods") or [], f"{class_name}.{member_name}")
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
    print("✅ All API claims verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
