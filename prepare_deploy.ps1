$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    throw 'Local .venv was not found. Run setup_windows.ps1 once first, then stop the local server with Ctrl+C.'
}
Write-Host '1/5 Checking Django configuration...' -ForegroundColor Cyan
& $python manage.py check
if ($LASTEXITCODE -ne 0) { throw 'Django check failed.' }
Write-Host '2/5 Generating initial migration files...' -ForegroundColor Cyan
& $python manage.py makemigrations accounts academics lessons homework exams attendance timetable fees notifications administration
if ($LASTEXITCODE -ne 0) { throw 'Could not create migrations. Do not deploy until this is resolved.' }
Write-Host '3/5 Applying local migrations...' -ForegroundColor Cyan
& $python manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) { throw 'Migration failed. Do not deploy until this is resolved.' }
Write-Host '4/5 Running regression tests...' -ForegroundColor Cyan
& $python manage.py test common
if ($LASTEXITCODE -ne 0) { throw 'Tests failed. Review the output before deployment.' }
Write-Host '5/5 Checking migration files are up to date...' -ForegroundColor Cyan
& $python manage.py makemigrations --check --dry-run
if ($LASTEXITCODE -ne 0) { throw 'Migrations are not up to date.' }
Write-Host ''
Write-Host 'Pre-deployment checks passed.' -ForegroundColor Green
Write-Host 'IMPORTANT: add and commit all generated */migrations/0001_initial.py files to GitHub.' -ForegroundColor Yellow
Write-Host 'Do NOT commit .env, database passwords, media uploads, or .venv.' -ForegroundColor Yellow
Write-Host 'Next: push this project folder to GitHub, then use render.yaml as a Render Blueprint.' -ForegroundColor Cyan
