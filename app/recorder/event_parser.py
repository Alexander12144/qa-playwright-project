from pathlib import Path
from typing import List, Dict, Any

from app.storage.json_repository import JsonRepository


class EventParser:
    def __init__(self):
        self.repository = JsonRepository()

    def parse_file(self, actions_file: Path, output_file: Path):
        import json

        if not actions_file.exists():
            raise FileNotFoundError(
                f"No existe el archivo: {actions_file}"
            )

        with open(actions_file, "r", encoding="utf-8") as file:
            actions = json.load(file)

        qa_actions = self.parse(actions)

        self.repository.save(output_file, qa_actions)

        return qa_actions

    def parse(
        self,
        actions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        if not actions:
            return []

        result = []
        index = 0

        while index < len(actions):

            current = actions[index]
            action_type = current.get("action_type")

            # Agrupar escritura carácter por carácter
            if action_type == "input":
                grouped = self._group_inputs(actions, index)

                result.append(grouped["action"])

                index = grouped["next_index"]
                continue

            # Procesar cambios
            if action_type == "change":

                if self._is_redundant_change(actions, index):
                    index += 1
                    continue

                result.append(
                    self._convert_change(current)
                )

                index += 1
                continue

            # Procesar clicks
            if action_type == "click":

                result.append(
                    self._convert_click(current)
                )

                index += 1
                continue

            # Cualquier otro evento
            result.append(
                self._convert_generic(current)
            )

            index += 1

        return self._renumber(result)

    # ==========================================================
    # AGRUPAR INPUTS
    # ==========================================================

    def _group_inputs(self, actions, start_index):

        first = actions[start_index]
        last = first

        index = start_index + 1

        while index < len(actions):

            current = actions[index]

            if current.get("action_type") != "input":
                break

            if not self._same_element(first, current):
                break

            last = current
            index += 1

        element = first.get("element") or {}

        value = last.get("value")

        action = {
            "sequence": 0,
            "action_type": "input",
            "description": self._build_input_description(
                element,
                value
            ),
            "url": last.get("url"),
            "timestamp": first.get("timestamp"),
            "element": element,
            "value": value,
            "screenshot": last.get("screenshot")
        }

        return {
            "action": action,
            "next_index": index
        }

    # ==========================================================
    # CLICK
    # ==========================================================

    def _convert_click(self, action):

        element = action.get("element") or {}

        return {
            "sequence": 0,
            "action_type": "click",
            "description": self._build_click_description(
                element
            ),
            "url": action.get("url"),
            "timestamp": action.get("timestamp"),
            "element": element,
            "value": None,
            "screenshot": action.get("screenshot")
        }

    # ==========================================================
    # CHANGE
    # ==========================================================

    def _convert_change(self, action):

        element = action.get("element") or {}

        value = action.get("value")

        return {
            "sequence": 0,
            "action_type": "change",
            "description": (
                f"Modificar el valor del elemento "
                f"{self._element_label(element)}"
            ),
            "url": action.get("url"),
            "timestamp": action.get("timestamp"),
            "element": element,
            "value": value,
            "screenshot": action.get("screenshot")
        }

    # ==========================================================
    # GENERIC
    # ==========================================================

    def _convert_generic(self, action):

        return {
            "sequence": 0,
            "action_type": action.get(
                "action_type",
                "unknown"
            ),
            "description": (
                f"Ejecutar acción "
                f"{action.get('action_type', 'desconocida')}"
            ),
            "url": action.get("url"),
            "timestamp": action.get("timestamp"),
            "element": action.get("element"),
            "value": action.get("value"),
            "screenshot": action.get("screenshot")
        }

    # ==========================================================
    # DESCRIPCIÓN DE INPUT
    # ==========================================================

    def _build_input_description(self, element, value):

        label = self._element_label(element)

        if value == "[MASKED]":
            return f'Ingresar información en el campo "{label}"'

        return f'Ingresar "{value}" en el campo "{label}"'

    # ==========================================================
    # DESCRIPCIÓN DE CLICK
    # ==========================================================

    def _build_click_description(self, element):

        element_type = self._element_type(element)

        label = self._element_label(element)

        if element_type == "option":
            return f'Seleccionar la opción "{label}"'

        if element_type == "button":
            return f'Presionar el botón "{label}"'

        if element_type == "link":
            return f'Seleccionar el enlace "{label}"'

        if element_type == "checkbox":
            return f'Seleccionar la casilla "{label}"'

        if element_type == "radio":
            return f'Seleccionar la opción "{label}"'

        return f'Seleccionar "{label}"'

    # ==========================================================
    # IDENTIFICAR TIPO DE ELEMENTO
    # ==========================================================

    def _element_type(self, element):

        role = (element.get("role") or "").lower()
        tag = (element.get("tag") or "").lower()

        # Primero usamos el role porque es más semántico
        if role == "option":
            return "option"

        if role == "button":
            return "button"

        if role == "link":
            return "link"

        if role == "checkbox":
            return "checkbox"

        if role == "radio":
            return "radio"

        # Luego usamos el tag HTML
        if tag == "button":
            return "button"

        if tag == "a":
            return "link"

        if tag == "option":
            return "option"

        if tag == "input":
            input_type = (
                element.get("type") or ""
            ).lower()

            if input_type == "checkbox":
                return "checkbox"

            if input_type == "radio":
                return "radio"

        return "generic"

    # ==========================================================
    # NOMBRE FUNCIONAL DEL ELEMENTO
    # ==========================================================

    def _element_label(self, element):

        # 1. aria-label
        aria_label = element.get("aria_label")

        if aria_label:
            return self._clean_text(aria_label)

        # 2. texto visible
        text = element.get("text")

        if text:
            return self._clean_text(text)

        # 3. title
        title = element.get("title")

        if title:
            return self._clean_text(title)

        # 4. placeholder
        placeholder = element.get("placeholder")

        if placeholder:
            return self._clean_text(placeholder)

        # 5. name
        name = element.get("name")

        if name:
            return self._clean_text(name)

        # 6. id
        element_id = element.get("id")

        if element_id:
            return self._clean_text(element_id)

        # 7. tag
        tag = element.get("tag")

        if tag:
            return tag.upper()

        return "elemento"

    # ==========================================================
    # LIMPIAR TEXTO
    # ==========================================================

    def _clean_text(self, value):

        value = " ".join(str(value).split())

        return value[:100]

    # ==========================================================
    # COMPARAR ELEMENTOS
    # ==========================================================

    def _same_element(self, first, second):

        first_element = first.get("element") or {}
        second_element = second.get("element") or {}

        keys = [
            "tag",
            "role",
            "name",
            "id",
            "placeholder"
        ]

        for key in keys:

            if (
                first_element.get(key)
                != second_element.get(key)
            ):
                return False

        return True

    # ==========================================================
    # DETECTAR CHANGE REDUNDANTE
    # ==========================================================

    def _is_redundant_change(self, actions, index):

        if index == 0:
            return False

        previous = actions[index - 1]
        current = actions[index]

        if previous.get("action_type") != "input":
            return False

        if not self._same_element(
            previous,
            current
        ):
            return False

        if previous.get("value") != current.get("value"):
            return False

        return True

    # ==========================================================
    # RENOMBRAR SECUENCIAS
    # ==========================================================

    def _renumber(self, actions):

        for index, action in enumerate(
            actions,
            start=1
        ):
            action["sequence"] = index

        return actions