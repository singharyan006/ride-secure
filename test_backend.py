#!/usr/bin/env python3
"""
Test script to verify Python ML backend is ready for frontend integration
"""
import sys
import requests
from pathlib import Path

API_URL = "http://127.0.0.1:8000"

def test_health():
    """Test /health endpoint"""
    print("🔍 Testing /health endpoint...")
    try:
        resp = requests.get(f"{API_URL}/health", timeout=5)
        if resp.status_code == 200:
            print(f"✅ Health check passed: {resp.json()}")
            return True
        else:
            print(f"❌ Health check failed: {resp.status_code} {resp.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {API_URL} - is the backend running?")
        print("   Start with: python -m src.api")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_models():
    """Test /models endpoint"""
    print("\n🔍 Testing /models endpoint...")
    try:
        resp = requests.get(f"{API_URL}/models", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Available models: {data}")
            if "custom_helmet" in data.get("models", []):
                print("   ✅ custom_helmet model registered")
                return True
            else:
                print("   ⚠️ custom_helmet model not found")
                return False
        else:
            print(f"❌ Models endpoint failed: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Models check error: {e}")
        return False

def test_predict_frame():
    """Test /predict/frame endpoint with dummy image"""
    print("\n🔍 Testing /predict/frame endpoint...")
    
    # Create a small test image
    try:
        from PIL import Image
        import io
        
        # Create 640x640 test image
        img = Image.new('RGB', (640, 640), color='blue')
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        buf.seek(0)
        
        files = {'file': ('test.jpg', buf, 'image/jpeg')}
        data = {'model': 'custom_helmet'}
        
        print(f"   📤 POSTing test image to {API_URL}/predict/frame...")
        resp = requests.post(f"{API_URL}/predict/frame", files=files, data=data, timeout=30)
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"✅ Prediction successful!")
            print(f"   Filename: {result.get('filename')}")
            print(f"   Detections: {len(result.get('detections', []))} object(s)")
            
            # Show first detection details
            if result.get('detections'):
                det = result['detections'][0]
                print(f"   First detection: {det}")
            
            return True
        else:
            print(f"❌ Prediction failed: {resp.status_code} {resp.text}")
            return False
            
    except ImportError:
        print("   ⚠️ PIL not installed, skipping /predict/frame test")
        print("   Install with: pip install Pillow")
        return None
    except Exception as e:
        print(f"❌ Prediction test error: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 RideSecure Python Backend Integration Test")
    print("=" * 60)
    
    results = []
    
    # Test 1: Health
    results.append(("Health Check", test_health()))
    
    # Test 2: Models
    results.append(("Models List", test_models()))
    
    # Test 3: Prediction
    pred_result = test_predict_frame()
    if pred_result is not None:
        results.append(("Prediction API", pred_result))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} | {name}")
    
    print(f"\n{passed} passed, {failed} failed out of {len(results)} tests")
    
    if all(r for _, r in results):
        print("\n🎉 All tests passed! Backend is ready for frontend integration.")
        print("\n📝 Next steps:")
        print("   1. Keep Python backend running (python -m src.api)")
        print("   2. Build Java frontend: cd java && mvn clean package")
        print("   3. Run JavaFX app: cd java && .\\runfx.bat")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check backend configuration.")
        print("\n🔧 Troubleshooting:")
        print("   - Ensure backend is running: python -m src.api")
        print("   - Check model path: models/detection/custom_helmet/weights.pt")
        print("   - Verify dependencies: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
