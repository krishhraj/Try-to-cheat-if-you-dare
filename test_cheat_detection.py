#!/usr/bin/env python3
"""
Test Suite for Try-to-cheat-if-you-dare System

Comprehensive testing of the cheat detection system including:
- Core detection algorithms
- API endpoints
- WebSocket functionality
- File processing
"""

import unittest
import requests
import numpy as np
import cv2
import io
import json
import time
import sys
import os
from PIL import Image

# Add backend to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from models.cheat_detector import CheatDetector
except ImportError:
    print("Warning: Could not import CheatDetector. Some tests will be skipped.")
    CheatDetector = None

class TestCheatDetector(unittest.TestCase):
    """Test the core cheat detection functionality."""
    
    def setUp(self):
        if CheatDetector:
            self.detector = CheatDetector()
    
    @unittest.skipIf(CheatDetector is None, "CheatDetector not available")
    def test_detector_initialization(self):
        """Test that the detector initializes properly."""
        self.assertIsNotNone(self.detector)
        self.assertIsNotNone(self.detector.face_cascade)
        self.assertEqual(self.detector.confidence_threshold, 0.6)
    
    @unittest.skipIf(CheatDetector is None, "CheatDetector not available")
    def test_feature_extraction(self):
        """Test feature extraction from face images."""
        # Create a test face image
        test_face = np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8)
        
        features = self.detector.extract_cheat_features(test_face)
        
        self.assertIsInstance(features, np.ndarray)
        self.assertGreater(len(features), 0)
        print(f"✅ Extracted {len(features)} features from test face")
    
    @unittest.skipIf(CheatDetector is None, "CheatDetector not available")
    def test_detection_with_no_faces(self):
        """Test detection on image with no faces."""
        # Create image with no faces
        no_face_image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        
        result = self.detector.detect_cheating(no_face_image)
        
        self.assertEqual(result['faces_detected'], 0)
        self.assertFalse(result['is_cheating'])
        print("✅ Correctly handled image with no faces")
    
    @unittest.skipIf(CheatDetector is None, "CheatDetector not available")
    def test_stats_tracking(self):
        """Test that statistics are tracked correctly."""
        initial_stats = self.detector.get_stats()
        initial_attempts = initial_stats['total_attempts']
        
        # Run a detection
        test_image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        self.detector.detect_cheating(test_image)
        
        new_stats = self.detector.get_stats()
        self.assertEqual(new_stats['total_attempts'], initial_attempts + 1)
        print("✅ Statistics tracking working correctly")


class TestAPIEndpoints(unittest.TestCase):
    """Test the API endpoints."""
    
    def setUp(self):
        self.base_url = "http://localhost:8000"
        self.timeout = 10
    
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn('status', data)
            self.assertIn('detector_ready', data)
            print("✅ Health endpoint working")
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"API server not running: {e}")
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        try:
            response = requests.get(f"{self.base_url}/", timeout=self.timeout)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn('message', data)
            self.assertIn('challenge', data)
            print("✅ Root endpoint working")
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"API server not running: {e}")
    
    def test_stats_endpoint(self):
        """Test the statistics endpoint."""
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=self.timeout)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn('total_attempts', data)
            self.assertIn('caught_cheats', data)
            self.assertIn('success_rate', data)
            print("✅ Stats endpoint working")
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"API server not running: {e}")
    
    def test_image_detection_endpoint(self):
        """Test image detection endpoint."""
        try:
            # Create a test image
            test_image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
            _, buffer = cv2.imencode('.jpg', test_image)
            
            files = {'file': ('test.jpg', io.BytesIO(buffer.tobytes()), 'image/jpeg')}
            
            response = requests.post(
                f"{self.base_url}/detect/image", 
                files=files, 
                timeout=self.timeout
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn('faces_detected', data)
            self.assertIn('is_cheating', data)
            self.assertIn('confidence', data)
            self.assertIn('message', data)
            print("✅ Image detection endpoint working")
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"API server not running: {e}")
    
    def test_invalid_file_upload(self):
        """Test uploading invalid file type."""
        try:
            # Create a text file
            files = {'file': ('test.txt', io.BytesIO(b'not an image'), 'text/plain')}
            
            response = requests.post(
                f"{self.base_url}/detect/image", 
                files=files, 
                timeout=self.timeout
            )
            
            self.assertEqual(response.status_code, 400)
            print("✅ Invalid file type correctly rejected")
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"API server not running: {e}")


