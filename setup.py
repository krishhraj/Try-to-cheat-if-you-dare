#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Setup Script for Try-to-cheat-if-you-dare
Run this to automatically set up and test the cheat detection system
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def print_step(step, message):
    print(f"\n{'='*50}")
    print(f"STEP {step}: {message}")
    print(f"{'='*50}")

def run_command(command, description):
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def check_python():
    print_step(1, "Checking Python Installation")
    
    # Check Python version
    try:
        version = sys.version_info
        print(f"Python version: {version.major}.{version.minor}.{version.micro}")
        if version.major >= 3 and version.minor >= 8:
            print("✅ Python version is compatible")
            return True
        else:
            print("❌ Python 3.8+ required")
            return False
    except:
        print("❌ Python not found")
        return False

def install_dependencies():
    print_step(2, "Installing Dependencies for Cheat Detection")
    
    packages = [
        "opencv-python",
        "fastapi",
        "uvicorn",
        "websockets", 
        "pillow",
        "numpy",
        "scikit-learn",
        "python-multipart",
        "aiofiles",
        "requests"
    ]
    
    print("Installing required packages for cheat detection...")
    for package in packages:
        print(f"Installing {package}...")
        success = run_command(f"pip install {package}", f"Install {package}")
        if not success:
            print(f"⚠️  Failed to install {package}, trying alternative...")
            if package == "opencv-python":
                run_command("pip install opencv-python-headless", "Install opencv-python-headless")

def check_project_structure():
    print_step(3, "Checking Project Structure")
    
    required_files = [
        "backend/models/cheat_detector.py",
        "backend/app/main.py", 
        "frontend/index.html"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nPlease ensure all project files are in the correct locations.")
        return False
    else:
        print("✅ All required files found")
        return True

def start_backend():
    print_step(4, "Starting Cheat Detection Backend Server")
    
    print("Starting FastAPI cheat detection server...")
    print("This will run in the background...")
    
    # Start backend in background
    try:
        if os.name == 'nt':  # Windows
            subprocess.Popen([sys.executable, "backend/app/main.py"], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Unix/Linux/Mac
            subprocess.Popen([sys.executable, "backend/app/main.py"])
        
        print("⏳ Waiting for cheat detection backend to start...")
        time.sleep(5)
        
        # Test if backend is running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Cheat detection backend server is running!")
                print("   API available at: http://localhost:8000")
                print("   API docs at: http://localhost:8000/docs")
                return True
            else:
                print("❌ Backend server not responding correctly")
                return False
        except:
            print("❌ Cannot connect to backend server")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_frontend():
    print_step(5, "Starting Frontend Web Interface")
    
    print("Starting frontend web server...")
    
    try:
        os.chdir("frontend")
        if os.name == 'nt':  # Windows
            subprocess.Popen([sys.executable, "-m", "http.server", "3000"],
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Unix/Linux/Mac
            subprocess.Popen([sys.executable, "-m", "http.server", "3000"])
        
        os.chdir("..")  # Go back to project root
        
        print("⏳ Waiting for frontend to start...")
        time.sleep(3)
        
        # Test if frontend is running
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            if response.status_code == 200:
                print("✅ Frontend server is running!")
                print("   Web interface at: http://localhost:3000")
                return True
            else:
                print("❌ Frontend server not responding")
                return False
        except:
            print("❌ Cannot connect to frontend server")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def run_tests():
    print_step(6, "Running Cheat Detection System Tests")
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: API Health
    print("Test 1: API Health Check")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health: {data.get('status', 'unknown')}")
            tests_passed += 1
        else:
            print("❌ API health check failed")
    except:
        print("❌ Cannot reach API")
    
    # Test 2: Frontend Access
    print("Test 2: Frontend Access")
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("✅ Frontend accessible")
            tests_passed += 1
        else:
            print("❌ Frontend not accessible")
    except:
        print("❌ Cannot reach frontend")
    
    # Test 3: Detection System
    print("Test 3: Cheat Detection System")
    try:
        # Create a simple test image
        import numpy as np
        import cv2
        from io import BytesIO
        
        # Create test image
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        _, buffer = cv2.imencode('.jpg', test_image)
        
        files = {'file': ('test.jpg', BytesIO(buffer.tobytes()), 'image/jpeg')}
        response = requests.post("http://localhost:8000/detect/image", files=files)
        
        if response.status_code == 200:
            print("✅ Cheat detection system working")
            tests_passed += 1
        else:
            print("❌ Cheat detection system failed")
    except Exception as e:
        print(f"❌ Detection test failed: {e}")
    
    print(f"\nTests passed: {tests_passed}/{total_tests}")
    return tests_passed == total_tests

def print_success_message():
    print("\n" + "🎯" * 50)
    print("SUCCESS! Your Try-to-cheat-if-you-dare System is running!")
    print("🎯" * 50)
    
    print("\n📱 Access Your Cheat Detection System:")
    print("   🌐 Web Demo: http://localhost:3000")
    print("   📚 API Docs: http://localhost:8000/docs") 
    print("   ❤️  Health Check: http://localhost:8000/health")
    
    print("\n🎯 What to do next:")
    print("   1. Open http://localhost:3000 in your browser")
    print("   2. Click 'Start Camera' and allow permissions")
    print("   3. Click 'Start Detection' and try to cheat!")
    print("   4. Try uploading deepfakes in the 'Upload & Analyze' tab")
    print("   5. Check out the API documentation")
    
    print("\n🚀 Perfect for your internship portfolio!")
    print("   • Real-time AI cheat detection ✅")
    print("   • Full-stack implementation ✅") 
    print("   • Production-ready API ✅")
    print("   • Interactive challenge demo ✅")
    print("   • Catchy project name ✅")

def main():
    print("🎯 TRY-TO-CHEAT-IF-YOU-DARE - QUICK SETUP")
    print("This script will set up your cheat detection system automatically!")
    
    # Run setup steps
    if not check_python():
        print("❌ Setup failed: Python requirements not met")
        return
    
    install_dependencies()
    
    if not check_project_structure():
        print("❌ Setup failed: Missing project files")
        return
    
    if not start_backend():
        print("❌ Setup failed: Backend server issues")
        return
    
    if not start_frontend():
        print("❌ Setup failed: Frontend server issues")
        return
    
    if run_tests():
        print_success_message()
    else:
        print("⚠️  Setup completed but some tests failed")
        print("The system should still work - try opening http://localhost:3000")

if __name__ == "__main__":
    main()