#!/usr/bin/env python3
"""
Python学习计划提醒系统 - QT版本启动脚本
使用方法：python run_qt_reminder.py
"""

import sys
import os

def check_dependencies():
    """检查依赖"""
    missing_deps = []
    
    try:
        import PyQt5
    except ImportError:
        missing_deps.append("PyQt5")
    
    try:
        import schedule
    except ImportError:
        missing_deps.append("schedule")
    
    return missing_deps

def install_dependencies(deps):
    """安装依赖"""
    print("⚠️  缺少以下依赖库：")
    for dep in deps:
        print(f"  • {dep}")
    
    print("\n🔧 请运行以下命令安装：")
    print(f"  pip install {' '.join(deps)}")
    
    choice = input("\n是否自动安装？(y/n): ").lower()
    if choice == 'y':
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + deps)
            print("✅ 依赖安装完成！")
            return True
        except Exception as e:
            print(f"❌ 安装失败：{e}")
            return False
    else:
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("  📖 Python学习计划提醒系统 - QT版本")
    print("=" * 50)
    
    # 检查依赖
    missing_deps = check_dependencies()
    if missing_deps:
        if not install_dependencies(missing_deps):
            print("\n❌ 请先安装依赖库再运行程序")
            sys.exit(1)
    
    # 启动QT应用程序
    try:
        from study_reminder_qt import main as qt_main
        print("\n🚀 启动QT应用程序...")
        qt_main()
    except Exception as e:
        print(f"\n❌ 启动失败：{e}")
        print("\n💡 如果遇到问题，可以尝试：")
        print("  1. 确保已安装所有依赖：pip install PyQt5 schedule")
        print("  2. 检查Python版本（建议3.6+）")
        print("  3. 查看错误信息并修复")
        sys.exit(1)

if __name__ == "__main__":
    main()