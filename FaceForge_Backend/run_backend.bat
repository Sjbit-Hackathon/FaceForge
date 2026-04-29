@echo off
echo Stopping existing uvicorn processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM uvicorn.exe /T >nul 2>&1

echo.
echo Installing dependencies with numpy fix...
call .\venv\Scripts\activate
pip install -r requirements.txt

echo.
echo Starting FaceForge Backend...
echo Server will be available at http://127.0.0.1:8000
echo.
uvicorn app.main:app --reload
pause
