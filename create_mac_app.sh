#!/bin/bash

APP_NAME="平安银行账单分析"
APP_DIR="${APP_NAME}.app"
CONTENTS_DIR="${APP_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

echo "🚀 创建Mac应用程序包..."

rm -rf "${APP_DIR}"

mkdir -p "${MACOS_DIR}"
mkdir -p "${RESOURCES_DIR}"

SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/启动应用.command"

cat > "${MACOS_DIR}/${APP_NAME}" << EOF
#!/bin/bash
cd "$(dirname "$0")/../../.."
osascript -e 'tell application "Terminal" to do script "cd \"'$(pwd)'\" && ./启动应用.command"'
EOF

chmod +x "${MACOS_DIR}/${APP_NAME}"

cat > "${CONTENTS_DIR}/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.pingan.billanalyzer</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
</dict>
</plist>
EOF

if [ -f "icon.png" ]; then
    echo "🎨 正在创建应用图标..."
    mkdir -p icon.iconset
    
    sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
    sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
    sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
    sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
    sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
    sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
    sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
    sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
    sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
    sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
    
    iconutil -c icns icon.iconset -o "${RESOURCES_DIR}/AppIcon.icns"
    rm -rf icon.iconset
    
    echo "✅ 应用图标创建成功"
fi

echo "✅ Mac应用程序包创建完成: ${APP_DIR}"
echo "📱 您可以双击 ${APP_DIR} 来启动应用"
echo ""
echo "💡 提示："
echo "   - 双击应用会在终端中启动"
echo "   - 请保持终端窗口打开"
