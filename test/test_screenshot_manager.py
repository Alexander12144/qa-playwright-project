import unittest
from pathlib import Path

from app.recorder.browser_recorder import BrowserRecorder
from app.evidence.screenshot_manager import ScreenshotManager
from app.ui.main_window import MainWindow


class FakePage:
    def __init__(self):
        self.calls = []

    def screenshot(self, **kwargs):
        self.calls.append(kwargs)


class ScreenshotManagerTests(unittest.TestCase):
    def test_capture_uses_viewport_and_adds_url_bar(self):
        execution_folder = Path("test_output")
        manager = ScreenshotManager(execution_folder)
        page = FakePage()
        page.url = "https://example.test/checkout"

        result = manager.capture(page, 7)

        expected = str(Path("screenshots") / "E007.png")

        self.assertEqual(result, expected)
        self.assertEqual(len(page.calls), 1)
        self.assertFalse(page.calls[0]["full_page"])
        self.assertIn("E007.png", str(page.calls[0]["path"]))

    def test_should_skip_screenshot_for_input_events(self):
        self.assertFalse(BrowserRecorder.should_capture_screenshot("input"))
        self.assertTrue(BrowserRecorder.should_capture_screenshot("click"))

    def test_flow_display_name_uses_case_name_or_fallback(self):
        flow_path = Path("data/flows/flow_compra_20260919_163943.json")
        self.assertEqual(
            MainWindow.resolve_flow_display_name(flow_path, {"name": "Compra de prueba"}),
            "Compra de prueba",
        )
        self.assertEqual(
            MainWindow.resolve_flow_display_name(flow_path),
            "compra",
        )

    def test_report_names_are_safe_and_keep_docx_extension(self):
        self.assertEqual(MainWindow._safe_report_name("Plan: compra", ".docx"), "Plan_ compra.docx")
        self.assertIsNone(MainWindow._safe_report_name(" ../ "))


if __name__ == "__main__":
    unittest.main()
