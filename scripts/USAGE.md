# Scripts Directory Usage Guide

## Quick Start

### Original Usage (unchanged)
All existing scripts work exactly as before:

```bash
# Example: Run authentication fix
python scripts/fix_auth_issue.py

# Example: Start WebRTC server
python scripts/webrtc_server_fingerprint_fix.py --host 127.0.0.1 --port 8080
```

### New Organized Usage
Files are now organized by function:

```bash
# Direct access to categorized scripts
python scripts/auth/fix_auth_issue.py
python scripts/webrtc/webrtc_server_fingerprint_fix.py --host 127.0.0.1 --port 8080
python scripts/device_management/add_http_nvr.py
```

### Compatibility Runner
Use the compatibility runner for any script:

```bash
python scripts/_compatibility_runner.py <script_name>
```

## Directory Structure

### /auth
Authentication and authorization scripts
- `fix_auth_issue.py` - Fix authentication problems
- `temp_public_api.py` - Temporary public API endpoint

### /webrtc
WebRTC server and streaming scripts
- `webrtc_server_fingerprint_fix.py` - WebRTC server with fingerprint fix
- `webrtc_server_enhanced.py` - Enhanced WebRTC server
- `webrtc_server_matched.py` - Matched WebRTC server
- `webrtc_server_sdp_final.py` - SDP final WebRTC server
- `real_webrtc_server_fixed.py` - Real fixed WebRTC server

### /device_management
Device and NVR management scripts
- `add_http_nvr.py` - Add HTTP NVR device
- `device_status_checker.py` - Check device status
- `import_devices.py` - Import devices from file
- `query_devices.py` - Query device information
- `fix_nvr_config.py` - Fix NVR configuration
- `channel_url_generator.py` - Generate channel URLs
- `devices.csv` - Device configuration file

### /database
Database management and maintenance scripts
- `db_manager.py` - Database manager
- `check_db.py` - Check database integrity
- `test_db_exceptions.py` - Test database exceptions
- `fix_data_sync.py` - Fix data synchronization

### /system
System monitoring and management scripts
- `heartbeat_monitor.py` - Monitor system heartbeat
- `heartbeat_service.py` - Heartbeat service
- `install_heartbeat_service.py` - Install heartbeat service
- `monitor_dashboard.py` - System dashboard
- `directory_guard.py` - Directory protection
- `exception_handler.py` - Exception handling

### /setup
Setup and configuration scripts
- `auto_setup.py` - Automatic setup
- `migrate_configs.py` - Migrate configurations
- `switch_environment.py` - Switch environment
- `fix_port_mapping.py` - Fix port mapping

### /development
Development and testing tools
- `quick_check.py` - Quick system check
- `dev-lint.bat` - Development linting
- `dev-start.bat` - Start development environment
- `dev-stop.bat` - Stop development environment
- `dev-test.bat` - Run development tests
- `start_stable.bat` - Start stable services
- `start_stable_services.bat` - Start stable services batch

### /vlc
VLC media player related scripts
- `start_vlc_monitor.bat` - Start VLC monitoring

## Batch Files
All batch files remain in root directory for easy access:
- `*_run.bat` files for each main script
- Original batch files moved to appropriate categories

## Backup Files
- `backup/` directory contains test and recovery scripts
- All original files are preserved

## Usage Examples

### 1. Fix Authentication Issues
```bash
# Method 1: Original path
python scripts/fix_auth_issue.py

# Method 2: New organized path
python scripts/auth/fix_auth_issue.py

# Method 3: Compatibility runner
python scripts/_compatibility_runner.py fix_auth_issue.py
```

### 2. Start WebRTC Server
```bash
# Method 1: Original path
python scripts/webrtc_server_fingerprint_fix.py --host 127.0.0.1 --port 8080

# Method 2: New organized path
python scripts/webrtc/webrtc_server_fingerprint_fix.py --host 127.0.0.1 --port 8080
```

### 3. Add NVR Device
```bash
# Method 1: Original path
python scripts/add_http_nvr.py

# Method 2: New organized path
python scripts/device_management/add_http_nvr.py
```

## Tips

1. **All existing shortcuts and batch files continue to work**
2. **New scripts should be placed in appropriate categories**
3. **Use the compatibility runner if unsure of script location**
4. **Check README.md for detailed category descriptions**

## Troubleshooting

If a script doesn't work:
1. Check if it's in the correct category
2. Use compatibility runner: `python scripts/_compatibility_runner.py <script_name>`
3. Verify script exists in its new location
4. Check script permissions if needed