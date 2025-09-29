#!/usr/bin/env python3
"""
RideSecure ML Foundation Setup Script
Installs dependencies and sets up the development environment
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def setup_virtual_environment():
    """Create and activate virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("📁 Virtual environment already exists")
        return True
    
    print("🔧 Creating virtual environment...")
    
    # Create virtual environment
    if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
        return False
    
    print("✅ Virtual environment created at ./venv")
    print("💡 Activate it with:")
    if os.name == 'nt':  # Windows
        print("   .\\venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source venv/bin/activate")
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    
    # Determine pip command
    pip_cmd = "pip"
    if os.name == 'nt':  # Windows
        if Path("venv/Scripts/pip.exe").exists():
            pip_cmd = "venv\\Scripts\\pip.exe"
    else:  # Unix/Linux/macOS
        if Path("venv/bin/pip").exists():
            pip_cmd = "venv/bin/pip"
    
    # Upgrade pip first
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install from pyproject.toml
    if not run_command(f"{pip_cmd} install -e .", "Installing RideSecure package"):
        return False
    
    return True

def download_yolo_model():
    """Download YOLO model for initial testing"""
    print("🤖 Downloading YOLO model...")
    
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # Download YOLOv8 nano model (smallest for testing)
    python_cmd = "python"
    if os.name == 'nt' and Path("venv/Scripts/python.exe").exists():
        python_cmd = "venv\\Scripts\\python.exe"
    elif Path("venv/bin/python").exists():
        python_cmd = "venv/bin/python"
    
    download_script = '''
import torch
from ultralytics import YOLO

# Download YOLOv8n model
model = YOLO("yolov8n.pt")
print("✅ YOLO model downloaded successfully")
'''
    
    try:
        subprocess.run([python_cmd, "-c", download_script], check=True)
        print("✅ YOLO model ready")
        return True
    except subprocess.CalledProcessError:
        print("⚠️ YOLO model download failed (will download on first use)")
        return True  # Not critical for setup

def create_sample_directories():
    """Create sample data directories"""
    print("📁 Creating directory structure...")
    
    directories = [
        "data/videos",
        "data/images", 
        "data/test_images",
        "models",
        "output/results",
        "output/annotations"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directory structure created")

def run_basic_tests():
    """Run basic import tests"""
    print("🧪 Running basic tests...")
    
    python_cmd = "python"
    if os.name == 'nt' and Path("venv/Scripts/python.exe").exists():
        python_cmd = "venv\\Scripts\\python.exe"
    elif Path("venv/bin/python").exists():
        python_cmd = "venv/bin/python"
    
    test_script = '''
try:
    import cv2
    print("✅ OpenCV imported")
except ImportError as e:
    print(f"❌ OpenCV import failed: {e}")

try:
    import torch
    print(f"✅ PyTorch {torch.__version__} imported")
    print(f"   CUDA available: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"❌ PyTorch import failed: {e}")

try:
    from ultralytics import YOLO
    print("✅ YOLO imported")
except ImportError as e:
    print(f"❌ YOLO import failed: {e}")

try:
    import easyocr
    print("✅ EasyOCR imported")
except ImportError as e:
    print(f"❌ EasyOCR import failed: {e}")

try:
    from ridesecure.detection import DetectionService
    print("✅ RideSecure package imported")
except ImportError as e:
    print(f"❌ RideSecure import failed: {e}")

print("🎉 Basic tests completed")
'''
    
    try:
        subprocess.run([python_cmd, "-c", test_script], check=True)
        return True
    except subprocess.CalledProcessError:
        print("⚠️ Some tests failed - check error messages above")
        return False

def print_next_steps():
    """Print next steps for user"""
    print("\n" + "="*60)
    print("🎉 RideSecure ML Foundation Setup Complete!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Activate virtual environment:")
    if os.name == 'nt':
        print("   .\\venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2. Test the detection modules:")
    print("   python -m ridesecure.detection.helmet_detector")
    print("   python -m ridesecure.detection.plate_detector")
    print("   python -m ridesecure.detection.detection_service")
    
    print("\n3. Run the API server:")
    print("   python src/ridesecure/api/detection_api.py")
    
    print("\n4. Run tests:")
    print("   python -m pytest tests/ -v")
    
    print("\n🔧 Development Commands:")
    print("   - Install new packages: pip install <package>")
    print("   - Update dependencies: pip install -e .")
    print("   - Format code: black src/")
    print("   - Type check: mypy src/")
    
    print("\n📁 Directory Structure:")
    print("   data/videos/     - Place video files here")
    print("   data/images/     - Place image files here") 
    print("   models/          - ML models stored here")
    print("   output/          - Processing results")
    
    print("\n🔗 Integration:")
    print("   - Java app can call Python API at http://localhost:5000")
    print("   - Use /java/detect endpoint for RideSecureSwingApp")

def main():
    """Main setup function"""
    print("🚀 Setting up RideSecure ML Foundation...")
    print("="*60)
    
    # Check requirements
    if not check_python_version():
        sys.exit(1)
    
    # Setup steps
    steps = [
        (setup_virtual_environment, "Virtual Environment Setup"),
        (create_sample_directories, "Directory Structure"),
        (install_dependencies, "Dependencies Installation"), 
        (download_yolo_model, "YOLO Model Download"),
        (run_basic_tests, "Basic Tests")
    ]
    
    success_count = 0
    for step_func, step_name in steps:
        print(f"\n📍 {step_name}")
        print("-" * 40)
        
        if step_func():
            success_count += 1
        else:
            print(f"⚠️ {step_name} encountered issues")
    
    print(f"\n📊 Setup Summary: {success_count}/{len(steps)} steps completed")
    
    if success_count == len(steps):
        print_next_steps()
    else:
        print("\n⚠️ Setup completed with some issues. Check error messages above.")
        print("You may need to manually install some dependencies.")

if __name__ == "__main__":
    main()