@echo off
REM JavaFX Run script for RideSecure

REM Set JAVA_HOME if not set
if not defined JAVA_HOME (
    set "JAVA_HOME=C:\Program Files\Java\jdk-17"
)
set "PATH=%JAVA_HOME%\bin;%PATH%"

echo Starting RideSecure JavaFX Application...
echo.
echo Using JAVA_HOME: %JAVA_HOME%
echo.

REM First, make sure we have all dependencies and compile
call mvn clean compile

if %errorlevel% neq 0 (
    echo Failed to compile!
    pause
    exit /b 1
)

REM Get JavaFX path
set JAVAFX_PATH=lib\javafx-sdk-17.0.2\lib

echo Using JavaFX SDK from: %JAVAFX_PATH%

if not exist "%JAVAFX_PATH%\javafx.controls.jar" (
    echo ERROR: JavaFX SDK not found in %JAVAFX_PATH%!
    echo Please copy the JavaFX SDK files to this location.
    echo Download from: https://download2.gluonhq.com/openjfx/17.0.2/openjfx-17.0.2_windows-x64_bin-sdk.zip
    pause
    exit /b 1
)

REM Run the application with proper module path and class path
"%JAVA_HOME%\bin\java" --module-path "%CD%\%JAVAFX_PATH%" ^
     --add-modules javafx.controls,javafx.fxml ^
     --add-opens javafx.controls/com.sun.javafx.scene.control.behavior=ALL-UNNAMED ^
     --add-opens javafx.controls/com.sun.javafx.scene.control=ALL-UNNAMED ^
     --add-opens javafx.base/com.sun.javafx.binding=ALL-UNNAMED ^
     --add-opens javafx.graphics/com.sun.javafx.stage=ALL-UNNAMED ^
     -cp "target\classes;lib\*" ^
     com.ridesecure.RideSecureFXApp

if %errorlevel% neq 0 (
    echo.
    echo Error running JavaFX application
    echo Make sure you have:
    echo 1. Compiled the project: mvn compile
    echo 2. Installed JavaFX SDK
    echo 3. Set JAVA_HOME correctly
    pause
)