#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建脚本 - 打包成 Windows exe
"""

import os
import sys
import subprocess
import shutil

def build(debug=False):
    """执行构建"""
    version = "1.2"
    print("=" * 60)
    print(f"合同对比助手 v{version} - 构建脚本")
    if debug:
        print("（调试模式）")
    print("=" * 60)
    
    # 项目路径
    project_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(project_dir, "src")
    dist_dir = os.path.join(project_dir, "dist")
    build_dir = os.path.join(project_dir, "build")
    
    # 清理旧的构建文件
    print("\n[1/5] 清理旧的构建文件...")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    print("      完成")
    
    # 创建 PyInstaller spec 文件
    print(f"\n[2/5] 创建打包配置{'（调试）' if debug else ''}...")
    
    exe_name = "合同对比助手_debug" if debug else "合同对比助手"
    console_setting = "True" if debug else "False"
    upx_setting = "False" if debug else "True"
    
    # 转义路径中的反斜杠（Windows 兼容）
    src_dir_escaped = src_dir.replace('\\', '\\\\')
    
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{exe_name}',
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
    
    spec_filename = "contract_diff_debug.spec" if debug else "contract_diff.spec"
    with open(os.path.join(project_dir, spec_filename), "w", encoding="utf-8") as f:
        f.write(spec_content)
    print("      完成")
    
    # 执行 PyInstaller 打包
    print("\n[3/5] 执行打包...")
    print("      这可能需要几分钟时间...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            os.path.join(project_dir, spec_filename)
        ], cwd=project_dir)
        print("      完成")
    except subprocess.CalledProcessError as e:
        print(f"      错误：{e}")
        return False
    
    # 复制 exe 到文稿文件夹
    print("\n[4/5] 复制文件到文稿文件夹...")
    documents_dir = os.path.expanduser("~/Documents")
    exe_file = os.path.join(dist_dir, f"{exe_name}.exe")
    
    if os.path.exists(exe_file):
        target_file = os.path.join(documents_dir, f"{exe_name}.exe")
        shutil.copy2(exe_file, target_file)
        print(f"      完成")
        print(f"      文件已保存至：{target_file}")
    else:
        print("      警告：未找到生成的 exe 文件")
        # 检查是否生成了其他文件
        if os.path.exists(dist_dir):
            print(f"      dist 目录内容：{os.listdir(dist_dir)}")
    
    print("\n" + "=" * 60)
    print("构建完成！")
    
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
    
    parser = argparse.ArgumentParser(description="构建合同对比助手")
    parser.add_argument("--debug", action="store_true", help="构建调试版本（带控制台窗口）")
    args = parser.parse_args()
    
    success = build(debug=args.debug)
    sys.exit(0 if success else 1)
