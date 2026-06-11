# Job Portal Management System
### Database Systems Project — Python + MySQL + Tkinter

---

## Project Structure

```
JobPortal/
├── main.py           ← START HERE (run this)
├── login.py          ← Login screen (Admin / Employer / Applicant)
├── register.py       ← Registration for new users
├── admin.py          ← Admin panel
├── employer.py       ← Employer panel
├── applicant.py      ← Applicant panel
├── database.py       ← DB connection & helpers  ← EDIT YOUR CREDENTIALS HERE
├── utils.py          ← Shared theme, widgets, utilities
├── requirements.txt  ← Python dependencies
├── database/
│   └── jobportal.sql ← Full database setup (run this first)
└── resumes/          ← (folder for resume uploads)
```

---

## Setup Instructions (Step by Step)

### Step 1 — Install Python dependencies
Open terminal in VS Code and run:
```
pip install pymysql
```

### Step 2 — Set up MySQL Database
1. Open **MySQL Workbench**
2. Connect to your local MySQL server
3. Open and run the file: `database/jobportal.sql`
4. This creates the database, all tables, views, stored procedures, indexes, and sample data

### Step 3 — Configure database credentials
Open `database.py` and edit:
```python
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",       # ← your MySQL username
    "password": "",           # ← your MySQL password
    "database": "jobportal",
}
```

### Step 4 — Run the application
```
python main.py
```

---

## Default Login Credentials (from sample data)

| Role      | Username  | Password |
|-----------|-----------|----------|
| Admin     | admin     | admin123 |
| Employer  | techcorp  | pass123  |
| Employer  | nexagen   | pass123  |
| Applicant | ali_dev   | pass123  |
| Applicant | sara_qa   | pass123  |
| Applicant | usman_ml  | pass123  |

---

## Features Implemented

### Login System
- Role-based login (Admin / Employer / Applicant)
- Show/hide password toggle
- Registration for new Employers and Applicants

### Admin Panel
- Dashboard with statistics
- View/search/delete Applicants
- View/search/delete Employers
- View/search/delete Jobs
- View all Applications with status filter
- Reports: Jobs by Category, Applications by Status, Top Hiring Companies

### Employer Panel
- Dashboard with company stats
- Post new jobs (with all required fields)
- Edit/delete own jobs
- View and manage applications (Accept / Reject / Mark Reviewed)
- Edit company profile

### Applicant Panel
- Dashboard with application stats
- Browse and search all active jobs
- Filter by category and job type
- View detailed job information
- Apply for jobs with cover letter
- Track application status
- Withdraw pending applications
- Edit personal profile

---

## Database Design

### Tables
1. **admin** — System administrators
2. **employer** — Hiring companies
3. **applicant** — Job seekers
4. **jobs** — Job listings (FK → employer)
5. **applications** — Job applications (FK → jobs, applicant)

### Views
- `active_jobs_view` — Active jobs with company info (JOIN)
- `application_details_view` — Applications with full applicant & job details (JOIN)

### Stored Procedures
- `ApplyForJob(job_id, applicant_id, cover_letter)` — Handles application logic
- `UpdateApplicationStatus(application_id, status)` — Updates status

### Indexes
- `idx_applicant_email` — Fast email lookups
- `idx_employer_email` — Fast email lookups
- `idx_jobs_title` — Fast job search
- `idx_jobs_category` — Fast category filter
- `idx_jobs_location` — Fast location filter

### Constraints
- PRIMARY KEY on all tables
- FOREIGN KEY with CASCADE DELETE
- UNIQUE on (job_id, applicant_id) in applications — prevents duplicate applications
- NOT NULL on required fields
- DEFAULT values for status fields
- ENUM for job_type and application status

---

## SQL Concepts Demonstrated (for presentation)

| Concept           | Where Used |
|-------------------|-----------|
| DDL (CREATE, ALTER) | jobportal.sql |
| DML (INSERT, UPDATE, DELETE, SELECT) | All modules |
| JOINs (INNER JOIN) | Views, all panels |
| GROUP BY + Aggregate | Reports section |
| ORDER BY | All table queries |
| LIKE operator | Search functionality |
| Subqueries | Statistics queries |
| Views | active_jobs_view, application_details_view |
| Stored Procedures | ApplyForJob, UpdateApplicationStatus |
| Indexes | On email, title, category, location |
| Constraints | PK, FK, UNIQUE, NOT NULL, DEFAULT |
| ENUM | job_type, application status |

---

## Normalization (for presentation)

- **UNF → 1NF**: All attributes are atomic (no repeating groups)
- **1NF → 2NF**: No partial dependencies (all non-key attributes depend on full PK)
- **2NF → 3NF**: No transitive dependencies (company info in employer table, not repeated in jobs)

---

## Presentation Demo Flow

1. Show Login Screen → Select role buttons
2. Login as **Employer** (techcorp / pass123)
   - Show Dashboard stats
   - Post a new Job
   - View Applications → Accept one
3. Login as **Applicant** (ali_dev / pass123)
   - Browse Jobs → search / filter
   - Double-click job to see details
   - Apply for a job with cover letter
   - View My Applications
4. Login as **Admin** (admin / admin123)
   - Show Dashboard overview
   - Browse Applicants / Employers
   - Show Reports

---

*Project by: [Your Name] | Course: Database Systems | Semester: 4th*
