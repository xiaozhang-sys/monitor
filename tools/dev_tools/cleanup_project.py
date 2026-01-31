#!/usr/bin/env python3
"""
项目清理脚本
自动识别并清理冗余文件，优化项目目录结构
"""

import os
import shutil
import glob
from datetime import datetime

class ProjectCleaner:
    def __init__(self, root_path):
        self.root_path = root_path
        self.cleaned_files = []
        self.cleaned_dirs = []
        
    def find_redundant_files(self):
        """查找冗余文件"""
        redundant_patterns = [
            "**/*.pyc",
            "**/*.pyo", 
            "**/*.pyd",
            "**/__pycache__",
            "**/*.log",
            "**/*.tmp",
            "**/*.bak",
            "**/*.old",
            "**/*~",
            "**/.DS_Store",
            "**/Thumbs.db",
            "**/node_modules/**",
            "**/*.egg-info"
        ]
        
        redundant_files = []
        for pattern in redundant_patterns:
            matches = glob.glob(os.path.join(self.root_path, pattern), recursive=True)
            redundant_files.extend(matches)
            
        return redundant_files
    
    def find_empty_dirs(self):
        """查找空目录"""
        empty_dirs = []
        for root, dirs, files in os.walk(self.root_path):
            # 忽略.git等隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            if not dirs and not files:
                empty_dirs.append(root)
                
        return empty_dirs
    
    def cleanup_files(self, dry_run=True):
        """清理文件"""
        redundant_files = self.find_redundant_files()
        
        print("🔍 发现冗余文件:")
        for file_path in redundant_files:
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"  📄 {file_path} ({size} bytes)")
                if not dry_run:
                    try:
                        os.remove(file_path)
                        self.cleaned_files.append(file_path)
                    except Exception as e:
                        print(f"  ❌ 删除失败: {e}")
            elif os.path.isdir(file_path):
                print(f"  📁 {file_path}/")
                if not dry_run:
                    try:
                        shutil.rmtree(file_path)
                        self.cleaned_dirs.append(file_path)
                    except Exception as e:
                        print(f"  ❌ 删除失败: {e}")
    
    def cleanup_empty_dirs(self, dry_run=True):
        """清理空目录"""
        empty_dirs = self.find_empty_dirs()
        
        print("\n🔍 发现空目录:")
        for dir_path in empty_dirs:
            print(f"  📁 {dir_path}/")
            if not dry_run:
                try:
                    os.rmdir(dir_path)
                    self.cleaned_dirs.append(dir_path)
                except Exception as e:
                    print(f"  ❌ 删除失败: {e}")
    
    def generate_cleanup_report(self):
        """生成清理报告"""
        report = f"""
# 🧹 项目清理报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 清理统计
- 清理文件数: {len(self.cleaned_files)}
- 清理目录数: {len(self.cleaned_dirs)}

## 🗂️ 已清理文件
"""
        
        if self.cleaned_files:
            report += "\n### 文件:\n"
            for file in self.cleaned_files:
                report += f"- {file}\n"
                
        if self.cleaned_dirs:
            report += "\n### 目录:\n"
            for dir in self.cleaned_dirs:
                report += f"- {dir}\n"
                
        if not self.cleaned_files and not self.cleaned_dirs:
            report += "\n✅ 无需清理，项目已优化！\n"
            
        return report
    
    def run_cleanup(self, dry_run=True):
        """运行清理"""
        print("🧹 开始项目清理...")
        
        # 清理冗余文件
        self.cleanup_files(dry_run)
        
        # 清理空目录
        self.cleanup_empty_dirs(dry_run)
        
        # 生成报告
        report = self.generate_cleanup_report()
        print(report)
        
        # 保存报告
        if not dry_run:
            with open("cleanup_report.md", "w", encoding="utf-8") as f:
                f.write(report)
            print("📄 清理报告已保存到: cleanup_report.md")

def main():
    """主函数"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    cleaner = ProjectCleaner(root_path)
    
    print("🎯 项目清理工具")
    print("=" * 50)
    
    # 先进行干运行检查
    print("\n🔍 干运行检查（仅显示，不删除）:")
    cleaner.run_cleanup(dry_run=True)
    
    # 询问是否执行清理
    choice = input("\n❓ 是否执行清理？(y/N): ").strip().lower()
    if choice == 'y':
        print("\n🗑️ 执行清理...")
        cleaner.run_cleanup(dry_run=False)
        print("✅ 清理完成！")
    else:
        print("❌ 取消清理")

if __name__ == "__main__":
    main()