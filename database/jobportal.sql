-- ============================================================
-- JOB PORTAL MANAGEMENT SYSTEM - DATABASE SETUP
-- Course: Database Systems | Technology: MySQL
-- ============================================================

CREATE DATABASE IF NOT EXISTS jobportal;
USE jobportal;

-- ============================================================
-- TABLE 1: ADMIN
-- ============================================================
CREATE TABLE IF NOT EXISTS admin (
    admin_id    INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    email       VARCHAR(100) NOT NULL UNIQUE,
    full_name   VARCHAR(100) NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE 2: EMPLOYER
-- ============================================================
CREATE TABLE IF NOT EXISTS employer (
    employer_id     INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50) NOT NULL UNIQUE,
    password        VARCHAR(255) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    company_name    VARCHAR(150) NOT NULL,
    industry        VARCHAR(100),
    location        VARCHAR(150),
    phone           VARCHAR(20),
    website         VARCHAR(200),
    description     TEXT,
    is_active       TINYINT(1) DEFAULT 1,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE 3: APPLICANT
-- ============================================================
CREATE TABLE IF NOT EXISTS applicant (
    applicant_id    INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50) NOT NULL UNIQUE,
    password        VARCHAR(255) NOT NULL,
    email           VARCHAR(100) NOT NULL UNIQUE,
    full_name       VARCHAR(100) NOT NULL,
    phone           VARCHAR(20),
    location        VARCHAR(150),
    skills          TEXT,
    education       VARCHAR(200),
    experience_years INT DEFAULT 0,
    resume_path     VARCHAR(300),
    is_active       TINYINT(1) DEFAULT 1,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE 4: JOBS
-- ============================================================
CREATE TABLE IF NOT EXISTS jobs (
    job_id          INT AUTO_INCREMENT PRIMARY KEY,
    employer_id     INT NOT NULL,
    title           VARCHAR(200) NOT NULL,
    description     TEXT,
    salary          VARCHAR(100),
    location        VARCHAR(150),
    category        VARCHAR(100),
    job_type        ENUM('Full-Time','Part-Time','Remote','Contract','Internship') DEFAULT 'Full-Time',
    experience_req  VARCHAR(100),
    deadline        DATE,
    is_active       TINYINT(1) DEFAULT 1,
    posted_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_jobs_employer FOREIGN KEY (employer_id) REFERENCES employer(employer_id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE 5: APPLICATIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS applications (
    application_id  INT AUTO_INCREMENT PRIMARY KEY,
    job_id          INT NOT NULL,
    applicant_id    INT NOT NULL,
    cover_letter    TEXT,
    status          ENUM('Pending','Reviewed','Accepted','Rejected') DEFAULT 'Pending',
    applied_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_app_job       FOREIGN KEY (job_id)       REFERENCES jobs(job_id)           ON DELETE CASCADE,
    CONSTRAINT fk_app_applicant FOREIGN KEY (applicant_id) REFERENCES applicant(applicant_id) ON DELETE CASCADE,
    CONSTRAINT uq_application   UNIQUE (job_id, applicant_id)
);

-- ============================================================
-- INDEXES (for performance)
-- ============================================================
CREATE INDEX idx_applicant_email ON applicant(email);
CREATE INDEX idx_employer_email  ON employer(email);
CREATE INDEX idx_jobs_title      ON jobs(title);
CREATE INDEX idx_jobs_category   ON jobs(category);
CREATE INDEX idx_jobs_location   ON jobs(location);

-- ============================================================
-- VIEW: Active Jobs with Company Info
-- ============================================================
CREATE OR REPLACE VIEW active_jobs_view AS
SELECT
    j.job_id,
    j.title,
    j.salary,
    j.location,
    j.category,
    j.job_type,
    j.experience_req,
    j.deadline,
    j.posted_at,
    e.company_name,
    e.industry,
    e.location AS company_location
FROM jobs j
JOIN employer e ON j.employer_id = e.employer_id
WHERE j.is_active = 1 AND j.deadline >= CURDATE();

-- ============================================================
-- VIEW: Application Details
-- ============================================================
CREATE OR REPLACE VIEW application_details_view AS
SELECT
    a.application_id,
    ap.full_name AS applicant_name,
    ap.email     AS applicant_email,
    ap.phone     AS applicant_phone,
    j.title      AS job_title,
    e.company_name,
    a.status,
    a.applied_at
FROM applications a
JOIN applicant ap ON a.applicant_id = ap.applicant_id
JOIN jobs j       ON a.job_id       = j.job_id
JOIN employer e   ON j.employer_id  = e.employer_id;

-- ============================================================
-- STORED PROCEDURE: Apply for Job
-- ============================================================
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS ApplyForJob(
    IN p_job_id       INT,
    IN p_applicant_id INT,
    IN p_cover_letter TEXT,
    OUT p_result      VARCHAR(100)
)
BEGIN
    DECLARE already_applied INT DEFAULT 0;
    DECLARE job_exists      INT DEFAULT 0;

    SELECT COUNT(*) INTO already_applied
    FROM applications
    WHERE job_id = p_job_id AND applicant_id = p_applicant_id;

    SELECT COUNT(*) INTO job_exists
    FROM jobs
    WHERE job_id = p_job_id AND is_active = 1;

    IF already_applied > 0 THEN
        SET p_result = 'ALREADY_APPLIED';
    ELSEIF job_exists = 0 THEN
        SET p_result = 'JOB_NOT_FOUND';
    ELSE
        INSERT INTO applications (job_id, applicant_id, cover_letter)
        VALUES (p_job_id, p_applicant_id, p_cover_letter);
        SET p_result = 'SUCCESS';
    END IF;
END //
DELIMITER ;

-- ============================================================
-- STORED PROCEDURE: Update Application Status
-- ============================================================
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS UpdateApplicationStatus(
    IN p_application_id INT,
    IN p_status         VARCHAR(20)
)
BEGIN
    UPDATE applications SET status = p_status WHERE application_id = p_application_id;
END //
DELIMITER ;

-- ============================================================
-- SAMPLE DATA
-- ============================================================
INSERT IGNORE INTO admin (username, password, email, full_name) VALUES
('admin', 'admin123', 'admin@jobportal.com', 'System Administrator');

INSERT IGNORE INTO employer (username, password, email, company_name, industry, location, phone, website, description) VALUES
('techcorp', 'pass123', 'hr@techcorp.com', 'TechCorp Solutions', 'Information Technology', 'Lahore, Pakistan', '0300-1234567', 'www.techcorp.com', 'Leading software house in Pakistan'),
('nexagen',  'pass123', 'jobs@nexagen.pk', 'NexaGen Systems',   'Software Development',  'Karachi, Pakistan','0321-9876543', 'www.nexagen.pk',  'Innovative tech startup building next-gen solutions');

INSERT IGNORE INTO applicant (username, password, email, full_name, phone, location, skills, education, experience_years) VALUES
('ali_dev',  'pass123', 'ali@gmail.com',   'Ali Hassan',   '0300-1111111', 'Lahore',  'Python, MySQL, Django',       'BSCS - UET Lahore',   2),
('sara_qa',  'pass123', 'sara@gmail.com',  'Sara Ahmed',   '0311-2222222', 'Karachi', 'Testing, Selenium, SQL',      'BSSE - FAST Karachi', 1),
('usman_ml', 'pass123', 'usman@gmail.com', 'Usman Tariq',  '0333-3333333', 'Islamabad','ML, TensorFlow, Python',     'MSCS - NUST',         3);

INSERT IGNORE INTO jobs (employer_id, title, description, salary, location, category, job_type, experience_req, deadline) VALUES
(1, 'Python Developer',      'Build scalable backend systems using Django and REST APIs.',  '80,000 - 120,000 PKR', 'Lahore',    'Software Development', 'Full-Time',  '1-2 years', DATE_ADD(CURDATE(), INTERVAL 30 DAY)),
(1, 'Database Administrator','Manage and optimize MySQL and PostgreSQL databases.',           '90,000 - 130,000 PKR', 'Lahore',    'Database',             'Full-Time',  '2-3 years', DATE_ADD(CURDATE(), INTERVAL 25 DAY)),
(2, 'ML Engineer',           'Develop machine learning models and deploy to production.',    '100,000-150,000 PKR',  'Remote',    'Artificial Intelligence','Remote',   '2-4 years', DATE_ADD(CURDATE(), INTERVAL 45 DAY)),
(2, 'QA Engineer',           'Test web and mobile applications, write test cases.',          '60,000 - 90,000 PKR',  'Karachi',   'Quality Assurance',    'Full-Time',  '1-2 years', DATE_ADD(CURDATE(), INTERVAL 20 DAY)),
(1, 'Frontend Developer',    'Build responsive UIs with React and modern CSS frameworks.',  '70,000 - 110,000 PKR', 'Lahore',    'Web Development',      'Full-Time',  '1-3 years', DATE_ADD(CURDATE(), INTERVAL 35 DAY));

INSERT IGNORE INTO applications (job_id, applicant_id, cover_letter, status) VALUES
(1, 1, 'I am a Python developer with 2 years of experience and would love to join TechCorp.', 'Pending'),
(3, 3, 'My ML expertise aligns perfectly with this role.', 'Reviewed'),
(4, 2, 'QA is my passion and I have strong Selenium skills.', 'Accepted');

SELECT 'Database setup complete!' AS message;
