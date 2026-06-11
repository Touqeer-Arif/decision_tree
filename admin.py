# admin.py — Admin Panel
# Job Portal Management System

import tkinter as tk
from tkinter import ttk, messagebox
from utils import (COLORS, FONTS, make_frame, make_button, make_danger_button,
                   make_success_button, make_entry, make_label, stat_card,
                   make_scrollable_table, populate_table, center_window,
                   apply_theme, show_error, show_info, show_confirm)
from database import execute_query, execute_update


MENU = [
    ("📊", "Dashboard"),
    ("👥", "Applicants"),
    ("🏢", "Employers"),
    ("💼", "Jobs"),
    ("📋", "Applications"),
    ("📈", "Reports"),
]


class AdminPanel:
    def __init__(self, user: dict):
        self.user = user
        self.active_section = tk.StringVar(value="Dashboard")

        self.root = tk.Tk()
        self.root.title("Admin Panel — Job Portal")
        self.root.configure(bg=COLORS["bg"])
        apply_theme(self.root)
        center_window(self.root, 1200, 720)
        self.root.resizable(True, True)

        self._build_layout()
        self._show_section("Dashboard")
        self.root.mainloop()

    # ──────────────────────────────────────────
    # LAYOUT
    # ──────────────────────────────────────────
    def _build_layout(self):
        # Sidebar
        self.sidebar = make_frame(self.root, bg=COLORS["sidebar"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # Main area
        self.main = make_frame(self.root, bg=COLORS["bg"])
        self.main.pack(side="right", fill="both", expand=True)
        self._build_topbar()

        self.content = make_frame(self.main, bg=COLORS["bg"])
        self.content.pack(fill="both", expand=True, padx=24, pady=16)

    def _build_sidebar(self):
        # Logo
        logo = make_frame(self.sidebar, bg=COLORS["accent"])
        logo.pack(fill="x")
        tk.Label(logo, text="💼 Job Portal", font=FONTS["logo"],
                 bg=COLORS["accent"], fg=COLORS["white"],
                 pady=16, padx=16, anchor="w").pack(fill="x")

        tk.Label(self.sidebar, text="ADMIN MENU", font=("Segoe UI", 8, "bold"),
                 bg=COLORS["sidebar"], fg=COLORS["text_sub"],
                 padx=16, pady=12, anchor="w").pack(fill="x")

        self._menu_buttons = {}
        for icon, label in MENU:
            btn = tk.Button(self.sidebar,
                text=f"  {icon}  {label}",
                font=FONTS["sidebar"],
                bg=COLORS["sidebar"], fg=COLORS["text"],
                activebackground=COLORS["accent"],
                activeforeground=COLORS["white"],
                relief="flat", anchor="w", padx=8, pady=10,
                cursor="hand2",
                command=lambda l=label: self._show_section(l)
            )
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORS["accent"]))
            btn.bind("<Leave>", lambda e, b=btn, l=label: b.config(
                bg=COLORS["accent"] if self.active_section.get() == l else COLORS["sidebar"]))
            self._menu_buttons[label] = btn

        # Logout
        tk.Frame(self.sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=16, pady=10)
        logout_btn = tk.Button(self.sidebar, text="  🚪  Logout",
            font=FONTS["sidebar"], bg=COLORS["sidebar"], fg=COLORS["danger"],
            activebackground=COLORS["danger"], activeforeground=COLORS["white"],
            relief="flat", anchor="w", padx=8, pady=10, cursor="hand2",
            command=self._logout)
        logout_btn.pack(fill="x")

    def _build_topbar(self):
        bar = make_frame(self.main, bg=COLORS["card"])
        bar.pack(fill="x")
        self.page_title = tk.Label(bar, text="Dashboard",
            font=FONTS["heading"], bg=COLORS["card"],
            fg=COLORS["white"], padx=24, pady=14, anchor="w")
        self.page_title.pack(side="left")
        tk.Label(bar, text=f"👤 {self.user['full_name']}",
            font=FONTS["small"], bg=COLORS["card"],
            fg=COLORS["text_sub"], padx=24, pady=14).pack(side="right")

    # ──────────────────────────────────────────
    # SECTION ROUTER
    # ──────────────────────────────────────────
    def _show_section(self, section: str):
        self.active_section.set(section)
        self.page_title.config(text=section)
        for lbl, btn in self._menu_buttons.items():
            btn.config(bg=COLORS["accent"] if lbl == section else COLORS["sidebar"])
        for w in self.content.winfo_children():
            w.destroy()
        {
            "Dashboard":    self._section_dashboard,
            "Applicants":   self._section_applicants,
            "Employers":    self._section_employers,
            "Jobs":         self._section_jobs,
            "Applications": self._section_applications,
            "Reports":      self._section_reports,
        }[section]()

    # ──────────────────────────────────────────
    # DASHBOARD
    # ──────────────────────────────────────────
    def _section_dashboard(self):
        p = self.content

        tk.Label(p, text="System Overview", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 16))

        # Stat cards
        stats = make_frame(p, bg=COLORS["bg"])
        stats.pack(fill="x", pady=(0, 24))

        rows = execute_query("SELECT COUNT(*) AS c FROM applicant", fetch="one")
        total_applicants = rows["c"] if rows else 0
        rows = execute_query("SELECT COUNT(*) AS c FROM employer", fetch="one")
        total_employers = rows["c"] if rows else 0
        rows = execute_query("SELECT COUNT(*) AS c FROM jobs WHERE is_active=1", fetch="one")
        active_jobs = rows["c"] if rows else 0
        rows = execute_query("SELECT COUNT(*) AS c FROM applications", fetch="one")
        total_apps = rows["c"] if rows else 0

        for i, (label, val, color) in enumerate([
            ("Total Applicants", total_applicants, COLORS["accent"]),
            ("Total Employers",  total_employers,  COLORS["accent2"]),
            ("Active Jobs",      active_jobs,      COLORS["warning"]),
            ("Applications",     total_apps,       "#8B5CF6"),
        ]):
            card = stat_card(stats, label, val, color)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            stats.grid_columnconfigure(i, weight=1)

        # Recent applications
        tk.Label(p, text="Recent Applications", font=FONTS["subhead"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 8))

        cols = ["applicant_name", "job_title", "company_name", "status", "applied_at"]
        widths = [160, 180, 160, 100, 150]
        frame, tree = make_scrollable_table(p, cols, widths)
        frame.pack(fill="both", expand=True)

        rows = execute_query(
            "SELECT * FROM application_details_view ORDER BY applied_at DESC LIMIT 20")
        populate_table(tree, rows or [], cols)

    # ──────────────────────────────────────────
    # APPLICANTS
    # ──────────────────────────────────────────
    def _section_applicants(self):
        p = self.content
        self._generic_user_section(
            p,
            table="applicant",
            id_col="applicant_id",
            cols=["applicant_id","full_name","email","phone","location","experience_years","is_active","created_at"],
            widths=[80,160,180,120,120,80,80,140],
            title="All Applicants",
        )

    # ──────────────────────────────────────────
    # EMPLOYERS
    # ──────────────────────────────────────────
    def _section_employers(self):
        p = self.content
        self._generic_user_section(
            p,
            table="employer",
            id_col="employer_id",
            cols=["employer_id","company_name","email","phone","industry","location","is_active","created_at"],
            widths=[80,180,180,120,130,120,80,140],
            title="All Employers",
        )

    def _generic_user_section(self, p, table, id_col, cols, widths, title):
        tk.Label(p, text=title, font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 12))

        # Search bar + buttons
        top = make_frame(p, bg=COLORS["bg"])
        top.pack(fill="x", pady=(0, 10))

        search_var = tk.StringVar()
        se = make_entry(top, width=30)
        se.pack(side="left", ipady=6, padx=(0, 8))
        make_button(top, "🔍 Search", lambda: self._search_users(tree, table, id_col, cols, search_var.get(), se.get()),
                    bg=COLORS["accent"]).pack(side="left", ipady=3)
        make_button(top, "↺ Refresh", lambda: self._load_users(tree, table, cols),
                    bg=COLORS["border"], fg=COLORS["text"]).pack(side="left", padx=8, ipady=3)

        # Toggle active / delete
        make_success_button(top, "✔ Toggle Active",
            lambda: self._toggle_active(tree, table, id_col, cols)).pack(side="right", ipady=3)
        make_danger_button(top, "🗑 Delete",
            lambda: self._delete_user(tree, table, id_col, cols)).pack(side="right", padx=8, ipady=3)

        frame, tree = make_scrollable_table(p, cols, widths)
        frame.pack(fill="both", expand=True)
        self._load_users(tree, table, cols)

    def _load_users(self, tree, table, cols):
        rows = execute_query(f"SELECT * FROM {table} ORDER BY 1 DESC")
        populate_table(tree, rows or [], cols)

    def _search_users(self, tree, table, id_col, cols, _sv, term):
        if not term.strip():
            self._load_users(tree, table, cols)
            return
        rows = execute_query(
            f"SELECT * FROM {table} WHERE username LIKE %s OR email LIKE %s ORDER BY 1 DESC",
            (f"%{term}%", f"%{term}%"))
        populate_table(tree, rows or [], cols)

    def _toggle_active(self, tree, table, id_col, cols):
        sel = tree.selection()
        if not sel:
            show_error("Select", "Please select a user.")
            return
        vals = tree.item(sel[0])["values"]
        uid  = vals[0]
        cur  = vals[-2]  # is_active column
        new  = 0 if cur else 1
        execute_update(f"UPDATE {table} SET is_active=%s WHERE {id_col}=%s", (new, uid))
        self._load_users(tree, table, cols)

    def _delete_user(self, tree, table, id_col, cols):
        sel = tree.selection()
        if not sel:
            show_error("Select", "Please select a user.")
            return
        vals = tree.item(sel[0])["values"]
        uid  = vals[0]
        name = vals[1]
        if show_confirm("Confirm Delete", f"Delete '{name}'? This cannot be undone."):
            execute_update(f"DELETE FROM {table} WHERE {id_col}=%s", (uid,))
            self._load_users(tree, table, cols)

    # ──────────────────────────────────────────
    # JOBS
    # ──────────────────────────────────────────
    def _section_jobs(self):
        p = self.content
        tk.Label(p, text="All Job Listings", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 12))

        top = make_frame(p, bg=COLORS["bg"])
        top.pack(fill="x", pady=(0, 10))

        se = make_entry(top, width=30)
        se.pack(side="left", ipady=6, padx=(0, 8))

        cols   = ["job_id","title","company_name","category","job_type","salary","location","deadline","is_active"]
        widths = [60,180,160,130,100,140,120,100,70]

        make_button(top, "🔍 Search", lambda: self._search_jobs(tree, se.get()),
                    bg=COLORS["accent"]).pack(side="left", ipady=3)
        make_button(top, "↺ Refresh", lambda: self._load_jobs(tree),
                    bg=COLORS["border"], fg=COLORS["text"]).pack(side="left", padx=8, ipady=3)
        make_danger_button(top, "🗑 Delete Job",
            lambda: self._delete_job(tree)).pack(side="right", ipady=3)

        frame, tree = make_scrollable_table(p, cols, widths)
        frame.pack(fill="both", expand=True)
        self._load_jobs(tree)

    def _load_jobs(self, tree):
        rows = execute_query(
            """SELECT j.job_id, j.title, e.company_name, j.category, j.job_type,
                      j.salary, j.location, j.deadline, j.is_active
               FROM jobs j JOIN employer e ON j.employer_id=e.employer_id
               ORDER BY j.job_id DESC""")
        populate_table(tree, rows or [],
                       ["job_id","title","company_name","category","job_type","salary","location","deadline","is_active"])

    def _search_jobs(self, tree, term):
        if not term.strip():
            self._load_jobs(tree)
            return
        rows = execute_query(
            """SELECT j.job_id, j.title, e.company_name, j.category, j.job_type,
                      j.salary, j.location, j.deadline, j.is_active
               FROM jobs j JOIN employer e ON j.employer_id=e.employer_id
               WHERE j.title LIKE %s OR e.company_name LIKE %s OR j.category LIKE %s
               ORDER BY j.job_id DESC""",
            (f"%{term}%", f"%{term}%", f"%{term}%"))
        populate_table(tree, rows or [],
                       ["job_id","title","company_name","category","job_type","salary","location","deadline","is_active"])

    def _delete_job(self, tree):
        sel = tree.selection()
        if not sel:
            show_error("Select", "Please select a job.")
            return
        vals  = tree.item(sel[0])["values"]
        job_id = vals[0]
        title  = vals[1]
        if show_confirm("Confirm Delete", f"Delete job '{title}'?"):
            execute_update("DELETE FROM jobs WHERE job_id=%s", (job_id,))
            self._load_jobs(tree)

    # ──────────────────────────────────────────
    # APPLICATIONS
    # ──────────────────────────────────────────
    def _section_applications(self):
        p = self.content
        tk.Label(p, text="All Applications", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 12))

        cols   = ["application_id","applicant_name","job_title","company_name","status","applied_at"]
        widths = [100,160,180,160,100,150]

        top = make_frame(p, bg=COLORS["bg"])
        top.pack(fill="x", pady=(0, 10))

        # Status filter
        tk.Label(top, text="Filter by Status:", font=FONTS["small"],
                 bg=COLORS["bg"], fg=COLORS["text_sub"]).pack(side="left", padx=(0, 6))
        status_var = tk.StringVar(value="All")
        cb = ttk.Combobox(top, values=["All","Pending","Reviewed","Accepted","Rejected"],
                          textvariable=status_var, state="readonly", width=14, font=FONTS["body"])
        cb.pack(side="left")

        frame, tree = make_scrollable_table(p, cols, widths)
        frame.pack(fill="both", expand=True)

        def load(sv="All"):
            if sv == "All":
                rows = execute_query("SELECT * FROM application_details_view ORDER BY applied_at DESC")
            else:
                rows = execute_query(
                    "SELECT * FROM application_details_view WHERE status=%s ORDER BY applied_at DESC", (sv,))
            populate_table(tree, rows or [], cols)

        cb.bind("<<ComboboxSelected>>", lambda e: load(status_var.get()))
        make_button(top, "↺ Refresh", lambda: load(status_var.get()),
                    bg=COLORS["border"], fg=COLORS["text"]).pack(side="left", padx=8, ipady=3)
        load()

    # ──────────────────────────────────────────
    # REPORTS
    # ──────────────────────────────────────────
    def _section_reports(self):
        p = self.content
        tk.Label(p, text="Reports & Analytics", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 16))

        # Jobs by category
        self._report_table(p, "Jobs by Category",
            """SELECT category AS 'Category', COUNT(*) AS 'Total Jobs'
               FROM jobs GROUP BY category ORDER BY COUNT(*) DESC""",
            ["Category","Total Jobs"], [200, 120])

        # Applications by status
        self._report_table(p, "Applications by Status",
            """SELECT status AS 'Status', COUNT(*) AS 'Count'
               FROM applications GROUP BY status ORDER BY COUNT(*) DESC""",
            ["Status","Count"], [200, 120])

        # Top companies
        self._report_table(p, "Top Hiring Companies",
            """SELECT e.company_name AS 'Company', COUNT(j.job_id) AS 'Jobs Posted'
               FROM employer e LEFT JOIN jobs j ON e.employer_id=j.employer_id
               GROUP BY e.employer_id ORDER BY COUNT(j.job_id) DESC LIMIT 10""",
            ["Company","Jobs Posted"], [250, 120])

    def _report_table(self, parent, title, sql, cols, widths):
        tk.Label(parent, text=title, font=FONTS["subhead"],
                 bg=COLORS["bg"], fg=COLORS["text_sub"]).pack(anchor="w", pady=(12, 6))
        frame, tree = make_scrollable_table(parent, cols, widths)
        frame.pack(fill="x", pady=(0, 8))
        rows = execute_query(sql)
        populate_table(tree, rows or [], cols)

    # ──────────────────────────────────────────
    def _logout(self):
        if show_confirm("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
