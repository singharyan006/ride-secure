# 🛡️ RideSecure - Intelligent Helmet Detection System

> **A hybrid JavaFX desktop + Python ML backend for real-time motorcycle helmet violation detection**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Java](https://img.shields.io/badge/Java-17+-orange.svg)](https://openjdk.java.net/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![JavaFX](https://img.shields.io/badge/JavaFX-17.0.2-green.svg)](https://openjfx.io/)

## 🎯 Project Overview

RideSecure is an intelligent computer vision system that automatically detects motorcycle riders without helmets from video footage and maintains comprehensive violation records. The system uses a modern architecture with a JavaFX desktop frontend and a Python FastAPI backend powered by YOLOv8 and DeepSORT tracking.

### 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              JavaFX Desktop Application             │
│  (Video Upload, Violation Display, Playback)        │
└────────────────┬────────────────────────────────────┘
                 │ HTTP API
                 ▼
┌─────────────────────────────────────────────────────┐
│           Python FastAPI Backend                    │
│  - YOLOv8 Person Detection                          │
│  - Custom Helmet Detection                          │
│  - DeepSORT Multi-Object Tracking                   │
│  - Video Annotation & Processing                    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│           Supabase PostgreSQL Database              │
│  (Violation Records, Track IDs, Timestamps)         │
└─────────────────────────────────────────────────────┘
```

### 🔧 Technology Stack

**Frontend (Java):**
- **UI Framework:** JavaFX 17.0.2
- **HTTP Client:** OkHttp3 4.10.0
- **JSON Processing:** Jackson 2.14.2
- **Database:** PostgreSQL JDBC Driver
- **Build Tool:** Maven 3.8+

**Backend (Python):**
- **Web Framework:** FastAPI + Uvicorn
- **ML Detection:** Ultralytics YOLOv8
- **Tracking:** DeepSORT
- **Video Processing:** OpenCV (cv2)
- **Database ORM:** Supabase Python Client
- **Package Manager:** uv

## 📁 Project Structure

```
RideSecure/
├── 📁 java/                          # JavaFX Desktop Application
│   ├── 📄 pom.xml                   # Maven dependencies
│   └── 📁 src/main/
│       ├── 📁 java/com/ridesecure/
│       │   ├── 📄 RideSecureApp.java           # Application entry point
│       │   ├── 📁 controllers/
│       │   │   ├── 📄 LandingController.java   # Landing page
│       │   │   └── 📄 MainController.java      # Main detection page
│       │   ├── 📁 models/
│       │   │   └── 📄 Violation.java           # Violation data model
│       │   ├── 📁 services/
│       │   │   ├── � APIService.java          # Python backend client
│       │   │   └── � DatabaseService.java     # Database operations
│       │   └── 📁 config/
│       │       └── 📄 EnvConfig.java            # Environment variables
│       └── 📁 resources/
│           ├── � fxml/                        # UI layouts
│           │   ├── 📄 Landing.fxml
│           │   └── 📄 Main.fxml
│           └── 📁 css/
│               └── 📄 main.css                 # Stylesheets
│
├── 📁 src/                           # Python Backend API
│   ├── 📄 __init__.py
│   ├── � api.py                    # FastAPI endpoints
│   ├── � detector.py               # YOLOv8 detection logic
│   ├── � tracker.py                # DeepSORT tracking
│   ├── � video_io.py               # Video processing
│   ├── � database.py               # Supabase client
│   ├── � config.py                 # Configuration management
│   ├── 📄 logger.py                 # Logging setup
│   ├── � model_registry.py         # Model loading
│   ├── � utils.py                  # Utility functions
│   └── 📄 cli.py                    # CLI interface
│
├── 📁 models/                        # ML Model Weights
│   ├── � models.json               # Model configuration
│   └── 📁 detection/
│       ├── 📁 yolov8n/              # Person detection
│       │   └── � weights.pt
│       └── 📁 custom_helmet/        # Helmet detection
│           └── � weights.pt
│
├── 📁 database/                      # Database Setup
│   ├── 📁 schema/
│   │   └── 📄 init.sql              # Database initialization
│   └── � migrations/               # Migration scripts
│
├── 📁 docs/                          # Documentation
│   └── � API_CLIENT.md             # API documentation
│
├── 📁 outputs/                       # Generated Outputs (gitignored)
│   ├── 📁 annotated_videos/         # Processed videos
│   └── 📁 csv_logs/                 # Violation logs
│
├── � .env.example                  # Environment variables template
├── 📄 .python-version               # Python version (3.11)
├── 📄 requirements.txt              # Python dependencies
├── � pyproject.toml                # Python project config (uv)
├── � uv.lock                       # Dependency lock file
├── � test_backend.py               # Backend API tests
├── 📄 test_model_detection.py       # Model inference tests
├── 📄 QUICK_START.md                # Quick start guide
├── 📄 CONTRIBUTING.md               # Contribution guidelines
└── 📄 README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- **Java 17+** (OpenJDK recommended)
- **Python 3.11+** with pip or uv
- **Maven 3.8+**
- **PostgreSQL** (Supabase account)
- **Git**

### 1. Clone Repository

```bash
git clone https://github.com/singharyan006/ride-secure.git
cd ride-secure
```

### 2. Setup Environment Variables

```bash
# Copy and configure environment file
cp .env.example .env

# Edit .env with your credentials:
# - SUPABASE_URL
# - SUPABASE_KEY
# - DATABASE_URL (PostgreSQL connection string)
```

### 3. Initialize Database

```bash
# Run the initialization script on your Supabase database
# Execute the SQL in database/schema/init.sql
```

### 4. Setup Python Backend

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt

# Start the FastAPI server
uvicorn src.api:app --reload --host 127.0.0.1 --port 8000
```

### 5. Run JavaFX Desktop App

```bash
cd java
mvn clean compile
mvn javafx:run
```

### 6. Process Videos

1. Click "Start Detection" on the landing page
2. Select a video file (MP4, AVI, MOV, MKV)
3. Backend processes the video with helmet detection
4. View violations in the table
5. Double-click to play annotated video in system player

For detailed instructions, see [QUICK_START.md](QUICK_START.md).

## 🔄 Workflow

### Detection Pipeline

1. **Video Upload**: User selects video through JavaFX interface
2. **API Request**: Java app sends video to Python backend via HTTP
3. **Frame Processing**: Backend processes each frame:
   - YOLOv8n detects persons in frame
   - Custom model detects helmets on detected persons
   - DeepSORT tracks each person across frames with unique track_id
4. **Violation Detection**: If helmet not detected for 30+ consecutive frames
5. **Database Logging**: Violations stored in Supabase with:
   - Track ID, frame number, timestamp
   - Detection confidence scores
   - Video filename and session info
6. **Video Annotation**: Annotated video created with:
   - RED bounding boxes = No helmet detected
   - GREEN bounding boxes = Helmet present
7. **Playback**: Annotated video opens in system default player (VLC/Windows Media Player)

### Detection Logic

```python
# Real-time helmet status tracking
track_helmet_status = {}  # {track_id: helmet_present}

for frame_idx, frame in enumerate(video):
    persons = detect_persons(frame)  # YOLOv8n
    
    for person in persons:
        track_id = tracker.update(person)
        helmet_present = detect_helmet(person.bbox)
        
        # Update real-time status
        track_helmet_status[track_id] = helmet_present
        
        # Log violation every 30 frames if no helmet
        if not helmet_present and frame_idx % 30 == 0:
            log_violation(track_id, frame_idx)
        
        # Annotate based on real-time status
        color = GREEN if helmet_present else RED
        draw_bbox(frame, person.bbox, color)
```

## 🏃‍♂️ Running the Application

### Development Mode

```bash
# Terminal 1: Start Python backend
cd ride-secure
uvicorn src.api:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Run JavaFX app
cd java
mvn javafx:run
```

### Production Mode

```bash
# Build standalone JAR
cd java
mvn clean package

# Run the application
java -jar target/ridesecure-1.0-SNAPSHOT.jar
```

### API Endpoints

The Python backend exposes:
- `POST /process-video/` - Upload and process video
- `GET /health` - Health check
- `GET /violations/` - Query violations

See [docs/API_CLIENT.md](docs/API_CLIENT.md) for detailed API documentation.

## 🧪 Testing

### Python Backend Tests

```bash
# Test API endpoints
python test_backend.py

# Test model detection
python test_model_detection.py
```

### Java Unit Tests

```bash
cd java
mvn test
```

### Manual Integration Test

1. Start Python backend: `uvicorn src.api:app --reload`
2. Run Java app: `cd java && mvn javafx:run`
3. Upload test video through UI
4. Verify violations appear in table
5. Check annotated video plays correctly

## � Configuration

### Environment Variables (`.env`)

```bash
# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# PostgreSQL Connection
DATABASE_URL=postgresql://user:password@host:port/database

# Python Backend
API_PORT=8000
API_HOST=127.0.0.1
```

### Model Configuration (`models/models.json`)

```json
{
  "person_detection": {
    "model_path": "models/detection/yolov8n/weights.pt",
    "confidence": 0.5
  },
  "helmet_detection": {
    "model_path": "models/detection/custom_helmet/weights.pt",
    "confidence": 0.6
  }
}
```

### Detection Thresholds

Adjust in `src/config.py`:
- `PERSON_CONFIDENCE_THRESHOLD = 0.5` - Person detection sensitivity
- `HELMET_CONFIDENCE_THRESHOLD = 0.6` - Helmet detection sensitivity
- `VIOLATION_LOG_INTERVAL = 30` - Frames between violation logs

## � Performance Considerations

### Hardware Recommendations

- **CPU**: Intel i5-8400 / AMD Ryzen 5 2600 or better
- **RAM**: 8GB minimum, 16GB recommended for HD videos
- **GPU**: Optional (NVIDIA CUDA support for faster inference)
- **Storage**: SSD recommended for video I/O

### Optimization Tips

- Process videos at 15-30 FPS for real-time performance
- Use smaller input resolution for faster processing
- Adjust confidence thresholds to balance accuracy vs speed
- GPU acceleration can provide 3-5x speedup

## 📋 Roadmap

### ✅ Phase 1: Core System (Completed)
- [x] YOLOv8 person and helmet detection
- [x] DeepSORT multi-object tracking
- [x] FastAPI backend with video processing
- [x] JavaFX desktop frontend
- [x] Supabase PostgreSQL integration
- [x] Annotated video output with color-coded boxes

### 🚧 Phase 2: Enhancement (In Progress)
- [ ] Real-time camera/RTSP stream support
- [ ] License plate detection and OCR
- [ ] Advanced analytics dashboard
- [ ] Batch video processing queue
- [ ] Export reports (PDF, CSV, Excel)

### 🔮 Phase 3: Production (Planned)
- [ ] Web-based admin dashboard
- [ ] Mobile application (Android/iOS)
- [ ] Cloud deployment support
- [ ] Edge device deployment
- [ ] Advanced violation classification

## 🛠️ Troubleshooting

### Common Issues

**Python Backend Not Starting**
```bash
# Check if port 8000 is available
netstat -ano | findstr :8000

# Install dependencies
pip install -r requirements.txt
```

**JavaFX Module Errors**
```bash
# Ensure JAVA_HOME is set to Java 17+
java --version

# Clean and rebuild
cd java
mvn clean install
```

**Database Connection Errors**
- Verify `.env` file has correct Supabase credentials
- Check database schema is initialized (`database/schema/init.sql`)
- Test connection: `psql $DATABASE_URL`

**Video Not Playing**
- Annotated videos open in system default player
- Ensure VLC or Windows Media Player is installed
- Check `outputs/annotated_videos/` for generated files

**Detection Not Working**
- Verify model weights exist in `models/detection/*/weights.pt`
- Check Python backend logs for errors
- Test models: `python test_model_detection.py`

## 🤝 Contributing

We encourage contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for:

- **Development Setup**: Environment configuration
- **Coding Standards**: Java and Python style guides
- **Testing Requirements**: Unit and integration tests
- **Pull Request Process**: Contribution workflow
- **Issue Guidelines**: Bug reports and feature requests

**Quick Start for Contributors:**
1. Fork the repository
2. Create feature branch: `git checkout -b feature/your-feature`
3. Follow coding standards and add tests
4. Commit with conventional commits: `feat:`, `fix:`, `docs:`, etc.
5. Push and submit Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Acknowledgments

- **Ultralytics YOLOv8** for state-of-the-art object detection
- **DeepSORT** for robust multi-object tracking
- **OpenCV** for computer vision utilities
- **FastAPI** for high-performance Python web framework
- **JavaFX** for modern desktop UI
- **Supabase** for managed PostgreSQL database

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/singharyan006/ride-secure/issues)
- **Discussions**: [GitHub Discussions](https://github.com/singharyan006/ride-secure/discussions)
- **Email**: support@ridesecure.com

---

**Built with ❤️ for road safety and traffic compliance automation**
