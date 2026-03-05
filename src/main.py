#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合同对比助手
Contract Diff Tool

主程序入口 - 带启动错误捕获
"""

import sys
import os
import json
import traceback
from datetime import datetime


def get_version():
    """从 version.json 读取版本号"""
    try:
        # 尝试多个可能的路径
        paths_to_try = []
        
        # 当前脚本所在目录
        if hasattr(sys, '_MEIPASS'):
            paths_to_try.append(os.path.join(sys._MEIPASS, 'version.json'))
        
        paths_to_try.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'version.json'))
        paths_to_try.append(os.path.join(os.path.dirname(__file__), '..', 'version.json'))
        paths_to_try.append(os.path.join(os.getcwd(), 'version.json'))
        
        for version_file in paths_to_try:
            if os.path.exists(version_file):
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    version = data.get('version', '1.0.0')
                    print(f"✅ 读取版本号：{version} (from {version_file})")
                    return version
        
        print("⚠️ 未找到 version.json，使用默认版本号 1.0.0")
    except Exception as e:
        print(f"⚠️ 读取 version.json 失败：{e}")
    
    return '1.0.0'


VERSION = get_version()

# 启动时立即捕获错误
def excepthook(exctype, value, tb):
    """全局异常捕获"""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    
    # 写入错误文件
    log_dir = os.path.join(os.path.expanduser("~"), "Documents", "合同对比助手", "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    error_file = os.path.join(log_dir, f"crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    with open(error_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write(f"崩溃时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(error_msg)
    
    print("=" * 60)
    print("程序发生严重错误！")
    print("=" * 60)
    print(error_msg)
    print("=" * 60)
    print(f"错误日志已保存至：{error_file}")
    print("=" * 60)
    
    sys.exit(1)

# 安装全局异常钩子
sys.excepthook = excepthook

try:
    # 确保使用绝对导入
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont
    
    # 尝试导入主窗口
    try:
        from ui.main_window import MainWindow
    except ImportError as e:
        # 如果相对导入失败，尝试添加 src 到路径
        import sys
        import os
        src_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'src')
        if os.path.exists(src_path) and src_path not in sys.path:
            sys.path.insert(0, src_path)
        from ui.main_window import MainWindow
        
except ImportError as e:
    print("=" * 60)
    print("导入模块失败！")
    print("=" * 60)
    print(f"错误：{e}")
    print("=" * 60)
    traceback.print_exc()
    input("\n按回车键退出...")
    sys.exit(1)


def main():
    """主函数"""
    try:
        print(f"正在启动合同对比助手 v{VERSION}...")
        
        # 启用高 DPI 支持
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        print("创建 QApplication...")
        app = QApplication(sys.argv)
        
        # 设置应用信息
        app.setApplicationName("合同对比助手")
        app.setApplicationVersion(VERSION)
        app.setOrganizationName("ContractDiffTool")
        
        # 设置全局字体（跨平台兼容）
        print("设置字体...")
        import platform
        system = platform.system()
        if system == "Darwin":  # macOS
            font = QFont("PingFang SC", 10)
        elif system == "Windows":
            font = QFont("Microsoft YaHei", 10)
        else:  # Linux 等其他系统
            font = QFont("WenQuanYi Micro Hei", 10)
        app.setFont(font)
        
        # 创建主窗口
        print("创建主窗口...")
        window = MainWindow()
        print("显示窗口...")
        window.show()
        
        print("程序启动成功！")
        sys.exit(app.exec())
        
    except Exception as e:
        print("=" * 60)
        print("启动失败！")
        print("=" * 60)
        print(f"错误：{e}")
        print("=" * 60)
        traceback.print_exc()
        input("\n按回车键退出...")
        sys.exit(1)


if __name__ == "__main__":
    main()
