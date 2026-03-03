#!/bin/bash

echo "🚀 平安银行账单分析系统启动器"
echo "================================"

cd "$(dirname "$0")"

if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python3"
    echo "下载地址: https://www.python.org/downloads/"
    exit 1
fi

echo "📦 检查依赖..."
pip3 install -q flask flask-cors pypdf2 pywebview 2>/dev/null

echo "🎯 启动应用..."
python3 desktop_app.py
