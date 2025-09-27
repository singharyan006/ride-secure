# Contributing to RideSecure

Thank you for your interest in contributing to RideSecure! This document provides guidelines and information for contributors working on this hybrid Java + Python helmet detection system.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Release Process](#release-process)

## 🤝 Code of Conduct

We are committed to fostering a welcoming and inclusive community. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

### Expected Behavior

- **Be respectful** and inclusive in all interactions
- **Be collaborative** and constructive in discussions
- **Be patient** when reviewing code and providing feedback
- **Focus on the issue** rather than personal attacks
- **Help newcomers** understand the project and codebase

### Unacceptable Behavior

- Harassment, discrimination, or offensive language
- Trolling, insulting comments, or personal attacks
- Publishing private information without permission
- Any conduct that could reasonably be considered inappropriate

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have the following installed:

- **Java 11+** (OpenJDK 11 or 17 recommended)
- **Python 3.8+** with pip and virtualenv
- **Maven 3.6+** for Java build management
- **Git** for version control
- **Docker** (optional, for containerized development)
- **CUDA Toolkit** (optional, for GPU acceleration)

### Fork and Clone

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ride-secure.git
   cd ride-secure
   ```
3. **Add upstream** remote:
   ```bash
   git remote add upstream https://github.com/singharyan006/ride-secure.git
   ```

## 🛠️ Development Environment Setup

### Quick Setup Script

Create a setup script to automate environment configuration:

```bash
#!/bin/bash
# setup.sh - Development environment setup

echo "Setting up RideSecure development environment..."

# Python Environment
echo "Creating Python virtual environment..."
cd python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .[dev]
cd ..

# Java Dependencies
echo "Installing Java dependencies..."
cd java
mvn clean compile
cd ..

# Database Setup
echo "Initializing database..."
cd database
sqlite3 ridesecure.db < schema/init.sql
cd ..

# Pre-commit Hooks
echo "Setting up pre-commit hooks..."
cd python
pre-commit install
cd ..

echo "Setup complete! Ready for development."
```

### Java Development Setup

1. **Import Project** into your IDE (IntelliJ IDEA, Eclipse, VS Code)
2. **Configure Maven** settings:
   ```bash
   cd java
   mvn clean compile
   mvn dependency:resolve
   ```
3. **Configure JavaFX** module path in your IDE
4. **Run Tests**:
   ```bash
   mvn test
   ```

### Python Development Setup

1. **Create Virtual Environment**:
   ```bash
   cd python
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install -e .[dev]  # Installs package in editable mode with dev dependencies
   ```
3. **Setup Pre-commit Hooks**:
   ```bash
   pre-commit install
   ```
4. **Run Tests**:
   ```bash
   pytest tests/ -v
   ```

### Docker Development Setup

```bash
# Build development containers
docker-compose -f docker-compose.dev.yml build

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Access containers
docker-compose exec java-app bash
docker-compose exec python-ml bash
```

## 🏗️ Project Structure

Understanding the codebase architecture is crucial for effective contributions:

### Java Application (`java/`)

```
java/
├── src/main/java/com/ridesecure/
│   ├── RideSecureApp.java          # JavaFX Application entry
│   ├── controller/                 # UI Controllers (MVC pattern)
│   ├── model/                      # Data models and entities
│   ├── service/                    # Business logic layer
│   ├── detection/                  # ML inference wrappers
│   ├── database/                   # Database access layer
│   └── utils/                      # Utility classes
├── src/main/resources/
│   ├── fxml/                       # JavaFX UI definitions
│   ├── css/                        # Stylesheets
│   └── config/                     # Configuration files
└── src/test/java/                  # Java unit tests
```

### Python ML Components (`python/`)

```
python/
├── src/ridesecure/
│   ├── training/                   # Model training scripts
│   ├── inference/                  # ONNX export and API service
│   ├── data/                       # Data processing utilities
│   ├── models/                     # Model architectures
│   └── utils/                      # Python utilities
├── notebooks/                      # Jupyter notebooks for experimentation
└── tests/                          # Python unit tests
```

## 📝 Coding Standards

### Java Coding Standards

We follow **Google Java Style Guide** with these modifications:

#### Code Formatting
- **Indentation**: 4 spaces (not tabs)
- **Line Length**: 120 characters maximum
- **Braces**: Always use braces, even for single statements
- **Imports**: Organize imports alphabetically, separate groups

#### Naming Conventions
```java
// Classes: PascalCase
public class HelmetDetector { }

// Methods and variables: camelCase
public void detectHelmet() { }
private int frameCount;

// Constants: UPPER_SNAKE_CASE
public static final String MODEL_PATH = "models/helmet.onnx";

// Packages: lowercase with dots
package com.ridesecure.detection;
```

#### Documentation
```java
/**
 * Detects helmet status from video frames using YOLO model.
 * 
 * @param frame Input video frame as BufferedImage
 * @param confidence Minimum confidence threshold (0.0-1.0)
 * @return Detection result with bounding boxes and confidence scores
 * @throws ModelException if model inference fails
 */
public DetectionResult detectHelmet(BufferedImage frame, double confidence) {
    // Implementation
}
```

#### Error Handling
```java
// Use specific exceptions
throw new ModelException("Failed to load ONNX model: " + modelPath);

// Log errors appropriately
logger.error("Detection failed for frame {}", frameNumber, exception);

// Use try-with-resources for resource management
try (OnnxTensor tensor = createInputTensor(frame)) {
    return runInference(tensor);
}
```

### Python Coding Standards

We follow **PEP 8** with these tools and configurations:

#### Code Formatting (Black)
```python
# .python/pyproject.toml
[tool.black]
line-length = 88
target-version = ["py38", "py39", "py310"]
include = '\.pyi?$'
```

#### Import Organization (isort)
```python
# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
import numpy as np
import torch
from ultralytics import YOLO

# Local application imports
from ridesecure.models.yolo_helmet import HelmetYOLO
from ridesecure.utils.config import load_config
```

#### Type Hints
```python
from typing import List, Optional, Tuple, Union
import numpy as np

def detect_helmet(
    frame: np.ndarray,
    model: YOLO,
    confidence: float = 0.7
) -> Tuple[List[dict], float]:
    """Detect helmet status in video frame.
    
    Args:
        frame: Input video frame as numpy array (H, W, C)
        model: Loaded YOLO model instance
        confidence: Minimum confidence threshold
        
    Returns:
        Tuple of (detection_results, inference_time)
        
    Raises:
        ModelError: If inference fails
    """
    # Implementation
    pass
```

#### Error Handling
```python
import logging
from ridesecure.exceptions import ModelError, DataError

logger = logging.getLogger(__name__)

def load_model(model_path: str) -> YOLO:
    """Load YOLO model with proper error handling."""
    try:
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        model = YOLO(model_path)
        logger.info(f"Successfully loaded model: {model_path}")
        return model
        
    except Exception as e:
        logger.error(f"Failed to load model {model_path}: {e}")
        raise ModelError(f"Model loading failed: {e}") from e
```

## 🧪 Testing Guidelines

### Java Testing (JUnit 5)

#### Test Structure
```java
@DisplayName("Helmet Detection Tests")
class HelmetDetectorTest {
    
    private HelmetDetector detector;
    private BufferedImage testFrame;
    
    @BeforeEach
    void setUp() {
        detector = new HelmetDetector("test-model.onnx");
        testFrame = loadTestImage("test-frame.jpg");
    }
    
    @Test
    @DisplayName("Should detect helmet with high confidence")
    void shouldDetectHelmetWithHighConfidence() {
        // Given
        double confidenceThreshold = 0.8;
        
        // When
        DetectionResult result = detector.detectHelmet(testFrame, confidenceThreshold);
        
        // Then
        assertThat(result.getDetections()).isNotEmpty();
        assertThat(result.getMaxConfidence()).isGreaterThan(confidenceThreshold);
    }
    
    @Test
    @DisplayName("Should handle empty frame gracefully")
    void shouldHandleEmptyFrameGracefully() {
        // Given
        BufferedImage emptyFrame = new BufferedImage(640, 480, BufferedImage.TYPE_3BYTE_BGR);
        
        // When & Then
        assertDoesNotThrow(() -> detector.detectHelmet(emptyFrame, 0.5));
    }
}
```

#### Test Coverage
```bash
# Run tests with coverage
mvn test jacoco:report

# View coverage report
open target/site/jacoco/index.html
```

### Python Testing (pytest)

#### Test Structure
```python
import pytest
import numpy as np
from unittest.mock import Mock, patch

from ridesecure.detection.helmet_detector import HelmetDetector
from ridesecure.exceptions import ModelError


class TestHelmetDetector:
    """Test suite for HelmetDetector class."""
    
    @pytest.fixture
    def detector(self):
        """Create detector instance for testing."""
        return HelmetDetector(model_path="test_model.pt")
    
    @pytest.fixture
    def sample_frame(self):
        """Create sample video frame for testing."""
        return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    def test_detect_helmet_success(self, detector, sample_frame):
        """Test successful helmet detection."""
        # Given
        confidence_threshold = 0.7
        
        # When
        results = detector.detect(sample_frame, confidence_threshold)
        
        # Then
        assert isinstance(results, list)
        assert all(result['confidence'] >= confidence_threshold for result in results)
    
    def test_detect_helmet_invalid_input(self, detector):
        """Test detection with invalid input."""
        with pytest.raises(ValueError, match="Invalid frame shape"):
            detector.detect(np.array([1, 2, 3]))  # Invalid shape
    
    @patch('ridesecure.detection.helmet_detector.YOLO')
    def test_model_loading_failure(self, mock_yolo):
        """Test model loading failure handling."""
        mock_yolo.side_effect = Exception("Model load failed")
        
        with pytest.raises(ModelError, match="Failed to load model"):
            HelmetDetector("invalid_model.pt")
```

#### Test Coverage
```bash
# Run tests with coverage
pytest tests/ --cov=ridesecure --cov-report=html --cov-report=term-missing

# View coverage report
open htmlcov/index.html
```

#### Integration Tests
```python
@pytest.mark.integration
def test_end_to_end_detection_pipeline():
    """Test complete detection pipeline integration."""
    # This test requires actual model files and sample videos
    video_path = "data/videos/sample/test_video.mp4"
    config_path = "config/application.yml"
    
    # Load configuration and models
    config = load_config(config_path)
    detector = create_detector_from_config(config)
    
    # Process video
    results = process_video(video_path, detector)
    
    # Verify results
    assert len(results) > 0
    assert all('helmet_status' in result for result in results)
```

## 📝 Commit Message Guidelines

We use **Conventional Commits** specification for consistent commit messages:

### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or modifying tests
- **chore**: Maintenance tasks
- **perf**: Performance improvements
- **ci**: CI/CD changes

### Examples
```bash
# Feature addition
feat(detection): add license plate OCR with Tesseract integration

# Bug fix
fix(database): resolve SQLite connection pool exhaustion

# Documentation
docs(api): update Python inference service documentation

# Breaking change
feat(detection)!: change helmet detection API to support batch processing

BREAKING CHANGE: detectHelmet() now accepts List<BufferedImage> instead of single image
```

### Scope Guidelines
- **java**: Java application changes
- **python**: Python ML components
- **detection**: Detection algorithms
- **database**: Database operations
- **ui**: User interface changes
- **config**: Configuration changes
- **docs**: Documentation updates

## 🔄 Pull Request Process

### Before Creating a Pull Request

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** following coding standards

4. **Add tests** for new functionality

5. **Run quality checks**:
   ```bash
   # Java
   cd java
   mvn clean test checkstyle:check spotbugs:check
   
   # Python
   cd python
   black src/ tests/
   flake8 src/ tests/
   mypy src/
   pytest tests/ --cov=ridesecure
   ```

6. **Update documentation** if needed

### Pull Request Template

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added and passing
- [ ] No new warnings introduced

## Screenshots (if applicable)
Add screenshots for UI changes.

## Related Issues
Fixes #123
Related to #456
```

### Review Process

1. **Automated Checks**: All CI/CD checks must pass
2. **Code Review**: At least one maintainer approval required
3. **Testing**: Reviewer should test functionality locally
4. **Documentation**: Verify documentation is updated
5. **Merge**: Maintainer merges using "Squash and merge"

## 🐛 Issue Guidelines

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Windows 10, Ubuntu 20.04]
 - Java Version: [e.g. OpenJDK 11]
 - Python Version: [e.g. 3.9.7]
 - Model Version: [e.g. helmet_yolo_v8_1.0.0]

