#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合同对比助手 - py2app 构建脚本
"""

import os
import sys
import subprocess
import shutil

def build():
    version = "1.2.3"
    print("=" * 70)
    print(f"合同对比助手 v{version} - py2app 构建")
    print("=" * 70)
    
    project_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_dir, "dist")
    build_dir = os.path.join(project_dir, "build")
    
    # 清理
    print("\n[1/6] 清理旧构建...")
    for d in [dist_dir, build_dir]:
        if os.path.exists(d):
            shutil.rmtree(d)
    print("      ✅ 完成")
    
    # 运行 py2app
    print("\n[2/6] 执行 py2app 打包...")
    print("      这可能需要几分钟...")
    
    try:
        subprocess.check_call([
            sys.executable, "setup.py", "py2app"
        ], cwd=project_dir)
        print("      ✅ 完成")
    except subprocess.CalledProcessError as e:
        print(f"      ❌ 错误：{e}")
        return False
    
    # 复制 App
    print("\n[3/6] 复制 App 到文稿文件夹...")
    documents_dir = os.path.expanduser("~/Documents")
    app_src = os.path.join(dist_dir, "合同对比助手.app")
    app_dest = os.path.join(documents_dir, "合同对比助手.app")
    
    if os.path.exists(app_dest):
        shutil.rmtree(app_dest)
    
    if os.path.exists(app_src):
        shutil.copytree(app_src, app_dest)
        print(f"      ✅ {app_dest}")
    else:
        print("      ❌ 未找到 .app")
        return False
    
    # 代码签名
    print("\n[4/6] 代码签名...")
    try:
        subprocess.run(['codesign', '--force', '--deep', '--sign', '-', app_dest],
                      capture_output=True, timeout=120)
        subprocess.run(['xattr', '-cr', app_dest], capture_output=True)
        print("      ✅ 完成")
    except Exception as e:
        print(f"      ⚠️ {e}")
    
    # 创建辅助文件
    print("\n[5/6] 创建辅助文件...")
    
    launcher = os.path.join(documents_dir, "启动合同对比助手.command")
    with open(launcher, 'w') as f:
        f.write(f'#!/bin/bash\nopen "{app_dest}"\n')
    os.chmod(launcher, 0o755)
    
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
• 自动打开结果文档

📦 安装位置：
{app_dest}

🚀 启动方式：
1. 双击 {app_dest}
2. 或运行：启动合同对比助手.command

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
    app_size = sum(os.path.getsize(os.path.join(dp, f))
                   for dp, dn, filenames in os.walk(app_dest)
                   for f in filenames)
    
    print(f"\n📊 App 体积：{app_size / 1024 / 1024:.1f} MB")
    
    # 验证
    print("\n[6/6] 验证...")
    result = subprocess.run(['codesign', '--verify', app_dest],
                           capture_output=True, text=True)
    if result.returncode == 0:
        print("      ✅ 签名验证通过")
    else:
        print(f"      ⚠️ 签名：{result.stderr[:100]}")
    
    print("\n" + "=" * 70)
    print("🎉 构建完成！")
    print("=" * 70)
    print(f"\n📍 位置：{app_dest}")
    print("\n🚀 现在可以双击运行！")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = build()
    sys.exit(0 if success else 1)