class TestWebInterface(unittest.TestCase):
    """Test the web interface."""
    
    def setUp(self):
        self.frontend_url = "http://localhost:3000"
        self.timeout = 10
    
    def test_frontend_accessible(self):
        """Test that the frontend is accessible."""
        try:
            response = requests.get(self.frontend_url, timeout=self.timeout)
            self.assertEqual(response.status_code, 200)
            
            # Check for key elements
            content = response.text
            self.assertIn('Try-to-cheat-if-you-dare', content)
            self.assertIn('Real-time Challenge', content)
            self.assertIn('Upload & Analyze', content)
            print("✅ Frontend accessible and contains expected content")
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"Frontend server not running: {e}")


class TestSystemIntegration(unittest.TestCase):
    """Test full system integration."""
    
    def setUp(self):
        self.api_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.timeout = 10
    
    def test_full_system_health(self):
        """Test that all system components are healthy."""
        try:
            # Test API
            api_response = requests.get(f"{self.api_url}/health", timeout=self.timeout)
            self.assertEqual(api_response.status_code, 200)
            
            # Test Frontend
            frontend_response = requests.get(self.frontend_url, timeout=self.timeout)
            self.assertEqual(frontend_response.status_code, 200)
            
            print("✅ Full system integration test passed")
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"System components not running: {e}")
    
    def test_end_to_end_detection(self):
        """Test end-to-end detection workflow."""
        try:
            # Create test image with a simple face-like pattern
            test_image = np.zeros((200, 200, 3), dtype=np.uint8)
            # Add some face-like features
            cv2.circle(test_image, (100, 100), 80, (255, 255, 255), -1)  # Face
            cv2.circle(test_image, (80, 80), 10, (0, 0, 0), -1)   # Left eye
            cv2.circle(test_image, (120, 80), 10, (0, 0, 0), -1)  # Right eye
            cv2.ellipse(test_image, (100, 120), (20, 10), 0, 0, 180, (0, 0, 0), 2)  # Mouth
            
            _, buffer = cv2.imencode('.jpg', test_image)
            files = {'file': ('face_test.jpg', io.BytesIO(buffer.tobytes()), 'image/jpeg')}
            
            # Submit for detection
            response = requests.post(
                f"{self.api_url}/detect/image", 
                files=files, 
                timeout=self.timeout
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertIn('processing_status', data)
            self.assertEqual(data['processing_status'], 'completed')
            
            print("✅ End-to-end detection workflow completed successfully")
            print(f"   Faces detected: {data.get('faces_detected', 0)}")
            print(f"   Cheating detected: {data.get('is_cheating', False)}")
            print(f"   Confidence: {data.get('confidence', 0):.2f}")
            print(f"   Message: {data.get('message', 'No message')}")
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"API server not running: {e}")


def create_demo_visualization():
    """Create a demo visualization showing the system in action."""
    print("\n" + "="*60)
    print("🎯 TRY-TO-CHEAT-IF-YOU-DARE - DEMO VISUALIZATION")
    print("="*60)
    
    try:
        # Test API health
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Status: {data.get('status', 'unknown')}")
            
            if 'stats' in data:
                stats = data['stats']
                print(f"📊 Total Attempts: {stats.get('total_attempts', 0)}")
                print(f"🚨 Caught Cheating: {stats.get('caught_cheats', 0)}")
                print(f"📈 Success Rate: {stats.get('success_rate', '0%')}")
        
        # Test frontend
        frontend_response = requests.get("http://localhost:3000", timeout=5)
        if frontend_response.status_code == 200:
            print("✅ Frontend: Accessible")
        
        print("\n🎮 Demo Features Available:")
        print("   🎥 Real-time camera detection")
        print("   📁 File upload and analysis")
        print("   📊 Statistics dashboard")
        print("   🔧 API documentation")
        
        print("\n🌐 Access Points:")
        print("   Web Demo: http://localhost:3000")
        print("   API Docs: http://localhost:8000/docs")
        print("   Health Check: http://localhost:8000/health")
        
        print("\n🎯 Challenge:")
        print("   Try to cheat if you dare!")
        print("   Upload deepfakes, use filters, or try any manipulation!")
        print("   Our AI is watching and ready to catch you! 👀")
        
    except Exception as e:
        print(f"❌ Demo visualization failed: {e}")
        print("Make sure both servers are running:")
        print("   python backend/app/main.py")
        print("   python -m http.server 3000 (in frontend directory)")


def main():
    """Run all tests and create demo visualization."""
    print("🎯 TRY-TO-CHEAT-IF-YOU-DARE - TEST SUITE")
    print("="*50)
    
    # Run unit tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCheatDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestWebInterface))
    suite.addTests(loader.loadTestsFromTestCase(TestSystemIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Create demo visualization
    create_demo_visualization()
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("🎉 ALL TESTS PASSED! Your cheat detection system is ready!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)