**Additional context**
Add any other context about the problem here.
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions.

**Additional context**
Add any other context or screenshots about the feature request here.
```

### Issue Labels

- **bug**: Something isn't working
- **enhancement**: New feature or request
- **documentation**: Improvements or additions to documentation
- **good first issue**: Good for newcomers
- **help wanted**: Extra attention is needed
- **priority/high**: High priority issue
- **component/java**: Java application related
- **component/python**: Python ML related
- **component/models**: ML models related

## 📚 Documentation Guidelines

### Code Documentation

#### Java Documentation (Javadoc)
```java
/**
 * Processes video frames for helmet detection violations.
 * 
 * <p>This class coordinates between video loading, ML inference,
 * and database logging to create a complete violation detection pipeline.
 * 
 * @author RideSecure Team
 * @version 1.0.0
 * @since 1.0.0
 */
public class VideoProcessor {
    
    /**
     * Processes a single video file for helmet violations.
     * 
     * @param videoPath Path to the input video file
     * @param config Processing configuration parameters
     * @return List of detected violations with metadata
     * @throws ProcessingException if video processing fails
     * @throws ModelException if ML inference fails
     */
    public List<Violation> processVideo(String videoPath, ProcessingConfig config) {
        // Implementation
    }
}
```

#### Python Documentation (Google Style)
```python
def train_helmet_model(
    dataset_path: str,
    epochs: int = 100,
    batch_size: int = 16,
    learning_rate: float = 0.001
) -> TrainingResult:
    """Train YOLO model for helmet detection.
    
    Args:
        dataset_path: Path to training dataset directory
        epochs: Number of training epochs
        batch_size: Training batch size
        learning_rate: Initial learning rate
        
    Returns:
        TrainingResult object containing metrics and model path
        
    Raises:
        DataError: If dataset is invalid or corrupted
        ModelError: If training fails
        
    Example:
        >>> result = train_helmet_model(
        ...     dataset_path="data/helmet_dataset",
        ...     epochs=50,
        ...     batch_size=8
        ... )
        >>> print(f"Final mAP: {result.final_map}")
    """
    # Implementation
