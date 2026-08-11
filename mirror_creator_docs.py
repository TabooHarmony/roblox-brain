#!/usr/bin/env python3
"""Mirror Roblox creator-docs engine reference YAML locally for offline drift checks.

The API drift checker (verify_api_drift.py) normally fetches each referenced
YAML from raw.githubusercontent.com per claim. This script downloads the
reference files the registry actually uses into vendor/creator-docs/ so the
checker can run with no network, and so you can diff versions over time.

Usage:
    python3 mirror_creator_docs.py            # fetch registry-referenced files
    python3 mirror_creator_docs.py --all      # fetch the full engine reference tree
    python3 mirror_creator_docs.py --check    # verify mirror is fresh/present (no fetch)

The mirror is a cache, not a vendored copy of the docs. It is gitignored by
default; commit it only if you want pinned offline CI.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = ROOT / "api_drift_registry.yaml"
MIRROR_DIR = ROOT / "vendor" / "creator-docs"
BASE_URL = "https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine"
# The tree API is the canonical list of engine reference files.
TREE_URL = "https://api.github.com/repos/Roblox/creator-docs/git/trees/main?recursive=1"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "roblox-brain-mirror"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()


def registry_referenced_files() -> set[str]:
    """Return the set of (category, name) pairs the drift registry references."""
    registry = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    referenced: set[str] = set()
    for entry in registry.get("entries") or []:
        check = entry.get("check") or {}
        check_type = check.get("type")
        if check_type in {"property_exists", "property_write_security", "property_has_tag",
                          "property_deprecation_status", "member_exists",
                          "method_parameter_type", "method_return_type",
                          "method_description_contains", "method_deprecation_status",
                          "class_deprecation_status"}:
            referenced.add(f"classes/{check.get('class', '')}.yaml")
        elif check_type == "enum_item_exists":
            referenced.add(f"enums/{check.get('enum', '')}.yaml")
        elif check_type in {"constructor_deprecation_status", "constructor_description_contains"}:
            referenced.add(f"datatypes/{check.get('datatype', '')}.yaml")
    return {p for p in referenced if not p.endswith("/.yaml")}


def all_reference_files() -> set[str]:
    """Return every engine reference file path from the live tree API."""
    data = json.loads(fetch(TREE_URL).decode("utf-8"))
    files: set[str] = set()
    for item in data.get("tree") or []:
        path = item.get("path", "")
        if path.startswith("content/en-us/reference/engine/") and path.endswith(".yaml"):
            files.add(path.split("content/en-us/reference/engine/", 1)[1])
    return files


def mirror_files(files: set[str], verbose: bool = False) -> tuple[int, int]:
    """Download files into the mirror. Returns (ok, failed)."""
    ok = failed = 0
    for rel in sorted(files):
        dest = MIRROR_DIR / rel
        if dest.exists():
            ok += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        url = f"{BASE_URL}/{rel}"
        try:
            data = fetch(url)
            dest.write_bytes(data)
            ok += 1
            if verbose:
                print(f"  ✓ {rel}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  ✗ {rel}: {exc}")
    return ok, failed


def main() -> int:
    parser = argparse.ArgumentParser(description="Mirror creator-docs engine reference YAML")
    parser.add_argument("--all", action="store_true", help="mirror the full engine reference tree")
    parser.add_argument("--check", action="store_true", help="verify mirror presence without fetching")
    args = parser.parse_args()

    if args.check:
        files = registry_referenced_files()
        missing = [f for f in sorted(files) if not (MIRROR_DIR / f).exists()]
        if missing:
            print(f"❌ Mirror missing {len(missing)} registry-referenced files:")
            for f in missing:
                print(f"   {f}")
            print("Run: python3 mirror_creator_docs.py")
            return 1
        print(f"✅ Mirror present for all {len(files)} registry-referenced files")
        return 0

    files = all_reference_files() if args.all else registry_referenced_files()
    print(f"Mirroring {len(files)} files to {MIRROR_DIR}...")
    ok, failed = mirror_files(files, verbose=not args.all)
    print(f"\nDone: {ok} ok, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
