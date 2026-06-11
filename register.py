# register.py — Registration window for Applicant and Employer
# Job Portal Management System

import tkinter as tk
from tkinter import ttk
from utils import (COLORS, FONTS, make_entry, make_button, make_frame,
                   make_label, make_text, center_window, show_error, show_info,
                   validate_email, validate_phone, is_empty)
from database import execute_query, execute_update


class RegisterWindow:
    def __init__(self, role: str, on_close=None):
        self.role = role
        self.on_close = on_close

        self.win = tk.Toplevel()
        self.win.title(f"Register as {role}")
        self.win.configure(bg=COLORS["bg"])
        self.win.resizable(False, False)
        center_window(self.win, 560, 680 if role == "Employer" else 640)
        self.win.grab_set()

        self._build_ui()
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        if self.on_close:
            self.on_close()
        self.win.destroy()

    def _build_ui(self):
        # Header
        hdr = make_frame(self.win, bg=COLORS["card"])
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"{'👤' if self.role == 'Applicant' else '🏢'}  Create {self.role} Account",
                 font=FONTS["heading"], bg=COLORS["card"], fg=COLORS["white"],
                 padx=24, pady=16).pack(anchor="w")

        # Scrollable body
        canvas = tk.Canvas(self.win, bg=COLORS["bg"], highlightthickness=0)
        vsb = ttk.Scrollbar(self.win, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        body = make_frame(canvas, bg=COLORS["bg"])
        cw = canvas.create_window((0, 0), window=body, anchor="nw")

        def on_resize(e):
            canvas.itemconfig(cw, width=e.width)
        canvas.bind("<Configure>", on_resize)
        body.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        self.fields = {}
        pad = {"padx": 30, "pady": 6}

        def add_field(label, key, show=None, widget="entry", options=None):
            make_label(body, label, font=FONTS["small"],
                       fg=COLORS["text_sub"], bg=COLORS["bg"]).pack(anchor="w", **pad)
            if widget == "entry":
                e = make_entry(body, show=show, width=48)
                e.pack(fill="x", padx=30, pady=(0, 4), ipady=7)
                self.fields[key] = e
            elif widget == "text":
                t = make_text(body, height=3, width=48)
                t.pack(fill="x", padx=30, pady=(0, 4))
                self.fields[key] = t
            elif widget == "combo":
                v = tk.StringVar(value=options[0])
                cb = ttk.Combobox(body, values=options, textvariable=v,
                                  state="readonly", width=46, font=FONTS["body"])
                cb.pack(fill="x", padx=30, pady=(0, 4), ipady=5)
                self.fields[key] = v

        # Common fields
        add_field("Full Name *", "full_name")
        add_field("Username *", "username")
        add_field("Email *", "email")
        add_field("Password *", "password", show="•")
        add_field("Confirm Password *", "confirm_password", show="•")
        add_field("Phone", "phone")
        add_field("Location / City", "location")

        if self.role == "Applicant":
            add_field("Skills (comma-separated)", "skills")
            add_field("Education (e.g. BSCS - UET Lahore)", "education")
            add_field("Years of Experience", "experience_years")

        elif self.role == "Employer":
            add_field("Company Name *", "company_name")
            add_field("Industry", "industry")
            add_field("Website", "website")
            add_field("Company Description", "description", widget="text")

        # Buttons
        btn_frame = make_frame(body, bg=COLORS["bg"])
        btn_frame.pack(pady=20, padx=30, fill="x")
        make_button(btn_frame, "Create Account", self._register).pack(side="left", ipady=6)
        make_button(btn_frame, "Cancel", self._on_close,
                    bg=COLORS["border"], fg=COLORS["text"]).pack(side="left", padx=12, ipady=6)

    def _get(self, key: str) -> str:
        w = self.fields.get(key)
        if w is None:
            return ""
        if isinstance(w, tk.StringVar):
            return w.get().strip()
        if isinstance(w, tk.Text):
            return w.get("1.0", "end").strip()
        return w.get().strip()

    def _register(self):
        # Collect
        full_name = self._get("full_name")
        username  = self._get("username")
        email     = self._get("email")
        password  = self._get("password")
        confirm   = self._get("confirm_password")
        phone     = self._get("phone")
        location  = self._get("location")

        # Validate
        if is_empty(full_name) or is_empty(username) or is_empty(email) or is_empty(password):
            show_error("Validation", "Please fill in all required fields (*).")
            return
        if not validate_email(email):
            show_error("Validation", "Invalid email address.")
            return
        if phone and not validate_phone(phone):
            show_error("Validation", "Invalid phone number.")
            return
        if password != confirm:
            show_error("Validation", "Passwords do not match.")
            return
        if len(password) < 6:
            show_error("Validation", "Password must be at least 6 characters.")
            return

        try:
            if self.role == "Applicant":
                skills    = self._get("skills")
                education = self._get("education")
                exp       = self._get("experience_years") or "0"
                try:
                    exp = int(exp)
                except ValueError:
                    exp = 0
                execute_update(
                    """INSERT INTO applicant
                       (username, password, email, full_name, phone, location,
                        skills, education, experience_years)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (username, password, email, full_name, phone, location,
                     skills, education, exp)
                )

            else:  # Employer
                company  = self._get("company_name")
                industry = self._get("industry")
                website  = self._get("website")
                desc     = self._get("description")
                if is_empty(company):
                    show_error("Validation", "Company name is required.")
                    return
                execute_update(
                    """INSERT INTO employer
                       (username, password, email, company_name, industry,
                        location, phone, website, description)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (username, password, email, company, industry,
                     location, phone, website, desc)
                )

            show_info("Success", f"{self.role} account created!\nYou can now log in.")
            self._on_close()

        except Exception as ex:
            err = str(ex)
            if "Duplicate entry" in err and "username" in err:
                show_error("Error", "Username already taken.")
            elif "Duplicate entry" in err and "email" in err:
                show_error("Error", "Email already registered.")
            else:
                show_error("Database Error", err)
