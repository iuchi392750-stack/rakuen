@echo off
setlocal enabledelayedexpansion

:: ============================================================
:: FF7風シーン Blender自動レンダリング
:: ------------------------------------------------------------
:: Blenderのパスを環境に合わせて変更してください。
:: 詳細は README.md の「Blenderパスの変更方法」を参照。
:: ============================================================

:: --- Blenderの実行ファイルパス（ここを変更） ---
set BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe

:: --- スクリプトのあるフォルダ（このbatファイルと同じ場所） ---
set SCRIPT_DIR=%~dp0

echo.
echo ============================================================
echo  FF7風スチームパンク都市シーン 自動レンダリング
echo ============================================================
echo.

:: Blenderの存在確認
if not exist "%BLENDER_EXE%" (
    echo [ERROR] Blenderが見つかりません:
    echo   %BLENDER_EXE%
    echo.
    echo BLENDER_EXEのパスを正しく設定してください。
    echo 参考: README.md の「Blenderパスの変更方法」
    pause
    exit /b 1
)

:: assetsフォルダ確認
if not exist "%SCRIPT_DIR%assets\" (
    echo [INFO] assetsフォルダが存在しないため作成します...
    mkdir "%SCRIPT_DIR%assets"
    echo.
    echo [WARN] assetsフォルダにモデルを配置してください:
    echo   %SCRIPT_DIR%assets\flower_girl_fall.fbx
    echo   %SCRIPT_DIR%assets\passerby_walk.fbx
    echo.
    echo 配置後、このbatを再実行してください。
    pause
    exit /b 1
)

:: モデルファイル確認
set MISSING=0
if not exist "%SCRIPT_DIR%assets\flower_girl_fall.fbx" (
    echo [WARN] 見つかりません: assets\flower_girl_fall.fbx
    set MISSING=1
)
if not exist "%SCRIPT_DIR%assets\passerby_walk.fbx" (
    echo [WARN] 見つかりません: assets\passerby_walk.fbx
    set MISSING=1
)

if !MISSING!==1 (
    echo.
    echo [ERROR] モデルファイルが不足しています。README.mdを参照して配置してください。
    pause
    exit /b 1
)

:: outputフォルダ作成
if not exist "%SCRIPT_DIR%output\" (
    mkdir "%SCRIPT_DIR%output"
)

echo [INFO] Blenderを起動してシーン生成・レンダリングを開始します...
echo [INFO] 完了まで数分かかります（360フレーム / 1920x1080 / 24fps）
echo.

:: Blenderをバックグラウンドで起動してレンダリング実行
"%BLENDER_EXE%" --background --python "%SCRIPT_DIR%render_viewport.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Blenderの実行中にエラーが発生しました。
    echo 上記のエラーメッセージを確認してください。
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  レンダリング完了！
echo  出力: %SCRIPT_DIR%output\flower_scene_reference.mp4
echo ============================================================
echo.

:: 出力フォルダを開く（任意）
explorer "%SCRIPT_DIR%output"

pause
