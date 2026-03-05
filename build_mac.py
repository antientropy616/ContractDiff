#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建脚本 - 打包成 macOS App
"""

import os
import sys
import subprocess
import shutil
import platform

def build(debug=False):
    """执行 macOS 构建"""
    version = "1.2.3"
    print("=" * 60)
    print(f"合同对比助手 v{version} - macOS 构建脚本")
    if debug:
        print("（调试模式）")
    print("=" * 60)
    
    # 检查系统
    if platform.system() != "Darwin":
        print(f"⚠️  警告：当前系统是 {platform.system()}，此脚本专为 macOS 设计")
        print("   在 macOS 上运行才能获得最佳结果")
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
    print("\n[1/6] 清理旧的构建文件...")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    print("      完成")
    
    # 创建 PyInstaller spec 文件
    print(f"\n[2/6] 创建打包配置{'（调试）' if debug else ''}...")
    
    app_name = "合同对比助手_debug" if debug else "合同对比助手"
    console_setting = "True" if debug else "False"
    upx_setting = "False" if debug else "True"
    
    # 使用正斜杠（macOS 路径）
    src_dir_escaped = src_dir
    
    spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[r'{src_dir_escaped}'],
    binaries=[],
    datas=[
        ('src/core', 'core'),
        ('src/ui', 'ui'),
        ('src/utils', 'utils'),
        ('version.json', '.'),
    ],
    hiddenimports=[
        # Word 处理
        'docx',
        'docx.opc',
        'docx.opc.oxml',
        'docx.oxml',
        'docx.oxml.ns',
        'docx.text',
        'docx.styles',
        'docx.enum',
        'docx.shared',
        'docx.oxml.simpletypes',
        'docx.oxml.ns',
        'docx.enum.style',
        'docx.enum.table',
        'docx.enum.section',
        'docx.enum.text',
        'docx.formatting',
        
        # Excel 处理
        'openpyxl',
        'openpyxl.workbook',
        'openpyxl.worksheet',
        'openpyxl.cell',
        'openpyxl.styles',
        'openpyxl.utils',
        'openpyxl.reader',
        'openpyxl.writer',
        
        # PyQt6
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        
        # 项目模块 - 使用点号格式
        'core',
        'core.doc_comparator',
        'core.__init__',
        'ui',
        'ui.main_window',
        'ui.__init__',
        'utils',
        'utils.logger',
        'utils.error_handler',
        'utils.pdf_handler',
        'utils.updater',
        'utils.styles',
        'utils.__init__',
        
        # 标准库
        'logging',
        'logging.handlers',
        'json',
        're',
        'tempfile',
        'datetime',
        'os',
        'sys',
        'webbrowser',
        'collections',
        'encodings',
        'encodings.utf_8',
        'hashlib',
        'io',
        'difflib',
        'traceback',
        'subprocess',
        'shutil',
        'zipfile',
        'platform',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'numpy',
        'PIL',
        'pillow',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

app = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx={upx_setting},
    upx_exclude=[],
    runtime_tmpdir=None,
    console={console_setting},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    spec_filename = "contract_diff_mac_debug.spec" if debug else "contract_diff_mac.spec"
    with open(os.path.join(project_dir, spec_filename), "w", encoding="utf-8") as f:
        f.write(spec_content)
    print("      完成")
    
    # 执行 PyInstaller 打包（使用 --windowed 生成 .app 包）
    print("\n[3/6] 执行打包...")
    print("      这可能需要几分钟时间...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "--windowed",  # 生成 .app 包而不是 Unix 可执行文件
            "--name", app_name,
            "--onedir",  # 生成文件夹模式（.app）
            "--paths", src_dir,
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
            os.path.join(src_dir, "main.py")
        ], cwd=project_dir)
        print("      完成")
    except subprocess.CalledProcessError as e:
        print(f"      错误：{e}")
        return False
    
    # 复制 App 到文稿文件夹
    print("\n[4/6] 复制 App 到文稿文件夹...")
    documents_dir = os.path.expanduser("~/Documents")
    app_file = os.path.join(dist_dir, f"{app_name}.app")
    
    if os.path.exists(app_file):
        target_app = os.path.join(documents_dir, f"{app_name}.app")
        # 如果目标已存在，先删除
        if os.path.exists(target_app):
            shutil.rmtree(target_app)
        shutil.copytree(app_file, target_app)
        print(f"      完成")
        print(f"      App 已保存至：{target_app}")
    else:
        # 检查是否生成了其他文件
        if os.path.exists(dist_dir):
            print(f"      dist 目录内容：{os.listdir(dist_dir)}")
        print("      警告：未找到生成的 .app 文件")
    
    # 创建启动脚本（可选）
    print("\n[5/6] 创建启动脚本...")
    launcher_script = os.path.join(documents_dir, "启动合同对比助手.command")
    with open(launcher_script, "w", encoding="utf-8") as f:
        f.write(f'''#!/bin/bash
# 合同对比助手启动脚本
echo "正在启动合同对比助手..."
open "{target_app}"
''')
    os.chmod(launcher_script, 0o755)
    print(f"      启动脚本已创建：{launcher_script}")
    
    # 显示使用说明
    print("\n[6/6] 生成使用说明...")
    readme_path = os.path.join(documents_dir, "合同对比助手_macOS_使用说明.txt")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"""合同对比助手 v{version} - macOS 版使用说明
=====================================

📦 安装位置：
   {target_app}

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
   • 支持 Word 和 PDF 格式
   • 日志记录与异常处理
   • 自动更新检查

🔧 技术支持：
   如有问题，请查看日志文件或联系开发团队。

---
玉哥与他的虾
版权所有 © 2026
""")
    print(f"      使用说明已保存：{readme_path}")
    
    print("\n" + "=" * 60)
    print("🎉 macOS 构建完成！")
    
    if debug:
        print("\n📝 调试版说明:")
        print("   • 运行时会显示控制台窗口")
        print("   • 可以看到详细的错误信息")
        print("   • 用于诊断闪退问题")
    else:
        print("\n📝 发布版说明:")
        print("   • 无控制台窗口")
        print("   • 如有闪退，请运行调试版查看错误")
    
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="构建合同对比助手 macOS 版")
    parser.add_argument("--debug", action="store_true", help="构建调试版本（带控制台窗口）")
    args = parser.parse_args()
    
    success = build(debug=args.debug)
    sys.exit(0 if success else 1)
