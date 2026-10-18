# Deploy Academix to Render (college-demo setup)

This guide prepares the current Django project for Render + managed PostgreSQL. It is a **demo deployment guide**, not a claim that the application has had an independent production-security audit. Render deploys code from a Git repository, so migrations must be generated locally and committed before the first deployment.

## Before you start

- The project runs on your computer using the current `setup_windows.ps1` script.
- Git and a GitHub account are available.
- You can sign in to Render and authorize access to the repository.
- Keep `.env`, database passwords and all secret values out of GitHub.

## 1. Generate and test the migrations on Windows

Open the `Deployment Academix` folder in VS Code. If the local setup is still running, stop the server with `Ctrl+C` in its terminal. Use PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\prepare_deploy.ps1
```

This checks Django, generates initial migration files, applies them to your local configured database, runs the `common` regression tests and verifies there are no uncommitted model changes. Fix any reported errors before continuing. The migration files generated under each app's `migrations` directory are essential; **do not skip committing them**.

> If your local PostgreSQL database still has the earlier migration-history problem, fix the local setup first or configure `.env` to point to a fresh local development database. Do not use your production database as a test database.

## 2. Put the project in GitHub

Create a new GitHub repository for the submission. Upload the **contents** of this `Deployment Academix` folder to the repository root—not a second nested `Deployment Academix` folder. From a PowerShell terminal opened at the project root, you can use:

```powershell
git init
git add .
git status
git commit -m "Prepare Academix for deployment"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```

Replace the remote URL with your repository. If the repository already exists and has a remote, do not run `git init` or add a second `origin`; use `git add`, `git commit` and `git push` normally. Before committing, make sure `.env` is not listed by `git status` and ensure all generated `*/migrations/*.py` files are listed.

## 3. Create the Render deployment

1. Sign in at <https://dashboard.render.com/>.
2. Choose **New → Blueprint** (the wording may change) and connect your GitHub repository.
3. Render reads `render.yaml` in the repository root. Review the services, region and currently available plans, then apply the Blueprint.
4. Wait for the PostgreSQL database and web service to finish provisioning. The build installs requirements, checks the Django project, applies committed migrations and collects static files.
5. Open the web service URL ending in `.onrender.com` and try the login page.

If you use a custom domain, add it to `DJANGO_ALLOWED_HOSTS` and add its HTTPS origin to `DJANGO_CSRF_TRUSTED_ORIGINS` in the Render Environment settings.

The Blueprint currently uses Render's free plan values as a low-cost demonstration starting point. Check Render's current plan availability, resource limits, free-service sleeping behavior and database retention before you rely on it for a presentation or any real data. If a free database plan is unavailable, choose a currently supported paid plan in the Blueprint or Render dashboard.

## 4. Demo accounts (only for a temporary college demo)

For safer defaults, the Blueprint sets `ACADEMIX_SEED_DEMO_DATA=false` and does **not** create public demo accounts automatically.

If you need the supplied demo users for a short presentation:

1. In the Render web service, open **Environment** and set `ACADEMIX_SEED_DEMO_DATA=true`.
2. Save and deploy. During the build, the seed command creates/refreshes the demo users and sample records.
3. After the deployment succeeds, immediately set `ACADEMIX_SEED_DEMO_DATA=false` and redeploy. Existing demo accounts remain, but future deploys will not reset their passwords.
4. Use only for the demonstration; remove or change public demo credentials before sharing the site more broadly. Never use demo accounts with real student data.

Demo credentials seeded by the project:

| Role | Username | Password |
|---|---|---|
| Admin | `admin_demo` | `Admin123` |
| Teacher | `teacher_demo` | `Teacher123` |
| Student | `student_demo` | `Student123` |
| Parent | `parent_demo` | `Parent123` |

These are intentionally simple for a class demo and are not secure production credentials.

## 5. Verify the deployed app

Use this checklist before presenting:

- `/login/` loads over HTTPS and static CSS is visible.
- Log in separately as Admin, Teacher, Student and Parent; confirm each role sees its own dashboard.
- As Teacher, create a course, add a lesson and publish it.
- As Student, confirm the published course appears and a lesson can be marked complete.
- Test homework creation/submission/review and attendance marking/viewing.
- As Parent, confirm the dashboard only exposes a linked child's records.
- Check a nonexistent route and unauthorized route handling.
- Review Render service logs for errors after each workflow.

## Important limits before real production use

- **Uploaded media persistence:** the current app stores uploads on the local filesystem. Render web filesystems are not a durable media store across redeploys/restarts. For lasting homework attachments, videos, images and PDFs, connect persistent/object storage (for example S3-compatible storage or Cloudinary) and test access permissions first. Use external video/document URLs for a short demo if you have not configured object storage.
- **Feature scope:** the README identifies unfinished timed-exam/question-authoring, payment processing, some announcement/leave-request CRUD, password-reset email and PDF report export. Do not present these as complete.
- **Student privacy/security:** before real student information, carry out a security and privacy review, configure durable backups, mail delivery, upload type/size limits, monitoring, data retention, and review all authorization paths. Avoid public demo credentials.
- **No live-host verification here:** the container cannot install dependencies from the package index, so this guide and deployment files have not been verified by an actual Render build. Treat the first deployment as a test deployment and check the build logs.

## Useful commands

Local checks:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test common
.\.venv\Scripts\python.exe manage.py check --deploy
```

The last command checks production security settings. Run it with production-like environment variables; local development settings may produce warnings by design.
