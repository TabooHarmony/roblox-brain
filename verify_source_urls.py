#!/usr/bin/env python3
"""Verify that all source URLs in skill frontmatter are reachable.

Extracts URLs from `sources:` frontmatter across all skills and HTTP HEADs
each one. Fails on 404 or unreachable URLs.

Usage:
    python3 verify_source_urls.py
    python3 verify_source_urls.py --verbose

Exit 0 = all URLs reachable, 1 = dead links found.
"""

import argparse
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS_DIR = ROOT / "skills"
TIMEOUT = 15


def extract_source_urls(content: str) -> list[str]:
    """Extract URLs from the sources: frontmatter field."""
    fm_match = re.match(r"^---\n(.+?)\n---", content, re.DOTALL)
    if not fm_match:
        return []
    fm_body = fm_match.group(1)
    urls = []
    for line in fm_body.split("\n"):
        line = line.strip()
        if line.startswith("- ") or line.startswith("  - "):
            url = line.lstrip("- ").strip()
            if url.startswith("http"):
                urls.append(url)
        elif line.startswith("sources:") and "http" in line:
            url = line.split("sources:", 1)[1].strip().strip("[]")
            if url.startswith("http"):
                urls.append(url)
    return urls


def source_url_policy_error(url: str) -> str | None:
    """Return a policy error for a reachable but disallowed source URL."""
    if "github.com/" in url and not url.startswith("https://raw.githubusercontent.com/"):
        return "GitHub source URLs must use raw.githubusercontent.com"
    return None


def check_url(url: str) -> tuple[str, str]:
    """HEAD request a URL, return (status, message)."""
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "roblox-brain-source-check"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            code = response.status
            if code == 200:
                return "pass", f"{code} OK"
            return "fail", f"HTTP {code}"
    except urllib.error.HTTPError as exc:
        if exc.code == 405:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "roblox-brain-source-check"})
                with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                    if response.status == 200:
                        return "pass", "200 OK (GET fallback)"
                    return "fail", f"HTTP {response.status}"
            except Exception as exc2:
                return "fail", f"GET fallback error: {exc2}"
        return "fail", f"HTTP {exc.code}"
    except Exception as exc:
        return "error", str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify source URLs in skill frontmatter")
    parser.add_argument("--verbose", action="store_true", help="show passing URLs too")
    args = parser.parse_args()

    all_urls = []
    for entry in sorted(os.listdir(SKILLS_DIR)):
        skill_dir = SKILLS_DIR / entry
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        with open(skill_md, encoding="utf-8") as f:
            content = f.read()
        urls = extract_source_urls(content)
        for url in urls:
            all_urls.append((entry, url))

    print(f"Checking {len(all_urls)} source URLs...\n")

    policy_errors = [(skill, url, source_url_policy_error(url)) for skill, url in all_urls]
    policy_errors = [(skill, url, error) for skill, url, error in policy_errors if error]
    for skill_name, url, message in policy_errors:
        print(f"  ❌ {skill_name}: {url}")
        print(f"     {message}")
    if policy_errors:
        print("❌ Source URL policy violations detected")
        return 1

    counts = {"pass": 0, "fail": 0, "error": 0}
    for skill_name, url in all_urls:
        status, message = check_url(url)
        counts[status] += 1
        if status != "pass" or args.verbose:
            icon = {"pass": "✅", "fail": "❌", "error": "⚠️"}[status]
            print(f"  {icon} {skill_name}: {url}")
            print(f"     {message}")

    print(f"\nResults: {counts['pass']} pass, {counts['fail']} dead, {counts['error']} error")
    if counts["fail"] or counts["error"]:
        print("❌ Dead or unreachable source URLs detected")
        return 1
    print("✅ All source URLs reachable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
