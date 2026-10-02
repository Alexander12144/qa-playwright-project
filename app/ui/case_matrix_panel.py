from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Callable

from app.storage.case_matrix_repository import CaseMatrixRepository, MatrixCase
from app.ui.dialogs import show_error


class CaseMatrixPanel:
    """Owns the Excel matrix selection and its result fields."""

    def __init__(
        self,
        parent: tk.Misc,
        colors: dict[str, str],
        on_case_selected: Callable[[MatrixCase], None],
    ) -> None:
        self.parent = parent
        self.colors = colors
        self.on_case_selected = on_case_selected
        self.path: Path | None = None
        self.cases: list[MatrixCase] = []

        self.frame = tk.Frame(parent, bg=colors["panel"])
        header = tk.Frame(self.frame, bg=colors["panel"])
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="CASO DE LA MATRIZ",
            font=("Segoe UI", 9, "bold"),
            fg=colors["muted"],
            bg=colors["panel"],
        ).pack(side=tk.LEFT)
        tk.Button(
            header,
            text="QUITAR",
            command=self.unload,
            font=("Segoe UI", 8, "bold"),
            fg=colors["muted"],
            bg=colors["panel"],
            relief=tk.FLAT,
            cursor="hand2",
        ).pack(side=tk.RIGHT, padx=(0, 12))

        self.case_combo = ttk.Combobox(
            self.frame,
            font=("Segoe UI", 10),
            state="readonly",
            values=[],
        )
        self.case_combo.pack(fill=tk.X, pady=(6, 0))
        self.case_combo.bind("<<ComboboxSelected>>", self._on_case_selected)

        self.expected_result_text = self._add_result_field(
            "RESULTADO ESPERADO (MATRIZ)",
            read_only=True,
        )
        self.obtained_result_text = self._add_result_field("RESULTADO OBTENIDO")

        self.status_label = tk.Label(
            self.frame,
            text="Sin matriz cargada",
            font=("Segoe UI", 8),
            fg=colors["muted"],
            bg=colors["panel"],
        )
        self.status_label.pack(anchor=tk.W, pady=(4, 0))
        self.auto_advance_var = tk.BooleanVar(value=False)
        self.auto_advance_check = tk.Checkbutton(
            self.frame,
            text="Avanzar al siguiente caso de la matriz al finalizar",
            variable=self.auto_advance_var,
            font=("Segoe UI", 9),
            fg=colors["text"],
            bg=colors["panel"],
            activebackground=colors["panel"],
            selectcolor=colors["panel"],
            state=tk.DISABLED,
        )
        self.auto_advance_check.pack(anchor=tk.W, pady=(4, 0))

    def _add_result_field(self, label: str, read_only: bool = False) -> tk.Text:
        tk.Label(
            self.frame,
            text=label,
            font=("Segoe UI", 8, "bold"),
            fg=self.colors["muted"],
            bg=self.colors["panel"],
        ).pack(anchor=tk.W, pady=(8, 4))
        text = tk.Text(
            self.frame,
            height=3,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            fg=self.colors["text"],
            bg="#edf2ef" if read_only else self.colors["field"],
            relief=tk.FLAT,
        )
        text.pack(fill=tk.X)
        if read_only:
            text.configure(state=tk.DISABLED)
        return text

    def load(self, before_widget: tk.Widget | None = None, log_callback=None) -> None:
        selected_file = filedialog.askopenfilename(
            parent=self.parent.winfo_toplevel(),
            title="Seleccionar matriz de casos de prueba",
            filetypes=[("Archivos Excel", "*.xlsx")],
        )
        if not selected_file:
            return

        try:
            cases = CaseMatrixRepository.load_cases(Path(selected_file))
        except Exception as error:
            show_error(
                self.parent.winfo_toplevel(),
                "Error",
                f"No se pudo cargar la matriz Excel:\n{error}",
            )
            return

        self.path = Path(selected_file)
        self.cases = cases
        self.case_combo.configure(values=[case.name for case in cases])
        self.case_combo.current(0)
        self.frame.pack(
            fill=tk.X,
            padx=22,
            pady=(12, 0),
            before=before_widget,
        )
        self._on_case_selected()
        self.status_label.configure(
            text=f"{self.path.name}: {len(cases)} casos cargados"
        )
        self.auto_advance_check.configure(state=tk.NORMAL)
        if log_callback:
            log_callback(f"Matriz cargada: {self.path} ({len(cases)} casos).")

    def unload(self) -> None:
        self.frame.pack_forget()
        self.path = None
        self.cases = []
        self.case_combo.configure(values=[])
        self.case_combo.set("")
        self.status_label.configure(text="Sin matriz cargada")
        self.auto_advance_var.set(False)
        self.auto_advance_check.configure(state=tk.DISABLED)
        self.expected_result_text.configure(state=tk.NORMAL)
        self.expected_result_text.delete("1.0", tk.END)
        self.expected_result_text.configure(state=tk.DISABLED)
        self.obtained_result_text.delete("1.0", tk.END)

    def selected_case(self) -> MatrixCase | None:
        index = self.case_combo.current()
        if index < 0 or index >= len(self.cases):
            return None
        return self.cases[index]

    def obtained_result(self) -> str:
        return self.obtained_result_text.get("1.0", "end-1c").strip()

    def advance(self, log_callback=None) -> None:
        if not self.auto_advance_var.get():
            return

        current_index = self.case_combo.current()
        if current_index < 0 or current_index + 1 >= len(self.cases):
            self.auto_advance_var.set(False)
            if log_callback:
                log_callback("Se completaron los casos de la matriz cargada.")
            return

        self.case_combo.current(current_index + 1)
        self._on_case_selected()

    def _on_case_selected(self, _event=None) -> None:
        matrix_case = self.selected_case()
        if matrix_case is None:
            return

        self.expected_result_text.configure(state=tk.NORMAL)
        self.expected_result_text.delete("1.0", tk.END)
        self.expected_result_text.insert("1.0", matrix_case.expected_result)
        self.expected_result_text.configure(state=tk.DISABLED)
        self.obtained_result_text.delete("1.0", tk.END)
        self.obtained_result_text.insert("1.0", matrix_case.obtained_result)
        self.on_case_selected(matrix_case)