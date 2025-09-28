@echo off
REM Cleanup script for RideSecure - Removes unnecessary files for Swing version

echo ========================================
echo RideSecure Project Cleanup
echo ========================================

echo Creating backup folder for removed files...
if not exist "backup" mkdir backup
if not exist "backup\controller" mkdir backup\controller
if not exist "backup\service" mkdir backup\service
if not exist "backup\resources" mkdir backup\resources
if not exist "backup\resources\fxml" mkdir backup\resources\fxml
if not exist "backup\resources\css" mkdir backup\resources\css

echo Moving JavaFX files to backup...

REM Move JavaFX main app
if exist "src\main\java\com\ridesecure\RideSecureApp.java" (
    move "src\main\java\com\ridesecure\RideSecureApp.java" "backup\"
    echo ✓ Moved RideSecureApp.java
)

REM Move JavaFX controller
if exist "src\main\java\com\ridesecure\controller\MainController.java" (
    move "src\main\java\com\ridesecure\controller\MainController.java" "backup\controller\"
    echo ✓ Moved MainController.java
)

REM Move service classes (currently mock)
if exist "src\main\java\com\ridesecure\service\VideoService.java" (
    move "src\main\java\com\ridesecure\service\VideoService.java" "backup\service\"
    echo ✓ Moved VideoService.java
)

if exist "src\main\java\com\ridesecure\service\DatabaseService.java" (
    move "src\main\java\com\ridesecure\service\DatabaseService.java" "backup\service\"
    echo ✓ Moved DatabaseService.java
)

REM Move DetectionResult (complex, not needed for mock)
if exist "src\main\java\com\ridesecure\model\DetectionResult.java" (
    move "src\main\java\com\ridesecure\model\DetectionResult.java" "backup\"
    echo ✓ Moved DetectionResult.java
)

REM Move JavaFX resources
if exist "src\main\resources\fxml\main-view.fxml" (
    move "src\main\resources\fxml\main-view.fxml" "backup\resources\fxml\"
    echo ✓ Moved main-view.fxml
)

if exist "src\main\resources\css\styles.css" (
    move "src\main\resources\css\styles.css" "backup\resources\css\"
    echo ✓ Moved styles.css
)

REM Remove empty directories
if exist "src\main\java\com\ridesecure\controller" rmdir "src\main\java\com\ridesecure\controller" 2>nul
if exist "src\main\java\com\ridesecure\service" rmdir "src\main\java\com\ridesecure\service" 2>nul
if exist "src\main\resources\fxml" rmdir "src\main\resources\fxml" 2>nul
if exist "src\main\resources\css" rmdir "src\main\resources\css" 2>nul

echo.
echo ✅ Cleanup completed!
echo.
echo Files moved to backup/ folder:
dir /b backup\*.java 2>nul
dir /b backup\controller\*.java 2>nul
dir /b backup\service\*.java 2>nul
dir /b backup\resources\fxml\*.fxml 2>nul
dir /b backup\resources\css\*.css 2>nul
echo.
echo Current active files:
dir /b src\main\java\com\ridesecure\*.java
dir /b src\main\java\com\ridesecure\model\*.java
echo.
echo To restore files: copy backup\[filename] back to original location
echo.

pause