# RideSecure JavaFX Application

## Migration from Swing to JavaFX

This directory contains the new JavaFX version of the RideSecure desktop application with CSS styling support.

### Files Added/Modified:

#### New JavaFX Files:
- `RideSecureFXApp.java` - Main JavaFX application class
- `RideSecureFXController.java` - FXML controller with all UI logic
- `src/main/resources/fxml/RideSecureMain.fxml` - FXML layout definition
- `src/main/resources/css/styles.css` - Modern CSS stylesheet
- `buildfx.bat` - Maven build script for JavaFX
- `runfx.bat` - Run script for JavaFX application

#### Updated Files:
- `pom.xml` - Added JavaFX dependencies and plugin

### Requirements:

1. **Java 11 or higher** with JavaFX support
2. **Maven** for dependency management
3. **JavaFX SDK** (if not bundled with your JDK)

### Setup Instructions:

#### Option 1: Using Maven (Recommended)
```powershell
# Build the application
.\buildfx.bat

# Run the application
mvn javafx:run
```

#### Option 2: Using JavaFX SDK
1. Download JavaFX SDK from https://openjfx.io/
2. Extract to `C:\Program Files\Java\javafx-sdk-17\` (or similar)
3. Build and run:
```powershell
.\buildfx.bat
.\runfx.bat
```

### Key Improvements:

#### CSS Styling:
- Modern, responsive design with CSS
- Custom button styles with hover effects
- Professional color scheme
- Consistent spacing and typography

#### JavaFX Features:
- Better video display with ImageView
- Smooth animations with Timeline
- Native file dialogs
- Better table rendering
- Improved threading with Task/Platform.runLater

#### Architecture:
- Clean separation with FXML
- Controller-based event handling
- Better resource management
- Improved error handling with alerts

### Development Commands:

```powershell
# Build only
mvn compile

# Run with Maven
mvn javafx:run

# Package (future)
mvn package

# Run tests
mvn test
```

### CSS Customization:

The `styles.css` file contains all styling. Key classes:
- `.control-button` - Video control buttons
- `.start-button` - Detection start button
- `.stop-button` - Detection stop button
- `.video-display` - Video area styling
- `.section-title` - Section headers
- `.table-view` - Table styling

### Troubleshooting:

#### JavaFX Module Issues:
If you get module-related errors, ensure JavaFX is properly installed:
```powershell
java --list-modules | findstr javafx
```

#### CSS Not Loading:
Check that the CSS file path in `RideSecureFXApp.java` matches the actual file location.

#### Video Playback Issues:
The video functionality remains the same as the Swing version, requiring FFmpeg for frame extraction.

### Migration Notes:

- All original functionality preserved
- Database integration unchanged
- Video processing logic identical
- Added CSS styling capabilities
- Improved UI responsiveness
- Better cross-platform compatibility

The original Swing version (`RideSecureSwingApp.java`) remains available for comparison or fallback.