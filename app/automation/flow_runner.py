import json
from pathlib import Path
from typing import Callable, Optional

from playwright.sync_api import Locator, sync_playwright


class FlowRunner:
    """Ejecuta un flujo técnico previamente grabado."""

    def __init__(
        self,
        log_callback: Optional[Callable[[str], None]] = None
    ):
        self.log_callback = log_callback

    def _log(self, message: str) -> None:
        if self.log_callback:
            self.log_callback(message)

    def run(self, flow_file: Path) -> None:
        with open(flow_file, "r", encoding="utf-8") as file:
            flow = json.load(file)

        start_url = flow.get("start_url")
        actions = flow.get("actions", [])

        if not start_url:
            raise ValueError("El flujo no tiene una URL inicial.")

        if not actions:
            raise ValueError("El flujo no contiene acciones.")

        self._log(f"Abriendo flujo: {flow_file}")

        playwright = sync_playwright().start()
        browser = None

        try:
            browser = playwright.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(start_url, wait_until="domcontentloaded")
            self._log(f"Página inicial: {start_url}")

            for index, action in enumerate(actions, start=1):
                self._run_action(page, action, index)

            self._log("Flujo ejecutado correctamente.")

        finally:
            if browser:
                browser.close()
            playwright.stop()
            self._log("Navegador del flujo cerrado.")

    def _run_action(self, page, action: dict, sequence: int) -> None:
        action_type = action.get("action_type")
        element = action.get("element") or {}
        value = action.get("value")
        locator = self._get_locator(page, element)

        if action_type == "click":
            locator.click(timeout=10000)

        elif action_type == "input":
            if value != "[MASKED]":
                locator.fill(value or "")

        elif action_type == "change":
            if element.get("tag", "").lower() == "select":
                locator.select_option(value or "")
            else:
                locator.fill(value or "")

        else:
            self._log(
                f"Paso {sequence} omitido: acción no soportada ({action_type})."
            )
            return

        description = action.get("description") or action_type
        self._log(f"Paso {sequence}: {description}")

    @staticmethod
    def _get_locator(page, element: dict) -> Locator:
        selector = element.get("selector")

        if selector:
            return page.locator(selector).first

        element_id = element.get("id")
        if element_id:
            return page.locator(f"#{element_id}").first

        name = element.get("name")
        if name:
            return page.locator(f"[name='{name}']").first

        text = element.get("text")
        if text:
            return page.get_by_text(text, exact=True).first

        raise ValueError("La acción no tiene un selector reproducible.")
