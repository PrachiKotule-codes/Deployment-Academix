# ACADEMIX — Learn. Grow. Achieve.

> **Deployment:** See [`DEPLOY_RENDER_GUIDE.md`](DEPLOY_RENDER_GUIDE.md) for the Windows migration-preparation step, GitHub setup, and Render + PostgreSQL deployment. The project archive does not include generated initial migration files; run `prepare_deploy.ps1` and commit the generated migrations before deploying. `render.yaml` defaults demo-user seeding off.

Django academic portal MVP with distinct Admin, Teacher, Student and Parent workspaces. The application uses PostgreSQL for the intended local project setup, Django authentication, role-based route checks, server-side record filtering, and a shared ERP-inspired Inter UI (navy sidebar, slim top bar, soft-grey workspace, white panels and pastel status states).

## What is wired in this version

- **Accounts & roles:** sign in, role-aware dashboard/navigation, self-signup as Student/Teacher/Parent, Admin account creation and role assignment. The demo seeder creates and refreshes reliable logins.
- **Courses:** teacher-owned course creation/editing, subject/class/module information, draft/published state and student/parent visibility of published courses.
- **Lessons:** create/edit lessons, order/section, video URL or uploaded video, study PDF/file/external URL, mindmap link and quick recap. Students can mark a lesson complete; course progress is calculated from completed lessons.
- **Homework:** teacher creates course assignments and due dates; student submits text/files; teacher reviews work with marks/feedback; students and linked parents can see submission/feedback status; notification entries are created for new homework/reviews.
- **Attendance:** teacher/admin can mark Present/Absent/Leave; students see only their own records; parents see records for linked children; absence creates notifications for the student and linked parent.
- **Timetable:** view schedule based on role and class; teacher/admin can add entries.
- **Fees:** students/parents see relevant fee amounts and outstanding balances; Admin can create fee records and record payments.
- **Tests:** teachers/admin can create test shells and students can view available tests. Question authoring and taking timed exams are not yet part of this deadline MVP.
- **Reports:** graded homework and submitted test-attempt summaries are role-filtered.
- **Parent monitoring:** linked-child progress, attendance and homework summary; parent-facing pages filter data to linked children/class.
- **Notifications and announcements:** notification inbox with mark-as-read and role-targeted announcement list.
- **Administration:** manage user accounts and roles; separate institution overview; student/teacher/parent directory pages.

## Windows + PostgreSQL setup (recommended)

**Use a fresh database named `academix_submission` for this updated version. Do not reuse the old `academix_db` database because it previously had inconsistent migration history.** The setup SQL checks whether the new database already exists and does not delete it.

1. Start PostgreSQL and open this folder in VS Code.
2. In a PowerShell terminal, create/prepare the local database. This script uses the simple local database password `ADMIN` for `academix_user` to match `.env.example`:
   ```powershell
   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -h 127.0.0.1 -d postgres -W -f setup_postgres.sql
   ```
   If your PostgreSQL is installed in a different folder/version, adjust only the path to `psql.exe`.
3. Make the project environment file from the provided local defaults (this replaces the old `.env` in this project folder, so use it only in the newly extracted project):
   ```powershell
   Copy-Item -Force .env.example .env
   ```
4. Run the setup script. It creates `.venv` if needed, installs dependencies, creates the initial Django migrations, migrates the fresh database and seeds demo data:
   ```powershell
   Set-ExecutionPolicy -Scope Process Bypass
   .\setup_windows.ps1
   ```
   If you prefer manual commands:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python manage.py makemigrations accounts academics lessons homework exams attendance timetable fees notifications administration
   python manage.py migrate
   python manage.py seed_demo
   python manage.py runserver
   ```
5. Open `http://127.0.0.1:8000/`.
6. Optional smoke/regression tests after setup: `python manage.py test common`.

### Demo logins (local testing only)

| Role | Username | Password |
|---|---|---|
| Admin | `admin_demo` | `Admin123` |
| Teacher | `teacher_demo` | `Teacher123` |
| Student | `student_demo` | `Student123` |
| Parent | `parent_demo` | `Parent123` |

Extra demo accounts are also created: `teacher2` to `teacher5` use `Teacher123`; `student2` to `student10` use `Student123`; `parent2` to `parent10` use `Parent123`. Each demo parent is linked to one demo student. Running `python manage.py seed_demo` again resets these demo passwords to the values above and adds any missing sample records; do not use this behavior for live accounts.

## Role behavior

- **Admin:** institution overview, accounts and role setup, directories, all courses, fee records, attendance and academic reporting.
- **Teacher:** teacher-specific dashboard, own course creation and lesson management, homework create/review, assigned class student list, attendance marking, timetable and reports.
- **Student:** published courses/lessons, lesson completion/progress, homework submission/feedback, attendance, timetable, fees, tests and results.
- **Parent:** linked child's course/progress summary, homework, attendance, timetable, fees, reports and notifications. Parent visibility depends on a valid student link.

## Folder structure

- `config/` — settings, URL routing, forms, role-aware views and context processor.
- `accounts/` — user profiles, roles, authentication signals and demo data command.
- `academics/` — subjects and courses.
- `lessons/` — lessons, study materials and progress.
- `homework/` — assignments and submissions/feedback.
- `attendance/` — attendance records and leave request model.
- `exams/` — test, question and attempt models.
- `timetable/` — class schedule.
- `fees/` — fee/payment records.
- `notifications/` — notifications and announcements.
- `administration/` — audit-log model.
- `students/`, `Teachers/`, `Parents/`, `common/` — retained role/common app packages.
- `templates/` — role-specific dashboards and module pages.
- `REQUIREMENTS_WORKFLOW.md` — role-wise workflow and submission verification checklist.
- `static/` — CSS and JavaScript.
- `setup_postgres.sql`, `setup_windows.ps1` — local setup helpers.

## Scope and safety note

This is a **submission-oriented MVP**, not a fully audited school production system. The core navigation and workflow paths are implemented, but exam question authoring/timed test taking, payment processing, full CRUD for announcements/leave requests, password reset email, report PDF export (a CSV export is available), real upload security policies, and production deployment hardening remain incomplete. Before using real student data, change demo passwords/secret key, configure HTTPS, secure media storage and upload limits, backups, allowed hosts, monitoring and a privacy/security review. Never deploy the demo credentials.