```

### README Updates

When adding new features:
1. Update the feature list in main README
2. Add setup instructions if needed
3. Update architecture diagrams if structure changes
4. Add to roadmap if it's a significant milestone

## 🚀 Release Process

### Version Numbers

We use **Semantic Versioning** (SemVer):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality in backwards-compatible manner
- **PATCH**: Backwards-compatible bug fixes

### Release Checklist

1. **Update Version Numbers**:
   - `java/pom.xml` - Maven version
   - `python/pyproject.toml` - Python package version
   - `config/application.yml` - Application version

2. **Update CHANGELOG.md**:
   ```markdown
   ## [1.1.0] - 2025-09-27
   ### Added
   - New license plate detection model
   - Real-time camera support
   
   ### Fixed
   - SQLite connection pool issues
   - JavaFX memory leaks
   
   ### Changed
   - Improved detection accuracy by 15%
   ```

3. **Run Full Test Suite**:
   ```bash
   # Java tests
   cd java && mvn clean test
   
   # Python tests
   cd python && pytest tests/ --cov=ridesecure
   
   # Integration tests
   python integration_tests.py
   ```

4. **Build Release Artifacts**:
   ```bash
   # Java JAR
   cd java && mvn clean package
   
   # Python wheel
   cd python && python -m build
   
   # Docker images
   docker build -t ridesecure:latest .
   ```

5. **Create Release**:
   - Create GitHub release with changelog
   - Upload JAR and wheel files
   - Tag with version number
   - Deploy Docker images

### Hotfix Process

For critical bugs in production:

1. Create hotfix branch from main: `git checkout -b hotfix/critical-fix`
2. Make minimal fix with tests
3. Fast-track review process
4. Merge to main and release immediately
5. Increment patch version

## 🤝 Community

### Communication Channels

- **GitHub Discussions**: General questions and ideas
- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Code contributions and reviews
- **Email**: ridesecure.support@example.com for private matters

### Maintainers

Current project maintainers:
- **@singharyan006** - Project Lead & Java Development
- **@contributor1** - Python ML Development
- **@contributor2** - DevOps & Infrastructure

### Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Annual contributor appreciation posts

## 📄 License

By contributing to RideSecure, you agree that your contributions will be licensed under the same [MIT License](LICENSE) that covers the project.

---

**Thank you for contributing to RideSecure! Together, we're building technology that makes roads safer for everyone.** 🛡️🏍️