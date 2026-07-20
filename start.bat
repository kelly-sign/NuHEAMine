@echo off
setlocal
set "ROOT=%~dp0"

if not exist "%ROOT%.env" (
  echo Missing .env. Copy .env.example to .env and configure it first.
  exit /b 1
)

if not exist "%ROOT%.venv\Scripts\python.exe" (
  echo Missing .venv. Create the Python 3.8 environment and install requirements.txt first.
  exit /b 1
)

if not exist "%ROOT%node_modules\.bin\vue-cli-service.cmd" (
  echo Missing node_modules. Run npm ci first.
  exit /b 1
)

start "NuHEAMine backend" /D "%ROOT%" cmd /k ""%ROOT%.venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000"
start "NuHEAMine frontend" /D "%ROOT%" cmd /k "npm run serve"

echo Backend and frontend terminals started.
echo Open http://localhost:8080 after both services are ready.

