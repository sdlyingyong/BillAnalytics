@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo 🚀 平安银行账单分析系统启动
echo ==========================================

REM 检查 Go 是否安装
where go >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 错误: 未检测到 Go 环境
    echo 请先安装 Go: https://golang.org/dl
    pause
    exit /b 1
)

echo 📦 安装依赖...
cd backend
call go mod tidy
call go mod download

echo.
echo ✅ 后端启动中...
start cmd /k "go run main.go"

timeout /t 2

echo.
echo ==========================================
echo ✅ 服务已启动!
echo ==========================================
echo.
echo 📍 API 服务: http://localhost:8080
echo 📊 前端页面: 在浏览器打开 frontend/index.html
echo.
pause
