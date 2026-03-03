@echo off
chcp 65001 >nul
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo       🚀 创建Windows应用程序快捷方式
echo ╚══════════════════════════════════════════════════════════╝
echo.

set APP_NAME=平安银行账单分析
set SHORTCUT_NAME=%APP_NAME%.lnk

echo 📱 正在创建快捷方式...

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_NAME%'); $s.TargetPath = '%~dp0启动应用.bat'; $s.WorkingDirectory = '%~dp0'; $s.Description = '%APP_NAME%'; $s.IconLocation = '%~dp0icon.ico'; $s.Save()"

if exist "%SHORTCUT_NAME%" (
    echo ✅ 快捷方式创建成功: %SHORTCUT_NAME%
    echo 📱 您可以双击 %SHORTCUT_NAME% 来启动应用
) else (
    echo ❌ 快捷方式创建失败
)

echo.
pause
