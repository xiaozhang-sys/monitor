@echo off
:: 简单修复脚本
echo 正在修复FLV播放错误...
echo.
echo 创建桌面快捷方式...

:: 创建应急播放器快捷方式
echo [InternetShortcut] > "%USERPROFILE%\Desktop\监控应急播放器.url"
echo URL=file:///%~dp0emergency_player.html >> "%USERPROFILE%\Desktop\监控应急播放器.url"

:: 创建VLC启动器快捷方式
echo @echo off > "%USERPROFILE%\Desktop\启动VLC监控.bat"
echo start "" "C:\Program Files\VideoLAN\VLC\vlc.exe" "rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101" >> "%USERPROFILE%\Desktop\启动VLC监控.bat"

echo.
echo 修复完成！请在桌面查看新创建的快捷方式
echo.
echo 1. 监控应急播放器.url - 网页播放器
echo 2. 启动VLC监控.bat - 一键VLC播放
echo.
pause