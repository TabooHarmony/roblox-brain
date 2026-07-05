#!/usr/bin/env python3
"""Check version pins in tooling/testing skills against latest releases.

Scans for package@version patterns and checks GitHub releases for each.
Reports pinned vs latest. Non-blocking (exit 0 always) — version bumps
are intentional decisions.

Usage:
    python3 verify_version_pins.py
"""

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS_DIR = ROOT / "skills"
TIMEOUT = 15

# Map of package@version patterns to GitHub repos for release checking
PACKAGE_REPOS = {
    "rojo": "rojo-rbx/rojo",
    "wally": "UpliftGames/wally",
    "selene": "kampfkarren/selene",
    "stylua": "JohnnyMorganz/StyLua",
    "lune": "lune-org/lune",
    "testez": "roblox/testez",
}


def find_version_pins(content: str) -> list[tuple[str, str]]:
    """Find package@version pins in skill content."""
    pins = []
    # Match patterns like rojo@7.4.4, wally@0.3.2, testez@0.4.1
    for match in re.finditer(r'(\w+)@(\d+\.\d+\.\d+)', content):
        pkg = match.group(1).lower()
        version = match.group(2)
        if pkg in PACKAGE_REPOS:
            pins.append((pkg, version))
    return pins


def get_latest_release(repo: str) -> str | None:
    """Get latest release tag from GitHub API."""
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "roblox-brain-version-check",
            "Accept": "application/vnd.github.v3+json",
        })
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
            tag = data.get("tag_name", "")
            # Strip leading 'v' from tag
            return tag.lstrip("v") if tag else None
    except Exception:
        return None


def normalize_version(v: str) -> tuple[int, int, int]:
    """Parse version string to comparable tuple."""
    parts = v.split(".")
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
    except (ValueError, IndexError):
        return (0, 0, 0)


def main() -> int:
    all_pins = []
    for entry in sorted(os.listdir(SKILLS_DIR)):
        skill_dir = SKILLS_DIR / entry
        if not skill_dir.is_dir():
            continue
        for filepath in [skill_dir / "SKILL.md", skill_dir / "references" / "full.md"]:
            if not filepath.exists():
                continue
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            pins = find_version_pins(content)
            for pkg, version in pins:
                all_pins.append((entry, pkg, version))

    # Deduplicate
    seen = set()
    unique_pins = []
    for skill, pkg, version in all_pins:
        key = (pkg, version)
        if key not in seen:
            seen.add(key)
            unique_pins.append((skill, pkg, version))

    print(f"Checking {len(unique_pins)} version pins...\n")

    up_to_date = 0
    stale = 0
    unknown = 0

    for skill, pkg, pinned in unique_pins:
        repo = PACKAGE_REPOS[pkg]
        latest = get_latest_release(repo)
        if latest is None:
            print(f"  ⚠️  {pkg}@{pinned} (in {skill}): could not check latest")
            unknown += 1
            continue

        if normalize_version(pinned) >= normalize_version(latest):
            print(f"  ✅ {pkg}@{pinned} (in {skill}): up to date (latest {latest})")
            up_to_date += 1
        else:
            print(f"  📦 {pkg}@{pinned} (in {skill}): behind latest {latest}")
            stale += 1

    print(f"\nResults: {up_to_date} up to date, {stale} behind, {unknown} unknown")
    # Non-blocking — always exit 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
