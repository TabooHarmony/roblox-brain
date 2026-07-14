import re
import tempfile
import unittest
from pathlib import Path

import generate_index
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

    def test_source_url_policy_rejects_github_web_urls(self):
        self.assertIsNotNone(
            verify_source_urls.source_url_policy_error(
                "https://github.com/example/repo/blob/main/README.md"
            )
        )
        self.assertIsNone(
            verify_source_urls.source_url_policy_error(
                "https://raw.githubusercontent.com/example/repo/main/README.md"
            )
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

    def test_index_generator_includes_promoted_ui_design_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / "skills"
            for name in ("roblox-example", "roblox-ui-design"):
                skill_dir = skills / name
                skill_dir.mkdir(parents=True)
                (skill_dir / "SKILL.md").write_text(
                    "---\nname: %s\ndescription: example\n---\n" % name
                )

            original = (generate_index.SKILLS_DIR, generate_index.INDEX_PATH)
            generate_index.SKILLS_DIR = skills
            generate_index.INDEX_PATH = root / "skill_index.md"
            try:
                self.assertEqual(generate_index.main(), 0)
            finally:
                generate_index.SKILLS_DIR, generate_index.INDEX_PATH = original

            index = (root / "skill_index.md").read_text()
            self.assertIn("roblox-example", index)
            self.assertIn("roblox-ui-design", index)

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
