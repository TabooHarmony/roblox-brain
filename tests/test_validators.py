import re
import tempfile
import unittest
from pathlib import Path

import validate_skills
import verify_api_drift
import verify_source_urls


ROOT = Path(__file__).resolve().parents[1]


class ValidatorRegressionTests(unittest.TestCase):
    def test_reference_paths_from_full_reference_resolve_at_skill_root(self):
        document = ROOT / "skills" / "roblox-cloud" / "references" / "full.md"
        target = validate_skills._resolve_local_reference(document, "references/full.md")
        self.assertEqual(target, document)

    def test_reference_scanner_handles_luau_resources(self):
        document = ROOT / "skills" / "roblox-analytics" / "references" / "full.md"
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
            errors = validate_skills.validate_luau_syntax([document])
            self.assertTrue(any("Luau syntax error" in error for error in errors))

    def test_annotated_luau_fence_compilation_rejects_invalid_syntax(self):
        with tempfile.TemporaryDirectory() as tmp:
            document = Path(tmp) / "invalid.md"
            document.write_text("```luau,linenos\nlocal function broken(\n```\n")
            errors = validate_skills.validate_luau_syntax([document])
            self.assertTrue(any("Luau syntax error" in error for error in errors))

    def test_standalone_luau_reference_rejects_invalid_syntax(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "invalid.luau"
            source.write_text("local function broken(\n")
            errors = validate_skills.validate_luau_syntax([], [source])
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
            (root / "AGENTS.md").write_text("99 curated skills\n")
            errors = validate_skills.validate_catalog({"roblox-example"}, root)
            self.assertGreaterEqual(len(errors), 3)

            (root / "README.md").write_text(
                "- 1 focused skills\n\n## Skills (1)\n\n| `roblox-example` | Example |\n"
            )
            (root / "AGENTS.md").write_text("1 curated skills\n")
            self.assertEqual(
                validate_skills.validate_catalog({"roblox-example"}, root), []
            )

            (root / "README.md").write_text(
                "- 1 focused skills\n\n## Skills (1)\n\n"
                "| `roblox-example` | Example |\n| `roblox-example` | Duplicate |\n"
            )
            errors = validate_skills.validate_catalog({"roblox-example"}, root)
            self.assertTrue(any("duplicate rows" in error for error in errors))

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
        text = (ROOT / "skills/roblox-monetization/references/full.md").read_text()
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
        compact = (ROOT / "skills/roblox-studio-mcp" / "SKILL.md").read_text()
        full = (ROOT / "skills/roblox-studio-mcp" / "references" / "full.md").read_text()
        building = (ROOT / "skills/roblox-building" / "SKILL.md").read_text()
        for token in ("generate_procedural_model", "generate_mesh", "generate_material"):
            self.assertIn(token, compact)
            self.assertIn(token, building)
        self.assertIn("search_asset", full)
        self.assertIn("insert_asset", full)
        self.assertIn("generationId", full)
        self.assertIn("read back", compact.lower())


if __name__ == "__main__":
    unittest.main()
