# 🎯 Setup Guide - Try-to-cheat-if-you-dare

## 📥 Quick Start (3 Methods)

### Method 1: Automatic Setup (Recommended)
```bash
git clone https://github.com//try-to-cheat-if-you-dare.git
cd try-to-cheat-if-you-dare
python setup.py
```

### Method 2: One-Click Scripts
**Windows:**
```bash
start_system.bat
```

**Mac/Linux:**
```bash
chmod +x start_system.sh
./start_system.sh
```

### Method 3: Docker (Production)
```bash
docker-compose up -d
```

---

## 🛠 Manual Installation

### Prerequisites
- Python 3.8+ (3.10+ recommended)
- Git
- Webcam (to try cheating in real-time)
- Modern web browser

### Step-by-Step Setup

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/try-to-cheat-if-you-dare.git
cd try-to-cheat-if-you-dare
```

2. **Create Virtual Environment (Recommended)**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Start Backend Server**
```bash
python backend/app/main.py
```
Wait for: "Cheat detector initialized successfully"

5. **Start Frontend Server** (New Terminal)
```bash
cd frontend
python -m http.server 3000
```

6. **Open Browser and Try to Cheat!**
```
http://localhost:3000
```

---

## 🎯 Verification

### Health Checks
- **Backend API**: http://localhost:8000/health
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

### Quick Test
```bash
python test_cheat_detection.py
```

---

## 🐛 Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'cv2'"**
```bash
pip install opencv-python-headless
```

**"Port already in use"**
```bash
# Kill existing processes
pkill -f python  # Mac/Linux
taskkill /f /im python.exe  # Windows
```

**Camera not working**
- Allow camera permissions in browser
- Use Chrome for best compatibility
- Close other apps using camera

---

## 🌐 Access Points

Once running:
- **🎥 Web Demo**: http://localhost:3000
- **📚 API Docs**: http://localhost:8000/docs
- **❤️ Health**: http://localhost:8000/health
- **📊 Stats**: http://localhost:8000/stats

---

## 🎮 Demo Features

### Real-Time Challenge
1. Click "Start Camera"
2. Allow permissions
3. Click "Start Detection"
4. Try to cheat if you dare!

### Upload Your Best Fake
1. Go to "Upload & Analyze"
2. Select your deepfake
3. Click "Analyze File"
4. See if you can fool our AI!

### API Testing
1. Visit `/docs` endpoint
2. Try interactive API
3. Test with sample data

---

## 🚀 Production Deployment

### Docker
```bash
# Build and run
docker build -t try-to-cheat-if-you-dare .
docker run -p 8000:8000 -p 3000:3000 try-to-cheat-if-you-dare

# Or use docker-compose
docker-compose up -d
```

### Cloud Platforms
- **Heroku**: `git push heroku main`
- **AWS**: Deploy to EC2/ECS
- **Google Cloud**: Use Cloud Run
- **Azure**: Deploy to App Service

---

## 📊 System Requirements

### Minimum
- Python 3.8+
- 2GB RAM
- 500MB storage
- Webcam (optional)

### Recommended
- Python 3.10+
- 4GB+ RAM
- Multi-core CPU
- Good lighting for camera

---

## 🔧 Configuration

### Environment Variables
```bash
export LOG_LEVEL=INFO
export API_HOST=0.0.0.0
export API_PORT=8000
export FRONTEND_PORT=3000
```

### Custom Ports
Edit `backend/app/main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

## 📈 Performance Tips

- Use virtual environment
- Close unnecessary apps
- Ensure good lighting
- Use Chrome browser
- Test with clear face images

---

## 🎯 Success Indicators

✅ Backend shows "initialized successfully"  
✅ Frontend loads at localhost:3000  
✅ Camera demo works  
✅ File upload produces results  
✅ API docs accessible  

**Ready to challenge our AI! 🎯**