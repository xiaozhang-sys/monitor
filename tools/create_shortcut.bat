@echo off
:: 创建桌面快捷方式脚本
:: 用于快速启动VLC监控播放器

title 创建监控快捷方式

echo.
echo =====================================
echo    创建监控桌面快捷方式
echo =====================================
echo.

:: 获取桌面路径
set DESKTOP=%USERPROFILE%\Desktop

:: 创建快捷方式文件
echo 正在创建快捷方式...

:: 创建主码流快捷方式
set SHORTCUT_MAIN=%DESKTOP%\监控-主码流.lnk
set SHORTCUT_SUB=%DESKTOP%\监控-子码流.lnk
set SHORTCUT_DUAL=%DESKTOP%\监控-双窗口.lnk
set SHORTCUT_WEB=%DESKTOP%\监控-网页版.lnk

:: 使用PowerShell创建快捷方式
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_MAIN%'); $Shortcut.TargetPath = '%~dp0start_vlc_monitor.bat'; $Shortcut.Arguments = ''; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = '%SystemRoot%\System32\shell32.dll,21'; $Shortcut.Description = '南京药大仓监控 - 主码流高清'; $Shortcut.Save()"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_SUB%'); $Shortcut.TargetPath = '%~dp0start_vlc_monitor.bat'; $Shortcut.Arguments = ''; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = '%SystemRoot%\System32\shell32.dll,22'; $Shortcut.Description = '南京药大仓监控 - 子码流流畅'; $Shortcut.Save()"

:: 创建网页播放器快捷方式
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_WEB%'); $Shortcut.TargetPath = 'chrome.exe'; $Shortcut.Arguments = '--allow-file-access-from-files file:///%~dp0vlc_web_player.html'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = '%SystemRoot%\System32\shell32.dll,23'; $Shortcut.Description = '南京药大仓监控 - 网页版'; $Shortcut.Save()"

echo.
echo 快捷方式创建完成!
echo.
echo 已在桌面创建以下快捷方式:
echo.
echo 1. 监控-主码流.lnk    - 高清画质
echo 2. 监控-子码流.lnk    - 流畅画质  
echo 3. 监控-网页版.lnk    - 网页播放器
echo.
echo 按任意键打开桌面...
pause >nul

:: 打开桌面
explorer "%DESKTOP%"

:: 可选：创建开始菜单快捷方式
set START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\监控系统
if not exist "%START_MENU%" mkdir "%START_MENU%"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%\监控播放器.lnk'); $Shortcut.TargetPath = '%~dp0start_vlc_monitor.bat'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.IconLocation = '%SystemRoot%\System32\shell32.dll,21'; $Shortcut.Save()"

echo.
echo 开始菜单快捷方式也已创建!
echo.
timeout /t 2 >nul