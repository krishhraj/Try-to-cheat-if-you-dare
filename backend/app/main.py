"""
Try-to-cheat-if-you-dare - FastAPI Backend

Main API server that dares users to try cheating with deepfakes and manipulation.
Provides REST endpoints and WebSocket support for real-time cheat detection.
"""

from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import cv2
import numpy as np
from PIL import Image
import io
import logging
import asyncio
import json
import base64
from typing import Dict, Any
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.cheat_detector import get_detector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Try-to-cheat-if-you-dare API",
    description="Advanced AI system that dares you to try cheating with deepfakes. Real-time detection using cutting-edge computer vision and machine learning.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            self.disconnect(websocket)

manager = ConnectionManager()

# Initialize detector
detector = get_detector()

@app.get("/")
async def root():
    """Welcome message for the cheat detection API."""
    return {
        "message": "Welcome to Try-to-cheat-if-you-dare API!",
        "description": "Think you can fool our AI? Try uploading a deepfake and see what happens!",
        "endpoints": {
            "health": "/health",
            "detect_image": "/detect/image",
            "detect_video": "/detect/video", 
            "stats": "/stats",
            "docs": "/docs"
        },
        "challenge": "We dare you to try cheating! 🎯"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "detector_ready": True,
        "message": "Cheat detection system is ready to catch your attempts!",
        "stats": detector.get_stats()
    }

@app.post("/detect/image")
async def detect_image_cheating(file: UploadFile = File(...)):
    """
    Detect cheating in uploaded image.
    
    Upload your best deepfake and see if you can fool our AI!
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert to numpy array
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        elif image.mode == 'L':
            image = image.convert('RGB')
        
        image_array = np.array(image)
        image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        # Detect cheating
        results = detector.detect_cheating(image_bgr)
        
        # Add file info
        results.update({
            "filename": file.filename,
            "file_size": len(contents),
            "image_dimensions": f"{image_array.shape[1]}x{image_array.shape[0]}",
            "processing_status": "completed"
        })
        
        logger.info(f"Processed image: {file.filename}, Cheating detected: {results['is_cheating']}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/detect/video")
async def detect_video_cheating(file: UploadFile = File(...)):
    """
    Detect cheating in uploaded video.
    
    Upload a video with deepfakes and see if our AI can catch your manipulation!
    """
    try:
        # Validate file type
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Save uploaded file temporarily
        contents = await file.read()
        temp_path = f"/tmp/{file.filename}"
        
        with open(temp_path, "wb") as f:
            f.write(contents)
        
        # Process video
        cap = cv2.VideoCapture(temp_path)
        frame_results = []
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Sample frames (every 30th frame to avoid processing too many)
        sample_rate = max(1, total_frames // 10)  # Sample 10 frames max
        
        while cap.isOpened() and frame_count < total_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % sample_rate == 0:
                # Detect cheating in this frame
                results = detector.detect_cheating(frame)
                frame_results.append({
                    "frame_number": frame_count,
                    "timestamp": frame_count / cap.get(cv2.CAP_PROP_FPS),
                    "is_cheating": results["is_cheating"],
                    "confidence": results["confidence"],
                    "faces_detected": results["faces_detected"]
                })
            
            frame_count += 1
        
        cap.release()
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        # Aggregate results
        total_cheating_frames = sum(1 for r in frame_results if r["is_cheating"])
        avg_confidence = np.mean([r["confidence"] for r in frame_results]) if frame_results else 0.0
        
        overall_results = {
            "filename": file.filename,
            "file_size": len(contents),
            "total_frames": total_frames,
            "frames_analyzed": len(frame_results),
            "cheating_frames": total_cheating_frames,
            "cheating_percentage": (total_cheating_frames / len(frame_results)) * 100 if frame_results else 0,
            "average_confidence": float(avg_confidence),
            "is_cheating": total_cheating_frames > 0,
            "frame_results": frame_results[:5],  # Return first 5 frame results
            "message": "Video analysis complete - check the results!",
            "processing_status": "completed"
        }
        
        logger.info(f"Processed video: {file.filename}, Cheating frames: {total_cheating_frames}/{len(frame_results)}")
        
        return overall_results
        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")

@app.get("/stats")
async def get_detection_stats():
    """Get cheat detection statistics."""
    stats = detector.get_stats()
    stats.update({
        "api_status": "active",
        "challenge_message": "Think you can beat our detection rate? Try uploading more content!",
        "leaderboard_message": f"Current success rate: {stats['success_rate']} - Can you lower it?"
    })
    return stats

@app.post("/configure")
async def configure_detector(config: dict):
    """Configure detector settings."""
    try:
        if "confidence_threshold" in config:
            threshold = float(config["confidence_threshold"])
            detector.update_threshold(threshold)
            return {
                "status": "success",
                "message": f"Confidence threshold updated to {threshold}",
                "new_settings": detector.get_stats()
            }
        else:
            raise HTTPException(status_code=400, detail="No valid configuration provided")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Configuration error: {str(e)}")

@app.websocket("/ws/detect")
async def websocket_detect(websocket: WebSocket):
    """
    WebSocket endpoint for real-time cheat detection.
    
    Send base64 encoded images and get real-time cheat detection results!
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive data from client
            data = await websocket.receive_text()
            
            try:
                # Parse JSON data
                message = json.loads(data)
                
                if message.get("type") == "frame":
                    # Decode base64 image
                    image_data = base64.b64decode(message["data"].split(",")[1])
                    image = Image.open(io.BytesIO(image_data))
                    
                    # Convert to numpy array
                    if image.mode == 'RGBA':
                        image = image.convert('RGB')
                    
                    image_array = np.array(image)
                    image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                    
                    # Detect cheating
                    results = detector.detect_cheating(image_bgr)
                    
                    # Send results back
                    response = {
                        "type": "detection_result",
                        "timestamp": message.get("timestamp"),
                        "results": results
                    }
                    
                    await manager.send_personal_message(response, websocket)
                
                elif message.get("type") == "ping":
                    # Respond to ping
                    await manager.send_personal_message({"type": "pong"}, websocket)
                
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, websocket)
            except Exception as e:
                await manager.send_personal_message({
                    "type": "error", 
                    "message": f"Processing error: {str(e)}"
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "Something went wrong with the cheat detection system",
            "suggestion": "Try again or contact support if the problem persists"
        }
    )

if __name__ == "__main__":
    logger.info("Starting Try-to-cheat-if-you-dare API server...")
    logger.info("Cheat detector initialized successfully - ready to catch cheaters!")
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )