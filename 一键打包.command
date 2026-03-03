#!/bin/bash

echo "=========================================="
echo "  平安银行账单分析系统 - 一键打包"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

echo "📦 检查并安装依赖..."
pip3 install -q pyinstaller flask flask-cors pypdf2 pywebview

echo "🔨 开始打包应用..."
echo ""

pyinstaller \
    --name="平安银行账单分析系统" \
    --onefile \
    --windowed \
    --add-data="frontend:frontend" \
    --hidden-import=flask \
    --hidden-import=flask_cors \
    --hidden-import=pypdf2 \
    --hidden-import=webview \
    --clean \
    --noconfirm \
    desktop_app.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 打包成功！"
    echo ""
    echo "📁 可执行文件位置：dist/平安银行账单分析系统"
    echo ""
    echo "🎉 现在您可以："
    echo "   1. 双击运行 dist/平安银行账单分析系统"
    echo "   2. 将此文件分享给其他Mac用户（无需安装Python）"
    echo "   3. 复制到任何Mac电脑直接运行"
    echo ""
    
    read -p "是否立即运行打包后的应用？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "dist/平安银行账单分析系统.app"
    fi
else
    echo ""
    echo "❌ 打包失败，请查看上方错误信息"
fi
