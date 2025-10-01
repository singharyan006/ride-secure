# RideSecure Python ML Backend

This folder contains the machine learning backend and API for the RideSecure helmet and license plate detection system.

## Structure Overview

```
python/
├── notebooks/                # (Empty) For Jupyter notebooks and experiments
├── pyproject.toml            # Project configuration and dependencies
├── setup_ml.py               # ML environment/model setup script
├── src/
│   └── ridesecure/
│       ├── api/
│       │   ├── detection_api.py   # REST API for detection endpoints
│       │   └── __init__.py        # Package marker
│       ├── detection/
│       │   ├── detection_service.py   # Orchestrates detection workflow
│       │   ├── helmet_detector.py     # Helmet detection logic (YOLO, etc.)
│       │   ├── plate_detector.py      # License plate detection logic
│       │   └── __init__.py           # Package marker
│       └── __init__.py               # Package marker
│   └── ridesecure_ml.egg-info/       # Installed package metadata
├── tests/
│   ├── test_detection.py         # Unit/integration tests for detection
│   └── __init__.py               # Package marker
├── test_clean_plate.jpg          # Test image (clean plate)
├── test_clean_plate_annotated.jpg# Annotated test image
├── test_helmet_detection.py      # Test script for helmet detection
├── test_image.jpg                # General test image
├── test_plate_detection.py       # Test script for plate detection
├── test_result_annotated.jpg     # Annotated result image
├── test_setup.py                 # Test script for setup
├── test_vehicle.jpg              # Test image (vehicle)
├── test_vehicle_annotated.jpg    # Annotated vehicle image
├── venv/                         # Python virtual environment
└── yolov8n.pt                    # YOLOv8 model weights
```

## Main Components

- **API** (`src/ridesecure/api/detection_api.py`):
  - Provides REST endpoints for helmet and plate detection.
- **Detection Logic** (`src/ridesecure/detection/`):
  - `detection_service.py`: Orchestrates detection workflow.
  - `helmet_detector.py`: Helmet detection using ML models (YOLO).
  - `plate_detector.py`: License plate detection and recognition.
- **Tests** (`tests/` and test scripts):
  - Unit and integration tests for detection pipeline.
  - Test images for validation and annotation.
- **Model Weights** (`yolov8n.pt`):
  - YOLOv8 weights for helmet detection.
- **Environment** (`venv/`, `pyproject.toml`, `setup_ml.py`):
  - Virtual environment and setup/configuration scripts.

## Usage

1. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
2. **Run API server**:
   ```sh
   python src/ridesecure/api/detection_api.py
   ```
3. **Test detection**:
   - Use provided test scripts and images for validation.

## Notes
- Place your YOLO model weights (`yolov8n.pt`) in the root of the `python` folder.
- Use the `setup_ml.py` script to initialize or update ML models as needed.
- Jupyter notebooks can be added to the `notebooks/` folder for experiments.

---

For more details, see the source code in each module or ask for specific file explanations.