import json
import re
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from app.config import AppPaths, DEFAULT_PATHS
from app.recorder.event_parser import EventParser
from app.reporting.test_case_report import TestCaseReportGenerator
from app.storage.json_repository import JsonRepository


class TestArtifactService:
    """Coordina la creación de artefactos de una ejecución."""

    def __init__(
        self,
        paths: AppPaths = DEFAULT_PATHS,
        log_callback: Optional[Callable[[str], None]] = None,
    ):
        self.paths = paths
        self.log_callback = log_callback
        self.repository = JsonRepository()

    def save_flow(
        self,
        execution_folder: Path,
        flow_name: str | None = None,
        report_folder: Path | None = None,
        report_name: str | None = None,
    ) -> Path | None:
        actions_file = execution_folder / "actions.json"
        actions = self._read_json(actions_file)

        if not actions:
            self._log("Flujo no guardado: no contiene acciones.")
            return None

        base_name = (flow_name or "flujo").strip() or "flujo"
        sanitized_name = re.sub(r"[^a-zA-Z0-9_\-]+", "_", base_name).strip("_") or "flujo"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        flow_file = self.paths.flows_dir / f"flow_{sanitized_name}_{timestamp}.json"
        flow_data = {
            "name": base_name,
            "start_url": actions[0].get("url"),
            "source_execution": str(execution_folder),
            "report_folder": report_folder.name if report_folder else None,
            "report_name": report_name,
            "actions": actions,
        }

        self.repository.save(flow_file, flow_data)
        self._log(f"Flujo reutilizable guardado: {flow_file}")
        return flow_file

    def generate_qa_actions(self, execution_folder: Path) -> tuple[Path, list[dict]]:
        actions_file = execution_folder / "actions.json"
        output_file = execution_folder / "qa_actions.json"
        self._log(f"Acciones técnicas: {actions_file.name}")
        self._log(f"Entrada existe: {actions_file.exists()}")

        qa_actions = EventParser().parse_file(actions_file, output_file)
        self._log(f"Acciones QA: {len(qa_actions)}")
        for action in qa_actions:
            self._log(f"{action['sequence']}. {action['description']}")
        self._log(f"Archivo generado: {output_file}")
        return output_file, qa_actions

    def generate_test_case(
        self,
        execution_folder: Path,
        qa_actions: list[dict],
        case_name: str | None = None,
        report_folder: Path | None = None,
        report_name: str = "CasosDePrueba.docx",
        matrix_case_key: str | None = None,
        matrix_case_id: str | None = None,
        expected_result: str | None = None,
        obtained_result: str | None = None,
        overwrite_matrix_case: bool = False,
    ) -> Path:
        start_url = qa_actions[0].get("url") if qa_actions else None
        report_file = TestCaseReportGenerator(
            report_folder=report_folder or self.paths.test_cases_dir
        ).generate_or_append(
            execution_folder,
            qa_actions,
            start_url=start_url,
            case_name=case_name,
            report_name=report_name,
            matrix_case_key=matrix_case_key,
            matrix_case_id=matrix_case_id,
            expected_result=expected_result,
            obtained_result=obtained_result,
            overwrite_matrix_case=overwrite_matrix_case,
        )
        self._log(f"Caso de prueba Word generado: {report_file}")
        return report_file

    @staticmethod
    def _read_json(filepath: Path) -> list[dict]:
        with filepath.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _log(self, message: str) -> None:
        if self.log_callback:
            self.log_callback(message)
