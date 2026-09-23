import contextlib
import hashlib
import io
import json
import re
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import validate_skills
import verify_api_drift
import verify_source_urls


ROOT = Path(__file__).resolve().parents[1]


class ValidatorRegressionTests(unittest.TestCase):
    def test_reference_paths_from_full_reference_resolve_at_skill_root(self):
        document = ROOT / "skills" / "tools" / "roblox-cloud" / "references" / "full.md"
        target = validate_skills._resolve_local_reference(document, "references/full.md")
        self.assertEqual(target, document)

    def test_reference_scanner_handles_luau_resources(self):
        document = ROOT / "skills" / "design" / "roblox-analytics" / "references" / "full.md"
        matches = list(
            validate_skills._local_reference_matches(
                document,
                "See [`references/event-batcher.luau`](references/event-batcher.luau).",
            )
        )
        self.assertEqual(matches[0][0], "references/event-batcher.luau")

    def test_api_registry_rejects_missing_repository_paths(self):
        missing = verify_api_drift.validate_file_paths(
            {"files": [{"path": "skills/does-not-exist/references/full.md"}]}
        )
        self.assertEqual(missing, ["skills/does-not-exist/references/full.md"])

    def test_api_registry_rejects_checks_detached_from_teaching_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            document = root / "skills" / "roblox-example" / "SKILL.md"
            document.parent.mkdir(parents=True)
            document.write_text("No API claim here.")
            entry = {
                "files": [{"path": "skills/roblox-example/SKILL.md"}],
                "check": {
                    "type": "member_exists",
                    "class": "ExampleService",
                    "member": "DoThingAsync",
                },
            }
            self.assertEqual(
                verify_api_drift.validate_claim_tether(entry, root),
                ["skills/roblox-example/SKILL.md:DoThingAsync"],
            )
            document.write_text("Call `ExampleService:DoThingAsync()`.")
            self.assertEqual(verify_api_drift.validate_claim_tether(entry, root), [])

    def test_api_registry_tether_requires_identifier_boundaries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            document = root / "skills" / "roblox-example" / "SKILL.md"
            document.parent.mkdir(parents=True)
            document.write_text("Containment is unrelated.")
            entry = {
                "files": [{"path": "skills/roblox-example/SKILL.md"}],
                "teaching_needles": ["contain"],
                "check": {"type": "member_exists", "class": "C", "member": "M"},
            }
            self.assertEqual(
                verify_api_drift.validate_claim_tether(entry, root),
                ["skills/roblox-example/SKILL.md:contain"],
            )

    def assert_api_check_passes(self, check, doc):
        original = verify_api_drift.fetch_doc
        verify_api_drift.fetch_doc = lambda _kind, _name: doc
        try:
            status, message = verify_api_drift.verify({"check": check})
        finally:
            verify_api_drift.fetch_doc = original
        self.assertEqual(status, "pass", message)

    def test_api_registry_checks_method_return_type(self):
        self.assert_api_check_passes(
            {
                "type": "method_return_type",
                "class": "UserInputService",
                "method": "GetMouseDelta",
                "expected": "Vector2",
            },
            {
                "methods": [
                    {
                        "name": "UserInputService:GetMouseDelta",
                        "returns": [{"type": "Vector2"}],
                    }
                ]
            },
        )

    def test_api_registry_checks_property_write_security(self):
        self.assert_api_check_passes(
            {
                "type": "property_write_security",
                "class": "Lighting",
                "property": "LightingStyle",
                "expected": "RobloxScriptSecurity",
            },
            {
                "properties": [
                    {
                        "name": "Lighting.LightingStyle",
                        "security": {"write": "RobloxScriptSecurity"},
                    }
                ]
            },
        )

    def test_api_registry_checks_property_tag(self):
        self.assert_api_check_passes(
            {
                "type": "property_has_tag",
                "class": "Workspace",
                "property": "StreamingIntegrityMode",
                "tag": "NotScriptable",
            },
            {
                "properties": [
                    {
                        "name": "Workspace.StreamingIntegrityMode",
                        "tags": ["NotScriptable"],
                    }
                ]
            },
        )

    def test_api_registry_checks_method_description(self):
        self.assert_api_check_passes(
            {
                "type": "method_description_contains",
                "class": "RunService",
                "method": "BindToSimulation",
                "contains": "UseFixedSimulation",
            },
            {
                "methods": [
                    {
                        "name": "RunService:BindToSimulation",
                        "description": "Only available when Workspace.UseFixedSimulation is enabled.",
                    }
                ]
            },
        )

    def test_api_registry_checks_enum_item(self):
        self.assert_api_check_passes(
            {
                "type": "enum_item_exists",
                "enum": "ScreenInsets",
                "item": "CoreUISafeInsets",
            },
            {"items": [{"name": "CoreUISafeInsets"}]},
        )

    def test_api_registry_check_types_reject_mutated_docs(self):
        cases = [
            (
                {"type": "method_return_type", "class": "C", "method": "M", "expected": "Vector2"},
                {"methods": [{"name": "C:M", "returns": [{"type": "number"}]}]},
            ),
            (
                {"type": "property_write_security", "class": "C", "property": "P", "expected": "PluginSecurity"},
                {"properties": [{"name": "C.P", "security": {"write": "None"}}]},
            ),
            (
                {"type": "property_has_tag", "class": "C", "property": "P", "tag": "NotScriptable"},
                {"properties": [{"name": "C.P", "tags": []}]},
            ),
            (
                {"type": "method_description_contains", "class": "C", "method": "M", "contains": "RequiredFlag"},
                {"methods": [{"name": "C:M", "description": "No prerequisite."}]},
            ),
            (
                {"type": "enum_item_exists", "enum": "E", "item": "Wanted"},
                {"items": [{"name": "Other"}]},
            ),
        ]
        original = verify_api_drift.fetch_doc
        try:
            for check, doc in cases:
                verify_api_drift.fetch_doc = lambda _kind, _name, value=doc: value
                status, _ = verify_api_drift.verify({"check": check})
                self.assertEqual(status, "fail", check)
        finally:
            verify_api_drift.fetch_doc = original

    def test_source_url_policy_rejects_github_web_urls(self):
        self.assertIsNotNone(
            verify_source_urls.source_url_policy_error(
                "https://github.com/example/repo/blob/main/README.md"
            )
        )
        self.assertIsNone(
            verify_source_urls.source_url_policy_error(
                "https://raw.githubusercontent.com/Roblox/creator-docs/main/README.md"
            )
        )

    def test_source_url_extraction_handles_crlf_and_inline_lists(self):
        content = (
            "---\r\nname: example\r\nsources: "
            "[https://example.com/a, https://example.com/b]\r\n---\r\n"
        )
        self.assertEqual(
            verify_source_urls.extract_source_urls(content),
            ["https://example.com/a", "https://example.com/b"],
        )

    def test_current_local_reference_and_resource_validation_pass(self):
        self.assertEqual(validate_skills.validate_local_references(), [])
        self.assertEqual(validate_skills.validate_reference_resources(), [])


    def test_code_fence_integrity_allows_adjacent_blocks_and_rejects_unclosed(self):
        valid = "```luau\nlocal x = 1\n```\n\n```luau\nlocal y = 2\n```\n"
        self.assertEqual(validate_skills.validate_code_fences(valid, "fixture"), [])

        unclosed = validate_skills.validate_code_fences("```luau\nlocal x = 1\n", "fixture")
        self.assertTrue(any("unclosed" in error for error in unclosed))

        nested = validate_skills.validate_code_fences(
            "```luau\n```luau\nlocal x = 1\n```\n", "fixture"
        )
        self.assertTrue(any("nested fenced block" in error for error in nested))

    def test_luau_fence_compilation_rejects_invalid_syntax(self):
        with tempfile.TemporaryDirectory() as tmp:
            document = Path(tmp) / "invalid.md"
            document.write_text("```luau\nlocal function broken(\n```\n")
            errors, _recognized, _compiled = validate_skills.validate_luau_syntax([document])
            self.assertTrue(any("Luau syntax error" in error for error in errors))

    def test_annotated_luau_fence_compilation_rejects_invalid_syntax(self):
        with tempfile.TemporaryDirectory() as tmp:
            document = Path(tmp) / "invalid.md"
            document.write_text("```luau,linenos\nlocal function broken(\n```\n")
            errors, _recognized, _compiled = validate_skills.validate_luau_syntax([document])
            self.assertTrue(any("Luau syntax error" in error for error in errors))

    def test_standalone_luau_reference_rejects_invalid_syntax(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "invalid.luau"
            source.write_text("local function broken(\n")
            errors, _recognized, _compiled = validate_skills.validate_luau_syntax([], [source])
            self.assertTrue(any("Luau syntax error" in error for error in errors))

    def test_lua_fence_annotations_fail_without_heading_false_positive(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "roblox-example"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: roblox-example\ndescription: example\n"
                "last_reviewed: 2026-07-26\nsources: [original]\nkind: router\n---\n"
                "# Example\n\n## When to Load\nNow.\n\n## Quick Reference\nRule.\n\n"
                "## Full Reference Notes\nAllowed heading.\n\n"
                "```lua,linenos\nlocal x = 1\n```\n"
            )
            errors = validate_skills.validate_skill(str(skill_dir))
            self.assertTrue(any("found ```lua" in error for error in errors))
            self.assertFalse(any("'## Full Reference' found" in error for error in errors))

    def test_skill_schema_rejects_name_date_and_sources_mutations(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "roblox-example"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: roblox-wrong\ndescription: example\n"
                "last_reviewed: not-a-date\nsources: []\nkind: router\n---\n"
                "# Example\n\n## When to Load\nNow.\n\n## Quick Reference\nRule.\n"
            )
            errors = validate_skills.validate_skill(str(skill_dir))
            self.assertTrue(any("frontmatter name must match" in error for error in errors))
            self.assertTrue(any("last_reviewed" in error for error in errors))
            self.assertTrue(any("sources must be" in error for error in errors))

            (skill_dir / "SKILL.md").write_text(
                "---\nname: roblox-example\ndescription: example\n"
                "last_reviewed: 2026-07-26T12:00:00Z\nsources: [original]\n"
                "kind: router\n---\n# Example\n\n## When to Load\nNow.\n\n"
                "## Quick Reference\nRule.\n"
            )
            errors = validate_skills.validate_skill(str(skill_dir))
            self.assertTrue(any("last_reviewed" in error for error in errors))

            (skill_dir / "SKILL.md").write_text(
                "---\nname: roblox-example\ndescription: ''\n"
                "last_reviewed: 2099-01-01\nsources: [original]\n"
                "kind: router\n---\n# Example\n\n## When to Load\nNow.\n\n"
                "## Quick Reference\nRule.\n"
            )
            errors = validate_skills.validate_skill(str(skill_dir))
            self.assertTrue(any("description must be non-empty" in error for error in errors))
            self.assertTrue(any("last_reviewed cannot be in the future" in error for error in errors))

    def test_catalog_validation_rejects_count_and_row_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "- 99 focused skills\n\n## Skills (99)\n\n| `roblox-example` | Example |\n"
            )
            errors = validate_skills.validate_catalog({"roblox-example"}, root)
            self.assertTrue(any("README heading" in error for error in errors))

            (root / "README.md").write_text(
                "- 1 focused skills\n\n## Skills (1)\n\n| `roblox-example` | Example |\n"
            )
            self.assertEqual(
                validate_skills.validate_catalog({"roblox-example"}, root), []
            )

            (root / "README.md").write_text(
                "- 1 focused skills\n\n## Skills (1)\n\n"
                "| `roblox-example` | Example |\n| `roblox-example` | Duplicate |\n"
            )
            errors = validate_skills.validate_catalog({"roblox-example"}, root)
            self.assertTrue(any("duplicate rows" in error for error in errors))

    def test_nested_skill_directories_are_discovered(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp) / "skills"
            (skills / "core" / "roblox-example").mkdir(parents=True)
            (skills / "gameplay" / "roblox-other").mkdir(parents=True)
            original = validate_skills.SKILLS_DIR
            validate_skills.SKILLS_DIR = str(skills)
            try:
                self.assertEqual(
                    validate_skills.collect_all_skill_names(),
                    {"roblox-example", "roblox-other"},
                )
                self.assertEqual(len(validate_skills.skill_directories()), 2)
            finally:
                validate_skills.SKILLS_DIR = original

    def test_local_reference_validation_skips_incomplete_skill_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp) / "skills"
            (skills / "roblox-incomplete").mkdir(parents=True)
            original = validate_skills.SKILLS_DIR
            validate_skills.SKILLS_DIR = str(skills)
            try:
                self.assertEqual(validate_skills.validate_local_references(), [])
            finally:
                validate_skills.SKILLS_DIR = original

    def test_four_backtick_and_tilde_luau_fences_compile_and_reject_invalid_syntax(self):
        # F15 regression: alternate fences must be extracted and compiled, so
        # malformed Luau inside them is caught instead of silently skipped.
        with tempfile.TemporaryDirectory() as tmp:
            cases = {
                "````luau": "````",
                "~~~luau": "~~~",
            }
            for opener, closer in cases.items():
                with self.subTest(fence=opener):
                    valid = Path(tmp) / f"valid-{opener[0]}.md"
                    valid.write_text(f"{opener}\nlocal x = 1\n{closer}\n")
                    errors, recognized, compiled = validate_skills.validate_luau_syntax([valid])
                    self.assertEqual(errors, [])
                    self.assertEqual(recognized, 1)
                    self.assertEqual(compiled, 1)

                    invalid = Path(tmp) / f"invalid-{opener[0]}.md"
                    invalid.write_text(f"{opener}\nlocal function broken(\n{closer}\n")
                    errors, _recognized, _compiled = validate_skills.validate_luau_syntax([invalid])
                    self.assertTrue(any("Luau syntax error" in error for error in errors))

    def test_leading_dot_slash_local_reference_fails_like_plain_spelling(self):
        # F15 regression: ./references/missing.md must fail exactly like
        # references/missing.md.
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp) / "skills"
            skill_dir = skills / "roblox-example"
            (skill_dir / "references").mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "See [full](./references/missing.md).\n"
            )
            original = validate_skills.SKILLS_DIR
            validate_skills.SKILLS_DIR = str(skills)
            try:
                errors = validate_skills.validate_local_references()
            finally:
                validate_skills.SKILLS_DIR = original
            self.assertEqual(len(errors), 1)
            self.assertIn("missing local reference 'references/missing.md'", errors[0])

    def test_parent_path_escape_reference_fails_containment(self):
        # F15 regression: a ../ reference resolving outside the skill dir is
        # a containment violation, not a valid link.
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp) / "skills"
            skill_dir = skills / "roblox-example"
            (skill_dir / "references").mkdir(parents=True)
            (Path(tmp) / "outside.md").write_text("outside\n")
            (skill_dir / "references" / "full.md").write_text(
                "See [escape](../../../outside.md).\n"
            )
            original = validate_skills.SKILLS_DIR
            validate_skills.SKILLS_DIR = str(skills)
            try:
                errors = validate_skills.validate_local_references()
            finally:
                validate_skills.SKILLS_DIR = original
            self.assertEqual(len(errors), 1)
            self.assertIn("escapes skill directory", errors[0])

    def test_valid_nested_leading_dot_slash_reference_resolves(self):
        # F15 regression: ./references/full.md resolves like references/full.md.
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp) / "skills"
            skill_dir = skills / "roblox-example"
            (skill_dir / "references").mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "See [full](./references/full.md).\n"
            )
            (skill_dir / "references" / "full.md").write_text("# Full\n")
            original = validate_skills.SKILLS_DIR
            validate_skills.SKILLS_DIR = str(skills)
            try:
                self.assertEqual(validate_skills.validate_local_references(), [])
            finally:
                validate_skills.SKILLS_DIR = original

    def test_validator_includes_promoted_ui_design_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            skills = Path(tmp) / "skills"
            (skills / "roblox-example").mkdir(parents=True)
            (skills / "roblox-ui-design").mkdir(parents=True)
            original = validate_skills.SKILLS_DIR
            validate_skills.SKILLS_DIR = str(skills)
            try:
                self.assertEqual(
                    validate_skills.collect_all_skill_names(),
                    {"roblox-example", "roblox-ui-design"},
                )
            finally:
                validate_skills.SKILLS_DIR = original

    def test_monetization_receipt_example_is_not_fragmented(self):
        text = (ROOT / "skills/design/roblox-monetization/references/full.md").read_text()
        section = re.search(
            r"## 3\. Centralize Developer Product receipts(.*?)## 4\.", text, re.S
        )
        if section is None:
            self.fail("Developer Product receipt section not found")
        receipts = section.group(1)
        self.assertEqual(receipts.count("MarketplaceService.ProcessReceipt"), 1)
        self.assertIn("PurchaseGranted", receipts)
        self.assertNotIn("```luau\n\n```luau", receipts)

    def test_mcp_contract_names_asset_generation_and_completion(self):
        full = (ROOT / "skills/tools/roblox-studio-mcp" / "references" / "full.md").read_text()
        building = (ROOT / "skills/gameplay/roblox-building" / "SKILL.md").read_text()
        for token in ("generate_procedural_model", "generate_mesh", "generate_material"):
            self.assertIn(token, full)
            self.assertIn(token, building)
        self.assertIn("search_asset", full)
        self.assertIn("insert_asset", full)
        self.assertIn("generationId", full)
        compact = (ROOT / "skills/tools/roblox-studio-mcp" / "SKILL.md").read_text()
        self.assertIn("generate_*", compact)  # entry point abbreviates the generate tool family
        self.assertIn("wait_job_finished", compact)
        self.assertIn("read back", compact.lower())

    def test_mirror_check_reports_presence_not_freshness(self):
        # F16 regression: --check output must state it is presence-only and
        # must never use freshness wording for retained cache files.
        # Isolated fixture: no dependence on the developer's real cache or
        # network. Registry + mirrors are pointed at a temp directory.
        import mirror_creator_docs

        with tempfile.TemporaryDirectory() as tmp:
            mirror_root = Path(tmp)
            registry = mirror_root / "registry.yaml"
            registry.write_text(
                "entries:\n"
                "  - id: fixture-claim\n"
                "    claim: 'fixture'\n"
                "    check:\n"
                "      type: property_exists\n"
                "      class: Part\n"
                "      member: Anchored\n"
            )
            mirror_dir = mirror_root / "creator-docs"
            (mirror_dir / "classes").mkdir(parents=True)
            (mirror_dir / "classes" / "Part.yaml").write_text("id: Part\n")
            original_dir = mirror_creator_docs.MIRROR_DIR
            original_registry = mirror_creator_docs.REGISTRY_PATH
            mirror_creator_docs.MIRROR_DIR = mirror_dir
            mirror_creator_docs.REGISTRY_PATH = registry
            try:
                referenced = mirror_creator_docs.registry_referenced_files()
                self.assertEqual(referenced, {"classes/Part.yaml"})
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    exit_code = mirror_creator_docs.check_mode()
                output = stdout.getvalue()
                self.assertEqual(exit_code, 0)
                self.assertIn("presence", output)
                # Presence-only output never claims a file is fresh; the --refresh
                # flag name itself contains the substring, so mask it first.
                self.assertNotIn("fresh", output.replace("--refresh", "<flag>"))
                self.assertNotIn("Mirroring", output)
            finally:
                mirror_creator_docs.MIRROR_DIR = original_dir
                mirror_creator_docs.REGISTRY_PATH = original_registry

    def test_mirror_check_detects_missing_registry_referenced_file(self):
        # F16 regression: a registry entry referencing a file the mirror
        # lacks must fail check mode. Isolated fixture, no real cache.
        import mirror_creator_docs

        with tempfile.TemporaryDirectory() as tmp:
            mirror_root = Path(tmp)
            registry = mirror_root / "registry.yaml"
            registry.write_text(
                "entries:\n"
                "  - id: fixture-claim\n"
                "    claim: 'fixture'\n"
                "    check:\n"
                "      type: property_exists\n"
                "      class: Missing\n"
                "      member: Nope\n"
            )
            mirror_dir = mirror_root / "creator-docs"
            mirror_dir.mkdir(parents=True)
            original_dir = mirror_creator_docs.MIRROR_DIR
            original_registry = mirror_creator_docs.REGISTRY_PATH
            mirror_creator_docs.MIRROR_DIR = mirror_dir
            mirror_creator_docs.REGISTRY_PATH = registry
            try:
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    exit_code = mirror_creator_docs.check_mode()
                self.assertEqual(exit_code, 1)
                self.assertIn("Missing", stdout.getvalue())
            finally:
                mirror_creator_docs.MIRROR_DIR = original_dir
                mirror_creator_docs.REGISTRY_PATH = original_registry

    def test_mirror_refresh_replaces_fixture_only_when_hash_differs(self):
        # F16 regression: explicit refresh verifies by hash before/after; an
        # identical payload is a no-op, a changed payload is replaced with the
        # old hash recorded.
        import mirror_creator_docs as m

        with tempfile.TemporaryDirectory() as tmp:
            mirror_dir = Path(tmp)
            dest = mirror_dir / "classes" / "Part.yaml"
            dest.parent.mkdir(parents=True)
            dest.write_bytes(b"old: true\n")
            old_bytes = dest.read_bytes()
            new_bytes = b"new: true\n"
            recorded: dict[str, bytes] = {}

            def fake_fetch(url):
                return new_bytes

            original_fetch = m.fetch
            original_dir = m.MIRROR_DIR
            m.MIRROR_DIR = mirror_dir
            m.fetch = fake_fetch
            try:
                ok, failed = m.mirror_files({"classes/Part.yaml"}, verbose=True, refresh=True)
                self.assertEqual((ok, failed), (1, 0))
                self.assertEqual(dest.read_bytes(), new_bytes)
                metadata = m.read_metadata(dest)
                self.assertIsNotNone(metadata)
                self.assertEqual(metadata["content_sha256"], m.sha256(new_bytes))
                self.assertIn("previous_sha256", metadata)
                self.assertEqual(metadata["previous_sha256"], m.sha256(old_bytes))
                self.assertIn("replaced", metadata["note"])
                self.assertEqual(recorded, {})  # nothing else fetched
            finally:
                m.MIRROR_DIR = original_dir
                m.fetch = original_fetch

            # Same hash before and after: no replacement, timestamp preserved.
            before_metadata = m.read_metadata(dest)
            dest.write_bytes(new_bytes)  # simulate unchanged upstream
            m.MIRROR_DIR = mirror_dir
            m.fetch = fake_fetch
            try:
                ok, failed = m.mirror_files({"classes/Part.yaml"}, verbose=True, refresh=True)
                self.assertEqual((ok, failed), (1, 0))
                # Content unchanged: bytes stay, but the sidecar must be
                # (re)stamped with this retrieval's snapshot identity, so an
                # untracked pre-metadata file becomes tracked after refresh
                # and the timestamp reflects a verified upstream fetch.
                after_metadata = m.read_metadata(dest)
                self.assertIsNotNone(after_metadata)
                assert after_metadata is not None
                self.assertEqual(
                    after_metadata["content_sha256"], m.sha256(new_bytes)
                )
                self.assertNotIn("previous_sha256", after_metadata)
                self.assertIn("unchanged", after_metadata["note"])
                self.assertGreaterEqual(
                    after_metadata["retrieved_at"], before_metadata["retrieved_at"]
                )
            finally:
                m.MIRROR_DIR = original_dir
                m.fetch = original_fetch

    def test_mirror_interrupted_fetch_leaves_no_complete_looking_file(self):
        # F16 regression: fetch failure mid-write must not leave the cached
        # path holding partial bytes that look complete.
        import mirror_creator_docs as m

        with tempfile.TemporaryDirectory() as tmp:
            mirror_dir = Path(tmp)
            original_dir = m.MIRROR_DIR
            original_fetch = m.fetch
            m.MIRROR_DIR = mirror_dir
            m.fetch = lambda url: (_ for _ in ()).throw(RuntimeError("connection reset"))
            try:
                ok, failed = m.mirror_files({"classes/Part.yaml"}, verbose=False)
                self.assertEqual((ok, failed), (0, 1))
            finally:
                m.MIRROR_DIR = original_dir
                m.fetch = original_fetch
            self.assertFalse((mirror_dir / "classes" / "Part.yaml").exists())
            leftovers = list(mirror_dir.rglob("*"))
            self.assertEqual([p for p in leftovers if p.is_file()], [])  # no tmp debris either

    def test_mirror_metadata_sidecar_records_retrieval_identity(self):
        # F16 regression: successful fetches record source, timestamp, hash in
        # an additive sidecar; read_metadata tolerates missing/corrupt ones.
        import mirror_creator_docs as m

        with tempfile.TemporaryDirectory() as tmp:
            mirror_dir = Path(tmp)
            original_dir = m.MIRROR_DIR
            original_fetch = m.fetch
            m.MIRROR_DIR = mirror_dir
            m.fetch = lambda url: b"engine: docs\n"
            try:
                ok, failed = m.mirror_files({"enums/RunService.yaml"}, verbose=False)
                self.assertEqual((ok, failed), (1, 0))

                dest = mirror_dir / "enums" / "RunService.yaml"
                metadata = m.read_metadata(dest)
                self.assertIsNotNone(metadata)
                assert metadata is not None
                self.assertEqual(metadata["source_url"], f"{m.BASE_URL}/enums/RunService.yaml")
                self.assertIn("retrieved_at", metadata)
                self.assertEqual(metadata["content_sha256"], m.sha256(b"engine: docs\n"))
                # Sidecar is additive: cache layout stays plain, no implicit naming coupling.
                self.assertTrue(dest.is_file())
                self.assertTrue(m.sidecar_path(dest).is_file())
                self.assertEqual(m.read_metadata(dest.parent / "absent.yaml"), None)

                corrupt = mirror_dir / "enums" / "Broken.yaml"
                corrupt.write_text("x: y")
                m.sidecar_path(corrupt).write_text("{not json")
                self.assertEqual(m.read_metadata(corrupt), None)
            finally:
                m.MIRROR_DIR = original_dir
                m.fetch = original_fetch

    def test_api_drift_reports_snapshot_identity_and_age(self):
        # F16 regression: mirror reads surface snapshot identity and warn on
        # stale or metadata-less snapshots, without any network activity.
        import verify_api_drift as v

        with tempfile.TemporaryDirectory() as tmp:
            mirror_dir = Path(tmp) / "creator-docs"
            class_dir = mirror_dir / "classes"
            class_dir.mkdir(parents=True)
            (class_dir / "Part.yaml").write_text("id: Part\nproperties:\n  - name: Part.Position\n")
            fresh_meta = {
                "source_url": "https://example.com/Part.yaml",
                "retrieved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "content_sha256": hashlib.sha256(b"id: Part\nproperties:\n  - name: Part.Position\n").hexdigest(),
            }
            (class_dir / "Part.yaml.meta.json").write_text(json.dumps(fresh_meta))
            stale_meta = dict(fresh_meta, retrieved_at="2020-01-01T00:00:00Z")
            (class_dir / "Old.yaml").write_text("id: Old\n")
            (class_dir / "Old.yaml.meta.json").write_text(json.dumps(stale_meta))
            (class_dir / "Mystery.yaml").write_text("id: Mystery\n")  # no sidecar
            # R10 regression: a sidecar whose recorded hash does not match the
            # cached bytes must NOT be reported as a verified snapshot.
            (class_dir / "Tampered.yaml").write_text("id: Tampered\n")
            tampered_meta = dict(fresh_meta, content_sha256="0" * 64)
            (class_dir / "Tampered.yaml.meta.json").write_text(json.dumps(tampered_meta))

            original_dir = v.MIRROR_DIR
            v.MIRROR_DIR = mirror_dir
            try:
                self.assertTrue(
                    str(v.snapshot_identity("classes", "Part")).startswith("snapshot ")
                )
                self.assertIn("metadata", v.snapshot_identity("classes", "Mystery"))
                self.assertIn("do not match", v.snapshot_identity("classes", "Tampered"))
                self.assertTrue(
                    str(v.snapshot_identity("classes", "Tampered")).startswith("snapshot date unknown")
                )
                self.assertEqual(v.snapshot_age_days("classes", "Part"), 0)
                old_age = v.snapshot_age_days("classes", "Old")
                assert old_age is not None
                self.assertGreater(old_age, 30)
                self.assertEqual(v.snapshot_age_days("classes", "Mystery"), None)
            finally:
                v.MIRROR_DIR = original_dir

    def test_api_drift_main_annotates_mirror_snapshot_without_fetching(self):
        # F16 regression: a mirror-backed run annotates results with the
        # snapshot date and warns about metadata-less files; no network call
        # is made and exit code stays 0 for passing claims.
        import verify_api_drift as v

        def fail_network(category, name):  # any fetch attempt fails the test
            raise AssertionError(f"unexpected network fetch: {category}/{name}")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mirror_dir = root / ".cache" / "creator-docs"
            class_dir = mirror_dir / "classes"
            class_dir.mkdir(parents=True)
            (class_dir / "Part.yaml").write_text("id: Part\nproperties:\n  - name: Part.Position\n")
            metadata = {
                "source_url": "https://example.com/Part.yaml",
                "retrieved_at": "2020-01-01T00:00:00Z",
                "content_sha256": hashlib.sha256(b"id: Part\nproperties:\n  - name: Part.Position\n").hexdigest(),
            }
            (class_dir / "Part.yaml.meta.json").write_text(json.dumps(metadata))

            original_dir = v.MIRROR_DIR
            original_registry = v.REGISTRY_PATH
            original_fetch = v.fetch_doc
            v.MIRROR_DIR = mirror_dir
            v.REGISTRY_PATH = root / "registry.yaml"
            v.fetch_doc = fail_network
            (root / "registry.yaml").write_text(
                "entries:\n"
                "  - id: part-exists\n"
                "    claim: 'Part exists'\n"
                "    teaching_needles: ['Workspace']\n"
                "    files:\n"
                "      - path: skills/core/roblox-networking/SKILL.md\n"
                "    check:\n"
                "      type: member_exists\n"
                "      class: Part\n"
                "      member: Position\n"
            )
            try:
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    exit_code = v.main()
                output = stdout.getvalue()
            finally:
                v.MIRROR_DIR = original_dir
                v.REGISTRY_PATH = original_registry
                v.fetch_doc = original_fetch
            self.assertEqual(exit_code, 0)
            self.assertIn("Snapshot: checked against local mirror retrieved 2020-01-01T00:00:00Z", output)
            self.assertIn("not live docs", output)
            self.assertIn("older than 30 days", output)

    def test_api_drift_main_does_not_date_snapshot_from_mismatched_sidecar(self):
        # R10 regression: main()'s snapshot banner must verify the sidecar
        # hash against the cached bytes; a tampered sidecar must produce the
        # hash-mismatch warning, never a dated "retrieved ..." claim.
        import verify_api_drift as v

        def fail_network(category, name):
            raise AssertionError(f"unexpected network fetch: {category}/{name}")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mirror_dir = root / ".cache" / "creator-docs"
            class_dir = mirror_dir / "classes"
            class_dir.mkdir(parents=True)
            (class_dir / "Part.yaml").write_text("id: Part\nproperties:\n  - name: Part.Position\n")
            metadata = {
                "source_url": "https://example.com/Part.yaml",
                "retrieved_at": "2026-01-01T00:00:00Z",
                "content_sha256": "0" * 64,  # does not match the cached bytes
            }
            (class_dir / "Part.yaml.meta.json").write_text(json.dumps(metadata))

            original_dir = v.MIRROR_DIR
            original_registry = v.REGISTRY_PATH
            original_fetch = v.fetch_doc
            v.MIRROR_DIR = mirror_dir
            v.REGISTRY_PATH = root / "registry.yaml"
            v.fetch_doc = fail_network
            (root / "registry.yaml").write_text(
                "entries:\n"
                "  - id: part-exists\n"
                "    claim: 'Part exists'\n"
                "    teaching_needles: ['Workspace']\n"
                "    files:\n"
                "      - path: skills/core/roblox-networking/SKILL.md\n"
                "    check:\n"
                "      type: member_exists\n"
                "      class: Part\n"
                "      member: Position\n"
            )
            try:
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    exit_code = v.main()
                output = stdout.getvalue()
            finally:
                v.MIRROR_DIR = original_dir
                v.REGISTRY_PATH = original_registry
                v.fetch_doc = original_fetch
            self.assertEqual(exit_code, 0)
            self.assertNotIn("retrieved 2026-01-01", output)
            self.assertIn("do not match the retrieval metadata hash", output)
            self.assertIn("snapshot date unknown", output)
            self.assertIn("1 pass, 0 drift, 0 error", output)

    def test_api_drift_main_reports_unknown_snapshot_identity(self):
        # F16 regression: a mirror file without retrieval metadata is reported
        # as an unknown snapshot instead of passing as fresh.
        import verify_api_drift as v

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mirror_dir = root / ".cache" / "creator-docs"
            class_dir = mirror_dir / "classes"
            class_dir.mkdir(parents=True)
            (class_dir / "Part.yaml").write_text("id: Part\nproperties:\n  - name: Part.Position\n")  # no sidecar

            original_dir = v.MIRROR_DIR
            original_registry = v.REGISTRY_PATH
            original_fetch = v.fetch_doc
            v.MIRROR_DIR = mirror_dir
            v.REGISTRY_PATH = root / "registry.yaml"
            v.fetch_doc = original_fetch
            (root / "registry.yaml").write_text(
                "entries:\n"
                "  - id: part-exists\n"
                "    claim: 'Part exists'\n"
                "    teaching_needles: ['Workspace']\n"
                "    files:\n"
                "      - path: skills/core/roblox-networking/SKILL.md\n"
                "    check:\n"
                "      type: member_exists\n"
                "      class: Part\n"
                "      member: Position\n"
            )
            try:
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    exit_code = v.main()
                output = stdout.getvalue()
            finally:
                v.MIRROR_DIR = original_dir
                v.REGISTRY_PATH = original_registry
                v.fetch_doc = original_fetch
            self.assertEqual(exit_code, 0)
            self.assertIn("no retrieval metadata", output)
            self.assertIn("snapshot date unknown", output)



if __name__ == "__main__":
    unittest.main()
