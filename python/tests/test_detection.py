"""
Test suite for RideSecure detection modules
Run with: python -m pytest tests/
"""

import pytest
import numpy as np
import cv2
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestHelmetDetector:
    """Test cases for HelmetDetector class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        from ridesecure.detection import HelmetDetector
        self.detector = HelmetDetector()
    
    def test_initialization(self):
        """Test detector initialization"""
        assert self.detector is not None
        assert hasattr(self.detector, 'class_names')
        assert hasattr(self.detector, 'device')
    
    def test_detect_violations_empty_frame(self):
        """Test detection with empty frame"""
        # Create empty frame
        empty_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Mock model to avoid loading actual YOLO
        with patch.object(self.detector, 'model') as mock_model:
            mock_result = Mock()
            mock_result.boxes = None
            mock_model.return_value = [mock_result]
            
            violations = self.detector.detect_violations(empty_frame)
            
        assert isinstance(violations, list)
    
    def test_draw_detections(self):
        """Test drawing detections on frame"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        violations = [{
            'bbox': [100, 100, 50, 80],
            'confidence': 0.85,
            'class_name': 'person_no_helmet',
            'violation_type': 'NO_HELMET'
        }]
        
        result_frame = self.detector.draw_detections(frame, violations)
        
        assert result_frame.shape == frame.shape
        # Frame should be modified (not all zeros anymore)
        assert not np.array_equal(result_frame, frame)
    
    def test_violation_summary(self):
        """Test violation summary generation"""
        violations = [
            {'violation_type': 'NO_HELMET'},
            {'violation_type': 'HELMET_OK'},
            {'violation_type': 'NO_HELMET'}
        ]
        
        summary = self.detector.get_violation_summary(violations)
        
        assert summary['total_detections'] == 3
        assert summary['helmet_violations'] == 2
        assert summary['helmet_compliance'] == 1
        assert summary['violation_rate'] == 2/3


