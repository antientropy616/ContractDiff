#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合同对比助手 - 测试启动脚本
"""

import sys
import os
import time

# 添加 src 到路径
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

print("Python 版本:", sys.version)
print("工作目录:", os.getcwd())

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QFont
    import platform
    
    print("\n✅ PyQt6 导入成功")
    print("系统:", platform.system())
    
    # 创建简单测试窗口
    app = QApplication(sys.argv)
    
    font_name = "PingFang SC" if platform.system() == "Darwin" else "Microsoft YaHei"
    print("使用字体:", font_name)
    
    window = QMainWindow()
    window.setWindowTitle("合同对比助手 - 测试窗口")
    window.setGeometry(200, 200, 500, 250)
    
    label = QLabel("合同对比助手 v1.2.3\n\n✅ PyQt6 工作正常\n✅ 窗口已显示\n\n窗口将在 30 秒后自动关闭", window)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setFont(QFont(font_name, 18))
    window.setCentralWidget(label)
    
    print("\n🚀 显示窗口...")
    window.show()
    window.raise_()
    window.activateWindow()
    
    print("✅ 窗口已显示")
    print("⏱️  等待 30 秒后自动关闭...")
    
    # 运行 30 秒
    for i in range(30):
        time.sleep(1)
        app.processEvents()
        if i % 5 == 0:
            print(f"   已运行 {i} 秒...")
    
    print("✅ 测试完成")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ 错误：{e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
