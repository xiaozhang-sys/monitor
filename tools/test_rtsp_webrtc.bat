@echo off
echo.
echo ========================================
echo 🎯 RTSP WebRTC测试工具
echo ========================================
echo.

:: 设置变量
set RTSP_URL=rtsp://admin:Chang168@192.168.42.85:55401/Streaming/Channels/101
set WEBRTC_PORT=8091
set WEBRTC_URL=http://localhost:%WEBRTC_PORT%

:: 检查WebRTC服务
:check_service
echo 🔍 检查WebRTC服务状态...
curl -s %WEBRTC_URL%/api/health > nul
if %errorlevel% neq 0 (
    echo ❌ WebRTC服务未启动
    goto start_service
) else (
    echo ✅ WebRTC服务已运行
    goto test_vlc
)

:: 启动WebRTC服务
:start_service
echo.
echo 🚀 启动WebRTC快速修复服务...
start /min cmd /c "cd /d %~dp0.. && python streaming\tools\webrtc_quick_fix.py --port %WEBRTC_PORT% --rtsp %RTSP_URL%"
timeout /t 3 /nobreak > nul
echo ✅ WebRTC服务已启动

:: 测试VLC
test_vlc
echo.
echo 📺 测试VLC播放RTSP流...
echo RTSP地址: %RTSP_URL%
echo.
echo 命令: "C:\Program Files\VideoLAN\VLC\vlc.exe" "%RTSP_URL%" --network-caching=300 --rtsp-tcp
echo.
echo 按任意键启动VLC测试...
pause > nul
start "" "C:\Program Files\VideoLAN\VLC\vlc.exe" "%RTSP_URL%" --network-caching=300 --rtsp-tcp

:: 打开WebRTC测试页面
:test_webrtc
echo.
echo 🌐 打开WebRTC测试页面...
echo 测试页面: file:///%~dp0..\tests\webrtc_rtsp_test.html
echo.
echo 按任意键打开浏览器测试页面...
pause > nul
start "" "file:///%~dp0..\tests\webrtc_rtsp_test.html"

:: 显示状态信息
:status
echo.
echo ========================================
echo 📊 当前状态
echo ========================================
echo RTSP地址: %RTSP_URL%
echo WebRTC服务: %WEBRTC_URL%
echo VLC测试: 已启动
echo WebRTC测试: 已打开

:: 提供快速测试命令
echo.
echo 🔧 快速测试命令:
echo 1. VLC播放: "C:\Program Files\VideoLAN\VLC\vlc.exe" "%RTSP_URL%" --network-caching=300 --rtsp-tcp
echo 2. 服务状态: curl %WEBRTC_URL%/api/health
echo 3. 测试页面: file:///%~dp0..\tests\webrtc_rtsp_test.html
echo.
echo 按任意键退出...
pause > nul