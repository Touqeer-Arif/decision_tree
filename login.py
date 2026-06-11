# login.py — Login Screen (Admin / Applicant / Employer)
# Job Portal Management System

import tkinter as tk
from tkinter import messagebox
from utils import (COLORS, FONTS, make_entry, make_button, make_frame,
                   make_label, center_window, apply_theme, show_error)
from database import execute_query, test_connection


class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Job Portal Management System — Login")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg"])
        apply_theme(self.root)
        center_window(self.root, 900, 580)

        self.role_var = tk.StringVar(value="Applicant")
        self._build_ui()
        self.root.mainloop()

    # ──────────────────────────────────────────
    def _build_ui(self):
        # Left decorative panel
        left = make_frame(self.root, bg=COLORS["sidebar"], width=380)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)
        self._build_left_panel(left)

        # Right login form
        right = make_frame(self.root, bg=COLORS["bg"])
        right.pack(side="right", fill="both", expand=True)
        self._build_right_panel(right)

    def _build_left_panel(self, parent):
        parent.pack_propagate(False)

        # Logo area
        top = make_frame(parent, bg=COLORS["sidebar"])
        top.pack(pady=(50, 10), padx=30, fill="x")

        tk.Label(top, text="💼", font=("Segoe UI Emoji", 48),
                 bg=COLORS["sidebar"], fg=COLORS["accent"]).pack()
        tk.Label(top, text="Job Portal", font=FONTS["logo"],
                 bg=COLORS["sidebar"], fg=COLORS["white"]).pack()
        tk.Label(top, text="Management System", font=("Segoe UI", 10),
                 bg=COLORS["sidebar"], fg=COLORS["text_sub"]).pack()

        # Divider
        tk.Frame(parent, bg=COLORS["border"], height=1).pack(fill="x", padx=30, pady=20)

        # Role selector
        tk.Label(parent, text="Select your role to login",
                 font=FONTS["small"], bg=COLORS["sidebar"],
                 fg=COLORS["text_sub"]).pack(pady=(0, 12))

        for role, icon in [("Admin", "🔐"), ("Employer", "🏢"), ("Applicant", "👤")]:
            self._role_btn(parent, role, icon)

        # Bottom credits
        tk.Label(parent, text="Database Systems Project",
                 font=("Segoe UI", 8), bg=COLORS["sidebar"],
                 fg=COLORS["text_sub"]).pack(side="bottom", pady=10)

    def _role_btn(self, parent, role, icon):
        f = tk.Frame(parent, bg=COLORS["sidebar"], cursor="hand2")
        f.pack(fill="x", padx=30, pady=4)

        def select():
            self.role_var.set(role)
            self._refresh_role_buttons()

        btn = tk.Frame(f, bg=COLORS["card"], pady=10, cursor="hand2")
        btn.pack(fill="x")
        btn.bind("<Button-1>", lambda e: select())

        tk.Label(btn, text=f"  {icon}  {role}", font=FONTS["sidebar"],
                 bg=COLORS["card"], fg=COLORS["text"],
                 anchor="w").pack(fill="x", padx=12)

        btn.bind("<Enter>", lambda e: btn.config(bg=COLORS["accent"]))
        btn.bind("<Leave>", lambda e: btn.config(
            bg=COLORS["accent"] if self.role_var.get() == role else COLORS["card"]))

        setattr(self, f"_rbtn_{role}", btn)
        setattr(self, f"_rlbl_{role}", btn.winfo_children()[0])

    def _refresh_role_buttons(self):
        for role in ["Admin", "Employer", "Applicant"]:
            btn = getattr(self, f"_rbtn_{role}", None)
            lbl = getattr(self, f"_rlbl_{role}", None)
            if btn and lbl:
                selected = self.role_var.get() == role
                bg = COLORS["accent"] if selected else COLORS["card"]
                btn.config(bg=bg)
                lbl.config(bg=bg)

    def _build_right_panel(self, parent):
        # Centered form container
        form = make_frame(parent, bg=COLORS["bg"])
        form.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(form, text="Welcome Back", font=FONTS["title"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(pady=(0, 4))
        tk.Label(form, text="Sign in to continue", font=FONTS["small"],
                 bg=COLORS["bg"], fg=COLORS["text_sub"]).pack(pady=(0, 30))

        # Username
        self._field(form, "Username")
        self.username_var = tk.StringVar()
        uf = make_frame(form, bg=COLORS["bg"])
        uf.pack(fill="x", pady=(0, 16))
        self.username_entry = make_entry(uf, width=34)
        self.username_entry.pack(fill="x", ipady=8, padx=2)

        # Password
        self._field(form, "Password")
        pf = make_frame(form, bg=COLORS["bg"])
        pf.pack(fill="x", pady=(0, 6))
        self.password_entry = make_entry(pf, show="•", width=34)
        self.password_entry.pack(fill="x", ipady=8, padx=2)

        # Show/hide password
        shf = make_frame(form, bg=COLORS["bg"])
        shf.pack(fill="x", pady=(0, 20))
        self.show_pw = tk.BooleanVar()
        tk.Checkbutton(shf, text=" Show password",
                       variable=self.show_pw,
                       command=self._toggle_pw,
                       bg=COLORS["bg"], fg=COLORS["text_sub"],
                       activebackground=COLORS["bg"],
                       activeforeground=COLORS["text"],
                       selectcolor=COLORS["card"],
                       font=FONTS["small"],
                       cursor="hand2").pack(anchor="w")

        # Login button
        login_btn = make_button(form, "Sign In →", self._do_login, width=30)
        login_btn.pack(fill="x", ipady=6)

        # Register link
        reg_frame = make_frame(form, bg=COLORS["bg"])
        reg_frame.pack(pady=(16, 0))
        tk.Label(reg_frame, text="New here? ", font=FONTS["small"],
                 bg=COLORS["bg"], fg=COLORS["text_sub"]).pack(side="left")
        reg_link = tk.Label(reg_frame, text="Create an Account",
                            font=("Segoe UI", 9, "underline"),
                            bg=COLORS["bg"], fg=COLORS["accent"],
                            cursor="hand2")
        reg_link.pack(side="left")
        reg_link.bind("<Button-1>", lambda e: self._open_register())

        # Enter key binding
        self.root.bind("<Return>", lambda e: self._do_login())

    def _field(self, parent, label):
        tk.Label(parent, text=label, font=FONTS["small"],
                 bg=COLORS["bg"], fg=COLORS["text_sub"]).pack(anchor="w", pady=(0, 4))

    def _toggle_pw(self):
        self.password_entry.config(show="" if self.show_pw.get() else "•")

    def _do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role     = self.role_var.get()

        if not username or not password:
            show_error("Validation", "Please enter username and password.")
            return

        user = self._authenticate(role, username, password)
        if user:
            self.root.withdraw()          # hide login window
            self._open_panel(role, user)
            self.root.destroy()           # destroy AFTER panel closes
        else:
            show_error("Login Failed", "Invalid username or password.")
            self.password_entry.delete(0, "end")

    def _authenticate(self, role: str, username: str, password: str):
        table_map = {"Admin": "admin", "Employer": "employer", "Applicant": "applicant"}
        table = table_map[role]
        row = execute_query(
            f"SELECT * FROM {table} WHERE username=%s AND password=%s",
            (username, password),
            fetch="one",
        )
        return row

    def _open_panel(self, role: str, user: dict):
        if role == "Admin":
            from admin import AdminPanel
            AdminPanel(user)
        elif role == "Employer":
            from employer import EmployerPanel
            EmployerPanel(user)
        else:
            from applicant import ApplicantPanel
            ApplicantPanel(user)

    def _open_register(self):
        role = self.role_var.get()
        if role == "Admin":
            show_error("Registration", "Admin accounts cannot be self-registered.")
            return
        from register import RegisterWindow
        RegisterWindow(role, on_close=lambda: None)


if __name__ == "__main__":
    if not test_connection():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Database Error",
            "Cannot connect to MySQL!\n\n"
            "Please:\n"
            "1. Start MySQL service\n"
            "2. Open database.py and set your username/password\n"
            "3. Run database/jobportal.sql in MySQL Workbench"
        )
        root.destroy()
    else:
        LoginWindow()
