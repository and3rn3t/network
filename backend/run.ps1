# Run the FastAPI backend server

Write-Host "Starting UniFi Network Monitor API..." -ForegroundColor Green

# Check if virtual environment exists
if (!(Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

# Install dependencies if needed
if (!(Test-Path ".venv\Lib\site-packages\fastapi")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Check if .env exists
if (!(Test-Path ".env")) {
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please edit .env file with your configuration" -ForegroundColor Red
}

# Run the server
Write-Host "`nStarting FastAPI server..." -ForegroundColor Green
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API docs at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor Yellow

python src/main.py
