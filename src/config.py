from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # ride_secure/
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# default subpaths
ANNOTATED_DIR = OUTPUTS_DIR / "annotated_videos"
CSV_DIR = OUTPUTS_DIR / "csv_logs"

# ensure output directories exist
ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)
CSV_DIR.mkdir(parents=True, exist_ok=True)

# Detection defaults
DEFAULT_COCO_MODEL = "yolov8n"      # name under models/detection/... or path
DEFAULT_HELMET_MODEL = "custom_helmet"
DEFAULT_CONF = 0.4
DEFAULT_HEAD_FRACTION = 0.35
DEFAULT_HELMET_IOU = 0.1
DEFAULT_LOG_REPEAT_FRAMES = 30
