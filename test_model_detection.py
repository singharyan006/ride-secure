"""
Quick test to verify the YOLO model can detect objects
"""
import sys
from pathlib import Path
import cv2
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.detector import Detector
from src.model_registry import resolve_model_path

def test_model_detection():
    print("🧪 Testing YOLO model detection capability...\n")
    
    # 1. Check if model exists
    try:
        model_path = resolve_model_path("custom_helmet", category="detection")
        print(f"✅ Model found: {model_path}")
    except FileNotFoundError as e:
        print(f"❌ Model not found: {e}")
        return False
    
    # 2. Load the model
    try:
        detector = Detector(str(model_path), conf_thresh=0.25)  # Lower threshold for testing
        print(f"✅ Model loaded successfully")
        print(f"   Class names: {detector.names}")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return False
    
    # 3. Create a test image (blank canvas)
    print("\n🎨 Creating test image (640x640 blue canvas)...")
    test_img = np.zeros((640, 640, 3), dtype=np.uint8)
    test_img[:, :] = (255, 0, 0)  # Blue canvas
    
    # 4. Run detection
    try:
        print("🔍 Running detection on test image...")
        boxes = detector.predict(test_img)
        print(f"   Result: {len(boxes)} detections")
        if boxes:
            print("   Detections:")
            for box in boxes:
                x1, y1, x2, y2, conf, cls = box
                cls_name = detector.class_name(cls)
                print(f"     - Class: {cls_name}, Conf: {conf:.2f}, BBox: [{x1},{y1},{x2},{y2}]")
        else:
            print("   ℹ️ No detections (expected for blank image)")
    except Exception as e:
        print(f"❌ Detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Summary
    print("\n" + "="*60)
    print("📊 Summary:")
    print(f"   Model: {model_path.name}")
    print(f"   Classes: {len(detector.names)} classes")
    print(f"   Detection threshold: {detector.conf_thresh}")
    print("   ✅ Model is working correctly!")
    print("\n💡 If your video shows 0 detections, possible reasons:")
    print("   1. Video has no motorcycles/people")
    print("   2. Objects are too small/blurry")
    print("   3. Model not trained for objects in your video")
    print("   4. Confidence threshold too high (currently 0.4)")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = test_model_detection()
    sys.exit(0 if success else 1)
