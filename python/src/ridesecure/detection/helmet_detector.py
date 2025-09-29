"""
RideSecure Helmet Detection Module
Uses YOLO for real-time helmet detection in traffic videos
"""

import cv2
import torch
from ultralytics import YOLO
import numpy as np
from typing import List, Dict, Tuple, Optional
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HelmetDetector:
    """
    Helmet detection using YOLO model
    Detects persons with/without helmets in video frames
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize helmet detector
        
        Args:
            model_path: Path to trained YOLO model (.pt file)
        """
        self.model_path = model_path or "models/helmet_detection.pt"
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.class_names = {
            0: 'person_with_helmet',
            1: 'person_no_helmet', 
            2: 'motorcycle',
            3: 'bicycle',
            4: 'license_plate'
        }
        
        logger.info(f"🤖 HelmetDetector initialized on device: {self.device}")
        
    def load_model(self) -> bool:
        """Load YOLO model for helmet detection"""
        try:
            if os.path.exists(self.model_path):
                self.model = YOLO(self.model_path)
                logger.info(f"✅ Custom model loaded: {self.model_path}")
            else:
                # Use pre-trained YOLO model as fallback
                self.model = YOLO('yolov8n.pt')  # Nano version for speed
                logger.warning("⚠️ Using pre-trained YOLO (no helmet-specific training)")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Model loading failed: {e}")
            return False
    
    def detect_violations(self, frame: np.ndarray, confidence_threshold: float = 0.5) -> List[Dict]:
        """
        Detect helmet violations in a single frame
        
        Args:
            frame: Input image/video frame
            confidence_threshold: Minimum confidence for detections
            
        Returns:
            List of violation dictionaries with bounding boxes and confidence
        """
        if self.model is None:
            if not self.load_model():
                return []
        
        violations = []
        
        try:
            # Run YOLO inference
            results = self.model(frame, conf=confidence_threshold, verbose=False)
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Extract detection info
                        coords = box.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]  
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        
                        # Convert to RideSecure format
                        violation = {
                            'bbox': [int(coords[0]), int(coords[1]), 
                                   int(coords[2] - coords[0]), int(coords[3] - coords[1])],  # [x, y, w, h]
                            'confidence': float(confidence),
                            'class_id': class_id,
                            'class_name': self.class_names.get(class_id, 'unknown'),
                            'violation_type': 'NO_HELMET' if class_id == 1 else 'HELMET_OK' if class_id == 0 else 'OTHER'
                        }
                        
                        violations.append(violation)
            
            logger.debug(f"🔍 Detected {len(violations)} objects in frame")
            return violations
            
        except Exception as e:
            logger.error(f"❌ Detection failed: {e}")
            return []
    
    def process_video_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
        """
        Process single video frame and return annotated frame + violations
        
        Args:
            frame: Input video frame
            
        Returns:
            Tuple of (annotated_frame, violations_list)
        """
        violations = self.detect_violations(frame)
        annotated_frame = self.draw_detections(frame.copy(), violations)
        
        return annotated_frame, violations
    
    def draw_detections(self, frame: np.ndarray, violations: List[Dict]) -> np.ndarray:
        """Draw bounding boxes and labels on frame"""
        for violation in violations:
            bbox = violation['bbox']
            confidence = violation['confidence']
            class_name = violation['class_name']
            violation_type = violation['violation_type']
            
            # Bounding box coordinates
            x, y, w, h = bbox
            x2, y2 = x + w, y + h
            
            # Choose color based on violation type
            if violation_type == 'NO_HELMET':
                color = (0, 0, 255)  # Red for violations
            elif violation_type == 'HELMET_OK':
                color = (0, 255, 0)  # Green for compliance
            else:
                color = (255, 0, 0)  # Blue for other detections
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(frame, (x, y - label_size[1] - 10), (x + label_size[0], y), color, -1)
            cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return frame

    def get_violation_summary(self, violations: List[Dict]) -> Dict:
        """
        Get summary statistics from violations list
        
        Args:
            violations: List of violation dictionaries
            
        Returns:
            Summary statistics
        """
        total_detections = len(violations)
        helmet_violations = sum(1 for v in violations if v['violation_type'] == 'NO_HELMET')
        helmet_compliance = sum(1 for v in violations if v['violation_type'] == 'HELMET_OK')
        
        return {
            'total_detections': total_detections,
            'helmet_violations': helmet_violations,
            'helmet_compliance': helmet_compliance,
            'violation_rate': helmet_violations / max(total_detections, 1),
            'compliance_rate': helmet_compliance / max(total_detections, 1)
        }


# Test/Demo functionality
if __name__ == "__main__":
    logger.info("🚀 Testing HelmetDetector...")
    
    detector = HelmetDetector()
    
    # Test with webcam or sample image
    cap = cv2.VideoCapture(0)  # Use webcam for testing
    
    if not cap.isOpened():
        logger.error("❌ Could not open webcam")
        # Try to load a test image instead
        test_image_path = "../data/test_images/sample_traffic.jpg"
        if os.path.exists(test_image_path):
            logger.info("📸 Testing with sample image")
            frame = cv2.imread(test_image_path)
            annotated_frame, violations = detector.process_video_frame(frame)
            
            # Display results
            cv2.imshow('RideSecure - Helmet Detection Test', annotated_frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            # Print summary
            summary = detector.get_violation_summary(violations)
            logger.info(f"📊 Detection Summary: {summary}")
        else:
            logger.error("❌ No webcam or test images available")
        exit()
    
    logger.info("📹 Press 'q' to quit, 's' to save detection")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        annotated_frame, violations = detector.process_video_frame(frame)
        
        # Display results
        cv2.imshow('RideSecure - Helmet Detection', annotated_frame)
        
        # Print violations to console
        for violation in violations:
            if violation['violation_type'] == 'NO_HELMET':
                logger.info(f"⚠️ VIOLATION: {violation['class_name']} (confidence: {violation['confidence']:.2f})")
        
        # Save frame on 's' key
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            filename = f"detection_frame_{frame_count}.jpg"
            cv2.imwrite(filename, annotated_frame)
            logger.info(f"💾 Saved frame: {filename}")
        
        # Quit on 'q' key
        if key == ord('q'):
            break
            
        frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    logger.info("✅ Helmet detection test completed")