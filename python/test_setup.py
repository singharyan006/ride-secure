#!/usr/bin/env python3
"""
Test script to verify ML environment setup and dependencies
"""

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing ML environment setup...")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
    except ImportError as e:
        print(f"❌ PyTorch import failed: {e}")
        return False
    
    try:
        import cv2
        print(f"✅ OpenCV {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV import failed: {e}")
        return False
    
    try:
        import ultralytics
        print(f"✅ Ultralytics (YOLO)")
    except ImportError as e:
        print(f"❌ Ultralytics import failed: {e}")
        return False
    
    try:
        import easyocr
        print(f"✅ EasyOCR")
    except ImportError as e:
        print(f"❌ EasyOCR import failed: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✅ NumPy {np.__version__}")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    return True

def test_yolo_model():
    """Test YOLO model loading"""
    print("\n🔍 Testing YOLO model...")
    
    try:
        from ultralytics import YOLO
        
        # This will download the model if not present
        print("📥 Loading YOLOv8 model...")
        model = YOLO('yolov8n.pt')  # nano version for quick testing
        print("✅ YOLO model loaded successfully")
        
        # Test with a dummy image
        import numpy as np
        dummy_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        results = model(dummy_image, verbose=False)
        print("✅ YOLO inference test passed")
        
        return True
    except Exception as e:
        print(f"❌ YOLO test failed: {e}")
        return False

def test_our_modules():
    """Test our custom detection modules"""
    print("\n🎯 Testing RideSecure detection modules...")
    
    try:
        from src.ridesecure.detection.helmet_detector import HelmetDetector
        print("✅ HelmetDetector import successful")
        
        from src.ridesecure.detection.plate_detector import PlateDetector
        print("✅ PlateDetector import successful")
        
        from src.ridesecure.detection.detection_service import DetectionService
        print("✅ DetectionService import successful")
        
        return True
    except Exception as e:
        print(f"❌ Module import failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 RideSecure ML Environment Test")
    print("=" * 50)
    
    # Test basic imports
    if not test_imports():
        print("\n❌ Basic imports failed. Please install missing dependencies.")
        exit(1)
    
    # Test YOLO
    if not test_yolo_model():
        print("\n❌ YOLO model test failed.")
        exit(1)
    
    # Test our modules
    if not test_our_modules():
        print("\n❌ Custom module test failed.")
        exit(1)
    
    print("\n🎉 All tests passed! Your ML environment is ready.")
    print("\nNext steps:")
    print("1. Run helmet detection test: python -m src.ridesecure.detection.helmet_detector")
    print("2. Run plate detection test: python -m src.ridesecure.detection.plate_detector")
    print("3. Start detection API: python -m src.ridesecure.api.detection_api")