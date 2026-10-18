$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

if (-not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
    Write-Host 'Created .env from .env.example.' -ForegroundColor Cyan
} else {
    Write-Host 'Using your existing .env file.' -ForegroundColor Yellow
}

if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -3 -m venv .venv
}
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed. Check internet access and requirements.txt.' }

& $python manage.py makemigrations accounts academics lessons homework exams attendance timetable fees notifications administration
if ($LASTEXITCODE -ne 0) { throw 'makemigrations failed. Keep the terminal output and ask for help.' }
& $python manage.py migrate
if ($LASTEXITCODE -ne 0) { throw 'Database migration failed. Confirm PostgreSQL is running and DATABASE_URL in .env is correct.' }
& $python manage.py seed_demo
if ($LASTEXITCODE -ne 0) { throw 'Demo data setup failed. Keep the terminal output and ask for help.' }
Write-Host ''
Write-Host 'ACADEMIX setup complete. Run: .\.venv\Scripts\python.exe manage.py runserver' -ForegroundColor Green
Write-Host 'Opening http://127.0.0.1:8000/ — stop server with Ctrl+C.' -ForegroundColor Green
& $python manage.py runserver
