@echo off
echo 🚀 Jira Management Dashboard - Windows Quick Start
echo ================================================

echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt

echo.
echo 🎯 Starting servers...
echo.
echo 📝 Note: Two command windows will open
echo    1. Backend server (Terminal 1)
echo    2. Frontend server (Terminal 2)
echo.

echo 🚀 Starting backend server...
start "Jira Dashboard Backend" cmd /k "python start_backend.py"

echo ⏳ Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak > nul

echo 🎨 Starting frontend server...
start "Jira Dashboard Frontend" cmd /k "python start_frontend.py"

echo.
echo 🌐 Opening dashboard in browser...
timeout /t 5 /nobreak > nul
start http://localhost:8501

echo.
echo ✅ Servers are starting up!
echo 📍 Backend: http://localhost:8000
echo 📍 Frontend: http://localhost:8501
echo.
echo Press any key to exit this launcher...
pause > nul 