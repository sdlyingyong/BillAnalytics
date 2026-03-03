#!/bin/bash

echo "=========================================="
echo "  平安银行账单分析系统 - 打包工具"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python3"
    exit 1
fi

echo "📦 安装打包工具..."
pip3 install -q pyinstaller

echo "🔨 开始打包..."
echo ""

pyinstaller --clean \
    --name="平安银行账单分析系统" \
    --onefile \
    --windowed \
    --add-data="frontend:frontend" \
    --hidden-import=flask \
    --hidden-import=flask_cors \
    --hidden-import=pypdf2 \
    --hidden-import=webview \
    --noconsole \
    desktop_app.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 打包成功！"
    echo ""
    echo "📁 可执行文件位置："
    echo "   dist/平安银行账单分析系统"
    echo ""
    echo "💡 提示："
    echo "   - Mac: 双击 dist/平安银行账单分析系统 即可运行"
    echo "   - 可以将此文件分享给其他Mac用户"
    echo ""
else
    echo ""
    echo "❌ 打包失败，请检查错误信息"
fi
