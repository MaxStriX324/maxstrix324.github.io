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
