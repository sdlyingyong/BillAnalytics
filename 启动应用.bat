@echo off
chcp 65001 >nul
cls
echo ╔══════════════════════════════════════════════════════════╗
echo ║       🚀 平安银行账单分析系统启动器                      ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python3
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 📋 启动步骤：
echo   1️⃣  检查Python环境
echo   2️⃣  安装依赖包
echo   3️⃣  启动应用服务
echo.

echo [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]   0%% - 准备启动...
timeout /t 1 /nobreak >nul

echo [████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]  33%% - 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo   ❌ Python环境异常
    pause
    exit /b 1
) else (
    echo.
    echo   ✅ Python环境正常
)
timeout /t 1 /nobreak >nul

echo [████████████████████████████████░░░░░░░░░░░░░░░░░░░░]  66%% - 安装依赖包...
echo   📦 正在安装: flask, flask-cors, pypdf2, pywebview
echo   ⏳ 请稍候...
echo.

echo   📥 安装 1/4: flask
pip install -q flask 2>nul
if errorlevel 1 (echo   ⚠️ 已安装) else (echo   ✅ 安装成功)

echo   📥 安装 2/4: flask-cors
pip install -q flask-cors 2>nul
if errorlevel 1 (echo   ⚠️ 已安装) else (echo   ✅ 安装成功)

echo   📥 安装 3/4: pypdf2
pip install -q pypdf2 2>nul
if errorlevel 1 (echo   ⚠️ 已安装) else (echo   ✅ 安装成功)

echo   📥 安装 4/4: pywebview
pip install -q pywebview 2>nul
if errorlevel 1 (echo   ⚠️ 已安装) else (echo   ✅ 安装成功)

echo.
echo   ✅ 依赖包安装完成
timeout /t 1 /nobreak >nul

echo [████████████████████████████████████████████████████] 100%% - 启动应用服务...
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                  🎉 启动成功！                           ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 📍 服务地址: http://127.0.0.1:8080
echo 🌐 正在打开浏览器...
echo.
echo 💡 提示：
echo   - 首次加载可能需要几秒钟
echo   - 请勿关闭此窗口
echo   - 按 Ctrl+C 可停止服务
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

python desktop_app.py

pause
