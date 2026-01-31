@echo off
echo 正在测试当前配置的录像机视频源...
echo.

set RTSP_URL=rtsp://admin:Chang168@192.168.42.85:55401/Streaming/Channels/101
echo RTSP地址: %RTSP_URL%
echo.

echo 正在启动VLC播放器进行测试...
"C:\Program Files\VideoLAN\VLC\vlc.exe" "%RTSP_URL%" --network-caching=300 --rtsp-tcp --video-on-top

echo VLC已启动！如果视频正常播放，说明RTSP源工作正常。
echo.
pause