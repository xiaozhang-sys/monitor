@echo off
echo 正在测试RTSP视频源...
echo RTSP地址: %1
echo.

if "%1"=="" (
    echo 使用方法: %0 [RTSP地址]
    echo 示例: %0 rtsp://admin:Chang168@192.168.42.85:55401/Streaming/Channels/101
    pause
    exit /b 1
)

echo 正在启动VLC播放器...
"C:\Program Files\VideoLAN\VLC\vlc.exe" "%1" --network-caching=300 --rtsp-tcp

echo VLC已启动！
pause