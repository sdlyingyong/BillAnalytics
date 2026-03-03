#!/bin/bash

echo "=========================================="
echo "🚀 平安银行账单分析系统启动"
echo "=========================================="

# 检查 Go 是否安装
if ! command -v go &> /dev/null
then
    echo "❌ 错误: 未检测到 Go 环境"
    echo "请先安装 Go: https://golang.org/dl"
    exit 1
fi

echo "📦 安装依赖..."
cd backend
go mod tidy
go mod download

echo ""
echo "✅ 后端启动中..."
go run main.go &
BACKEND_PID=$!

sleep 2

echo ""
echo "=========================================="
echo "✅ 服务已启动!"
echo "=========================================="
echo ""
echo "📍 API 服务: http://localhost:8080"
echo "📊 前端页面: 在浏览器打开 frontend/index.html"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=========================================="

wait $BACKEND_PID
