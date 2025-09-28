@echo off
REM RideSecure Build Script - No Maven Required!
REM Compiles and runs the Swing version of RideSecure

echo ========================================
echo RideSecure - Helmet Detection System
echo ========================================

REM Check if Java is available
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Java is not installed or not in PATH
    echo Please install Java 8 or higher
    pause
    exit /b 1
)

echo Java found, starting build...

REM Create output directory
if not exist "build" mkdir build

REM Clean previous build
echo Cleaning previous build...
if exist "build\*.class" del /q "build\*.class"

REM Compile Swing application with Supabase PostgreSQL support
echo Compiling RideSecure Swing Application with Supabase Database...
cd src\main\java
javac -cp "..\..\..\lib\postgresql-42.7.1.jar" -d ..\..\..\build com\ridesecure\config\*.java com\ridesecure\model\*.java com\ridesecure\service\*.java com\ridesecure\RideSecureSwingApp.java

if %errorlevel% equ 0 (
    echo.
    echo ✅ BUILD SUCCESS!
    echo.
    echo To run the application:
    echo   cd build
    echo   java com.ridesecure.RideSecureSwingApp
    echo.
    echo Or simply run: run.bat
    echo.
) else (
    echo.
    echo ❌ BUILD FAILED!
    echo Check the error messages above
    echo.
)

cd ..\..\..
pause