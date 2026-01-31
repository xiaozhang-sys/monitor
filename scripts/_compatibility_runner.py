#!/usr/bin/env python3
"""
Compatibility Runner - Maintain original script usage
"""

import os
import sys
from pathlib import Path

# Script mapping table
SCRIPT_MAPPING = {
    'fix_auth_issue.py': 'auth/fix_auth_issue.py',
    'temp_public_api.py': 'auth/temp_public_api.py',
    'webrtc_server_fingerprint_fix.py': 'webrtc/webrtc_server_fingerprint_fix.py',
    'webrtc_server_enhanced.py': 'webrtc/webrtc_server_enhanced.py',
    'webrtc_server_matched.py': 'webrtc/webrtc_server_matched.py',
    'webrtc_server_sdp_final.py': 'webrtc/webrtc_server_sdp_final.py',
    'real_webrtc_server_fixed.py': 'webrtc/real_webrtc_server_fixed.py',
    'add_http_nvr.py': 'device_management/add_http_nvr.py',
    'device_status_checker.py': 'device_management/device_status_checker.py',
    'import_devices.py': 'device_management/import_devices.py',
    'query_devices.py': 'device_management/query_devices.py',
    'fix_nvr_config.py': 'device_management/fix_nvr_config.py',
    'channel_url_generator.py': 'device_management/channel_url_generator.py',
    'db_manager.py': 'database/db_manager.py',
    'check_db.py': 'database/check_db.py',
    'test_db_exceptions.py': 'database/test_db_exceptions.py',
    'fix_data_sync.py': 'database/fix_data_sync.py',
    'heartbeat_monitor.py': 'system/heartbeat_monitor.py',
    'heartbeat_service.py': 'system/heartbeat_service.py',
    'install_heartbeat_service.py': 'system/install_heartbeat_service.py',
    'monitor_dashboard.py': 'system/monitor_dashboard.py',
    'directory_guard.py': 'system/directory_guard.py',
    'exception_handler.py': 'system/exception_handler.py',
    'auto_setup.py': 'setup/auto_setup.py',
    'migrate_configs.py': 'setup/migrate_configs.py',
    'switch_environment.py': 'setup/switch_environment.py',
    'fix_port_mapping.py': 'setup/fix_port_mapping.py',
    'dev-lint.bat': 'development/dev-lint.bat',
    'dev-start.bat': 'development/dev-start.bat',
    'dev-stop.bat': 'development/dev-stop.bat',
    'dev-test.bat': 'development/dev-test.bat',
    'start_stable.bat': 'development/start_stable.bat',
    'start_stable_services.bat': 'development/start_stable_services.bat',
    'quick_check.py': 'development/quick_check.py',
    'start_vlc_monitor.bat': 'vlc/start_vlc_monitor.bat',
}

def run_original_script(script_name):
    """Run original script"""
    if script_name in SCRIPT_MAPPING:
        scripts_dir = Path(__file__).parent
        target_script = scripts_dir / SCRIPT_MAPPING[script_name]
        
        if target_script.exists():
            os.chdir(target_script.parent)
            os.system(f'python {target_script.name}')
        else:
            print(f"Error: Script not found {target_script}")
    else:
        print(f"Error: Script not mapped {script_name}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_original_script(sys.argv[1])
    else:
        print("Usage: python _compatibility_runner.py <script_name>")
