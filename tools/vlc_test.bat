@echo off
echo 🎯 WebRTC黑屏问题VLC测试工具
echo =================================

echo 正在测试录像机1...
echo RTSP地址: rtsp://admin:Chang168@192.168.42.85:55401/Streaming/Channels/101
echo.
start "" "C:\Program Files\VideoLAN\VLC\vlc.exe" "rtsp://admin:Chang168@192.168.42.85:55401/Streaming/Channels/101" --network-caching=300 --rtsp-tcp

timeout /t 3

echo 正在测试录像机2...
echo RTSP地址: rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101
echo.
start "" "C:\Program Files\VideoLAN\VLC\vlc.exe" "rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101" --network-caching=300 --rtsp-tcp

echo.
echo 📝 测试说明：
echo - 如果VLC能正常显示画面，说明RTSP流正常
echo - 如果VLC黑屏，可能是网络或摄像头问题
echo - 请等待5-10秒让VLC缓冲视频流
echo.
echo 按任意键继续...
pause > nul