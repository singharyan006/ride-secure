@echo off
REM Build script for JavaFX RideSecure

echo Building RideSecure JavaFX Application...

REM Check if Maven is available
mvn --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Maven not found in PATH
    echo Please install Maven or add it to your PATH
    pause
    exit /b 1
)

REM Clean and compile with Maven
echo Cleaning previous build...
mvn clean

echo Compiling JavaFX application...
mvn compile

if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b 1
)

echo Build successful!
echo Run the application with: runfx.bat
pause