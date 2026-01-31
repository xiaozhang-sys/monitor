#!/usr/bin/env python3
"""
自动配置设置脚本
一键完成环境初始化和验证
"""
import os
import sys
from pathlib import Path
import subprocess

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def print_status(message, success=True):
    """打印状态信息"""
    status = "✅" if success else "❌"
    print(f"{status} {message}")

def main():
    print("🚀 自动配置设置开始...")
    print("=" * 50)
    
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # 1. 验证所有环境配置
    print("\n📋 验证环境配置...")
    
    environments = ["development", "test", "production"]
    for env in environments:
        success, stdout, stderr = run_command(f"python scripts/switch_environment.py --validate {env}")
        if success:
            print_status(f"{env} 环境验证通过")
        else:
            print_status(f"{env} 环境验证失败: {stderr}", False)
    
    # 2. 切换到开发环境
    print("\n🔄 设置开发环境为默认...")
    success, stdout, stderr = run_command("python scripts/switch_environment.py development")
    if success:
        print_status("已切换到开发环境")
        print(stdout)
    else:
        print_status("切换环境失败", False)
    
    # 3. 验证当前配置
    print("\n🔍 验证当前配置...")
    success, stdout, stderr = run_command("python config/validate_config.py")
    if success:
        print_status("配置验证通过")
        print(stdout)
    else:
        print_status("配置验证失败", False)
    
    # 4. 显示使用说明
    print("\n📖 使用说明:")
    print("-" * 30)
    print("环境管理命令:")
    print("  查看当前环境: python scripts/switch_environment.py --current")
    print("  切换环境: python scripts/switch_environment.py [development|test|production]")
    print("  验证环境: python scripts/switch_environment.py --validate [environment]")
    print("  迁移配置: python scripts/migrate_configs.py")
    
    print("\n🎉 自动配置设置完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()