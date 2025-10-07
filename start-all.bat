@echo off
echo Starting Frontend and Backend...
echo.
start "Frontend" cmd /k "cd frontend && npm install && npm run dev"
start "Backend" cmd /k "cd backend && pip install -r requirements.txt && python app.py"
echo.
echo Both servers are starting in separate windows...
