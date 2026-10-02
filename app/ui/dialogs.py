import tkinter as tk


COLORS = {
    "background": "#f2f5f3",
    "surface": "#ffffff",
    "text": "#203332",
    "muted": "#607370",
    "border": "#d8e2de",
    "accent": "#216b66",
    "accent_hover": "#185652",
    "warning": "#c47b36",
    "danger": "#b94d58",
}


class ThemedDialog:
    def __init__(
        self,
        parent: tk.Misc,
        title: str,
        message: str,
        kind: str,
        buttons: list[tuple[str, bool | None, bool]],
    ) -> None:
        self.result: bool | None = None
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.configure(bg=COLORS["background"])
        self.window.transient(parent)
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self._close)

        icon_color = COLORS["danger"] if kind == "error" else COLORS["warning"]
        if kind == "info":
            icon_color = COLORS["accent"]

        shell = tk.Frame(
            self.window,
            bg=COLORS["surface"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        shell.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        heading = tk.Frame(shell, bg=COLORS["surface"])
        heading.pack(fill=tk.X, padx=24, pady=(22, 10))
        tk.Label(
            heading,
            text={"warning": "!", "error": "!", "info": "i", "question": "?"}[kind],
            font=("Segoe UI", 13, "bold"),
            fg="white",
            bg=icon_color,
            width=2,
            height=1,
            padx=3,
            pady=3,
        ).pack(side=tk.LEFT, padx=(0, 12))
        tk.Label(
            heading,
            text=title,
            font=("Segoe UI", 14, "bold"),
            fg=COLORS["text"],
            bg=COLORS["surface"],
            anchor=tk.W,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            shell,
            text=message,
            font=("Segoe UI", 10),
            fg=COLORS["muted"],
            bg=COLORS["surface"],
            justify=tk.LEFT,
            anchor=tk.W,
            wraplength=440,
        ).pack(fill=tk.X, padx=24, pady=(0, 22))

        button_row = tk.Frame(shell, bg=COLORS["background"])
        button_row.pack(fill=tk.X, side=tk.BOTTOM)
        button_container = tk.Frame(button_row, bg=COLORS["background"])
        button_container.pack(side=tk.RIGHT, padx=20, pady=14)

        for label, result, primary in buttons:
            background = COLORS["accent"] if primary else COLORS["surface"]
            foreground = "white" if primary else COLORS["text"]
            button = tk.Button(
                button_container,
                text=label,
                command=lambda value=result: self._choose(value),
                font=("Segoe UI", 9, "bold"),
                fg=foreground,
                bg=background,
                activeforeground="white" if primary else COLORS["text"],
                activebackground=COLORS["accent_hover"] if primary else "#e9efec",
                relief=tk.FLAT,
                cursor="hand2",
                padx=16,
                pady=8,
                highlightthickness=1 if not primary else 0,
                highlightbackground=COLORS["border"],
            )
            button.pack(side=tk.LEFT, padx=(8, 0))
            if primary:
                button.focus_set()

        self.window.bind("<Escape>", lambda _event: self._close())
        self.window.bind("<Return>", lambda _event: self._default_button(buttons))
        self.window.update_idletasks()
        self._center(parent)

    def show(self) -> bool | None:
        self.window.grab_set()
        self.window.wait_window()
        return self.result

    def _default_button(self, buttons: list[tuple[str, bool | None, bool]]) -> None:
        primary = next((result for _label, result, is_primary in buttons if is_primary), None)
        self._choose(primary)

    def _choose(self, result: bool | None) -> None:
        self.result = result
        self.window.destroy()

    def _close(self) -> None:
        self.result = None
        self.window.destroy()

    def _center(self, parent: tk.Misc) -> None:
        self.window.update_idletasks()
        width = self.window.winfo_reqwidth()
        height = self.window.winfo_reqheight()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = max(parent.winfo_width(), width)
        parent_height = max(parent.winfo_height(), height)
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        self.window.geometry(f"+{max(0, x)}+{max(0, y)}")


def show_warning(parent: tk.Misc, title: str, message: str) -> None:
    ThemedDialog(parent, title, message, "warning", [("Entendido", True, True)]).show()


def show_error(parent: tk.Misc, title: str, message: str) -> None:
    ThemedDialog(parent, title, message, "error", [("Cerrar", True, True)]).show()


def show_info(parent: tk.Misc, title: str, message: str) -> None:
    ThemedDialog(parent, title, message, "info", [("Listo", True, True)]).show()


def ask_yes_no(parent: tk.Misc, title: str, message: str) -> bool:
    result = ThemedDialog(
        parent,
        title,
        message,
        "question",
        [("No", False, False), ("Sí", True, True)],
    ).show()
    return result is True


def ask_yes_no_cancel(parent: tk.Misc, title: str, message: str) -> bool | None:
    return ThemedDialog(
        parent,
        title,
        message,
        "question",
        [("Cancelar", None, False), ("No", False, False), ("Sí", True, True)],
    ).show()