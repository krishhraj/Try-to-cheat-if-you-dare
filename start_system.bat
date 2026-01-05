@echo off
echo ========================================
echo  TRY-TO-CHEAT-IF-YOU-DARE - STARTUP
echo ========================================

echo.
echo Installing dependencies for cheat detection...
pip install opencv-python fastapi uvicorn websockets pillow numpy scikit-learn python-multipart aiofiles requests

echo.
echo Starting cheat detection backend server...
start "Cheat Detection Backend" python backend/app/main.py

echo.
echo Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo.
echo Starting frontend web interface...
cd frontend
start "Frontend Server" python -m http.server 3000
cd ..

echo.
echo Waiting for servers to start...
timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo  CHEAT DETECTION SYSTEM READY!
echo ========================================
echo.
echo Web Demo: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Challenge: Try to cheat if you dare!
echo.
echo Opening web browser...
start http://localhost:3000

echo.
echo Press any key to close this window...
pause > nul