"""Regression checks for claims in non-generated project-page prose.

These checks supplement catalog-card synchronization. They do not certify
external hardware, Google Analytics operation or live website availability.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DocumentationContractsTests(unittest.TestCase):
    def read_page(self, rel):
        return (ROOT / rel / "index.html").read_text(encoding="utf-8")

    def test_lab_rigol_result_is_consistent_with_verified_20_channels(self):
        page = self.read_page("project/lab-automation")
        catalog = json.loads((ROOT / "data/lab-tools.json").read_text(encoding="utf-8"))
        rigol = next(tool for tool in catalog["tools"] if tool["slug"] == "rigol-oscilloscope-sorter")
        self.assertIn("20 каналов", rigol["description"])
        self.assertIn("20 каналов", page)
        self.assertIn("D0–D15", page)
        self.assertNotIn("не обещает выгрузку всех цифровых каналов", page)

    def test_stm32_page_describes_both_programming_backends(self):
        page = self.read_page("project/stm32-stlink-flasher")
        self.assertIn("OpenOCD", page)
        self.assertIn("STM32CubeProgrammer", page)
        self.assertIn("основной способ", page)
        self.assertNotIn(
            "Для работы прошивальщика используются Windows PowerShell и официальный STM32CubeProgrammer",
            page
        )

    def test_bom_page_documents_required_columns(self):
        page = self.read_page("project/kicad-bom-chipdip")
        for required in ("Reference", "Value"):
            self.assertIn(required, page)
        self.assertIn("Произвольный CSV без этих заголовков не поддерживается", page)

    def test_workbalance_gallery_uses_local_real_screenshots(self):
        page = self.read_page("project/workbalance")
        for shot in ("today-en.webp", "calendar-ru.webp", "forecast-ru.webp", "settings-en.webp"):
            with self.subTest(shot=shot):
                path = ROOT / "assets" / "projects" / "workbalance" / shot
                self.assertTrue(path.is_file(), f"Missing local screenshot {path}")
                self.assertIn("/assets/projects/workbalance/" + shot, page)
        self.assertIn('id="screenshots"', page)
        self.assertIn('loading="lazy"', page)

    def test_archived_early_projects_are_separate_from_active_projects(self):
        catalog = self.read_page("project")
        self.assertIn('id="early-projects"', catalog)
        self.assertIn("Не поддерживается", catalog)
        self.assertIn("Описание и экраны", catalog)
        self.assertIn('href="/project/workbalance/"', catalog)

    def test_mobile_navigation_is_visible(self):
        css = (ROOT / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".nav-links{display:flex;width:100%;", css)

    def test_site_pages_use_known_analytics_entrypoint(self):
        for route in (
            "project/lab-automation",
            "project/stm32-stlink-flasher",
            "project/kicad-bom-chipdip",
            "privacy"
        ):
            with self.subTest(route=route):
                self.assertIn('src="/assets/analytics.js"', self.read_page(route))


if __name__ == "__main__":
    unittest.main()
