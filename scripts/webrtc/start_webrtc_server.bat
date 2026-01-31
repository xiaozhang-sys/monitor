@echo off
echo === 启动WebRTC RTSP服务器 ===
setlocal enabledelayedexpansion

REM 设置工作目录
cd /d "%~dp0..\.."

REM 检查Python环境
echo 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Python未安装或未添加到PATH
    pause
    exit /b 1
)

REM 检查依赖
echo 检查依赖...
python -c "import aiortc" >nul 2>&1
if %errorlevel% neq 0 (
    echo 安装WebRTC依赖...
    pip install aiortc aiohttp aiohttp-cors av opencv-python
)

REM 启动WebRTC服务器（HEVC兼容版本）
echo 启动WebRTC服务器（HEVC兼容版本）...
python scripts\webrtc\hevc_compat_server.py --host 0.0.0.0 --port 8090

echo WebRTC服务器启动完成
pause