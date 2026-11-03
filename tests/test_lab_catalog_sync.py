"""Checks for deterministic project-card generation."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lab_catalog", ROOT / "scripts/sync_lab_catalog.py")
assert spec is not None and spec.loader is not None
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tools = catalog.load_tools()

    def test_unique_five_public_tools(self):
        self.assertEqual(len(self.tools), 5)
        self.assertEqual(len({x["slug"] for x in self.tools}), 5)

    def test_generated_sections_match_checked_in_files(self):
        renderers = {
            "index.html": catalog.homepage,
            "project/index.html": catalog.catalog_cards,
            "project/lab-automation/index.html": catalog.lab_cards,
        }
        for rel, render in renderers.items():
            with self.subTest(rel=rel):
                content = (ROOT / rel).read_text(encoding="utf-8")
                self.assertEqual(catalog.apply_region(content, render(self.tools), rel), content)

    def test_project_pages_are_in_sitemap(self):
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        for tool in self.tools:
            if tool["page"]:
                with self.subTest(page=tool["page"]):
                    self.assertTrue((ROOT / tool["page"].lstrip("/") / "index.html").is_file())
                    self.assertIn("https://maxstrix324.github.io" + tool["page"], sitemap)

    def test_profile_renderer_includes_repositories(self):
        rendered = catalog.profile(self.tools)
        for tool in self.tools:
            self.assertIn(tool["repository"], rendered)


if __name__ == "__main__":
    unittest.main()
