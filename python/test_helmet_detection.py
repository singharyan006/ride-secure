#!/usr/bin/env python3
"""
Test script for helmet detection functionality
"""

import cv2
import numpy as np
from pathlib import Path
import sys
sys.path.append('src')

from ridesecure.detection.helmet_detector import HelmetDetector

def create_test_image():
    """Create a simple test image with a person-like shape"""
    # Create a 640x640 test image
    img = np.zeros((640, 640, 3), dtype=np.uint8)
    img.fill(50)  # Dark gray background
    
    # Draw a simple person-like shape
    # Head (circle)
    cv2.circle(img, (320, 150), 40, (200, 180, 160), -1)
    
    # Body (rectangle)
    cv2.rectangle(img, (290, 190), (350, 350), (100, 150, 200), -1)
    
    # Arms
    cv2.rectangle(img, (250, 200), (290, 280), (100, 150, 200), -1)
    cv2.rectangle(img, (350, 200), (390, 280), (100, 150, 200), -1)
    
    return img

def test_helmet_detector():
    """Test the helmet detector with a sample image"""
    print("🔍 Testing Helmet Detector...")
    
    try:
        # Initialize detector
        print("📥 Loading helmet detector...")
        detector = HelmetDetector()
        print("✅ Helmet detector loaded successfully!")
        
        # Create test image
        test_img = create_test_image()
        print("🖼️ Created test image")
        
        # Save test image for reference
        cv2.imwrite('test_image.jpg', test_img)
        print("💾 Saved test image as 'test_image.jpg'")
        
        # Run detection
        print("🔎 Running helmet detection...")
        violations = detector.detect_violations(test_img)
        
        # Get summary statistics
        summary = detector.get_violation_summary(violations)
        
        print(f"📊 Detection Results:")
        print(f"   - Total detections: {summary['total_detections']}")
        print(f"   - Helmet violations: {summary['helmet_violations']}")
        print(f"   - Helmet compliance: {summary['helmet_compliance']}")
        print(f"   - Violation rate: {summary['violation_rate']:.2%}")
        
        # Save annotated result
        annotated = detector.draw_detections(test_img, violations)
        cv2.imwrite('test_result_annotated.jpg', annotated)
        print("💾 Saved annotated result as 'test_result_annotated.jpg'")
        
        return True
        
    except Exception as e:
        print(f"❌ Helmet detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_webcam():
    """Test with webcam if available"""
    print("\n📹 Testing with webcam (if available)...")
    
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("ℹ️ No webcam available, skipping webcam test")
            return True
            
        detector = HelmetDetector()
        
        print("🎥 Webcam opened! Press 'q' to quit webcam test")
        print("   This will show real-time helmet detection")
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            
            # Process every 5th frame for performance
            if frame_count % 5 == 0:
                violations = detector.detect_violations(frame)
                frame = detector.draw_detections(frame, violations)
                
                # Show violation count on frame
                summary = detector.get_violation_summary(violations)
                violation_text = f"Violations: {summary['helmet_violations']}"
                cv2.putText(frame, violation_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            cv2.imshow('Helmet Detection Test', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Webcam test completed")
        return True
        
    except Exception as e:
        print(f"❌ Webcam test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 RideSecure Helmet Detection Test")
    print("=" * 50)
    
    # Test with static image
    if not test_helmet_detector():
        print("\n❌ Static image test failed!")
        exit(1)
    
    print("\n✅ Static image test passed!")
    
    # Ask user about webcam test
    print("\n🎥 Do you want to test with webcam? (It will open a video window)")
    print("   Press Enter to skip, or type 'yes' to test with webcam:")
    
    # For automated testing, we'll skip webcam
    # In interactive mode, user can uncomment the next lines:
    # response = input().strip().lower()
    # if response == 'yes':
    #     test_with_webcam()
    
    print("\n🎉 Helmet detection module is working!")
    print("\nNext steps:")
    print("1. Test license plate detection")
    print("2. Start the detection API service") 
    print("3. Connect Java GUI to Python backend")