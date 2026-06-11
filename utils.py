# utils.py — Shared styles, helpers, and UI utilities
# Job Portal Management System

import tkinter as tk
from tkinter import ttk, messagebox
import re

# ──────────────────────────────────────────────
# THEME / COLOR PALETTE
# ──────────────────────────────────────────────
COLORS = {
    "bg":           "#0F1624",   # deep navy background
    "sidebar":      "#141E2E",   # sidebar panel
    "card":         "#1A2540",   # card / frame background
    "accent":       "#2563EB",   # primary blue accent
    "accent_hover": "#1D4ED8",   # hover state
    "accent2":      "#10B981",   # green for success / accept
    "danger":       "#EF4444",   # red for delete / reject
    "warning":      "#F59E0B",   # amber for pending
    "text":         "#F1F5F9",   # primary text (near white)
    "text_sub":     "#94A3B8",   # secondary / muted text
    "border":       "#2D3F5C",   # subtle borders
    "entry_bg":     "#0F1624",   # entry field background
    "header_bg":    "#1E3A5F",   # table header background
    "row_odd":      "#1A2540",
    "row_even":     "#162035",
    "white":        "#FFFFFF",
}

FONTS = {
    "title":    ("Segoe UI", 22, "bold"),
    "heading":  ("Segoe UI", 14, "bold"),
    "subhead":  ("Segoe UI", 11, "bold"),
    "body":     ("Segoe UI", 10),
    "small":    ("Segoe UI", 9),
    "btn":      ("Segoe UI", 10, "bold"),
    "sidebar":  ("Segoe UI", 11),
    "logo":     ("Segoe UI", 16, "bold"),
    "stat":     ("Segoe UI", 28, "bold"),
}


# ──────────────────────────────────────────────
# GLOBAL TTK STYLE SETUP
# ──────────────────────────────────────────────
def apply_theme(root: tk.Tk):
    """Apply the dark-blue theme to all ttk widgets."""
    style = ttk.Style(root)
    style.theme_use("clam")

    # Treeview
    style.configure("Treeview",
        background=COLORS["row_odd"],
        foreground=COLORS["text"],
        fieldbackground=COLORS["row_odd"],
        rowheight=30,
        font=FONTS["body"],
        borderwidth=0,
    )
    style.configure("Treeview.Heading",
        background=COLORS["header_bg"],
        foreground=COLORS["white"],
        font=FONTS["subhead"],
        relief="flat",
        padding=(8, 6),
    )
    style.map("Treeview",
        background=[("selected", COLORS["accent"])],
        foreground=[("selected", COLORS["white"])],
    )
    style.map("Treeview.Heading",
        background=[("active", COLORS["accent"])],
    )

    # Scrollbar
    style.configure("Vertical.TScrollbar",
        background=COLORS["card"],
        troughcolor=COLORS["bg"],
        arrowcolor=COLORS["text_sub"],
        borderwidth=0,
    )
    style.configure("Horizontal.TScrollbar",
        background=COLORS["card"],
        troughcolor=COLORS["bg"],
        arrowcolor=COLORS["text_sub"],
        borderwidth=0,
    )

    # Combobox
    style.configure("TCombobox",
        fieldbackground=COLORS["entry_bg"],
        background=COLORS["card"],
        foreground=COLORS["text"],
        arrowcolor=COLORS["text_sub"],
        insertcolor=COLORS["text"],
        selectbackground=COLORS["accent"],
        selectforeground=COLORS["white"],
    )
    style.map("TCombobox",
        fieldbackground=[("readonly", COLORS["entry_bg"])],
        foreground=[("readonly", COLORS["text"])],
    )

    root.option_add("*TCombobox*Listbox.background", COLORS["card"])
    root.option_add("*TCombobox*Listbox.foreground", COLORS["text"])
    root.option_add("*TCombobox*Listbox.selectBackground", COLORS["accent"])


# ──────────────────────────────────────────────
# REUSABLE WIDGET FACTORIES
# ──────────────────────────────────────────────
def make_label(parent, text, font=None, fg=None, bg=None, **kw):
    return tk.Label(parent,
        text=text,
        font=font or FONTS["body"],
        fg=fg or COLORS["text"],
        bg=bg or COLORS["bg"],
        **kw
    )


def make_entry(parent, show=None, width=30):
    e = tk.Entry(parent,
        bg=COLORS["entry_bg"],
        fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief="flat",
        font=FONTS["body"],
        bd=0,
        highlightthickness=1,
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["accent"],
        width=width,
    )
    if show:
        e.config(show=show)
    return e


