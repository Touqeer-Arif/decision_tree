# applicant.py — Applicant Panel
# Job Portal Management System

import tkinter as tk
from tkinter import ttk, filedialog
from utils import (COLORS, FONTS, make_frame, make_button, make_danger_button,
                   make_success_button, make_entry, make_label, make_text, stat_card,
                   make_scrollable_table, populate_table,
                   center_window, apply_theme, show_error, show_info, show_confirm,
                   is_empty)
from database import execute_query, execute_update

MENU = [
    ("📊", "Dashboard"),
    ("🔍", "Browse Jobs"),
    ("📋", "My Applications"),
    ("👤", "My Profile"),
]


class ApplicantPanel:
    def __init__(self, user: dict):
        self.user = user
        self.applicant_id = user["applicant_id"]
        self.active_section = tk.StringVar(value="Dashboard")

        self.root = tk.Tk()
        self.root.title(f"Applicant Panel — {user['full_name']}")
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

        tk.Label(self.sidebar, text="APPLICANT MENU", font=("Segoe UI", 8, "bold"),
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
        tk.Label(bar, text=f"👤 {self.user['full_name']}",
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
            "Dashboard":       self._section_dashboard,
            "Browse Jobs":     self._section_browse,
            "My Applications": self._section_my_apps,
            "My Profile":      self._section_profile,
        }[section]()

    # ──────────────────────────────────────────
    # DASHBOARD
    # ──────────────────────────────────────────
    def _section_dashboard(self):
        p = self.content
        tk.Label(p, text=f"Hello, {self.user['full_name']}!",
                 font=FONTS["heading"], bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 16))

        stats = make_frame(p, bg=COLORS["bg"])
        stats.pack(fill="x", pady=(0, 24))

        r1 = execute_query("SELECT COUNT(*) AS c FROM applications WHERE applicant_id=%s",
                           (self.applicant_id,), fetch="one")
        r2 = execute_query("SELECT COUNT(*) AS c FROM applications WHERE applicant_id=%s AND status='Accepted'",
                           (self.applicant_id,), fetch="one")
        r3 = execute_query("SELECT COUNT(*) AS c FROM applications WHERE applicant_id=%s AND status='Pending'",
                           (self.applicant_id,), fetch="one")
        r4 = execute_query("SELECT COUNT(*) AS c FROM active_jobs_view", fetch="one")

        for i, (lbl, val, col) in enumerate([
            ("Total Applied",   r1["c"] if r1 else 0, COLORS["accent"]),
            ("Accepted",        r2["c"] if r2 else 0, COLORS["accent2"]),
            ("Pending",         r3["c"] if r3 else 0, COLORS["warning"]),
            ("Available Jobs",  r4["c"] if r4 else 0, "#8B5CF6"),
        ]):
            card = stat_card(stats, lbl, val, col)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            stats.grid_columnconfigure(i, weight=1)

        # My recent applications
        tk.Label(p, text="My Recent Applications", font=FONTS["subhead"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 8))

        cols   = ["job_title","company_name","status","applied_at"]
        widths = [220, 200, 120, 160]
        frame, tree = make_scrollable_table(p, cols, widths)
        frame.pack(fill="both", expand=True)
        rows = execute_query(
            """SELECT j.title AS job_title, e.company_name, a.status, a.applied_at
               FROM applications a
               JOIN jobs j ON a.job_id=j.job_id
               JOIN employer e ON j.employer_id=e.employer_id
               WHERE a.applicant_id=%s ORDER BY a.applied_at DESC LIMIT 10""",
            (self.applicant_id,))
        populate_table(tree, rows or [], cols)

    # ──────────────────────────────────────────
    # BROWSE JOBS
    # ──────────────────────────────────────────
    def _section_browse(self):
        p = self.content
        tk.Label(p, text="Browse Available Jobs", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 12))

        # Search + filter bar
        top = make_frame(p, bg=COLORS["bg"])
        top.pack(fill="x", pady=(0, 10))

        se = make_entry(top, width=24)
        se.pack(side="left", ipady=6, padx=(0, 6))
        se.insert(0, "Search jobs...")
        se.bind("<FocusIn>",  lambda e: se.delete(0, "end") if se.get() == "Search jobs..." else None)
        se.bind("<FocusOut>", lambda e: se.insert(0, "Search jobs...") if not se.get() else None)

        cat_var = tk.StringVar(value="All Categories")
        cats = ["All Categories","Software Development","Web Development","Data Science",
                "Artificial Intelligence","Database","Quality Assurance","DevOps",
                "UI/UX Design","Mobile Development","Other"]
        cat_cb = ttk.Combobox(top, values=cats, textvariable=cat_var,
                              state="readonly", width=22, font=FONTS["body"])
        cat_cb.pack(side="left", padx=6, ipady=4)

        type_var = tk.StringVar(value="All Types")
        ttypes   = ["All Types","Full-Time","Part-Time","Remote","Contract","Internship"]
        type_cb  = ttk.Combobox(top, values=ttypes, textvariable=type_var,
                                state="readonly", width=14, font=FONTS["body"])
        type_cb.pack(side="left", padx=6, ipady=4)

        cols   = ["job_id","title","company_name","category","job_type","salary","location","deadline"]
        widths = [60, 200, 160, 140, 100, 140, 120, 110]
        frame, tree = make_scrollable_table(p, cols, widths)
        frame.pack(fill="both", expand=True)

        def load():
            term = se.get().strip()
            if term == "Search jobs...":
                term = ""
            cat  = cat_var.get()
            jtyp = type_var.get()
            sql  = """SELECT job_id, title, company_name, category, job_type,
                             salary, location, deadline
                      FROM active_jobs_view WHERE 1=1"""
            params = []
            if term:
                sql += " AND (title LIKE %s OR company_name LIKE %s OR category LIKE %s)"
                params += [f"%{term}%", f"%{term}%", f"%{term}%"]
            if cat != "All Categories":
                sql += " AND category=%s"
                params.append(cat)
            if jtyp != "All Types":
                sql += " AND job_type=%s"
                params.append(jtyp)
            sql += " ORDER BY posted_at DESC"
            rows = execute_query(sql, params)
            populate_table(tree, rows or [], cols)

        make_button(top, "🔍 Search", load, bg=COLORS["accent"]).pack(side="left", padx=6, ipady=3)
        make_button(top, "↺ All", load, bg=COLORS["border"], fg=COLORS["text"]).pack(side="left", ipady=3)
        make_success_button(top, "✔ Apply for Selected",
                            lambda: self._apply_dialog(tree)).pack(side="right", ipady=3)

        # Hint label
        tk.Label(p, text="💡 Tip: Select a job and click 'Apply for Selected', or Double-click a job to view details and apply.",
                 font=FONTS["small"], bg=COLORS["bg"], fg=COLORS["text_sub"]).pack(anchor="w", pady=(0,6))

        tree.bind("<Double-1>", lambda e: self._view_job_details(tree))
        load()

    def _view_job_details(self, tree):
        sel = tree.selection()
        if not sel:
            return
        vals   = tree.item(sel[0])["values"]
        job_id = vals[0]
        row    = execute_query(
            """SELECT j.*, e.company_name, e.industry, e.website
               FROM jobs j JOIN employer e ON j.employer_id=e.employer_id
               WHERE j.job_id=%s""", (job_id,), fetch="one")
        if not row:
            return

        win = tk.Toplevel(self.root)
        win.title(f"Job Details — {row['title']}")
        win.configure(bg=COLORS["bg"])
        center_window(win, 600, 500)
        win.grab_set()

        hdr = make_frame(win, bg=COLORS["card"])
        hdr.pack(fill="x")
        tk.Label(hdr, text=row["title"], font=FONTS["heading"],
                 bg=COLORS["card"], fg=COLORS["white"],
                 padx=20, pady=14, anchor="w").pack(fill="x")

        body = make_frame(win, bg=COLORS["bg"])
        body.pack(fill="both", expand=True, padx=24, pady=16)

        def info(lbl, val):
            f = make_frame(body, bg=COLORS["bg"])
            f.pack(fill="x", pady=3)
            tk.Label(f, text=f"{lbl}:", font=FONTS["subhead"],
                     bg=COLORS["bg"], fg=COLORS["text_sub"], width=16, anchor="w").pack(side="left")
            tk.Label(f, text=str(val or "—"), font=FONTS["body"],
                     bg=COLORS["bg"], fg=COLORS["text"], anchor="w").pack(side="left")

        info("Company",    row["company_name"])
        info("Industry",   row["industry"])
        info("Category",   row["category"])
        info("Job Type",   row["job_type"])
        info("Salary",     row["salary"])
        info("Location",   row["location"])
        info("Experience", row["experience_req"])
        info("Deadline",   row["deadline"])
        info("Website",    row["website"])

        tk.Label(body, text="Description:", font=FONTS["subhead"],
                 bg=COLORS["bg"], fg=COLORS["text_sub"]).pack(anchor="w", pady=(12, 4))
        desc_t = make_text(body, height=5, width=60)
        desc_t.insert("1.0", str(row["description"] or ""))
        desc_t.config(state="disabled")
        desc_t.pack(fill="x")

        make_success_button(body, "✔ Apply Now",
                            lambda: (win.destroy(), self._apply_with_id(job_id))).pack(pady=12)

    def _apply_dialog(self, tree):
        sel = tree.selection()
        if not sel:
            show_error("Select", "Please select a job to apply.")
            return
        vals   = tree.item(sel[0])["values"]
        job_id = vals[0]
        self._apply_with_id(job_id)

    def _apply_with_id(self, job_id: int):
        # Check already applied
        exists = execute_query(
            "SELECT 1 FROM applications WHERE job_id=%s AND applicant_id=%s",
            (job_id, self.applicant_id), fetch="one")
        if exists:
            show_info("Already Applied", "You have already applied for this job.")
            return

        # Cover letter dialog
        win = tk.Toplevel(self.root)
        win.title("Apply for Job")
        win.configure(bg=COLORS["bg"])
        center_window(win, 520, 380)
        win.grab_set()

        tk.Label(win, text="Write a Cover Letter (Optional)", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["white"],
                 padx=20, pady=16).pack(anchor="w")

        t = make_text(win, height=10, width=60)
        t.pack(fill="both", expand=True, padx=20)

        def submit():
            cl = t.get("1.0", "end").strip()
            try:
                execute_update(
                    "INSERT INTO applications (job_id, applicant_id, cover_letter) VALUES (%s,%s,%s)",
                    (job_id, self.applicant_id, cl))
                show_info("Applied!", "Your application has been submitted successfully.")
                win.destroy()
            except Exception as ex:
                show_error("Error", str(ex))

        btn_f = make_frame(win, bg=COLORS["bg"])
        btn_f.pack(pady=12, padx=20, fill="x")
        make_success_button(btn_f, "✔ Submit Application", submit).pack(side="left", ipady=5)
        make_button(btn_f, "Cancel", win.destroy,
                    bg=COLORS["border"], fg=COLORS["text"]).pack(side="left", padx=10, ipady=5)

    # ──────────────────────────────────────────
    # MY APPLICATIONS
    # ──────────────────────────────────────────
    def _section_my_apps(self):
        p = self.content
        tk.Label(p, text="My Applications", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 12))

        top = make_frame(p, bg=COLORS["bg"])
        top.pack(fill="x", pady=(0, 10))

        cols   = ["application_id","job_title","company_name","status","applied_at"]
        widths = [100, 220, 180, 120, 160]
        frame, tree = make_scrollable_table(p, cols, widths)
        frame.pack(fill="both", expand=True)

        def load():
            rows = execute_query(
                """SELECT a.application_id, j.title AS job_title, e.company_name,
                          a.status, a.applied_at
                   FROM applications a
                   JOIN jobs j ON a.job_id=j.job_id
                   JOIN employer e ON j.employer_id=e.employer_id
                   WHERE a.applicant_id=%s ORDER BY a.applied_at DESC""",
                (self.applicant_id,))
            populate_table(tree, rows or [], cols)

        def withdraw():
            sel = tree.selection()
            if not sel:
                show_error("Select", "Please select an application.")
                return
            vals = tree.item(sel[0])["values"]
            if vals[3] != "Pending":
                show_error("Cannot Withdraw", "You can only withdraw Pending applications.")
                return
            if show_confirm("Withdraw", "Withdraw this application?"):
                execute_update("DELETE FROM applications WHERE application_id=%s", (vals[0],))
                load()

        make_button(top, "↺ Refresh", load,
                    bg=COLORS["border"], fg=COLORS["text"]).pack(side="left", ipady=3)
        make_danger_button(top, "✖ Withdraw Application",
                           withdraw).pack(side="right", ipady=3)
        load()

    # ──────────────────────────────────────────
    # PROFILE
    # ──────────────────────────────────────────
    def _section_profile(self):
        p = self.content
        tk.Label(p, text="My Profile", font=FONTS["heading"],
                 bg=COLORS["bg"], fg=COLORS["white"]).pack(anchor="w", pady=(0, 16))

        row = execute_query("SELECT * FROM applicant WHERE applicant_id=%s",
                            (self.applicant_id,), fetch="one") or self.user

        fields_cfg = [
            ("Full Name",         "full_name"),
            ("Email",             "email"),
            ("Phone",             "phone"),
            ("Location / City",   "location"),
            ("Education",         "education"),
            ("Years of Experience","experience_years"),
        ]
        self.profile_fields = {}

        canvas = tk.Canvas(p, bg=COLORS["bg"], highlightthickness=0)
        vsb = ttk.Scrollbar(p, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        form = make_frame(canvas, bg=COLORS["bg"])
        cw = canvas.create_window((0, 0), window=form, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(cw, width=e.width))
        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        for lbl, key in fields_cfg:
            make_label(form, lbl, font=FONTS["small"],
                       fg=COLORS["text_sub"], bg=COLORS["bg"]).pack(anchor="w", padx=20, pady=(8,2))
            e = make_entry(form, width=50)
            e.insert(0, str(row.get(key, "") or ""))
            e.pack(fill="x", padx=20, ipady=7)
            self.profile_fields[key] = e

        make_label(form, "Skills (comma-separated)", font=FONTS["small"],
                   fg=COLORS["text_sub"], bg=COLORS["bg"]).pack(anchor="w", padx=20, pady=(8,2))
        skills_t = make_text(form, height=3, width=60)
        skills_t.insert("1.0", str(row.get("skills", "") or ""))
        skills_t.pack(fill="x", padx=20)
        self.profile_fields["skills"] = skills_t

        # ── Resume Upload ──
        tk.Frame(form, bg=COLORS["border"], height=1).pack(fill="x", padx=20, pady=(16,0))
        make_label(form, "📄 Resume / CV Upload", font=FONTS["subhead"],
                   fg=COLORS["white"], bg=COLORS["bg"]).pack(anchor="w", padx=20, pady=(12,4))

        current_resume = str(row.get("resume_path", "") or "")
        self.resume_path_var = tk.StringVar(value=current_resume)

        resume_row = make_frame(form, bg=COLORS["bg"])
        resume_row.pack(fill="x", padx=20, pady=(0,8))

        resume_lbl = tk.Label(resume_row,
            textvariable=self.resume_path_var,
            font=FONTS["small"], bg=COLORS["card"], fg=COLORS["text_sub"],
            anchor="w", padx=10, pady=8, relief="flat",
            highlightthickness=1, highlightbackground=COLORS["border"])
        resume_lbl.pack(side="left", fill="x", expand=True, ipady=4)

        def browse_resume():
            path = filedialog.askopenfilename(
                title="Select Resume / CV",
                filetypes=[("PDF Files","*.pdf"),("Word Files","*.docx *.doc"),("All Files","*.*")]
            )
            if path:
                import shutil, os
                os.makedirs("resumes", exist_ok=True)
                filename = f"resume_{self.applicant_id}_{os.path.basename(path)}"
                dest = os.path.join("resumes", filename)
                shutil.copy2(path, dest)
                self.resume_path_var.set(dest)
                show_info("Resume Uploaded", f"Resume saved:\n{filename}\n\nClick 'Save Profile' to confirm.")

        tk.Button(resume_row, text="📂 Browse File",
                  bg=COLORS["accent"], fg=COLORS["white"],
                  activebackground=COLORS["accent_hover"],
                  font=FONTS["btn"], relief="flat", cursor="hand2",
                  padx=12, pady=8, command=browse_resume).pack(side="left", padx=(8,0))

        if current_resume:
            tk.Label(form, text=f"✅ Current: {current_resume}",
                     font=FONTS["small"], bg=COLORS["bg"],
                     fg=COLORS["accent2"]).pack(anchor="w", padx=20, pady=(0,8))

        make_button(form, "💾 Save Profile", self._save_profile).pack(padx=20, pady=16, anchor="w", ipady=6)

    def _save_profile(self):
        def gf(key):
            w = self.profile_fields.get(key)
            if isinstance(w, tk.Text):
                return w.get("1.0", "end").strip()
            return w.get().strip()

        try:
            exp = gf("experience_years")
            try:
                exp = int(exp)
            except ValueError:
                exp = 0
            resume = self.resume_path_var.get() if hasattr(self, "resume_path_var") else ""
            execute_update(
                """UPDATE applicant SET full_name=%s, email=%s, phone=%s,
                          location=%s, education=%s, experience_years=%s, skills=%s,
                          resume_path=%s
                   WHERE applicant_id=%s""",
                (gf("full_name"), gf("email"), gf("phone"),
                 gf("location"), gf("education"), exp,
                 gf("skills"), resume, self.applicant_id))
            show_info("Saved", "Profile updated successfully!")
        except Exception as ex:
            show_error("Error", str(ex))

    def _logout(self):
        if show_confirm("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
