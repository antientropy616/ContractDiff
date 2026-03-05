#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建脚本 - 打包成 macOS App（优化版）
优化目标：
1. 修复 PyQt6 位置服务崩溃
2. 精简体积（移除不必要的库）
"""

import os
import sys
import subprocess
import shutil
import platform
import json

def build(debug=False):
    """执行 macOS 构建（优化版）"""
    version = "1.2.3"
    print("=" * 60)
    print(f"合同对比助手 v{version} - macOS 构建脚本（优化版）")
    if debug:
        print("（调试模式）")
    print("=" * 60)
    
    # 检查系统
    if platform.system() != "Darwin":
        print(f"⚠️  警告：当前系统是 {platform.system()}，此脚本专为 macOS 设计")
        response = input("继续构建？(y/N): ")
        if response.lower() != 'y':
            print("构建已取消")
            return False
    
    # 项目路径
    project_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_dir, "src")
    dist_dir = os.path.join(project_dir, "dist")
    build_dir = os.path.join(project_dir, "build")
    
    # 清理旧的构建文件
    print("\n[1/7] 清理旧的构建文件...")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    print("      完成")
    
    # 执行 PyInstaller 打包
    print("\n[2/7] 执行打包（优化配置）...")
    print("      这可能需要几分钟时间...")
    
    app_name = "合同对比助手_debug" if debug else "合同对比助手"
    
    try:
        # 使用命令行方式构建（更灵活的控制）
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "--windowed",  # 生成 .app 包
            "--name", app_name,
            "--onedir",  # 文件夹模式
            "--paths", src_dir,
            
            # 排除不必要的模块（精简体积）
            "--exclude-module", "tkinter",
            "--exclude-module", "matplotlib",
            "--exclude-module", "scipy",
            "--exclude-module", "numpy",  # 我们不需要 numpy
            "--exclude-module", "PIL",  # 不需要图像处理
            "--exclude-module", "pillow",
            "--exclude-module", "cv2",  # 不需要 opencv
            "--exclude-module", "PyMuPDF",  # 不需要 PDF 渲染
            "--exclude-module", "pdf2docx",  # 不需要 PDF 转 Word（太占空间）
            "--exclude-module", "pdfplumber",  # 同上
            "--exclude-module", "pytest",
            "--exclude-module", "_pyi_rth_utils",
            
            # 必要的隐藏导入
            "--hidden-import", "core",
            "--hidden-import", "core.doc_comparator",
            "--hidden-import", "ui",
            "--hidden-import", "ui.main_window",
            "--hidden-import", "utils",
            "--hidden-import", "utils.logger",
            "--hidden-import", "utils.error_handler",
            "--hidden-import", "utils.pdf_handler",
            "--hidden-import", "utils.updater",
            "--hidden-import", "utils.styles",
            "--hidden-import", "docx",
            "--hidden-import", "openpyxl",
            "--hidden-import", "diff_match_patch",
            
            # 数据文件
            "--add-data", f"version.json{os.pathsep}.",
            
            # 入口文件
            os.path.join(src_dir, "main.py")
        ]
        
        subprocess.check_call(cmd, cwd=project_dir)
        print("      完成")
    except subprocess.CalledProcessError as e:
        print(f"      错误：{e}")
        return False
    
    # 复制 App 到文稿文件夹
    print("\n[3/7] 复制 App 到文稿文件夹...")
    documents_dir = os.path.expanduser("~/Documents")
    app_src = os.path.join(dist_dir, f"{app_name}.app")
    app_dest = os.path.join(documents_dir, f"{app_name}.app")
    
    if os.path.exists(app_dest):
        shutil.rmtree(app_dest)
    
    if os.path.exists(app_src):
        shutil.copytree(app_src, app_dest)
        print(f"      完成")
        print(f"      App 已保存至：{app_dest}")
    else:
        print("      警告：未找到生成的 .app 文件")
        return False
    
    # 修改 Info.plist 禁用位置权限（修复崩溃）
    print("\n[4/7] 修改 Info.plist 禁用位置权限...")
    info_plist = os.path.join(app_dest, "Contents", "Info.plist")
    if os.path.exists(info_plist):
        # 读取并修改 plist
        try:
            import plistlib
            with open(info_plist, 'rb') as f:
                plist = plistlib.load(f)
            
            # 添加权限限制
            plist['NSLocationWhenInUseUsageDescription'] = 'This app does not use location services'
            plist['NSLocationUsageDescription'] = 'This app does not use location services'
            plist['NSLocationAlwaysAndWhenInUseUsageDescription'] = 'This app does not use location services'
            
            # 设置最小系统版本
            plist['LSMinimumSystemVersion'] = '10.15'
            
            # 设置版本信息
            plist['CFBundleShortVersionString'] = version
            plist['CFBundleVersion'] = version.replace('.', '')
            
            with open(info_plist, 'wb') as f:
                plistlib.dump(plist, f)
            
            print("      完成")
        except Exception as e:
            print(f"      警告：修改 Info.plist 失败：{e}")
    else:
        print("      警告：未找到 Info.plist")
    
    # 创建 entitlements 文件（进一步限制权限）
    print("\n[5/7] 创建 Entitlements 文件...")
    entitlements_path = os.path.join(project_dir, "entitlements.plist")
    entitlements_content = b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.app-sandbox</key>
    <false/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <false/>
</dict>
</plist>
'''
    with open(entitlements_path, 'wb') as f:
        f.write(entitlements_content)
    print(f"      完成：{entitlements_path}")
    
    # 重新签名 App（应用 entitlements）
    print("\n[6/7] 重新签名 App...")
    try:
        # 先移除旧签名
        subprocess.run([
            "codesign", "--remove-signature", app_dest
        ], check=False, capture_output=True)
        
        # 使用 ad-hoc 签名
        subprocess.run([
            "codesign",
            "--force",
            "--deep",
            "--sign", "-",
            "--entitlements", entitlements_path,
            app_dest
        ], check=False, capture_output=True)
        
        print("      完成")
    except Exception as e:
        print(f"      警告：签名失败：{e}")
    
    # 创建启动脚本和说明文档
    print("\n[7/7] 创建辅助文件...")
    
    # 启动脚本
    launcher_script = os.path.join(documents_dir, "启动合同对比助手.command")
    with open(launcher_script, "w", encoding="utf-8") as f:
        f.write(f'''#!/bin/bash
# 合同对比助手启动脚本
echo "正在启动合同对比助手..."
open "{app_dest}"
''')
    os.chmod(launcher_script, 0o755)
    
    # 使用说明
    readme_path = os.path.join(documents_dir, "合同对比助手_macOS_使用说明.txt")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"""合同对比助手 v{version} - macOS 版使用说明
