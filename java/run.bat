@echo off
REM Quick run script for RideSecure

echo Starting RideSecure Desktop Application...

cd build
java com.ridesecure.RideSecureSwingApp

if %errorlevel% neq 0 (
    echo.
    echo Error running application. Please run build.bat first.
    pause
)

cd ..