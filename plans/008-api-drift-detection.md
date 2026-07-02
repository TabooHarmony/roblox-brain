# Plan 008: API Drift Detection System

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md`.
>
> **Drift check (run first)**: `git log --oneline -5 -- skills/`
> If skill files changed significantly since 2026-06-30, compare the
> API claims listed in the registry against the live content before
> proceeding — line numbers may have shifted.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: LOW
- **Depends on**: none (standalone)
- **Category**: maintenance

## Why this matters

The repo makes specific factual claims about Roblox engine APIs across 30+
skill files. These claims are correct at time of writing but silently rot as
Roblox ships updates. Example: `roblox-gui/references/full.md` stated
"UIStroke does NOT support Scale" which became false when Roblox shipped
UIStroke improvements (full release Dec 4, 2025) adding `StrokeSizingMode`.

There is no process to catch this. External readers found it, not us. This
plan builds a system to detect drift before it becomes wrong advice.

## Approach

Three artifacts:

1. **`api_drift_registry.yaml`** — a curated list of specific API claims the
   repo makes, each mapped to a machine-checkable fact in the official docs.
   Human-written, machine-read.

2. **`verify_api_drift.py`** — a script that fetches the corresponding YAML
   files from `Roblox/creator-docs` on GitHub and checks each claim against
   the current docs. Reports stale/wrong entries.

3. **Immediate fixes** — correct the UIStroke claims and any other drift the
   first verification pass surfaces.

The Roblox creator-docs repo (`github.com/Roblox/creator-docs`) stores engine
API reference as YAML files at predictable paths:
`content/en-us/reference/engine/classes/<ClassName>.yaml`
`content/en-us/reference/engine/enums/<EnumName>.yaml`
`content/en-us/reference/engine/datatypes/<TypeName>.yaml`

Each property has a `deprecation_message` field (empty string = not
deprecated). New properties appear as new entries in the `properties:` list.
This gives us two check types: `property_exists` and `deprecation_status`.

## Files you will create

- `api_drift_registry.yaml` (repo root)
- `verify_api_drift.py` (repo root)

## Files you will modify

- `skills/roblox-gui/references/full.md` (UIStroke fixes)
- `plans/README.md` (status row)
- `README.md` (add maintenance workflow section)

## Out of scope

- Do NOT touch any skill files other than the UIStroke fix in roblox-gui.
- Do NOT modify `validate_skills.py` (that's Plan 006's territory).
- Do NOT push or open a PR.

## Git workflow

- Branch: `advisor/008-api-drift-detection`
- Commits: one per step group (registry+script, fixes, docs)
- Do NOT push or open a PR unless the operator instructed it.

## Step 1: Create the drift registry

Create `api_drift_registry.yaml` at the repo root with this content:

```yaml
# API Drift Watch Registry
# Maps factual API claims in roblox-brain skills to verifiable facts
# in the Roblox creator-docs YAML files on GitHub.
#
# Run `python3 verify_api_drift.py` to check all entries.
# Add new entries when skills make new API claims that could drift.

