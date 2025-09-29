"""
RideSecure Main Detection Service
Orchestrates helmet detection and license plate recognition
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
import json
import logging
from pathlib import Path

from .helmet_detector import HelmetDetector
from .plate_detector import PlateDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DetectionService:
    """
    Main service that combines helmet detection and license plate recognition
    Processes video files and streams for RideSecure violations
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize detection service
        
        Args:
            config: Configuration dictionary for detectors
        """
        self.config = config or self._get_default_config()
        
        # Initialize detectors
        self.helmet_detector = HelmetDetector(
            model_path=self.config.get('helmet_model_path')
        )
        self.plate_detector = PlateDetector(
            languages=self.config.get('ocr_languages', ['en'])
        )
        
        # Detection statistics
        self.stats = {
            'total_frames_processed': 0,
            'violations_detected': 0,
            'plates_detected': 0,
            'processing_time_ms': []
        }
        
        logger.info("🚀 DetectionService initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration settings"""
        return {
            'helmet_model_path': None,  # Will use default YOLO
            'ocr_languages': ['en'],
            'confidence_thresholds': {
                'helmet': 0.5,
                'plate': 0.6
            },
            'video_processing': {
                'skip_frames': 1,  # Process every frame (0 = all, 1 = every 2nd, etc.)
                'resize_width': 640,  # Resize for faster processing
                'output_annotations': True
            },
            'violation_criteria': {
                'min_helmet_confidence': 0.5,
                'min_plate_confidence': 0.6,
                'require_plate_for_violation': True
            }
        }
    
    def process_video_file(self, video_path: str, output_path: str = None) -> Dict[str, Any]:
        """
        Process video file for helmet violations
        
        Args:
            video_path: Path to input video file
            output_path: Path for annotated output video (optional)
            
        Returns:
            Processing results with violations and statistics
        """
        logger.info(f"📹 Processing video: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"❌ Could not open video file: {video_path}")
        
        # Video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        logger.info(f"📊 Video info: {width}x{height}, {fps} FPS, {frame_count} frames")
        
        # Setup output video writer if needed
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            resize_width = self.config['video_processing']['resize_width']
            resize_height = int(height * resize_width / width)
            writer = cv2.VideoWriter(output_path, fourcc, fps, (resize_width, resize_height))
        
        # Processing variables
        violations = []
        current_frame = 0
        skip_frames = self.config['video_processing']['skip_frames']
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Skip frames for performance if configured
                if current_frame % (skip_frames + 1) != 0:
                    current_frame += 1
                    continue
                
                # Process frame
                timestamp_ms = current_frame / fps * 1000
                frame_result = self.process_single_frame(frame, timestamp_ms)
                
                # Collect violations
                if frame_result['violations']:
                    violations.extend(frame_result['violations'])
                
                # Write annotated frame if output is requested
                if writer and self.config['video_processing']['output_annotations']:
                    resized_frame = self.resize_frame(
                        frame_result['annotated_frame'], 
                        self.config['video_processing']['resize_width']
                    )
                    writer.write(resized_frame)
                
                # Update progress
                current_frame += 1
                if current_frame % 100 == 0:
                    progress = current_frame / frame_count * 100
                    logger.info(f"🔄 Progress: {progress:.1f}% ({current_frame}/{frame_count})")
        
        finally:
            cap.release()
            if writer:
                writer.release()
        
        # Generate results summary
        results = self._generate_results_summary(violations, video_path, fps, frame_count)
        logger.info(f"✅ Processing complete: {len(violations)} violations detected")
        
        return results
    
    def process_single_frame(self, frame: np.ndarray, timestamp_ms: float = 0) -> Dict[str, Any]:
        """
        Process single frame for violations
        
        Args:
            frame: Input video frame
            timestamp_ms: Frame timestamp in milliseconds
            
        Returns:
            Frame processing results
        """
        start_time = cv2.getTickCount()
        
        # Resize frame for processing if configured
        resize_width = self.config['video_processing'].get('resize_width')
        if resize_width and frame.shape[1] > resize_width:
            processing_frame = self.resize_frame(frame, resize_width)
            scale_factor = frame.shape[1] / processing_frame.shape[1]
        else:
            processing_frame = frame
            scale_factor = 1.0
        
        # Detect helmets
        helmet_detections = self.helmet_detector.detect_violations(
            processing_frame, 
            self.config['confidence_thresholds']['helmet']
        )
        
        # Detect license plates
        _, plate_detections = self.plate_detector.process_frame(processing_frame)
        
        # Scale detections back to original frame size
        if scale_factor != 1.0:
            helmet_detections = self._scale_detections(helmet_detections, scale_factor)
            plate_detections = self._scale_detections(plate_detections, scale_factor)
        
        # Identify violations
        violations = self._identify_violations(
            helmet_detections, 
            plate_detections, 
            timestamp_ms
        )
        
        # Draw annotations on original frame
        annotated_frame = self._draw_all_detections(
            frame.copy(), 
            helmet_detections, 
            plate_detections, 
            violations
        )
        
        # Calculate processing time
        processing_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency() * 1000
        self.stats['processing_time_ms'].append(processing_time)
        self.stats['total_frames_processed'] += 1
        
        return {
            'annotated_frame': annotated_frame,
            'helmet_detections': helmet_detections,
            'plate_detections': plate_detections,
            'violations': violations,
            'timestamp_ms': timestamp_ms,
            'processing_time_ms': processing_time
        }
    
    def _identify_violations(self, helmet_detections: List[Dict], 
                           plate_detections: List[Dict], 
                           timestamp_ms: float) -> List[Dict]:
        """Identify violations based on detections and criteria"""
        violations = []
        
        # Find helmet violations (persons without helmets)
        helmet_violations = [
            det for det in helmet_detections 
            if det['violation_type'] == 'NO_HELMET' and 
               det['confidence'] >= self.config['violation_criteria']['min_helmet_confidence']
        ]
        
        # Find valid license plates
        valid_plates = [
            plate for plate in plate_detections
            if plate['confidence'] >= self.config['violation_criteria']['min_plate_confidence'] and
               plate.get('pattern_match', {}).get('is_valid', False)
        ]
        
        for violation in helmet_violations:
            # Create violation record
            violation_record = {
                'id': f"violation_{timestamp_ms}_{len(violations)}",
                'timestamp_ms': timestamp_ms,
                'violation_type': 'NO_HELMET',
                'helmet_detection': violation,
                'license_plate': None,
                'confidence_score': violation['confidence'],
                'location_bbox': violation['bbox'],
                'has_license_plate': len(valid_plates) > 0
            }
            
            # Try to associate with nearest license plate
            if valid_plates:
                nearest_plate = self._find_nearest_plate(violation['bbox'], valid_plates)
                if nearest_plate:
                    violation_record['license_plate'] = nearest_plate
                    violation_record['confidence_score'] = (
                        violation['confidence'] + nearest_plate['confidence']
                    ) / 2
            
            # Apply violation criteria
            if self.config['violation_criteria']['require_plate_for_violation']:
                if violation_record['license_plate'] is None:
                    continue  # Skip violations without license plates
            
            violations.append(violation_record)
            self.stats['violations_detected'] += 1
        
        # Update plate detection stats
        self.stats['plates_detected'] += len(valid_plates)
        
        return violations
    
    def _find_nearest_plate(self, helmet_bbox: List[int], plates: List[Dict]) -> Optional[Dict]:
        """Find the license plate closest to helmet detection"""
        if not plates:
            return None
        
        helmet_center = [
            helmet_bbox[0] + helmet_bbox[2] // 2,
            helmet_bbox[1] + helmet_bbox[3] // 2
        ]
        
        min_distance = float('inf')
        nearest_plate = None
        
        for plate in plates:
            plate_center = [
                plate['bbox'][0] + plate['bbox'][2] // 2,
                plate['bbox'][1] + plate['bbox'][3] // 2
            ]
            
            # Calculate Euclidean distance
            distance = np.sqrt(
                (helmet_center[0] - plate_center[0]) ** 2 + 
                (helmet_center[1] - plate_center[1]) ** 2
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest_plate = plate
        
        return nearest_plate
    
    def resize_frame(self, frame: np.ndarray, width: int) -> np.ndarray:
        """Resize frame maintaining aspect ratio"""
        height = int(frame.shape[0] * width / frame.shape[1])
        return cv2.resize(frame, (width, height))
    
    def _scale_detections(self, detections: List[Dict], scale_factor: float) -> List[Dict]:
        """Scale detection bounding boxes by factor"""
        scaled = []
        for det in detections:
            scaled_det = det.copy()
            if 'bbox' in det:
                bbox = det['bbox']
                scaled_det['bbox'] = [
                    int(bbox[0] * scale_factor),
                    int(bbox[1] * scale_factor),
                    int(bbox[2] * scale_factor),
                    int(bbox[3] * scale_factor)
                ]
            scaled.append(scaled_det)
        return scaled
    
    def _draw_all_detections(self, frame: np.ndarray, 
                            helmet_detections: List[Dict],
                            plate_detections: List[Dict],
                            violations: List[Dict]) -> np.ndarray:
        """Draw all detections and violations on frame"""
        # Draw helmet detections
        frame = self.helmet_detector.draw_detections(frame, helmet_detections)
        
        # Draw plate detections
        for plate in plate_detections:
            frame = self.plate_detector.draw_plate_detection(frame, plate)
        
        # Highlight violations with special marking
        for violation in violations:
            bbox = violation['location_bbox']
            x, y, w, h = bbox
            
            # Draw violation marker (red circle)
            center = (x + w // 2, y + h // 2)
            cv2.circle(frame, center, 20, (0, 0, 255), 3)
            cv2.putText(frame, "VIOLATION", (x, y - 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        return frame
    
    def _generate_results_summary(self, violations: List[Dict], video_path: str, 
                                 fps: float, total_frames: int) -> Dict[str, Any]:
        """Generate comprehensive results summary"""
        duration_seconds = total_frames / fps
        avg_processing_time = np.mean(self.stats['processing_time_ms']) if self.stats['processing_time_ms'] else 0
        
        return {
            'video_info': {
                'path': video_path,
                'duration_seconds': duration_seconds,
                'fps': fps,
                'total_frames': total_frames,
                'frames_processed': self.stats['total_frames_processed']
            },
            'detection_results': {
                'total_violations': len(violations),
                'violations_with_plates': sum(1 for v in violations if v['license_plate']),
                'unique_plates': len(set(
                    v['license_plate']['text'] for v in violations 
                    if v['license_plate']
                )),
                'violation_rate_per_minute': len(violations) / (duration_seconds / 60)
            },
            'performance_metrics': {
                'avg_processing_time_ms': avg_processing_time,
                'processing_fps': 1000 / avg_processing_time if avg_processing_time > 0 else 0,
                'total_processing_time_seconds': sum(self.stats['processing_time_ms']) / 1000
            },
            'violations': violations,
            'timestamp': datetime.now().isoformat()
        }
    
    def export_results(self, results: Dict[str, Any], output_path: str):
        """Export results to JSON file"""
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"📄 Results exported to: {output_path}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current detection statistics"""
        return self.stats.copy()


# Test/Demo functionality
if __name__ == "__main__":
    logger.info("🚀 Testing DetectionService...")
    
    # Test with sample video or webcam
    service = DetectionService()
    
    # Try webcam first
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        logger.info("📹 Testing with webcam - press 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process single frame
            result = service.process_single_frame(frame)
            
            # Display annotated frame
            cv2.imshow('RideSecure - Detection Service', result['annotated_frame'])
            
            # Print violations
            for violation in result['violations']:
                plate_text = violation['license_plate']['text'] if violation['license_plate'] else 'No plate'
                logger.info(f"⚠️ VIOLATION: {violation['violation_type']} - Plate: {plate_text}")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        # Print final statistics
        stats = service.get_statistics()
        logger.info(f"📊 Final Statistics: {stats}")
    else:
        logger.error("❌ No webcam available for testing")
    
    logger.info("✅ DetectionService test completed")