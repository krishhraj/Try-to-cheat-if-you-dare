"""
Try-to-cheat-if-you-dare - Advanced Cheat Detection Model

This module implements a sophisticated cheat detection system that dares users to try
fooling it with deepfakes, filters, or any form of facial manipulation.
Uses cutting-edge computer vision and machine learning to catch cheating attempts.
"""

import cv2
import numpy as np
from typing import Tuple, Dict, Any, Optional
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
import os

logger = logging.getLogger(__name__)


class CheatDetector:
    """
    Advanced cheat detection system that challenges users to try fooling it.
    
    This detector analyzes facial features, texture patterns, and temporal inconsistencies
    to identify any attempts at cheating with deepfakes or manipulated content.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the cheat detector - ready to catch any cheating attempts!"""
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.is_trained = False
        self.confidence_threshold = 0.6
        
        # Feature extraction parameters
        self.lbp_radius = 3
        self.lbp_n_points = 8 * self.lbp_radius
        
        # Statistics tracking
        self.total_attempts = 0
        self.caught_cheats = 0
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def extract_cheat_features(self, face_roi: np.ndarray) -> np.ndarray:
        """
        Extract comprehensive features to catch cheating attempts.
        
        Args:
            face_roi: Region of interest containing the face
            
        Returns:
            Feature vector designed to detect manipulation
        """
        features = []
        
        # Resize face for consistent analysis
        face_resized = cv2.resize(face_roi, (128, 128))
        gray_face = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
        
        # 1. Local Binary Pattern features - catches texture manipulation
        lbp_features = self._extract_lbp_features(gray_face)
        features.extend(lbp_features)
        
        # 2. Edge density features - deepfakes often have inconsistent edges
        edge_features = self._extract_edge_features(gray_face)
        features.extend(edge_features)
        
        # 3. Color distribution features - color inconsistencies reveal cheating
        color_features = self._extract_color_features(face_resized)
        features.extend(color_features)
        
        # 4. Frequency domain features - compression artifacts from manipulation
        freq_features = self._extract_frequency_features(gray_face)
        features.extend(freq_features)
        
        # 5. Symmetry features - facial asymmetries from poor manipulation
        symmetry_features = self._extract_symmetry_features(gray_face)
        features.extend(symmetry_features)
        
        return np.array(features)
    
    def _extract_lbp_features(self, gray_image: np.ndarray) -> list:
        """Extract Local Binary Pattern features to catch texture manipulation."""
        # Simple LBP implementation
        lbp = np.zeros_like(gray_image)
        
        for i in range(1, gray_image.shape[0] - 1):
            for j in range(1, gray_image.shape[1] - 1):
                center = gray_image[i, j]
                binary_string = ''
                
                # 8-neighborhood
                neighbors = [
                    gray_image[i-1, j-1], gray_image[i-1, j], gray_image[i-1, j+1],
                    gray_image[i, j+1], gray_image[i+1, j+1], gray_image[i+1, j],
                    gray_image[i+1, j-1], gray_image[i, j-1]
                ]
                
                for neighbor in neighbors:
                    binary_string += '1' if neighbor >= center else '0'
                
                lbp[i, j] = int(binary_string, 2)
        
        # Calculate histogram
        hist, _ = np.histogram(lbp.ravel(), bins=256, range=(0, 256))
        hist = hist.astype(float)
        hist /= (hist.sum() + 1e-7)  # Normalize
        
        return hist[:50].tolist()  # Return first 50 bins
    
    def _extract_edge_features(self, gray_image: np.ndarray) -> list:
        """Extract edge features - manipulated images often have inconsistent edges."""
        # Sobel edge detection
        sobel_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        
        # Canny edge detection
        canny = cv2.Canny(gray_image, 50, 150)
        
        features = [
            np.mean(sobel_magnitude),
            np.std(sobel_magnitude),
            np.mean(canny),
            np.std(canny),
            np.sum(canny > 0) / canny.size,  # Edge density
        ]
        
        return features
    
    def _extract_color_features(self, color_image: np.ndarray) -> list:
        """Extract color distribution features - color inconsistencies reveal manipulation."""
        features = []
        
        # BGR color space
        for channel in range(3):
            channel_data = color_image[:, :, channel]
            features.extend([
                np.mean(channel_data),
                np.std(channel_data),
                np.median(channel_data)
            ])
        
        # HSV color space
        hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)
        for channel in range(3):
            channel_data = hsv[:, :, channel]
            features.extend([
                np.mean(channel_data),
                np.std(channel_data)
            ])
        
        # LAB color space
        lab = cv2.cvtColor(color_image, cv2.COLOR_BGR2LAB)
        for channel in range(3):
            channel_data = lab[:, :, channel]
            features.extend([
                np.mean(channel_data),
                np.std(channel_data)
            ])
        
        return features
    
    def _extract_frequency_features(self, gray_image: np.ndarray) -> list:
        """Extract frequency domain features - compression artifacts from manipulation."""
        # DCT (Discrete Cosine Transform)
        dct = cv2.dct(np.float32(gray_image))
        
        # Focus on high-frequency components (where artifacts appear)
        high_freq = dct[32:64, 32:64]
        
        features = [
            np.mean(np.abs(high_freq)),
            np.std(np.abs(high_freq)),
            np.max(np.abs(high_freq)),
            np.sum(np.abs(high_freq) > np.mean(np.abs(high_freq)))
        ]
        
        return features
    
    def _extract_symmetry_features(self, gray_image: np.ndarray) -> list:
        """Extract facial symmetry features - poor manipulation creates asymmetries."""
        height, width = gray_image.shape
        
        # Split face vertically
        left_half = gray_image[:, :width//2]
        right_half = gray_image[:, width//2:]
        right_half_flipped = np.fliplr(right_half)
        
        # Resize to match if needed
        min_width = min(left_half.shape[1], right_half_flipped.shape[1])
        left_half = left_half[:, :min_width]
        right_half_flipped = right_half_flipped[:, :min_width]
        
        # Calculate symmetry metrics
        diff = np.abs(left_half.astype(float) - right_half_flipped.astype(float))
        
        features = [
            np.mean(diff),
            np.std(diff),
            np.max(diff),
            np.sum(diff > 50) / diff.size  # Asymmetry ratio
        ]
        
        return features
    
    def detect_cheating(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Main detection method - try to cheat if you dare!
        
        Args:
            image: Input image to analyze for cheating
            
        Returns:
            Detection results with confidence scores
        """
        self.total_attempts += 1
        
        # Convert to BGR if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Assume it's already BGR
            pass
        elif len(image.shape) == 3 and image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        
        # Detect faces
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return {
                'faces_detected': 0,
                'is_cheating': False,
                'confidence': 0.0,
                'message': 'No faces detected - nice try hiding!',
                'total_attempts': self.total_attempts,
                'caught_cheats': self.caught_cheats
            }
        
        results = []
        max_confidence = 0.0
        is_cheating = False
        
        for (x, y, w, h) in faces:
            # Extract face region
            face_roi = image[y:y+h, x:x+w]
            
            # Extract features
            features = self.extract_cheat_features(face_roi)
            
            # Heuristic-based detection (since we don't have training data)
            confidence = self._calculate_cheat_confidence(features)
            
            if confidence > self.confidence_threshold:
                is_cheating = True
                self.caught_cheats += 1
            
            max_confidence = max(max_confidence, confidence)
            
            results.append({
                'bbox': [int(x), int(y), int(w), int(h)],
                'confidence': float(confidence),
                'is_cheating': confidence > self.confidence_threshold,
                'features_extracted': len(features)
            })
        
        # Determine message based on results
        if is_cheating:
            messages = [
                "Caught you cheating! Nice try though 😏",
                "Your deepfake skills need work! 🕵️",
                "Manipulation detected - better luck next time!",
                "AI: 1, Cheater: 0 🤖",
                "Your fake is no match for our detection!"
            ]
            message = messages[self.total_attempts % len(messages)]
        else:
            messages = [
                "Looks real to me... for now 🤔",
                "You passed this time, but we're watching!",
                "Clean image detected - or are you just that good?",
                "No cheating detected... yet 👀",
                "Impressive! Either real or very well done."
            ]
            message = messages[self.total_attempts % len(messages)]
        
        return {
            'faces_detected': len(faces),
            'faces': results,
            'is_cheating': is_cheating,
            'confidence': float(max_confidence),
            'message': message,
            'total_attempts': self.total_attempts,
            'caught_cheats': self.caught_cheats,
            'success_rate': f"{(self.caught_cheats/self.total_attempts)*100:.1f}%" if self.total_attempts > 0 else "0%"
        }
    
    def _calculate_cheat_confidence(self, features: np.ndarray) -> float:
        """Calculate confidence that this is a cheating attempt."""
        # Heuristic-based scoring since we don't have labeled training data
        
        # Normalize features
        features = np.array(features)
        features = (features - np.mean(features)) / (np.std(features) + 1e-7)
        
        # Look for anomalous patterns that suggest manipulation
        anomaly_score = 0.0
        
        # High variance in texture features suggests manipulation
        if len(features) > 50:
            texture_variance = np.var(features[:50])
            if texture_variance > 2.0:
                anomaly_score += 0.3
        
        # Edge inconsistencies
        if len(features) > 55:
            edge_features = features[50:55]
            edge_anomaly = np.sum(np.abs(edge_features) > 2.0) / len(edge_features)
            anomaly_score += edge_anomaly * 0.25
        
        # Color distribution anomalies
        if len(features) > 70:
            color_features = features[55:70]
            color_anomaly = np.sum(np.abs(color_features) > 1.5) / len(color_features)
            anomaly_score += color_anomaly * 0.2
        
        # Frequency domain anomalies
        if len(features) > 74:
            freq_features = features[70:74]
            freq_anomaly = np.sum(np.abs(freq_features) > 2.5) / len(freq_features)
            anomaly_score += freq_anomaly * 0.15
        
        # Symmetry anomalies
        if len(features) > 78:
            symmetry_features = features[74:78]
            symmetry_anomaly = np.sum(np.abs(symmetry_features) > 2.0) / len(symmetry_features)
            anomaly_score += symmetry_anomaly * 0.1
        
        return min(anomaly_score, 1.0)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detection statistics."""
        return {
            'total_attempts': self.total_attempts,
            'caught_cheats': self.caught_cheats,
            'success_rate': f"{(self.caught_cheats/self.total_attempts)*100:.1f}%" if self.total_attempts > 0 else "0%",
            'confidence_threshold': self.confidence_threshold,
            'model_ready': True
        }
    
    def save_model(self, path: str):
        """Save the trained model."""
        model_data = {
            'scaler': self.scaler,
            'anomaly_detector': self.anomaly_detector,
            'is_trained': self.is_trained,
            'confidence_threshold': self.confidence_threshold,
            'total_attempts': self.total_attempts,
            'caught_cheats': self.caught_cheats
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Cheat detector model saved to {path}")
    
    def load_model(self, path: str):
        """Load a pre-trained model."""
        try:
            with open(path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.scaler = model_data['scaler']
            self.anomaly_detector = model_data['anomaly_detector']
            self.is_trained = model_data['is_trained']
            self.confidence_threshold = model_data['confidence_threshold']
            self.total_attempts = model_data.get('total_attempts', 0)
            self.caught_cheats = model_data.get('caught_cheats', 0)
            
            logger.info(f"Cheat detector model loaded from {path}")
        except Exception as e:
            logger.error(f"Failed to load model from {path}: {e}")
    
    def update_threshold(self, new_threshold: float):
        """Update the confidence threshold for detection."""
        self.confidence_threshold = max(0.0, min(1.0, new_threshold))
        logger.info(f"Confidence threshold updated to {self.confidence_threshold}")


# Global detector instance
detector = None

def get_detector() -> CheatDetector:
    """Get the global detector instance."""
    global detector
    if detector is None:
        detector = CheatDetector()
        logger.info("Cheat detector initialized - ready to catch cheaters!")
    return detector