@echo off
chcp 65001 >nul
echo 🚀 平安银行账单分析系统启动器
echo ================================

cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到 Python，请先安装 Python3
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 📦 检查依赖...
pip install -q flask flask-cors pypdf2 pywebview 2>nul

echo 🎯 启动应用...
python desktop_app.py

pause
