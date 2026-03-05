#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合同对比助手 - macOS 最终构建脚本
功能：
1. 生成独立 .app
2. 包含 PDF 支持
3. 代码签名
4. 自动打开结果文档（已集成到主程序）
"""

import os
import sys
import subprocess
import shutil
import platform
import plistlib

def build(debug=False):
    """执行最终构建"""
    version = "1.2.3"
    print("=" * 70)
    print(f"合同对比助手 v{version} - macOS 最终构建")
    print("=" * 70)
    
    if platform.system() != "Darwin":
        print(f"❌ 错误：此脚本仅在 macOS 上运行")
        return False
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_dir, "src")
    dist_dir = os.path.join(project_dir, "dist")
    build_dir = os.path.join(project_dir, "build")
    
    # 清理
    print("\n[1/8] 清理旧构建...")
    for d in [dist_dir, build_dir]:
        if os.path.exists(d):
            shutil.rmtree(d)
    print("      ✅ 完成")
    
    # PyInstaller 打包
    print("\n[2/8] 执行 PyInstaller 打包...")
    app_name = "合同对比助手_debug" if debug else "合同对比助手"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean", "--noconfirm",
        "--windowed",
        "--name", app_name,
        "--onedir",
        "--paths", src_dir,
        
        # 排除不必要的（这些库导致签名问题）
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "scipy",
        "--exclude-module", "pytest",
        "--exclude-module", "cv2",
        "--exclude-module", "opencv_python_headless",
        "--exclude-module", "PIL",
        "--exclude-module", "pillow",
        
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
        "--hidden-import", "pdfplumber",
        "--hidden-import", "pdf2docx",
        "--hidden-import", "PyMuPDF",
        
        # 数据文件
        "--add-data", f"version.json{os.pathsep}.",
        
        # 入口
        os.path.join(src_dir, "main.py")
    ]
    
    try:
        subprocess.check_call(cmd, cwd=project_dir)
        print("      ✅ 完成")
    except subprocess.CalledProcessError as e:
        print(f"      ❌ 错误：{e}")
        return False
    
    # 复制 App
    print("\n[3/8] 复制 App 到文稿文件夹...")
    documents_dir = os.path.expanduser("~/Documents")
    app_src = os.path.join(dist_dir, f"{app_name}.app")
    app_dest = os.path.join(documents_dir, f"{app_name}.app")
    
    if os.path.exists(app_dest):
        shutil.rmtree(app_dest)
    
    if os.path.exists(app_src):
        shutil.copytree(app_src, app_dest)
        print(f"      ✅ {app_dest}")
    else:
        print("      ❌ 未找到 .app")
        return False
    
    # 修改 Info.plist
    print("\n[4/8] 配置 Info.plist...")
    info_plist = os.path.join(app_dest, "Contents", "Info.plist")
    try:
        with open(info_plist, 'rb') as f:
            plist = plistlib.load(f)
        
        plist['CFBundleIdentifier'] = 'com.yuclaw.contractdiff'
        plist['CFBundleShortVersionString'] = version
        plist['CFBundleVersion'] = version.replace('.', '')
        plist['LSMinimumSystemVersion'] = '10.15'
        plist['NSHighResolutionCapable'] = True
        
        # 权限说明（禁用位置服务）
        plist['NSLocationWhenInUseUsageDescription'] = 'This app does not use location'
        plist['NSLocationUsageDescription'] = 'This app does not use location'
        plist['NSLocationAlwaysAndWhenInUseUsageDescription'] = 'This app does not use location'
        plist['NSCameraUsageDescription'] = 'This app does not use camera'
        plist['NSMicrophoneUsageDescription'] = 'This app does not use microphone'
        
        with open(info_plist, 'wb') as f:
            plistlib.dump(plist, f)
        
        print("      ✅ 完成")
    except Exception as e:
        print(f"      ⚠️ 警告：{e}")
    
    # 创建 Entitlements
    print("\n[5/8] 创建 Entitlements...")
    entitlements_path = os.path.join(project_dir, "entitlements.plist")
    entitlements = {
        'com.apple.security.app-sandbox': False,
        'com.apple.security.files.user-selected.read-write': True,
        'com.apple.security.network.client': False,
    }
    with open(entitlements_path, 'wb') as f:
        plistlib.dump(entitlements, f)
    print(f"      ✅ {entitlements_path}")
    
    # 代码签名
    print("\n[6/8] 代码签名...")
    try:
        # 移除旧签名
        subprocess.run(['codesign', '--remove-signature', app_dest],
                      capture_output=True, check=False)
        
        # 简单深度签名（不处理子组件）
        result = subprocess.run(['codesign', '--force', '--deep', '--sign', '-', app_dest],
                               capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("      ✅ 签名成功")
        else:
            # 即使失败也继续（ad-hoc 签名可能不完美但能运行）
            print(f"      ⚠️ 签名警告（仍可运行）")
    except subprocess.TimeoutExpired:
        print("      ⚠️ 签名超时")
    except Exception as e:
        print(f"      ⚠️ 签名失败：{e}")
    
    # 清除隔离属性
    print("\n[7/8] 清除隔离属性...")
    try:
        subprocess.run(['xattr', '-cr', app_dest], check=True, capture_output=True)
        print("      ✅ 完成")
    except Exception as e:
        print(f"      ⚠️ 警告：{e}")
    
    # 创建辅助文件
    print("\n[8/8] 创建辅助文件...")
    
    # 启动脚本
    launcher = os.path.join(documents_dir, "启动合同对比助手.command")
    with open(launcher, 'w') as f:
        f.write(f'#!/bin/bash\nopen "{app_dest}"\n')
    os.chmod(launcher, 0o755)
    
    # 说明文档
    readme = os.path.join(documents_dir, "合同对比助手_使用说明.txt")
    with open(readme, 'w', encoding='utf-8') as f:
        f.write(f"""合同对比助手 v{version} - macOS 版
