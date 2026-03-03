# 打包说明

本文档说明如何将平安银行账单分析系统打包成独立的可执行文件。

## 快速打包

### Mac用户
双击运行 `一键打包.command` 文件

### Windows用户
双击运行 `一键打包.bat` 文件

打包完成后，可执行文件位于 `dist/` 目录下。

## 详细说明

### 前提条件
- 已安装 Python 3.7 或更高版本
- 已安装 pip 包管理器

### Mac打包步骤

1. **安装PyInstaller**
```bash
pip3 install pyinstaller
```

2. **执行打包**
```bash
# 方式1：使用打包脚本
./一键打包.command

# 方式2：手动打包
pyinstaller --name="平安银行账单分析系统" \
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
```

3. **查找可执行文件**
打包完成后，可执行文件位于：
```
dist/平安银行账单分析系统
```

### Windows打包步骤

1. **安装PyInstaller**
```cmd
pip install pyinstaller
```

2. **执行打包**
```cmd
# 方式1：使用打包脚本
一键打包.bat

# 方式2：手动打包
pyinstaller --name="平安银行账单分析系统" ^
    --onefile ^
    --windowed ^
    --add-data="frontend;frontend" ^
    --hidden-import=flask ^
    --hidden-import=flask_cors ^
    --hidden-import=pypdf2 ^
    --hidden-import=webview ^
    --clean ^
    --noconfirm ^
    desktop_app.py
```

3. **查找可执行文件**
打包完成后，可执行文件位于：
```
dist\平安银行账单分析系统.exe
```

## 打包参数说明

| 参数 | 说明 |
|------|------|
| `--name` | 应用名称 |
| `--onefile` | 打包成单个文件 |
| `--windowed` | 不显示控制台窗口 |
| `--add-data` | 添加数据文件（格式：源路径:目标路径） |
| `--hidden-import` | 显式导入的模块 |
| `--clean` | 清理临时文件 |
| `--noconfirm` | 不询问确认 |

## 分发说明

### Mac应用
- 打包后的文件是 `dist/平安银行账单分析系统`
- 可以直接分发给其他Mac用户
- 用户无需安装Python或其他依赖
- 首次运行可能需要在"系统偏好设置 > 安全性与隐私"中允许运行

### Windows应用
- 打包后的文件是 `dist\平安银行账单分析系统.exe`
- 可以直接分发给其他Windows用户
- 用户无需安装Python或其他依赖
- 可能被杀毒软件误报，需要添加信任

## 文件大小

打包后的文件大小约为：
- Mac: 30-50 MB
- Windows: 20-40 MB

## 常见问题

### 1. 打包失败
- 确保已安装所有依赖：`pip install flask flask-cors pypdf2 pywebview`
- 检查Python版本是否兼容
- 查看错误日志，根据提示修复问题

### 2. 运行时缺少文件
- 确保 `--add-data` 参数正确
- 检查文件路径是否正确

### 3. Mac应用无法打开
- 在"系统偏好设置 > 安全性与隐私"中允许运行
- 或使用命令：`xattr -cr dist/平安银行账单分析系统`

### 4. Windows应用被杀毒软件拦截
- 将应用添加到杀毒软件的白名单
- 或暂时禁用杀毒软件

## 高级选项

### 添加应用图标

**Mac:**
```bash
pyinstaller --icon=icon.icns ...
```

**Windows:**
```cmd
pyinstaller --icon=icon.ico ...
```

### 创建安装包

**Mac:**
使用 `create-dmg` 工具创建DMG安装包：
```bash
brew install create-dmg
create-dmg dist/平安银行账单分析系统.dmg dist/平安银行账单分析系统
```

**Windows:**
使用 Inno Setup 或 NSIS 创建安装程序。

## 技术支持

如有问题，请访问项目GitHub页面：
https://github.com/sdlyingyong/BillAnalytics
