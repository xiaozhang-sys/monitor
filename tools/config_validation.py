#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置验证脚本 - 检查文档和配置是否反映当前运行环境
"""
import os
import json
import re
from pathlib import Path

# 当前实际运行环境的配置
CURRENT_CONFIG = {
    "ports": {
        "backend": 8004,
        "frontend": 5173,
        "webrtc": 8081,
        "hevc": 8090
    },
    "tech_stack": {
        "backend": "FastAPI",
        "db": "SQLite",
        "frontend": "Vue 3",
        "streaming": "WebRTC",
        "hevc_support": True
    },
    "deployment_type": "local",  # local or docker
    "has_test_devices": True
}

# 需要检查的文件列表
CHECK_FILES = [
    # 文档文件
    "docs/QUICK_START.md",
    "docs/DOCUMENTATION_INDEX.md",
    "docs/ARCHITECTURE.md",
    "docs/API_DOCUMENTATION.md",
    "docs/PORT_FIX_SUMMARY.md",
    "README.md",
    
    # 配置文件
    "config/port_config_new.json",
    "config/docker_config.json",
    "config/apps/backend.json",
    "config/webrtc_config.json"
]

def read_file(file_path):
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️  无法读取文件 {file_path}: {e}")
        return ""

def validate_document(file_path, content):
    """验证文档内容是否反映当前环境"""
    issues = []
    
    # 检查端口配置
    for service, port in CURRENT_CONFIG["ports"].items():
        # 查找旧端口配置（如果有）
        if service == "backend":
            old_ports = [8000, 8001]
        elif service == "webrtc":
            old_ports = [8080, 8889]
        else:
            old_ports = []
        
        # 检查是否使用了正确的端口
        if str(port) not in content and file_path.endswith(".md"):
            issues.append(f"未找到正确的{service}端口配置({port})")
        
        # 检查是否仍有旧端口配置
        for old_port in old_ports:
            if str(old_port) in content and service not in content:
                issues.append(f"仍包含旧的{service}端口配置({old_port})")
    
    # 检查技术栈描述
    if "FastAPI" not in content and "架构" in content:
        issues.append("技术栈描述中缺少FastAPI或仍使用Flask")
    
    # 检查HEVC支持
    if CURRENT_CONFIG["tech_stack"]["hevc_support"] and "HEVC" not in content and "H.265" not in content:
        if "架构" in content or "功能特性" in content:
            issues.append("未提及HEVC/H.265视频支持")
    
    # 检查部署类型
    if CURRENT_CONFIG["deployment_type"] == "local":
        if "Docker" in content and "不再使用" not in content:
            issues.append("仍包含Docker部署相关内容")
    
    return issues

def validate_config(file_path, content):
    """验证配置文件内容是否反映当前环境"""
    issues = []
    
    try:
        config = json.loads(content)
        
        # 检查端口配置
        if "ports" in config:
            for service, port_info in config["ports"].items():
                if service in CURRENT_CONFIG["ports"]:
                    expected_port = CURRENT_CONFIG["ports"][service]
                    # 处理不同的配置格式
                    if isinstance(port_info, dict):
                        if "dev" in port_info and port_info["dev"] != expected_port:
                            issues.append(f"{service}开发端口配置错误: 期望{expected_port}，实际{port_info['dev']}")
                    elif isinstance(port_info, int) and port_info != expected_port:
                        issues.append(f"{port_info}端口配置错误: 期望{expected_port}，实际{port_info}")
        
        # 检查docker_config.json
        if file_path.endswith("docker_config.json"):
            if "services" in config and len(config["services"]) > 0:
                issues.append("docker_config.json仍包含服务配置，应为空")
    except json.JSONDecodeError:
        issues.append("配置文件不是有效的JSON格式")
    
    return issues

def main():
    """主函数"""
    print("===== 配置验证脚本 =====")
    print(f"检查 {len(CHECK_FILES)} 个文件...\n")
    
    total_issues = 0
    
    for file_path in CHECK_FILES:
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", file_path)
        
        if not os.path.exists(full_path):
            print(f"⚠️  文件不存在: {file_path}")
            continue
        
        content = read_file(full_path)
        
        if file_path.endswith(".json"):
            issues = validate_config(file_path, content)
        else:
            issues = validate_document(file_path, content)
        
        if issues:
            total_issues += len(issues)
            print(f"❌  {file_path} 存在 {len(issues)} 个问题:")
            for issue in issues:
                print(f"   - {issue}")
            print()
        else:
            print(f"✅  {file_path} 验证通过\n")
    
    print("===== 验证结果总结 =====")
    if total_issues == 0:
        print("🎉  所有文件验证通过！配置文档已反映当前运行环境。")
    else:
        print(f"⚠️  共发现 {total_issues} 个问题需要修复。")
        print("建议：根据以上提示更新相关文件。")
    
if __name__ == "__main__":
    main()