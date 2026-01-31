# Scripts Directory Structure

## Directory Structure

### webrtc/ - WebRTC related
- webrtc_server_enhanced.py
- webrtc_server_matched.py
- webrtc_server_sdp_final.py
- webrtc_server_fingerprint_fix.py
- real_webrtc_server_fixed.py
- webrtc_server.log

### auth/ - Authentication related
- fix_auth_issue.py
- temp_public_api.py

### device_management/ - Device management
- add_http_nvr.py
- device_status_checker.py
- import_devices.py
- query_devices.py
- fix_nvr_config.py
- channel_url_generator.py
- devices.csv

### database/ - Database related
- db_manager.py
- check_db.py
- test_db_exceptions.py
- fix_data_sync.py

### system/ - System management
- heartbeat_monitor.py
- heartbeat_service.py
- install_heartbeat_service.py
- monitor_dashboard.py
- monitor_system.log
- directory_guard.py
- exception_handler.py

### setup/ - Setup and configuration
- auto_setup.py
- init.bat
- init.sh
- migrate_configs.py
- switch_environment.py
- fix_port_mapping.py

### development/ - Development tools
- dev-lint.bat
- dev-start.bat
- dev-stop.bat
- dev-test.bat
- start_stable.bat
- start_stable_services.bat
- quick_check.py

### vlc/ - VLC related
- start_vlc_monitor.bat

## Compatibility

All files can still be accessed through original paths:

1. Use compatibility runner:
   python scripts/_compatibility_runner.py fix_auth_issue.py

2. Direct access:
   python scripts/auth/fix_auth_issue.py

3. Batch file shortcuts (Windows)
