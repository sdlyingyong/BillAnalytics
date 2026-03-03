#!/bin/bash

echo "🚀 创建跨平台应用程序..."
echo ""

echo "📱 创建Mac应用程序..."
chmod +x create_mac_app.sh
./create_mac_app.sh

echo ""
echo "🎨 创建应用图标..."
pip3 install -q Pillow 2>/dev/null
python3 create_icon.py

if [ -f "icon.icns" ]; then
    cp icon.icns "平安银行账单分析.app/Contents/Resources/AppIcon.icns"
    echo "✅ 已添加Mac应用图标"
fi

echo ""
echo "✅ 应用程序创建完成！"
echo ""
echo "📱 Mac用户："
echo "   双击 '平安银行账单分析.app' 启动应用"
echo ""
echo "📱 Windows用户："
echo "   运行 'create_windows_shortcut.bat' 创建快捷方式"
echo "   然后双击 '平安银行账单分析.lnk' 启动应用"
echo ""