=====================================

✅ 功能特点：
• 自动识别文字增删改
• 详细改动列表输出
• 生成 Excel 对比报告
• 支持 Word (.docx) 和 PDF 格式
• 日志记录与异常处理
• 自动更新检查
• 自动打开结果文档

📦 安装位置：
{app_dest}

🚀 启动方式：
1. 双击 {app_name}.app
2. 或运行：启动合同对比助手.command
3. 或终端：open "{app_dest}"

⚠️  首次运行：
如提示"身份不明的开发者"：
1. 系统偏好设置 → 安全性与隐私
2. 点击"仍要打开"

📁 结果文件：
~/Documents/合同对比结果_*.docx
~/Documents/合同对比报告_*.xlsx

📝 日志文件：
~/Documents/合同对比助手/logs/

---
玉哥与他的虾
2026-03-05
""")
    
    print(f"      ✅ 启动脚本：{launcher}")
    print(f"      ✅ 使用说明：{readme}")
    
    # 显示信息
    app_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                   for dirpath, dirnames, filenames in os.walk(app_dest)
                   for filename in filenames)
    
    print(f"\n📊 App 体积：{app_size / 1024 / 1024:.1f} MB")
    
    # 验证签名
    print("\n🔍 验证签名...")
    result = subprocess.run(['codesign', '--verify', app_dest],
                           capture_output=True, text=True)
    if result.returncode == 0:
        print("      ✅ 签名验证通过")
    else:
        print(f"      ⚠️ 签名验证：{result.stderr}")
    
    print("\n" + "=" * 70)
    print("🎉 构建完成！")
    print("=" * 70)
    print(f"\n📍 位置：{app_dest}")
    print("\n✅ 已完成：")
    print("   1. 生成独立 .app")
    print("   2. 包含 PDF 支持")
    print("   3. 代码签名")
    print("   4. 自动打开结果文档")
    print("\n🚀 现在可以双击运行！")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="合同对比助手 macOS 最终构建")
    parser.add_argument("--debug", action="store_true", help="构建调试版")
    args = parser.parse_args()
    
    success = build(debug=args.debug)
    sys.exit(0 if success else 1)
