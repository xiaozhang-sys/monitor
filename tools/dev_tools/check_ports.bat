@echo off
cd /d "%~dp0"

echo === 端口状态检查 ===
echo.

setlocal enabledelayedexpansion

:: 定义端口列表
set ports=5173 8090 8001 8000

echo 检查端口占用情况...
echo.

for %%p in (%ports%) do (
    set occupied=0
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%p"') do (
        if not "%%a"=="" (
            set occupied=%%a
        )
    )
    
    if !occupied! neq 0 (
        echo 端口 %%p: ❌ 被占用 (PID: !occupied!)
        
        :: 尝试获取进程名称
        for /f "tokens=1*" %%b in ('tasklist /fi "pid eq !occupied!" ^| findstr "!occupied!"') do (
            echo         进程: %%b %%c
        )
    ) else (
        echo 端口 %%p: ✅ 可用
    )
)

echo.
echo 服务访问地址：
echo 主应用: http://localhost:5173
echo 后端API: http://localhost:8090
echo WebRTC: http://localhost:8090
echo 测试页面: http://localhost:8000/webrtc_test.html
echo.
pause