class TestPlateDetector:
    """Test cases for PlateDetector class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        from ridesecure.detection import PlateDetector
        self.detector = PlateDetector()
    
    def test_initialization(self):
        """Test detector initialization"""
        assert self.detector is not None
        assert hasattr(self.detector, 'languages')
        assert hasattr(self.detector, 'plate_patterns')
    
    def test_clean_plate_text(self):
        """Test plate text cleaning"""
        # Test various input formats
        assert self.detector.clean_plate_text("MH 12 AB 1234") == "MH12AB1234"
        assert self.detector.clean_plate_text("mh12ab1234") == "MH12AB1234"
        assert self.detector.clean_plate_text("MH-12-AB-1234") == "MH12AB1234"
        
        # Test OCR error corrections
        assert self.detector.clean_plate_text("MH12OB1234") == "MH120B1234"  # O -> 0
        assert self.detector.clean_plate_text("MH12IB1234") == "MH121B1234"  # I -> 1
    
    def test_validate_plate_pattern(self):
        """Test plate pattern validation"""
        # Valid Indian plates
        valid_old = "MH12AB1234"
        valid_new = "MH12A1234"
        invalid = "INVALID123"
        
        result_valid_old = self.detector.validate_plate_pattern(valid_old)
        result_valid_new = self.detector.validate_plate_pattern(valid_new)
        result_invalid = self.detector.validate_plate_pattern(invalid)
        
        assert result_valid_old['india_old'] == True
        assert result_valid_new['india_new'] == True
        assert result_invalid['is_valid'] == False
    
    def test_cv_detection_basic(self):
        """Test basic CV plate detection"""
        # Create simple test image with rectangle (simulated plate)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(frame, (200, 200), (400, 250), (255, 255, 255), -1)
        
        plates = self.detector.detect_plates_cv(frame)
        
        assert isinstance(plates, list)
        # Should detect at least some rectangular regions


class TestDetectionService:
    """Test cases for DetectionService class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        from ridesecure.detection import DetectionService
        self.service = DetectionService()
    
    def test_initialization(self):
        """Test service initialization"""
        assert self.service is not None
        assert hasattr(self.service, 'helmet_detector')
        assert hasattr(self.service, 'plate_detector')
        assert hasattr(self.service, 'stats')
    
    def test_default_config(self):
        """Test default configuration"""
        config = self.service._get_default_config()
        
        assert 'helmet_model_path' in config
        assert 'confidence_thresholds' in config
        assert 'video_processing' in config
        assert 'violation_criteria' in config
    
    def test_resize_frame(self):
        """Test frame resizing"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        resized = self.service.resize_frame(frame, 320)
        
        assert resized.shape[1] == 320
        assert resized.shape[0] == 240  # Maintains aspect ratio
    
    def test_scale_detections(self):
        """Test detection scaling"""
        detections = [{
            'bbox': [100, 100, 50, 50],
            'confidence': 0.8
        }]
        
        scaled = self.service._scale_detections(detections, 2.0)
        
        assert scaled[0]['bbox'] == [200, 200, 100, 100]
        assert scaled[0]['confidence'] == 0.8  # Confidence unchanged
    
    def test_find_nearest_plate(self):
        """Test nearest plate finding"""
        helmet_bbox = [100, 100, 50, 50]  # Center at (125, 125)
        
        plates = [
            {'bbox': [200, 200, 50, 20]},  # Center at (225, 210) - farther
            {'bbox': [110, 130, 60, 25]}   # Center at (140, 142.5) - closer
        ]
        
        nearest = self.service._find_nearest_plate(helmet_bbox, plates)
        
        assert nearest == plates[1]  # Should return closer plate
    
    def test_identify_violations(self):
        """Test violation identification"""
        helmet_detections = [
            {
                'violation_type': 'NO_HELMET',
                'confidence': 0.8,
                'bbox': [100, 100, 50, 50]
            }
        ]
        
        plate_detections = [
            {
                'text': 'MH12AB1234',
                'confidence': 0.9,
                'bbox': [110, 140, 60, 20],
                'pattern_match': {'is_valid': True}
            }
        ]
        
        violations = self.service._identify_violations(
            helmet_detections, plate_detections, 1000.0
        )
        
        assert len(violations) == 1
        assert violations[0]['violation_type'] == 'NO_HELMET'
        assert violations[0]['license_plate'] is not None
        assert violations[0]['license_plate']['text'] == 'MH12AB1234'


# Integration Tests
class TestIntegration:
    """Integration tests for complete workflow"""
    
    def test_full_pipeline(self):
        """Test complete detection pipeline"""
        from ridesecure.detection import DetectionService
        
        service = DetectionService()
        
        # Create test frame with some content
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add some rectangles to simulate objects
        cv2.rectangle(frame, (100, 100), (150, 200), (255, 255, 255), -1)  # Person
        cv2.rectangle(frame, (200, 300), (300, 320), (128, 128, 128), -1)  # Plate
        
        # Process frame (will use mocked detections in real tests)
        with patch.object(service.helmet_detector, 'detect_violations') as mock_helmet, \
             patch.object(service.plate_detector, 'process_frame') as mock_plate:
            
            # Mock return values
            mock_helmet.return_value = [{
                'violation_type': 'NO_HELMET',
                'confidence': 0.85,
                'bbox': [100, 100, 50, 100]
            }]
            
            mock_plate.return_value = (frame, [{
                'text': 'TEST123',
                'confidence': 0.9,
                'bbox': [200, 300, 100, 20],
                'pattern_match': {'is_valid': True}
            }])
            
            result = service.process_single_frame(frame, 0)
            
            # Verify result structure
            assert 'annotated_frame' in result
            assert 'violations' in result
            assert 'helmet_detections' in result
            assert 'plate_detections' in result
            assert 'timestamp_ms' in result
            
            # Should have detected violation
            assert len(result['violations']) > 0


# Performance Tests
class TestPerformance:
    """Performance benchmarking tests"""
    
    def test_frame_processing_speed(self):
        """Test frame processing performance"""
        from ridesecure.detection import DetectionService
        import time
        
        service = DetectionService()
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Mock detectors for speed test
        with patch.object(service.helmet_detector, 'detect_violations', return_value=[]), \
             patch.object(service.plate_detector, 'process_frame', return_value=(frame, [])):
            
            start_time = time.time()
            
            for _ in range(10):  # Process 10 frames
                service.process_single_frame(frame)
            
            end_time = time.time()
            avg_time = (end_time - start_time) / 10
            
            # Should process frame in reasonable time (< 100ms with mocks)
            assert avg_time < 0.1
            
            print(f"Average frame processing time: {avg_time:.3f}s")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
    print("✅ All tests completed")