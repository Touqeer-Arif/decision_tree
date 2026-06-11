# employer.py — Employer Panel
# Job Portal Management System

import tkinter as tk
from tkinter import ttk
from utils import (COLORS, FONTS, make_frame, make_button, make_danger_button,
                   make_success_button, make_entry, make_label, make_text,
                   stat_card, make_scrollable_table, populate_table,
                   center_window, apply_theme, show_error, show_info, show_confirm,
                   is_empty)
from database import execute_query, execute_update
from datepicker import DatePicker

MENU = [
    ("📊", "Dashboard"),
    ("💼", "My Jobs"),
    ("➕", "Post a Job"),
    ("📋", "Applications"),
    ("👤", "My Profile"),
]


class EmployerPanel:
    def __init__(self, user: dict):
        self.user = user
        self.employer_id = user["employer_id"]
        self.active_section = tk.StringVar(value="Dashboard")
        self.edit_job_id = None

        self.root = tk.Tk()
        self.root.title(f"Employer Panel — {user['company_name']}")
        self.root.configure(bg=COLORS["bg"])
        apply_theme(self.root)
        center_window(self.root, 1200, 720)
        self.root.resizable(True, True)

        self._build_layout()
        self._show_section("Dashboard")
        self.root.mainloop()

    def _build_layout(self):
        self.sidebar = make_frame(self.root, bg=COLORS["sidebar"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        self.main = make_frame(self.root, bg=COLORS["bg"])
        self.main.pack(side="right", fill="both", expand=True)
        self._build_topbar()

        self.content = make_frame(self.main, bg=COLORS["bg"])
        self.content.pack(fill="both", expand=True, padx=24, pady=16)

    def _build_sidebar(self):
        logo = make_frame(self.sidebar, bg=COLORS["accent"])
        logo.pack(fill="x")
        tk.Label(logo, text="💼 Job Portal", font=FONTS["logo"],
                 bg=COLORS["accent"], fg=COLORS["white"],
                 pady=16, padx=16, anchor="w").pack(fill="x")

        tk.Label(self.sidebar, text="EMPLOYER MENU", font=("Segoe UI", 8, "bold"),
                 bg=COLORS["sidebar"], fg=COLORS["text_sub"],
                 padx=16, pady=12, anchor="w").pack(fill="x")

        self._menu_buttons = {}
        for icon, label in MENU:
            btn = tk.Button(self.sidebar,
                text=f"  {icon}  {label}", font=FONTS["sidebar"],
                bg=COLORS["sidebar"], fg=COLORS["text"],
                activebackground=COLORS["accent"], activeforeground=COLORS["white"],
                relief="flat", anchor="w", padx=8, pady=10, cursor="hand2",
                command=lambda l=label: self._show_section(l))
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORS["accent"]))
            btn.bind("<Leave>", lambda e, b=btn, l=label: b.config(
                bg=COLORS["accent"] if self.active_section.get() == l else COLORS["sidebar"]))
            self._menu_buttons[label] = btn

        tk.Frame(self.sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=16, pady=10)
        tk.Button(self.sidebar, text="  🚪  Logout", font=FONTS["sidebar"],
                  bg=COLORS["sidebar"], fg=COLORS["danger"],
                  activebackground=COLORS["danger"], activeforeground=COLORS["white"],
                  relief="flat", anchor="w", padx=8, pady=10, cursor="hand2",
                  command=self._logout).pack(fill="x")

    def _build_topbar(self):
        bar = make_frame(self.main, bg=COLORS["card"])
        bar.pack(fill="x")
        self.page_title = tk.Label(bar, text="Dashboard", font=FONTS["heading"],
                                   bg=COLORS["card"], fg=COLORS["white"],
                                   padx=24, pady=14, anchor="w")
        self.page_title.pack(side="left")
        tk.Label(bar, text=f"🏢 {self.user['company_name']}",
                 font=FONTS["small"], bg=COLORS["card"],
                 fg=COLORS["text_sub"], padx=24, pady=14).pack(side="right")

    def _show_section(self, section: str):
        self.active_section.set(section)
        self.page_title.config(text=section)
        for lbl, btn in self._menu_buttons.items():
            btn.config(bg=COLORS["accent"] if lbl == section else COLORS["sidebar"])
        for w in self.content.winfo_children():
            w.destroy()
        {
            "Dashboard":    self._section_dashboard,
            "My Jobs":      self._section_my_jobs,
            "Post a Job":   self._section_post_job,
            "Applications": self._section_applications,
            "My Profile":   self._section_profile,
        }[section]()

    # ──────────────────────────────────────────
    # DASHBOARD
    # ──────────────────────────────────────────
    def _section_dashboard(self):
        p = self.content
        tk.Label(p, text=f"Welcome, {self.user['company_name']}!",
                 font=FONTS["heading"], bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 16))

        stats = make_frame(p, bg=COLORS["bg"])
        stats.pack(fill="x", pady=(0, 24))

        r1 = execute_query("SELECT COUNT(*) AS c FROM jobs WHERE employer_id=%s AND is_active=1",
                           (self.employer_id,), fetch="one")
        r2 = execute_query("SELECT COUNT(*) AS c FROM jobs WHERE employer_id=%s",
                           (self.employer_id,), fetch="one")
        r3 = execute_query(
            """SELECT COUNT(*) AS c FROM applications a
               JOIN jobs j ON a.job_id=j.job_id WHERE j.employer_id=%s""",
            (self.employer_id,), fetch="one")
        r4 = execute_query(
            """SELECT COUNT(*) AS c FROM applications a
               JOIN jobs j ON a.job_id=j.job_id
               WHERE j.employer_id=%s AND a.status='Accepted'""",
            (self.employer_id,), fetch="one")

        data = [
            ("Active Jobs",    r1["c"] if r1 else 0, COLORS["accent"]),
            ("Total Jobs",     r2["c"] if r2 else 0, COLORS["accent2"]),
            ("Applications",   r3["c"] if r3 else 0, COLORS["warning"]),
            ("Accepted",       r4["c"] if r4 else 0, "#8B5CF6"),
        ]
        for i, (lbl, val, col) in enumerate(data):
            card = stat_card(stats, lbl, val, col)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            stats.grid_columnconfigure(i, weight=1)

        # Recent applications
        tk.Label(p, text="Recent Applications to Your Jobs",
                 font=FONTS["subhead"], bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 8))
        cols   = ["applicant_name","job_title","status","applied_at"]
        widths = [180, 220, 110, 150]
        frame, tree = make_scrollable_table(p, cols, widths)
        frame.pack(fill="both", expand=True)
        rows = execute_query(
            """SELECT ap.full_name AS applicant_name, j.title AS job_title,
                      a.status, a.applied_at
               FROM applications a
               JOIN applicant ap ON a.applicant_id=ap.applicant_id
               JOIN jobs j ON a.job_id=j.job_id
               WHERE j.employer_id=%s ORDER BY a.applied_at DESC LIMIT 20""",
            (self.employer_id,))
        populate_table(tree, rows or [], cols)

    # ──────────────────────────────────────────
    # MY JOBS
    # ──────────────────────────────────────────
    def _section_my_jobs(self):
        p = self.content
        tk.Label(p, text="My Job Listings", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 12))

        top = make_frame(p, bg=COLORS["bg"])
        top.pack(fill="x", pady=(0, 10))
        make_button(top, "➕ Post New Job", lambda: self._show_section("Post a Job")).pack(side="left", ipady=3)
        make_button(top, "↺ Refresh", lambda: self._load_my_jobs(tree),
                    bg=COLORS["border"], fg=COLORS["text"]).pack(side="left", padx=8, ipady=3)
        make_button(top, "✏ Edit Selected",
                    lambda: self._edit_job(tree)).pack(side="right", padx=8, ipady=3)
        make_danger_button(top, "🗑 Delete",
                           lambda: self._delete_job(tree)).pack(side="right", ipady=3)

        cols   = ["job_id","title","category","job_type","salary","location","deadline","is_active"]
        widths = [70, 200, 130, 110, 140, 130, 110, 70]
        frame, tree = make_scrollable_table(p, cols, widths)
        frame.pack(fill="both", expand=True)
        self._load_my_jobs(tree)
        self._jobs_tree = tree

    def _load_my_jobs(self, tree):
        rows = execute_query(
            """SELECT job_id, title, category, job_type, salary, location, deadline, is_active
               FROM jobs WHERE employer_id=%s ORDER BY job_id DESC""",
            (self.employer_id,))
        populate_table(tree, rows or [],
                       ["job_id","title","category","job_type","salary","location","deadline","is_active"])

    def _delete_job(self, tree):
        sel = tree.selection()
        if not sel:
            show_error("Select", "Please select a job.")
            return
        vals = tree.item(sel[0])["values"]
        if show_confirm("Delete", f"Delete job '{vals[1]}'?"):
            execute_update("DELETE FROM jobs WHERE job_id=%s AND employer_id=%s",
                           (vals[0], self.employer_id))
            self._load_my_jobs(tree)

    def _edit_job(self, tree):
        sel = tree.selection()
        if not sel:
            show_error("Select", "Please select a job to edit.")
            return
        vals = tree.item(sel[0])["values"]
        self.edit_job_id = vals[0]
        self._show_section("Post a Job")

    # ──────────────────────────────────────────
    # POST / EDIT JOB
    # ──────────────────────────────────────────
    def _section_post_job(self):
        p = self.content
        editing = self.edit_job_id is not None
        tk.Label(p, text="Edit Job" if editing else "Post a New Job",
                 font=FONTS["heading"], bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 16))

        # Load existing data if editing
        existing = {}
        if editing:
            row = execute_query("SELECT * FROM jobs WHERE job_id=%s", (self.edit_job_id,), fetch="one")
            if row:
                existing = row

        # Scrollable form
        canvas = tk.Canvas(p, bg=COLORS["bg"], highlightthickness=0)
        vsb = ttk.Scrollbar(p, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        form = make_frame(canvas, bg=COLORS["bg"])
        cw = canvas.create_window((0, 0), window=form, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(cw, width=e.width))
        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self.job_fields = {}
        pad = {"padx": 20, "pady": 4}

        def row_pair(lbl1, key1, lbl2, key2, show1=None, show2=None, combo_opts=None, combo_opts2=None):
            r = make_frame(form, bg=COLORS["bg"])
            r.pack(fill="x", **pad)
            for lbl, key, side, so, co in [(lbl1, key1, "left", show1, combo_opts),
                                            (lbl2, key2, "right", show2, combo_opts2)]:
                col = make_frame(r, bg=COLORS["bg"])
                col.pack(side=side, fill="x", expand=True, padx=6)
                tk.Label(col, text=lbl, font=FONTS["small"],
                         bg=COLORS["bg"], fg=COLORS["text_sub"]).pack(anchor="w", pady=(0, 3))
                if co:
                    v = tk.StringVar(value=existing.get(key, co[0]) or co[0])
                    cb = ttk.Combobox(col, values=co, textvariable=v,
                                      state="readonly", width=28, font=FONTS["body"])
                    cb.pack(fill="x", ipady=5)
                    self.job_fields[key] = v
                else:
                    e = make_entry(col, show=so, width=32)
                    if existing.get(key):
                        e.insert(0, str(existing[key]))
                    e.pack(fill="x", ipady=7)
                    self.job_fields[key] = e

        def single_row(lbl, key, widget="entry", height=4):
            make_label(form, lbl, font=FONTS["small"],
                       fg=COLORS["text_sub"], bg=COLORS["bg"]).pack(anchor="w", padx=26, pady=(8, 3))
            if widget == "text":
                t = make_text(form, height=height, width=60)
                if existing.get(key):
                    t.insert("1.0", str(existing[key]))
                t.pack(fill="x", padx=26, pady=(0, 4))
                self.job_fields[key] = t
            else:
                e = make_entry(form, width=60)
                if existing.get(key):
                    e.insert(0, str(existing[key]))
                e.pack(fill="x", padx=26, ipady=7, pady=(0, 4))
                self.job_fields[key] = e

        single_row("Job Title *", "title")
        row_pair("Category *", "category", "Job Type *", "job_type",
                 combo_opts=["Software Development","Web Development","Data Science",
                             "Artificial Intelligence","Database","Quality Assurance",
                             "DevOps","UI/UX Design","Mobile Development","Other"],
                 combo_opts2=["Full-Time","Part-Time","Remote","Contract","Internship"])
        row_pair("Salary / Package", "salary", "Location *", "location")
        # Experience + Deadline row with calendar picker
        dr = make_frame(form, bg=COLORS["bg"])
        dr.pack(fill="x", padx=20, pady=4)

        exp_col = make_frame(dr, bg=COLORS["bg"])
        exp_col.pack(side="left", fill="x", expand=True, padx=6)
        tk.Label(exp_col, text="Experience Required", font=FONTS["small"],
                 bg=COLORS["bg"], fg=COLORS["text_sub"]).pack(anchor="w", pady=(0,3))
        exp_e = make_entry(exp_col, width=32)
        if existing.get("experience_req"):
            exp_e.insert(0, str(existing["experience_req"]))
        exp_e.pack(fill="x", ipady=7)
        self.job_fields["experience_req"] = exp_e

        dl_col = make_frame(dr, bg=COLORS["bg"])
        dl_col.pack(side="right", fill="x", expand=True, padx=6)
        tk.Label(dl_col, text="Application Deadline  (📅 click calendar)", font=FONTS["small"],
                 bg=COLORS["bg"], fg=COLORS["text_sub"]).pack(anchor="w", pady=(0,3))
        dl_row = make_frame(dl_col, bg=COLORS["bg"])
        dl_row.pack(fill="x")
        dl_e = make_entry(dl_row, width=22)
        if existing.get("deadline"):
            dl_e.insert(0, str(existing["deadline"]))
        dl_e.pack(side="left", ipady=7, fill="x", expand=True)
        tk.Button(dl_row, text="📅", font=("Segoe UI Emoji", 11),
                  bg=COLORS["accent"], fg=COLORS["white"],
                  activebackground=COLORS["accent_hover"],
                  relief="flat", cursor="hand2", padx=8, pady=6,
                  command=lambda e=dl_e: DatePicker(form, e)).pack(side="left", padx=(4,0))
        self.job_fields["deadline"] = dl_e

        single_row("Job Description *", "description", widget="text", height=5)

        # Buttons
        btn_f = make_frame(form, bg=COLORS["bg"])
        btn_f.pack(pady=20, padx=26, fill="x")
        lbl = "Update Job" if editing else "Post Job"
        make_button(btn_f, f"✔ {lbl}", self._save_job).pack(side="left", ipady=6)
        make_button(btn_f, "Cancel", lambda: self._cancel_edit(),
                    bg=COLORS["border"], fg=COLORS["text"]).pack(side="left", padx=12, ipady=6)

    def _get_field(self, key):
        w = self.job_fields.get(key)
        if w is None:
            return ""
        if isinstance(w, tk.StringVar):
            return w.get().strip()
        if isinstance(w, tk.Text):
            return w.get("1.0", "end").strip()
        return w.get().strip()

    def _save_job(self):
        title    = self._get_field("title")
        category = self._get_field("category")
        job_type = self._get_field("job_type")
        location = self._get_field("location")
        desc     = self._get_field("description")
        salary   = self._get_field("salary")
        exp_req  = self._get_field("experience_req")
        deadline = self._get_field("deadline") or None

        if is_empty(title) or is_empty(location) or is_empty(desc):
            show_error("Validation", "Please fill in Title, Location, and Description.")
            return

        try:
            if self.edit_job_id:
                execute_update(
                    """UPDATE jobs SET title=%s, category=%s, job_type=%s, location=%s,
                              description=%s, salary=%s, experience_req=%s, deadline=%s
                       WHERE job_id=%s AND employer_id=%s""",
                    (title, category, job_type, location, desc,
                     salary, exp_req, deadline, self.edit_job_id, self.employer_id))
                show_info("Success", "Job updated successfully!")
            else:
                execute_update(
                    """INSERT INTO jobs (employer_id, title, category, job_type, location,
                                        description, salary, experience_req, deadline)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (self.employer_id, title, category, job_type, location,
                     desc, salary, exp_req, deadline))
                show_info("Success", "Job posted successfully!")
        except Exception as ex:
            show_error("Error", str(ex))
        finally:
            self._cancel_edit()

    def _cancel_edit(self):
        self.edit_job_id = None
        self._show_section("My Jobs")

    # ──────────────────────────────────────────
    # APPLICATIONS
    # ──────────────────────────────────────────
    def _section_applications(self):
        p = self.content
        tk.Label(p, text="Applications Received", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 12))

        top = make_frame(p, bg=COLORS["bg"])
        top.pack(fill="x", pady=(0, 10))

        cols   = ["application_id","applicant_name","applicant_email","applicant_phone",
                  "job_title","status","applied_at"]
        widths = [100, 160, 180, 120, 180, 100, 140]
        frame, tree = make_scrollable_table(p, cols, widths)
        frame.pack(fill="both", expand=True)

        def load():
            rows = execute_query(
                """SELECT a.application_id, ap.full_name AS applicant_name,
                          ap.email AS applicant_email, ap.phone AS applicant_phone,
                          j.title AS job_title, a.status, a.applied_at
                   FROM applications a
                   JOIN applicant ap ON a.applicant_id=ap.applicant_id
                   JOIN jobs j ON a.job_id=j.job_id
                   WHERE j.employer_id=%s ORDER BY a.applied_at DESC""",
                (self.employer_id,))
            populate_table(tree, rows or [], cols)

        def change_status(new_status):
            sel = tree.selection()
            if not sel:
                show_error("Select", "Please select an application.")
                return
            vals = tree.item(sel[0])["values"]
            aid  = vals[0]
            execute_update("UPDATE applications SET status=%s WHERE application_id=%s",
                           (new_status, aid))
            load()

        make_button(top, "↺ Refresh", load,
                    bg=COLORS["border"], fg=COLORS["text"]).pack(side="left", ipady=3)
        make_success_button(top, "✔ Accept",
                            lambda: change_status("Accepted")).pack(side="right", ipady=3)
        make_danger_button(top, "✖ Reject",
                           lambda: change_status("Rejected")).pack(side="right", padx=8, ipady=3)
        make_button(top, "📝 Mark Reviewed",
                    lambda: change_status("Reviewed"),
                    bg=COLORS["warning"], fg=COLORS["bg"]).pack(side="right", padx=8, ipady=3)
        load()

    # ──────────────────────────────────────────
    # PROFILE
    # ──────────────────────────────────────────
    def _section_profile(self):
        p = self.content
        tk.Label(p, text="My Company Profile", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 16))

        row = execute_query("SELECT * FROM employer WHERE employer_id=%s",
                            (self.employer_id,), fetch="one") or self.user

        fields_cfg = [
            ("Company Name",  "company_name"),
            ("Email",         "email"),
            ("Phone",         "phone"),
            ("Industry",      "industry"),
            ("Location",      "location"),
            ("Website",       "website"),
        ]
        self.profile_fields = {}
        for lbl, key in fields_cfg:
            make_label(p, lbl, font=FONTS["small"],
                       fg=COLORS["text_sub"], bg=COLORS["bg"]).pack(anchor="w", padx=20, pady=(8,2))
            e = make_entry(p, width=50)
            e.insert(0, str(row.get(key, "") or ""))
            e.pack(fill="x", padx=20, ipady=7)
            self.profile_fields[key] = e

        make_label(p, "Description", font=FONTS["small"],
                   fg=COLORS["text_sub"], bg=COLORS["bg"]).pack(anchor="w", padx=20, pady=(8,2))
        desc_t = make_text(p, height=4, width=60)
        desc_t.insert("1.0", str(row.get("description", "") or ""))
        desc_t.pack(fill="x", padx=20)
        self.profile_fields["description"] = desc_t

        make_button(p, "💾 Save Profile", self._save_profile).pack(padx=20, pady=16, anchor="w", ipady=6)

    def _save_profile(self):
        def gf(key):
            w = self.profile_fields.get(key)
            if isinstance(w, tk.Text):
                return w.get("1.0", "end").strip()
            return w.get().strip()

        try:
            execute_update(
                """UPDATE employer SET company_name=%s, email=%s, phone=%s,
                          industry=%s, location=%s, website=%s, description=%s
                   WHERE employer_id=%s""",
                (gf("company_name"), gf("email"), gf("phone"),
                 gf("industry"), gf("location"), gf("website"),
                 gf("description"), self.employer_id))
            show_info("Saved", "Profile updated successfully!")
        except Exception as ex:
            show_error("Error", str(ex))

    def _logout(self):
        if show_confirm("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
