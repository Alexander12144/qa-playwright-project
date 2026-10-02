import json
import tempfile
import unittest
from pathlib import Path

from app.config import AppPaths
from app.services.artifact_service import TestArtifactService


class ArtifactServiceTests(unittest.TestCase):
    def test_saved_flow_keeps_its_report_folder_and_document(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            paths = AppPaths(data_dir=Path(temporary_directory) / "data")
            paths.ensure_data_directories()
            execution_folder = paths.execution_dir("run_001")
            execution_folder.mkdir(parents=True)
            (execution_folder / "actions.json").write_text(
                json.dumps([{"url": "https://example.test"}]),
                encoding="utf-8",
            )
            report_folder = paths.test_cases_dir / "Regresion"

            flow_file = TestArtifactService(paths).save_flow(
                execution_folder,
                flow_name="Inicio de sesión",
                report_folder=report_folder,
                report_name="Casos.docx",
            )

            with flow_file.open("r", encoding="utf-8") as handle:
                flow = json.load(handle)

            self.assertEqual(flow["report_folder"], "Regresion")
            self.assertEqual(flow["report_name"], "Casos.docx")


if __name__ == "__main__":
    unittest.main()