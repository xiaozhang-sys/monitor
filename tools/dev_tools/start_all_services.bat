@echo off
echo 正在启动零售天眼通所有服务...
echo ================================================

:: 启动后端API服务
echo 正在启动后端API服务...
cd /d d:\code\Monitor\backend
start cmd /k "python main.py"

:: 启动前端开发服务器
echo 正在启动前端开发服务器...
cd /d d:\code\Monitor\frontend
start cmd /k "npm run dev"

:: 启动WebRTC服务器
echo 正在启动WebRTC服务器...
cd /d d:\code\Monitor\streaming\tools
start cmd /k "python webrtc_server_sdp_enhanced.py"

:: 启动心跳监控服务（可选）
echo 正在启动心跳监控服务...
cd /d d:\code\Monitor
start cmd /k "python scripts/heartbeat_monitor.py"

echo ================================================
echo 🎉 所有服务启动完成！
echo.
echo 访问地址:
echo   前端应用: http://localhost:5173
echo   WebRTC测试: http://localhost:8891/sdp_fix_test.html
echo   后端API文档: http://localhost:8090/docs
echo.
echo 按任意键关闭此窗口...
pause > nul