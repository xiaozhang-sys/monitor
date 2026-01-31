@echo off
@echo off
chcp 65001 > nul

:: 设置标题和清屏
title 监控系统 - 一键启动工具
cls

:: 欢迎界面
echo ╔═══════════════════════════════════════════════╗
echo ║             监控系统 - 一键启动工具           ║
echo ║             版本: v2.0.0                      ║
echo ╚═══════════════════════════════════════════════╝
echo.
echo 🔍 正在检查系统环境...

:: 检查是否以管理员权限运行
NET SESSION >nul 2>&1
if %errorLevel% neq 0 (
echo 🔴 警告: 建议以管理员权限运行，以获得最佳体验

echo. 按任意键继续，或按Ctrl+C取消...
pause > nul
)

:: 创建日志目录
if not exist "logs" mkdir "logs"
set LOG_FILE=logs\startup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
echo. > %LOG_FILE%
echo [%date% %time%] 启动监控系统 >> %LOG_FILE%

:: 定义服务配置
set FRONTEND_PORT=5173
set BACKEND_PORT=8003
set WEBRTC_PORT=8090
set HTTP_SERVER_PORT=8081

:: 停止已运行的服务
echo.
echo 🛑 正在停止已运行的服务...

:: 停止Python服务
echo   - 停止后端服务...
taskkill /IM "python.exe" /FI "WINDOWTITLE eq Backend-Server" /F >nul 2>&1
taskkill /IM "python.exe" /FI "WINDOWTITLE eq WebRTC-Server" /F >nul 2>&1
taskkill /IM "python.exe" /FI "WINDOWTITLE eq HTTP-Server" /F >nul 2>&1

:: 停止Node.js服务
echo   - 停止前端服务...
taskkill /IM "node.exe" /F >nul 2>&1

echo   - 等待服务停止...
timeout /t 2 /nobreak > nul

:: 检查端口占用情况
echo.
echo 🔍 检查端口占用情况...
for %%p in (%FRONTEND_PORT%, %BACKEND_PORT%, %WEBRTC_PORT%, %HTTP_SERVER_PORT%) do (
    netstat -ano | findstr :%%p >nul
    if !errorLevel! equ 0 (
        for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%p') do (
            echo   - 端口 %%p 被进程 ID %%a 占用，尝试终止...
            taskkill /PID %%a /F >nul 2>&1
            if !errorLevel! equ 0 (
                echo     ✓ 成功终止进程 ID %%a
            ) else (
                echo     ✗ 无法终止进程 ID %%a，请手动检查
            )
        )
    ) else (
        echo   - 端口 %%p 可用
    )
)

echo.
echo 🚀 开始启动服务...

:: 启动后端服务
start "Backend-Server" cmd /k "cd /d %~dp0 && python backend/main.py"
echo   - 后端服务已启动 [端口: %BACKEND_PORT%]
echo [%date% %time%] 启动后端服务 >> %LOG_FILE%

:: 等待后端服务初始化
timeout /t 2 /nobreak > nul

:: 启动WebRTC服务（使用HEVC兼容版本）
start "WebRTC-Server" cmd /k "cd /d %~dp0 && python scripts/webrtc/hevc_compat_server.py --port %WEBRTC_PORT%"
echo   - WebRTC服务已启动 [端口: %WEBRTC_PORT%, HEVC兼容版本]
echo [%date% %time%] 启动WebRTC服务(HEVC兼容版本) >> %LOG_FILE%

:: 启动HTTP测试服务器
start "HTTP-Server" cmd /k "cd /d %~dp0 && python -m http.server %HTTP_SERVER_PORT%"
echo   - HTTP测试服务器已启动 [端口: %HTTP_SERVER_PORT%]
echo [%date% %time%] 启动HTTP测试服务器 >> %LOG_FILE%

:: 启动前端服务
start "Frontend-Server" cmd /k "cd /d %~dp0\frontend && npm run dev"
echo   - 前端服务已启动 [端口: %FRONTEND_PORT%]
echo [%date% %time%] 启动前端服务 >> %LOG_FILE%

:: 等待服务启动完成
echo.
echo ⏳ 等待所有服务启动完成（约10秒）...
echo   请勿关闭此窗口，正在初始化服务...
echo [%date% %time%] 等待服务启动完成 >> %LOG_FILE%

:: 倒计时显示
for /l %%i in (10,-1,1) do (
    cls
    echo ╔═══════════════════════════════════════════════╗
    echo ║             监控系统 - 一键启动工具           ║
    echo ║             版本: v2.0.0                      ║
    echo ╚═══════════════════════════════════════════════╝
    echo.
    echo 🚀 所有服务已启动，正在初始化...
    echo.
    echo ⏳ 系统初始化中，请稍候 %%i 秒...
    echo.
    echo 📝 启动日志已保存至: %LOG_FILE%
    timeout /t 1 /nobreak > nul
)

:: 显示访问信息
cls
echo ╔═══════════════════════════════════════════════╗
echo ║             监控系统 - 一键启动工具           ║
echo ║             版本: v2.0.0                      ║
echo ╚═══════════════════════════════════════════════╝
echo.
echo ✅ 所有服务已成功启动！
echo.
echo 🌐 访问地址：
echo    🖥️  前端界面: http://localhost:%FRONTEND_PORT%
echo    🔧  后端API: http://localhost:%BACKEND_PORT%
echo    📹  WebRTC服务: http://localhost:%WEBRTC_PORT%
echo    📋  HTTP测试服务器: http://localhost:%HTTP_SERVER_PORT%
echo.
echo 📝 启动日志已保存至: %LOG_FILE%
echo.
echo 💡 使用提示：
echo    1. 请不要关闭任何自动弹出的命令窗口
    2. 如需停止服务，请手动关闭所有相关窗口
    3. 如遇端口冲突，请检查 %LOG_FILE% 日志文件

echo.
echo 🎯 系统已准备就绪，按任意键打开前端界面...
echo [%date% %time%] 系统启动完成 >> %LOG_FILE%

:: 等待用户按键并打开前端界面
pause > nul
start http://localhost:%FRONTEND_PORT%

:: 保持窗口打开
echo.
echo 🔍 系统运行中... 如需退出，请关闭此窗口
pause