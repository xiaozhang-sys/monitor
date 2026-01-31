@echo off
chcp 65001 > nul

:: 停止已运行的服务
echo 正在停止所有服务...
taskkill /IM "python.exe" /F >nul 2>&1
taskkill /IM "node.exe" /F >nul 2>&1
timeout /t 2 /nobreak > nul

:: 启动后端服务
echo 启动后端服务...
start "Backend-Server" cmd /k "cd /d %~dp0 && python backend/main.py"
timeout /t 2 /nobreak > nul

:: 启动WebRTC服务（使用HEVC兼容版本）
echo 启动WebRTC服务(HEVC兼容版本)...
start "WebRTC-Server" cmd /k "cd /d %~dp0 && python scripts/webrtc/hevc_compat_server.py --port 8090"
timeout /t 2 /nobreak > nul

:: 启动HTTP测试服务器
echo 启动HTTP测试服务器...
start "HTTP-Server" cmd /k "cd /d %~dp0 && python -m http.server 8081"
timeout /t 2 /nobreak > nul

:: 启动前端服务
echo 启动前端服务...
start "Frontend-Server" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo 所有服务已开始启动，请稍候几分钟让服务完全初始化。
echo 如需查看服务状态，请查看自动弹出的命令窗口。
pause