def make_button(parent, text, command, bg=None, fg=None, width=None, **kw):
    btn = tk.Button(parent,
        text=text,
        command=command,
        bg=bg or COLORS["accent"],
        fg=fg or COLORS["white"],
        activebackground=COLORS["accent_hover"],
        activeforeground=COLORS["white"],
        font=FONTS["btn"],
        relief="flat",
        cursor="hand2",
        bd=0,
        padx=16,
        pady=8,
        **kw
    )
    if width:
        btn.config(width=width)
    # hover effect
    btn.bind("<Enter>", lambda e: btn.config(bg=COLORS["accent_hover"]))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg or COLORS["accent"]))
    return btn


def make_danger_button(parent, text, command, **kw):
    btn = tk.Button(parent,
        text=text, command=command,
        bg=COLORS["danger"], fg=COLORS["white"],
        activebackground="#DC2626", activeforeground=COLORS["white"],
        font=FONTS["btn"], relief="flat", cursor="hand2", bd=0,
        padx=16, pady=8, **kw
    )
    btn.bind("<Enter>", lambda e: btn.config(bg="#DC2626"))
    btn.bind("<Leave>", lambda e: btn.config(bg=COLORS["danger"]))
    return btn


def make_success_button(parent, text, command, **kw):
    btn = tk.Button(parent,
        text=text, command=command,
        bg=COLORS["accent2"], fg=COLORS["white"],
        activebackground="#059669", activeforeground=COLORS["white"],
        font=FONTS["btn"], relief="flat", cursor="hand2", bd=0,
        padx=16, pady=8, **kw
    )
    btn.bind("<Enter>", lambda e: btn.config(bg="#059669"))
    btn.bind("<Leave>", lambda e: btn.config(bg=COLORS["accent2"]))
    return btn


def make_text(parent, height=5, width=50):
    t = tk.Text(parent,
        bg=COLORS["entry_bg"],
        fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief="flat",
        font=FONTS["body"],
        height=height,
        width=width,
        highlightthickness=1,
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["accent"],
        wrap="word",
    )
    return t


def make_frame(parent, bg=None, **kw):
    return tk.Frame(parent, bg=bg or COLORS["bg"], **kw)


def make_card(parent, **kw):
    return tk.Frame(parent, bg=COLORS["card"], **kw)


def stat_card(parent, label, value, color=None):
    """A small stat box for dashboards."""
    card = tk.Frame(parent, bg=COLORS["card"], padx=20, pady=16,
                    highlightthickness=1, highlightbackground=COLORS["border"])
    tk.Label(card, text=str(value),
             font=FONTS["stat"], fg=color or COLORS["accent"],
             bg=COLORS["card"]).pack()
    tk.Label(card, text=label,
             font=FONTS["small"], fg=COLORS["text_sub"],
             bg=COLORS["card"]).pack()
    return card


def make_scrollable_table(parent, columns: list, col_widths: list = None):
    """Return (frame, treeview) with both scrollbars."""
    frame = tk.Frame(parent, bg=COLORS["bg"])

    tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
    vsb  = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
    hsb  = ttk.Scrollbar(frame, orient="horizontal",  command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    for i, col in enumerate(columns):
        w = (col_widths[i] if col_widths and i < len(col_widths) else 130)
        tree.heading(col, text=col.replace("_", " ").title())
        tree.column(col,  width=w, anchor="w", minwidth=60)

    tree.tag_configure("odd",  background=COLORS["row_odd"])
    tree.tag_configure("even", background=COLORS["row_even"])

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    return frame, tree


def populate_table(tree, rows: list, keys: list):
    """Clear tree then insert rows with alternating colors."""
    tree.delete(*tree.get_children())
    for i, row in enumerate(rows):
        values = [row.get(k, "") for k in keys]
        tag = "even" if i % 2 == 0 else "odd"
        tree.insert("", "end", values=values, tags=(tag,))


def center_window(win, w, h):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")


# ──────────────────────────────────────────────
# VALIDATION HELPERS
# ──────────────────────────────────────────────
def validate_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.\-]+@[\w\-]+\.\w{2,}$", email))


def validate_phone(phone: str) -> bool:
    return bool(re.match(r"^[\d\+\-\s]{7,15}$", phone))


def is_empty(value: str) -> bool:
    return not value.strip()


def show_error(title, msg):
    messagebox.showerror(title, msg)


def show_info(title, msg):
    messagebox.showinfo(title, msg)


def show_confirm(title, msg) -> bool:
    return messagebox.askyesno(title, msg)
