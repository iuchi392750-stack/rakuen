@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

:: Blender executable path - change this to match your installation
set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 5.1\blender.exe

:: Script directory (same folder as this bat file)
set SCRIPT_DIR=%~dp0

echo.
echo ============================================================
echo  FF7 Steampunk City Scene - Auto Render
echo ============================================================
echo.

:: Check Blender exists
if not exist "%BLENDER_EXE%" (
    echo [ERROR] Blender not found:
    echo   %BLENDER_EXE%
    echo.
    echo Please set BLENDER_EXE to the correct path.
    pause
    exit /b 1
)

:: Check assets folder
if not exist "%SCRIPT_DIR%assets\" (
    echo [INFO] Creating assets folder...
    mkdir "%SCRIPT_DIR%assets"
    echo.
    echo [WARN] Please put model files in assets folder:
    echo   %SCRIPT_DIR%assets\flower_girl_fall.fbx
    echo   %SCRIPT_DIR%assets\passerby_walk.fbx
    echo.
    pause
    exit /b 1
)

:: Check model files
set MISSING=0
if not exist "%SCRIPT_DIR%assets\flower_girl_fall.fbx" (
    echo [WARN] Not found: assets\flower_girl_fall.fbx
    set MISSING=1
)
if not exist "%SCRIPT_DIR%assets\passerby_walk.fbx" (
    echo [WARN] Not found: assets\passerby_walk.fbx
    set MISSING=1
)

if !MISSING!==1 (
    echo.
    echo [ERROR] Model files missing. See README.md.
    pause
    exit /b 1
)

:: Create output folder
if not exist "%SCRIPT_DIR%output\" (
    mkdir "%SCRIPT_DIR%output"
)

echo [INFO] Starting Blender render...
echo [INFO] This will take a few minutes (360 frames / 1920x1080 / 24fps)
echo.

:: Run Blender in background
"%BLENDER_EXE%" --background --python "%SCRIPT_DIR%render_viewport.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Blender exited with an error. Check messages above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Done! Output: %SCRIPT_DIR%output\flower_scene_reference.mp4
echo ============================================================
echo.

explorer "%SCRIPT_DIR%output"

pause
