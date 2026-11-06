"""Static regressions for portfolio positioning, project statuses and social cards."""
import importlib.util
import json
import re
import struct
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SOCIAL_ROOT = ROOT / "assets" / "social"
PREVIEWS = {
    "project": "projects",
    "project/workbalance": "workbalance",
    "project/lab-automation": "lab-tools",
    "project/kicad-bom-chipdip": "kicad-bom",
    "project/stm32-stlink-flasher": "stm32-flasher",
}


def page(route):
    return (ROOT / route / "index.html").read_text(encoding="utf-8")


class PortfolioPresentationTests(unittest.TestCase):
    def test_homepage_leads_with_engineering(self):
        homepage = page(".")
        self.assertIn("Инженер-схемотехник. Разрабатываю электронные устройства", homepage)
        self.assertIn('<a class="button primary" href="/project/">Инженерные проекты</a>', homepage)
        showcase = homepage.split('<div class="showcase-grid">', 1)[1].split(
            '\n        </div>\n      </div>\n    </section>', 1
        )[0]
        self.assertLess(showcase.index("LAB_TOOLS_GENERATED_START"),
                        showcase.index('href="/project/900-pyk/"'))
        self.assertLess(showcase.index('href="/project/900-pyk/"'),
                        showcase.index('href="/project/workbalance/"'))

    def test_project_catalog_labels_statuses_unambiguously(self):
        catalog = page("project")
        self.assertIn("Статус каждой работы", catalog)
        for status in (
            "Концепция · в проработке",
            "Опытный образец",
            "Исследование · опубликована статья",
            "В работе · переоборудование",
            "История · использовался в работе",
            "Не поддерживается",
        ):
            self.assertIn(status, catalog)

    def test_social_image_files_and_metadata(self):
        for route, slug in PREVIEWS.items():
            with self.subTest(route=route):
                html = page(route)
                image_path = SOCIAL_ROOT / (slug + ".png")
                self.assertTrue(image_path.is_file(), f"Missing {image_path}")
                raw = image_path.read_bytes()
                self.assertTrue(raw.startswith(b"\x89PNG\r\n\x1a\n"))
                self.assertEqual(raw[12:16], b"IHDR")
                self.assertEqual(struct.unpack(">II", raw[16:24]), (1200, 630))
                self.assertIn(
                    'property="og:image" content="https://maxstrix324.github.io/'
                    f'assets/social/{slug}.png"', html
                )
                self.assertIn('property="og:image:width" content="1200"', html)
                self.assertIn('property="og:image:height" content="630"', html)
                self.assertIn('name="twitter:card" content="summary_large_image"', html)

    def test_about_uses_real_portrait_for_preview(self):
        html = page("about")
        self.assertIn('property="og:image" content="https://maxstrix324.github.io/assets/portrait.jpg"', html)
        self.assertTrue((ROOT / "assets/portrait.jpg").is_file())

    def test_workbalance_existing_screenshots_retained(self):
        html = page("project/workbalance")
        for shot in ("today-en", "calendar-ru", "forecast-ru", "settings-en"):
            self.assertIn(f'/assets/projects/workbalance/{shot}.webp', html)
            self.assertTrue((ROOT / "assets/projects/workbalance" / (shot + ".webp")).is_file())

    def test_github_about_manifest(self):
        spec = importlib.util.spec_from_file_location(
            "sync_github_about", ROOT / "scripts" / "sync_github_about.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        records = module.load_records()
        self.assertEqual(len(records), 7)
        for record in records:
            with self.subTest(repo=record["repo"]):
                self.assertTrue(record["homepage"].startswith("https://maxstrix324.github.io/"))
                part = urlsplit(record["homepage"]).path.strip("/")
                self.assertTrue((ROOT / part / "index.html").is_file())
                self.assertEqual(len(record["topics"]), len(set(record["topics"])))
                self.assertFalse(module.mismatches(record, {
                    "description": record["description"],
                    "homepage": record["homepage"],
                    "topics": list(reversed(record["topics"])),
                }))
        self.assertIn("WorkBalance-Android", [r["repo"].split("/")[-1] for r in records])


if __name__ == "__main__":
    unittest.main()
