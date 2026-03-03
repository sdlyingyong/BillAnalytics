@echo off
chcp 65001 >nul
echo ==========================================
echo   平安银行账单分析系统 - 打包工具
echo ==========================================
echo.

cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python3
    pause
    exit /b 1
)

echo 📦 安装打包工具...
pip install -q pyinstaller

echo 🔨 开始打包...
echo.

pyinstaller --clean ^
    --name="平安银行账单分析系统" ^
    --onefile ^
    --windowed ^
    --add-data="frontend;frontend" ^
    --hidden-import=flask ^
    --hidden-import=flask_cors ^
    --hidden-import=pypdf2 ^
    --hidden-import=webview ^
    --noconsole ^
    desktop_app.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ 打包成功！
    echo.
    echo 📁 可执行文件位置：
    echo    dist\平安银行账单分析系统.exe
    echo.
    echo 💡 提示：
    echo    - 双击 dist\平安银行账单分析系统.exe 即可运行
    echo    - 可以将此文件分享给其他Windows用户
    echo.
) else (
    echo.
    echo ❌ 打包失败，请检查错误信息
)

pause
