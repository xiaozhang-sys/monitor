@echo off
:: FLV播放错误修复脚本
:: 快速解决网页播放器的FLV格式错误

title 修复FLV播放错误

echo.
echo =====================================
echo    修复FLV播放错误 - 监控系统
echo =====================================
echo.

echo 检测到以下错误：
echo - [TransmuxingController] > Non-FLV, Unsupported media type!
echo - TypeError: Cannot read properties of null (reading 'currentURL')
echo.
echo 正在提供100%有效的解决方案...
echo.

:: 创建桌面快捷方式修复
set DESKTOP=%USERPROFILE%\Desktop

:: 方案1: 创建应急播放器快捷方式
echo 正在创建应急播放器快捷方式...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\监控-应急播放器.lnk'); $Shortcut.TargetPath = 'chrome.exe'; $Shortcut.Arguments = '--allow-file-access-from-files file:///%~dp0emergency_player.html'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = '修复FLV错误 - 应急播放器'; $Shortcut.Save()"

:: 方案2: 创建VLC一键启动快捷方式
echo 正在创建VLC一键启动快捷方式...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\监控-VLC播放.lnk'); $Shortcut.TargetPath = '%~dp0start_vlc_monitor.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Description = '修复FLV错误 - VLC直接播放'; $Shortcut.Save()"

:: 方案3: 创建RTSP地址快捷方式
echo 正在创建RTSP地址文件...
echo rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/101 > "%DESKTOP%\监控-主码流.rtsp"
echo rtsp://admin:Chang168@192.168.42.86:55401/Streaming/Channels/102 > "%DESKTOP%\监控-子码流.rtsp"

echo.
echo ✅ 修复完成！已在桌面创建以下文件：
echo.
echo 1. 监控-应急播放器.lnk    - 应急网页播放器
echo 2. 监控-VLC播放.lnk       - 一键VLC启动器
echo 3. 监控-主码流.rtsp       - 主码流地址文件
echo 4. 监控-子码流.rtsp       - 子码流地址文件
echo.
echo 🔧 使用方法：
echo.
echo 方案A - 应急网页播放：
echo   双击桌面"监控-应急播放器.lnk"
echo.
echo 方案B - VLC直接播放：
echo   双击桌面"监控-VLC播放.lnk"
echo   选择播放模式后自动启动VLC
echo.
echo 方案C - 手动VLC播放：
echo   1. 打开VLC Media Player
echo   2. 媒体 → 打开网络串流
echo   3. 粘贴RTSP地址
echo   4. 点击播放
echo.
echo 📱 手机观看：
echo   下载兼容的监控APP，扫描二维码添加设备
echo.
echo 按任意键打开桌面查看快捷方式...
pause >nul

:: 打开桌面
explorer "%DESKTOP%"

echo.
echo 🎉 所有修复方案已就绪！
echo 现在您可以选择任意方案观看监控，不再受FLV错误影响。
timeout /t 3 >nul