@echo off
chcp 65001 >nul
echo ==========================================
echo   平安银行账单分析系统 - 一键打包
echo ==========================================
echo.

cd /d "%~dp0"

echo 📦 检查并安装依赖...
pip install -q pyinstaller flask flask-cors pypdf2 pywebview

echo 🔨 开始打包应用...
echo.

pyinstaller ^
    --name="平安银行账单分析系统" ^
    --onefile ^
    --windowed ^
    --add-data="frontend;frontend" ^
    --hidden-import=flask ^
    --hidden-import=flask_cors ^
    --hidden-import=pypdf2 ^
    --hidden-import=webview ^
    --clean ^
    --noconfirm ^
    desktop_app.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ 打包成功！
    echo.
    echo 📁 可执行文件位置：dist\平安银行账单分析系统.exe
    echo.
    echo 🎉 现在您可以：
    echo    1. 双击运行 dist\平安银行账单分析系统.exe
    echo    2. 将此文件分享给其他Windows用户（无需安装Python）
    echo    3. 复制到任何Windows电脑直接运行
    echo.
    
    set /p choice="是否立即运行打包后的应用？(y/n): "
    if /i "%choice%"=="y" (
        start "" "dist\平安银行账单分析系统.exe"
    )
) else (
    echo.
    echo ❌ 打包失败，请查看上方错误信息
)

pause
