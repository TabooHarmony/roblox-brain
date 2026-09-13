#!/usr/bin/env python3
"""Mirror Roblox creator-docs engine reference YAML locally for offline drift checks.

The API drift checker (verify_api_drift.py) normally fetches each referenced
YAML from raw.githubusercontent.com per claim. This script downloads the
reference files the registry actually uses into .cache/creator-docs/ so the
checker can run with no network, and so you can diff versions over time.

Three distinct modes:

    python3 mirror_creator_docs.py            # fill gaps only; existing files stay untouched
    python3 mirror_creator_docs.py --all      # fill gaps across the full engine reference tree
    python3 mirror_creator_docs.py --refresh  # explicit re-download that REPLACES existing files
    python3 mirror_creator_docs.py --check    # presence check only (never fetches, never reports freshness)

Freshness contract for the retained cache:

- Every successful fetch records retrieval metadata in a sidecar next to the
  cached file (`<name>.yaml.meta.json`): the source URL, a retrieved-at
  timestamp, and the SHA-256 of the stored bytes. Presence alone never implies
  freshness; only the sidecar speaks to when a file was retrieved and from
  where.
- The default run is gap-filling, not a refresh. If a file exists it is left
  exactly as-is, so an intentional offline snapshot survives every re-run.
  Replacing a cached file requires the explicit --refresh flag.
- --refresh replaces an existing file only when the downloaded bytes hash
  differently from what is stored; the before and after hashes are recorded so
  a silent no-op or an unexpected overwrite is visible in the output.
- Downloads are written to a temp file and atomically renamed into place, so an
  interrupted fetch can never leave a truncated file that looks complete.

The mirror is a local cache, not a committed copy of the docs. It is gitignored by
default; commit it only if you want pinned offline CI.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = ROOT / "api_drift_registry.yaml"
MIRROR_DIR = ROOT / ".cache" / "creator-docs"
BASE_URL = "https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine"
# The tree API is the canonical list of engine reference files.
TREE_URL = "https://api.github.com/repos/Roblox/creator-docs/git/trees/main?recursive=1"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "roblox-brain-mirror"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def sidecar_path(dest: Path) -> Path:
    """Sidecar JSON path for a cached file; additive, never collides with the cache layout."""
    return dest.with_name(dest.name + ".meta.json")


def write_metadata(dest: Path, rel: str, data: bytes, note: str | None = None,
                    previous_sha256: str | None = None) -> dict:
    """Atomically write the retrieval sidecar for a cached file."""
    metadata = {
        "source_url": f"{BASE_URL}/{rel}",
        "retrieved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "content_sha256": sha256(data),
        "size": len(data),
    }
    if previous_sha256:
        metadata["previous_sha256"] = previous_sha256
    if note:
        metadata["note"] = note
    payload = json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    fd, tmp_name = tempfile.mkstemp(dir=str(dest.parent), prefix=dest.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.replace(tmp_name, sidecar_path(dest))
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise
    return metadata


def read_metadata(dest: Path) -> dict | None:
    """Return the sidecar metadata for a cached file, or None when absent or unreadable."""
    try:
        parsed = json.loads(sidecar_path(dest).read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError, OSError):
        return None
    return parsed if isinstance(parsed, dict) else None


def store_fetched(rel: str, dest: Path, data: bytes, verbose: bool,
                  replaced_from: str | None = None) -> None:
    """Write fetched bytes atomically (temp file, then rename) plus the sidecar.

    The rename guarantees an interrupted fetch never leaves a partial file at
    the cached path; a truncated download at worst leaves a stray .tmp file.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(dest.parent), prefix=dest.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp_name, dest)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise
    write_metadata(dest, rel, data,
                   note="replaced existing cached copy on --refresh" if replaced_from else None,
                   previous_sha256=replaced_from)
    if verbose:
        print(f"  ✓ {rel}")


def mirror_files(files: set[str], verbose: bool = False, refresh: bool = False) -> tuple[int, int]:
    """Fill the mirror. Returns (ok, failed).

    Default is gap-filling: an existing file is left untouched so an offline
    snapshot stays stable. refresh=True is the explicit opt-in to re-download
    and replace existing files, verified by hash before and after.
    """
    ok = failed = 0
    for rel in sorted(files):
        dest = MIRROR_DIR / rel
        url = f"{BASE_URL}/{rel}"
        if dest.exists() and not refresh:
            ok += 1
            continue
        try:
            data = fetch(url)
            if dest.exists():
                before = sha256(dest.read_bytes())
                after = sha256(data)
                if before == after:
                    # Content unchanged: keep the existing bytes untouched, but
                    # still (re)write the sidecar so the refresh stamps this
                    # retrieval with current snapshot identity and timestamp.
                    # Skipping metadata here left untracked files untracked.
                    write_metadata(dest, rel, data, note="refresh: content unchanged")
                    ok += 1
                    if verbose:
                        print(f"  = {rel} (unchanged, hash match)")
                    continue
                print(f"  ~ {rel}: replacing cached copy {before[:12]} with {after[:12]}")
            store_fetched(rel, dest, data, verbose=False, replaced_from=before if dest.exists() else None)
            if verbose:
                print(f"  ✓ {rel}")
            ok += 1
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  ✗ {rel}: {exc}")
    return ok, failed


def check_mode() -> int:
    """Presence check for registry-referenced files. Never fetches, never claims freshness."""
    files = registry_referenced_files()
    missing = [f for f in sorted(files) if not (MIRROR_DIR / f).exists()]
    untracked = [
        f for f in sorted(files)
        if (MIRROR_DIR / f).exists() and read_metadata(MIRROR_DIR / f) is None
    ]
    print("Check mode: presence (cache existence only; no retrieval-age claim, no network)")
    if missing:
        print(f"❌ Mirror missing {len(missing)} registry-referenced files:")
        for f in missing:
            print(f"   {f}")
        print("Run: python3 mirror_creator_docs.py")
        return 1
    print(f"✅ Mirror present for all {len(files)} registry-referenced files")
    if untracked:
        print(
            f"ℹ️ {len(untracked)} present file(s) predate retrieval metadata and carry no "
            "snapshot identity:"
        )
        for f in untracked:
            print(f"   {f}")
        print("Run: python3 mirror_creator_docs.py --refresh to record metadata for them")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Mirror creator-docs engine reference YAML")
    parser.add_argument("--all", action="store_true", help="mirror the full engine reference tree")
    parser.add_argument(
        "--refresh", action="store_true",
        help="explicit re-download: replace existing cached files (default run only fills gaps)",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="verify mirror presence without fetching (presence only, not freshness)",
    )
    args = parser.parse_args()

    if args.check:
        return check_mode()

    files = all_reference_files() if args.all else registry_referenced_files()
    if args.refresh:
        print(f"Explicit refresh: re-downloading {len(files)} files to {MIRROR_DIR}...")
    else:
        print(f"Mirroring {len(files)} files to {MIRROR_DIR} (gap-filling; existing files kept)...")
    ok, failed = mirror_files(files, verbose=not args.all, refresh=args.refresh)
    print(f"\nDone: {ok} ok, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
