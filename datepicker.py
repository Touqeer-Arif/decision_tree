# datepicker.py — Simple date picker popup for Job Portal
# Job Portal Management System

import tkinter as tk
from tkinter import ttk
from utils import COLORS, FONTS, make_button
import calendar
from datetime import date


class DatePicker:
    """
    A popup calendar widget.
    Usage:
        dp = DatePicker(parent, entry_widget)
        # When user picks a date, entry_widget is filled with YYYY-MM-DD
    """
    def __init__(self, parent, entry_widget):
        self.entry = entry_widget

        # Try to parse existing entry value
        try:
            existing = entry_widget.get().strip()
            parts = existing.split("-")
            if len(parts) == 3 and len(parts[0]) == 4:
                self.year  = int(parts[0])
                self.month = int(parts[1])
            else:
                today = date.today()
                self.year  = today.year
                self.month = today.month
        except Exception:
            today = date.today()
            self.year  = today.year
            self.month = today.month

        self.win = tk.Toplevel(parent)
        self.win.title("Pick a Date")
        self.win.configure(bg=COLORS["bg"])
        self.win.resizable(False, False)
        self.win.grab_set()

        # Position near the entry widget
        try:
            ex = entry_widget.winfo_rootx()
            ey = entry_widget.winfo_rooty() + entry_widget.winfo_height()
            self.win.geometry(f"280x300+{ex}+{ey}")
        except Exception:
            self.win.geometry("280x300")

        self._build()

    def _build(self):
        # Navigation bar
        nav = tk.Frame(self.win, bg=COLORS["card"], pady=8)
        nav.pack(fill="x")

        tk.Button(nav, text="◀", command=self._prev_month,
                  bg=COLORS["card"], fg=COLORS["text"],
                  activebackground=COLORS["accent"], relief="flat",
                  font=FONTS["body"], cursor="hand2", padx=10).pack(side="left")

        self.title_lbl = tk.Label(nav, text="", font=FONTS["subhead"],
                                  bg=COLORS["card"], fg=COLORS["white"])
        self.title_lbl.pack(side="left", expand=True)

        tk.Button(nav, text="▶", command=self._next_month,
                  bg=COLORS["card"], fg=COLORS["text"],
                  activebackground=COLORS["accent"], relief="flat",
                  font=FONTS["body"], cursor="hand2", padx=10).pack(side="right")

        # Day headers
        days_frame = tk.Frame(self.win, bg=COLORS["bg"])
        days_frame.pack(fill="x", padx=8, pady=(6, 0))
        for d in ["Mo","Tu","We","Th","Fr","Sa","Su"]:
            tk.Label(days_frame, text=d, width=3, font=FONTS["small"],
                     bg=COLORS["bg"], fg=COLORS["text_sub"]).pack(side="left", expand=True)

        # Calendar grid container
        self.grid_frame = tk.Frame(self.win, bg=COLORS["bg"])
        self.grid_frame.pack(fill="both", expand=True, padx=8, pady=4)

        # Year entry at bottom
        bot = tk.Frame(self.win, bg=COLORS["card"], pady=6)
        bot.pack(fill="x")
        tk.Label(bot, text="Year:", font=FONTS["small"],
                 bg=COLORS["card"], fg=COLORS["text_sub"]).pack(side="left", padx=(12,4))
        self.year_var = tk.StringVar(value=str(self.year))
        ye = tk.Entry(bot, textvariable=self.year_var, width=6,
                      bg=COLORS["entry_bg"], fg=COLORS["text"],
                      insertbackground=COLORS["text"], font=FONTS["body"],
                      relief="flat", highlightthickness=1,
                      highlightbackground=COLORS["border"])
        ye.pack(side="left")
        tk.Button(bot, text="Go", command=self._go_year,
                  bg=COLORS["accent"], fg=COLORS["white"],
                  relief="flat", font=FONTS["small"], cursor="hand2",
                  padx=8).pack(side="left", padx=6)

        self._render_month()

    def _render_month(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        self.title_lbl.config(
            text=f"{calendar.month_name[self.month]} {self.year}")

        weeks = calendar.monthcalendar(self.year, self.month)
        today = date.today()

        for week in weeks:
            row = tk.Frame(self.grid_frame, bg=COLORS["bg"])
            row.pack(fill="x", pady=1)
            for day in week:
                if day == 0:
                    tk.Label(row, text="", width=3, bg=COLORS["bg"]).pack(side="left", expand=True)
                else:
                    is_today = (day == today.day and
                                self.month == today.month and
                                self.year == today.year)
                    bg = COLORS["accent"] if is_today else COLORS["card"]
                    btn = tk.Button(row, text=str(day), width=3,
                                    bg=bg, fg=COLORS["white"],
                                    activebackground=COLORS["accent_hover"],
                                    activeforeground=COLORS["white"],
                                    relief="flat", font=FONTS["small"],
                                    cursor="hand2",
                                    command=lambda d=day: self._select(d))
                    btn.pack(side="left", expand=True, padx=1)

    def _prev_month(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self._render_month()

    def _next_month(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self._render_month()

    def _go_year(self):
        try:
            y = int(self.year_var.get())
            if 2000 <= y <= 2100:
                self.year = y
                self._render_month()
        except ValueError:
            pass

    def _select(self, day: int):
        chosen = f"{self.year:04d}-{self.month:02d}-{day:02d}"
        self.entry.delete(0, "end")
        self.entry.insert(0, chosen)
        self.win.destroy()
