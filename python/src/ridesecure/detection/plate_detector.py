"""
RideSecure License Plate Detection and OCR Module
Uses YOLO + EasyOCR for license plate detection and text extraction
"""

import cv2
import easyocr
import numpy as np
from typing import List, Dict, Tuple, Optional
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlateDetector:
    """
    License plate detection and OCR using YOLO + EasyOCR
    Detects license plates in frames and extracts text
    """
    
    def __init__(self, languages: List[str] = ['en']):
        """
        Initialize plate detector
        
        Args:
            languages: OCR languages (e.g., ['en', 'hi'] for English + Hindi)
        """
        self.languages = languages
        self.ocr_reader = None
        self.plate_patterns = {
            'india_old': r'^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$',  # MH12AB1234
            'india_new': r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$',  # MH12A1234
            'standard': r'^[A-Z0-9\-\s]+$'  # Generic alphanumeric
        }
        
        logger.info(f"🔤 PlateDetector initialized with languages: {languages}")
    
    def load_ocr_reader(self) -> bool:
        """Initialize EasyOCR reader"""
        try:
            self.ocr_reader = easyocr.Reader(
                lang_list=self.languages,
                gpu=True,  # Use GPU if available
                verbose=False
            )
            logger.info("✅ EasyOCR reader loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ OCR reader loading failed: {e}")
            return False
    
    def detect_plates_yolo(self, frame: np.ndarray, confidence_threshold: float = 0.5) -> List[Dict]:
        """
        Detect license plates using YOLO (placeholder - needs trained model)
        
        Args:
            frame: Input image
            confidence_threshold: Minimum confidence for detections
            
        Returns:
            List of detected plate regions
        """
        # NOTE: This would use a YOLO model trained specifically for license plates
        # For now, we'll use traditional CV methods as fallback
        return self.detect_plates_cv(frame)
    
    def detect_plates_cv(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect license plates using traditional computer vision
        Fallback method when YOLO model is not available
        """
        plates = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter to reduce noise
            filtered = cv2.bilateralFilter(gray, 11, 17, 17)
            
            # Find edges using Canny
            edges = cv2.Canny(filtered, 30, 200)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
            
            for contour in contours:
                # Approximate contour to polygon
                epsilon = 0.018 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # License plates are typically rectangular (4 points)
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Filter by aspect ratio (license plates are wider than tall)
                    aspect_ratio = w / h
                    if 2.0 <= aspect_ratio <= 6.0 and w > 50 and h > 15:
                        plate_region = {
                            'bbox': [x, y, w, h],
                            'confidence': 0.8,  # Default confidence for CV method
                            'contour': approx,
                            'method': 'opencv'
                        }
                        plates.append(plate_region)
            
            logger.debug(f"🔍 CV method detected {len(plates)} potential plates")
            return plates
            
        except Exception as e:
            logger.error(f"❌ CV plate detection failed: {e}")
            return []
    
    def extract_plate_text(self, frame: np.ndarray, plate_region: Dict) -> Optional[Dict]:
        """
        Extract text from detected plate region using OCR
        
        Args:
            frame: Full frame image
            plate_region: Detected plate region info
            
        Returns:
            Dictionary with plate text and confidence
        """
        if self.ocr_reader is None:
            if not self.load_ocr_reader():
                return None
        
        try:
            # Extract plate ROI
            bbox = plate_region['bbox']
            x, y, w, h = bbox
            plate_roi = frame[y:y+h, x:x+w]
            
            # Preprocess plate ROI for better OCR
            plate_processed = self.preprocess_plate(plate_roi)
            
            # Perform OCR
            ocr_results = self.ocr_reader.readtext(plate_processed)
            
            if not ocr_results:
                return None
            
            # Find best text result
            best_result = max(ocr_results, key=lambda x: x[2])  # Highest confidence
            text, confidence = best_result[1], best_result[2]
            
            # Clean and validate text
            cleaned_text = self.clean_plate_text(text)
            pattern_match = self.validate_plate_pattern(cleaned_text)
            
            return {
                'text': cleaned_text,
                'raw_text': text,
                'confidence': confidence,
                'pattern_match': pattern_match,
                'bbox': bbox,
                'method': 'easyocr'
            }
            
        except Exception as e:
            logger.error(f"❌ OCR extraction failed: {e}")
            return None
    
    def preprocess_plate(self, plate_roi: np.ndarray) -> np.ndarray:
        """Preprocess plate image for better OCR accuracy"""
        try:
            # Resize if too small
            if plate_roi.shape[1] < 100:
                scale_factor = 100 / plate_roi.shape[1]
                new_width = int(plate_roi.shape[1] * scale_factor)
                new_height = int(plate_roi.shape[0] * scale_factor)
                plate_roi = cv2.resize(plate_roi, (new_width, new_height))
            
            # Convert to grayscale if needed
            if len(plate_roi.shape) == 3:
                gray = cv2.cvtColor(plate_roi, cv2.COLOR_BGR2GRAY)
            else:
                gray = plate_roi
            
            # Apply morphological operations
            kernel = np.ones((2, 2), np.uint8)
            processed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)
            
            # Enhance contrast
            processed = cv2.equalizeHist(processed)
            
            return processed
            
        except Exception as e:
            logger.error(f"❌ Plate preprocessing failed: {e}")
            return plate_roi
    
    def clean_plate_text(self, text: str) -> str:
        """Clean OCR text for license plate format"""
        # Remove spaces and convert to uppercase
        cleaned = re.sub(r'[^A-Z0-9]', '', text.upper())
        
        # Remove common OCR errors
        cleaned = cleaned.replace('O', '0')  # O -> 0
        cleaned = cleaned.replace('I', '1')  # I -> 1
        cleaned = cleaned.replace('S', '5')  # S -> 5
        cleaned = cleaned.replace('G', '6')  # G -> 6
        
        return cleaned
    
    def validate_plate_pattern(self, text: str) -> Dict:
        """Validate plate text against known patterns"""
        results = {}
        
        for pattern_name, pattern in self.plate_patterns.items():
            match = re.match(pattern, text)
            results[pattern_name] = match is not None
        
        # Overall validity
        results['is_valid'] = any(results.values())
        results['confidence_boost'] = 0.2 if results['is_valid'] else -0.1
        
        return results
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
        """
        Process frame for license plate detection and OCR
        
        Args:
            frame: Input video frame
            
        Returns:
            Tuple of (annotated_frame, plate_results)
        """
        # Detect plate regions
        plate_regions = self.detect_plates_yolo(frame)  # Will fallback to CV
        
        plate_results = []
        annotated_frame = frame.copy()
        
        for region in plate_regions:
            # Extract text from each region
            plate_info = self.extract_plate_text(frame, region)
            
            if plate_info:
                plate_results.append(plate_info)
                
                # Draw detection on frame
                annotated_frame = self.draw_plate_detection(annotated_frame, plate_info)
        
        return annotated_frame, plate_results
    
    def draw_plate_detection(self, frame: np.ndarray, plate_info: Dict) -> np.ndarray:
        """Draw plate detection and text on frame"""
        bbox = plate_info['bbox']
        text = plate_info['text']
        confidence = plate_info['confidence']
        is_valid = plate_info['pattern_match']['is_valid']
        
        x, y, w, h = bbox
        
        # Choose color based on validity
        color = (0, 255, 0) if is_valid else (0, 255, 255)  # Green if valid, yellow if not
        
        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        
        # Draw text
        label = f"{text} ({confidence:.2f})"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        
        # Background rectangle for text
        cv2.rectangle(frame, (x, y - label_size[1] - 10), (x + label_size[0], y), color, -1)
        cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        return frame


# Test/Demo functionality
if __name__ == "__main__":
    logger.info("🚀 Testing PlateDetector...")
    
    detector = PlateDetector(languages=['en'])
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        logger.error("❌ Could not open webcam")
        exit()
    
    logger.info("📹 Press 'q' to quit, 's' to save detection")
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        annotated_frame, plate_results = detector.process_frame(frame)
        
        # Display results
        cv2.imshow('RideSecure - License Plate Detection', annotated_frame)
        
        # Print detected plates
        for plate in plate_results:
            if plate['pattern_match']['is_valid']:
                logger.info(f"📋 PLATE DETECTED: {plate['text']} (confidence: {plate['confidence']:.2f})")
        
        # Save frame on 's' key
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            filename = f"plate_detection_{frame_count}.jpg"
            cv2.imwrite(filename, annotated_frame)
            logger.info(f"💾 Saved frame: {filename}")
        
        if key == ord('q'):
            break
            
        frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    logger.info("✅ License plate detection test completed")