=====================================

📦 安装位置：
   {app_dest}

🚀 启动方式：
   1. 双击 {app_name}.app
   2. 或运行：启动合同对比助手.command

⚠️  首次运行提示：
   macOS 可能会提示"无法打开，因为来自身份不明的开发者"
   解决方法：
   1. 打开"系统偏好设置" → "安全性与隐私"
   2. 点击"仍要打开"
   3. 之后就可以正常打开了

📝 日志文件位置：
   ~/Documents/合同对比助手/logs/

📚 功能特点：
   • 自动识别文字增删改
   • 详细改动列表输出（第 X 段）
   • 生成 Excel 对比报告
   • 支持 Word (.docx) 格式
   • 日志记录与异常处理
   • 自动更新检查

⚠️  PDF 支持说明：
   为精简体积，macOS 版移除了 PDF 处理功能
   如需 PDF 支持，请使用 Windows 版或从源码运行

🔧 技术支持：
   如有问题，请查看日志文件或联系开发团队。

---
玉哥与他的虾
版权所有 © 2026
""")
    
    # 显示体积信息
    app_size = 0
    for dirpath, dirnames, filenames in os.walk(app_dest):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            app_size += os.path.getsize(fp)
    
    print(f"\n      启动脚本：{launcher_script}")
    print(f"      使用说明：{readme_path}")
    print(f"\n📊 App 体积：{app_size / 1024 / 1024:.1f} MB")
    
    print("\n" + "=" * 60)
    print("🎉 macOS 构建完成！")
    
    if debug:
        print("\n📝 调试版说明:")
        print("   • 运行时会显示控制台窗口")
        print("   • 可以看到详细的错误信息")
    else:
        print("\n📝 发布版说明:")
        print("   • 无控制台窗口")
        print("   • 已禁用位置服务权限（修复崩溃）")
        print("   • 已移除不必要的依赖（精简体积）")
    
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="构建合同对比助手 macOS 版（优化）")
    parser.add_argument("--debug", action="store_true", help="构建调试版本（带控制台窗口）")
    args = parser.parse_args()
    
    success = build(debug=args.debug)
    sys.exit(0 if success else 1)
