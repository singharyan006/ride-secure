@echo off
REM JavaFX Run script for RideSecure

echo Starting RideSecure JavaFX Application...

REM Check if JavaFX runtime is available
java --list-modules | findstr javafx.controls >nul
if %errorlevel% equ 0 (
    echo JavaFX runtime detected
    java -cp "target\classes;lib\*" com.ridesecure.RideSecureFXApp
) else (
    echo JavaFX runtime not found, using module path approach...
    
    REM Try with common JavaFX SDK locations
    set JAVAFX_PATH=""
    
    if exist "C:\Program Files\Java\javafx-sdk-17\lib" (
        set JAVAFX_PATH="C:\Program Files\Java\javafx-sdk-17\lib"
    ) else if exist "C:\Program Files\Java\javafx-sdk-11\lib" (
        set JAVAFX_PATH="C:\Program Files\Java\javafx-sdk-11\lib"
    ) else if exist "%JAVA_HOME%\javafx\lib" (
        set JAVAFX_PATH="%JAVA_HOME%\javafx\lib"
    )
    
    if %JAVAFX_PATH%=="" (
        echo ERROR: JavaFX SDK not found!
        echo Please install JavaFX SDK or add JavaFX to your JDK
        echo Download from: https://openjfx.io/
        pause
        exit /b 1
    )
    
    java --module-path %JAVAFX_PATH% --add-modules javafx.controls,javafx.fxml -cp "target\classes;lib\*" com.ridesecure.RideSecureFXApp
)

if %errorlevel% neq 0 (
    echo.
    echo Error running JavaFX application
    echo Make sure you have compiled the project first with: mvn compile
    pause
)