$ErrorActionPreference = 'Stop'
Write-Host "DeepGuard AI - Windows setup" -ForegroundColor Cyan

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Warning "FFmpeg is not installed. Video+audio analysis will use visual-only mode. Install FFmpeg and add it to PATH."
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.11+ is required. Install Python and ensure it is available as 'python'."
}

python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
& .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
& .\.venv\Scripts\python.exe -m pip install -r frontend\requirements.txt

if (-not (Test-Path "backend\.env")) {
    @"
DATABASE_URL=mysql+pymysql://deepguard_app:YOUR_URL_ENCODED_PASSWORD@localhost:3306/deepguard
"@ | Set-Content "backend\.env"
    Write-Host "Created backend\.env. Set DATABASE_URL before starting the application." -ForegroundColor Yellow
}

Write-Host "Setup complete." -ForegroundColor Green
Write-Host "Start backend: .\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000"
Write-Host "Start frontend: .\.venv\Scripts\python.exe -m streamlit run frontend\app.py"
