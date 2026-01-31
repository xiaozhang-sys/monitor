@echo off
echo 启动设备心跳监测服务...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: Python未安装或未添加到系统PATH
    echo 请先安装Python并确保添加到系统环境变量
    pause
    exit /b 1
)

REM 检查必要依赖
echo 检查依赖...
python -c "import aiohttp" >nul 2>&1
if errorlevel 1 (
    echo 安装依赖...
    pip install aiohttp
)

echo.
echo 请选择运行模式:
echo 1. 单次检查
echo 2. 持续运行（每10分钟检查一次）
echo 3. 调试模式（每1分钟检查一次）
echo.

set /p choice=请输入选择(1-3): 

if "%choice%"=="1" (
    echo 执行单次设备状态检查...
    python scripts\heartbeat_service.py --once
) else if "%choice%"=="2" (
    echo 启动持续心跳监测服务...
    python scripts\heartbeat_service.py
) else if "%choice%"=="3" (
    echo 启动调试模式...
    python scripts\heartbeat_service.py --debug
) else (
    echo 无效选择，执行单次检查...
    python scripts\heartbeat_service.py --once
)

echo.
echo 操作完成！
pause