import tkinter as tk
from tkinter import messagebox, ttk


WINDOW_WIDTH = 460
WINDOW_HEIGHT = 440
BG_COLOR = "#f5f7fb"
PANEL_COLOR = "#ffffff"
TEXT_COLOR = "#111827"
MUTED_COLOR = "#6b7280"
ACCENT_COLOR = "#2563eb"
ACCENT_HOVER_COLOR = "#1d4ed8"


def center_window(root, width, height):
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    root.geometry(f"{width}x{height}+{x}+{y}")


def configure_styles(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    root.configure(bg=BG_COLOR)

    style.configure("App.TFrame", background=BG_COLOR)
    style.configure("Panel.TFrame", background=PANEL_COLOR)

    style.configure(
        "Title.TLabel",
        background=PANEL_COLOR,
        foreground=TEXT_COLOR,
        font=("Segoe UI", 18, "bold"),
    )
    style.configure(
        "Subtitle.TLabel",
        background=PANEL_COLOR,
        foreground=MUTED_COLOR,
        font=("Segoe UI", 10),
    )
    style.configure(
        "Field.TLabel",
        background=PANEL_COLOR,
        foreground=TEXT_COLOR,
        font=("Segoe UI", 10, "bold"),
    )
    style.configure(
        "Hint.TLabel",
        background=PANEL_COLOR,
        foreground=MUTED_COLOR,
        font=("Segoe UI", 9),
    )

    style.configure(
        "App.TEntry",
        fieldbackground="#f9fafb",
        foreground=TEXT_COLOR,
        bordercolor="#d1d5db",
        lightcolor=ACCENT_COLOR,
        darkcolor="#d1d5db",
        padding=(10, 8),
        font=("Segoe UI", 10),
    )

    style.configure(
        "Primary.TButton",
        background=ACCENT_COLOR,
        foreground="#ffffff",
        bordercolor=ACCENT_COLOR,
        focusthickness=0,
        font=("Segoe UI", 10, "bold"),
        padding=(18, 9),
    )
    style.map(
        "Primary.TButton",
        background=[("active", ACCENT_HOVER_COLOR), ("pressed", ACCENT_HOVER_COLOR)],
        bordercolor=[("active", ACCENT_HOVER_COLOR), ("pressed", ACCENT_HOVER_COLOR)],
    )

    style.configure(
        "Secondary.TButton",
        background="#eef2f7",
        foreground=TEXT_COLOR,
        bordercolor="#eef2f7",
        focusthickness=0,
        font=("Segoe UI", 10),
        padding=(18, 9),
    )
    style.map("Secondary.TButton", background=[("active", "#e5e7eb"), ("pressed", "#e5e7eb")])


def open_app_window(on_submit=None):
    """
    Open a small desktop window with inputs and a submit button.

    Args:
        on_submit: Optional callback that receives a dict of input values.

    Returns:
        dict | None: The submitted values, or None if the window is closed/cancelled.
    """
    result = {"data": None}

    root = tk.Tk()
    root.title("AutoVote")
    configure_styles(root)
    center_window(root, WINDOW_WIDTH, WINDOW_HEIGHT)
    root.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
    root.resizable(False, False)

    shell = ttk.Frame(root, style="App.TFrame", padding=22)
    shell.pack(fill="both", expand=True)

    container = ttk.Frame(shell, style="Panel.TFrame", padding=(24, 22, 24, 20))
    container.pack(fill="both", expand=True)
    container.columnconfigure(0, weight=1)

    ttk.Label(container, text="AutoVote", style="Title.TLabel").grid(row=0, column=0, sticky="w")
    ttk.Label(
        container,
        text="Choose a celebrity and number of votes to run.",
        style="Subtitle.TLabel",
    ).grid(row=1, column=0, sticky="w", pady=(4, 20))

    fields = [
        ("Celebrity Name", "celeb", "", False, "Example: Nguyen Van A"),
        ("Amount", "amount", "", False, "Enter a positive whole number"),
    ]

    entries = {}
    for index, (label, key, default_value, is_password, hint) in enumerate(fields):
        row = index * 3 + 2
        ttk.Label(container, text=label, style="Field.TLabel").grid(row=row, column=0, sticky="w")

        entry = ttk.Entry(container, width=42, show="*" if is_password else "", style="App.TEntry")
        entry.insert(0, default_value)
        entry.grid(row=row + 1, column=0, sticky="ew", pady=(6, 4))

        ttk.Label(container, text=hint, style="Hint.TLabel").grid(row=row + 2, column=0, sticky="w", pady=(0, 14))

        entries[key] = entry

    def submit():
        data = {key: entry.get().strip() for key, entry in entries.items()}

        if not data["celeb"]:
            messagebox.showerror("Invalid input", "Celebrity Name is required.")
            return
        
        if not data["amount"]:
            messagebox.showerror("Invalid input", "Amount is required.")
            return

        try:
            amount = int(data["amount"])
        except ValueError:
            messagebox.showerror("Invalid input", "Amount must be a whole number.")
            return

        if amount <= 0:
            messagebox.showerror("Invalid input", "Amount must be greater than 0.")
            return

        data["amount"] = amount

        result["data"] = data

        if on_submit:
            on_submit(data)

        root.destroy()

    def cancel():
        root.destroy()

    button_frame = ttk.Frame(container, style="Panel.TFrame")
    button_frame.grid(row=8, column=0, sticky="e", pady=(8, 0))

    ttk.Button(button_frame, text="Cancel", style="Secondary.TButton", command=cancel).grid(row=0, column=0, padx=(0, 8))
    ttk.Button(button_frame, text="Submit", style="Primary.TButton", command=submit).grid(row=0, column=1)

    root.bind("<Return>", lambda _event: submit())
    root.bind("<Escape>", lambda _event: cancel())
    entries["celeb"].focus()
    root.mainloop()

    return result["data"]


if __name__ == "__main__":
    values = open_app_window()