entries:
  # --- UIStroke (was wrong: claimed no Scale support) ---
  - id: uistroke-sizing-mode
    claim: "UIStroke supports scale-based thickness via StrokeSizingMode"
    files:
      - path: skills/roblox-gui/references/full.md
        line: 27
    check:
      type: property_exists
      class: UIStroke
      property: StrokeSizingMode
    verified: 2026-06-30

  - id: uistroke-border-position
    claim: "UIStroke supports BorderStrokePosition enum"
    files:
      - path: skills/roblox-gui/references/full.md
        line: 252
    check:
      type: property_exists
      class: UIStroke
      property: BorderStrokePosition
    verified: 2026-06-30

  - id: uistroke-border-offset
    claim: "UIStroke supports BorderOffset property"
    files:
      - path: skills/roblox-gui/references/full.md
        line: 252
    check:
      type: property_exists
      class: UIStroke
      property: BorderOffset
    verified: 2026-06-30

  # --- CFrame (repo says deprecated — verify still true) ---
  - id: cframe-new-lookat-deprecated
    claim: "CFrame.new(pos, lookAt) is deprecated, use CFrame.lookAt"
    files:
      - path: skills/roblox-camera/references/full.md
        line: 102
      - path: skills/roblox-camera/references/full.md
        line: 401
    check:
      type: deprecation_status
      class: CFrame
      method: new
      overload: pos_lookAt
      expected: deprecated
    verified: 2026-06-30

  # --- Camera SetRoll/GetRoll (repo says outdated — verify) ---
  - id: camera-setroll-deprecated
    claim: "Camera.SetRoll is outdated/deprecated"
    files:
      - path: skills/roblox-camera/SKILL.md
        line: 51
      - path: skills/roblox-camera/references/full.md
        line: 60
    check:
      type: deprecation_status
      class: Camera
      method: SetRoll
      expected: deprecated
    verified: 2026-06-30

  - id: camera-getroll-deprecated
    claim: "Camera.GetRoll is outdated/deprecated"
    files:
      - path: skills/roblox-camera/references/full.md
        line: 59
    check:
      type: deprecation_status
      class: Camera
      method: GetRoll
      expected: deprecated
    verified: 2026-06-30

  # --- BodyVelocity (repo says deprecated — verify) ---
  - id: bodyvelocity-deprecated
    claim: "BodyVelocity is deprecated, use LinearVelocity"
    files:
      - path: skills/roblox-architecture/references/combat-systems.md
        line: 607
    check:
      type: deprecation_status
      class: BodyVelocity
      expected: deprecated
    verified: 2026-06-30

  # --- Font enum vs FontFace (soft drift — note for future) ---
  - id: enum-font-legacy
    claim: "Enum.Font is the legacy path; FontFace with Font datatype is modern"
    files:
      - path: skills/roblox-gui/references/full.md
        line: 175
    check:
      type: property_exists
      class: TextLabel
      property: FontFace
    verified: 2026-06-30
    note: "Enum.Font still works but can't access newer fonts. FontFace is preferred."
```

**Verify**:
```
cat api_drift_registry.yaml   → file exists with 9 entries
```

## Step 2: Create the verification script

Create `verify_api_drift.py` at the repo root:

```python
#!/usr/bin/env python3
"""
Verify API drift registry entries against live Roblox creator-docs YAML.

Fetches YAML files from raw.githubusercontent.com/Roblox/creator-docs
and checks each registry entry's claim against the current docs.

Usage:
    python3 verify_api_drift.py              # check all entries
    python3 verify_api_drift.py --verbose     # show passing checks too
    python3 verify_api_drift.py --update      # update verified dates on pass

Exit code 0 = all checks pass, 1 = drift or errors found.
"""

import argparse
import os
import re
import sys
import urllib.request
from datetime import date

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "api_drift_registry.yaml")
BASE_URL = "https://raw.githubusercontent.com/Roblox/creator-docs/main/content/en-us/reference/engine"

# Cache fetched YAML by URL to avoid refetching
_yaml_cache: dict[str, str] = {}


def fetch_yaml(category: str, name: str) -> str:
    """Fetch a YAML file from the Roblox creator-docs repo."""
    url = f"{BASE_URL}/{category}/{name}.yaml"
    if url in _yaml_cache:
        return _yaml_cache[url]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "roblox-brain-drift-checker"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read().decode("utf-8")
        _yaml_cache[url] = content
        return content
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} fetching {url}") from e
    except Exception as e:
        raise RuntimeError(f"Error fetching {url}: {e}") from e


