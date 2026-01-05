#!/bin/bash

echo "========================================"
echo " TRY-TO-CHEAT-IF-YOU-DARE - STARTUP"
echo "========================================"

echo ""
echo "Installing dependencies for cheat detection..."
pip3 install opencv-python fastapi uvicorn websockets pillow numpy scikit-learn python-multipart aiofiles requests

echo ""
echo "Starting cheat detection backend server..."
python3 backend/app/main.py &
BACKEND_PID=$!

echo ""
echo "Waiting for backend to initialize..."
sleep 5

echo ""
echo "Starting frontend web interface..."
cd frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "Waiting for servers to start..."
sleep 3

echo ""
echo "========================================"
echo " CHEAT DETECTION SYSTEM READY!"
echo "========================================"
echo ""
echo "Web Demo: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Challenge: Try to cheat if you dare!"
echo ""

# Try to open browser (works on most systems)
if command -v open > /dev/null; then
    echo "Opening web browser..."
    open http://localhost:3000
elif command -v xdg-open > /dev/null; then
    echo "Opening web browser..."
    xdg-open http://localhost:3000
else
    echo "Please open http://localhost:3000 in your browser"
fi

echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for user to stop
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait