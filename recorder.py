"""Legacy recorder kept for backwards compatibility.

The application entry point uses ``app.recorder.browser_recorder.BrowserRecorder``.
New changes must be made in the ``app`` package instead of this module.
"""

from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import os


class QARecorder:

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.actions = []

        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.run_folder = os.path.join(
            "data",
            f"test_run_{self.run_id}"
        )

        self.screenshots_folder = os.path.join(
            self.run_folder,
            "screenshots"
        )

        os.makedirs(self.screenshots_folder, exist_ok=True)

    def start(self, url):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=False
        )

        self.page = self.browser.new_page()

        # Escuchamos los clics
        self.page.on(
            "click",
            lambda element: self.record_click(element)
        )

        # Escuchamos navegación
        self.page.on(
            "framenavigated",
            lambda frame: self.record_navigation(frame)
        )

        self.page.goto(url)

    def record_click(self, element):

        try:

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            tag = element.evaluate(
                "(el) => el.tagName"
            )

            text = element.inner_text(
                timeout=1000
            ).strip()

            action = {
                "type": "click",
                "timestamp": timestamp,
                "element": tag,
                "text": text
            }

            self.actions.append(action)

            print(
                f"[CLICK] {tag} - {text}"
            )

        except Exception:
            pass

    def record_navigation(self, frame):

        if frame == self.page.main_frame:

            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            action = {
                "type": "navigation",
                "timestamp": timestamp,
                "url": frame.url
            }

            self.actions.append(action)

            print(
                f"[NAVIGATION] {frame.url}"
            )

    def save(self):

        actions_file = os.path.join(
            self.run_folder,
            "actions.json"
        )

        with open(
            actions_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.actions,
                file,
                ensure_ascii=False,
                indent=4
            )

        print(
            f"Archivo generado: {actions_file}"
        )

    def stop(self):

        self.save()

        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()