def parse_registry(path: str) -> list[dict]:
    """Parse the YAML registry without external deps (simple parser)."""
    with open(path, encoding="utf-8") as f:
        content = f.read()

    entries = []
    current = None

    for line in content.split("\n"):
        stripped = line.strip()

        # New entry
        if stripped.startswith("- id:"):
            if current:
                entries.append(current)
            current = {"id": stripped.split(":", 1)[1].strip(), "files": [], "check": {}}

        elif current is None:
            continue

        # Parse fields
        if stripped.startswith("claim:"):
            current["claim"] = stripped.split(":", 1)[1].strip().strip('"').strip("'")
        elif stripped.startswith("type:"):
            current["check"]["type"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("class:"):
            current["check"]["class"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("property:"):
            current["check"]["property"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("method:"):
            current["check"]["method"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("overload:"):
            current["check"]["overload"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("expected:"):
            current["check"]["expected"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("verified:"):
            current["verified"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("note:"):
            current["note"] = stripped.split(":", 1)[1].strip().strip('"').strip("'")
        elif stripped.startswith("- path:"):
            current["files"].append({"path": stripped.split(":", 1)[1].strip()})

    if current:
        entries.append(current)

    return entries


def check_property_exists(yaml_text: str, class_name: str, property_name: str) -> tuple[bool, str]:
    """Check if a property exists in the class YAML."""
    # Properties are listed as "- name: ClassName.PropertyName"
    pattern = rf"name:\s*{re.escape(class_name)}\.{re.escape(property_name)}\b"
    if re.search(pattern, yaml_text):
        return True, f"Property {class_name}.{property_name} exists"
    return False, f"Property {class_name}.{property_name} NOT found in docs"


def check_deprecation_status(yaml_text: str, class_name: str, method_name: str = None) -> tuple[bool, str]:
    """Check if a class or method is deprecated.

    For classes: check top-level deprecation_message field.
    For methods: check the method's deprecation_message field.
    """
    if method_name:
        # Find the method section and check its deprecation_message
        # Methods are under "methods:" list with "name: ClassName.MethodName"
        pattern = rf"name:\s*{re.escape(class_name)}\.{re.escape(method_name)}\b"
        match = re.search(pattern, yaml_text)
        if not match:
            # Method might not exist (could mean removed/renamed)
            # Check if it appears anywhere
            if method_name in yaml_text:
                return True, f"{class_name}.{method_name} found but format unclear (likely deprecated or renamed)"
            return False, f"{class_name}.{method_name} NOT found in docs — may be removed"

        # Check for deprecation_message near the method entry
        # Look within ~500 chars after the method name match
        after = yaml_text[match.start():match.start() + 500]
        dep_match = re.search(r"deprecation_message:\s*['\"]?(.*?)['\"]?\s*$", after, re.MULTILINE)
        if dep_match:
            msg = dep_match.group(1).strip()
            if msg and msg != "''" and msg != '""':
                return True, f"{class_name}.{method_name} is deprecated: {msg}"
            return False, f"{class_name}.{method_name} is NOT deprecated"
        return False, f"{class_name}.{method_name} deprecation status unclear"

    else:
        # Class-level deprecation
        dep_match = re.search(r"^deprecation_message:\s*['\"]?(.*?)['\"]?\s*$", yaml_text, re.MULTILINE)
        if dep_match:
            msg = dep_match.group(1).strip()
            if msg and msg != "''" and msg != '""':
                return True, f"{class_name} is deprecated: {msg}"
            return False, f"{class_name} is NOT deprecated"
        return False, f"{class_name} deprecation status unclear"


def verify_entry(entry: dict) -> tuple[str, str]:
    """Verify a single registry entry. Returns (status, message).

    status: 'pass', 'fail', 'error'
    """
    check = entry.get("check", {})
    check_type = check.get("type")
    class_name = check.get("class", "")

    try:
        # Determine category (classes, enums, datatypes)
        # Try classes first, then datatypes, then enums
        yaml_text = None
        for category in ("classes", "datatypes", "enums"):
            try:
                yaml_text = fetch_yaml(category, class_name)
                break
            except RuntimeError:
                continue

        if yaml_text is None:
            return "error", f"Could not find {class_name} in any category"

        if check_type == "property_exists":
            exists, msg = check_property_exists(yaml_text, class_name, check["property"])
            if exists:
                return "pass", msg
            return "fail", msg

        elif check_type == "deprecation_status":
            expected_deprecated = check.get("expected") == "deprecated"
            is_deprecated, msg = check_deprecation_status(
                yaml_text, class_name, check.get("method")
            )
            if is_deprecated == expected_deprecated:
                return "pass", msg
            else:
                if expected_deprecated and not is_deprecated:
                    return "fail", f"Expected deprecated but {msg}"
                else:
                    return "fail", f"Expected NOT deprecated but {msg}"

        else:
            return "error", f"Unknown check type: {check_type}"

    except Exception as e:
        return "error", str(e)


def main():
    parser = argparse.ArgumentParser(description="Verify API drift registry")
    parser.add_argument("--verbose", action="store_true", help="Show passing checks")
    parser.add_argument("--update", action="store_true", help="Update verified dates on pass")
    args = parser.parse_args()

    if not os.path.exists(REGISTRY_PATH):
        print(f"Error: registry not found: {REGISTRY_PATH}")
        sys.exit(1)

    entries = parse_registry(REGISTRY_PATH)
    print(f"Checking {len(entries)} registry entries...\n")

    passes = 0
    fails = 0
    errors = 0

    for entry in entries:
        status, msg = verify_entry(entry)
        eid = entry["id"]

        if status == "pass":
            passes += 1
            if args.verbose:
                print(f"  ✅ {eid}: {msg}")
        elif status == "fail":
            fails += 1
            print(f"  ❌ {eid}: {msg}")
            print(f"     Claim: {entry.get('claim', '?')}")
            for f in entry.get("files", []):
                print(f"     File: {f['path']}")
        else:
            errors += 1
            print(f"  ⚠️  {eid}: {msg}")

    print(f"\nResults: {passes} pass, {fails} drift, {errors} error")

    if fails == 0 and errors == 0:
        print("✅ All API claims verified")
        sys.exit(0)
    else:
        print("❌ Drift or errors detected — review failed entries")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Verify**:
```
python3 verify_api_drift.py --verbose
```

Expected: fetches YAML from GitHub, checks each entry, reports results.
Some entries may fail if the YAML parsing needs adjustment — fix the
parsing logic, not the registry, unless the registry claim itself is wrong.

## Step 3: Fix the UIStroke claims in roblox-gui

In `skills/roblox-gui/references/full.md`, make these changes:

**Line 26-27** — replace:
```
- **Offset** = fixed pixels. Use for pixel-perfect icons, small graphics, UIStroke.
- **UIStroke** does NOT support Scale - only Offset.
```
with:
```
- **Offset** = fixed pixels. Use for pixel-perfect icons, small graphics.
- **UIStroke** supports both Offset (default, `StrokeSizingMode.FixedSize`) and Scale (`StrokeSizingMode.ScaledSize`, where Thickness acts as a fraction of the parent's shortest axis). Added Dec 2025.
<!-- verified: 2026-06-30 — source: create.roblox.com/docs/reference/engine/classes/UIStroke -->
```

**Line 35-36** — replace:
```
-- Offset for UIStroke (Scale not supported)
stroke.Thickness = 2  -- always Offset
```
with:
```
-- UIStroke thickness: Offset (default) or Scale
stroke.Thickness = 2                          -- FixedSize (pixels)
-- OR: stroke.StrokeSizingMode = Enum.StrokeSizingMode.ScaledSize
--     stroke.Thickness = 0.1                 -- 10% of parent's shortest axis
```

**Line 252-256** — update the stroke example to show new properties:
```
local stroke = Instance.new("UIStroke")
stroke.Color = Color3.fromRGB(255, 255, 255)
stroke.Thickness = 2
stroke.Transparency = 0.5
stroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
-- New properties (Dec 2025):
-- stroke.StrokeSizingMode = Enum.StrokeSizingMode.ScaledSize  -- scale with parent
-- stroke.BorderStrokePosition = Enum.BorderStrokePosition.Center  -- inner/center/outer
-- stroke.BorderOffset = UDim.new(0, 4)  -- additional offset
stroke.Parent = frame
```

**Line 608** — if it says "UICorner + UIStroke" as a tip, add:
```
  - UICorner + UIStroke (now supports scale, border position, multiple strokes per object)
```

**Verify**:
```
grep -n "UIStroke" skills/roblox-gui/references/full.md
```
Confirm no remaining instances of "does NOT support Scale".

## Step 4: Run the verification script and address findings

```
python3 verify_api_drift.py --verbose
```

For each `❌` (drift) or `⚠️` (error) result:

1. **Drift** — the repo's claim contradicts the current docs. Fix the skill
   file, then update the registry entry's `verified:` date.

2. **Error** — usually a fetch or parsing issue. Debug the script. If the
   YAML format has changed, update the parsing logic in `verify_api_drift.py`.

3. If a check passes but the claim is still soft-drift (like Enum.Font —
   works but legacy), that's fine. The registry tracks it; no action needed
   unless you want to modernize the code examples.

## Step 5: Add maintenance workflow to README

Add a section to `README.md` (at the end, before any contributing section):

```markdown
## API Drift Maintenance

The repo makes specific claims about Roblox engine APIs that can become
outdated as Roblox ships updates. To catch drift:

1. Run `python3 verify_api_drift.py` — checks all registry entries against
   live Roblox creator-docs YAML files on GitHub.

2. If drift is detected (`❌`), fix the skill file and update the registry
   entry's `verified:` date.

3. When adding new API claims to skills, add a corresponding entry to
   `api_drift_registry.yaml` so they get checked automatically.

The registry maps each claim to a `property_exists` or `deprecation_status`
check against the official docs YAML at
`github.com/Roblox/creator-docs`. Run the script before any release or
when preparing skills for external review.
```

**Verify**:
```
grep -n "API Drift" README.md   → section exists
```

## Step 6: Update plans/README.md

Add a row to the status table:

```
| 008  | API drift detection system | P1 | M | — | DONE |
```

## Done criteria

ALL must hold:

- [ ] `api_drift_registry.yaml` exists at repo root with 9+ entries
- [ ] `verify_api_drift.py` exists and runs without crashing
- [ ] `python3 verify_api_drift.py` exits 0 (all checks pass after fixes)
- [ ] UIStroke claims in `roblox-gui/references/full.md` are corrected
- [ ] No remaining "UIStroke does NOT support Scale" text in the repo
- [ ] `README.md` has an "API Drift Maintenance" section
- [ ] `plans/README.md` status row updated
- [ ] No files outside the listed scope are modified

## STOP conditions

Stop and report back (do not improvise) if:

- The Roblox creator-docs repo URL structure has changed (YAML files not at
  the expected paths). Report the actual structure and adjust the script
  accordingly — do NOT switch to HTML scraping.

- The YAML format has changed significantly (no `deprecation_message` field,
  different property listing format). Report what you find and adjust the
  parsing logic.

- The verification script finds drift in claims that were believed correct
  (e.g., CFrame.new(pos, lookAt) is no longer marked deprecated). Report
  the finding — do NOT silently fix. The operator should decide whether to
  update the claim or investigate further.

- Network access to `raw.githubusercontent.com` is unavailable. Report and
  stop — the script requires network access to function.

## Maintenance notes

- **When to run**: Before external review, before publishing, or quarterly.
  The script is safe to run anytime (read-only, no side effects).

- **Adding entries**: When a skill makes a new factual API claim (e.g., "X
  supports Y" or "X is deprecated"), add an entry to the registry. The
  entry needs: an ID, the claim text, the file(s) it appears in, and a
  check spec (type + class + property/method).

- **YAML source**: `github.com/Roblox/creator-docs` is the official repo.
  It's auto-generated from the engine. The YAML files may occasionally
  have formatting quirks — the parser uses simple regex, not a full YAML
  parser, to avoid dependency issues. If parsing breaks, fix the regex.

- **Limitations**: This system catches property additions/removals and
  deprecation changes. It does NOT catch semantic changes (e.g., default
  values changing, behavior modifications without API changes). Those
  require manual review of the skill content against docs.
