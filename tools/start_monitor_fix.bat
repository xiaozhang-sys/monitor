@echo off
echo 🚀 启动零售天眼通黑屏修复方案
echo =================================

REM 启动后端公共API (绕过认证)
echo 正在启动后端公共API...
start "Backend Public API" cmd /k "python temp_public_api.py"
timeout /t 2

REM 启动WebRTC服务
echo 正在启动WebRTC服务...
start "WebRTC Service" cmd /k "python webrtc_server_fingerprint_fix.py --host 0.0.0.0 --port 8080"
timeout /t 2

REM 启动前端服务
echo 正在启动前端服务...
start "Frontend" cmd /k "cd frontend && npm run dev"
timeout /t 2

echo.
echo ✅ 所有服务已启动！
echo.
echo 🌐 访问地址：
echo    调试页面: http://127.0.0.1:5173/debug_video.html
echo    主页面: http://127.0.0.1:5173
echo    设备API: http://localhost:8004/devices
echo    WebRTC: http://localhost:8090/health
echo.
echo 🎯 使用步骤：
echo    1. 打开浏览器访问调试页面
echo    2. 点击"加载设备"
echo    3. 点击"启动WebRTC"测试视频
echo.
echo 📞 如仍黑屏，请查看 BLACK_SCREEN_SOLUTION.md
pause