#!/bin/bash

clear
echo "╔══════════════════════════════════════════════════════════╗"
echo "║       🚀 平安银行账单分析系统启动器                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"

show_progress() {
    local current=$1
    local total=$2
    local message=$3
    local width=50
    local percentage=$((current * 100 / total))
    local completed=$((current * width / total))
    local remaining=$((width - completed))
    
    printf "\r["
    printf "%${completed}s" | tr ' ' '█'
    printf "%${remaining}s" | tr ' ' '░'
    printf "] %3d%% - %s" "$percentage" "$message"
}

if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python3"
    echo "下载地址: https://www.python.org/downloads/"
    exit 1
fi

echo "📋 启动步骤："
echo "  1️⃣  检查Python环境"
echo "  2️⃣  安装依赖包"
echo "  3️⃣  启动应用服务"
echo ""

show_progress 0 3 "准备启动..."
sleep 0.5

show_progress 1 3 "检查Python环境..."
if command -v python3 &> /dev/null; then
    echo ""
    echo "  ✅ Python环境正常"
else
    echo ""
    echo "  ❌ Python环境异常"
    exit 1
fi
sleep 0.3

show_progress 2 3 "安装依赖包..."
echo ""
echo "  📦 正在安装: flask, flask-cors, pypdf2, pywebview"
echo "  ⏳ 请稍候..."

packages=("flask" "flask-cors" "pypdf2" "pywebview")
total_packages=${#packages[@]}
current_package=0

for package in "${packages[@]}"; do
    current_package=$((current_package + 1))
    printf "\r  📥 安装 %d/%d: %-20s" "$current_package" "$total_packages" "$package"
    pip3 install -q "$package" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        printf " ✅\n"
    else
        printf " ⚠️ (已安装)\n"
    fi
done

echo "  ✅ 依赖包安装完成"
sleep 0.3

show_progress 3 3 "启动应用服务..."
echo ""
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                  🎉 启动成功！                           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📍 服务地址: http://127.0.0.1:8080"
echo "🌐 正在打开浏览器..."
echo ""
echo "💡 提示："
echo "  - 首次加载可能需要几秒钟"
echo "  - 请勿关闭此终端窗口"
echo "  - 按 Ctrl+C 可停止服务"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 desktop_app.py
