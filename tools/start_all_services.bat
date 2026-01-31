@echo off
echo === 启动监控系统服务 ===

REM 启动后端API服务
echo 正在启动后端API服务...
cd /d d:\code\Monitor
start cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload"

REM 启动前端开发服务器
echo 正在启动前端开发服务器...
cd /d d:\code\Monitor\frontend
start cmd /k "npm run dev"

REM 启动HEVC兼容WebRTC服务器
echo 正在启动HEVC兼容WebRTC服务器...
cd /d d:\code\Monitor
start cmd /k "python scripts/webrtc/hevc_compat_server.py --port 8090"

echo.
echo === 服务启动完成 ===
echo 后端API: http://localhost:8001
echo 前端界面: http://localhost:5173
echo 文档: http://localhost:8001/docs
echo.
echo 按任意键继续...
pause