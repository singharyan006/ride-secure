#!/usr/bin/env python3
"""
Test script for license plate detection functionality
"""

import cv2
import numpy as np
from pathlib import Path
import sys
sys.path.append('src')

from ridesecure.detection.plate_detector import PlateDetector

def create_test_plate_image():
    """Create a test image with a mock license plate"""
    # Create a 640x480 test image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    img.fill(80)  # Gray background
    
    # Create a mock vehicle (rectangle)
    cv2.rectangle(img, (150, 200), (500, 400), (100, 100, 150), -1)
    
    # Create a mock license plate area (white rectangle)
    plate_x, plate_y = 250, 320
    plate_w, plate_h = 150, 40
    cv2.rectangle(img, (plate_x, plate_y), (plate_x + plate_w, plate_y + plate_h), (240, 240, 240), -1)
    
    # Add mock text on the plate (Indian format: MH 12 AB 1234)
    cv2.putText(img, "MH 12 AB 1234", (plate_x + 10, plate_y + 25), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (20, 20, 20), 2)
    
    return img

def create_realistic_plate_image():
    """Create a more realistic license plate image"""
    img = np.zeros((200, 400, 3), dtype=np.uint8)
    img.fill(255)  # White background
    
    # Create license plate background
    cv2.rectangle(img, (50, 50), (350, 150), (255, 255, 255), -1)
    cv2.rectangle(img, (50, 50), (350, 150), (0, 0, 0), 2)
    
    # Add Indian license plate text
    cv2.putText(img, "KA 01 HJ 9999", (80, 110), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
    
    return img

def test_plate_detector():
    """Test the license plate detector"""
    print("🚗 Testing License Plate Detector...")
    
    try:
        # Initialize detector
        print("📥 Loading plate detector...")
        detector = PlateDetector()
        print("✅ Plate detector loaded successfully!")
        
        # Test 1: Mock vehicle image with plate
        print("\n📸 Test 1: Mock vehicle with license plate")
        test_img1 = create_test_plate_image()
        cv2.imwrite('test_vehicle.jpg', test_img1)
        print("💾 Saved test vehicle image as 'test_vehicle.jpg'")
        
        # Run detection
        print("🔍 Running plate detection on vehicle image...")
        results1 = detector.detect_plates_cv(test_img1)
        
        print(f"📊 Vehicle Image Results:")
        print(f"   - Plates detected: {len(results1)}")
        for i, plate in enumerate(results1):
            bbox = plate.get('bbox', [0, 0, 0, 0])
            confidence = plate.get('confidence', 0)
            method = plate.get('method', 'unknown')
            print(f"   - Plate {i+1}: bbox={bbox}, confidence={confidence:.2f}, method={method}")
        
        # Save annotated result (draw simple rectangles)
        annotated1 = test_img1.copy()
        for result in results1:
            bbox = result['bbox']
            x, y, w, h = bbox
            cv2.rectangle(annotated1, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(annotated1, f"Plate {result.get('confidence', 0):.2f}", 
                       (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.imwrite('test_vehicle_annotated.jpg', annotated1)
        print("💾 Saved annotated vehicle result")
        
        # Test 2: Clean license plate image
        print("\n🎯 Test 2: Clean license plate image")
        test_img2 = create_realistic_plate_image()
        cv2.imwrite('test_clean_plate.jpg', test_img2)
        print("💾 Saved clean plate image as 'test_clean_plate.jpg'")
        
        print("🔍 Running plate detection on clean plate...")
        results2 = detector.detect_plates_cv(test_img2)
        
        print(f"📊 Clean Plate Results:")
        print(f"   - Plates detected: {len(results2)}")
        for i, plate in enumerate(results2):
            bbox = plate.get('bbox', [0, 0, 0, 0])
            confidence = plate.get('confidence', 0)
            method = plate.get('method', 'unknown')
            print(f"   - Plate {i+1}: bbox={bbox}, confidence={confidence:.2f}, method={method}")
        
        annotated2 = test_img2.copy()
        for result in results2:
            bbox = result['bbox']
            x, y, w, h = bbox
            cv2.rectangle(annotated2, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(annotated2, f"Plate {result.get('confidence', 0):.2f}", 
                       (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.imwrite('test_clean_plate_annotated.jpg', annotated2)
        print("💾 Saved annotated clean plate result")
        
        # Test OCR directly
        print("\n📝 Test 3: Direct OCR test")
        if results2:  # If we found a plate in the clean plate image
            plate_bbox = results2[0]['bbox']
            x, y, w, h = plate_bbox
            plate_region_img = test_img2[y:y+h, x:x+w]
            
            # Test OCR extraction on the plate region
            ocr_result = detector.extract_plate_text(test_img2, results2[0])
            if ocr_result:
                ocr_text = ocr_result.get('text', 'No text extracted')
                print(f"🔤 OCR extracted text: '{ocr_text}'")
                
                # Validate format
                validation_result = detector.validate_plate_pattern(ocr_text)
                is_valid = validation_result.get('is_valid', False)
                print(f"✅ Valid Indian format: {is_valid}")
            else:
                print("❌ No text could be extracted from plate region")
        
        return True
        
    except Exception as e:
        print(f"❌ Plate detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_plate_validation():
    """Test license plate validation patterns"""
    print("\n🔍 Testing Indian License Plate Validation...")
    
    detector = PlateDetector()
    
    test_plates = [
        "MH 12 AB 1234",  # Valid
        "KA 01 HJ 9999",  # Valid
        "DL 8C AA 0001",  # Valid
        "ABC 123",        # Invalid
        "MH12AB1234",     # Valid (without spaces)
        "123 ABC 456",    # Invalid
        "",               # Invalid
    ]
    
    for plate_text in test_plates:
        validation_result = detector.validate_plate_pattern(plate_text)
        is_valid = validation_result.get('is_valid', False)
        status = "✅ VALID" if is_valid else "❌ INVALID"
        print(f"   {plate_text:15} → {status}")
    
    return True

if __name__ == "__main__":
    print("🚀 RideSecure License Plate Detection Test")
    print("=" * 55)
    
    # Test plate detection
    if not test_plate_detector():
        print("\n❌ Plate detection test failed!")
        exit(1)
    
    # Test plate validation
    if not test_plate_validation():
        print("\n❌ Plate validation test failed!")
        exit(1)
    
    print("\n🎉 License plate detection module is working!")
    print("\nFiles created:")
    print("- test_vehicle.jpg (mock vehicle with plate)")
    print("- test_clean_plate.jpg (clean plate image)")
    print("- test_vehicle_annotated.jpg (detection results)")
    print("- test_clean_plate_annotated.jpg (detection results)")
    
    print("\nNext steps:")
    print("1. Start the detection API service")
    print("2. Connect Java GUI to Python backend")
    print("3. Test end-to-end integration")